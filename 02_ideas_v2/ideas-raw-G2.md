# Ideas — Generator G2 (raw)

- **Generator id:** G2
- **Persona:** Bank IT / integration engineer — the person who inherits every vendor system, wires core banking to fraud engines, CRMs, payment gateways, and reg-reporting tools that were never designed to talk to each other. Thinks in APIs that lie, batch files that arrive late, message formats from 1987, vendor SLAs, and the middleware graveyard. Gets paged when the plumbing breaks.
- **Directions:**
  - **A — The machine customer:** software agents as account holders, payers, purchasers — identity, mandates, spending authority, dispute standing for non-human actors.
  - **B — Inter-institution back-office plumbing:** settlement fails, reconciliation breaks, corporate actions, reference-data disagreements, standards migrations — many-to-many coordination toil.
- **Date:** 2026-07-15
- **Input diet:** exactly one repo file (`01_research/agentic-ai-landscape.md`) + own domain knowledge. No other repo files, no git, no web (bias quarantine).

---

## Direction A — The machine customer

### G2-1 — KYA Desk (Know-Your-Agent Onboarding) [Direction A]

**The problem:** Our onboarding stack physically cannot open an account for a piece of software. The customer master requires a date of birth. CIP wants a driver's license. The workflow engine has a hard-coded "send welcome letter" step. Meanwhile the business has signed a deal that says we'll bank AI purchasing agents by Q4, and the "plan" is — as always — that integration will figure it out. Somebody has to turn "an agent presented a signed identity chain and a mandate from a Delaware LLC" into rows our 1998 core system can hold, with limits the fraud engine can actually read.

**Who has it:** Onboarding/KYC operations lead + the core-banking integration team (me) at any bank whose commercial clients start deploying purchasing agents; also fintech sponsor banks getting API-first agent traffic first.

**What the agent does:** Runs the full Know-Your-Agent case end-to-end: verifies the agent's identity attestation and signed card, walks the principal chain (who deployed it, which legal entity's mandate, is that entity itself KYC'd with us), pulls the mandate apart into machine-enforceable authority (caps, categories, expiry, revocation path), provisions the account with scoped credentials and graduated limits (new agents start in a low-limit "parole" tier and earn headroom from observed behavior), writes the whole dossier into the case system, and — the part nobody else will do — generates the mapping into the legacy customer master so downstream batch jobs don't choke on a customer with no birthday. HITL sign-off before the account goes live.

**Why newly possible now:** Agent identity is finally attestable instead of vibes — A2A v1.0 signed Agent Cards, MCP enterprise OAuth/CIMD, and AgentCore Identity give you cryptographic material to verify rather than a PDF to eyeball. AP2-style mandates (60+ orgs including Amex/Mastercard/PayPal) give a standard artifact to parse. And long-horizon agents can actually run a multi-hour investigation case with an audit trail, which is what onboarding is.

---

### G2-2 — Mandate Enforcement Bridge [Direction A]

**The problem:** A mandate is a beautiful signed JSON object that says "this agent may spend up to $500/day on cloud services until September." My core system's idea of spending authority is an account-level flag and a daily limit field added in 2009. The card processor has its own limit table. The fraud engine has a third. When the agent's mandate says one thing and three legacy systems each enforce an approximation of it, the gap between them is where the losses and the lawsuits live. I know exactly how this movie goes because I've watched it with every prior "authority" concept — the systems drift, nobody reconciles them, and one day the approximation pays out $40k it shouldn't have.

**Who has it:** Payments platform owner and fraud-systems engineering at issuing banks; whoever gets named in the post-incident review when an agent overspends its mandate through a limit-system gap.

**What the agent does:** Sits in the middleware layer as the single translator and reconciler of authority. Ingests mandates (AP2, ACP, custom), compiles each into the *native* limit/flag configuration of every downstream enforcement system (core, card processor, fraud engine, API gateway), pushes the configs, then continuously audits: replays sampled transactions against the source mandate, detects where a legacy system's approximation diverges from the signed intent, and either auto-corrects the config or files a discrepancy ticket with the exact transactions at risk. On mandate revocation, it chases the revocation through every system and produces a signed "authority fully revoked as of T" attestation — because "we turned it off in one of four places" is the classic failure.

