"""Corpus-side utterance fragments — AUTHORING PASS A.

This module is what gets *planted* into synthetic conversations.

SEPARATION RULE. The extractor's cue vocabulary lives in
`extract_lexicon.py` and was authored as a separate pass, as if by someone who had never seen
this file. The overlap is deliberately partial: some fragments here are phrased in ways the
extractor's cues do not cover, which is where its honest miss rate comes from. Do not "fix"
that overlap — a matcher that catches everything it planted proves nothing, and the whole
originality claim collapses when a judge notices.

`tests/test_separation.py` asserts the extractor cannot import this module.
"""

from __future__ import annotations

from dataclasses import dataclass

from .schema import SignalType


@dataclass(frozen=True)
class Fragment:
    fragment_id: str
    signal_type: SignalType
    strength: float  # 0..1, the fragment's intrinsic loudness
    text: str


# Strong fragments are unambiguous. Weak ones are the ones that matter: individually they
# should read as unremarkable to a human reviewer, and only add up across an arc.
PLANTS: tuple[Fragment, ...] = (
    # --- churn intent -------------------------------------------------------------
    Fragment("ci-s1", SignalType.CHURN_INTENT, 0.95, "I want to close the account, this week."),
    Fragment("ci-s2", SignalType.CHURN_INTENT, 0.90, "Send me whatever form I need to move my money out."),
    Fragment("ci-m1", SignalType.CHURN_INTENT, 0.60, "My colleague keeps telling me her bank does this for free."),
    Fragment("ci-m2", SignalType.CHURN_INTENT, 0.55, "I've started looking at what else is out there, honestly."),
    Fragment("ci-w1", SignalType.CHURN_INTENT, 0.30, "Is there a fee if I ever wanted to take the balance elsewhere?"),
    Fragment("ci-w2", SignalType.CHURN_INTENT, 0.28, "How long does it take to get a full statement history exported?"),
    Fragment("ci-w3", SignalType.CHURN_INTENT, 0.25, "I don't use half of what I'm paying for here anymore."),
    Fragment("ci-w4", SignalType.CHURN_INTENT, 0.22, "My salary goes into the other one now, it's just easier."),
    # --- financial distress -------------------------------------------------------
    Fragment("fd-s1", SignalType.FINANCIAL_DISTRESS, 0.95, "I can't make the payment this month, I just can't."),
    Fragment("fd-s2", SignalType.FINANCIAL_DISTRESS, 0.88, "I was made redundant in March and nothing's come in since."),
    Fragment("fd-m1", SignalType.FINANCIAL_DISTRESS, 0.62, "Things have been tight since my hours got cut."),
    Fragment("fd-m2", SignalType.FINANCIAL_DISTRESS, 0.58, "I had to put the shopping on the credit card again."),
    Fragment("fd-w1", SignalType.FINANCIAL_DISTRESS, 0.32, "Can you tell me the very last day I can pay without a charge?"),
    Fragment("fd-w2", SignalType.FINANCIAL_DISTRESS, 0.30, "Is there any way to change the date it comes out?"),
    Fragment("fd-w3", SignalType.FINANCIAL_DISTRESS, 0.26, "What happens if it bounces, does that show up anywhere?"),
    Fragment("fd-w4", SignalType.FINANCIAL_DISTRESS, 0.24, "I'm juggling a few things at the moment, that's all."),
    # --- complaint escalation -----------------------------------------------------
    Fragment("ce-s1", SignalType.COMPLAINT_ESCALATION, 0.92, "This is the fourth time I've called about this and nobody has fixed it."),
    Fragment("ce-m1", SignalType.COMPLAINT_ESCALATION, 0.60, "I was promised a callback last week and it never came."),
    Fragment("ce-w1", SignalType.COMPLAINT_ESCALATION, 0.30, "I did raise this before, I think in the spring."),
    Fragment("ce-w2", SignalType.COMPLAINT_ESCALATION, 0.27, "Is there a reference number from the last time I rang?"),
    # --- life event ---------------------------------------------------------------
    Fragment("le-s1", SignalType.LIFE_EVENT, 0.85, "My husband passed away in June and I'm sorting out the accounts."),
    Fragment("le-m1", SignalType.LIFE_EVENT, 0.55, "We're separating, so I need to look at what's in joint names."),
    Fragment("le-w1", SignalType.LIFE_EVENT, 0.30, "I'll be changing my address soon, I'm moving back in with family."),
    Fragment("le-w2", SignalType.LIFE_EVENT, 0.26, "I'm on statutory pay at the moment so the numbers look odd."),
)

