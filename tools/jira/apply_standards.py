"""Apply the house Jira standard (docs/ops/jira-conventions.md) to every issue on the board.

ALREADY APPLIED, 2026-08-09 (commit c3d774b). **Do not re-run it as-is.** It is a one-shot
migration that presents as a maintained tool, which is the trap this note exists to close:

- Not idempotent. `comment()` and `link()` are POSTs, so a second run duplicates a 56-line
  comment on AT-38 and duplicates every blocking link. Jira deletion returns 403 for us
  (jira-conventions.md), so the duplicates would be permanent.
- It would silently revert work. Line ~525 transitions AT-61 to In Progress; commit 6ab0d06
  deliberately moved it back to To Do because the reviewer queue was never started.
- Its due dates (2026-08-13, 2026-08-17) are in the past.
- The 45 issue keys AT-38..AT-82 are hardcoded, with no JQL and no --dry-run.

To change the board now, write a new scoped script rather than re-running this one. Kept
because it is the only record of how the board's house style was actually applied.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from adf import adf, description  # noqa: E402
from client import IN_PROGRESS, TODO, Jira  # noqa: E402

# key -> (summary or None, why, doing[], done_when[], notes)
TICKETS: dict[str, tuple] = {
    # ============================ data =========================================
    "AT-38": (
        "Decide what data we test on",
        "We cannot use real customer conversations, so we have to decide what we test on and be "
        "able to defend it. This is the decision, with the search already done.",
        [
            "Keep the made-up conversations for the memory experiment (AT-39, AT-40, AT-41)",
            "Shape them using real complaint data so our distribution is not invented (AT-42)",
            "Prove the reader works on real complaints, not only on our own prose (AT-43)",
        ],
        [
            "We can say in one sentence why we test on what we test on, and back it with what we "
            "looked at",
            "The reader has been measured against real customer language as well as ours",
        ],
        "Findings from the public-data search are in the comments. Decide by **2026-08-13** so the "
        "work lands before the 24 August demo. Estimated 3 days of the 15 remaining.",
    ),
    "AT-39": (
        None,
        "Everything downstream needs conversations to read, and we need to know the right answer "
        "for each one.",
        [
            "A few hundred customers, several conversations each, spread over months",
            "Three channels: calls, chats and complaints",
        ],
        [
            "One command generates the whole set from a seed",
            "The same seed produces byte-identical output every time",
        ],
        "",
    ),
    "AT-40": (
        None,
        "If we wrote the conversations and then decided what they meant, we would be marking our "
        "own homework. We decide first, then write around it.",
        [
            "Record which customer, which conversation, which sentence, and how strong",
            "Keep that answer key completely out of reach of anything that reads a conversation",
        ],
        [
            "Nothing on the path from conversation to decision can recover the answer key",
            "A test fails if someone reintroduces a way in",
        ],
        "**Found and fixed 09 Aug.** The answer key was leaking. Each customer carried a risk number "
        "that was exactly zero for everyone who was fine and above 0.55 for everyone who was not, so "
        "that single number gave the answer away — and the agent could read it through the account "
        "tool without reading a word of conversation. A customer's financial situation and how much "
        "they talked about it are now separate things, drawn so the two groups genuinely overlap.",
    ),
    "AT-41": (
        None,
        "The whole idea is about customers you cannot spot from any single conversation. If the "
        "dataset has none of those, we prove nothing.",
        [
            "Customers whose worry is spread thin and never obvious in one conversation",
            "Customers who sound worrying but are perfectly fine, so we can count false alarms",
        ],
        [
            "Both groups exist in numbers large enough to measure",
            "How often each is flagged is reported, rather than designed so we cannot get it wrong",
        ],
        "",
    ),
    "AT-42": (
        "Shape our made-up conversations using the real complaint data",
        "Our conversations are currently invented end to end, including how often each kind of "
        "problem comes up. Real data can fix the shape for free.",
        [
            "Pull the real distribution of products, issues and complaint types from CFPB",
            "Feed those proportions into our generator",
            "Add the texture we are still missing: transcription errors, compliance scripts",
        ],
        [
            "Our generated mix matches the real one, and we can show the two side by side",
        ],
        "",
    ),
    "AT-43": (
        "Test the reader against real complaints, not just our own writing",
        "The strongest single objection to this project is that our reader only works because it is "
        "reading prose we wrote ourselves. This closes it.",
        [
            "Take a sample of real CFPB complaint narratives",
            "Mark up by hand where the warning signs are, with written rules for doing so",
            "Have a second person check a portion of the markup",
            "Measure the reader on real text the way we already measure it on ours",
        ],
        [
            "Two numbers side by side: how the reader does on our conversations, and on real ones",
            "The marking-up rules are written down and someone else has checked a sample",
        ],
        "This is the long pole of the data work, roughly 2 days. If time runs out, cut this and keep "
        "AT-42 — but cut it last, because this is the part that earns technical credit.",
    ),
    # ============================ reading ======================================
    "AT-44": (
        None,
        "Turning conversations into signals is the input to everything else. It is also the part a "
        "vendor already does well, so we treat it as plumbing rather than as our contribution.",
        [],
        ["Every signal we produce carries the exact words behind it"],
        "",
    ),
    "AT-45": (
        None,
        "A signal we cannot point at is not evidence, and a reviewer cannot act on it.",
        ["Pull out money worry, thinking of leaving, life events and repeated complaints"],
        ["No quote, no signal — an unquotable claim is dropped rather than kept"],
        "",
    ),
    "AT-46": (
        None,
        "Publishing how much our reader misses is stronger than implying it misses nothing.",
        ["Compare what the reader found against the planted answer key"],
        ["The miss rate is published in the README, not buried"],
        "Currently **0.681 recall — it misses 32%.** That is on purpose: the offline reader is a "
        "keyword matcher and is meant to be the weaker option, so that a result which survives it "
        "means something.",
    ),
    "AT-47": (
        None,
        "Keyword rules cannot understand context. A language model can, and the gap between them "
        "tells us what the model is worth.",
        ["Swap the keyword rules for a model reading each conversation",
         "Compare the two on the same dataset"],
        ["We can state what using a model buys us, as a number"],
        "",
    ),
    # ============================ memory =======================================
    "AT-48": (
        None,
        "This is the idea. Most tools score a call and file it away; we keep a running record per "
        "customer so three faint worries months apart can add up to one real one.",
        [],
        ["A customer whose evidence is spread thin gets caught, where a per-call tool misses them"],
        "",
    ),
    "AT-49": (
        None,
        "Everything else in the product depends on nothing being thrown away.",
        ["Keep a per-customer record that never drops a weak signal"],
        ["No code path deletes or overwrites a stored signal"],
        "",
    ),
    "AT-50": (
        None,
        "A conversation from March should be allowed to change meaning once June arrives.",
        ["Re-run the whole record on every new conversation, not just the new part"],
        ["Adding a conversation updates the score with no manual step",
         "The same inputs always give the same result"],
        "",
    ),
    "AT-51": (
        None,
        "This is the moment the demo turns on, and the one thing no competitor product does.",
        ["Show what each earlier conversation was worth when it arrived, and what it supports now"],
        ["The change in meaning is visible on screen, not asserted in the script"],
        "",
    ),
    "AT-52": (
        None,
        "Carrying scoring that does nothing is worse than not having it — it is complexity we would "
        "have to defend.",
        ["Turn each part of the scoring off in turn and see if results get worse"],
        ["Each part is either shown to earn its place, or removed"],
        "**Where it stands:** they do not earn it. A plain count of signals does as well as decay, "
        "corroboration, channel weighting and confidence weighting combined.",
    ),
    "AT-53": (
        None,
        "Remembering wins on thin-evidence customers and gains nothing elsewhere. So the product is "
        "probably both — ordinary per-call detection plus memory for what it misses — which is what "
        "our submitted brief actually described.",
        ["Work out how the two combine", "Decide which version we would ship"],
        ["We can name the version we would put in front of a bank, and say why"],
        "The obvious combination was worse than either half alone, because the two produce scores "
        "that are not on the same scale. **This is the main open question for Sprint 2.**",
    ),
    # ============================ the agent ====================================
    "AT-54": (
        None,
        "Something has to decide whether a flagged customer is a real case. That is judgement, not "
        "arithmetic, and it is the part that makes this a product rather than a dashboard.",
        [],
        ["A flagged customer produces a case a bank team could act on, with a person deciding"],
        "",
    ),
    "AT-55": (
        None,
        "A worry in a conversation means more if the account agrees with it, and less if it does not.",
        ["Give the agent tools for transactions, balance history, missed payments and past cases"],
        ["Each tool is a plain function that can be tested on its own, with no model involved"],
        "",
    ),
    "AT-56": (
        None,
        "A queue of maybes is not useful. Someone has to say yes, no, or who owns it.",
        ["Decide real case or false alarm", "Route to retention, collections, vulnerability or complaints"],
        ["Every case comes back with a verdict, an owning team and a confidence"],
        "",
    ),
    "AT-57": (
        None,
        "An agent that cannot point at what convinced it cannot be checked by a compliance officer.",
        ["Reject any decision that does not quote real words from a real conversation"],
        ["We publish how often the agent gets it wrong on the first attempt",
         "The quote must be a real span of a real customer turn"],
        "**Found 09 Aug, still open.** We publish 'unresolved evidence: 0', but that is true by "
        "construction — failures are retried until they pass, so it can only ever be zero. It "
        "measures nothing. The real number is the first-attempt failure rate.",
    ),
    "AT-58": (
        None,
        "An agent that can loop forever, or spend without limit, cannot go near a bank.",
        ["Cap steps, retries and money per case", "Always return an answer, even out of budget"],
        ["A test proves the money actually spent stays under the cap, not just that the code "
         "noticed it went over"],
        "**Found and fixed 09 Aug.** The cap existed in the code but the command we actually run "
        "never passed it, so in practice there was no cap while we claimed bounded cost. A test was "
        "also asserting the overspend as correct behaviour.",
    ),
    "AT-59": (
        None,
        "The output has to be something a bank team can act on without asking us what it means.",
        ["What we heard, when, what supports it, what we suggest, and what would change our mind"],
        ["Someone outside the team can read a case file and know what to do next"],
        "",
    ),
    # ============================ review queue =================================
    "AT-60": (
        None,
        "A person decides every action. The system never contacts a customer — that is enforced by "
        "there being no way to.",
        [],
        ["A reviewer can work a ranked list and act on cases"],
        "",
    ),
    "AT-61": (
        "Turn the ranking into a queue a reviewer can work",
        "The ranking already exists inside the evaluation code. It needs to be something a person "
        "can sit in front of.",
        ["Surface the highest-scoring cases first, with evidence attached"],
        ["A reviewer sees a ranked list sized to what a team can actually get through in a day"],
        "",
    ),
    "AT-62": (
        None,
        "Without a recorded decision there is no audit trail, and no feedback for the system.",
        ["Act on it, dismiss it, or send it to another team", "Log who, when and why"],
        ["All three actions work and are recorded"],
        "",
    ),
    "AT-63": (
        None,
        "A queue that keeps showing you the case you already dismissed stops being used.",
        ["Suppress a dismissed case until genuinely new evidence arrives"],
        ["Dismissing suppresses it; new evidence revives it"],
        "",
    ),
    "AT-64": (
        "One case list, several team views",
        "One shared feed several teams read is the difference between a layer and a single tool.",
        ["Same case list, filtered and ranked per team"],
        ["One case appears in more than one team's view, ranked differently, from a single feed"],
        "The agent routes to **four** teams — retention, collections, vulnerability, complaints — so "
        "the views should follow the code rather than the other way round.",
    ),
    # ============================ measurement ==================================
    "AT-65": (
        None,
        "Numbers a judge and a client can both check, produced by a command rather than typed.",
        [],
        ["Every published figure comes from a recorded run with its seed and code version"],
        "",
    ),
    "AT-66": (
        None,
        "This is the experiment the entry rests on. Same data, same reader, same review capacity — "
        "the only difference is whether the system remembers the customer.",
        ["Five versions: forget each call, a plain count, read the last few together, our full "
         "scoring, and a combination"],
        ["Every published number comes from the ten-dataset run, with the counts behind it"],
        "**Where it stands:** on thin-evidence customers, remembering beats forgetting 0.174 to "
        "0.126 — winning 8 of 10 datasets, tying 2, losing none. Across everyone, nothing separates "
        "the approaches.\n"
        "**Found and fixed 09 Aug:** the 'read the last few together' version had a window of 10 "
        "against customers who only have 2-5 conversations, so it never did anything and was "
        "quietly identical to another version. And our headline came from a single run with 39 "
        "relevant customers, where every difference was one or two people.",
    ),
    "AT-67": (
        None,
        "We measure whether the flagging works, but not yet whether the agent's judgement is any good.",
        ["Check verdicts and team routing against the known answers"],
        ["We can state how often the agent is right, and where it goes wrong"],
        "",
    ),
    "AT-68": (
        None,
        "Reading every conversation has to be affordable or the idea does not ship.",
        ["Cost per thousand conversations, and how long a nightly batch takes"],
        ["A cost figure a bank could budget against, with the method behind it"],
        "One live investigation currently costs **$0.078** and takes 33 seconds.",
    ),
    "AT-69": (
        None,
        "Showing the system decline to escalate is more convincing than showing it fire.",
        ["A customer who sounds worrying but is fine, dismissed with reasons"],
        ["The demo includes the agent turning something down and explaining why"],
        "",
    ),
    "AT-70": (
        None,
        "A number typed by hand is a number nobody can check.",
        ["Generate the README figures from a recorded run"],
        ["Someone can clone the repo, run one command, and get the published numbers"],
        "",
    ),
    # ============================ demo =========================================
    "AT-71": (
        None,
        "What the committee and the judges actually see. Sprint 1+2 demo 24 August, Sprint 3 demo "
        "7 September.",
        [],
        ["A demo that runs with no network and cannot be broken on the day"],
        "",
    ),
    "AT-72": (
        None,
        "Several unremarkable conversations weeks apart that together open a case a per-call tool "
        "never would.",
        ["Pick the customer honestly, run the comparison for real, show both"],
        ["The demo says so plainly if the moment fails for the customer it picked"],
        "**Found and fixed 09 Aug.** The demo was rigged. The line for 'this counts as alarming' was "
        "calculated from the final score, so the dramatic moment was guaranteed for any customer — "
        "and next to it we printed a claim about what an ordinary tool would have done without ever "
        "running one. Now the threshold comes from the real review-capacity cut, the comparison "
        "actually runs, and we report how many customers in the dataset show the pattern.",
    ),
    "AT-73": (
        None,
        "A recording beats a live failure on the day.",
        ["Rehearse it, record it, keep the recording current"],
        ["A recorded run exists that could be played if anything breaks"],
        "Due **2026-08-17**, a week before the demo.",
    ),
    "AT-74": (
        None,
        "A bank buyer needs to understand this without any architecture.",
        ["One page: what it listens to, what it opens, what it saves"],
        ["Someone outside the team reads it and can explain the idea back"],
        "",
    ),
    "AT-75": (
        None,
        "Required deliverable: the accuracy, cost and speed summary.",
        ["One page, with the method behind each number"],
        ["Every figure traces to a recorded run"],
        "",
    ),
    "AT-76": (
        None,
        "Required deliverable: how this would actually go into a bank.",
        ["What it reads, what it writes, privacy and retention, where the person sits"],
        ["A reader can tell what would have to be true at their bank for this to run"],
        "",
    ),
    "AT-77": (
        None,
        "Required deliverable: one-minute video and team photos.",
        ["The early conversation, the later one, the case opening"],
        ["A minute of video and the photos, submitted"],
        "",
    ),
    # ============================ practice =====================================
    "AT-78": (
        None,
        "The engineering practice the competition scores directly: reproducible setup, tests that "
        "run themselves, code in the right place, honest claims.",
        [],
        ["A stranger can clone the repo and reproduce our numbers"],
        "",
    ),
    "AT-79": (
        None,
        "Our data has the answers written into it. If anything that reads a conversation can reach "
        "them, every number we publish is worthless.",
        ["Block it at the import level", "Block it at the data level too"],
        ["A test fails if someone adds a way in, whether by importing it or by passing a value "
         "that encodes it"],
        "The import guard alone could never have caught the leak we actually had — a ground-truth "
        "field handed to the tools as a plain number. Both kinds of test now exist.",
    ),
    "AT-80": (
        None,
        "Reproducibility is scored directly, and it is cheap.",
        ["One command regenerates every published number, with seed and code version recorded"],
        ["A clone-and-run produces the numbers in the README"],
        "",
    ),
    "AT-81": (
        None,
        "Catching a break on the next change is much cheaper than catching it before a demo.",
        ["Run tests and checks on every push", "Fail the build if a key is ever committed"],
        ["A push that breaks something goes red without anyone remembering to look"],
        "",
    ),
    "AT-82": (
        None,
        "The competition asks for the prototype in AWS CodeCommit. Right now it is only on a laptop "
        "and a personal remote.",
        ["Push the full history once we have the repository"],
        ["The code is in CodeCommit with its history intact, not squashed into one commit"],
        "",
    ),
}

DATASET_FINDINGS = """**Public data search — findings, 2026-08-09**

