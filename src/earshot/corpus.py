"""Synthetic corpus generation: plan first, prose second.

Two properties matter more than realism here:

1. **Strata are generative.** A customer's stratum is decided by the Dirichlet concentration
   used to split their arc's evidence mass, NOT by asking whether some baseline can detect
   them. Defining a stratum by reference to a baseline's decision function, or regenerating
   arcs that baseline catches, would be selection on the dependent variable. Whether an arm
   can detect a DIFFUSE arc is a *measured result*, not a construction.

2. **Outcomes are drawn stochastically from latent risk.** Nobody is handed the answer, so
   outcome prediction is a genuine prediction task rather than a lookup on the answer key.

No third-party dependencies: Dirichlet is sampled via normalised Gamma draws from `random`.
"""

from __future__ import annotations

import datetime
import random
import warnings
from dataclasses import dataclass

from .config import CorpusConfig, RunConfig
from .corpus_lexicon import (
    ASIDE_CONNECTORS,
    CHASE_ACK,
    CHASE_FOLLOWUPS,
    BY_TYPE,
    COMPLAINT_ACK_GENERIC,
    COMPLAINT_ASK,
    COMPLAINT_FIRST_CONTACT,
    COMPLAINT_IMPACT,
    COMPLAINT_SUBJECT_LINES,
    FORMAL_ACKNOWLEDGEMENT_FLOOR,
    DECOYS_ACCUMULATOR,
    DECOYS_EXTRACTOR,
    FILLER_AGENT,
    OPENINGS,
    TOPICS,
    VERIFY_ANSWER,
    VERIFY_ASK,
    VERIFY_DONE,
    Fragment,
    Topic,
    agent_opening,
    agent_reply_to_filler,
    agent_reply_to_signal,
    complaint_chronology,
    continuity_opening,
)
from .schema import (
    Channel,
    Conversation,
    Corpus,
    CustomerTruth,
    Outcome,
    SeededSignal,
    SignalType,
    Stratum,
    Turn,
)

_TRAJECTORY_CHOICES = (
    SignalType.CHURN_INTENT,
    SignalType.FINANCIAL_DISTRESS,
    SignalType.COMPLAINT_ESCALATION,
    SignalType.LIFE_EVENT,
)


def _dirichlet(rng: random.Random, alpha: float, k: int) -> list[float]:
    draws = [rng.gammavariate(alpha, 1.0) for _ in range(k)]
    total = sum(draws) or 1.0
    return [d / total for d in draws]


def _pick_stratum(rng: random.Random, cfg: CorpusConfig) -> Stratum:
    names, weights = zip(*cfg.stratum_weights.items())
    return Stratum(rng.choices(names, weights=weights, k=1)[0])


def _nearest_fragment(
    pool: tuple[Fragment, ...],
    target: float,
    used: set[str],
    *,
    position: int,
    day: int,
    prior_promise_broken: bool,
) -> Fragment | None:
    """Pick the unused, TRUE fragment whose loudness best matches the mass allocated here.

    Returns None once the pool is exhausted, and the conversation is then left EMPTY.

    "True" is the Phase C addition and it is a filter, not a preference. Twelve fragments assert
    a prior contact with the bank and 34 of their 126 plantings landed in the customer's first
    conversation, where there had been none; *"this is the fourth time I've called about this
    and nobody has fixed it"* went into an arc with fewer than four contacts 9 times in 10. The
    conditions live on the fragment (`Fragment.plantable_at`) and are evaluated against the arc
    PLAN -- position, day, and whether the planner scheduled a broken promise last time -- so
    the answer key is still authored before a word of prose exists.

    There used to be an `or list(pool)` fallback here, which re-planted an already-used
    fragment instead. That was a correctness defect, not a convenience: the identical sentence
    appeared in two conversations on different days, the extractor emitted two signals with
    different `conversation_id`s, and `memory._raw()` counted them as `n_conversations = 2`.
    The ledger then paid a cross-conversation corroboration bonus for evidence that was one
    utterance copied twice -- manufacturing the exact mechanism this system claims to measure.
    At the shipped default range it hit 28 / 213 arc customers per 400.

    Padding with an empty conversation dilutes an arc, which is a bias AGAINST the ledger and
    is visible in the diagnostics. Repeating a fragment inflated it, and was invisible.
    """
    candidates = [
        f
        for f in pool
        if f.fragment_id not in used
        and f.plantable_at(
            position=position, day=day, prior_promise_broken=prior_promise_broken
        )
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda f: (abs(f.strength - target), f.fragment_id))


CORPUS_EPOCH = datetime.date(2026, 2, 1)
_MONTHS = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)


def month_name(day: int) -> str:
    """The calendar month of a corpus day.

    The horizon had no epoch, so seasonal text contradicted itself: "back in the spring" was
    planted on days 40-142 and "passed away in June" on days 9-109 of the same unanchored 180
    days. Two of those in one arc disagree with each other. Anchoring day 0 to 1 February makes
    the generated back-references ("I rang in March") true by construction, and lets a fragment
    that names a month declare the earliest day it can be said (`Fragment.earliest_day`).
    """
    return _MONTHS[(CORPUS_EPOCH + datetime.timedelta(days=day)).month - 1]