**Why newly possible now:** Deterministic policy layers you can compile *to* now exist (Cedar-based policy engines that intercept tool/payment calls pre-execution), mandates are becoming standardized signed artifacts instead of email instructions, and LLM agents are good enough at reading each legacy system's config semantics to do the "compile authority into four dialects" job that previously took a human integrator per system.

---

### G2-3 — Machine Chargeback Desk (Dispute Standing for Agents) [Direction A]

**The problem:** Every dispute process I've ever integrated assumes a human at the start: Reg E/Reg Z timelines keyed to a cardholder noticing, a call-center script that asks "do you recognize this merchant?", an affidavit with a signature line. When an agent's purchase goes wrong — wrong item, double charge, merchant's agent misrepresented the API product — there is literally no intake door. The agent can't call the 1-800 number. Its human principal doesn't even know the transaction happened until the statement. And when the volume is 10,000 micro-transactions a day, the per-dispute economics of our current process are off by two orders of magnitude.

**Who has it:** Disputes/chargeback operations at issuers and acquirers; the principal companies running fleets of purchasing agents who currently just eat the losses because filing isn't worth it.

**What the agent does:** A bank-side dispute agent that gives machine customers standing. Accepts machine-readable dispute filings from customer agents (with the mandate, the request/response logs, the delivery evidence attached — evidence quality machines produce natively and humans never do), validates the evidence pack cryptographically, classifies against network dispute reason codes, auto-resolves the clear cases at machine speed (batch-nets micro-disputes below a threshold instead of filing 10,000 chargebacks), assembles and files representment-grade packets for the contested ones, and negotiates directly with the counterparty bank's dispute agent to converge before anything hits the formal network process. Produces the audit trail a regulator will eventually demand for non-human dispute standing.

**Why newly possible now:** Agent transactions come with evidence humans never had — signed mandates, full request logs, cryptographic receipts (x402 already at 165M+ agent transactions) — so adjudication can be evidence-driven instead of attestation-driven. Card networks are actively standing up dispute frameworks for agent commerce, meaning the rules are being written *right now* and the intake infrastructure doesn't exist yet. Agent-to-agent protocols make bank-to-bank pre-network convergence wireable for the first time.

---

### G2-4 — Zombie Agent Hunter (Credential & Authority Lifecycle) [Direction A]

**The problem:** I have spent twenty years finding API keys in production that belong to vendors we fired in 2015. Now scale that: agents get spun up by a business unit for a pilot, granted payment authority, and then the pilot ends, the team reorgs, the intern leaves — and the agent keeps its credentials. Except this time the orphaned credential isn't a read-only report feed, it's a thing with a bank account and spending authority. The 88%-of-orgs-had-an-agent-incident stat doesn't surprise me at all; the middleware graveyard now has ghosts that can move money.

**Who has it:** Security/IAM operations and treasury at any institution banking or deploying agent fleets; auditors who currently have no answer to "enumerate every non-human identity with payment authority and its living human owner."

**What the agent does:** Continuously reconciles the *authority graph* against the *reality graph*. Inventories every agent credential/mandate/limit across the bank's systems (core, gateway, card processor, MCP/tool gateways), traces each back to a living principal — an employed human, an active vendor contract, an unexpired mandate — by querying HR, vendor-management, and contract systems. Flags orphans, dormants-with-authority, and scope-drift (agent granted $100/day now moving $5k). Executes graduated response under policy: step down limits, quarantine to a sandbox tier, revoke — with HITL gates on revocations that could break production. Produces the quarterly attestation pack ("every non-human identity, its authority, its owner, its last activity") that audit is going to start demanding the first time a zombie agent makes the news.

**Why newly possible now:** Agent identity primitives (AgentCore Identity, MCP OAuth, signed agent cards) make the inventory *possible* — a year ago these were undifferentiated API keys. Cross-system investigation (HR system + vendor DB + gateway logs + payment history) is exactly the multi-step evidence-gathering agents now do reliably, and it's a job no human team will ever staff at agent-fleet scale.

