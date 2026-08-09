"""Extractor cue vocabulary — AUTHORING PASS B.

Written as a domain analyst would write it: "what phrasings mean a customer is drifting or
under money stress?" — WITHOUT reference to `corpus_lexicon.py`.

This module MUST NOT import `corpus_lexicon` or any ground-truth type. `tests/test_separation.py`
enforces it. The consequence is real and intended:

  * some planted fragments are phrased in ways no cue below covers  -> honest misses
  * some cues fire on decoys and on innocent filler                 -> honest false positives

That is what makes the offline provider the *weaker* arm, and it is why the memory delta
means something when it holds anyway.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .schema import SignalType


@dataclass(frozen=True)
class Cue:
    cue_id: str
    signal_type: SignalType
    weight: float  # maps to extractor confidence before dampeners
    pattern: str

    def compiled(self) -> re.Pattern[str]:
        return re.compile(self.pattern, re.IGNORECASE)


CUES: tuple[Cue, ...] = (
    # --- churn intent -------------------------------------------------------------
    Cue("c-close", SignalType.CHURN_INTENT, 0.90, r"\bclos(e|ing) (the|my|this) account\b"),
    Cue("c-move", SignalType.CHURN_INTENT, 0.85, r"\b(move|transfer|take) (my |the )?(money|balance|funds)\b.{0,20}\b(out|elsewhere|away|another)\b"),
    Cue("c-switch", SignalType.CHURN_INTENT, 0.75, r"\bswitch(ing)?\b.{0,25}\b(bank|provider|account)\b"),
    Cue("c-shop", SignalType.CHURN_INTENT, 0.55, r"\b(looking at|comparing|shopping around)\b.{0,30}\b(else|other|providers?|options?)\b"),
    Cue("c-rival", SignalType.CHURN_INTENT, 0.45, r"\b(another|other|different|her|his|their) bank\b"),
    Cue("c-exit-fee", SignalType.CHURN_INTENT, 0.40, r"\bfee\b.{0,40}\b(elsewhere|move|leave|transfer out)\b"),
    Cue("c-dormant", SignalType.CHURN_INTENT, 0.35, r"\b(don'?t|do not|no longer) use\b.{0,30}\b(anymore|any more)\b"),
    Cue("c-notice", SignalType.CHURN_INTENT, 0.30, r"\bnotice period\b"),
    # NOTE: no cue covers "my salary goes into the other one now" or the statement-export
    # phrasing. Those are real signals this extractor will miss. Left uncovered on purpose.
    # --- financial distress -------------------------------------------------------
    Cue("f-cant-pay", SignalType.FINANCIAL_DISTRESS, 0.92, r"\bcan'?t (make|afford|manage) the (payment|repayment)\b"),
    Cue("f-job", SignalType.FINANCIAL_DISTRESS, 0.88, r"\b(lost my job|made redundant|redundancy|laid off)\b"),
    Cue("f-hours", SignalType.FINANCIAL_DISTRESS, 0.60, r"\bhours (got |were |been )?cut\b"),
    Cue("f-tight", SignalType.FINANCIAL_DISTRESS, 0.50, r"\b(things|money|it'?s) (have |has |been )?(been )?(tight|hard|difficult)\b"),
    Cue("f-credit", SignalType.FINANCIAL_DISTRESS, 0.45, r"\bon the credit card\b"),
    Cue("f-late", SignalType.FINANCIAL_DISTRESS, 0.40, r"\b(last day|latest).{0,25}\bpay\b.{0,25}\b(charge|fee|penalt)"),
    Cue("f-date", SignalType.FINANCIAL_DISTRESS, 0.35, r"\bchange the (date|day)\b.{0,25}\b(comes out|payment|direct debit)\b"),
    Cue("f-bounce", SignalType.FINANCIAL_DISTRESS, 0.35, r"\b(bounce[sd]?|declined?)\b.{0,30}\b(show up|record|credit file)\b"),
    Cue("f-juggle", SignalType.FINANCIAL_DISTRESS, 0.28, r"\bjuggling\b"),
    Cue("f-payday", SignalType.FINANCIAL_DISTRESS, 0.26, r"\bafter payday\b"),
    # --- complaint escalation -----------------------------------------------------
    Cue("e-nth", SignalType.COMPLAINT_ESCALATION, 0.85, r"\b(second|third|fourth|fifth|\d+(st|nd|rd|th)) time I'?ve (called|rung|contacted)\b"),
    Cue("e-callback", SignalType.COMPLAINT_ESCALATION, 0.55, r"\b(promised|expecting) a callback\b"),
    Cue("e-before", SignalType.COMPLAINT_ESCALATION, 0.35, r"\bI did raise this before\b"),
    Cue("e-ref", SignalType.COMPLAINT_ESCALATION, 0.30, r"\breference number\b.{0,30}\blast time\b"),
    # --- life event ---------------------------------------------------------------
    Cue("l-bereave", SignalType.LIFE_EVENT, 0.85, r"\b(passed away|bereave|deceased|died)\b"),
    Cue("l-separate", SignalType.LIFE_EVENT, 0.60, r"\b(separating|divorc|splitting up)\b"),
    Cue("l-move", SignalType.LIFE_EVENT, 0.30, r"\bmoving (back )?in with\b"),
    Cue("l-statpay", SignalType.LIFE_EVENT, 0.30, r"\bstatutory (pay|maternity|sick)\b"),
)

# Dampeners: a cue that fires inside one of these contexts is attributed elsewhere, hypothetical,
# or resolved. This is the extractor's own attempt at not being fooled — deliberately imperfect,
# so decoys still get through and produce a real false-positive rate.
DAMPENERS: tuple[tuple[str, float], ...] = (
    (r"\b(my |a )?(friend|brother|sister|colleague|neighbour|mate)\b.{0,40}$", 0.25),
    (r"\bif\b.{0,30}\b(ever|were to|would)\b", 0.30),
    (r"\b(in |back in )(19|20)\d\d\b", 0.35),
    (r"\b(that'?s|it'?s) (all )?(sorted|resolved|fine) now\b", 0.20),
    (r"\bnot that I'?d\b", 0.25),
    (r"\bI'?m not complaining\b", 0.30),
)

COMPILED_CUES: tuple[tuple[Cue, re.Pattern[str]], ...] = tuple((c, c.compiled()) for c in CUES)
COMPILED_DAMPENERS: tuple[tuple[re.Pattern[str], float], ...] = tuple(
    (re.compile(p, re.IGNORECASE), m) for p, m in DAMPENERS
)
