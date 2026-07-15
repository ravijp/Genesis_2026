# Ideas — Raw Output G4

- **Generator id:** G4
- **Persona:** Small-business owner who banks — the customer side. I run Redline Electric, a 12-person commercial electrical contracting shop (8 electricians, 2 apprentices, 1 office manager, me). I carry a $250k line of credit, run payroll every two weeks, chase general contractors for money, and pay my bank for the privilege of everything.
- **Direction A:** Life-event administration on the customer's behalf
- **Direction B:** The autonomous finance office for small and mid-size businesses
- **Date:** 2026-07-15
- **Input diet:** CLOSED-BOOK (no repo files, no git, no web; all factual claims tagged UNVERIFIED)

---

## Reasoning (written out before finalizing cards)

I started from what actually eats my weeks, not from what sounds like a product. Two buckets:

**The rare catastrophes (Direction A).** Every big transition in the life of my business — starting it, moving it, nearly losing it in a flood, thinking about selling it, wondering what happens if I die — turns into the same nightmare: 30–60 sequenced tasks across a dozen institutions that don't talk to each other, each with its own form, its own hold time, its own "we need a wet signature." Nobody owns the whole journey. The bank owns maybe 4 of the 40 tasks and acts like that's the whole job. What I would pay real money for is *completion*: someone who knows the full checklist, does the tasks in the right order, and tells me only when a decision or signature is genuinely mine.

**The everyday grind (Direction B).** I don't have a CFO. I have QuickBooks (UNVERIFIED as the common SMB ledger), a spreadsheet, and Sunday nights. The finance function of my business is me, tired, guessing. The bank sees every dollar in and out and does *nothing* with that knowledge except charge me when I guess wrong (overdraft, LOC interest, wire fees). The opportunity is the bank going from ledger to doer — actually operating my receivables, payables, cash positioning, and fee hygiene, because it already sits on the data and the payment rails.

Filters I applied: each idea must ACT (file, send, negotiate, execute, produce artifacts), not summarize. Each must be something *I'd* recognize as pain, in trade-contractor terms. I aimed for ideas other teams won't generate because they've never chased a GC for a retainage check or filled out a certified payroll report at 11pm.

Why-now logic I lean on repeatedly (stated once here): language models can now read messy real-world paper — supplier invoices, bank fee schedules, government forms, contract clauses — reliably enough to act on (UNVERIFIED); agent frameworks can run long multi-step workflows with tool use; most government and institutional processes now have web portals or e-file endpoints even when there's no API, and browser-driving agents can operate those (UNVERIFIED); open-banking-style account access and payment-initiation APIs exist in many markets (UNVERIFIED); e-signature is legally accepted almost everywhere (UNVERIFIED).

---

## DIRECTION A — Life-event administration

### G4-1 · The Wind-Down Clerk (Direction A)

1. **Name:** The Wind-Down Clerk
2. **The problem:** My buddy closed his HVAC shop last year and it took him ELEVEN MONTHS after his last job. Final payroll and payroll-tax filings, cancelling the state contractor license, closing the sales/use tax account, dissolving the LLC with the state, notifying the insurer so the audits stop, final 941s and W-2s (UNVERIFIED form names), telling every vendor so they stop shipping, closing the merchant account without triggering early-termination fees (UNVERIFIED that these are common), and the bank kept charging monthly account fees on a dead business the whole time. Closing a business is a second full-time job you do while grieving the first one.
3. **Who has it:** Any owner closing a small business — retirement, health, or it just stopped working. Also the family of an owner who died with the business still open.
4. **What the agent does:** Builds the full dissolution task graph for MY state, MY entity type, MY licenses and accounts (it discovers them by reading my bank transactions and mail — every recurring debit is a relationship that needs closing). Then it executes: files dissolution paperwork, submits final tax account closures, drafts and sends vendor/customer termination notices, schedules final payroll, cancels licenses and permits, negotiates the merchant-account exit, closes accounts in dependency order (keep the operating account open until the last check clears), and produces a signed-off "this business is fully dead, nothing will bite you in two years" certificate with an archive of every confirmation number.
5. **Why newly possible now:** Agents can drive the dozens of heterogeneous state/IRS/vendor portals that will never share an API; transaction-history reading lets it *discover* obligations the owner forgot exist; long-horizon agent orchestration can hold a 9-month sequenced plan and actually finish it.

