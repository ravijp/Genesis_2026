"""`earshot stream --serve`: the same stream, live on localhost, over Server-Sent Events.

**Why this exists alongside the recorded replay.** The static `ui/` opens from `file://` with no
server, no network and no toolchain, and that stays the default because a judging room with no
wifi must still see the product (D-004). But "we recorded this earlier" and "watch it happen" are
different claims, and only one of them survives the question *is the model actually running?*
This server is the second claim: every frame it emits is a Bedrock call that happened while the
audience was watching, and the pace is the model's own latency rather than a chosen animation.

**Credentials stay in this process.** The browser never holds an AWS key, never signs a request
and never talks to AWS. It holds an EventSource to 127.0.0.1 and renders what arrives. That is
also why the deployed Function URL is not the answer here: it is `AuthType=AWS_IAM`, which a
static page cannot sign, and the execution role still lacks DynamoDB and SQS anyway.

**Localhost only, and that is a security property, not a limitation.** The socket binds
127.0.0.1. There is no auth on these routes because there is nothing to authenticate to -- and
if it bound 0.0.0.0 that sentence would be false. The static handler refuses any path that
escapes `ui/`.

**It computes nothing the batch path does not.** Frames come from `run_stream`, the identical
function `earshot stream` calls, through the identical `on_frame` callback. The live screen and
the recorded screen cannot drift about what a frame is, because there is one producer.

**No outbound contact surface, here as everywhere.** There is no route in this file that emails,
calls or messages a customer, and `tests/test_stream_server.py` asserts the absence. HITL in this
system is enforced by there being nothing to enforce it against.
"""

from __future__ import annotations

import json
import mimetypes
import queue
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .stream import Crossing, StreamRun, run_stream, stream_payload
from .tenants import Tenant

UI_DIR = Path(__file__).resolve().parents[2] / "ui"

# Sentinel pushed onto the frame queue when the producer thread is finished. A `None` would be
# ambiguous with a dropped frame; an object identity cannot be.
_DONE = object()


def _sse(event: str, data: Any) -> bytes:
    """One Server-Sent Event. `json.dumps` with no newlines, because SSE is newline-framed."""
    body = json.dumps(data, default=str, separators=(",", ":"))
    return f"event: {event}\ndata: {body}\n\n".encode("utf-8")


class _Handler(BaseHTTPRequestHandler):
    """Static `ui/` plus two live routes. Reads only; there is no POST here at all."""

    server_version = "earshot-stream"
    # Set by `serve_stream` on the server object, read through `self.server`.
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        # The default logs every asset fetch to stderr and buries the one line that matters.
        if "/live/" in (args[0] if args else ""):
            sys.stderr.write("  %s\n" % (fmt % args))

    # -- routes ---------------------------------------------------------------------------
    def do_GET(self) -> None:  # noqa: N802  (stdlib naming)
        path = urlparse(self.path).path
        if path == "/live/meta":
            return self._json(self.server.meta)  # type: ignore[attr-defined]
        if path == "/live/stream":
            return self._stream()
        return self._static(path)

    def _json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _static(self, path: str) -> None:
        """Serve `ui/`, and nothing outside it.

        `resolve()` then `relative_to()` rather than string prefix checks: `..%2f` survives one
        unquote and a prefix test on the raw path would pass it.
        """
        rel = unquote(path).lstrip("/") or "index.html"
        try:
            target = (UI_DIR / rel).resolve()
            target.relative_to(UI_DIR.resolve())
        except (ValueError, OSError):
            return self._json({"error": "not found"}, 404)
        if not target.is_file():
            return self._json({"error": "not found"}, 404)
        body = target.read_bytes()
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _stream(self) -> None:
        """Hold the connection open and forward frames as the producer computes them.

        Chunked rather than a content length, obviously -- the length is not known until the book
        has been read. The producer runs on its own thread so a browser that disconnects mid-demo
        does not abort a run that has already spent money.
        """
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "keep-alive")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()

        server = self.server  # type: ignore[assignment]
        frames: queue.Queue = server.frames  # type: ignore[attr-defined]
        try:
            self._write_chunk(_sse("meta", server.meta))  # type: ignore[attr-defined]
            while True:
                item = frames.get()
                if item is _DONE:
                    break
                kind, payload = item
                self._write_chunk(_sse(kind, payload))
        except (BrokenPipeError, ConnectionResetError):
            # The audience closed the tab. Not an error worth a traceback on a stage.
            return
        try:
            self._write_chunk(b"")
        except (BrokenPipeError, ConnectionResetError):
            return

    def _write_chunk(self, data: bytes) -> None:
        self.wfile.write(f"{len(data):X}\r\n".encode("ascii"))
        self.wfile.write(data)
        self.wfile.write(b"\r\n")
        self.wfile.flush()


