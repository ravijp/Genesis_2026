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

from .schema import Channel, SignalType


@dataclass(frozen=True)
class Fragment:
    """One plantable utterance, plus the arc conditions under which it is TRUE.

    The gating fields exist because until 2026-08-31 the corpus contradicted itself in prose a
    judge reads before they read any number. *"This is the fourth time I've called about this
    and nobody has fixed it"* was planted 9 times in 10 into an arc where the customer had made
    fewer than four contacts, and 34 of 126 plantings of a back-reference fragment landed in the
    customer's FIRST conversation, where there is nothing to refer back to.

    These are plan-side conditions, not prose-side ones. Every one of them is decided from
    quantities the planner has already fixed -- the conversation's position in the arc, its day,
    and whether the promise the agent made last time was kept -- before a word of text exists.
    The answer key is still authored before the prose; this only stops the planner authoring a
    key that the prose then has to lie about.
    """

    fragment_id: str
    signal_type: SignalType
    strength: float  # 0..1, the fragment's intrinsic loudness
    text: str
    # Minimum number of EARLIER conversations in this customer's arc. 0 = plantable on first
    # contact. 1 = "I raised this before". 3 = "this is the fourth time".
    requires_prior: int = 0
    # The fragment claims the bank said it would do something and did not. Only true where the
    # planner actually scheduled a broken promise in the preceding contact.
    requires_broken_promise: bool = False
    # Earliest corpus day the fragment can be spoken, for text naming a calendar month. Day 0
    # is 1 February (`corpus.CORPUS_EPOCH`), so a fragment saying "in March" needs day >= 28.
    earliest_day: int = 0
    # Alternative surfaces for the SAME evidence. Used for two things: so one customer never
    # says the identical sentence twice (the decoy paths plant in every conversation, and a
    # human repeating a sentence verbatim is the tell), and so two different customers in the
    # queue are not shown the identical flagship quote. The `fragment_id`, `signal_type` and
    # `strength` are unchanged, because it is the same piece of evidence -- only the wording
    # moves. The ledger's corroboration bonus therefore behaves exactly as before.
    paraphrases: tuple[str, ...] = ()

    def surfaces(self) -> tuple[str, ...]:
        """Every legitimate wording of this fragment, canonical form first."""
        return (self.text, *self.paraphrases)

    def plantable_at(
        self, *, position: int, day: int, prior_promise_broken: bool
    ) -> bool:
        """Is this fragment true, said here, by this customer, on this day?"""
        if position < self.requires_prior:
            return False
        if self.requires_broken_promise and not prior_promise_broken:
            return False
        return day >= self.earliest_day