---

### G2-5 — Rails Rosetta (Self-Healing Agent-Payments Interop Gateway) [Direction A]

**The problem:** There are four agent-payment protocols — x402, AP2, ACP, MPP — plus whatever ships next quarter, and the bank has to accept traffic in all of them and land it on rails designed around ISO 8583 and a batch settlement window. I've done this dance before: it's the EDI era, it's MT-vs-MX, it's every "standard" that ships with a spec and no conformance suite. Every counterparty implements it slightly differently, the specs rev, and the mapping tables rot. The last time we built a protocol translation layer it took 18 months and it's been in "maintenance" (i.e., decay) ever since, because maintaining mappings is a job nobody wants.

**Who has it:** Payments integration engineering (me, personally) at every bank and processor that wants agent-commerce volume without ripping out the core; product owners promising "we support agentic payments" on top of plumbing that doesn't.

**What the agent does:** Not just a static translation gateway — a gateway *whose mappings are maintained by the agent*. Normalizes inbound agent-payment messages across protocols into a canonical internal representation and routes to legacy rails (card, ACH, RTP, stablecoin settlement). When a message fails to parse — new spec rev, a counterparty's dialect quirk — the agent diagnoses it against the published spec and observed traffic, drafts the mapping-table change, regression-tests it against the archived message corpus, and ships it behind an approval gate. Tracks each counterparty's dialect profile the way I keep mental notes on which vendor's "ISO 20022" isn't. Files spec-deviation reports to the counterparty's integration team (or their agent) automatically.

**Why newly possible now:** The protocol fragmentation is *new* (all four contenders reached production traction within the last ~18 months), so the interop pain is arriving now with no incumbent solution. And the specific superpower LLM agents have — reading a spec, reading a malformed message, and inferring the mapping — is exactly the human skill that made protocol integration expensive. The maintenance half-life problem that killed every prior gateway is the part an agent solves.

---

### G2-6 — The Agent Relations Manager (Machine-Customer Service Desk) [Direction A]

**The problem:** When a human customer's payment fails, they call us. When an agent customer's payment fails, it gets an HTTP 500 with a body that says `{"error": "internal error"}` — because I wrote that error handler in 2019 and nobody gave me requirements for anything better. The agent retries, trips the rate limiter, gets IP-banned by the WAF, and its principal's business stops. There is no service channel for machine customers: no way to ask why a payment was declined, no way to negotiate a rate limit, no way to be told "that endpoint is deprecated, here's the migration path." We are about to have millions of customers who can only communicate in ways our support org doesn't speak.

**Who has it:** API platform/support operations at banks with agent traffic; the client-side developers whose agents fail mysteriously against bank APIs and burn days in ticket queues.

**What the agent does:** A bank-side servicing agent that *is* the support desk for machine customers, exposed as an MCP/A2A endpoint. A customer agent contacts it with a problem; the servicing agent investigates with real access — pulls the actual decline reason from the fraud engine, the rate-limit state from the gateway, the settlement status from the batch system — and returns a machine-readable diagnosis and remediation ("declined by rule 4417: mandate category mismatch; amend mandate or retry with category X"). It executes fixes it's authorized for (temporary limit lifts within policy, retry scheduling around the batch window, credential rotation), escalates the rest to humans with a pre-built case file, and negotiates service terms (rate limits, webhook configs) agent-to-agent within Cedar-policed bounds. Every interaction logged as tamper-evident audit.

**Why newly possible now:** Until agents could hold real accounts and move real money there was no machine-customer segment to serve; now there is, and it's arriving faster than support orgs can rebuild. MCP as settled standard + A2A give a wire format for the conversation. And an agent with least-privilege tool access into five internal systems can do the cross-system diagnosis that currently takes a tier-2 human three days — at the interaction volumes machine customers generate, agent-speed servicing isn't an optimization, it's the only physically possible model.

---

## Direction B — Inter-institution back-office plumbing

### G2-7 — Fail Fixer Pair (Bilateral Settlement-Fail Negotiator) [Direction B]