We searched for public data that could replace our made-up conversations. US and UK regulators, the
UK, EU, Australian and Canadian ombudsmen, HuggingFace, Kaggle, the LDC telephone corpora, the standard
dialogue benchmarks, and the agent-memory benchmark family.

**The headline: nothing public has what our core idea needs.**

No public dataset anywhere has repeated contacts from the same identifiable customer, over time, in
financial services, with an outcome we can score against. The three that do have repeat-contact
structure each fail on something else:

- **Customer Support on Twitter** — has a persistent author id, but is licensed CC BY-NC-SA with an
  explicit commercial-use gate, and barely any financial brands
- **Switchboard** — genuinely has ~4.4 calls per speaker, but it is small talk, has no outcome, and
  needs a paid licence
- **eRisk / CLPsych and MIMIC** — textbook accumulate-then-label structure, but they are real medical
  and mental-health records under research-only agreements. Off-limits for commercially-owned work.

**What we can use: the CFPB Consumer Complaint Database.**

- 17.0 million complaints, **3.83 million with written narratives**
- Real people, real banks, real financial distress, in our exact domain
- Personal details already removed by the regulator, and consumers opt in to publication
- US federal public domain, free, 1.41 GB, updated the morning of 2026-08-09
- Has outcome labels: company response, whether the consumer disputed it
- **Does not have** any customer identifier — by deliberate privacy design