@dataclass(frozen=True)
class PriorContact:
    """What the customer and the bank both remember from the last conversation."""

    day: int
    channel: Channel
    topic: Topic
    promise_made: bool
    promise_kept: bool

    @property
    def continuity(self) -> str:
        """"kept" / "broken" / "neutral" -- which story the next contact opens with."""
        if not self.promise_made:
            return "neutral"
        return "kept" if self.promise_kept else "broken"


@dataclass(frozen=True)
class ArcContext:
    """Where this conversation sits in one customer's relationship with the bank.

    Everything here is decided by the PLANNER before any prose exists. `_render_conversation`
    used to take none of it, which is why an arc read as N independent scenes sharing a customer
    id: measured over 22,114 turns, "I called", "as I said" and "you said" appeared zero times.
    """

    position: int  # 0-based index of this conversation within the arc
    total: int  # how many conversations the arc holds
    topic: Topic  # the reason for THIS contact
    prior: PriorContact | None  # None on first contact
    promise_made: bool  # does this contact end with an undertaking rather than a resolution?

    @property
    def chasing(self) -> bool:
        """Is this contact about the same thing as the last one, because it was not done?"""
        return self.prior is not None and self.prior.topic is self.topic

    @property
    def prior_promise_broken(self) -> bool:
        return self.prior is not None and self.prior.continuity == "broken"


# The customer pivots from "here is what happened last time" to "here is why I'm calling today".
# Only used when the previous thread was closed; a broken promise means they are still on it.
# At most this many off-topic questions per conversation.
_MAX_ASIDES = 2

_PIVOTS: tuple[str, ...] = (
    "Anyway. ",
    "Today it's something else. ",
    "Separate thing this time. ",
    "Different thing today, though. ",
)


def _apply_asr_noise(rng: random.Random, text: str, rate: float) -> str:
    """Transcription is never clean. Drop or mangle the occasional word.

    CALL ONLY, and never on a planted fragment -- both enforced by the caller, and both by
    measurement rather than taste. 1,428 of 7,453 customer turns in chat and complaint used to
    be speech-recognition damaged, which cannot happen to typed text and is the sort of thing a
    contact-centre reader spots in ten seconds. And 212 of 973 planted signals (21.8%) shipped a
    damaged evidence quote -- including `can't make the payment this month, I just` -- which is
    the single most-looked-at string in the product, printed on the case screen as proof.
    """
    if rate <= 0:
        return text
    words = text.split()
    out: list[str] = []
    for w in words:
        if rng.random() < rate:
            if rng.random() < 0.5:
                continue  # dropped word
            out.append(w[:-1] + "-")  # clipped word
        else:
            out.append(w)
    return " ".join(out) or text


def _surface(rng: random.Random, fragment: Fragment, used_surfaces: set[str]) -> str:
    """Which wording of this fragment to plant: the canonical one, unless it is already used.

    The rule is about people, not about matchers. You say a thing once; when you say it again you
    say it differently. So the first time a customer raises a piece of evidence they use the
    fragment's canonical text, and a repeat inside the same arc reaches for a paraphrase.

    That fixes the defect this exists for. 38 duplicate plantings across 33 of 400 customers put
    the IDENTICAL sentence in two conversations of one arc -- `CUST-0002` said *"Cashflow's a bit
    lumpy this quarter, it always is."* verbatim on day 175 and again on day 178. Those are all on
    the decoy paths, which draw with replacement ON PURPOSE, because a recurring decoy earns a
    corroboration bonus it does not deserve and so makes the trap harder. A paraphrase keeps the
    trap exactly as hard -- the ledger corroborates across conversations of the same signal type,
    not across identical strings -- and stops a human saying the same sentence twice.

    WHAT THIS DELIBERATELY DOES NOT DO, and the measurement behind it. Plan item 8 wanted the
    surface varied ACROSS customers too, because 222 of 303 customers with a signal share their
    flagship quote with somebody else. Rotating all three surfaces uniformly was built and
    measured on 2026-08-31: offline strict recall fell to 0.1972 (139 / 705) against 0.31 on
    canonical text, because two thirds of every planting became prose the lexicon was not
    co-developed with -- the same effect already published as "the reader finds 1 of the 32
    blind-authored fragments". At the Northwind stream size (44 customers) that produced ZERO
    crossings and a blank demo screen. Widening the pools is the non-destructive version of item
    8 and is left for the owner to price.
    """
    if fragment.text not in used_surfaces:
        return fragment.text
    options = [s for s in fragment.paraphrases if s not in used_surfaces]
    return rng.choice(options) if options else rng.choice(fragment.surfaces())