# Strong fragments are unambiguous. Weak ones are the ones that matter: individually they
# should read as unremarkable to a human reviewer, and only add up across an arc.
PLANTS: tuple[Fragment, ...] = (
    # --- churn intent -------------------------------------------------------------
    Fragment(
        "ci-s1", SignalType.CHURN_INTENT, 0.95,
        "I want to close the account, this week.",
        paraphrases=(
            "I want the account closed, and I'd like it done this week.",
            "Can we get the account closed? This week, ideally.",
        ),
    ),
    Fragment(
        "ci-s2", SignalType.CHURN_INTENT, 0.90,
        "Send me whatever form I need to move my money out.",
        paraphrases=(
            "Whatever form I need to move my money out, send it.",
            "Just post me the form for moving the money out, please.",
        ),
    ),
    Fragment(
        "ci-m1", SignalType.CHURN_INTENT, 0.60,
        "My colleague keeps telling me her bank does this for free.",
        paraphrases=(
            "A woman at work keeps telling me her bank does all this for free.",
            "My colleague's bank does this for free, she keeps saying.",
        ),
    ),
    Fragment(
        "ci-m2", SignalType.CHURN_INTENT, 0.55,
        "I've started looking at what else is out there, honestly.",
        paraphrases=(
            "I have started looking at what else is out there, if I'm honest.",
            "Honestly, I've begun having a look at what else is out there.",
        ),
    ),
    Fragment(
        "ci-w1", SignalType.CHURN_INTENT, 0.30,
        "Is there a fee if I ever wanted to take the balance elsewhere?",
        paraphrases=(
            "Would there be a fee if I ever took the balance elsewhere?",
            "If I ever moved the balance elsewhere, is there a fee for that?",
        ),
    ),
    Fragment(
        "ci-w2", SignalType.CHURN_INTENT, 0.28,
        "How long does it take to get a full statement history exported?",
        paraphrases=(
            "How long would a full statement history take to export?",
            "If I asked for the full statement history exported, how long is that?",
        ),
    ),
    Fragment(
        "ci-w3", SignalType.CHURN_INTENT, 0.25,
        "I don't use half of what I'm paying for here anymore.",
        paraphrases=(
            "Half of what I'm paying for here I don't use anymore.",
            "I'm paying for things here I don't use half of these days.",
        ),
    ),
    Fragment(
        "ci-w4", SignalType.CHURN_INTENT, 0.22,
        "My salary goes into the other one now, it's just easier.",
        paraphrases=(
            "The salary goes into the other account now, it's simpler that way.",
            "My wages land in the other one these days, it's just easier.",
        ),
    ),
    Fragment(
        "ci-s3", SignalType.CHURN_INTENT, 0.88,
        "I've already opened an account elsewhere, I just need my direct debits moved off this one.",
        paraphrases=(
            "The new account's already open elsewhere. I just need the direct debits moved off this one.",
            "I've opened one somewhere else already, so it's the direct debits I need moving off here.",
        ),
    ),
    Fragment(
        "ci-m3", SignalType.CHURN_INTENT, 0.58,
        "My daughter says I'm paying over the odds compared to hers, and she's usually right about this stuff.",
        paraphrases=(
            "My daughter reckons I'm paying over the odds next to hers, and she's normally right about this sort of thing.",
            "According to my daughter I'm paying over the odds compared to hers, and she does tend to be right.",
        ),
    ),
    Fragment(
        "ci-m4", SignalType.CHURN_INTENT, 0.52,
        "I keep meaning to sort out switching, it's just never the week for it.",
        paraphrases=(
            "Switching is one of those things I keep meaning to sort out, and it's never the right week.",
            "I keep saying I'll get round to switching, it's just never the week.",
        ),
    ),
    Fragment(
        "ci-w5", SignalType.CHURN_INTENT, 0.29,
        "Does the loyalty thing still exist, or did that stop a while back?",
        paraphrases=(
            "Is the loyalty thing still going, or did that get stopped?",
            "That loyalty thing you had, does it still exist?",
        ),
    ),
    Fragment(
        "ci-w6", SignalType.CHURN_INTENT, 0.24,
        "I've not really needed to come in as much since I set most of it up online with someone else.",
        paraphrases=(
            "Since I set most of it up online with someone else I've not needed to come in much.",
            "I don't come in as much now, most of it's set up online with someone else.",
        ),
    ),
    Fragment(
        "ci-w7", SignalType.CHURN_INTENT, 0.21,
        "No, nothing wrong, just tidying up which accounts I actually still use.",
        paraphrases=(
            "Nothing's wrong, I'm just tidying up which accounts I actually use.",
            "No problem as such, I'm having a tidy-up of the accounts I still use.",
        ),
    ),
    # --- financial distress -------------------------------------------------------
    Fragment(
        "fd-s1", SignalType.FINANCIAL_DISTRESS, 0.95,
        "I can't make the payment this month, I just can't.",
        paraphrases=(
            "I can't make this month's payment. I just can't do it.",
            "There's no way I can make the payment this month, I'm sorry.",
        ),
    ),
    Fragment(
        "fd-s2", SignalType.FINANCIAL_DISTRESS, 0.88,
        "I was made redundant in March and nothing's come in since.",
        # "in March" is a calendar claim. Day 0 is 1 February, so this needs a day in March or
        # later or the sentence contradicts the timeline it is planted into.
        earliest_day=28,
        paraphrases=(
            "They made me redundant in March and nothing has come in since then.",
            "I was made redundant back in March, and nothing's come in since.",
        ),
    ),
    Fragment(
        "fd-m1", SignalType.FINANCIAL_DISTRESS, 0.62,
        "Things have been tight since my hours got cut.",
        paraphrases=(
            "Since my hours got cut things have been tight.",
            "It's been tight since they cut my hours.",
        ),
    ),
    Fragment(
        "fd-m2", SignalType.FINANCIAL_DISTRESS, 0.58,
        "I had to put the shopping on the credit card again.",
        paraphrases=(
            "The shopping went on the credit card again this week.",
            "I've had to put the shopping on the credit card again.",
        ),
    ),
    Fragment(
        "fd-w1", SignalType.FINANCIAL_DISTRESS, 0.32,
        "Can you tell me the very last day I can pay without a charge?",
        paraphrases=(
            "What's the very last day I can pay before there's a charge?",
            "When's the latest I can pay without a charge going on?",
        ),
    ),
    Fragment(
        "fd-w2", SignalType.FINANCIAL_DISTRESS, 0.30,
        "Is there any way to change the date it comes out?",
        paraphrases=(
            "Can the date it comes out be changed at all?",
            "Is it possible to move the date it comes out?",
        ),
    ),
    Fragment(
        "fd-w3", SignalType.FINANCIAL_DISTRESS, 0.26,
        "What happens if it bounces, does that show up anywhere?",
        paraphrases=(
            "If it bounces, does that show up anywhere?",
            "What happens if one bounces? Does it go on a record somewhere?",
        ),
    ),
    Fragment(
        "fd-w4", SignalType.FINANCIAL_DISTRESS, 0.24,
        "I'm juggling a few things at the moment, that's all.",
        paraphrases=(
            "I'm juggling a few bits at the moment, that's all it is.",
            "There's a few things I'm juggling just now, nothing more than that.",
        ),
    ),
    Fragment(
        "fd-s3", SignalType.FINANCIAL_DISTRESS, 0.86,
        "I've had two letters about arrears now and I don't know how I'm going to catch it up.",
        paraphrases=(
            "Two letters about arrears have come now and I don't know how I catch it up.",
            "That's two arrears letters now, and I honestly don't know how I'm meant to catch up.",
        ),
    ),
    Fragment(
        "fd-m3", SignalType.FINANCIAL_DISTRESS, 0.60,
        "I've started using the overdraft most months now, which I never used to.",
        paraphrases=(
            "The overdraft gets used most months now, and it never used to.",
            "I'm into the overdraft most months these days, which I never was before.",
        ),
    ),
    Fragment(
        "fd-m4", SignalType.FINANCIAL_DISTRESS, 0.54,
        "My other half's hours got cut too, so it's both of us at once at the minute.",
        paraphrases=(
            "My other half's hours got cut as well, so it's the pair of us at the minute.",
            "They cut my other half's hours too, so we're both in it at once just now.",
        ),
    ),
    Fragment(
        "fd-w5", SignalType.FINANCIAL_DISTRESS, 0.31,
        "Is there a minimum you have to pay off the card, or can it just be whatever?",
        paraphrases=(
            "Is there a minimum on the card, or can I pay whatever?",
            "Does the card have a minimum you have to pay, or is it up to you?",
        ),
    ),
    Fragment(
        "fd-w6", SignalType.FINANCIAL_DISTRESS, 0.25,
        "I moved the gym membership to yearly, works out cheaper that way.",
        paraphrases=(
            "The gym membership's gone to yearly, it works out cheaper.",
            "I've put the gym membership on yearly, cheaper that way.",
        ),
    ),
    Fragment(
        "fd-w7", SignalType.FINANCIAL_DISTRESS, 0.22,
        "We're doing a proper look at the outgoings this month, spring clean sort of thing.",
        paraphrases=(
            "We're having a proper look at the outgoings this month, a bit of a spring clean.",
            "It's a proper look at the outgoings this month, spring-clean sort of thing.",
        ),
    ),
    # --- complaint escalation -----------------------------------------------------
    #
    # Eleven of these assert a PRIOR CONTACT and are gated on arc position. That gate left only
    # three fragments plantable on a customer's first contact, which would have emptied the
    # opening conversation of every complaint arc, so `ce-s4`..`ce-w9` were authored as what a
    # FIRST complaint sounds like -- somebody who has just been let down, not somebody chasing.
    Fragment(
        "ce-s1", SignalType.COMPLAINT_ESCALATION, 0.92,
        "This is the fourth time I've called about this and nobody has fixed it.",
        requires_prior=3, requires_broken_promise=True,
        paraphrases=(
            "That's four times I've called about this now and nobody has fixed it.",
            "This is the fourth time of asking and it still isn't fixed.",
        ),
    ),
    Fragment(
        "ce-m1", SignalType.COMPLAINT_ESCALATION, 0.60,
        "I was promised a callback and it never came.",
        requires_prior=1, requires_broken_promise=True,
        paraphrases=(
            "Somebody promised me a callback and it never came.",
            "I was told I'd get a callback. It never came.",
        ),
    ),
    Fragment(
        "ce-w1", SignalType.COMPLAINT_ESCALATION, 0.30,
        "I did raise this before, I'm fairly sure I did.",
        requires_prior=1,
        paraphrases=(
            "I'm fairly sure I raised this before.",
            "I did bring this up before, I'm certain of it.",
        ),
    ),
    Fragment(
        "ce-w2", SignalType.COMPLAINT_ESCALATION, 0.27,
        "Is there a reference number from the last time I rang?",
        requires_prior=1,
        paraphrases=(
            "Would there be a reference number from the last time I rang?",
            "From last time I rang, is there a reference number on there?",
        ),
    ),
    Fragment(
        "ce-s2", SignalType.COMPLAINT_ESCALATION, 0.90,
        "I want this put in writing and I want to know how to take it to the ombudsman if it isn't sorted.",
        requires_prior=1,
        paraphrases=(
            "Put this in writing please, and tell me how I take it to the ombudsman if it isn't sorted.",
            "I want it in writing, and I want to know the route to the ombudsman if this isn't sorted.",
        ),
    ),
    Fragment(
        "ce-s3", SignalType.COMPLAINT_ESCALATION, 0.85,
        "I've been passed round three departments since this started and not one of them has actually done anything.",
        requires_prior=1,
        # The old wording said "four different people today", which was false in a corpus where
        # no conversation has more than one agent. Passed round ACROSS contacts is true here.
        paraphrases=(
            "Three departments have had this since it started and not one of them has done anything.",
            "Since this started I've been passed round three departments and none of them has actually done a thing.",
        ),
    ),
    Fragment(
        "ce-m2", SignalType.COMPLAINT_ESCALATION, 0.63,
        "Can I speak to someone above you, no offence, I just need this actually resolved.",
        requires_prior=1,
        paraphrases=(
            "No offence, but can I speak to someone above you? I just need this resolved.",
            "Is there someone above you I can speak to? Nothing personal, I just need it sorted.",
        ),
    ),
    Fragment(
        "ce-m3", SignalType.COMPLAINT_ESCALATION, 0.57,
        "I thought we'd sorted this last time, and now it's happening again.",
        requires_prior=1,
        paraphrases=(
            "I was under the impression we'd sorted this last time, and here it is again.",
            "We sorted this last time, or I thought we had, and now it's back.",
        ),
    ),
    Fragment(
        "ce-m4", SignalType.COMPLAINT_ESCALATION, 0.51,
        "I've put a complaint in through the website as well, just so it's on record twice.",
        requires_prior=1,
        paraphrases=(
            "I've also put a complaint in through the website, so it's on record twice.",
            "There's a complaint gone in through the website too, just so it's recorded twice.",
        ),
    ),
    Fragment(
        "ce-w3", SignalType.COMPLAINT_ESCALATION, 0.34,
        "Nobody's got back to me about the email I sent, but I know things get busy.",
        requires_prior=1,
        paraphrases=(
            "No one has got back to me about that email, though I know things get busy.",
            "I've had nothing back about the email I sent. I know you're busy, mind.",
        ),
    ),
    Fragment(
        "ce-w4", SignalType.COMPLAINT_ESCALATION, 0.29,
        "Can you tell me what the process is if I'm not happy with how this gets handled?",
        paraphrases=(
            "What's the process if I'm not happy with how this gets handled?",
            "If I end up unhappy with how this is handled, what's the process?",
        ),
    ),
    Fragment(
        "ce-w5", SignalType.COMPLAINT_ESCALATION, 0.25,
        "I mentioned it to someone last time as well, not sure if that went anywhere.",
        requires_prior=1,
        paraphrases=(
            "I did mention it to someone last time too, don't know if it went anywhere.",
            "Someone had this from me last time as well, though I don't think it went anywhere.",
        ),
    ),
    Fragment(
        "ce-w6", SignalType.COMPLAINT_ESCALATION, 0.23,
        "It's fine, I'll just mention it again if it happens a third time.",
        requires_prior=2,
        paraphrases=(
            "It's fine. If it happens a third time I'll mention it again.",
            "Not to worry, I'll say something again if there's a third time.",
        ),
    ),
    Fragment(
        "ce-w7", SignalType.COMPLAINT_ESCALATION, 0.20,
        "I did post something about it, just venting really, on the socials.",
        paraphrases=(
            "I put something on the socials about it, just venting really.",
            "I did have a moan about it online, nothing serious.",
        ),
    ),
    Fragment(
        "ce-s4", SignalType.COMPLAINT_ESCALATION, 0.89,
        "I've been charged twice for the same thing and I want this treated as a formal complaint.",
        paraphrases=(
            "Two charges for the same thing, and I'd like it treated as a formal complaint.",
            "I want a formal complaint raised: I've been charged twice for the same thing.",
        ),
    ),
    Fragment(
        "ce-m5", SignalType.COMPLAINT_ESCALATION, 0.59,
        "I'd like this logged as a complaint, please, not just noted on the account.",
        paraphrases=(
            "Please log this as a complaint rather than just a note on the account.",
            "Can this go down as a complaint, not just a note?",
        ),
    ),
    Fragment(
        "ce-m6", SignalType.COMPLAINT_ESCALATION, 0.53,
        "Whoever set this up got it wrong and it has cost me money, and I want that acknowledged.",
        paraphrases=(
            "Somebody set this up wrong, it's cost me money, and I want that acknowledged.",
            "This was set up wrong by someone and it's cost me. I want that acknowledged.",
        ),
    ),
    Fragment(
        "ce-w8", SignalType.COMPLAINT_ESCALATION, 0.32,
        "Is there somewhere I can put in writing that I'm unhappy with how this was handled?",
        paraphrases=(
            "Where would I put in writing that I'm unhappy with how this was handled?",
            "Can I put it in writing somewhere that I'm not happy with how this went?",
        ),
    ),
    Fragment(
        "ce-w9", SignalType.COMPLAINT_ESCALATION, 0.28,
        "It's not a disaster, but I do think somebody should know it happened.",
        paraphrases=(
            "It's no disaster, but somebody ought to know it happened.",
            "Not the end of the world, but I think someone should know about it.",
        ),
    ),
    # --- life event ---------------------------------------------------------------
    Fragment(
        "le-s1", SignalType.LIFE_EVENT, 0.85,
        "My husband passed away earlier this year and I'm sorting out the accounts.",
        # Was "passed away in June". The corpus horizon starts on 1 February, so June was in the
        # future for two thirds of the days this could be planted on.
        paraphrases=(
            "I lost my husband earlier this year, and I'm sorting out the accounts.",
            "My husband died earlier this year and I'm working through the accounts.",
        ),
    ),
    Fragment(
        "le-m1", SignalType.LIFE_EVENT, 0.55,
        "We're separating, so I need to look at what's in joint names.",
        paraphrases=(
            "We're separating, so I need to go through what's in joint names.",
            "My partner and I are separating and I need to look at the joint ones.",
        ),
    ),
    Fragment(
        "le-w1", SignalType.LIFE_EVENT, 0.30,
        "I'll be changing my address soon, I'm moving back in with family.",
        paraphrases=(
            "My address is changing soon, I'm going back to live with family.",
            "I'm moving back in with family, so the address will be changing.",
        ),
    ),
    Fragment(
        "le-w2", SignalType.LIFE_EVENT, 0.26,
        "I'm on statutory pay at the moment so the numbers look odd.",
        paraphrases=(
            "I'm on statutory pay just now, which is why the numbers look odd.",
            "The numbers look odd because I'm on statutory pay at the moment.",
        ),
    ),
    Fragment(
        "le-s2", SignalType.LIFE_EVENT, 0.87,
        "We had the baby three weeks early, so I'm ringing round sorting everything out from the hospital, basically.",
        paraphrases=(
            "The baby came three weeks early, so I'm ringing round from the hospital sorting everything out.",
            "We had the baby three weeks early and I'm sorting everything out from a hospital chair, basically.",
        ),
    ),
    Fragment(
        "le-s3", SignalType.LIFE_EVENT, 0.83,
        "I'm retiring at the end of the month, so I need to talk through what happens to the pension payments.",
        paraphrases=(
            "I retire at the end of the month and I need to go through what happens to the pension payments.",
            "End of the month I'm retired, so I need to understand what happens to the pension payments.",
        ),
    ),
    Fragment(
        "le-m2", SignalType.LIFE_EVENT, 0.61,
        "My mum's moved in with us now, she can't really manage on her own anymore.",
        paraphrases=(
            "Mum's living with us now, she can't manage on her own anymore.",
            "My mother has moved in with us, she wasn't managing on her own.",
        ),
    ),
    Fragment(
        "le-m3", SignalType.LIFE_EVENT, 0.56,
        "We're emigrating in the autumn, so I'll need to know what happens to the account once we're not resident here.",
        paraphrases=(
            "We emigrate in the autumn, so I need to know what happens to the account when we're not resident.",
            "We're going abroad for good in the autumn and I'll need to know what happens to the account then.",
        ),
    ),
    Fragment(
        "le-m4", SignalType.LIFE_EVENT, 0.50,
        "It's a second wedding for both of us, so we're trying to work out what stays separate.",
        paraphrases=(
            "It's a second marriage for the two of us, so we're working out what stays separate.",
            "We're both marrying for the second time, so we're deciding what to keep separate.",
        ),
    ),
    Fragment(
        "le-w3", SignalType.LIFE_EVENT, 0.33,
        "Our eldest starts university in September, so there'll be a new standing order for her.",
        paraphrases=(
            "Our eldest is off to university in September, so there's a new standing order to set up.",
            "The eldest starts university in September and she'll need a standing order.",
        ),
    ),
    Fragment(
        "le-w4", SignalType.LIFE_EVENT, 0.29,
        "The house we were buying fell through last week, so the deposit's coming back in, I think.",
        paraphrases=(
            "The house purchase fell through last week, so the deposit should be coming back in.",
            "We lost the house last week, so I think the deposit comes back in.",
        ),
    ),
    Fragment(
        "le-w5", SignalType.LIFE_EVENT, 0.25,
        "My partner's in a consultation at work, nothing decided yet, but it's on our minds.",
        paraphrases=(
            "My partner is in a work consultation, nothing decided, but it's on our minds.",
            "There's a consultation on at my partner's work. Nothing settled yet, but we're thinking about it.",
        ),
    ),
    Fragment(
        "le-w6", SignalType.LIFE_EVENT, 0.22,
        "I've been going back and forth to appointments with my dad a lot lately, that's why the odd hours calling.",
        paraphrases=(
            "I'm back and forth to appointments with my dad a lot at the moment, hence the odd hours.",
            "Lots of appointments with my dad lately, which is why I ring at strange times.",
        ),
    ),
    Fragment(
        "le-w7", SignalType.LIFE_EVENT, 0.20,
        "Just updating a few details, nothing major, my circumstances have shifted a bit this year.",
        paraphrases=(
            "Just a few details to update, nothing major. Circumstances have shifted a bit this year.",
            "Nothing major, just updating details. Things have shifted a bit for me this year.",
        ),
    ),
)