### G4-2 · Keys to the Shop (Direction A)

1. **Name:** Keys to the Shop
2. **The problem:** If I got hit by a bus tomorrow, my wife could not make payroll on Friday. She doesn't have bank signatory rights, doesn't know the LOC has my personal guarantee on it, doesn't know which GC owes us what, doesn't know the bonding company needs to be told within some number of days (UNVERIFIED). Banks freeze accounts when the sole signer dies (UNVERIFIED as standard practice) — which kills the business precisely when the family needs it alive. Every owner knows this and none of us have done anything about it because "succession planning" sounds like something for people with yachts.
3. **Who has it:** Every sole-signatory owner of a small business; acutely, the spouse/family in week one after a death or incapacitating accident.
4. **What the agent does:** Two modes. **Peacetime:** continuously maintains a living succession pack — keeps signatory backups current, flags when the LOC guarantee structure would strand the family, drafts and keeps updated the powers/authorizations so accounts DON'T freeze, rehearses the "owner is gone" runbook annually like a fire drill. **Wartime:** on activation (death certificate or incapacity), it executes the runbook — files the death certificate with every institution, invokes the pre-arranged account continuity, notifies the surety, insurer, key customers and vendors with pre-approved letters, keeps payroll running, and hands the family a single daily briefing: "here's what I did, here's the one thing I need from you."
5. **Why newly possible now:** The peacetime mode makes the wartime mode possible — an always-on agent can keep the pack current, which no human advisor does; document generation + institutional-portal execution means the week-one blizzard of paperwork can actually be done BY the agent, not listed FOR the widow.

### G4-3 · The Bank Transplant (Direction A)