**The problem:** A trade fails to settle. Now two back offices run the *identical* investigation in parallel — check the SSIs, check the inventory, check whether the instruction went out late, check whose reference data is stale — and then converge over email, phone tag, and a shared Excel someone mails around, across time zones, while CSDR penalties tick and T+1 has cut the slack out of the timeline. I've watched the same fail take four days to resolve when the root cause was a counterparty's agent bank change that *their own reference team knew about*. The information existed; the coordination didn't. Multiply by every bilateral relationship on the street: the industry runs this duplicated investigation thousands of times a day.

**Who has it:** Settlement operations analysts at broker-dealers, custodians, and asset managers; ops managers who own the fails KPI and the penalty bill.

**What the agent does:** An agent deployed *inside each institution* that, on a fail, investigates its own side with internal access (instruction timestamps, SSI records, inventory/lending status, matching-engine state) and produces a structured, evidence-backed position. Then — the new part — it contacts the counterparty institution's fail agent over A2A and the two *negotiate to shared facts*: exchange evidence packs, isolate the disagreement (your SSI v12 vs our v11), agree the root cause, agree the fix (amend instruction, partial settle, borrow), and each execute their side behind their own HITL gate. Output: a jointly signed break-resolution record both firms file, and a root-cause feed that fixes the upstream data so the same fail doesn't recur next week. No shared utility to build, no data leaves either firm except the negotiated evidence pack.

**Why newly possible now:** This was always a two-organization convergence problem, and there was never a channel for org-A software to negotiate with org-B software — A2A v1.0 (signed agent cards, 150+ production orgs) is that channel. Long-horizon agents can carry a multi-hour investigation; LLMs can read the free-text SWIFT narratives and legacy status codes where fail evidence actually lives. T+1 plus CSDR penalties turned "days of email" from annoying into expensive, so both sides finally have a bill that funds fixing it.

---

### G2-8 — Corporate-Action Golden Record Adjudicator [Direction B]

**The problem:** One dividend announcement, five sources, three interpretations. The issuer's PDF says one thing, two data vendors disagree on the ex-date, the custodian's MT564 has different terms than the sub-custodian's, and the voluntary-event deadline is Thursday. Every institution on the street burns senior ops analysts re-deriving the same golden record from the same messy sources, and when two firms derive it *differently*, you get an entitlement break that surfaces weeks later as a cash rec item nobody can explain. Corporate actions is the last great unautomated swamp of the back office precisely because the inputs are prose, footnotes, and PDFs — the formats that broke every rules-engine attempt since 1995.

**Who has it:** Corporate-actions operations teams at custodians, prime brokers, and asset servicers; the analyst personally on the hook when a missed election costs a client real money.

**What the agent does:** Ingests every source for an event — issuer documents (prospectus, press release, the footnotes), vendor feeds, incoming MT564/565s from upstream custodians — and *adjudicates*: extracts terms from the primary source documents, cross-checks every derived feed against them, flags exactly where each vendor/custodian diverges and why (with the sentence from the prospectus as evidence), and composes the institution's golden record with a per-field confidence score and citation. Drafts the outbound corrected MT564s and the vendor challenge tickets. On disagreement with a counterparty's version, exchanges evidence with *their* corporate-actions agent and converges pre-deadline instead of post-break. Escalates only genuinely ambiguous events to the senior analyst, with the ambiguity isolated to the specific clause.

**Why newly possible now:** The blocking problem was always that the authoritative source is unstructured prose — exactly what LLMs now read reliably with citations. Verifier-loop patterns give the accuracy story a custodian needs before trusting entitlement math. And the inter-firm convergence half becomes wireable once counterparties expose agents (A2A), turning "everyone re-derives alone, breaks discovered later" into "converge on evidence before the deadline."

---

### G2-9 — Dialect Keeper (Counterparty Message-Dialect Mapper) [Direction B]

**The problem:** The dirty secret of every standards migration: there is no such thing as "the standard." There is Bank A's ISO 20022, which truncates the remittance field; Bank B's, which puts the LEI where the BIC goes; Vendor C's, which is MT-in-MX clothing. Post-CBPR+ migration, my mapping layer contains hundreds of per-counterparty exception rules, each discovered in production, each documented in a wiki page that was stale the day it was written, and the whole thing lives in the heads of two engineers who are both eligible for retirement. Every new counterparty is a fresh archaeology project. Every spec rev breaks a random subset.