def _body_turns(
    rng: random.Random,
    topic: Topic,
    n: int,
    said: set[str] | None = None,
    chasing: bool = False,
) -> list[tuple[str, str]]:
    """`n` (customer line, agent reply) pairs, WITHOUT replacement, on topic first and last.

    899 of 1,400 conversations repeated a customer line verbatim and 166 said one three or more
    times, because filler was `rng.choice` over a 15-tuple on every turn. Sampling without
    replacement is most of the fix; drawing the topic's OWN follow-ups first is the rest, because
    the conversation is now about the reason the customer gave for calling.

    Anything drawn from another topic is marked as an aside ("While I've got you -"). Real calls
    drift; an unmarked drift is what made the old transcripts read as a bag of questions. Asides
    are capped at two and are placed in the interior, never last, because the agent's closing --
    the resolution or the undertaking -- is appended to the final reply and has to land on the
    thing the customer actually rang about.
    """
    said = said or set()
    # A chase is not a fresh enquiry. Its material is topic-independent -- what has actually been
    # done, who owns it, why it stuck -- so it never exhausts however long the arc runs, and the
    # topic's own three follow-ups do not get asked for a third time.
    topical = list(CHASE_FOLLOWUPS if chasing else topic.followups)
    rng.shuffle(topical)
    # Prefer what this customer has not said yet. A broken undertaking means the NEXT contact is
    # about the same topic, so without this a customer chasing one thing across four contacts
    # asked "Do I need to set it up again from scratch?" four times.
    unused = [pair for pair in topical if pair[0] not in said]
    spent = [pair for pair in topical if pair[0] in said]
    pairs = unused[:n]

    wanted = min(n, len(unused) + _MAX_ASIDES) - len(pairs)
    if wanted > 0:
        others = [t for t in TOPICS if t is not topic]
        rng.shuffle(others)
        others.sort(key=lambda t: t.opener in said)
        for other in others[:wanted]:
            connector = rng.choice(ASIDE_CONNECTORS)
            head = other.opener
            # A connector that closes its own sentence keeps the capital; one that runs on
            # ("While I've got you - ") does not.
            if not connector.rstrip().endswith("."):
                head = head[0].lower() + head[1:]
            reply = agent_reply_to_filler(
                other.opener, Channel.CALL, rng.choice(FILLER_AGENT)
            )
            # Interior only: index 0 sets up the topic, the last pair carries the closing.
            # Interior strictly: the last pair's reply carries the closing, and a closing about
            # the reason for contact glued to the answer to an off-topic question reads as two
            # conversations spliced together.
            at = rng.randint(1, len(pairs) - 1) if len(pairs) > 1 else len(pairs)
            pairs.insert(at, (connector + head, reply))

    # Only if there is genuinely nothing new left. A fourth contact about one unresolved thing
    # SHOULD run shorter than the first -- a customer who has asked everything twice does not
    # invent an eighth question -- so this runs out rather than looping, which is what put the
    # same three chase questions into contacts 3 and 4 of `CUST-0007`.
    if not pairs:
        pairs = spent[:1] or list(topic.followups)[:1]
    return pairs


