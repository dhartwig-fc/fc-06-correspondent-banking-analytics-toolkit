"""BA004 Circular Funds Flow — correspondent-banking exposure risk model.

A circular flow is a round-tripping loop: funds leave an originating account,
pass through one or more intermediary accounts, and return to the same
originating account (or an account under the same control) having changed
identity along the way. It is the correspondent-banking mirror of BA003 Mule
Accounts run backwards — where a mule forwards funds onward and never sees
them again, a circular flow is engineered so the ORIGINATOR gets the funds
back, laundered through the appearance of unrelated third-party activity.

The signature is CLOSURE: how much of what left the origin comes back to it,
how many hops the loop takes to disguise the trip, how little value is lost
along the way (real correspondent banking bleeds fees/FX at every hop; a loop
that returns almost lossless is not behaving like ordinary trade finance),
and how quickly the whole round trip completes.

Four components, from the macro framework:

    Loop Closure          0.35   how much of the originated funds return to
                                  the origin account -- returned approx originated
    Hop Count              0.25   how many intermediary accounts the loop
                                  passes through before closing
    Value Preservation     0.20   how little value is lost hop to hop across
                                  the loop (near-lossless is the tell)
    Timing Compression     0.20   how rapidly the whole loop completes,
                                  origin to origin

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites scoring-models/common/Risk_Scoring_Standards.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_loop_closure", "score_hop_count", "score_value_preservation",
    "score_timing_compression", "ba004_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "loop_closure": 0.35, "hop_count": 0.25,
    "value_preservation": 0.20, "timing_compression": 0.20,
}
RISK_BANDS = ((0, 29, "Low"), (30, 59, "Medium"), (60, 79, "High"), (80, 100, "Critical"))


def _round_half_up(value: float) -> int:
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _require(value: Any, field: str) -> Any:
    if value is None:
        raise RiskModelError(
            "%s is missing. Refusing to score it as absent -- not measured and "
            "measured-as-zero are different findings." % field)
    return value


def band_of(score: float) -> str:
    for low, high, name in RISK_BANDS:
        if low <= score <= high:
            return name
    raise RiskModelError("score out of range: %r" % score)


def score_loop_closure(returned_amount: Any, originated_amount: Any) -> str:
    """The core circular-flow signal: how much of what left the origin account
    comes back to it -- returned approx originated. Both amounts are REQUIRED."""
    returned = float(_require(returned_amount, "returned_amount"))
    originated = float(_require(originated_amount, "originated_amount"))
    if originated <= 0:
        raise RiskModelError("originated_amount must be > 0 to compute a ratio")
    r = returned / originated
    if r < 0.50:
        return "Low"
    if r < 0.75:
        return "Medium"
    if r < 0.92:
        return "High"
    return "Critical"


def score_hop_count(hop_count: Any) -> str:
    """How many intermediary accounts the loop passes through before closing
    back on the origin -- more hops disguise the round trip further.
    REQUIRED -- not measured is not zero hops."""
    hops = int(float(_require(hop_count, "hop_count")))
    if hops <= 2:
        return "Low"
    if hops <= 4:
        return "Medium"
    if hops <= 6:
        return "High"
    return "Critical"


def score_value_preservation(avg_hop_retention_pct: Any) -> str:
    """How little value is lost hop to hop across the loop. Ordinary
    correspondent-banking activity bleeds fees and FX spread at every hop;
    a loop that returns almost lossless is not behaving like trade finance.
    REQUIRED -- not measured is not zero retention."""
    retention = float(_require(avg_hop_retention_pct, "avg_hop_retention_pct"))
    if retention < 0.80:
        return "Low"
    if retention < 0.90:
        return "Medium"
    if retention < 0.97:
        return "High"
    return "Critical"


def score_timing_compression(loop_duration_hours: Any) -> str:
    """How rapidly the whole loop completes, origin to origin. REQUIRED --
    not measured is not zero hours."""
    hours = float(_require(loop_duration_hours, "loop_duration_hours"))
    if hours >= 720:
        return "Low"
    if hours >= 168:
        return "Medium"
    if hours >= 24:
        return "High"
    return "Critical"


def ba004_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
    missing = sorted(set(COMPONENT_WEIGHTS) - set(bands))
    if missing:
        raise RiskModelError(
            "the model has four components and %d were supplied; missing: %s. "
            "Scoring a subset silently re-weights the model." % (len(bands), missing))
    working: Dict[str, Any] = {}
    total = 0.0
    for name, weight in COMPONENT_WEIGHTS.items():
        band = bands[name]
        if band not in BAND_SCORE:
            raise RiskModelError("%s: unknown band %r" % (name, band))
        contribution = BAND_SCORE[band] * weight
        total += contribution
        working[name] = {"band": band, "component_score": BAND_SCORE[band], "weight": weight, "contribution": round(contribution, 4)}
    score = _round_half_up(total)
    return score, band_of(score), {
        "components": working, "total": round(total, 4), "score": score, "band": band_of(score),
        "rounding": "half-up", "basis": "scoring-models/specific/BA004_Circular_Funds_Flow_Scoring_Framework.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
