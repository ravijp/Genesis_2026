# Architecture — Ear on Every Call

One sentence: **banks read every conversation and remember no customer.** We keep a standing
per-customer signal ledger, and when it crosses a threshold an agent investigates and hands a
decision-ready case to a human.

The full plan of record is [build-plan.md](build-plan.md). This page is the shape of the system.

---

## The one design rule

> **Code counts and remembers. The model reads and judges.**

Arithmetic, accumulation, decay and thresholds are plain Python — deterministic, unit-tested,
reproducible bit-for-bit. Reading natural language and weighing ambiguous evidence is the model's job.
Every boundary below follows from that split, and a test enforces it.

---

## Three layers

```mermaid
flowchart TB
    subgraph L1["Layer 1 · Deterministic core — no LLM, ever"]
        direction LR
        CORPUS[["Synthetic corpus<br/>ground truth authored<br/>before the prose"]]
        LEDGER[("Signal ledger<br/>append-only<br/>never discards")]
        RESCORE["Re-scorer<br/>decay · corroboration<br/>cross-channel · escalation"]
        TRIGGER{"threshold<br/>crossed?"}
        CORPUS --> LEDGER --> RESCORE --> TRIGGER
    end

    subgraph L2["Layer 2 · Agentic"]
        EXTRACT["Extractor<br/>conversation → signals<br/>+ evidence spans"]
        AGENT["Investigator agent<br/>plan → call tools → decide"]
        TOOLS[/"Tools<br/>ledger · conversations<br/>transactions · accounts · prior cases"/]
        AGENT <--> TOOLS
    end

    subgraph L3["Layer 3 · Human"]
        QUEUE["Review queue<br/>ranked cases"]
        ACT{{"approve · dismiss · route"}}
        QUEUE --> ACT
    end

    CORPUS --> EXTRACT --> LEDGER
    TRIGGER -->|yes| AGENT
    TRIGGER -->|no| WAIT["stay in the ledger<br/>re-scored next batch"]
    AGENT --> CASE["Case file<br/>verdict · owning team<br/>recommendation<br/>evidence refs"]
    CASE --> QUEUE
    ACT -.->|dismissal writes back| LEDGER

    style L1 fill:#e8f0fe,stroke:#4285f4
    style L2 fill:#fef0e8,stroke:#f4a142
    style L3 fill:#e8f8ec,stroke:#34a853
```

**Why the split matters commercially.** Layer 1 is what no vendor ships — incumbents reconcile customer
memory to *current truth*, so new observations supersede old ones. Correct for personalization, wrong
for risk, because three faint signals must **sum**, not overwrite. Layer 2 is why this is a product
rather than a dashboard: something has to decide whether a threshold crossing is real, and that is
judgment, not arithmetic.

---

## Data flow — one customer, four months

```mermaid
sequenceDiagram
    autonumber
    participant C as Conversations<br/>(call · chat · complaint)
    participant X as Extractor
    participant L as Ledger + re-scorer
    participant A as Investigator agent
    participant H as Human reviewer

    C->>X: Mar · "moving back in with family"
    X->>L: life_event, conf 0.30, quoted + spanned
    L-->>L: score 0.10 — no action, RETAINED

    C->>X: Apr · "on statutory pay just now"
    X->>L: life_event, conf 0.30
    L-->>L: score 0.29 — no action, RETAINED

    C->>X: Apr · "we're separating, joint accounts"
    X->>L: life_event, conf 0.60
    L-->>L: score 0.66 — no action, RETAINED

    C->>X: Jun · "my husband passed away"
    X->>L: life_event, conf 0.85
    L-->>L: score 0.80 — THRESHOLD CROSSED
    Note over L: retro re-score: March is re-read<br/>in light of June and is load-bearing

    L->>A: investigate CUST-0372
    A->>A: read evidence chain
    A->>A: pull 90d transactions — corroborate or refute?
    A->>A: check prior cases — already handled?
    A->>H: case file: verdict, owning team,<br/>recommendation, evidence refs
    H->>L: approve / dismiss / route
```

The agent never contacts the customer. There is no outbound surface anywhere in the system — HITL is
enforced by absence, not by policy.

---

## The agent loop