def _render_live(
    rng: random.Random,
    cfg: CorpusConfig,
    conversation_id: str,
    customer_id: str,
    channel: Channel,
    day: int,
    plant: Fragment | None,
    arc: ArcContext,
    used_surfaces: set[str],
) -> tuple[Conversation, int | None]:
    """A call or a chat: strictly alternating, one move per turn, opened by the agent.

    The choreography is fixed rather than sampled, and each step is here because the sampled
    version was wrong. 1,106 of 1,400 conversations contained a run of two or more customer
    turns nobody answered (the agent replied with probability 0.75) and 740 contained an
    agent->agent run (a filler immediately followed by the closing). Verification fired 869 times
    and was in the first three turns only 88 of them. The recording notice fired 893 times, 591
    of them inside a typed channel.

        0  agent     opening; on a call the recording notice is part of it
        1  customer  the reason for contact, and what happened since last time
        2  agent     one security check
        3  customer  the answer
        4  agent     verified, and an acknowledgement of the reason
        5+ customer / agent, alternating, about the reason
        N  agent     the same reply, plus either a resolution or a specific undertaking
    """
    topic = arc.topic
    turns: list[Turn] = []
    idx = 0

    turns.append(Turn(idx, "agent", agent_opening(channel, rng.choice(OPENINGS))))
    idx += 1

    if arc.prior is None:
        reason = topic.opener
    else:
        prior = arc.prior
        continuity = continuity_opening(
            kind=prior.continuity,
            gap_days=day - prior.day,
            month=month_name(prior.day),
            prior_channel=prior.channel,
            subject=prior.topic.subject,
            undertaking=prior.topic.undertaking,
            chase=rng.choice(prior.topic.chase),
            pick=rng.randrange(3),
        )
        reason = continuity if arc.chasing else (
            continuity + " " + rng.choice(_PIVOTS) + topic.opener
        )
    # Not through `_asr`: see its docstring. The reason for contact carries the continuity.
    turns.append(Turn(idx, "customer", reason))
    idx += 1

    key = channel.value if channel.value in VERIFY_ASK else "call"
    turns.append(Turn(idx, "agent", rng.choice(VERIFY_ASK[key])))
    idx += 1
    turns.append(Turn(idx, "customer", rng.choice(VERIFY_ANSWER[key])))
    idx += 1
    # A chase is acknowledged as a chase. Answering it with the same first-contact line is what
    # made `CUST-0029` hear "No block that I can see, it may have been their terminal" in
    # February, March and June -- an agent with no memory, on the demo screen of a product whose
    # entire claim is memory.
    acknowledgement = (
        rng.choice(CHASE_ACK)
        if arc.chasing
        else agent_reply_to_filler(topic.opener, channel, rng.choice(FILLER_AGENT))
    )
    turns.append(Turn(idx, "agent", rng.choice(VERIFY_DONE) + " " + acknowledgement))
    idx += 1
    # The stated reason counts as said, so a topic settled in one contact does not come back as
    # an aside in the next.
    used_surfaces.add(topic.opener)

    n_body = rng.randint(*cfg.body_turns)
    body = _body_turns(rng, topic, n_body, used_surfaces, chasing=arc.chasing)
    # Drawn against the body that was actually built, not against `n_body`. `_body_turns` caps
    # its output at the topic's follow-ups plus `_MAX_ASIDES`, so for a long draw it returns
    # fewer pairs than asked for -- and `randint(1, n_body - 1)` then pointed past the end, the
    # loop never reached `i == plant_at`, and the fragment the PLAN had allocated was silently
    # never spoken. Measured at 600 customers: 69 arc conversations, spread over all four
    # trajectories, held no evidence the planner had allocated to them. The answer key stayed
    # consistent -- nothing is seeded that was not placed -- so it diluted arcs invisibly, which
    # is the failure mode `smallest_fragment_pool`'s docstring calls the safe direction and still
    # spends a real signal. `test_every_allocated_fragment_is_actually_spoken` pins it.
    plant_at = rng.randrange(len(body)) if plant is not None else -1
    closing_pool = topic.promised if arc.promise_made else topic.resolved
    closing = rng.choice(closing_pool)

    plant_turn_index: int | None = None
    for i, (customer_line, agent_line) in enumerate(body):
        last = i == len(body) - 1
        if i == plant_at and plant is not None:
            text = _surface(rng, plant, used_surfaces)
            used_surfaces.add(text)
            turns.append(Turn(idx, "customer", text))  # never ASR-damaged
            plant_turn_index = idx
            idx += 1
            agent_line = agent_reply_to_signal(
                plant.fragment_id, plant.signal_type, plant.strength, channel,
                rng.choice(FILLER_AGENT),
            )
        else:
            used_surfaces.add(customer_line)
            turns.append(Turn(idx, "customer", _asr(rng, cfg, channel, customer_line)))
            idx += 1
        turns.append(Turn(idx, "agent", agent_line + " " + closing if last else agent_line))
        idx += 1

    return (
        Conversation(
            conversation_id=conversation_id,
            customer_id=customer_id,
            channel=channel,
            day=day,
            turns=tuple(turns),
        ),
        plant_turn_index,
    )


def _render_complaint(
    rng: random.Random,
    cfg: CorpusConfig,
    conversation_id: str,
    customer_id: str,
    day: int,
    plant: Fragment | None,
    arc: ArcContext,
    used_surfaces: set[str],
) -> tuple[Conversation, int | None]:
    """A written complaint: ONE author, no turn-taking, and one written answer at the end.

    Fitted to the 150 real CFPB narratives committed at `benchmarks/cfpb/out/sample.jsonl` (CC0,
    consumer-written, PII-scrubbed by the publisher) -- measured 2026-08-31: single author, no
    agent, min 11 words, median 155, mean 184. Ours were 459 of 460 interleaved two-party
    dialogues at a median of 84 customer words, i.e. a phone call with a different label. The
    structure below -- subject, chronology, detail, impact, ask -- is the shape those narratives
    take and the order a complaint-handling team reads them in. No sentence is taken from them.

    The single trailing agent turn is the firm's written response, which the CFPB records as a
    field of its own. That is not turn-taking; it is the reply to a letter.
    """
    paragraphs: list[str] = [
        rng.choice(COMPLAINT_SUBJECT_LINES).format(subject=arc.topic.subject)
    ]
    if arc.prior is None:
        paragraphs.append(rng.choice(COMPLAINT_FIRST_CONTACT))
    else:
        prior = arc.prior
        paragraphs.append(
            complaint_chronology(
                kind=prior.continuity,
                gap_days=day - prior.day,
                month=month_name(prior.day),
                prior_channel=prior.channel,
                subject=prior.topic.subject,
                undertaking=prior.topic.undertaking,
                chase=rng.choice(prior.topic.chase),
                pick=rng.randrange(2),
            )
        )

    # How much this person writes. Drawn on its own rather than off `body_turns`, because the
    # CFPB sample's shape is the target and it is not the shape of a phone call: min 11 words,
    # median 155, mean 184, p90 354. Some people write three lines and some write an essay, so
    # the number of paragraphs is drawn, not fixed.
    size = rng.random()
    n_detail, n_impact = (0, 0) if size < 0.30 else (1, 1) if size < 0.75 else (2, 2)
    # Source order, never shuffled: the two narrative lines are setup then consequence ("I
    # travelled to the branch on the strength of the hours I was given" / "when I rang to ask why
    # I was told they had changed"), and shuffling them inverted the chronology of a letter whose
    # whole job is to set out a chronology.
    narrative = list(arc.topic.narrative)
    if n_detail == 1:
        detail = [next((line for line in narrative if line not in used_surfaces), narrative[0])]
    else:
        detail = narrative[:n_detail]
    used_surfaces.update(detail)
    paragraphs.extend(detail)

    plant_turn_index: int | None = None
    if plant is not None:
        text = _surface(rng, plant, used_surfaces)
        used_surfaces.add(text)
        plant_turn_index = len(paragraphs)
        paragraphs.append(text)

    paragraphs.extend(rng.sample(COMPLAINT_IMPACT, n_impact))
    paragraphs.append(rng.choice(COMPLAINT_ASK))

    turns = [Turn(i, "customer", p) for i, p in enumerate(paragraphs)]
    # A case handler writes back once, in writing. Routing this through
    # `agent_reply_to_signal` would fall through to the SPOKEN reply for anything below the
    # formal-acknowledgement floor -- "No problem. Anything you want me to record while we're
    # here?" at the bottom of a complaint letter, which is worse than saying nothing.
    if plant is not None and plant.strength >= FORMAL_ACKNOWLEDGEMENT_FLOOR:
        answer = agent_reply_to_signal(
            plant.fragment_id, plant.signal_type, plant.strength, Channel.COMPLAINT,
            rng.choice(FILLER_AGENT),
        )
    else:
        answer = rng.choice(COMPLAINT_ACK_GENERIC)
    turns.append(Turn(len(turns), "agent", answer))

    return (
        Conversation(
            conversation_id=conversation_id,
            customer_id=customer_id,
            channel=Channel.COMPLAINT,
            day=day,
            turns=tuple(turns),
        ),
        plant_turn_index,
    )


