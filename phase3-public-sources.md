# Phase 3 — real, public, citable conversation data

**All URLs fetched and verified on 2026-08-31** unless a row says otherwise. Where a site refused
automated access I say so rather than describing what I could not read.

---

## The constraint that decides everything

Competition rules require **synthetic or anonymised data only** (`CLAUDE.md`, Working rules), and the
corpus additionally requires **seeded ground truth authored before the prose** — no real dataset can
supply "how much evidence was planted in this conversation" because nobody wrote it down before the
conversation happened. `docs/ops/decisions.md` D-010 (2026-08-09) already records a public-data search
that reached the same conclusion.

So the design is fixed by the rules, not by taste:

> **Real transcripts ground the *distributions*. They never ship as our text.**
>
> We derive from them: turn-taking shape, turn-length distribution, opening and closing conventions,
> agent move types and their ordering, disfluency rate, the vocabulary of retail-banking topics, and
> how customers actually phrase distress. We author every shipped sentence ourselves against those
> distributions, and we record which source informed which decision.

This is the same relationship a statistical model has to its training set, and it is the relationship
`benchmarks/cfpb/` already has to the CFPB archive: the archive is downloaded, checksummed and
**cited**, 150 documents are committed for replication, and the *corpus* is untouched by it.

**Two rules that fall out, and both are testable:**

1. No shipped fragment in `corpus_lexicon.py` may be a substring of, or contain a substring of, any
   real source document. A test can assert this against `benchmarks/cfpb/out/sample.jsonl` directly.
2. Every derivation gets a line in a provenance table naming the source, the access date, the
   licence, and what was taken (a distribution, a move taxonomy, a rate) — never a sentence.

---

## Source evaluation

### 1. CFPB Consumer Complaint Database — **already in this repo, CC0, best available**

