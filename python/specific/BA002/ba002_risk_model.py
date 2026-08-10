"""BA002 Funnel Accounts — correspondent-banking exposure risk model.

A funnel account collects many small, geographically-dispersed deposits from
unrelated depositors and rapidly moves the aggregated funds onward to a single
downstream beneficiary. It is the collection-side mirror of BA001 Structuring:
where structuring hides the DEPOSIT pattern beneath a reporting line, funnelling
hides the COLLECTION pattern behind volume and dispersion, then clears it out
before it can be reviewed.

The signature is a FAN-IN / FAN-OUT finding: many distinct depositors spread
across many distinct regions feeding one account (fan-in), which holds the
money only briefly before it clears to one beneficiary (rapid passthrough,
beneficiary concentration).

Four components, from the macro framework:

    Geographic Dispersion       0.30   count/spread of distinct depositor regions
    Inflow Fan-in                0.25   number of distinct source depositors
    Rapid Passthrough            0.25   how short the in-to-out dwell is (shorter = worse)
    Beneficiary Concentration    0.20   share of outbound funds concentrated on the
                                        top beneficiary

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites scoring-models/common/Risk_Scoring_Standards.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_geographic_dispersion", "score_inflow_fan_in", "score_rapid_passthrough",
    "score_beneficiary_concentration", "ba002_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "geographic_dispersion": 0.30, "inflow_fan_in": 0.25,
    "rapid_passthrough": 0.25, "beneficiary_concentration": 0.20,
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


def score_geographic_dispersion(distinct_source_regions: Any) -> str:
    """How many distinct depositor regions feed the account. REQUIRED -- not
    measured is not zero regions."""
    n = int(float(_require(distinct_source_regions, "distinct_source_regions")))
    if n <= 2:
        return "Low"
    if n <= 4:
        return "Medium"
    if n <= 7:
        return "High"
    return "Critical"


def score_inflow_fan_in(distinct_depositors: Any) -> str:
    """The core funnelling signal: how many distinct, unrelated depositors feed
    the account. REQUIRED."""
    n = int(float(_require(distinct_depositors, "distinct_depositors")))
    if n <= 5:
        return "Low"
    if n <= 15:
        return "Medium"
    if n <= 30:
        return "High"
    return "Critical"


def score_rapid_passthrough(max_dwell_hours: Any) -> str:
    """How long the funnelled cash sits on the account before it clears onward --
    shorter dwell is worse. REQUIRED."""
    h = float(_require(max_dwell_hours, "max_dwell_hours"))
    if h >= 72:
        return "Low"
    if h >= 24:
        return "Medium"
    if h >= 6:
        return "High"
    return "Critical"


def score_beneficiary_concentration(top_beneficiary_amount: Any, total_outflow_amount: Any) -> str:
    """How much of the outbound funds concentrate on a single downstream
    beneficiary -- the fan-out step that turns a fan-in collection pattern into a
    laundering leg."""
    top = float(_require(top_beneficiary_amount, "top_beneficiary_amount"))
    total = float(_require(total_outflow_amount, "total_outflow_amount"))
    if total <= 0:
        raise RiskModelError("total_outflow_amount must be > 0 to compute a ratio")
    r = top / total
    if r < 0.25:
        return "Low"
    if r < 0.50:
        return "Medium"
    if r < 0.80:
        return "High"
    return "Critical"


def ba002_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "scoring-models/specific/BA002_Funnel_Accounts_Scoring_Framework.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
