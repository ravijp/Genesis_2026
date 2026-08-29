"""Corpus-side utterance fragments — AUTHORING PASS A.

This module is what gets *planted* into synthetic conversations.

SEPARATION RULE. The extractor's cue vocabulary lives in
`extract_lexicon.py` and was authored as a separate pass, as if by someone who had never seen
this file. The overlap is deliberately partial: some fragments here are phrased in ways the
extractor's cues do not cover, which is where its honest miss rate comes from. Do not "fix"
that overlap — a matcher that catches everything it planted proves nothing.

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
    Fragment("ci-s3", SignalType.CHURN_INTENT, 0.88, "I've already opened an account elsewhere, I just need my direct debits moved off this one."),
    Fragment("ci-m3", SignalType.CHURN_INTENT, 0.58, "My daughter says I'm paying over the odds compared to hers, and she's usually right about this stuff."),
    Fragment("ci-m4", SignalType.CHURN_INTENT, 0.52, "I keep meaning to sort out switching, it's just never the week for it."),
    Fragment("ci-w5", SignalType.CHURN_INTENT, 0.29, "Does the loyalty thing still exist, or did that stop a while back?"),
    Fragment("ci-w6", SignalType.CHURN_INTENT, 0.24, "I've not really needed to come in as much since I set most of it up online with someone else."),
    Fragment("ci-w7", SignalType.CHURN_INTENT, 0.21, "No, nothing wrong, just tidying up which accounts I actually still use."),
    # --- financial distress -------------------------------------------------------
    Fragment("fd-s1", SignalType.FINANCIAL_DISTRESS, 0.95, "I can't make the payment this month, I just can't."),
    Fragment("fd-s2", SignalType.FINANCIAL_DISTRESS, 0.88, "I was made redundant in March and nothing's come in since."),
    Fragment("fd-m1", SignalType.FINANCIAL_DISTRESS, 0.62, "Things have been tight since my hours got cut."),
    Fragment("fd-m2", SignalType.FINANCIAL_DISTRESS, 0.58, "I had to put the shopping on the credit card again."),
    Fragment("fd-w1", SignalType.FINANCIAL_DISTRESS, 0.32, "Can you tell me the very last day I can pay without a charge?"),
    Fragment("fd-w2", SignalType.FINANCIAL_DISTRESS, 0.30, "Is there any way to change the date it comes out?"),
    Fragment("fd-w3", SignalType.FINANCIAL_DISTRESS, 0.26, "What happens if it bounces, does that show up anywhere?"),
    Fragment("fd-w4", SignalType.FINANCIAL_DISTRESS, 0.24, "I'm juggling a few things at the moment, that's all."),
    Fragment("fd-s3", SignalType.FINANCIAL_DISTRESS, 0.86, "I've had two letters about arrears now and I don't know how I'm going to catch it up."),
    Fragment("fd-m3", SignalType.FINANCIAL_DISTRESS, 0.60, "I've started using the overdraft most months now, which I never used to."),
    Fragment("fd-m4", SignalType.FINANCIAL_DISTRESS, 0.54, "My other half's hours got cut too, so it's both of us at once at the minute."),
    Fragment("fd-w5", SignalType.FINANCIAL_DISTRESS, 0.31, "Is there a minimum you have to pay off the card, or can it just be whatever?"),
    Fragment("fd-w6", SignalType.FINANCIAL_DISTRESS, 0.25, "I moved the gym membership to yearly, works out cheaper that way."),
    Fragment("fd-w7", SignalType.FINANCIAL_DISTRESS, 0.22, "We're doing a proper look at the outgoings this month, spring clean sort of thing."),
    # --- complaint escalation -----------------------------------------------------
    Fragment("ce-s1", SignalType.COMPLAINT_ESCALATION, 0.92, "This is the fourth time I've called about this and nobody has fixed it."),
    Fragment("ce-m1", SignalType.COMPLAINT_ESCALATION, 0.60, "I was promised a callback last week and it never came."),
    Fragment("ce-w1", SignalType.COMPLAINT_ESCALATION, 0.30, "I did raise this before, I think in the spring."),
    Fragment("ce-w2", SignalType.COMPLAINT_ESCALATION, 0.27, "Is there a reference number from the last time I rang?"),
    Fragment("ce-s2", SignalType.COMPLAINT_ESCALATION, 0.90, "I want this put in writing and I want to know how to take it to the ombudsman if it isn't sorted."),
    Fragment("ce-s3", SignalType.COMPLAINT_ESCALATION, 0.85, "I've been passed to four different people today and not one of them has actually done anything."),
    Fragment("ce-m2", SignalType.COMPLAINT_ESCALATION, 0.63, "Can I speak to someone above you, no offence, I just need this actually resolved."),
    Fragment("ce-m3", SignalType.COMPLAINT_ESCALATION, 0.57, "I thought we'd fixed this back in the spring, and now it's happening again."),
    Fragment("ce-m4", SignalType.COMPLAINT_ESCALATION, 0.51, "I've put a complaint in through the website as well, just so it's on record twice."),
    Fragment("ce-w3", SignalType.COMPLAINT_ESCALATION, 0.34, "Nobody's got back to me about the email I sent, but I know things get busy."),
    Fragment("ce-w4", SignalType.COMPLAINT_ESCALATION, 0.29, "Can you tell me what the process is if I'm not happy with how this gets handled?"),
    Fragment("ce-w5", SignalType.COMPLAINT_ESCALATION, 0.25, "I mentioned it to someone on the online chat too, not sure if that went anywhere."),
    Fragment("ce-w6", SignalType.COMPLAINT_ESCALATION, 0.23, "It's fine, I'll just mention it again if it happens a third time."),
    Fragment("ce-w7", SignalType.COMPLAINT_ESCALATION, 0.20, "I did post something about it, just venting really, on the socials."),
    # --- life event ---------------------------------------------------------------
    Fragment("le-s1", SignalType.LIFE_EVENT, 0.85, "My husband passed away in June and I'm sorting out the accounts."),
    Fragment("le-m1", SignalType.LIFE_EVENT, 0.55, "We're separating, so I need to look at what's in joint names."),
    Fragment("le-w1", SignalType.LIFE_EVENT, 0.30, "I'll be changing my address soon, I'm moving back in with family."),
    Fragment("le-w2", SignalType.LIFE_EVENT, 0.26, "I'm on statutory pay at the moment so the numbers look odd."),
    Fragment("le-s2", SignalType.LIFE_EVENT, 0.87, "We had the baby three weeks early, so I'm ringing round sorting everything out from the hospital, basically."),
    Fragment("le-s3", SignalType.LIFE_EVENT, 0.83, "I'm retiring at the end of the month, so I need to talk through what happens to the pension payments."),
    Fragment("le-m2", SignalType.LIFE_EVENT, 0.61, "My mum's moved in with us now, she can't really manage on her own anymore."),
    Fragment("le-m3", SignalType.LIFE_EVENT, 0.56, "We're emigrating in the autumn, so I'll need to know what happens to the account once we're not resident here."),
    Fragment("le-m4", SignalType.LIFE_EVENT, 0.50, "It's a second wedding for both of us, so we're trying to work out what stays separate."),
    Fragment("le-w3", SignalType.LIFE_EVENT, 0.33, "Our eldest starts university in September, so there'll be a new standing order for her."),
    Fragment("le-w4", SignalType.LIFE_EVENT, 0.29, "The house we were buying fell through last week, so the deposit's coming back in, I think."),
    Fragment("le-w5", SignalType.LIFE_EVENT, 0.25, "My partner's in a consultation at work, nothing decided yet, but it's on our minds."),
    Fragment("le-w6", SignalType.LIFE_EVENT, 0.22, "I've been going back and forth to appointments with my dad a lot lately, that's why the odd hours calling."),
    Fragment("le-w7", SignalType.LIFE_EVENT, 0.20, "Just updating a few details, nothing major, my circumstances have shifted a bit this year."),
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
# channels and months — and never lead to an outcome. Without them nothing in the corpus
# punishes an over-eager accumulator.
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