# Decoys, kind 1 (extractor-targeted): lexically close to a real signal, semantically not one.
# Attribution to a third party, hypotheticals, past-tense-resolved, rhetorical venting.
DECOYS_EXTRACTOR: tuple[Fragment, ...] = (
    Fragment("dx-1", SignalType.CHURN_INTENT, 0.0, "My brother closed his account with you lot last year, mind."),
    Fragment("dx-2", SignalType.CHURN_INTENT, 0.0, "If the fees ever doubled I'd walk, but they haven't, so."),
    Fragment("dx-3", SignalType.FINANCIAL_DISTRESS, 0.0, "I couldn't pay it back in 2019, but that's all sorted now."),
    Fragment("dx-4", SignalType.FINANCIAL_DISTRESS, 0.0, "A friend of mine lost her job and the bank was awful to her."),
    Fragment("dx-5", SignalType.COMPLAINT_ESCALATION, 0.0, "Honestly the app is a nightmare, but I'm not complaining, I know it's not you."),
    Fragment("dx-6", SignalType.CHURN_INTENT, 0.0, "I read an article about switching bonuses, not that I'd bother."),
)

# Decoys, kind 2 (accumulator-targeted): GENUINE weak signals that corroborate across
# channels and months — and never lead to an outcome. v1 had no equivalent, which meant
# nothing in the corpus could ever punish an over-eager accumulator.
DECOYS_ACCUMULATOR: tuple[Fragment, ...] = (
    Fragment("da-1", SignalType.FINANCIAL_DISTRESS, 0.30, "Cashflow's a bit lumpy this quarter, it always is."),
    Fragment("da-2", SignalType.FINANCIAL_DISTRESS, 0.28, "Can I move the direct debit to just after payday?"),
    Fragment("da-3", SignalType.CHURN_INTENT, 0.26, "I'm comparing a few providers for the business, standard review."),
    Fragment("da-4", SignalType.CHURN_INTENT, 0.24, "What's the notice period on the savings one, just so I know?"),
    Fragment("da-5", SignalType.FINANCIAL_DISTRESS, 0.25, "I keep the balance low on purpose, stops me spending it."),
)

# Filler: the majority of real conversations are about nothing. Without this the extraction
# task is trivial and every downstream number is worthless.
FILLER_CUSTOMER: tuple[str, ...] = (
    "I just need to check the balance on the current account.",
    "Has the standing order to the gym gone out yet?",
    "The card reader at the shop wouldn't take it, is there a block?",
    "Can you read me the last three transactions?",
    "I've lost the card, I think it's in the car actually.",
    "What's the sort code again, I never remember it.",
    "Do I need to tell you if I'm going abroad these days?",
    "The app logged me out and now it wants a code I don't have.",
    "Is the branch on the high street still open on Saturdays?",
    "I want to set up a new payee, a plumber.",
    "There's a charge for four pounds I don't recognise.",
    "Can you send a replacement card to the new address?",
    "Someone told me there's a better savings rate now.",
    "I need a mortgage statement for the accountant.",
    "Just checking the transfer landed, it says pending.",
)

FILLER_AGENT: tuple[str, ...] = (
    "Of course, let me pull that up for you.",
    "Can I take the first and third character of your memorable word?",
    "Thanks for holding, I appreciate your patience.",
    "I can see that here on the account.",
    "Just so you know, this call may be recorded for training purposes.",
    "Let me check that with the relevant team, bear with me.",
    "Is there anything else I can help you with today?",
    "That's now updated on our side.",
    "I'm sorry to hear that, let me see what I can do.",
    "You should receive that within three to five working days.",
)

OPENINGS: tuple[str, ...] = (
    "Thank you for calling, you're speaking with Sam, how can I help?",
    "Good afternoon, how can I help today?",
    "Hi there, thanks for getting in touch.",
)

CLOSINGS: tuple[str, ...] = (
    "Thanks for your time, have a good day.",
    "Glad we got that sorted, take care.",
    "If anything else comes up, just give us a ring.",
)

BY_TYPE: dict[SignalType, tuple[Fragment, ...]] = {
    st: tuple(f for f in PLANTS if f.signal_type == st) for st in SignalType
}