```mermaid
flowchart LR
    IN["Trigger:<br/>customer + signal type"] --> PLAN["Read the<br/>evidence chain"]
    PLAN --> LOOP{"enough to<br/>decide?"}
    LOOP -->|no, budget left| TOOL["Call a tool"]
    TOOL --> LOOP
    LOOP -->|yes| DECIDE["Emit decision"]
    LOOP -->|budget spent| DECIDE
    DECIDE --> VALID{"schema valid?<br/>≥1 evidence ref,<br/>all resolvable?"}
    VALID -->|no| RETRY["retry, max 2"] --> DECIDE
    VALID -->|yes| OUT["Case file → queue"]

    style DECIDE fill:#fef0e8
    style VALID fill:#fde8e8
```

Bounded by design: **max 6 steps, max 2 retries, cost cap per investigation.** An agent that can loop
forever is not production-ready, and "feasibility & production readiness" is 25% of the score.

**Evidence is mandatory.** A decision must cite at least one `EvidenceRef` whose conversation id and
character span resolve against the corpus. An unquotable claim is rejected by the schema, not by
good intentions — that is our answer to hallucinated justification, and the rejection rate is a
published metric rather than an exception swallowed at the edge.

---

## Runtime shape

```mermaid
flowchart LR
    subgraph NIGHT["Nightly batch — no always-on infrastructure"]
        FEED["Existing conversation feeds<br/>(the bank already records these)"]
        PIPE["ear pipeline"]
        STORE[("Signal ledger")]
        FEED --> PIPE --> STORE
        PIPE --> CASES[("Cases")]
    end

    subgraph MODELS["Model access"]
        OR["OpenRouter gateway"]
        OFF["Offline provider<br/>zero keys"]
        CACHE[("Response cache<br/>committed → replayable")]
    end

    PIPE -.-> OR
    PIPE -.-> OFF
    OR --> CACHE

    CASES --> VIEWS["One feed, several teams<br/>retention · risk &amp; compliance · commercial"]

    style NIGHT fill:#e8f0fe,stroke:#4285f4
    style MODELS fill:#fef0e8,stroke:#f4a142
```

Batch, not real-time — a deliberate choice, and the one that makes the economics work. The cost that
matters is **per conversation**, not latency on a live call, and an incremental ledger update is O(1)
per arriving conversation instead of re-reading a customer's whole history through a model every night.

**Integration surface is thin on purpose:** read the conversation feeds a bank already produces, write
cases into a queue each team already works. It adds a memory on top of the tools banks already run
rather than replacing them.

---

## Repository map

| Path | What lives there |
|---|---|
| `src/earshot/core/` | Layer 1. Corpus, ledger, re-score math, synthetic account/transaction state. **No LLM import allowed** |
| `src/earshot/agent/` | Layer 2. Investigator loop, tools, decision schemas, prompt loading |
| `src/earshot/llm/` | Provider abstraction: OpenRouter, offline, response cache, cost + latency capture |
| `src/earshot/evals/` | Accuracy, cost, latency, and agent-decision quality |
| `prompts/investigator/v1/` | Prompts as versioned files, so a prompt change is a reviewable diff |
| `artifacts/cache/` | Committed model responses — the demo replays with no keys and no network |
| `artifacts/runs/pinned/` | One committed run + manifest (seed, git SHA, config hash) |
| `docs/` | This page, the build plan, gate briefs, deliverables |

---

## What is measured

| Question | Metric |
|---|---|
| Does the extractor find what was planted? | Span precision/recall vs seeded signals; **published miss rate** |
| Does memory beat forgetting? | Five arms at **equal alert budget**, broken out per stratum |
| Does each scoring mechanism earn its place? | Per-mechanism ablation |
| Is the agent right? | Verdict accuracy, routing accuracy vs seeded trajectory |
| Is the agent honest? | Evidence-groundedness: share of decisions whose refs all resolve |
| Can a bank afford it? | Cost per 1,000 conversations, tokens + steps per investigation, p50/p95 latency |

Numbers are regenerated by one command and written to a run manifest. Nothing published is typed by
hand.

**The honest state, as of 2026-08-09:** the ledger wins the stratum it exists for — arcs where evidence
is spread thin — but loses overall to per-call detection, and a dumb unweighted sum currently matches
the full ledger. That is a real finding from a harness built to test the claim rather than illustrate
it, and it reframes the arms as *"which trigger feeds the investigator best"* rather than as the product
itself.