1. **Name:** The Bank Transplant
2. **The problem:** I hate my bank. I have hated my bank for six years. I am still with my bank, because moving means re-pointing every GC's ACH remittance, every autopay, payroll direct deposits for 12 people, the merchant processor, the loan autopay, the fuel cards — miss one and either an employee doesn't get paid or a $40k receivable goes to a closed account. Banks know switching is surgery, which is exactly why they can treat small businesses badly. (Claim that SMB bank-switching rates are very low: UNVERIFIED.)
3. **Who has it:** Any small-business owner who stays with a bad bank out of dread. Which is most of us.
4. **What the agent does:** Performs the transplant. Reads 24 months of transactions to build the complete map of inbound payers and outbound pulls. Opens the new account, then executes the migration in a safe order: sets up everything at the new bank first, sends payer-notification letters with new remittance details to every GC and customer (with follow-up until each confirms), re-points payroll and every autopay, runs BOTH accounts in parallel with a live dashboard of "who has switched, who hasn't," sweeps stragglers automatically, and only recommends closing the old account when inflows there have been zero for a full billing cycle. Produces an audit trail so nothing was silently dropped.
5. **Why newly possible now:** Transaction-data access gives a complete, machine-readable relationship map (the old approach — the owner's memory — misses things); agents can do the long tail of payer-by-payer follow-up that made this economically impossible for a human to offer at SMB price points. A challenger bank could offer this as its acquisition weapon.

### G4-4 · After the Fire (Direction A)

1. **Name:** After the Fire
2. **The problem:** A shop two units down from mine flooded in 2023. The owner spent the next four months doing paperwork instead of rebuilding: property insurance claim with its inventory schedules, business-interruption claim needing months of P&L reconstruction, an SBA disaster loan application (UNVERIFIED program details), asking the bank for payment deferral on the equipment loan, payroll decisions with no revenue, notifying customers, chasing the landlord's insurer. Every one of those has deadlines, and blowing a deadline costs real money. He was doing all of it while standing in a wet building.
3. **Who has it:** Any owner in the weeks after fire, flood, theft, or storm — the moment of maximum stress and maximum paperwork, simultaneously.
4. **What the agent does:** Activates as a disaster finance officer. Assembles the insurance claim from records it already has access to (bank feed, invoices, asset purchases reconstructed from transaction history — it can PROVE the inventory existed from purchase records), files the claims, calendars and beats every deadline, drafts and files the disaster-loan application, negotiates forbearance with each lender using a cash-runway model it maintains live, triages which bills to pay in survival mode, and fights the insurer's lowball with a documented counter (line-item replacement costs pulled from supplier catalogs). Owner rebuilds; agent litigates the paperwork.
5. **Why newly possible now:** The killer input — proving what you lost — used to require records that burned with the building; now the financial exhaust (bank + card + invoice history in the cloud) reconstructs it, and an agent can turn that into claim-grade documentation and then prosecute the claim across institutions.

### G4-5 · Second-State Setup (Direction A)

1. **Name:** Second-State Setup
2. **The problem:** We won a two-year job forty minutes away — across the state line. Suddenly: foreign-entity registration in the new state, a new state contractor license with its own exam and bond, new payroll withholding and unemployment accounts, workers' comp coverage in that state, local business license, sales/use tax registration, and my bank asking for all-new paperwork to lend against out-of-state receivables (UNVERIFIED that banks commonly require this). I nearly turned down the job. Nobody — not the bank, not the accountant, not the state — owns the checklist.
3. **Who has it:** Any small business expanding across a state (or provincial/national) line for the first time; trade contractors hit hardest because licensing is state-by-state.
4. **What the agent does:** Generates the complete, ordered registration graph for my trade in the target state, then does it: files the foreign registration, prepares the license application and books the exam, procures the bond quote, opens the payroll tax and unemployment accounts, registers for sales/use tax, updates the insurance certificates, and maintains a "legal to work there yet? — 4 of 9 done, blocker is the bond" tracker. It also runs the ongoing compliance calendar afterward (annual reports in two states now, not one) forever.
5. **Why newly possible now:** State requirements are published but scattered across dozens of agency sites in inconsistent formats — exactly what language models are now good at compiling into an executable plan; portal-driving agents can then file rather than instruct.

### G4-6 · The Sale Room (Direction A)

1. **Name:** The Sale Room
2. **The problem:** A guy offered to buy my shop last spring. He asked for three years of clean financials, customer concentration numbers, aged receivables, equipment list with liens, contract backlog, and license transferability. I had maybe a third of that, in shoeboxes. By the time I could have assembled it, he'd bought someone else. Small businesses sell for less than they're worth — or don't sell at all — because the owner can't produce the paperwork that proves the value. (Claim that a large share of small businesses fail to sell when the owner retires: UNVERIFIED.)
3. **Who has it:** Every owner within ten years of wanting out — which is a huge slice of small-business owners as my generation ages (UNVERIFIED demographic claim).
4. **What the agent does:** Maintains a perpetually sale-ready data room as a byproduct of normal operations: normalized financials, contracts indexed with assignability clauses flagged, equipment register reconciled against lien filings, customer-concentration and backlog dashboards, owner-dependence red flags with fixes ("you personally hold the license — here's the path to putting it on the company"). When a real buyer shows up, it runs the sale-side sequence: NDA, staged disclosure, responds to diligence requests overnight, coordinates the license transfers, lien releases, escrow checklist, and the closing task list across lawyer, bank, and landlord.
5. **Why newly possible now:** The data room used to be a $50k investment-banker artifact (UNVERIFIED price point) assembled in a panic; an agent with standing access to the ledger and document store can maintain it continuously for near-zero marginal cost, turning "unsellable" businesses into sellable ones.

---

## DIRECTION B — The autonomous finance office

### G4-7 · The Polite Bulldog (Direction B)

1. **Name:** The Polite Bulldog
2. **The problem:** GCs pay when they feel like it. I'm owed $180k right now and about $60k of it is past 60 days. Chasing it is awkward — these are also my future customers — so I under-chase, and I NEVER track the lien-rights deadlines (in many states you lose mechanic's-lien rights if you don't send a preliminary notice within a few weeks of starting work — UNVERIFIED specifics, varies by state). My office manager spends a day a week on collections and hates every minute.
3. **Who has it:** Every trade contractor and B2B service business; anyone whose customers are bigger than they are.
4. **What the agent does:** Owns receivables end-to-end. Sends preliminary lien notices on every job automatically at job start (preserving rights costs nothing, losing them costs everything). Learns each GC's actual payment behavior and times escalations to their pay-cycle. Drafts and sends the reminder sequence in MY voice, matching the relationship (soft for the GC who always pays at 47 days, firm for the one who pays whoever screams). Reconciles partial payments and retainage. At defined tripwires it escalates: notice of intent to lien, then tees up the lien filing with everything prepared for my one-click approval. Feeds expected-collection dates into the cash forecast.
5. **Why newly possible now:** Tone-calibrated, relationship-aware dunning was the reason this couldn't be automated before — templates torched relationships. LLMs can hold the relationship register. And lien-deadline law across states is exactly the scattered-rules corpus agents can now operationalize.

### G4-8 · The Nightly Money Router (Direction B)

1. **Name:** The Nightly Money Router
2. **The problem:** Every dollar in my operating account earns nothing while my LOC costs me prime-plus-something (UNVERIFIED typical pricing). I draw the line too early because I'm scared of missing payroll, then leave the draw outstanding for weeks because paying it down takes attention I don't have. The bank profits from my inattention twice — dead deposits AND lazy borrowing. A big company has a treasurer for this. I have a feeling in my stomach.
3. **Who has it:** Every SMB owner with a checking account, a credit line, and no treasurer — i.e., basically all of us below maybe 50 employees.
4. **What the agent does:** Runs treasury every night. Maintains a rolling cash forecast built from the bulldog's collection dates, the payables schedule, and payroll. Then it EXECUTES: sweeps excess into interest-bearing, pays the LOC down the moment the buffer allows, draws only the amount and only the day actually needed, times vendor payments to terms (never early unless there's a discount worth more than my LOC rate), and pre-positions payroll cash 48 hours out, always. Sends me one line a day: "Moved $22k to savings, paid LOC down $15k, Friday payroll covered." Escalates only genuine judgment calls.
5. **Why newly possible now:** Payment-initiation APIs mean the agent can move money, not just recommend moving it (UNVERIFIED availability by market); forecast-grade models over an SMB's own transaction history are now cheap; and the trust problem — letting software move your money — is crossing over as agentic guardrails (caps, allowlists, approval tripwires) mature.