# Decoys, kind 1 (extractor-targeted): lexically close to a real signal, semantically not one.
# Attribution to a third party, hypotheticals, past-tense-resolved, rhetorical venting.
DECOYS_EXTRACTOR: tuple[Fragment, ...] = (
    Fragment(
        "dx-1", SignalType.CHURN_INTENT, 0.0,
        "My brother closed his account with you lot last year, mind.",
        paraphrases=(
            "My brother shut his account with you last year, mind you.",
            "It was my brother who closed his account with you, last year that was.",
        ),
    ),
    Fragment(
        "dx-2", SignalType.CHURN_INTENT, 0.0,
        "If the fees ever doubled I'd walk, but they haven't, so.",
        paraphrases=(
            "I'd walk if the fees ever doubled, but they haven't, so there we are.",
            "Double the fees and I'd be off, but you haven't, so it's fine.",
        ),
    ),
    Fragment(
        "dx-3", SignalType.FINANCIAL_DISTRESS, 0.0,
        "I couldn't pay it back in 2019, but that's all sorted now.",
        paraphrases=(
            "Back in 2019 I couldn't pay it, but that's long sorted.",
            "There was a time in 2019 I couldn't pay it. All sorted now.",
        ),
    ),
    Fragment(
        "dx-4", SignalType.FINANCIAL_DISTRESS, 0.0,
        "A friend of mine lost her job and the bank was awful to her.",
        paraphrases=(
            "A friend of mine lost her job and her bank was awful about it.",
            "One of my friends lost her job and the bank treated her terribly.",
        ),
    ),
    Fragment(
        "dx-5", SignalType.COMPLAINT_ESCALATION, 0.0,
        "Honestly the app is a nightmare, but I'm not complaining, I know it's not you.",
        paraphrases=(
            "The app is a nightmare, honestly. Not a complaint, mind, I know it's not you.",
            "That app of yours is a nightmare. I'm not complaining at you, it's not your doing.",
        ),
    ),
    Fragment(
        "dx-6", SignalType.CHURN_INTENT, 0.0,
        "I read an article about switching bonuses, not that I'd bother.",
        paraphrases=(
            "There was an article about switching bonuses. Not that I'd bother.",
            "I saw something about switching bonuses in the paper. Wouldn't bother myself.",
        ),
    ),
)

# Decoys, kind 2 (accumulator-targeted): GENUINE weak signals that corroborate across
# channels and months — and never lead to an outcome. Without them nothing in the corpus
# punishes an over-eager accumulator.
DECOYS_ACCUMULATOR: tuple[Fragment, ...] = (
    Fragment(
        "da-1", SignalType.FINANCIAL_DISTRESS, 0.30,
        "Cashflow's a bit lumpy this quarter, it always is.",
        paraphrases=(
            "Cashflow is a bit lumpy this quarter. It always is, this time of year.",
            "The cashflow's lumpy again this quarter, same as ever.",
        ),
    ),
    Fragment(
        "da-2", SignalType.FINANCIAL_DISTRESS, 0.28,
        "Can I move the direct debit to just after payday?",
        paraphrases=(
            "Could the direct debit move to just after payday?",
            "Is it possible to shift the direct debit to the day after payday?",
        ),
    ),
    Fragment(
        "da-3", SignalType.CHURN_INTENT, 0.26,
        "I'm comparing a few providers for the business, standard review.",
        paraphrases=(
            "I'm comparing a few providers for the business. It's a standard review.",
            "We compare providers for the business every so often, it's just the standard review.",
        ),
    ),
    Fragment(
        "da-4", SignalType.CHURN_INTENT, 0.24,
        "What's the notice period on the savings one, just so I know?",
        paraphrases=(
            "On the savings one, what's the notice period? Just so I know.",
            "Remind me what the notice period is on the savings account.",
        ),
    ),
    Fragment(
        "da-5", SignalType.FINANCIAL_DISTRESS, 0.25,
        "I keep the balance low on purpose, stops me spending it.",
        paraphrases=(
            "I keep that balance low deliberately, it stops me spending it.",
            "The balance stays low on purpose. If it's there I spend it.",
        ),
    ),
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
    "Right, let me take a look at that for you.",
    "Bear with me a moment, I'm just bringing that up.",
    "Thanks - I've put a note on the account so you don't have to say it twice.",
    "Yes, I can see that here.",
    "Let me just check I've got that right before I do anything.",
    "I'll need to check that with the team who look after it - give me a second.",
    "Sorry, can I take you back a step? I want to make sure I've got this right.",
    "Okay, I've made a note of that.",
    "I'm sorry to hear that. Let's see what we can do.",
    "Let me find out for you rather than guess.",
)

# EXACTLY 3, and the CHAT variants are index-matched to them. `agent_opening()` swaps by
# position, so the RNG draw over OPENINGS is what picks and the channel only decides which
# wording that pick renders as. Names vary because one agent called Sam handling 299
# conversations is the sort of detail a contact-centre reader spots immediately.
# The recording notice is INSIDE the call opening rather than a turn of its own. It used to fire
# 893 times, only 135 of them in the first three turns and 591 of them inside a typed channel; a
# separate notice turn would also put two agent turns back to back, which is half of why 52.9% of
# conversations contained an agent->agent run. Folding it into turn 0 makes it true, once, and
# only on the phone.
OPENINGS: tuple[str, ...] = (
    "Thanks for calling, you're through to Priya. The call's recorded for training. Who am I speaking with?",
    "Good afternoon, you're speaking with Daniel, and this call is recorded. How can I help?",
    "Hello, Marcus here - the call's recorded for training and monitoring. What can I do for you today?",
)

CHAT_OPENINGS: tuple[str, ...] = (
    "Hi, you're chatting with Priya. How can I help today?",
    "Hello - Daniel here on chat. What can I help you with?",
    "Hi there, thanks for messaging. Marcus here - what's happened?",
)

# The closings assert the one thing this product is about: the contact is on the record and it
# will still be there next time. Free narrative reinforcement on every non-complaint document.
CLOSINGS: tuple[str, ...] = (
    "That's everything from me. My note's on the account if you need to ring back.",
    "Thanks for your patience with that one. Take care.",
    "If it happens again, ring us and say it's happened before - it's all on the record.",
)

CHAT_CLOSINGS: tuple[str, ...] = (
    "I've saved this chat to your record, so you won't have to start again.",
    "Thanks for bearing with me. I'll leave the chat open a minute in case.",
    "If it comes back, message us and say it's happened before - it's all logged.",
)


# ---------------------------------------------------------------------------------------------
# RESPONSIVE AGENT REPLIES
#
# WHY THIS EXISTS. Until 2026-08-31 every agent turn was `rng.choice(FILLER_AGENT)` -- ten
# strings dealt at random with no reference to what the customer had just said. Measured over
# 1,400 conversations at seed 20260809: 864 of 973 planted signals (88.8%) were answered with a
# non-sequitur, and 77 of the 85 loudest ones (90.6%) were. A customer disclosing a bereavement
# was answered with the call-recording notice. That is not a realism blemish; in a UK retail bank
# it reads as a Consumer Duty failure, and it was on the recorded demo screens.
#
# WHY IT IS FREE. `extract.py` reads only `speaker == "customer"` turns, so agent text cannot
# reach the extractor, the ledger or any published number. The one thing that CAN move them is
# the RNG stream, which is shared with the customer turns. So every selector below takes the
# ALREADY-DRAWN `rng.choice(FILLER_AGENT)` value as its `drawn` argument and uses it only as an
# index. The draw still happens, on a tuple that is still length 10, in the same place in the
# stream. Verified over 3 seeds x 400 customers: every customer turn, every seeded signal, every
# extracted signal and every ledger score byte-identical.
#
# Do NOT resize FILLER_AGENT, OPENINGS or CLOSINGS, and do NOT skip the draw. Either one moves
# every published figure. Measured: resizing FILLER_AGENT 10 -> 14 changed 11,371 of 11,378
# customer turns; replacing the draw with a deterministic pick changed 11,096 of 11,378.
#
# WHAT THE WORDING IS GROUNDED IN. Not invented politeness. Two public sources, read 2026-08-31:
#
#  * FCA, "Delivering good outcomes for customers in vulnerable circumstances - good practice and
#    areas for improvement", 2025-03-07 (updated 2025-12-03), Crown copyright / OGL v3.
#    https://www.fca.org.uk/publications/good-and-poor-practice/delivering-vulnerable-customers
#    Documented GOOD practice: record the disclosure so the customer is not asked twice; keep a
#    consistent named person; do not restart a standard process over a disclosed need. Documented
#    POOR practice: failing to record an accessibility need so the customer repeats it; rigid
#    adherence to process after disclosure; a seven-month delay contacting a bereaved customer.
#    Every acknowledgement below follows the good pattern, and the bereavement reply is written
#    directly against the poor one.
#  * FCA Financial Lives 2024 (published 2025-05-16): 49% of UK adults (26.4m) have a
#    characteristic of vulnerability and only about 4 in 10 of them have ever disclosed it to a
#    provider. An agent who rewards a disclosure rather than talking past it is the whole reason
#    the second number could move -- so the distress and life-event replies thank the customer for
#    saying it.
#  * Turn mechanics (acknowledge -> clarify -> act -> confirm, one move per turn, disfluency left
#    in) follow Taskmaster-1's spoken half: 5,507 dialogues in which trained call-centre operators
#    played the agent, CC BY 4.0.
#    https://github.com/google-research-datasets/Taskmaster/blob/master/TM-1-2019/README.md
#
# NOTHING HERE IS COPIED FROM ANY SOURCE. Competition rules require synthetic or anonymised data
# only. What crossed from the sources above is behaviour and shape -- a documented good-practice
# move, a turn-taking pattern -- never a sentence. All wording is authored.
# ---------------------------------------------------------------------------------------------

