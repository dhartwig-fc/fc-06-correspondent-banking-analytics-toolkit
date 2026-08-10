"""BA001 Structuring — correspondent-banking exposure risk model.

Structuring (a.k.a. "smurfing") breaks cash deposits into amounts just under a
reporting threshold (in the US, the $10,000 CTR line) to evade currency-transaction
reporting, then aggregates the structured cash and moves it onward to a beneficiary.
The signature is the CLUSTERING: many sub-threshold cash deposits, close together in
time, often spread across branches or ATMs, that are eventually wired out.

Four components, from the macro framework:

    Sub-threshold Clustering   0.35   share of cash deposits sitting just under the
                                       CTR reporting line
    Temporal Clustering        0.25   how many deposits land inside a rolling 7-day
                                       window
    Multi-location             0.20   deposits spread across distinct branches/ATMs
    Aggregation to Transfer    0.20   structured-in cash wired out to one beneficiary

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites scoring-models/common/Risk_Scoring_Standards.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_sub_threshold_clustering", "score_temporal_clustering", "score_multi_location",
    "score_aggregation_to_transfer", "ba001_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "sub_threshold_clustering": 0.35, "temporal_clustering": 0.25,
    "multi_location": 0.20, "aggregation_to_transfer": 0.20,
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


def score_sub_threshold_clustering(subthreshold_deposits: Any, total_cash_deposits: Any) -> str:
    """The core structuring signal: what share of cash deposits sit just under the
    CTR reporting line. Both amounts are REQUIRED."""
    sub = float(_require(subthreshold_deposits, "subthreshold_deposits"))
    total = float(_require(total_cash_deposits, "total_cash_deposits"))
    if total <= 0:
        raise RiskModelError("total_cash_deposits must be > 0 to compute a ratio")
    r = sub / total
    if r < 0.10:
        return "Low"
    if r < 0.30:
        return "Medium"
    if r < 0.60:
        return "High"
    return "Critical"


def score_temporal_clustering(max_deposits_7d: Any) -> str:
    """How many sub-threshold deposits land inside the account's busiest rolling
    7-day window. REQUIRED — not measured is not zero deposits."""
    n = int(float(_require(max_deposits_7d, "max_deposits_7d")))
    if n <= 2:
        return "Low"
    if n <= 5:
        return "Medium"
    if n <= 9:
        return "High"
    return "Critical"


def score_multi_location(distinct_locations: Any) -> str:
    """How many distinct branches/ATMs the structured deposits are spread across."""
    n = int(float(_require(distinct_locations, "distinct_locations")))
    if n <= 1:
        return "Low"
    if n == 2:
        return "Medium"
    if n <= 4:
        return "High"
    return "Critical"


def score_aggregation_to_transfer(wired_out: Any, structured_in: Any) -> str:
    """How much of the structured-in cash is wired onward to a single beneficiary —
    the aggregation-to-transfer step that turns clustering into a laundering leg."""
    wired = float(_require(wired_out, "wired_out"))
    structured = float(_require(structured_in, "structured_in"))
    if structured <= 0:
        raise RiskModelError("structured_in must be > 0 to compute a ratio")
    a = wired / structured
    if a < 0.25:
        return "Low"
    if a < 0.50:
        return "Medium"
    if a < 0.80:
        return "High"
    return "Critical"


def ba001_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "scoring-models/specific/BA001_Structuring_Scoring_Framework.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