**The part worth saying out loud.**

Our experiment needs to know, before a word is written, how much evidence was placed in each
conversation. That is what lets us separate "the signal was spread thin" from "the signal was
obvious", and it is the entire basis of the result we report. No real dataset can ever supply that.

So the made-up data is **not a fallback we settled for — it is a requirement of the measurement**. What
we can and now will do is test the reading half of the system against real complaints.

**Rejected, and worth recording that we rejected it:** stitching real complaints together into
invented customer histories. It looks clever and is worse than either option — incoherent people with
contradictory products and locations, and we lose the answer key that makes the measurement possible.
A judge would fairly say we fabricated the customer, fabricated the ordering, and lost our ground
truth in exchange for the appearance of realism.

**Free wins we should take:**

- Adopt the **earliness metrics from CLEF eRisk** (ERDE and latency-weighted F1). Established prior
  art for exactly "accumulate evidence, decide as early as you can".
- Cite **MSC, LoCoMo and LongMemEval** as the recognised multi-session memory benchmarks — and note
  that no equivalent exists for customer service, complaints or financial risk. That absence is an
  originality argument with evidence behind it.

**Sources**, all accessed 2026-08-09: portal https://www.consumerfinance.gov/data-research/consumer-complaints/
· bulk download https://files.consumerfinance.gov/ccdb/complaints.csv.zip (verified 1,411,120,769 bytes)
· scrubbing and opt-in policy https://www.consumerfinance.gov/complaint/data-use/
· mirror https://huggingface.co/datasets/CFPB/consumer-finance-complaints (CC0-1.0)
· https://erisk.irlab.org/"""


