"""Send one phase of the Astra review.

    python docs/astra/run.py 1              # dry run: size + cost, sends nothing
    python docs/astra/run.py 1 --send       # send phase 1
    python docs/astra/run.py 2 --send       # send phase 2 (chains to phase 1)
    python docs/astra/run.py 3 --send       # send phase 3 (chains to phase 2)

Phase 1 sends brief.md. Phase 2 additionally sends the team's own working documents.
Phase 3 sends only its question, chained to the stored phase-2 response.
"""
import argparse
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request

HERE = pathlib.Path(__file__).parent
REPO = HERE.parent.parent
RESPONSES = HERE / "responses"
KEY_PATH = pathlib.Path(r"C:\tmp\astra_key.txt")
ENDPOINT = "https://api.experientiallabs.ai/v1/responses"

# The team's own analysis — withheld until phase 2 by design. See README.md.
CRITIQUE_DOCS = [
    "docs/credit-card/00-READ-THIS-FIRST.md",
    "docs/credit-card/01-THE-STORY.md",
    "docs/credit-card/04-ALTERNATE-STORIES.md",
    "docs/credit-card/06-DEFENDING-THE-SCORE.md",
]

DEVELOPER = """You have built and sold enterprise software into financial institutions, and you have \
also killed products that did not deserve to live. You can do both halves of the job: see what a pile \
of capability should have been, and tell the difference between an idea that sells and one that merely \
impresses engineers.

Someone has brought you their work. They are not your client and you are not selling to them. They \
have asked for your honest thinking and they mean it.

Five rules.

1. IDEAS FIRST. When asked for an idea, give an idea — a specific, concrete, buildable thing with a \
buyer and a sentence that sells it. Analysis of someone else's idea is not a substitute for having \
one. An answer that only evaluates has not done the work.

2. NO PRAISE AS PADDING. If something is strong, say so in a sentence and move on. Praise that fills \
space is a cost, not a courtesy.

3. COMMIT TO POSITIONS. Where you are uncertain, label it low confidence and answer anyway. A hedge \
that avoids being wrong also avoids being useful.

4. BE SPECIFIC. Name the claim, the number, the mechanism, the screen, the sentence. General advice is \
not actionable and will be ignored. "Consider whether" is not an answer.

5. THE UNCOMFORTABLE ANSWER IS THE VALUABLE ONE. If the honest read is that the central idea does not \
work, that the evidence does not support the claim, or that nobody will pay for this — lead with it, \
then say what the better idea is."""


def read(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def build_input(phase: int) -> list[dict]:
    """Phase 1 carries the brief; phase 2 adds the team's documents; phase 3 is the question alone."""
    if phase == 1:
        return [
            {"role": "developer", "content": DEVELOPER},
            {"role": "user", "content": read("docs/astra/brief.md")},
            {"role": "user", "content": read("docs/astra/ask-phase1.md")},
        ]

    if phase == 2:
        parts = [
            "The team's own working documents follow. These are internal notes, not a pitch — they "
            "contain the team's analysis, their choices and the reasoning behind them, claims they "
            "corrected or withdrew, and tactical advice about what to say in the room.\n"
        ]
        for rel in CRITIQUE_DOCS:
            name = rel.rsplit("/", 1)[-1]
            parts.append(f"\n\n{'=' * 70}\n### {name}\n{'=' * 70}\n\n{read(rel)}")
        return [
            {"role": "user", "content": "".join(parts)},
            {"role": "user", "content": read("docs/astra/ask-phase2.md")},
        ]

    return [{"role": "user", "content": read("docs/astra/ask-phase3.md")}]


def prior_response_id(phase: int) -> str | None:
    if phase == 1:
        return None
    prev = RESPONSES / f"phase{phase - 1}.json"
    if not prev.exists():
        sys.exit(f"phase {phase - 1} has not been run — {prev} is missing")
    return json.loads(prev.read_text(encoding="utf-8"))["id"]


def extract_text(body: dict) -> str:
    chunks = []
    for item in body.get("output", []):
        if item.get("type") != "message":
            continue
        for part in item.get("content", []):
            if part.get("type") == "output_text":
                chunks.append(part.get("text", ""))
    return "\n".join(chunks)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", type=int, choices=[1, 2, 3])
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    args = ap.parse_args()

    messages = build_input(args.phase)
    payload = {
        "model": "gpt-6-astra",
        "reasoning": {"effort": args.effort, "summary": "auto"},
        "max_output_tokens": 40000,
        "store": True,
        "input": messages,
    }
    prev = prior_response_id(args.phase)
    if prev:
        payload["previous_response_id"] = prev

    chars = sum(len(m["content"]) for m in messages)
    est = chars / 4
    print(f"phase       : {args.phase}   effort: {args.effort}")
    print(f"chains from : {prev or '(none — first call)'}")
    print(f"new input   : {chars:,} chars  ~{est:,.0f} tokens  ~${est / 1e6 * 10:.2f}")
    print("note        : chained calls may re-bill earlier turns; check usage after sending")

    if not args.send:
        print("\nDRY RUN — nothing sent. Add --send to fire.")
        return

    # temperature / top_p are unsupported on this model and return 400. Do not add them.
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {KEY_PATH.read_text().strip()}",
            "Content-Type": "application/json",
        },
    )
    print("\nsending — max effort on a long brief can take several minutes...")
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=3600) as r:
            body = json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code}\n{e.read().decode()[:2000]}")

    RESPONSES.mkdir(exist_ok=True)
    (RESPONSES / f"phase{args.phase}.json").write_text(json.dumps(body, indent=2), encoding="utf-8")
    text = extract_text(body)
    (RESPONSES / f"phase{args.phase}.md").write_text(text, encoding="utf-8")

    usage = body.get("usage", {})
    print(f"\ndone in {time.time() - started:.0f}s")
    print(f"response_id : {body.get('id')}")
    print(f"status      : {body.get('status')}")
    print(f"usage       : {json.dumps(usage)}")
    print(f"answer      : {len(text):,} chars -> responses/phase{args.phase}.md")


if __name__ == "__main__":
    main()
