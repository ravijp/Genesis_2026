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
OPENINGS: tuple[str, ...] = (
    "Thanks for calling, you're through to Priya. Who am I speaking with?",
    "Good afternoon, you're speaking with Daniel. How can I help?",
    "Hello, Marcus here. What can I do for you today?",
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


BY_TYPE: dict[SignalType, tuple[Fragment, ...]] = {
    st: tuple(f for f in PLANTS if f.signal_type == st) for st in SignalType
}