def _asr(rng: random.Random, cfg: CorpusConfig, channel: Channel, text: str) -> str:
    """Speech-recognition damage: on the phone, on filler, and nowhere else.

    Two exclusions, and both are the same rule. Damage may never fall on a sentence the product
    reads a claim off. The planted evidence quote is one -- 212 of 973 plants used to ship
    damaged, and it is the string the case screen prints as proof. The customer's statement of
    why they are in touch is the other, because from the second contact on it carries the
    continuity: `"I rang about the lost card about a month ago and nothing has come of it"` came
    out as `"I about a month ago and nothing has come of it"`, which is not what a transcriber
    produces and is not readable as the thing the whole entry is about.

    Callers pass those two strings through untouched; everything else in a call comes here.
    """
    if channel is not Channel.CALL:
        return text
    return _apply_asr_noise(rng, text, cfg.asr_error_rate)


def _render_conversation(
    rng: random.Random,
    cfg: CorpusConfig,
    conversation_id: str,
    customer_id: str,
    channel: Channel,
    day: int,
    plant: Fragment | None,
    arc: ArcContext,
    used_surfaces: set[str],
) -> tuple[Conversation, int | None]:
    """Build one conversation around an optional planted fragment.

    Returns (conversation, plant turn index). The signature gained `arc` and `used_surfaces` in
    Phase C; before that it took no prior conversation at all and nothing could reference
    anything.
    """
    if channel is Channel.COMPLAINT:
        return _render_complaint(
            rng, cfg, conversation_id, customer_id, day, plant, arc, used_surfaces
        )
    return _render_live(
        rng, cfg, conversation_id, customer_id, channel, day, plant, arc, used_surfaces
    )


def _promise_schedule(
    rng: random.Random, trajectory: SignalType | None, k: int
) -> tuple[list[bool], list[bool]]:
    """Which contacts end with an undertaking, and whether it was kept by the next one.

    THE PLAN DECIDES THIS, NOT THE PROSE. That distinction is the whole reason it lives in
    `generate()` and not in the renderer. A `complaint_escalation` arc is, by definition, an arc
    in which the bank keeps not doing what it said it would; making the promises in that arc
    break is what turns "this is the fourth time I've called" from an assertion the corpus
    contradicts into a fact the corpus contains. The renderer then reads the schedule and writes
    it down. It never writes the schedule.

    Rates: a complaint arc breaks its promises 85% of the time, everything else keeps them 85%
    of the time and only makes one at all on about half of contacts. Nothing here touches which
    fragment is planted or how loud it is -- only `ce-s1` and `ce-m1`, which explicitly claim a
    broken promise, are gated on it.
    """
    if trajectory is SignalType.COMPLAINT_ESCALATION:
        made = [True] * k
        kept = [rng.random() < 0.15 for _ in range(k)]
    else:
        made = [rng.random() < 0.55 for _ in range(k)]
        kept = [rng.random() < 0.85 for _ in range(k)]
    return made, kept