# Keyed by `Fragment.fragment_id`, so the reply matches the exact thing that was said rather than
# its signal family: `le-s1` (bereavement) and `le-w3` (a child starting university) are both
# LIFE_EVENT and need nothing in common.
AGENT_REPLIES_TO_SIGNAL: dict[str, tuple[str, ...]] = {
    # --- churn intent ---------------------------------------------------------------------
    "ci-s1": (
        "Okay. Before I start that - can I ask what's prompted it? If we've got something wrong "
        "I'd rather try to fix it.",
        "I can do that. I'd rather not until I understand why, though. What's happened?",
    ),
    "ci-s2": (
        "I'll get that out to you. Can I ask first - is this about the charges, or something else?",
        "There's a switching form, yes. Before I send it, has something gone wrong that I could sort?",
    ),
    "ci-m1": (
        "That's worth looking at. Let me see what you're actually paying and whether you're on the "
        "right account for it.",
        "Fair enough. Let me pull up your charges for the last few months so we're comparing like "
        "for like.",
    ),
    "ci-m2": (
        "That's your right, and I'd rather you told me. Is there something specific pushing you?",
        "Understood. Can I ask what you're looking for that you're not getting from us?",
    ),
    "ci-w1": (
        "No fee to move it out. I'll note that you asked, in case it comes up again.",
        "There isn't one. Is that something you're thinking about, or just checking?",
    ),
    "ci-w2": (
        "Usually a couple of days. Do you need it for something in particular?",
        "I can order that now. Is it for an application, or your own records?",
    ),
    "ci-w3": (
        "Then let's look at that. It may be you're on the wrong account for how you use it now.",
        "That's worth a proper look. Shall I go through what you're being charged for?",
    ),
    "ci-w4": (
        "Noted. Do you want me to leave this one as it is, or change anything?",
        "That's fine. Just so I know - is this one still doing a job for you?",
    ),
    "ci-s3": (
        "Right. The switching service moves them for you and I'll walk you through it. Can I ask "
        "what took you elsewhere?",
        "I can start that. Before I do - was there something here that pushed you to open the other "
        "one?",
    ),
    "ci-m3": (
        "She may well be right. Let me go through what you're actually paying and we'll see.",
        "Then let's check. Do you know which account she's on?",
    ),
    "ci-m4": (
        "I'll leave that with you. If you do want to talk it through, ring and ask for me.",
        "Understood. Is there anything I could sort now that would make you less likely to?",
    ),
    "ci-w5": (
        "That changed a couple of years back. Let me check what applies to your account now.",
        "Let me look it up - I don't want to tell you the wrong thing on that one.",
    ),
    "ci-w6": (
        "That's fine, most people don't come in now. Is everything working the way you want?",
        "Noted. Is there anything you'd still rather do with us in person?",
    ),
    "ci-w7": (
        "Fair enough. Do you want me to list what you've got open with us?",
        "Sensible. I'll note that you're reviewing, in case you ring back about it.",
    ),
    # --- financial distress ---------------------------------------------------------------
    "fd-s1": (
        "Thank you for telling me, that's the right call. Nothing happens today. Let me go through "
        "what we can do.",
        "Right - I'm glad you've rung rather than left it. We can work with this. What's changed?",
    ),
    "fd-s2": (
        "I'm sorry, that's a lot to deal with. Let me stop the standard process and go through your "
        "options properly.",
        "That's really difficult. Before anything else - do you know what's coming in at the moment?",
    ),
    "fd-m1": (
        "Thanks for telling me. Do you want me to look at whether the payment dates could work "
        "better for you?",
        "I'm sorry to hear that. Is it manageable at the moment, or is it getting harder?",
    ),
    "fd-m2": (
        "Okay. Is that a one-off, or has it been a few months now?",
        "Noted. Do you want me to look at what the card's costing you?",
    ),
    "fd-w1": (
        "I'll get you the exact date. Is it tight this month?",
        "Let me check that for you. If the timing's the problem, we can look at moving it.",
    ),
    "fd-w2": (
        "Yes, we can move it. What date would suit you better?",
        "We can do that. Is it landing before payday at the moment?",
    ),
    "fd-w3": (
        "There's a charge, and it can show on your file. Are you expecting one to?",
        "Let me explain what happens - and if you think one might, say so now and we'll avoid it.",
    ),
    "fd-w4": (
        "Okay. If any of it's to do with us, tell me and I'll see what I can do.",
        "Noted. Say the word if you want to go through what's going out.",
    ),
    "fd-s3": (
        "Right. I'm going to stop the letters while we sort this out. Let's go through it properly.",
        "Thank you for ringing rather than ignoring them. Nothing else goes out today. Talk me "
        "through it.",
    ),
    "fd-m3": (
        "That's worth flagging. Do you want me to look at what it's costing you?",
        "Okay. Is that since something changed, or has it crept up?",
    ),
    "fd-m4": (
        "That's a lot at once, I'm sorry. Do you want to go through what's coming out?",
        "Both of you at the same time is hard. I'll note it - and tell me if it gets worse.",
    ),
    "fd-w5": (
        "There's a minimum, and I'll tell you what yours is. Is the full amount difficult this "
        "month?",
        "There is a minimum. Do you want me to go through what happens if you only pay that?",
    ),
    "fd-w6": (
        "Sensible. Do you want me to check for anything else going out you're not using?",
        "That does work out cheaper. Anything else you want me to look at while we're here?",
    ),
    "fd-w7": (
        "Good idea. I can list the direct debits and standing orders if that helps.",
        "I can send you the last three months of regular payments if it's useful.",
    ),
    # --- complaint escalation ---------------------------------------------------------------
    "ce-s1": (
        "Then I'm not passing you on again. I'll own this one and come back to you myself with an "
        "answer.",
        "Four times is four too many. I'm logging this as a complaint now so it's tracked properly.",
    ),
    "ce-m1": (
        "That shouldn't have happened and I'm sorry. Let me find the note and see what went wrong.",
        "That's on us. Give me a moment - I want to see who took that call.",
    ),
    "ce-w1": (
        "Let me look back through your contacts and find it, rather than start you from scratch.",
        "I'll go back and read what was said last time before you have to tell it again.",
    ),
    "ce-w2": (
        "There should be. Let me pull up your previous contacts and read it to you.",
        "Yes - give me a second and I'll find it, so we're both looking at the same case.",
    ),
    "ce-s2": (
        "That's your right. I'll log a formal complaint now and send the written response, with the "
        "ombudsman details in it.",
        "Understood, and you'll get that in writing. Let me raise it properly before we go any "
        "further.",
    ),
    "ce-s3": (
        "I'm not passing you to anyone else. Whatever this needs, I'll do it from here or come "
        "back to you myself.",
        "That's a poor experience and I'm sorry. Stay with me - I'll sort it or find who can.",
    ),
    "ce-m2": (
        "None taken. I'll get a manager, and I'll brief them first so you're not starting again.",
        "Of course. Let me tell them what's happened so you don't have to repeat all of it.",
    ),
    "ce-m3": (
        "Then it wasn't fixed. Let me find what was done last time and why it hasn't held.",
        "That's frustrating. I'll look at what we did before, rather than doing the same thing "
        "again.",
    ),
    "ce-m4": (
        "That's fine - I'll link them, so you get one answer rather than two.",
        "Noted. I'll make sure they're joined up rather than handled separately.",
    ),
    "ce-w3": (
        "It shouldn't matter how busy we are. Let me find your email and chase it.",
        "You shouldn't have to wait for that. Let me see where it's got to.",
    ),
    "ce-w4": (
        "Yes, and I'll put it in writing. You come to us first, and then the ombudsman if you're "
        "still not happy.",
        "I'll explain it properly - it's worth knowing either way.",
    ),
    "ce-w5": (
        "Let me check the chat notes so we're not starting from the beginning.",
        "I'll look for it. If it wasn't logged, I'll log it now.",
    ),
    "ce-w6": (
        "I'd rather you didn't have to. Let me note it now, so there's a record either way.",
        "Let me log it anyway. If there is a third time, it won't be your word against ours.",
    ),
    "ce-w7": (
        "Fair enough. Is there anything in it I can actually fix while you're on?",
        "I'd rather sort it here. What was it that got to you?",
    ),
    "ce-s4": (
        "That's not right and I'm not going to argue it with you. I'm raising it as a formal complaint now, and I'll get the second charge back while it's open.",
        "Charged twice for the same thing is our error, not a dispute. I'm logging the complaint and refunding the duplicate today.",
    ),
    "ce-m5": (
        "Yes, and you're right to ask. A note isn't a complaint and it doesn't get looked at. I'm opening it properly, and you'll get the reference.",
        "It'll go down as a complaint, not a note. That means someone has to answer it in writing, which is what you want.",
    ),
    "ce-m6": (
        "It was set up wrong, and I can see where. I'm not going to pretend otherwise -- I'll put that in the complaint in those words.",
        "You're owed an acknowledgement, not an explanation of our process. I'll say plainly what went wrong when I write to you.",
    ),
    "ce-w8": (
        "There is, and I'll do it from here rather than send you off to find a form. Tell me what you'd want it to say.",
        "You can, and you shouldn't have to hunt for it. I'll start it now and you can add to it.",
    ),
    "ce-w9": (
        "I'd rather know than not. I'll write it up even though you're not making a fuss about it -- that's how the pattern gets spotted.",
        "It matters even if nothing came of it. I'm recording it, so it's there if it happens again.",
    ),
    # --- life event ---------------------------------------------------------------------------
    "le-s1": (
        "I'm very sorry. Let me stop what I'm doing - I'll take the details once and pass you to the "
        "bereavement team, so you don't have to go through it again.",
        "I'm so sorry for your loss. There's no rush from our side. I'll note it now so nobody asks "
        "you to explain it twice.",
    ),
    "le-m1": (
        "I'm sorry. Let me list the joint accounts, and I'll explain what needs both of you and what "
        "doesn't.",
        "That's a difficult one. I'll note it on the account so you're not explaining it every time "
        "you ring.",
    ),
    "le-w1": (
        "I'll get that changed whenever you're ready. Is the move something you've chosen?",
        "Just let me know when. Is there anything else changing that I should know about?",
    ),
    "le-w2": (
        "Thanks for saying, that helps me read the account properly. How long is that likely to be?",
        "Noted. If anything gets difficult while you're on it, ring us early rather than late.",
    ),
    "le-s2": (
        "Congratulations - and that's a lot to be doing from a hospital. Let's do the essential bit "
        "now, the rest can wait.",
        "Congratulations. I'll keep this short then. What's the one thing you need done today?",
    ),
    "le-s3": (
        "Congratulations. That's worth doing properly - let me book you time with someone rather "
        "than rush it now.",
        "Let's go through it. Do you know yet what's coming in, and when?",
    ),
    "le-m2": (
        "That's a big change. If you end up managing anything of hers, tell us and we'll explain "
        "what's needed.",
        "Noted, and I'm sorry. Is there anything about her accounts you need to ask while you're on?",
    ),
    "le-m3": (
        "There are rules on that and I'd rather get it right. Let me find out properly and come back "
        "to you.",
        "Good to know early. Let me check what changes and what stays the same.",
    ),
    "le-m4": (
        "Congratulations. You don't have to join anything up - let me explain the options.",
        "That's a fair question. I'll go through what a joint account does and doesn't change.",
    ),
    "le-w3": (
        "I can set that up whenever you're ready. Do you know the amount and the date?",
        "Congratulations to her. Let me know when you want it starting.",
    ),
    "le-w4": (
        "Sorry to hear that. Let me check when the money's due to land.",
        "That's a blow. I'll watch for it coming in and note it, so it isn't flagged as unusual.",
    ),
    "le-w5": (
        "Thanks for telling me. Nothing to do now, but ring us early if it goes the wrong way.",
        "Noted. If it does change things we've got options - better to know before than after.",
    ),
    "le-w6": (
        "Not a problem at all, ring whenever suits you. I hope he's doing okay.",
        "That's fine, we're open late. I'll note it so nobody questions the timing.",
    ),
    "le-w7": (
        "No problem. Anything you want me to record while we're here?",
        "That's fine. If any of it changes what you need from us, just say.",
    ),
    # --- extractor decoys: NOT signals. The agent treats them as conversation, which is the -----
    # --- correct behaviour and also what makes them read as decoys to a human reviewer. --------
    "dx-1": (
        "Well, I hope we didn't drive him to it. Anything you need doing today?",
        "Fair enough. Was there something on yours you wanted sorting?",
    ),
    "dx-2": (
        "Understood. We'd have to write to you before anything changed, either way.",
        "Noted. We'd tell you in advance if they did.",
    ),
    "dx-3": (
        "Glad that's behind you. It shouldn't be affecting anything now.",
        "Thanks for the context. That's a long time ago now.",
    ),
    "dx-4": (
        "That shouldn't happen. If she's still stuck, tell her to ring and ask for the support team.",
        "I'm sorry to hear that. It's not how it should go.",
    ),
    "dx-5": (
        "You can complain, it's fine. Is it one particular thing, or all of it?",
        "Say it anyway, it's useful. What's it doing?",
    ),
    "dx-6": (
        "They come and go. Nothing you need to do.",
        "There are a few about. Happy to check what you'd be giving up, if you ever wanted.",
    ),
    # --- accumulator decoys: genuine weak signals that never amount to anything. A mild, ------
    # --- correct response -- neither ignoring them nor over-reacting. --------------------------
    "da-1": (
        "Same every year, is it? Let me know if the dates need moving.",
        "Noted. Say if you want anything shifted to suit.",
    ),
    "da-2": (
        "Yes, easily done. What date do you get paid?",
        "We can do that. When would you like it going out?",
    ),
    "da-3": (
        "Sensible. Do you want me to put together what you're paying us?",
        "Fair enough. Let me know if you need figures from our side.",
    ),
    "da-4": (
        "Let me check the exact terms rather than guess at it.",
        "I'll look it up - it depends which one you're on.",
    ),
    "da-5": (
        "Whatever works. Just watch the overdraft if anything lands unexpectedly.",
        "Makes sense. Let me know if you want an alert setting up.",
    ),
}