def serve_stream(
    t: Tenant,
    *,
    provider_name: str,
    extractor_name: str,
    port: int = 8765,
    investigate_limit: int | None = None,
    pace_seconds: float = 0.0,
) -> int:
    """Run one tenant's stream on a worker thread and serve it, plus `ui/`, on localhost.

    The stream starts when the first browser connects, not at boot: a demo that has already run
    its first thirty conversations before anyone opens the page has nothing to show.
    """
    from .agent.prompts import investigator_prompts
    from .cli import _stream_manifest, build_extractor, stream_inputs
    from .llm import build_provider

    _, _, prompt_sha = investigator_prompts()
    extractor = build_extractor(extractor_name, t.run)
    provider = build_provider(provider_name, prompt_sha)
    manifest = _stream_manifest(t, extractor, provider, provider_name)
    manifest["live"] = True
    # **The honesty gap this closes.** Once the reader cache is warm, a "live" run serves recorded
    # completions and finishes in seconds -- a LIVE badge over a cache replay, which is the exact
    # kind of claim this repo spends its effort not making. So the mode travels to the browser and
    # the badge names it. `EARSHOT_CACHE_MODE=off` is what forces genuinely new calls on stage.
    mode = manifest.get("cache_mode")
    manifest["live_kind"] = (
        "every call is new" if mode == "off" else f"loop is live, responses cached ({mode})"
    )
    # Built before the socket opens, not on the first connection: generating a corpus takes long
    # enough to look like a hang if it happens after someone has already clicked.
    conversations, context_for = stream_inputs(t)

    frames: queue.Queue = queue.Queue()
    state: dict[str, Any] = {"run": None, "started": False}

    def on_frame(frame: dict[str, Any]) -> None:
        frames.put(("frame", frame))
        if pace_seconds:
            time.sleep(pace_seconds)
        elif mode != "off":
            # A cached read returns instantly and the whole book blurs past. Hold each frame for
            # the latency the reader ACTUALLY took when that response was recorded, so the pace on
            # screen is still a measurement rather than an animation speed someone picked.
            recorded = (frame.get("reader") or {}).get("latency_ms") or 0
            if recorded:
                time.sleep(min(3.0, recorded / 1000.0))

    def on_investigated(crossing: Crossing) -> None:
        frames.put((
            "verdict",
            {
                "customer_id": crossing.customer_id,
                "frame_index": crossing.frame_index,
                "day": crossing.day,
                "signal_type": crossing.signal_type.value,
                "score": crossing.score_at_cross,
                "skipped": crossing.skipped,
                "verdict": None if crossing.decision is None else crossing.decision.verdict,
                "confidence": None if crossing.decision is None else crossing.decision.confidence,
                "team_label": None if crossing.decision is None
                else t.team_label(crossing.decision.owning_team),
                "rationale": None if crossing.decision is None else crossing.decision.rationale,
                "cost_usd": None if crossing.trace is None else round(crossing.trace.cost_usd, 4),
            },
        ))

    def produce() -> None:
        try:
            run: StreamRun = run_stream(
                t,
                conversations,
                extractor,
                provider,
                context_for=context_for,
                investigate_limit=investigate_limit,
                on_frame=on_frame,
                on_investigated=on_investigated,
            )
            state["run"] = run
            # The full payload last, so the browser can populate the case and retro screens from
            # the same objects the recorded file carries. One shape, two transports.
            frames.put(("done", stream_payload(run, manifest)))
        except Exception as exc:  # a live demo must say what broke, not hang
            frames.put(("failed", {"error": f"{type(exc).__name__}: {exc}"}))
        finally:
            frames.put(_DONE)

    class _Server(ThreadingHTTPServer):
        daemon_threads = True
        allow_reuse_address = True

    # 127.0.0.1, never 0.0.0.0. These routes have no authentication because there is nothing on
    # the far side of them; binding the interface is what makes that true.
    httpd = _Server(("127.0.0.1", port), _Handler)
    httpd.meta = manifest  # type: ignore[attr-defined]
    httpd.frames = frames  # type: ignore[attr-defined]

    original_stream = _Handler._stream

    def _stream_and_start(self: _Handler) -> None:
        if not state["started"]:
            state["started"] = True
            threading.Thread(target=produce, daemon=True).start()
        original_stream(self)

    _Handler._stream = _stream_and_start  # type: ignore[method-assign]

    url = f"http://127.0.0.1:{port}/index.html#/stream"
    print(f"\n{'=' * 78}")
    print(f"LIVE STREAM  {t.name}   reader={extractor_name}  agent={provider_name}")
    print(f"{'=' * 78}")
    print(f"  open  {url}")
    print("  Frames are produced by the same run_stream() the recorded command calls, and the")
    print("  pace is the reader's own latency. Credentials stay in this process; the browser")
    print("  holds an EventSource to localhost and nothing else.")
    print("  NO SPEECH RECOGNITION: transcripts are generated text, the arrival pattern is what")
    print("  is being reproduced.")
    print("  Ctrl-C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    finally:
        httpd.server_close()
    return 0