def _topic_schedule(
    rng: random.Random, k: int, made: list[bool], kept: list[bool]
) -> list[Topic]:
    """One reason for contact per conversation, and the thread between them.

    A contact whose undertaking was broken is CHASED: the next conversation is about the same
    thing. Otherwise the customer is in touch about something new, drawn without replacement so
    an arc does not ask the same question twice by accident.
    """
    fresh = rng.sample(TOPICS, min(k, len(TOPICS)))
    schedule: list[Topic] = []
    j = 0
    for i in range(k):
        if i > 0 and made[i - 1] and not kept[i - 1]:
            schedule.append(schedule[i - 1])
        else:
            schedule.append(fresh[j % len(fresh)])
            j += 1
    return schedule


def _unused_decoy(
    rng: random.Random, pool: tuple[Fragment, ...], used: set[str]
) -> Fragment:
    """Draw a decoy this customer has not used yet, falling back to the whole pool.

    Both decoy paths used to draw with replacement, and that was DELIBERATE: a decoy that
    recurs earns a cross-conversation corroboration bonus it does not deserve, which makes the
    trap harder and biases the result against the ledger, i.e. the safe direction. What was not
    deliberate was the prose. Measured at 400 customers: 33 customers carried the same fragment
    twice, 38 duplicate plantings, and `CUST-0002` said *"Cashflow's a bit lumpy this quarter,
    it always is."* verbatim on day 175 and again on day 178. Nobody says the same sentence
    twice, three days apart, word for word.

    So the fix is both halves. Drawing without replacement stops the repeat; `_surface()`
    renders a paraphrase if the pool is small enough that a repeat happens anyway. The trap
    survives because the ledger corroborates across CONVERSATIONS of the same signal type, and a
    different decoy of the same type in the next conversation corroborates exactly as hard.

    One honest side effect: `DECOYS_ACCUMULATOR` holds 3 financial-distress and 2 churn
    fragments, so drawing without replacement makes an arc's decoy types slightly more mixed
    than drawing with replacement did, which very slightly WEAKENS the trap. Direction stated
    rather than hidden; it is visible in the decoy false-positive rate the sweep prints.
    """
    options = [f for f in pool if f.fragment_id not in used] or list(pool)
    frag = rng.choice(options)
    used.add(frag.fragment_id)
    return frag


class ArcCeilingWarning(UserWarning):
    """The configured arc length exceeds the scarcest fragment pool.

    Its own class so `cli.py` can silence exactly this warning after printing the same fact in
    readable prose, without silencing anything else.
    """


# Read off the dataclass default rather than hard-coded, so "did the caller choose this range,
# or is it the range we ship?" stays true if the shipped default ever moves.
_SHIPPED_CONVERSATION_RANGE = CorpusConfig().conversations_per_customer


def check_arc_ceiling(cfg: CorpusConfig) -> None:
    """Enforce the fragment-pool ceiling for EVERY caller, not just the command line.

    Fragments are planted WITHOUT replacement, so no arc can carry more signals than the
    scarcest trajectory pool holds. A `conversations_per_customer` maximum above that ceiling
    produces arcs whose later conversations are empty, and a longer-history comparison then
    measures padding rather than accumulation.

    This check used to live in `cli.py`'s argument parsing, where it only ran when
    `--conversations-per-customer` was passed. `sweep.py`, `tools/verdict_accuracy.py`,
    `tenants.py` and every test build a `RunConfig` programmatically and never touched it, and
    the shipped default -- whose maximum of 5 already exceeds the pool of 4 -- never reached it
    at all. It lives here now because `generate()` is the one door every corpus comes through.

    Warn vs raise, and why the two cases differ:

    * A range the CALLER chose is a mistake the caller can fix, and the resulting comparison is
      not worth running. Raise.
    * The SHIPPED default also breaches the ceiling and has done so for every number published
      to date. Raising on it would break `sweep`, `demo`, every test and the reproduction of
      every figure in the README -- turning a documented corpus limitation into an outage. So
      it warns, loudly, through a real `warnings.warn` that a programmatic caller sees. Fixing
      it means widening the pools in `corpus_lexicon.py`, which changes pass A / pass B overlap
      and moves the published extractor recall, so it is a deliberate act, not a side effect.
    """
    scarcest, pool_size = smallest_fragment_pool()
    hi = cfg.conversations_per_customer[1]
    if hi <= pool_size:
        return
    detail = (
        f"arcs run to {hi} conversations but the scarcest fragment pool "
        f"({scarcest.value}) holds {pool_size}, and fragments are planted without replacement. "
        f"Arcs on that trajectory carry at most {pool_size} signals, so their later "
        f"conversations are empty by construction. This bounds what any history-length claim "
        f"can show."
    )
    if cfg.conversations_per_customer == _SHIPPED_CONVERSATION_RANGE:
        warnings.warn(detail, ArcCeilingWarning, stacklevel=3)
        return
    raise ValueError(
        f"conversations_per_customer MAX={hi} exceeds the smallest fragment pool "
        f"({scarcest.value}, {pool_size} fragments). {detail} Widen the pools in "
        f"corpus_lexicon.py first."
    )