# Keyed by the FILLER_CUSTOMER line as authored, BEFORE ASR noise is applied -- `corpus.py`
# hoists the draw so the clean string is what reaches this map. An agent who answers the mundane
# question is what makes the surrounding conversation read as a conversation, and it is 82.5% of
# all agent turns.
AGENT_REPLIES_TO_FILLER: dict[str, tuple[str, ...]] = {
    "I just need to check the balance on the current account.": (
        "Of course. Do you want the available balance or the cleared one?",
        "I've got it here. There's one payment still to clear, so I'll give you both figures.",
    ),
    "Has the standing order to the gym gone out yet?": (
        "Let me look - yes, that went out on the second.",
        "Checking now. I can see it's set up and due, but it hasn't left yet.",
    ),
    "The card reader at the shop wouldn't take it, is there a block?": (
        "Nothing on our side stopping it. Did it say declined, or just not read at all?",
        "No block that I can see. It may have been their terminal. Try it once more and ring me if "
        "it fails again.",
    ),
    "Can you read me the last three transactions?": (
        "Yes - a card payment, a direct debit and a transfer in. Do you want the amounts?",
        "Of course. Do you want them from today, or from the start of the week?",
    ),
    "I've lost the card, I think it's in the car actually.": (
        "I can freeze it rather than cancel it, so if it turns up you just unfreeze it.",
        "Have a look before I cancel it - if it's gone for good I'll order you a new one.",
    ),
    "What's the sort code again, I never remember it.": (
        "No problem, nobody does. Let me get that for you now.",
        "It's in the app under account details too, if that's easier next time.",
    ),
    "Do I need to tell you if I'm going abroad these days?": (
        "You don't, not any more. The card should just work.",
        "No need. Only worth a word if you want to know about the charges.",
    ),
    "The app logged me out and now it wants a code I don't have.": (
        "That'll be the new device check. I can send a fresh code now if you're by your phone.",
        "Annoying, I know. Let me reset it from this end for you.",
    ),
    "Is the branch on the high street still open on Saturdays?": (
        "It is, mornings only - nine till one.",
        "Let me check the hours rather than tell you wrong.",
    ),
    "I want to set up a new payee, a plumber.": (
        "I can do that. Do you have the sort code and account number?",
        "Yes - I'll need their details, and I'll confirm them back to you before it saves.",
    ),
    "There's a charge for four pounds I don't recognise.": (
        "Let me look at it. Do you want me to raise a dispute while I'm here?",
        "I can see it. Give me a second and I'll tell you where it's come from.",
    ),
    "Can you send a replacement card to the new address?": (
        "I'll need to update the address first, then order it. Is the new one already on file?",
        "Yes - let me confirm the address with you before I order it.",
    ),
    "Someone told me there's a better savings rate now.": (
        "There are a few. Let me see what you're on at the moment.",
        "Depends what you're after. Do you need to get at the money, or can it sit?",
    ),
    "I need a mortgage statement for the accountant.": (
        "I can order that. Do you need the current year or the last full one?",
        "No problem. Post, or shall I put it in your secure messages?",
    ),
    "Just checking the transfer landed, it says pending.": (
        "Pending usually clears the same day. Let me see if it's moved.",
        "I can see it here. It should be with them today.",
    ),
}

# A COMPLAINT is a written document handled by a case handler, not a live call. Until the channel
# is restructured properly (which changes turn counts, and therefore every published number),
# this at least stops the complaint channel talking like a phone call. Keyed by signal family
# rather than fragment, because a written acknowledgement is generic by nature -- that is what
# makes it a written acknowledgement.
COMPLAINT_REPLIES_BY_TYPE: dict[str, tuple[str, ...]] = {
    SignalType.CHURN_INTENT.value: (
        "Thank you for writing in. I've opened a case and I'll look at your charges before I reply "
        "properly.",
        "I've read this and opened a case. I'd like to understand what's driven it before you go "
        "anywhere.",
    ),
    SignalType.FINANCIAL_DISTRESS.value: (
        "Thank you for telling us. I've paused any further letters while I look at this, and I'll "
        "come back to you within five working days.",
        "I've read this and put a hold on the account while we sort it out. You don't need to do "
        "anything today.",
    ),
    SignalType.COMPLAINT_ESCALATION.value: (
        "I've logged this as a formal complaint. It will not be closed until you have a written "
        "answer.",
        "This is now a formal complaint with a case reference, and I'll be handling it myself.",
    ),
    SignalType.LIFE_EVENT.value: (
        "Thank you for letting us know. I've recorded it, so you will not be asked to explain it "
        "again.",
        "I'm sorry to hear this. I've noted it on the account and I'll make sure the right team "
        "picks it up.",
    ),
    "none": (
        "Thanks for your message. I've picked this up and I'll come back to you.",
        "Received, and logged. I'll reply once I've checked it.",
    ),
}


_FILLER_AGENT_INDEX: dict[str, int] = {line: i for i, line in enumerate(FILLER_AGENT)}


def _variant(variants: tuple[str, ...], drawn: str) -> str:
    """Choose among `variants` using the ALREADY-DRAWN filler line as the index source.

    `drawn` is the value `rng.choice(FILLER_AGENT)` returned. Using its position rather than a
    fresh `rng` call is the whole trick: the RNG stream is untouched, so nothing the extractor
    reads can move, while the agent still varies.

    With ten filler lines and two variants the split is exactly 5/5. A variant tuple whose length
    does not divide 10 is mildly biased toward its early entries; that is cosmetic and does not
    reach any measured quantity.
    """
    return variants[_FILLER_AGENT_INDEX.get(drawn, 0) % len(variants)]


# Below this intrinsic strength a planted line is a passing remark, not a disclosure, and a
# written case handler would not open anything on it.
FORMAL_ACKNOWLEDGEMENT_FLOOR = 0.50


def agent_reply_to_signal(
    fragment_id: str, signal_type: SignalType, strength: float, channel: Channel, drawn: str
) -> str:
    """The agent's reply to a PLANTED customer utterance.

    The strength gate is not decoration. Keying the written acknowledgement on signal TYPE alone
    made the case handler answer *"I mentioned it to someone on the online chat too, not sure if
    that went anywhere"* (`ce-w5`, strength 0.25) with "I've logged this as a formal complaint" --
    on 261 complaint plants, 84 of them DECOYS. An agent who formally escalates
    *"the app is a nightmare, but I'm not complaining"* is both wrong about that customer and
    wrong about this product: the entry's whole claim is that the quiet ones go unactioned at the
    time and only add up later. An over-reacting agent argues against us on our own screen.

    Note this changes agent prose only. Which signals are planted, how loud they are and what the
    ledger does with them are untouched -- `strength` is read here purely to choose wording.
    """
    if channel is Channel.COMPLAINT and strength >= FORMAL_ACKNOWLEDGEMENT_FLOOR:
        return _variant(COMPLAINT_REPLIES_BY_TYPE[signal_type.value], drawn)
    # Falls back to `drawn` itself when a fragment has no mapped reply, because
    # `_variant(FILLER_AGENT, drawn) is drawn`. A new fragment therefore degrades to the old
    # behaviour rather than raising -- and the coverage check keeps the map complete.
    return _variant(AGENT_REPLIES_TO_SIGNAL.get(fragment_id, FILLER_AGENT), drawn)


def agent_reply_to_filler(customer_line: str, channel: Channel, drawn: str) -> str:
    """The agent's reply to an ordinary FILLER customer turn.

    The same map serves all three channels. Routing COMPLAINT here rather than to the written
    acknowledgement was a deliberate second pass: sending every complaint filler turn to
    `COMPLAINT_REPLIES_BY_TYPE["none"]` produced 1,290 copies of one sentence, 12.0% of every
    agent turn in the corpus -- trading the old monoculture for a worse, more concentrated one.
    The mundane answers below read equally well typed, so the written case-handler voice is now
    reserved for the turn that matters: the reply to a planted signal.
    """
    return _variant(AGENT_REPLIES_TO_FILLER.get(customer_line, FILLER_AGENT), drawn)