def main() -> None:
    jira = Jira()
    print("Applying the house standard to every issue\n")

    for key, (summary, why, doing, done_when, notes) in TICKETS.items():
        if summary:
            jira.set_summary(key, summary)
        jira.set_description(key, description(why, doing, done_when, notes))
        print(f"  {key}  {summary or '(reformatted)'}")

    print("\nAdding the public-data findings as a comment on AT-38")
    jira.comment("AT-38", adf(DATASET_FINDINGS))

    print("Setting due dates")
    for key, date in {"AT-73": "2026-08-17", "AT-38": "2026-08-13"}.items():
        jira.set_due(key, date)
        print(f"  {key}  due {date}")

    print("Sequencing: what blocks what")
    for blocker, blocked in [
        ("AT-38", "AT-42"),  # decide the data before shaping it
        ("AT-38", "AT-43"),
        ("AT-52", "AT-53"),  # know if the mechanisms earn their place before choosing a shape
        ("AT-61", "AT-62"),  # a queue before actions on it
        ("AT-62", "AT-63"),  # actions before feeding dismissals back
        ("AT-66", "AT-75"),  # the numbers before the write-up
        ("AT-72", "AT-73"),  # the demo before recording it
    ]:
        jira.link(blocker, blocked, "Blocks")
        print(f"  {blocker} blocks {blocked}")

    jira.transition("AT-61", IN_PROGRESS)
    jira.transition("AT-42", TODO)
    jira.report()


if __name__ == "__main__":
    main()
