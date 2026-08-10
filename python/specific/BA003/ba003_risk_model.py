"""BA003 Mule Accounts — correspondent-banking exposure risk model.

A mule account is a personal account used as a pass-through point: it receives
illicit funds from one or more originators and forwards them onward almost
immediately, retaining little or nothing. It is the personal-account mirror of
BA002 Funnel Accounts — where funnelling hides behind volume and dispersion on
the collection side, muling hides behind an individual's identity and a thin
personal-banking profile, then clears the funds out through a controller's
instruction.

The signature is PASS-THROUGH: outbound funds tracking inbound funds almost
1:1, on an account too young to have built a real transaction history, whose
throughput dwarfs the holder's declared income, and which shares a device or
downstream beneficiary with other accounts already known to be mules.

Four components, from the macro framework:

    Pass-through Ratio    0.30   how much of the inbound funds are forwarded
                                  onward -- out approx in, near-zero retained
    Account Youth         0.25   how recently the account was opened
    Behavioural Mismatch  0.25   throughput vs the holder's declared income/profile
    Network Linkage       0.20   shared device/beneficiary with known mule accounts

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites scoring-models/common/Risk_Scoring_Standards.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_pass_through_ratio", "score_account_youth", "score_behavioural_mismatch",
    "score_network_linkage", "ba003_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "pass_through_ratio": 0.30, "account_youth": 0.25,
    "behavioural_mismatch": 0.25, "network_linkage": 0.20,
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


def score_pass_through_ratio(total_outflow_amount: Any, total_inflow_amount: Any) -> str:
    """The core mule signal: how much of what came in was forwarded straight back
    out -- out approx in, near-zero retained. Both amounts are REQUIRED."""
    outflow = float(_require(total_outflow_amount, "total_outflow_amount"))
    inflow = float(_require(total_inflow_amount, "total_inflow_amount"))
    if inflow <= 0:
        raise RiskModelError("total_inflow_amount must be > 0 to compute a ratio")
    r = outflow / inflow
    if r < 0.50:
        return "Low"
    if r < 0.75:
        return "Medium"
    if r < 0.92:
        return "High"
    return "Critical"


def score_account_youth(account_age_days: Any) -> str:
    """How recently the account was opened -- a mule account is typically opened
    just before it starts moving illicit funds. REQUIRED -- not measured is not
    zero days."""
    age = int(float(_require(account_age_days, "account_age_days")))
    if age >= 365:
        return "Low"
    if age >= 180:
        return "Medium"
    if age >= 60:
        return "High"
    return "Critical"


def score_behavioural_mismatch(monthly_throughput_amount: Any, declared_monthly_income: Any) -> str:
    """How far the account's monthly throughput departs from the holder's declared
    income/profile -- the behavioural tell that the account is not being used the
    way it was opened to be used."""
    throughput = float(_require(monthly_throughput_amount, "monthly_throughput_amount"))
    income = float(_require(declared_monthly_income, "declared_monthly_income"))
    if income <= 0:
        raise RiskModelError("declared_monthly_income must be > 0 to compute a ratio")
    r = throughput / income
    if r < 3:
        return "Low"
    if r < 8:
        return "Medium"
    if r < 20:
        return "High"
    return "Critical"


def score_network_linkage(shared_link_count: Any) -> str:
    """How many shared-device/shared-beneficiary links tie this account to other
    accounts already known to be mules. REQUIRED -- not measured is not zero links."""
    n = int(float(_require(shared_link_count, "shared_link_count")))
    if n <= 0:
        return "Low"
    if n <= 1:
        return "Medium"
    if n <= 3:
        return "High"
    return "Critical"


def ba003_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "scoring-models/specific/BA003_Mule_Accounts_Scoring_Framework.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
