"""BA006 Dormant Reactivation — correspondent-banking exposure risk model.

Dormant reactivation is the behavioural-anomaly signal: an account that has sat idle,
sometimes for years, suddenly comes back to life with flows that dwarf anything it ever
carried while active. The tell is not any single transaction -- it is the CONTRAST between
the account's long silence and the size, shape and speed of what happens the moment it
wakes up.

The signature is REACTIVATION SHOCK: how large the reactivating inflow is relative to what
the account used to carry every month before it went quiet, how long the account sat dormant
before that inflow landed (a longer silence makes the reactivation more anomalous, not less),
how much the account's behaviour after reactivation deviates from its prior profile (new
counterparties and geographies it never dealt with before), and how quickly the reactivating
funds drain back out again (a wake-up-and-drain pattern is far more concerning than a
wake-up-and-settle one).

Four components, from the macro framework:

    Reactivation Spike      0.30   magnitude of the reactivating inflow relative to the
                                    account's pre-dormancy average monthly activity
    Dormancy Length          0.25   how long the account sat dormant before reactivating --
                                    longer dormancy is worse
    Profile Deviation        0.25   how many new counterparties/geographies appear after
                                    reactivation that were never seen in the prior profile
    Immediate Outflow         0.20   how closely the outbound amount after reactivation
                                    tracks the reactivating inflow -- wake up and drain

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites scoring-models/common/Risk_Scoring_Standards.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_reactivation_spike", "score_dormancy_length", "score_profile_deviation",
    "score_immediate_outflow", "ba006_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "reactivation_spike": 0.30, "dormancy_length": 0.25,
    "profile_deviation": 0.25, "immediate_outflow": 0.20,
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


def score_reactivation_spike(reactivation_amount: Any, pre_dormancy_avg_monthly_activity: Any) -> str:
    """The core reactivation-shock signal: how large the reactivating inflow is relative
    to the account's pre-dormancy average monthly activity. Both values are REQUIRED."""
    reactivation = float(_require(reactivation_amount, "reactivation_amount"))
    baseline = float(_require(pre_dormancy_avg_monthly_activity, "pre_dormancy_avg_monthly_activity"))
    if baseline <= 0:
        raise RiskModelError("pre_dormancy_avg_monthly_activity must be > 0 to compute a ratio")
    r = reactivation / baseline
    if r < 3:
        return "Low"
    if r < 8:
        return "Medium"
    if r < 20:
        return "High"
    return "Critical"


def score_dormancy_length(dormancy_days: Any) -> str:
    """How long the account sat dormant before reactivating -- longer dormancy makes the
    sudden reactivation more anomalous, not less. REQUIRED -- not measured is not zero
    days."""
    days = float(_require(dormancy_days, "dormancy_days"))
    if days < 90:
        return "Low"
    if days < 180:
        return "Medium"
    if days < 365:
        return "High"
    return "Critical"


def score_profile_deviation(new_counterparty_count: Any) -> str:
    """How many new counterparties/geographies appear after reactivation that were never
    part of the account's prior profile. REQUIRED -- not measured is not zero
    counterparties."""
    n = int(float(_require(new_counterparty_count, "new_counterparty_count")))
    if n <= 2:
        return "Low"
    if n <= 4:
        return "Medium"
    if n <= 7:
        return "High"
    return "Critical"


def score_immediate_outflow(outflow_amount: Any, reactivation_amount: Any) -> str:
    """How closely the outbound amount after reactivation tracks the reactivating inflow
    -- wake up and drain, near-total pass-through with almost nothing retained. Both
    amounts are REQUIRED."""
    outflow = float(_require(outflow_amount, "outflow_amount"))
    reactivation = float(_require(reactivation_amount, "reactivation_amount"))
    if reactivation <= 0:
        raise RiskModelError("reactivation_amount must be > 0 to compute a ratio")
    r = outflow / reactivation
    if r < 0.50:
        return "Low"
    if r < 0.75:
        return "Medium"
    if r < 0.92:
        return "High"
    return "Critical"


def ba006_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "scoring-models/specific/BA006_Dormant_Reactivation_Scoring_Framework.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