**Who has it:** Payments/messaging integration teams (me again) at every bank, market infrastructure, and corporate treasury on SWIFT rails; the ops teams downstream who eat the repair queues when a mapping silently drops a field.

**What the agent does:** Owns the dialect knowledge as a living artifact instead of tribal memory. Continuously profiles inbound message traffic per counterparty, infers each counterparty's dialect (deviations from the base spec, field conventions, truncation behavior) as an explicit, versioned dialect model with example evidence. When a message hits the repair queue, it diagnoses which dialect rule (or missing rule) is responsible, drafts the mapping fix, regression-tests it against the full archived corpus of that counterparty's traffic, and deploys behind approval. When *our* outbound messages bounce, it reads the counterparty's rejection codes, forms a hypothesis, and drafts the fix plus a precise, evidence-attached deviation report to send to the counterparty's integration team — the email I currently spend half a day composing. On spec rev (new SWIFT SR, new CBPR+ usage guideline), it re-validates every dialect model against the new base and produces the migration delta per counterparty.

**Why newly possible now:** Inferring "how does this counterparty actually implement the standard" from message samples + spec documents is a pattern-recognition-over-messy-artifacts task that was uneconomic for humans and impossible for rules engines — and is now a core LLM strength. Regression-testing mapping changes against message archives gives the deterministic verification harness that makes auto-maintained mappings trustworthy. The MT→MX long tail plus ongoing yearly SR changes mean the pain is permanent, not a one-off migration.

---

### G2-10 — Night Watch (Inter-Institution Batch & File Babysitter) [Direction B]

**The problem:** The modern financial system still runs on files showing up on time. Positions file from the custodian by 02:00, ACH return file by 06:00, the pricing vendor's feed before NAV calc. When one is late, malformed, or silently *short* (arrived, parsed, but 40k rows instead of the usual 400k — the worst one), a human on the overnight shift notices (or doesn't), phones a counterparty ops desk in another time zone, gets voicemail, and the morning batch cascade starts late. I have personally been the person diffing yesterday's file against today's at 3 a.m. to prove to a vendor that *they* changed the format. Every institution staffs this vigil separately, for the same files, against the same counterparties.

**Who has it:** Overnight batch operations, fund-admin ops, and integration on-call rotations (me, holding the pager) at banks, fund administrators, and asset managers; the counterparty ops desks fielding the 3 a.m. calls.

**What the agent does:** Learns the expected rhythm of every inbound/outbound file per counterparty (timing, size, schema, row-count seasonality, checksum patterns) and watches the night. On anomaly, it investigates: is it late at the source, stuck in our SFTP, a format change, a short file? It diffs against history, characterizes the problem precisely, and then *does the coordination*: contacts the counterparty's ops agent (or, transitional mode, sends their desk a machine-precise notification with the evidence attached — "file X, 03:12, schema drift in columns 14–16, sample rows attached" instead of "your file looks wrong"). For known-benign issues it executes the runbook under policy: re-pull, apply the standard repair, re-sequence downstream jobs, document. For real problems it wakes the right human on *the right side* with the diagnosis already done, and negotiates the recovery plan (resend ETA, run with stale data + flag, hold NAV) against the institution's policy. Every night produces a signed log of what the plumbing did.

**Why newly possible now:** Anomaly detection on file feeds is old; what's new is the *acting* — an agent that can investigate across SFTP servers, schedulers, and archives, read the vendor's spec PDF to confirm a format change, execute a runbook with approval gates, and coordinate with the counterparty's side through an actual machine channel. Long-horizon reliability plus HITL patterns make it deployable in the one environment (overnight batch) where there's no human around *by definition* — which is exactly why the pain exists.

---

### G2-11 — Claims Clerk (Inter-Bank Fails-Claims Negotiator) [Direction B]

