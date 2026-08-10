"""BA005 Rapid Movement — correspondent-banking exposure risk model.

Rapid movement is the velocity / layering signal: funds land on an account and leave it
again almost immediately, having barely rested long enough to register as a balance. It is
the correspondent-banking cousin of BA002 Funnel Accounts and BA003 Mule Accounts, but the
tell here is not who the money came from or where it goes — it is HOW FAST it moves and
HOW MUCH of it moves relative to what the account normally holds.

The signature is THROUGHPUT: how briefly funds dwell on the account before clearing back
out, how large the turnover is relative to the account's own balance (an account that turns
over many multiples of its balance every cycle is not behaving like an ordinary deposit
account), how widely the outbound leg disperses across multiple onward destinations rather
than settling with one counterparty, and how closely the outbound amount tracks the inbound
amount (near-total pass-through, almost nothing retained).

Four components, from the macro framework:

    Dwell Time            0.35   how briefly funds are held before clearing onward --
                                  shorter dwell is worse
    Velocity               0.25   turnover relative to the account's own balance
    Onward Dispersion      0.20   how many distinct onward destinations receive the
                                  outbound leg
    Value Match             0.20   how closely the outbound amount tracks the inbound
                                  amount -- out approx in

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites scoring-models/common/Risk_Scoring_Standards.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_dwell_time", "score_velocity", "score_onward_dispersion",
    "score_value_match", "ba005_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "dwell_time": 0.35, "velocity": 0.25,
    "onward_dispersion": 0.20, "value_match": 0.20,
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


def score_dwell_time(dwell_time_hours: Any) -> str:
    """The core rapid-movement signal: how briefly funds rest on the account before
    clearing onward -- shorter dwell is worse. REQUIRED -- not measured is not zero
    hours."""
    hours = float(_require(dwell_time_hours, "dwell_time_hours"))
    if hours >= 48:
        return "Low"
    if hours >= 12:
        return "Medium"
    if hours >= 2:
        return "High"
    return "Critical"


def score_velocity(total_turnover_amount: Any, avg_balance: Any) -> str:
    """How large the account's turnover is relative to its own balance -- an account
    that turns over many multiples of its balance every cycle is not behaving like an
    ordinary deposit account. Both values are REQUIRED."""
    turnover = float(_require(total_turnover_amount, "total_turnover_amount"))
    balance = float(_require(avg_balance, "avg_balance"))
    if balance <= 0:
        raise RiskModelError("avg_balance must be > 0 to compute a ratio")
    r = turnover / balance
    if r < 3:
        return "Low"
    if r < 8:
        return "Medium"
    if r < 20:
        return "High"
    return "Critical"


def score_onward_dispersion(distinct_destination_count: Any) -> str:
    """How many distinct onward destinations receive the outbound leg -- spreading the
    outflow across more destinations disperses and disguises the funds' onward path.
    REQUIRED -- not measured is not zero destinations."""
    n = int(float(_require(distinct_destination_count, "distinct_destination_count")))
    if n <= 2:
        return "Low"
    if n <= 4:
        return "Medium"
    if n <= 7:
        return "High"
    return "Critical"


def score_value_match(outbound_amount: Any, inbound_amount: Any) -> str:
    """How closely the outbound amount tracks the inbound amount -- out approx in,
    near-total pass-through with almost nothing retained. Both amounts are REQUIRED."""
    outbound = float(_require(outbound_amount, "outbound_amount"))
    inbound = float(_require(inbound_amount, "inbound_amount"))
    if inbound <= 0:
        raise RiskModelError("inbound_amount must be > 0 to compute a ratio")
    r = outbound / inbound
    if r < 0.50:
        return "Low"
    if r < 0.75:
        return "Medium"
    if r < 0.92:
        return "High"
    return "Critical"


def ba005_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "scoring-models/specific/BA005_Rapid_Movement_Scoring_Framework.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