def agent_opening(channel: Channel, drawn: str) -> str:
    """Channel-correct opening, chosen by the POSITION of the already-drawn OPENINGS value.

    Fixes the most obvious tell in the corpus: 129 of 450 chat conversations (28.7%) opened
    "Thank you for calling, you're speaking with Sam".
    """
    pool = CHAT_OPENINGS if channel is Channel.CHAT else OPENINGS
    try:
        return pool[OPENINGS.index(drawn)]
    except ValueError:  # pragma: no cover - only if OPENINGS is edited without CHAT_OPENINGS
        return drawn


def agent_closing(channel: Channel, drawn: str) -> str:
    """Channel-correct closing, chosen by the POSITION of the already-drawn CLOSINGS value."""
    pool = CHAT_CLOSINGS if channel is Channel.CHAT else CLOSINGS
    try:
        return pool[CLOSINGS.index(drawn)]
    except ValueError:  # pragma: no cover
        return drawn


# ---------------------------------------------------------------------------------------------
# REASON FOR CONTACT, AND THE THREAD BETWEEN CONTACTS  —  Phase C
#
# WHAT WAS WRONG. Until 2026-08-31 a conversation was a bag of unrelated questions. The customer
# never said why they were in touch, nothing was ever resolved, and `_render_conversation` took
# no prior conversation at all -- measured over 22,114 turns, the strings "I called", "as I said"
# and "you said" appeared zero times, and every one of the 41 hits for "last time" / "last week"
# / "reference number" was inside a planted fragment's fixed text. An arc was N independent
# scenes that happened to share a customer id. That is a problem for THIS entry specifically:
# the whole claim is that evidence accumulates across contacts, and the corpus we demonstrate it
# on had no notion of a previous contact.
#
# WHAT REPLACES IT. Every conversation now has:
#
#   * a REASON FOR CONTACT, stated by the customer in their first turn;
#   * body turns drawn from that reason's own follow-ups, so the conversation is ABOUT something;
#   * an ending in which the agent either resolves it or makes a specific undertaking;
#   * and, from the second contact onward, an opening that names the last contact, how long ago
#     it was, and whether the undertaking was kept.
#
# WHO DECIDES KEPT-OR-BROKEN. The planner, in `corpus.generate`, before any prose exists -- see
# `_promise_schedule`. Prose never writes the answer key. What the schedule does is make the
# key HONEST: a `complaint_escalation` arc is one where the bank keeps not doing what it said,
# so "this is the fourth time I've called and nobody has fixed it" is planted only into an arc
# that actually contains three earlier contacts and a broken undertaking.
#
# THE INTENT TAXONOMY. The fifteen reasons below are the fifteen existing `FILLER_CUSTOMER`
# lines, promoted from filler to reasons, and named with intent ids in the style of the Bitext
# retail-banking intent list (26 intents over 9 categories, CDLA-Sharing-1.0,
# huggingface.co/datasets/bitext/Bitext-retail-banking-llm-chatbot-training-dataset, read
# 2026-08-31). **The taxonomy only.** That dataset's own card says its pairs are NLG-generated,
# so its text is worth nothing to us; its list of what retail customers actually contact a bank
# about is worth having as a checked inventory. Every sentence below is authored here.
#
# Deliberately, the fifteen reasons are all OPERATIONAL and none of them is a signal. A reason
# like "I want to close my savings account" would put unplanted churn evidence into conversations
# the answer key says are empty, which is the one thing this generator may never do.
#
# WRITTEN-CHANNEL SHAPE. `benchmarks/cfpb/out/sample.jsonl` -- 150 real CFPB narratives, CC0,
# already committed -- measured 2026-08-31: single author, no turn-taking, min 11 words, median
# 155, mean 184, p90 354. The complaint scaffolding below is built to that shape and to nothing
# else. No sentence is taken from it; `tests/test_corpus.py` asserts no fragment of ours shares
# a six-word run with any of those narratives.
# ---------------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Topic:
    """One reason a customer gets in touch, and everything the conversation needs to be about it.

    `opener` is the customer's statement of why they are calling and is one of the fifteen
    `FILLER_CUSTOMER` lines, so `AGENT_REPLIES_TO_FILLER` already holds an authored
    acknowledgement for it and nothing from Phase A is wasted.
    """

    topic_id: str  # Bitext-style intent name; the taxonomy, never the text
    opener: str  # == the matching FILLER_CUSTOMER entry
    subject: str  # short noun phrase, for "I rang about {subject}"
    undertaking: str  # what the agent says it will do when it cannot finish today
    followups: tuple[tuple[str, str], ...]  # (customer turn, agent reply), topic-consistent
    narrative: tuple[str, ...]  # the same ground, WRITTEN: declarative, past tense, no questions
    resolved: tuple[str, ...]  # agent's closing when it IS done in this contact
    promised: tuple[str, ...]  # agent's closing when it is NOT; names the undertaking
    chase: tuple[str, ...]  # customer's line when contacting again about the same thing