def generate(run: RunConfig | None = None) -> Corpus:
    run = run or RunConfig()
    cfg = run.corpus
    check_arc_ceiling(cfg)
    rng = random.Random(run.seed)

    customers: list[CustomerTruth] = []
    conversations: list[Conversation] = []
    seeded: list[SeededSignal] = []

    for n in range(cfg.n_customers):
        customer_id = f"CUST-{n:04d}"
        stratum = _pick_stratum(rng, cfg)
        k = rng.randint(*cfg.conversations_per_customer)

        # Conversation days, spread over the horizon and always ordered.
        days = sorted(rng.sample(range(cfg.horizon_days), k)) if k <= cfg.horizon_days else list(
            range(k)
        )
        # Channel mix: arcs that cross channels are the interesting ones, so bias toward variety.
        channels = [rng.choice(list(Channel)) for _ in range(k)]

        trajectory: SignalType | None = None
        latent_risk = 0.0
        plants: list[Fragment | None] = [None] * k

        # Drawn before the trajectory so the schedule does not depend on which pool is used,
        # only on whether the arc is a complaint arc. Both are pure plan.
        provisional = (
            rng.choice(_TRAJECTORY_CHOICES)
            if stratum in (Stratum.CONCENTRATED, Stratum.DIFFUSE)
            else None
        )
        promise_made, promise_kept = _promise_schedule(rng, provisional, k)
        topics = _topic_schedule(rng, k, promise_made, promise_kept)
        # True at conversation i when the undertaking given at i-1 was not delivered.
        broken_before = [False] + [
            promise_made[i - 1] and not promise_kept[i - 1] for i in range(1, k)
        ]

        if stratum in (Stratum.CONCENTRATED, Stratum.DIFFUSE):
            trajectory = provisional
            total_mass = rng.uniform(*cfg.total_arc_mass)
            alpha = (
                cfg.alpha_concentrated
                if stratum is Stratum.CONCENTRATED
                else cfg.alpha_diffuse
            )
            shares = _dirichlet(rng, alpha, k)
            pool = BY_TYPE[trajectory]
            used: set[str] = set()
            for i, share in enumerate(shares):
                # Mass allocated to this conversation, expressed on the fragment strength scale.
                allocated = min(1.0, share * total_mass * k / max(1, k) * (1.0 if k == 1 else 1.6))
                frag = _nearest_fragment(
                    pool,
                    allocated,
                    used,
                    position=i,
                    day=days[i],
                    prior_promise_broken=broken_before[i],
                )
                if frag is not None:
                    used.add(frag.fragment_id)
                    plants[i] = frag
            latent_risk = total_mass

        elif stratum is Stratum.DECOY_EXTRACTOR:
            trajectory = None
            drawn: set[str] = set()
            for i in range(k):
                if rng.random() < 0.6:
                    plants[i] = _unused_decoy(rng, DECOYS_EXTRACTOR, drawn)

        elif stratum is Stratum.DECOY_ACCUMULATOR:
            # Genuine weak signals that corroborate across time and channel -- and go nowhere.
            # Their whole job is to punish an over-eager accumulator. latent_risk stays 0.
            trajectory = None
            drawn = set()
            for i in range(k):
                plants[i] = _unused_decoy(rng, DECOYS_ACCUMULATOR, drawn)

        # NULL: plants stay empty.

        # Latent risk for the customers who are NOT on a distress arc. Real customers who are
        # fine still carry some risk, and it must OVERLAP the bottom of the distressed range.
        #
        # Leaving this at 0.0 would make `latent_risk > 0` a lossless readout of `Stratum` --
        # an answer-key field. Tools take latent risk as a plain float, so no import guard
        # would see it, and an agent could separate decoys from real arcs off the account tool
        # without reading a word of conversation.
        if stratum not in (Stratum.CONCENTRATED, Stratum.DIFFUSE):
            latent_risk = rng.betavariate(2.0, 3.5) * 0.75

        # Financial state: mostly idiosyncratic, only loosely tied to conversational risk.
        # The 0.35 weight is what keeps the account tool useful (a distressed customer really
        # is more likely to look distressed) without making it decisive on its own.
        financial_state = min(
            1.0, max(0.0, 0.35 * latent_risk + 0.65 * rng.betavariate(2.2, 2.6))
        )

        # Outcome drawn from latent risk. Decoy-accumulator and null customers sit at the
        # base rate, so a few of them churn by chance -- as they would in a real portfolio.
        p_outcome = min(0.95, cfg.outcome_base_rate + cfg.outcome_risk_gain * latent_risk)
        outcome, outcome_day = Outcome.NONE, None
        if rng.random() < p_outcome:
            outcome = (
                Outcome.CHURNED
                if (trajectory is SignalType.CHURN_INTENT or trajectory is None)
                else Outcome.DELINQUENT
            )
            outcome_day = days[-1] + rng.randint(10, 60)

        # One relationship, in day order. `prior` is what both parties remember; `surfaces`
        # is every sentence this customer has already said, so nobody repeats themselves.
        prior: PriorContact | None = None
        surfaces: set[str] = set()
        for i in range(k):
            conversation_id = f"{customer_id}-C{i}"
            arc = ArcContext(
                position=i,
                total=k,
                topic=topics[i],
                prior=prior,
                promise_made=promise_made[i],
            )
            conv, plant_turn = _render_conversation(
                rng, cfg, conversation_id, customer_id, channels[i], days[i], plants[i],
                arc, surfaces,
            )
            prior = PriorContact(
                day=days[i],
                channel=channels[i],
                topic=topics[i],
                promise_made=promise_made[i],
                promise_kept=promise_kept[i],
            )
            conversations.append(conv)
            frag = plants[i]
            if frag is not None and plant_turn is not None:
                seeded.append(
                    SeededSignal(
                        customer_id=customer_id,
                        conversation_id=conversation_id,
                        signal_type=frag.signal_type,
                        mass=frag.strength,
                        turn_index=plant_turn,
                        fragment_id=frag.fragment_id,
                        is_decoy=stratum
                        in (Stratum.DECOY_EXTRACTOR, Stratum.DECOY_ACCUMULATOR),
                        decoy_kind=(
                            "extractor"
                            if stratum is Stratum.DECOY_EXTRACTOR
                            else "accumulator"
                            if stratum is Stratum.DECOY_ACCUMULATOR
                            else None
                        ),
                    )
                )

        customers.append(
            CustomerTruth(
                customer_id=customer_id,
                stratum=stratum,
                trajectory=trajectory,
                outcome=outcome,
                outcome_day=outcome_day,
                latent_risk=latent_risk,
                financial_state=financial_state,
            )
        )

    return Corpus(
        customers=tuple(customers),
        conversations=tuple(conversations),
        seeded=tuple(seeded),
        seed=run.seed,
        config_hash=run.hash(),
    )