**The problem:** Downstream of every settlement fail is the claims fight: interest compensation, buy-in cost allocation, overdraft charges caused by your late delivery. Today this is two ops clerks exchanging emails for *months* over a $3,200 claim — calculating with different day-count conventions, disputing whose fault window it was, attaching screenshots of internal systems as "evidence." Half the claims under $5k are simply never filed because the fight costs more than the claim. The other half sit in aging queues that both sides' auditors flag every year. It's a pure coordination-toil market: real money, zero alpha, nobody's core business, everybody's problem.

**Who has it:** Claims/fails-management teams in settlement ops at broker-dealers and custodians; CFO offices writing off unfiled claims; auditors staring at 180-day-old claim queues.

**What the agent does:** End-to-end claims lifecycle, bilaterally. Detects claimable events from settlement data (fail duration, funding cost, penalty pass-through), computes the claim under the applicable convention with a show-your-work calculation sheet, assembles the evidence pack from internal records, and files it — to the counterparty's claims agent. The receiving agent independently validates against *its* records, and the two negotiate within policy-set bounds (tolerance thresholds, netting proposals, split-the-difference rules the ops manager configures): most claims match-and-settle automatically because both sides computed from the same facts; genuine disputes get escalated to humans with the disagreement isolated to the specific parameter (your fault-window start vs ours). Periodically proposes bilateral netting of accumulated small claims so the sub-$5k tail stops being uneconomic. Ledger of every claim, calculation, and settlement — audit-ready.

**Why newly possible now:** The unit economics flipped: an agent makes a $500 claim worth filing, which unlocks the enormous unfiled tail. Bilateral machine negotiation needs a channel and a trust story — signed agent identities, bounded negotiation authority under deterministic policy, tamper-evident logs — all of which just became off-the-shelf. And claims math from messy evidence (SWIFT confirms, statements, penalty reports) is document-grounded calculation, which agents now do with verifiable working.

---

### G2-12 — SSI Drift Sentinel (Standing Settlement Instructions Reconciler) [Direction B]

**The problem:** A huge fraction of settlement fails trace to one dumb root cause: somebody's standing settlement instructions were stale. The counterparty changed agent banks in March, told you in an email your shared mailbox swallowed, and your reference-data team finds out in July when trades start failing. SSI maintenance across thousands of bilateral relationships is done by circulating spreadsheets and re-keying from PDFs — the same data, held redundantly by every counterparty pair, drifting independently. The industry utilities help but coverage is partial, and the last mile into each firm's internal systems is still manual re-keying, which is where I come in with the ETL duct tape.

**Who has it:** Reference-data/static-data teams and settlement ops at every buy-side and sell-side firm; relationship managers who get yelled at when their client's trades fail on stale instructions.

**What the agent does:** Treats SSI agreement as a continuously-verified bilateral state instead of a yearly cleanup. Periodically (and on trigger events — a fail, a counterparty notification, an agent-bank news item) exchanges cryptographic digests of the relevant SSI set with each counterparty's sentinel agent: matching digests, done, no data moved; mismatch, the agents exchange the specific records, identify the divergent fields, trace each side's version to its source evidence (the notification email, the utility record, the custodian confirm — reading the PDFs and free-text where these things actually live), and determine which is current. Then it executes the last mile: drafts the update in each firm's *internal* format (the core system's SSI table, the matching engine's ALERT-style record), pushes behind HITL approval, and confirms bilateral re-verification. Flags upcoming drift proactively by reading counterparty notifications the shared mailbox would have swallowed. Coverage report per relationship: when each SSI set was last bilaterally verified.

**Why newly possible now:** Digest-exchange verification requires software on both ends that can talk — that's the new A2A/MCP substrate, not new cryptography. The evidence for "which version is right" lives in unstructured artifacts (emails, PDFs, confirms) that only now became machine-readable with citations. And unlike a central utility, agent-pair verification needs no industry-wide adoption event — any two counterparties that deploy it get the benefit bilaterally, which is how plumbing actually gets adopted: one integration at a time.

---

*End of G2 raw ideas — 12 cards: 6 × Direction A (G2-1…G2-6), 6 × Direction B (G2-7…G2-12).*