TOPICS: tuple[Topic, ...] = (
    Topic(
        topic_id="check_balance",
        narrative=(
            "I was given a figure that turned out to include items that had not yet come off, so I budgeted against money that was not there.",
            "When I asked for the pending items to be set out separately I was told that was not something that could be done over the phone.",
        ),
        opener="I just need to check the balance on the current account.",
        subject="the balance on the current account",
        undertaking="a written breakdown of the pending items",
        followups=(
            ("Is that the figure before the direct debits go out, or after?",
             "That's the available figure, so before the two due on Friday."),
            ("There's something showing as pending, does that count in it?",
             "Not yet - pending items come off once the retailer claims them."),
            ("Can you tell me what it was at the start of the month?",
             "I can, give me a second to pull the statement up."),
        ),
        resolved=(
            "Right, that's the balance confirmed, and I've noted that you asked about it.",
            "That's it confirmed. It's on the account that we went through it today.",
        ),
        promised=(
            "I can't see the pending side from here, so I'll send you a written breakdown of the pending items.",
            "I'll get a written breakdown of the pending items out to you rather than guess at it now.",
        ),
        chase=(
            "the breakdown never turned up",
            "I've still not had that breakdown",
        ),
    ),
    Topic(
        topic_id="check_direct_debit",
        narrative=(
            "The payment should have left on the second of the month and it did not, and the gym has since written to me about it.",
            "I was told not to set up a replacement in case it went twice, and then nothing happened at all.",
        ),
        opener="Has the standing order to the gym gone out yet?",
        subject="the standing order to the gym",
        undertaking="a check with the payments team",
        followups=(
            ("It normally leaves on the second, and it's the fifth today.",
             "You're right, it should have gone on the second. Let me see what's happened."),
            ("The gym have emailed me saying they've not had it.",
             "I can see why they'd say that - it hasn't left us."),
            ("Do I need to set it up again from scratch?",
             "No, don't do that yet. If we set up a second one you'll pay twice."),
        ),
        resolved=(
            "That's gone now, so nothing more for you to do.",
            "It's left the account this morning. I've noted why it was late.",
        ),
        promised=(
            "I'll put in a check with the payments team on why it hasn't left, and you'll hear back.",
            "I'm raising it with the payments team now. Don't cancel anything in the meantime.",
        ),
        chase=(
            "nobody came back to me about the standing order",
            "the standing order still hasn't gone",
        ),
    ),
    Topic(
        topic_id="card_payment_declined",
        narrative=(
            "My card was declined in a shop with a queue behind me, and I had been given no warning that anything had been flagged.",
            "I later found the same block stopped me taking cash out, which nobody had mentioned when I first reported it.",
        ),
        opener="The card reader at the shop wouldn't take it, is there a block?",
        subject="the card being declined in the shop",
        undertaking="the block lifted",
        followups=(
            ("It went through fine on Saturday, it's only since then.",
             "That fits - something's flagged on it since the weekend."),
            ("It was embarrassing, to be honest, there was a queue behind me.",
             "I'm sorry, that shouldn't happen without us telling you first."),
            ("Will it work at the cash machine, or is that stopped as well?",
             "Cash machines are on the same block, so no, not until it's lifted."),
        ),
        resolved=(
            "That's the block off. Try a small amount first so you're not caught out again.",
            "It's cleared now, and I've noted why so it doesn't flag again.",
        ),
        promised=(
            "I can't lift it myself, so I've asked for the block to be taken off and a note put on the account.",
            "I've requested it is lifted and noted why. Use another card today if you can.",
        ),
        chase=(
            "the card is still being declined",
            "the block is still on it",
        ),
    ),
    Topic(
        topic_id="check_transactions",
        narrative=(
            "I asked for a list of recent transactions because one of them was not familiar to me, and I was read three of them and told the rest were not available.",
            "I was told a paper copy would follow so that I could go through them properly, and it did not arrive.",
        ),
        opener="Can you read me the last three transactions?",
        subject="the last few transactions",
        undertaking="a copy of last month's transactions in the post",
        followups=(
            ("The middle one, who is that with? I don't know the name.",
             "That's the trading name - it's usually the parking app."),
            ("Can you go back a bit further, say the last ten?",
             "I can. I'll take them one at a time, stop me if you need one repeating."),
            ("Is there a way to see these without the app?",
             "There is, we can post a statement or you can pick one up in branch."),
        ),
        resolved=(
            "That's all three confirmed and noted. Anything you want disputing, get back to us and quote today.",
            "Confirmed and logged. If one of those turns out to be wrong we've got today on record.",
        ),
        promised=(
            "The older ones aren't on my screen, so I'll send a copy of last month's transactions in the post.",
            "I'll order a paper copy rather than go through half of them here.",
        ),
        chase=(
            "the statement copy never arrived",
            "I'm still waiting on those transactions",
        ),
    ),
    Topic(
        topic_id="report_lost_card",
        narrative=(
            "I reported the card missing and asked for it to be frozen rather than cancelled, because I was fairly sure it was in the car.",
            "I was told a replacement would be sent and given a timescale, and I made arrangements around that timescale.",
        ),
        opener="I've lost the card, I think it's in the car actually.",
        subject="the lost card",
        undertaking="a replacement card",
        followups=(
            ("If I find it in the car tonight, can I just carry on using it?",
             "If we freeze it rather than cancel it, yes - I'd freeze it for now."),
            ("Nothing's gone out on it that I don't recognise, I checked.",
             "Good, and I'll keep an eye on it from this end for a few days."),
            ("How long does a new one take if I do need it?",
             "Five working days as a rule, and it comes separately from the PIN."),
        ),
        resolved=(
            "Frozen rather than cancelled, so you can unfreeze it in the app if it turns up.",
            "That's frozen for now. If the car search works out, unfreeze it and carry on.",
        ),
        promised=(
            "I've ordered a replacement card, and I've frozen the old one so nothing can go on it.",
            "There's a replacement card on order. Give it five working days before you chase.",
        ),
        chase=(
            "the replacement card hasn't come",
            "no card has arrived",
        ),
    ),
    Topic(
        topic_id="account_details",
        narrative=(
            "I asked for the sort code and account number to be confirmed in writing, because somebody was paying money in and wanted it written down.",
            "I was told it would be posted out and it never came, so the payment was delayed by a fortnight.",
        ),
        opener="What's the sort code again, I never remember it.",
        subject="the sort code and account number",
        undertaking="the account details in writing",
        followups=(
            ("Is that the same one for the savings, or a different code?",
             "Different account number, same sort code."),
            ("Someone's paying money in and they want it written down.",
             "I'd send it in writing rather than have you write it down from me."),
            ("Does it change if I move branch?",
             "No, it stays with the account wherever you are."),
        ),
        resolved=(
            "That's the details confirmed, and it's noted that you asked today.",
            "Confirmed, and noted. No need to come back to us for the same thing.",
        ),
        promised=(
            "Rather than give it out here, I'll have the account details sent to you in writing.",
            "I'll get them to you in writing - safer that way.",
        ),
        chase=(
            "nothing came in writing",
            "those details never arrived",
        ),
    ),
    Topic(
        topic_id="travel_notification",
        narrative=(
            "I told you the dates I would be abroad and asked for a note to go on the account so the card would not be stopped.",
            "The card was stopped anyway, on the second day, and I had to borrow money for the rest of the trip.",
        ),
        opener="Do I need to tell you if I'm going abroad these days?",
        subject="using the card abroad",
        undertaking="a travel note on the account",
        followups=(
            ("It's two weeks, back at the end of the month.",
             "That's fine, and it's worth me noting the dates either way."),
            ("Will I get charged for using it out there?",
             "There's a non-sterling fee on purchases - I'll tell you the rate."),
            ("What do I do if it stops working while I'm away?",
             "There's a number that works from abroad. I'll make sure you've got it."),
        ),
        resolved=(
            "No note needed these days, but I've put the dates on anyway. Have a good trip.",
            "You're all set. I've noted the dates so nothing flags while you're out there.",
        ),
        promised=(
            "I'll get a travel note added to the account so nothing blocks while you're away.",
            "There's a travel note going on now - you should see no difference out there.",
        ),
        chase=(
            "the card was blocked abroad anyway",
            "that travel note clearly never went on",
        ),
    ),
    Topic(
        topic_id="reset_login",
        narrative=(
            "I was locked out of the app because the security code was being sent to a number I stopped using last year.",
            "I asked for the number on file to be corrected and for a code to be sent by post, and neither of those things happened.",
        ),
        opener="The app logged me out and now it wants a code I don't have.",
        subject="being locked out of the app",
        undertaking="a reset code in the post",
        followups=(
            ("It's going to a number I changed last year, I think.",
             "That would do it. The code is going to the old number."),
            ("I've tried it four times and now it says I'm locked.",
             "Yes, it locks after three. That's why it's stopped you."),
            ("Can I do what I need through you instead?",
             "Most of it, yes. Let's do that now and fix the app after."),
        ),
        resolved=(
            "You're unlocked. Give it five minutes before you try, it takes a moment to clear.",
            "That's reset at this end. Log in fresh rather than reopening the old screen.",
        ),
        promised=(
            "I've had a reset code sent out - it goes by post, because the number on file is wrong.",
            "There's a reset code in the post. Don't try again until it lands or it re-locks.",
        ),
        chase=(
            "the reset code never came",
            "I'm still locked out of the app",
        ),
    ),
    Topic(
        topic_id="find_branch",
        narrative=(
            "I travelled to the branch on a Saturday on the strength of the opening hours I was given, and it was closed.",
            "When I rang to ask why, I was told the hours had changed some time ago and that the information I had been given was out of date.",
        ),
        opener="Is the branch on the high street still open on Saturdays?",
        subject="the branch opening hours",
        undertaking="the opening hours confirmed",
        followups=(
            ("I only ask because it was shut when I went last month.",
             "The hours changed, so you wouldn't have known."),
            ("Is there a counter, or is it all machines now?",
             "There's still a counter, though not all day on a Saturday."),
            ("Do I need an appointment for paying in a cheque?",
             "Not for a cheque, no. Appointments are for the longer things."),
        ),
        resolved=(
            "So Saturday morning only. I've noted you asked, in case the hours move again.",
            "Saturdays until midday. That's confirmed on the record now.",
        ),
        promised=(
            "The hours are being reviewed, so I'll get them confirmed and come back to you.",
            "I'd rather not guess - I'll have the hours confirmed and let you know.",
        ),
        chase=(
            "nobody confirmed the hours",
            "I never got those opening hours",
        ),
    ),
    Topic(
        topic_id="setup_payee",
        narrative=(
            "I asked for a new payee to be set up so that I could pay a tradesman four hundred pounds, and I was told the name check had not come back clean.",
            "I was told it would be sorted and confirmed back to me before I sent anything, and I heard nothing.",
        ),
        opener="I want to set up a new payee, a plumber.",
        subject="setting up the new payee",
        undertaking="the payee set up and confirmed",
        followups=(
            ("He's given me the details on a scrap of paper, is that alright?",
             "It's fine, as long as the name matches what his bank holds."),
            ("It's four hundred, so I don't want it going astray.",
             "Understood. We'll check the name against his account before it goes."),
            ("Can I send it today or is there a wait on new ones?",
             "New payees can hold for a few hours the first time. After that it's instant."),
        ),
        resolved=(
            "Payee's on. First payment may hold a couple of hours, then it's normal.",
            "That's set up. It's on your record that we checked the name today.",
        ),
        promised=(
            "The name check didn't come back clean, so I'll get it set up and confirm it back to you.",
            "I'll have it set up and confirmed rather than send four hundred pounds on a maybe.",
        ),
        chase=(
            "the payee still isn't set up",
            "nobody confirmed the payee",
        ),
    ),
    Topic(
        topic_id="dispute_charge",
        narrative=(
            "There is a charge on the account of four pounds that I do not recognise, and it has now appeared three months running.",
            "I asked for it to be raised as a dispute and for the merchant to be blocked, and as far as I can tell neither has been done.",
        ),
        opener="There's a charge for four pounds I don't recognise.",
        subject="the four pound charge",
        undertaking="the charge raised as a dispute",
        followups=(
            ("It's small, I know, but it's the third month it's been there.",
             "Then it's a subscription of some sort, and that's worth stopping."),
            ("I've not signed up to anything, not that I remember.",
             "They're easy to sign up to by accident. Let's find out who it is."),
            ("Can you stop it going out again next month?",
             "I can block that merchant, yes, and I'll tell you what it's called."),
        ),
        resolved=(
            "Refunded and blocked. It's on the record in case it reappears.",
            "That's the four pounds back and the merchant blocked.",
        ),
        promised=(
            "I've had the charge raised as a dispute - you'll get a decision in writing.",
            "It's raised as a dispute now. Don't cancel the card, it won't help.",
        ),
        chase=(
            "the dispute hasn't been decided",
            "the four pounds still hasn't come back",
        ),
    ),
    Topic(
        topic_id="order_replacement_card",
        narrative=(
            "I asked for a replacement card to be sent to my new address, and I made a point of saying that the address you held was the old one.",
            "The card was sent to the old address regardless, to a house I no longer live in, and I have had to ask the new occupants about it.",
        ),
        opener="Can you send a replacement card to the new address?",
        subject="the replacement card to the new address",
        undertaking="the address changed and a card sent to it",
        followups=(
            ("The address on your system is the old one, I moved in February.",
             "It is, so we'd have posted it to the wrong door."),
            ("Does the PIN come with it or separately?",
             "Separately, and usually a day apart."),
            ("What do I do with the old card when it comes?",
             "Cut through the chip and bin it. Don't post it back."),
        ),
        resolved=(
            "Address changed and the card's ordered to the new one.",
            "New address on, card on its way there. It's all noted.",
        ),
        promised=(
            "I've put the address change through and ordered the card to the new one - five working days.",
            "Address updated and a card on its way there. Come back to us if it's not with you in a week.",
        ),
        chase=(
            "the card went to the old address again",
            "the new card still hasn't come",
        ),
    ),
    Topic(
        topic_id="interest_rates",
        narrative=(
            "I asked to see how the rate on my savings compared with what is currently on offer, having been on the same one for several years.",
            "I was told a written comparison would be sent so that I could decide in my own time, and nothing came.",
        ),
        opener="Someone told me there's a better savings rate now.",
        subject="the savings rate",
        undertaking="a written comparison of the two savings rates",
        followups=(
            ("Mine's been on the same one for years, I've never looked.",
             "A lot of people haven't. It's worth the five minutes."),
            ("Is there a catch, do I have to lock it away?",
             "Some of them yes, some no. That's the bit worth comparing."),
            ("Would I lose the interest I've already earned?",
             "No, what's accrued stays yours whatever you move to."),
        ),
        resolved=(
            "So you're on the older rate and there is a better one. I've noted we discussed it.",
            "We've been through both. Nothing's moved yet, and it's on the record that you asked.",
        ),
        promised=(
            "I'll send a written comparison of the two savings rates so you can decide in your own time.",
            "I'd rather you had it in front of you - I'll send a written comparison of the two savings rates.",
        ),
        chase=(
            "the rate comparison never arrived",
            "I never got that comparison",
        ),
    ),
    Topic(
        topic_id="request_statement",
        narrative=(
            "I asked for a mortgage statement covering the last tax year because my accountant needed it, and I gave the deadline at the time.",
            "The statement did not arrive, the deadline passed, and I have had to pay for the accountant's time twice.",
        ),
        opener="I need a mortgage statement for the accountant.",
        subject="the mortgage statement",
        undertaking="the mortgage statement in the post",
        followups=(
            ("It needs to cover the whole of last tax year.",
             "Understood - April to April, not the calendar year."),
            ("Can it come by email, he's asking for a PDF?",
             "Secure message rather than plain email, but yes, effectively a PDF."),
            ("How long do these normally take to come?",
             "Ten working days if it's posted, quicker if it's the secure message."),
        ),
        resolved=(
            "That's it in your secure messages now. Nothing to wait for.",
            "Issued and available to download. It's logged that you asked today.",
        ),
        promised=(
            "I've put in for it to be issued and posted - ten working days.",
            "That's ordered and it will come by post. I've noted the accountant's deadline.",
        ),
        chase=(
            "the mortgage statement never came",
            "the accountant is still waiting on that statement",
        ),
    ),
    Topic(
        topic_id="check_transfer_status",
        narrative=(
            "A transfer left my account and did not arrive at the other end, and the person waiting for it has been chasing me ever since.",
            "I asked for a trace to be put on it and I was told I would hear the outcome either way, and I have heard nothing.",
        ),
        opener="Just checking the transfer landed, it says pending.",
        subject="the pending transfer",
        undertaking="a trace on the transfer",
        followups=(
            ("It went at eleven this morning, it's gone four now.",
             "That's longer than it should be for a normal one."),
            ("The money's left my side, I can see it's gone.",
             "Yes, it's out of here. So it's sitting somewhere in between."),
            ("They're chasing me for it, that's the problem.",
             "Then let's get it traced rather than wait and see."),
        ),
        resolved=(
            "It's landed. Their end just hadn't updated when you looked.",
            "Showing as settled now. I've noted the time in case they query it.",
        ),
        promised=(
            "I've put a trace on the transfer - the other bank has to answer within a set time.",
            "There's a trace on it now. You'll get the outcome either way.",
        ),
        chase=(
            "the trace hasn't come back",
            "the transfer still hasn't landed",
        ),
    ),
)

