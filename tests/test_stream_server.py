"""The live demo server: no outbound surface, no path escape, localhost only.

The server exists so a demo can make real Bedrock calls while a room watches. That is worth
having and it is also the newest place in this repo where a rule could be broken quietly, so the
three properties that make it safe are asserted rather than assumed.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from earshot import stream_server

SOURCE = Path(inspect.getfile(stream_server)).read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def test_there_is_no_write_route_at_all() -> None:
    """No POST, PUT, PATCH or DELETE handler exists on the demo server.

    `aws/api.py` has exactly one write and it appends a review; this server has none, because a
    demo player has nothing to persist. A handler added here would be reachable with no
    authentication -- the routes are unauthenticated on purpose, which is only safe while they
    are all reads.
    """
    methods = {
        node.name
        for node in ast.walk(TREE)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("do_")
    }
    assert methods == {"do_GET"}, f"the demo server defines {sorted(methods)}"


def test_no_outbound_contact_surface() -> None:
    """HITL in this system is enforced by the absence of anywhere to contact a customer.

    Checked on the AST rather than the raw text so the module's own prose about the rule does not
    trip its own guard.
    """
    forbidden = {
        "smtplib", "sendgrid", "twilio", "boto3.client('ses')", "ses", "sns",
        "send_email", "send_message", "publish", "sendmail",
    }
    names: set[str] = set()
    for node in ast.walk(TREE):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Name):
            names.add(node.id)
    leaked = names & forbidden
    assert not leaked, f"the demo server can reach a customer through {sorted(leaked)}"


def test_binds_loopback_only() -> None:
    """The routes have no authentication because there is nothing on the far side of them.

    That sentence is only true while the socket is bound to 127.0.0.1, so the binding is the
    security property and it is pinned here. Read off the AST rather than the file text: the
    module's own prose explains why it does not bind 0.0.0.0, and a text scan flags that prose.
    """
    hosts = {
        node.elts[0].value
        for node in ast.walk(TREE)
        if isinstance(node, ast.Tuple)
        and len(node.elts) == 2
        and isinstance(node.elts[0], ast.Constant)
        and isinstance(node.elts[0].value, str)
        and isinstance(node.elts[1], ast.Name)
        and node.elts[1].id == "port"
    }
    assert hosts == {"127.0.0.1"}, f"the demo server binds {hosts or 'nothing recognisable'}"


@pytest.mark.parametrize(
    "path",
    [
        "/../pyproject.toml",
        "/..%2fpyproject.toml",
        "/ui/../../pyproject.toml",
        "/%2e%2e/%2e%2e/pyproject.toml",
    ],
)
def test_static_handler_refuses_paths_outside_ui(path: str) -> None:
    """`resolve()` + `relative_to()`, not a string prefix test.

    `..%2f` survives one unquote, so a prefix check on the raw path passes it straight through.
    Driven through the real method with a stub socket rather than by reading the source, because
    "the code looks careful" is not the same claim as "the traversal is refused".
    """
    served: list[tuple] = []

    class Stub:
        _static = stream_server._Handler._static
        _json = lambda self, payload, status=200: served.append((status, payload))  # noqa: E731

    Stub()._static(path)
    assert served == [(404, {"error": "not found"})], f"{path} was not refused: {served}"


def test_static_handler_serves_a_real_ui_file() -> None:
    """The negative test above is worthless if `_static` refuses everything."""
    written: list[bytes] = []

    class Stub:
        _static = stream_server._Handler._static

        def send_response(self, code):
            self.code = code

        def send_header(self, *a):
            pass

        def end_headers(self):
            pass

        @property
        def wfile(self):
            return self

        def write(self, data):
            written.append(data)

    stub = Stub()
    stub._static("/index.html")
    assert stub.code == 200
    assert b"<!doctype html>" in written[0].lower()


def test_sse_framing_is_newline_terminated() -> None:
    """SSE is newline-framed, so a payload containing a raw newline splits into two events."""
    body = stream_server._sse("frame", {"quote": "line one\nline two"})
    assert body.endswith(b"\n\n")
    assert body.count(b"\ndata: ") == 1
    assert body.decode().split("data: ")[1].count("\n") == 2  # the two framing newlines only