### G4-9 · The Margin Watchdog (Direction B)

1. **Name:** The Margin Watchdog
2. **The problem:** I bid a job with copper wire at one price; by month three the supplier's invoicing 12% more and nobody notices because the invoices go straight to a pile. Change orders get done on a handshake and never billed — I'd guess I eat several percent of revenue a year in unbilled extras (UNVERIFIED, but every contractor I know says the same). I find out a job lost money six months after it closed, at tax time, from my accountant, who tells me like it's weather.
3. **Who has it:** Project-based businesses — contractors, shops, agencies — where the owner is the estimator and nobody reconciles actuals to bid until it's too late to act.
4. **What the agent does:** Reads every supplier invoice as it arrives and three-way-matches it against my bid pricing and the PO. Flags price creep the week it starts and drafts the supplier dispute email or the customer change-order — with the paper trail attached. Listens to job signals (foreman's texts, material orders beyond estimate) to catch scope creep and generates the change-order document BEFORE the work is done, not never. Keeps a live per-job margin gauge and interrupts me only when a job crosses from green to yellow: "Job 214 is now at 8% margin vs 22% bid; here are the three invoices that did it and the change order I drafted."
5. **Why newly possible now:** Supplier invoices are unstructured PDFs in fifteen formats — unreadable by classic OCR-template systems at small-shop cost, trivially readable by LLMs now; connecting the ledger, the bid spreadsheet, and the invoice stream into one acting loop is an agent-orchestration problem that just became tractable.

### G4-10 · The Fee Forensics Agent (Direction B)

1. **Name:** The Fee Forensics Agent
2. **The problem:** My merchant statement is 14 pages of deliberate confusion — interchange categories, downgrade surcharges, "non-qualified" rates, a monthly "regulatory compliance fee" that appeared one day (UNVERIFIED that junk fees like this are common, but I have the statements). My bank charges per-item fees, wire fees, a monthly analysis fee that's supposed to offset against balances and never seems to. I KNOW I'm being skimmed a few thousand a year. I don't have the hours or the vocabulary to fight it.
3. **Who has it:** Every card-accepting small business; every business checking customer. The skim is universal precisely because it's individually too small to fight.
4. **What the agent does:** Ingests every bank, card, and merchant statement monthly. Decodes the fee structure, benchmarks it, and finds the recoverables: transactions downgraded to expensive interchange tiers because of fixable behavior (it fixes the behavior — e.g., settlement timing, missing data fields — UNVERIFIED mechanics), fees that violate my own fee schedule (it files the dispute), and above-market pricing (it drafts the renegotiation letter, or runs a competitive re-quote across processors and manages the switch). Reports in dollars recovered, not insights delivered. Works on contingency of savings, so it costs me nothing unless it wins.
5. **Why newly possible now:** Fee statements were designed to defeat human attention — an agent has infinite attention; the fix loop (dispute filing, re-quoting, switching) is executable through portals and email; and a contingency pricing model only works when the marginal cost of the audit is near zero, which is newly true.

### G4-11 · The Gap Shopper (Direction B)

1. **Name:** The Gap Shopper
2. **The problem:** When I see a cash gap coming — big materials buy for a new job before the first progress payment lands — my options are: draw the LOC, beg the supplier for terms, take an early-pay discount deal from a GC's supply-chain-finance portal (UNVERIFIED that GC portals offering this are common), or those merchant-cash-advance sharks who email me daily with money at rates they refuse to state as APR (UNVERIFIED characterization). I always just draw the LOC because comparing the real cost of four differently-shaped offers is a finance-degree problem and it's 10pm.
3. **Who has it:** Every SMB owner facing a working-capital gap — which is a recurring, predictable event, not an emergency, except we always handle it AS an emergency.
4. **What the agent does:** Sees the gap in the forecast weeks out (from the Router's model). Converts every available option into one honest number — true annualized cost including fees and my time — across LOC draw, supplier-term negotiation (it drafts and sends the ask), early-pay discounts on my receivables, invoice financing offers it solicits competitively, and stretching specific payables. Recommends the mix, and on approval executes it: makes the draw, sends the negotiation, accepts the offer, schedules the payments. Afterward it tells me what the gap actually cost, so the next bid prices it in.
5. **Why newly possible now:** The options were never comparable before because they're priced in deliberately incompatible units (discount %, factor rates, APR, "fees") — normalizing that is now a solved extraction problem; and lenders increasingly expose programmatic offers an agent can solicit and accept (UNVERIFIED extent).

### G4-12 · The Certified Payroll Ghostwriter (Direction B)

1. **Name:** The Certified Payroll Ghostwriter
2. **The problem:** Public-works jobs pay well but come with prevailing-wage rules and weekly certified payroll reports (in the US, Davis-Bacon and forms like WH-347 — UNVERIFIED specifics), fringe-benefit calculations per worker classification per job, and penalties if you misclassify an apprentice's hours. My office manager spends most of a day a week on this for ONE public job, and one mistake can get you debarred from public work (UNVERIFIED consequence). Half the small shops I know just don't bid public work because of this paperwork wall — which means the paperwork, not skill, decides who gets public money.
3. **Who has it:** Every small contractor on (or scared off from) government-funded work: construction, electrical, mechanical, paving, janitorial.
4. **What the agent does:** Sits between timekeeping and payroll. Pulls hours from the field app, applies the correct prevailing-wage determination per classification per county per job (it maintains the wage-determination library), computes fringes, generates and FILES the certified reports weekly, flags misclassification risk before submission ("Marco logged 6 hrs as journeyman on the school job but his apprentice card says otherwise — fix or attest?"), and keeps the audit-ready archive. Net effect: bidding public work stops requiring a compliance department.
5. **Why newly possible now:** Wage determinations are published but voluminous and constantly updated — a corpus-maintenance job agents do well; the reasoning step (classification × county × job type × fringe rules) is exactly the kind of rule-application LLMs with verification loops now handle; filing portals are drivable. The prize is expanding who can access public contracts, which is bigger than saving my office manager a day.

---

*End of G4 raw ideas. 12 ideas: 6 Direction A (G4-1..G4-6), 6 Direction B (G4-7..G4-12). All factual claims tagged UNVERIFIED per closed-book protocol.*