TOPIC_BY_OPENER: dict[str, Topic] = {t.opener: t for t in TOPICS}


# --- how the customer opens a SECOND, THIRD, FOURTH contact ------------------------------------
#
# The gap is real and is not currently used anywhere: measured over the shipped corpus, the median
# gap between two contacts is 30 days, the mean 37, and 20.3% of gaps are 60 days or more. So
# "it's been a couple of months" is available, true, and was never said. These buckets are read
# off that distribution rather than invented.

GAP_PHRASES: dict[str, tuple[str, ...]] = {
    "days": ("the other day", "earlier this week"),
    "weeks": ("a couple of weeks back", "a week or two ago"),
    "month": ("about a month ago", "last month"),
    "months": ("a couple of months ago", "a good two months ago"),
    "long": ("months ago now", "back at the start of all this"),
}

# Filled with the month name computed from the PRIOR conversation's day, so it is true by
# construction rather than by hope. `{when}` takes a phrase above, `{how}` the verb for the prior
# channel, `{subject}` the prior reason, `{undertaking}` what the agent said it would do.
CONTACT_VERB: dict[str, str] = {
    "call": "rang",
    "chat": "messaged",
    "complaint": "wrote in",
}

# The prior contact happened and nothing was promised. Neutral continuity.
CONTINUITY_NEUTRAL: tuple[str, ...] = (
    "Hello again - I {how} {when}, in {month}, about {subject}.",
    "Me again. I {how} about {subject} {when}, back in {month}.",
    "I {how} {when} about {subject}, just so you've got the background.",
)

# A promise was made and KEPT. The customer says so, then moves on. This is the arc getting
# better, and the corpus needs some of those or "broken" means nothing.
CONTINUITY_KEPT: tuple[str, ...] = (
    "Hello again - I {how} {when} about {subject}. That got sorted, so thank you.",
    "Me again. Last time, {when}, it was {subject}, and that did come through in the end.",
    "I {how} in {month} about {subject}. You said you'd sort it and you did.",
)

# A promise was made and BROKEN. This is what earns a complaint escalation, and it is the only
# thing in the corpus that does.
CONTINUITY_BROKEN: tuple[str, ...] = (
    "I {how} {when} about {subject}, and I was told I'd get {undertaking}. It hasn't happened.",
    "Right - I {how} about {subject} back in {month}. I was promised {undertaking}, and {chase}.",
    "This is about {subject} again. I {how} {when} and nothing has come of it - {chase}.",
)


# --- conversation choreography -------------------------------------------------------------
#
# Verification once, at the start, and only on a live channel. The security question used to fire
# 869 times, at turn index <= 2 only 88 of them, and twice or more inside 161 conversations. Phase A
# deleted it outright, which fixed the wrongness by removing the realism; this puts it back in the
# one place a contact centre actually asks it. The recording notice is folded into the call
# opening itself rather than emitted as its own turn, so a call cannot open with two agent turns
# in a row — 52.9% of conversations used to contain an agent->agent run.

VERIFY_ASK: dict[str, tuple[str, ...]] = {
    "call": (
        "Thanks. Before I bring anything up - can I take the first and third character of your memorable word?",
        "Before I look at that, I'll need to check it's you. First and third character of the memorable word, please.",
    ),
    "chat": (
        "Thanks. Before I open the account - can you confirm the postcode we hold for you?",
        "One security check before I look: can you confirm the postcode on the account?",
    ),
}

VERIFY_ANSWER: dict[str, tuple[str, ...]] = {
    "call": (
        "It's E and then R.",
        "First is H, third is L.",
    ),
    "chat": (
        "Yes, it's the one starting NW3.",
        "Postcode's the same one, ends 7QB.",
    ),
}

VERIFY_DONE: tuple[str, ...] = (
    "That's you verified, thank you.",
    "Perfect, thank you - that's you through security.",
)

# "While I've got you" — the marker that a turn is deliberately off the stated reason. A real
# call drifts; an undeclared drift is what made the old corpus read as a random bag of questions.
ASIDE_CONNECTORS: tuple[str, ...] = (
    "While I've got you - ",
    "Oh, and before I forget - ",
    "One other thing while you're there. ",
    "Sorry, unrelated, but - ",
)


# --- the written channel ---------------------------------------------------------------------
#
# Fitted to `benchmarks/cfpb/out/sample.jsonl`: single author, no turn-taking, median 155 words.
# Our complaint documents used to be 460 / 460 interleaved two-party dialogues with a median of 84
# customer words. Structure below follows what those 150 narratives actually do — subject, then
# chronology, then impact, then the ask — which is also how a complaint-handling team reads one.

COMPLAINT_SUBJECT_LINES: tuple[str, ...] = (
    "I am writing to complain about {subject}, and I would like this dealt with properly rather than passed around.",
    "This is a formal complaint about {subject}. I have tried to resolve it in the ordinary way and got nowhere.",
    "I want to raise a complaint regarding {subject}. Please treat this letter as the start of your complaints process.",
)

COMPLAINT_FIRST_CONTACT: tuple[str, ...] = (
    "This is the first time I have put anything in writing to you, and I would rather not have had to.",
    "I have not contacted you about this before, so there is nothing on file, and I am setting it out from the beginning.",
    "I am writing rather than ringing because I want a record of it from the outset.",
)

COMPLAINT_IMPACT: tuple[str, ...] = (
    "The practical effect is that I have had to arrange things around a problem that is not of my making, and I have spent a good deal of time on it that I do not have.",
    "It has cost me time and, more to the point, it has cost me confidence that anything I am told by your staff will actually happen.",
    "I have had to explain the same set of facts to a different person every time, which is exactly what your own literature says will not happen.",
    "None of this is a fortune in money terms. It is the being ignored that I object to, and the sense that nothing is written down anywhere.",
)

COMPLAINT_ASK: tuple[str, ...] = (
    "What I want is a written answer setting out what went wrong, what you are doing about it, and by when.",
    "I would like this acknowledged in writing, a named person to deal with it, and a date by which it will be resolved.",
    "Please confirm in writing that this is logged as a complaint, and tell me what happens next and how long it takes.",
    "I want it fixed, I want it confirmed in writing, and I want to know how to escalate it if that does not happen.",
)

COMPLAINT_CHRONOLOGY_BROKEN: tuple[str, ...] = (
    "I {how} in {month}, {when}, about {subject}. I was told I would get {undertaking}. Nothing arrived, and nobody contacted me to explain why.",
    "The history is this. I {how} about {subject} in {month}, and I was promised {undertaking}. {chase_cap}. I have heard nothing since.",
)

COMPLAINT_CHRONOLOGY_KEPT: tuple[str, ...] = (
    "For completeness: I {how} in {month} about {subject}, and that particular thing was dealt with. This is a separate matter and I am writing because I do not want it going the same way as things that are not chased.",
    "I should say that when I {how} {when} about {subject}, it was sorted out. That is why it is worth putting this one in writing before it drifts.",
)

COMPLAINT_CHRONOLOGY_NEUTRAL: tuple[str, ...] = (
    "By way of background, I {how} in {month}, {when}, about {subject}. I mention it because there is a pattern here, not a one-off.",
    "I have contacted you before about this account - I {how} {when} regarding {subject} - so there should be a record on file.",
)

# The single written acknowledgement a case handler sends back. One turn, at the end. Not
# turn-taking: the CFPB sample has a company response field for exactly this and nothing else.
COMPLAINT_ACK_GENERIC: tuple[str, ...] = (
    "Thank you for writing in. I have opened a case and logged this as a complaint. You will get a written response, and I will be handling it myself.",
    "I have read your letter and opened a case. This is recorded as a complaint and it will not be closed until you have a written answer.",
)


# --- markers a measurement script can grep for -------------------------------------------------
# Exported so `docs/corpus/06-phase-c-record.md`'s counts can be reproduced without re-deriving
# the templates. Anything here is generated continuity prose, not a planted fragment.
CONTINUITY_MARKERS: tuple[str, ...] = (
    "i rang", "i messaged", "i wrote in", "hello again", "me again",
    "last time", "you said you'd", "was promised", "it hasn't happened",
    "by way of background", "for completeness", "i have contacted you before",
)


def gap_bucket(gap_days: int) -> str:
    """Which of the five gap phrasings is TRUE for this many days.

    Cut points read off the shipped gap distribution (median 30, mean 37, 20.3% >= 60), not
    chosen for roundness. The point of the buckets is that "it's been a couple of months" is only
    ever said when it has been a couple of months.
    """
    if gap_days < 10:
        return "days"
    if gap_days < 25:
        return "weeks"
    if gap_days < 50:
        return "month"
    if gap_days < 110:
        return "months"
    return "long"


def _fill(
    template: str,
    *,
    how: str,
    when: str,
    month: str,
    subject: str,
    undertaking: str,
    chase: str,
) -> str:
    return template.format(
        how=how,
        when=when,
        month=month,
        subject=subject,
        undertaking=undertaking,
        chase_cap=chase[0].upper() + chase[1:],
        chase=chase,
    )


def continuity_opening(
    *,
    kind: str,
    gap_days: int,
    month: str,
    prior_channel: Channel,
    subject: str,
    undertaking: str,
    chase: str,
    pick: int,
) -> str:
    """The customer's first line of a SECOND or later contact.

    `kind` is one of "kept" / "broken" / "neutral" and comes from the planner's promise schedule,
    never from the text. `pick` is a caller-supplied integer (an rng draw) so selection stays with
    the generator and this module stays a pile of strings.
    """
    pool = {
        "kept": CONTINUITY_KEPT,
        "broken": CONTINUITY_BROKEN,
    }.get(kind, CONTINUITY_NEUTRAL)
    phrases = GAP_PHRASES[gap_bucket(gap_days)]
    return _fill(
        pool[pick % len(pool)],
        how=CONTACT_VERB[prior_channel.value],
        when=phrases[pick % len(phrases)],
        month=month,
        subject=subject,
        undertaking=undertaking,
        chase=chase,
    )


def complaint_chronology(
    *,
    kind: str,
    gap_days: int,
    month: str,
    prior_channel: Channel,
    subject: str,
    undertaking: str,
    chase: str,
    pick: int,
) -> str:
    """The same continuity, written out as a paragraph of a complaint letter."""
    pool = {
        "kept": COMPLAINT_CHRONOLOGY_KEPT,
        "broken": COMPLAINT_CHRONOLOGY_BROKEN,
    }.get(kind, COMPLAINT_CHRONOLOGY_NEUTRAL)
    phrases = GAP_PHRASES[gap_bucket(gap_days)]
    return _fill(
        pool[pick % len(pool)],
        how=CONTACT_VERB[prior_channel.value],
        when=phrases[pick % len(phrases)],
        month=month,
        subject=subject,
        undertaking=undertaking,
        chase=chase,
    )


BY_TYPE: dict[SignalType, tuple[Fragment, ...]] = {
    st: tuple(f for f in PLANTS if f.signal_type == st) for st in SignalType
}