def smallest_fragment_pool() -> tuple[SignalType, int]:
    """The scarcest trajectory pool, and its size.

    Fragments are planted WITHOUT replacement within a customer's arc, so this number is the
    hard ceiling on how many signals any single arc can carry. A conversations-per-customer
    range whose maximum exceeds it produces arcs padded with empty conversations, which makes
    a longer-history comparison measure padding rather than accumulation.

    That sentence used to be a claim rather than a description. Until 2026-08-28 the planter
    fell back to re-using an already-planted fragment when the pool ran out, so exceeding the
    ceiling produced arcs with REPEATED conversations -- the opposite failure, and the one that
    inflates the ledger instead of diluting it. `_nearest_fragment` now returns None and the
    conversation really is left empty.

    `check_arc_ceiling()` enforces the ceiling on every caller: it raises for a range the
    caller chose and warns for the shipped default, which breaches it by one.
    """
    signal_type, pool = min(BY_TYPE.items(), key=lambda kv: len(kv[1]))
    return signal_type, len(pool)


# Pinned by name rather than globbed. A glob would quietly absorb a new module into the
# fingerprint (harmless) and, worse, quietly drop one that was renamed (not harmless) -- the
# fingerprint would keep matching while the pipeline it claims to describe had changed.
PIPELINE_MODULES = (
    "corpus.py",  # the planter: who gets which signal, how loud, on what day
    "corpus_lexicon.py",  # authoring pass A: the utterances planted
    "extract.py",  # the offline reader `_queue` always uses, whichever model investigates
    "extract_lexicon.py",  # authoring pass B: the cues that fire
    "memory.py",  # accumulation, decay and the score the queue is ranked on
)


def fingerprint_paths(paths) -> str:
    """sha256 over the bytes of `paths`, in the order given, truncated to 12 hex chars.

    Order matters and is the caller's: two different pipelines that happen to hold the same
    bytes in a different arrangement are different pipelines.
    """
    import hashlib

    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.read_bytes())
    return digest.hexdigest()[:12]


def pipeline_fingerprint() -> str:
    """A short hash of the CODE that turns a seed into a queue of crossings.

    `RunConfig.hash()` covers configuration *values* — seed, customer count, decay half-lives,
    thresholds. It does not cover the generator, and on 2026-08-28 that gap cost a $1.50 keyed
    run. Fixing the fragment re-plant defect changed which customers cross (25 with an outcome
    became 17, threshold 0.7246 became 0.6655) while `config_hash` stayed `3ebd9fb57097` on
    both sides. Every guard that compares config hashes — `tools/routing_accuracy.py`'s
    included, which exists precisely to refuse a mismatched corpus — would have scored the new
    corpus against the old artifact and reported a confident wrong number.

    So this hashes the source of every module whose behaviour decides the sample: the corpus
    planner and its lexicon, the offline reader and its lexicon, and the ledger that scores and
    ranks. Written into run manifests and checked when an artifact is re-read.

    **Deliberately over-sensitive.** A comment-only edit changes it and invalidates artifacts
    that would in fact still reproduce. That is the correct direction to be wrong in: a false
    "this artifact is stale" costs a re-run, and a false "this artifact is current" costs a
    number nobody can trust and nobody can spot.
    """
    from pathlib import Path

    here = Path(__file__).resolve().parent
    return fingerprint_paths([here / name for name in PIPELINE_MODULES])