| | |
|---|---|
| What | Real consumer complaint narratives, written by the consumer, published only with the consumer's opt-in consent and after CFPB PII scrubbing |
| Real human language | **Yes** — consumers' own words, unedited except for scrubbing |
| Domain | US retail banking. Exact product fit, wrong dialect |
| Licence | **CC0.** The CFPB search API self-reports `_meta.license = "CC0"`, which is what `benchmarks/cfpb/steps/01_frame.py:87` records into `benchmarks/cfpb/out/frame.json`. Independently: CFPB is a US federal agency, so its works are public domain in the US (17 USC §105); [cfpb.github.io/api/ccdb/](https://cfpb.github.io/api/ccdb/) states "As a work of the United States Government, source code released by the CFPB is in the public domain by default within the United States." |
| Redistribution | **Permitted without restriction.** [consumerfinance.gov/complaint/data-use/](https://www.consumerfinance.gov/complaint/data-use/) imposes no restriction on redistribution, republication or derivative works; the only stated conditions are on what CFPB itself publishes (opt-in consent, PII scrubbing) |
| Already downloaded | **Yes.** `benchmarks/cfpb/out/source_archive.json`: `complaints.csv.zip`, 1,411,120,769 bytes, sha256 `e6183856f536…`, fetched 2026-08-09 from `https://files.consumerfinance.gov/ccdb/complaints.csv.zip`. Lives outside the repo at `c:/tmp/ccdb`. |
| Already committed | **150 narratives** in `benchmarks/cfpb/out/sample.jsonl` — Panel A n=100 drawn uniformly, Panel B n=50 stratified 17/17/16 across churn / distress / complaint-escalation. Frame: 141,180 narratives received in calendar 2025 across seven retail products. |

**Measured shape of the committed sample** (my own count, 2026-08-31): 150 records, all
`submitted_via: "Web"`; narrative length **min 11 words, median 155, mean 184, p90 354, max 888**;
products 55 credit card / 52 checking-or-savings / 15 student loan / 12 vehicle / 7 payday / 6
mortgage / 3 prepaid.

**How it can be used.**

- **This is the evidence that our `complaint` channel is wrong.** Real complaint narratives are
  **single-author, median 155 words, no turn-taking, no agent**. Our `complaint` channel renders
  460 / 460 documents as interleaved two-party dialogue. The fix is not a guess — it is "make it look
  like the thing we already have 150 real examples of."
- **Vocabulary and topic distribution** for the written channel, taken as frequency counts, not text.
- **A held-out realism check that costs nothing:** the extractor already scores 4 / 112 = 0.036 strict
  recall on these documents (`benchmarks/cfpb/out/results.json`) against 92 / 112 = 0.821 for the
  model reader (`results-model.json`). If a rewritten corpus is more realistic, the *gap between our
  synthetic recall and our CFPB recall should narrow*. That is a falsifiable claim about realism, and
  it can be computed offline from artifacts already in the repo.

**Caveat to state out loud:** US English, and complaint narratives are self-selected — people who
write to a regulator are angrier and more articulate than the median caller. Use it for the written
channel and for distress vocabulary; do not use it to set the *rate* of anything.

### 2. UK Financial Ombudsman Service — published final decisions — **best domain fit, worst access**

| | |
|---|---|
| What | Every FOS final decision, published as an individual PDF. The database holds **over 400,000** decisions |
| Real human language | **Partly.** The ombudsman writes the decision, but decisions routinely narrate and quote what the customer said and what the firm's adviser said on specific calls on specific dates |
| Domain | **UK retail banking, exact fit** — arrears, bereavement, account closure, complaint handling, vulnerability |
| Anonymisation | Complainants are already anonymised by FOS before publication ("Mrs F", "Mr B"); **firms are named** |
| Licence | Open Government Licence v3. FOS publications carry the OGL v3 reference to nationalarchives.gov.uk, with the standard third-party-copyright carve-out. OGL v3 permits copying, adapting and commercial reuse **with attribution** |
| Access | **Blocked to automated fetching.** `https://www.financial-ombudsman.org.uk/decisions-case-studies/ombudsman-decisions`, `/terms-use`, and the direct decision PDF path `https://www.financial-ombudsman.org.uk/decision/DRN-4401591.pdf` all returned **HTTP 403** to WebFetch on 2026-08-31. The prior report hit the same 403 on the statistics pages. Third-party scrapers exist ([Apify](https://apify.com/spookyweb/uk-fos-decisions)), which is itself evidence the site blocks direct programmatic access |

**Verdict.** This is the single best source for what the corpus most lacks — **an arc that unfolds
over months, with a promise made in one contact and broken by the next.** A FOS decision is
literally a written summary of exactly that. But it cannot be harvested from this environment. Using
it means a human downloading a manual sample (20–40 decisions is plenty for structure work), and that
is a Ravi decision, not something a subagent can do.

**If a sample is obtained, use it for the one thing nothing else supplies:** the *shape* of a
multi-contact arc — what gets said on contact 1, what the firm promises, what actually happens, how
the customer opens contact 2. That is Phase C's blueprint. Take no sentences.

### 3. FCA publications — **the right source for agent behaviour, and it is Crown-copyright OGL**

**[Delivering good outcomes for customers in vulnerable circumstances — good practice and areas for
improvement](https://www.fca.org.uk/publications/good-and-poor-practice/delivering-vulnerable-customers)**,
published 2025-03-07, last updated 2025-12-03. Fetched and read 2026-08-31.

It contains real, if paraphrased, disclosure examples and — crucially — **matched good and poor firm
responses to the same disclosure**. Examples it gives:

- a customer whose "rent had increased and they were suffering from anxiety";
- a customer with cystic fibrosis whose "tight finances meant they should not have an overdraft";
- a customer who "had paid an outstanding debt on his deceased wife's account" and was then chased by
  a debt purchaser;
- a blind customer "repeatedly asked by staff to do things they are unable to do, such as read aloud
  a reference number".

Good firm responses documented: courtesy calls every three weeks with a **consistent named staff
member**; proactively emailing a call summary to a hearing-impaired customer; inviting the customer
in for a regular review. Poor responses documented: failing to record an accessibility need so the
customer has to repeat it; rigid adherence to standard process after a need is disclosed; a seven-month
delay communicating with a bereaved customer.

**This is the direct citable basis for rewriting the agent lines**, and it is exactly what our
bereavement transcript gets wrong. It is also the regulator saying, in its own words, that *failing
to carry a disclosure forward between contacts is a poor outcome* — which is this entry's thesis,
sourced.

Licence: Crown copyright under the Open Government Licence v3. Reuse permitted with attribution.

Companion, already cited in the repo's numbers work: **FCA Financial Lives 2024** — 49% of UK adults
(26.4m) have a characteristic of vulnerability, and only **4 in 10 who have one have ever disclosed
it to a provider**. That second number is the population our DIFFUSE stratum represents.

### 4. Taskmaster-1 — **the best free source for how a real call-centre agent actually talks**

| | |
|---|---|
| What | 13,215 task-based dialogues: **5,507 spoken** and 7,708 written |
| How the spoken half was made | Wizard-of-Oz: crowdworkers played the user, **trained call-centre operators played the assistant** |
| Real human language | **Yes, and unusually honest about it.** The README states disfluencies "such as 'they um, they want Korean cuisine' were also usually transcribed as spoken", and operator shorthand like "cuz" and "lol" was left as-is |
| Domain | Pizza, auto repair, ride service, movie tickets, coffee, restaurant reservations. **No banking** |
| Licence | **CC BY 4.0** — commercial use and adaptation permitted with attribution |
| Source | [github.com/google-research-datasets/Taskmaster](https://github.com/google-research-datasets/Taskmaster), TM-1-2019 |

**Why it matters despite the domain mismatch.** The thing we are worst at is not banking vocabulary —
our 56 planted fragments are already good UK banking English. It is **conversational mechanics**: who
speaks when, how long a turn is, how an agent acknowledges before acting, how a call opens and closes,
how often a real agent says "let me just check that for you" versus actually answering. Those are
domain-independent, and 5,507 transcripts of trained operators are the cleanest free sample of them.

Use it to derive: turn-length distribution, agent-move taxonomy (acknowledge / clarify / act /
confirm / close), the ratio of agent moves that reference the customer's last utterance, and the
disfluency rate. Take no sentences.

### 5. ABCD — Action-Based Conversations Dataset

10,000+ **human-to-human** live-chat dialogues, 55 user intents, collected by ASAPP with an "Expert
Live Chat" protocol. **MIT licence.**
[github.com/asappresearch/abcd](https://github.com/asappresearch/abcd) · paper
[arXiv:2104.00783](https://arxiv.org/abs/2104.00783), NAACL 2021.

Domain is e-commerce (accounts, shipping, refunds), not banking. Its distinctive value is that agent
turns are **constrained by company policy and annotated with the action taken** — which is the closest
public analogue to a contact-centre agent working to a script. Good source for the *chat* channel's
register, which is different from voice: shorter turns, no "thanks for holding".

### 6. MultiWOZ and Schema-Guided Dialogue — thin

- **MultiWOZ** — ~10,000 Wizard-of-Oz dialogues, MIT licence, domains hotel/restaurant/train/
  attraction/hospital/police/taxi. **No banking.** Value: turn-count and turn-length statistics only.
  [github.com/budzianowski/multiwoz](https://github.com/budzianowski/multiwoz) ·
  [arXiv:1810.00278](https://arxiv.org/abs/1810.00278).
- **Schema-Guided Dialogue (SGD)** — 20,000+ dialogues over 20 domains, **CC BY-SA 4.0**, and it
  does include `Banks_1` / `Banks_2` services. But the dialogues were "generated with the help of a
  dialogue simulator and paid crowd-workers", i.e. machine-generated skeletons that humans
  paraphrased. **Grounding synthetic data on synthetic data launders nothing.** The share-alike term
  is also a live consideration if anything derived were redistributed.
  [github.com/google-research-datasets/dstc8-schema-guided-dialogue](https://github.com/google-research-datasets/dstc8-schema-guided-dialogue).

### 7. CallCenterEN — **real, large, and we cannot use it**

91,706 real call-centre transcripts, 10,448 audio hours, inbound and outbound, PII removed, audio
withheld for biometric-privacy reasons. Ha Dao, Gaurav Chawla, Raghu Banda, Caleb DeLeeuw,
[arXiv:2507.02958](https://arxiv.org/pdf/2507.02958), submitted 2025-06-30.

**Licence: CC BY-NC 4.0 — non-commercial only.** This is a competition entry for a commercial AI
services company, positioned as a client-facing product. Even "we only read it to inform our writing"
is an argument I would not want to have in front of a judge who checks. **Excluded on licence.**
Worth naming in the write-up precisely because excluding it on licence grounds is a credibility
marker.

### 8. Bitext retail-banking chatbot dataset — wrong kind of real

25,545 question/answer pairs, 26 intents across 9 retail-banking categories, **CDLA-Sharing-1.0**.
[huggingface.co/datasets/bitext/Bitext-retail-banking-llm-chatbot-training-dataset](https://huggingface.co/datasets/bitext/Bitext-retail-banking-llm-chatbot-training-dataset).

But Bitext's own card says the pairs are "generated using a hybrid methodology" — NLP seed extraction
plus NLG expansion. **It is synthetic.** Its only use here is as an **intent taxonomy** for the
"reason for contact" work in Phase C — a checked list of the 26 things retail-banking customers
actually contact a bank about. Take the taxonomy, not the text.

### 9. Switchboard / Fisher (LDC)

Real conversational telephone speech, the reference corpora for the genre. Both are **LDC-licensed and
paid**, and neither is customer-service. Not worth the cost or the procurement time before 2026-09-07.

---

## Summary table

| Source | Real human? | Banking? | UK? | Licence | Redistributable | Accessible now | Use |
|---|---|---|---|---|---|---|---|
| CFPB CCDB | yes | yes (US) | no | CC0 | yes | **already in repo** | complaint-channel shape, distress vocabulary, realism check |
| FOS decisions | quoted | **yes (UK)** | **yes** | OGL v3 | yes, attribution | **403 — manual only** | multi-contact arc structure (Phase C) |
| FCA vulnerability review | paraphrased | yes (UK) | yes | OGL v3 | yes, attribution | yes | **agent behaviour, good vs poor responses** |
| Taskmaster-1 (spoken) | **yes, trained operators** | no | no | CC BY 4.0 | yes, attribution | yes | turn mechanics, disfluency, agent moves |
| ABCD | yes | no | no | MIT | yes | yes | chat-channel register, policy-constrained agent |
| MultiWOZ | yes (WoZ) | no | no | MIT | yes | yes | turn-length stats only |
| SGD | simulator + paraphrase | has `Banks_1/2` | no | CC BY-SA 4.0 | yes, share-alike | yes | weak — synthetic |
| CallCenterEN | **yes** | mixed | no | **CC BY-NC 4.0** | **no (non-commercial)** | yes | **excluded on licence** |
| Bitext retail banking | **no (NLG)** | yes | unclear | CDLA-Sharing-1.0 | yes | yes | intent taxonomy only |
| Switchboard / Fisher | yes | no | no | LDC, paid | no | no | not worth it |

---

## The design, and why it satisfies the rule

**Three tiers, and only the first two are needed before 2026-09-07.**

**Tier 1 — behavioural grounding (no data pipeline at all).** The FCA good-practice document and the
Taskmaster-1 spoken README are read by a human, and the *rules* they imply are written into
`corpus_lexicon.py` as authored English. Example, and this is the actual derivation behind Phase A:
FCA documents that a good firm response to a disclosure **acknowledges the specific thing disclosed
and does not restart the process**; our agent currently answers a bereavement with the recording
notice. That is a citation-backed reason to write a specific replacement line. Nothing is copied,
because there is nothing to copy — the source is a finding, not a sentence.

**Tier 2 — distributional grounding (offline, from data already committed).** Compute statistics from
`benchmarks/cfpb/out/sample.jsonl` (already in the repo, CC0) and from Taskmaster-1 if it is
downloaded: narrative length distribution, turns per conversation, words per turn, the share of agent
turns that reference the previous customer turn. Fit the generator's parameters to those
distributions. **A distribution is not expression and cannot be copyrighted**; and CC0 and CC BY 4.0
would both permit it anyway.

**Tier 3 — arc grounding (needs a human to fetch FOS).** A manual sample of 20–40 FOS decisions,
read to extract a *taxonomy of arc shapes*: promise-then-silence, repeated-contact-escalation,
disclosure-then-process-restart, and so on. Encode the taxonomy as generator parameters. This is the
input to Phase C.

**How the "synthetic or anonymised only" rule is satisfied at every tier.**

1. Every shipped sentence is authored by us. No real customer text enters `corpus_lexicon.py`.
2. What crosses from a real source is a **number or a rule** — a median turn length, a move ordering,
   a documented good-practice behaviour. None of that is customer data.
3. The one real dataset that is redistributed at all (the 150 CFPB narratives) is already committed,
   is CC0, is PII-scrubbed by the publisher, is opt-in by the consumer, and sits in `benchmarks/`
   labelled as a **benchmark input**, never as our corpus. That separation already exists and is
   already documented in `benchmarks/cfpb/PROTOCOL.md`.
4. A test can enforce rule 1 mechanically: assert no `corpus_lexicon` fragment shares a 6-gram with
   any narrative in `sample.jsonl`. Cheap, offline, and it turns a promise into a guard — which is
   how this repo handles every other rule it cares about.

**What to cite on the day.** "Our transcripts are synthetic. Their *shape* is not invented — turn
mechanics are fitted to Taskmaster-1's 5,507 spoken dialogues with trained call-centre operators
(CC BY 4.0), the written channel is fitted to 141,180 real 2025 CFPB complaint narratives (CC0, and
150 of them are committed to this repo and benchmarked against), and the agent behaviour follows the
FCA's March 2025 good-practice findings. Here is the provenance table." That is a materially stronger
answer than "we wrote it ourselves", and every element of it is already true or one Phase away.

---

## Sources

- [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/) · [How we share complaint data](https://www.consumerfinance.gov/complaint/data-use/) · [CCDB API docs](https://cfpb.github.io/api/ccdb/) · [data.gov catalog entry](https://catalog.data.gov/dataset/consumer-complaint-database)
- [FOS ombudsman decisions](https://www.financial-ombudsman.org.uk/decisions-case-studies/ombudsman-decisions) (403 to automated fetch, 2026-08-31)
- [FCA — Delivering good outcomes for customers in vulnerable circumstances](https://www.fca.org.uk/publications/good-and-poor-practice/delivering-vulnerable-customers) (2025-03-07, updated 2025-12-03) · [FCA — Firms' treatment of customers in vulnerable circumstances](https://www.fca.org.uk/publications/multi-firm-reviews/firms-treatment-vulnerable-customers)
- [Taskmaster](https://github.com/google-research-datasets/Taskmaster) · [TM-1 README](https://github.com/google-research-datasets/Taskmaster/blob/master/TM-1-2019/README.md) · [arXiv:1909.05358](https://arxiv.org/abs/1909.05358)
- [ABCD](https://github.com/asappresearch/abcd) · [arXiv:2104.00783](https://arxiv.org/abs/2104.00783)
- [MultiWOZ](https://github.com/budzianowski/multiwoz) · [arXiv:1810.00278](https://arxiv.org/abs/1810.00278)
- [Schema-Guided Dialogue](https://github.com/google-research-datasets/dstc8-schema-guided-dialogue)
- [CallCenterEN, arXiv:2507.02958](https://arxiv.org/pdf/2507.02958) — CC BY-NC 4.0, excluded
- [Bitext retail-banking dataset](https://huggingface.co/datasets/bitext/Bitext-retail-banking-llm-chatbot-training-dataset)
- [LDC Switchboard-1 Release 2](https://catalog.ldc.upenn.edu/LDC97S62) · [Fisher English Part 1 Transcripts](https://catalog.ldc.upenn.edu/LDC2004T19)
