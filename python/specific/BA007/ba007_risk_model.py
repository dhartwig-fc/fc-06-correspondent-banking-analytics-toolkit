"""BA007 Cash Intensive Activity — correspondent-banking exposure risk model.

A cash-intensive business is a legitimate cover for laundering physical cash: cash &
carry wholesalers, currency exchange houses, laundromats, and similar operators that
plausibly handle real cash every day. The tell is not the presence of cash -- it is
cash disproportionate to the business's own declared profile, layered with the tells
that separate genuine trade volume from placement: the cash share of turnover run far
above what the business's own peer segment carries, the cash actually deposited
exceeding what the business declared when the account was profiled, deposits landing
with an unnaturally even rhythm (real retail cash is noisy; fabricated cash is not),
and third-party funds mixed into what should be the business's own till.

The signature is EXCESS OVER PROFILE: how far the cash ratio runs above the business's
own peer-segment norm, how far the actual cash deposited exceeds the volume the
business declared, how suspiciously even the deposit rhythm is, and how much of the
deposited cash did not originate with the business itself.

Four components, from the macro framework:

    Cash Ratio             0.35   cash deposits vs total turnover, scaled against the
                                    business's declared peer-segment cash norm
    Profile Excess          0.25   actual cash deposited vs the business's own declared
                                    annual cash volume
    Deposit Regularity      0.20   how unnaturally even the deposit rhythm is (lower
                                    variability = worse -- real cash businesses are noisy)
    Commingling              0.20   share of deposited cash that did not originate with
                                    the business itself (third-party funds mixed in)

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites scoring-models/common/Risk_Scoring_Standards.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_cash_ratio", "score_profile_excess", "score_deposit_regularity",
    "score_commingling", "ba007_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "cash_ratio": 0.35, "profile_excess": 0.25,
    "deposit_regularity": 0.20, "commingling": 0.20,
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


def score_cash_ratio(cash_deposits_amount: Any, total_turnover_amount: Any, peer_norm_cash_ratio: Any) -> str:
    """The core cash-intensity signal: the account's own cash-to-turnover ratio, scaled
    against its declared peer-segment cash norm. A cash & carry running at its peer norm
    scores Low; one running multiples of its peer norm scores Critical. All three values
    are REQUIRED."""
    cash = float(_require(cash_deposits_amount, "cash_deposits_amount"))
    turnover = float(_require(total_turnover_amount, "total_turnover_amount"))
    peer_norm = float(_require(peer_norm_cash_ratio, "peer_norm_cash_ratio"))
    if turnover <= 0:
        raise RiskModelError("total_turnover_amount must be > 0 to compute a ratio")
    if peer_norm <= 0:
        raise RiskModelError("peer_norm_cash_ratio must be > 0 to compute an excess")
    excess = (cash / turnover) / peer_norm
    if excess < 1.3:
        return "Low"
    if excess < 1.8:
        return "Medium"
    if excess < 2.5:
        return "High"
    return "Critical"


def score_profile_excess(cash_deposits_amount: Any, declared_annual_cash_volume: Any) -> str:
    """How far the cash actually deposited exceeds the volume the business declared when
    the account was profiled for KYC. Both values are REQUIRED."""
    cash = float(_require(cash_deposits_amount, "cash_deposits_amount"))
    declared = float(_require(declared_annual_cash_volume, "declared_annual_cash_volume"))
    if declared <= 0:
        raise RiskModelError("declared_annual_cash_volume must be > 0 to compute a ratio")
    r = cash / declared
    if r < 1.1:
        return "Low"
    if r < 1.5:
        return "Medium"
    if r < 2.2:
        return "High"
    return "Critical"


def score_deposit_regularity(deposit_cv_pct: Any) -> str:
    """How unnaturally even the deposit rhythm is, measured as the coefficient of
    variation (%) of individual deposit sizes. Real cash businesses are noisy day to day;
    a suspiciously LOW coefficient of variation means the deposits were engineered, not
    counted. REQUIRED -- not measured is not zero variability."""
    cv = float(_require(deposit_cv_pct, "deposit_cv_pct"))
    if cv >= 45:
        return "Low"
    if cv >= 30:
        return "Medium"
    if cv >= 15:
        return "High"
    return "Critical"


def score_commingling(third_party_deposit_amount: Any, total_deposit_amount: Any) -> str:
    """How much of the deposited cash did not originate with the business itself -- funds
    from unrelated third parties mixed into what should be the business's own till. Both
    amounts are REQUIRED."""
    third_party = float(_require(third_party_deposit_amount, "third_party_deposit_amount"))
    total = float(_require(total_deposit_amount, "total_deposit_amount"))
    if total <= 0:
        raise RiskModelError("total_deposit_amount must be > 0 to compute a ratio")
    r = third_party / total
    if r < 0.05:
        return "Low"
    if r < 0.15:
        return "Medium"
    if r < 0.30:
        return "High"
    return "Critical"


def ba007_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "scoring-models/specific/BA007_Cash_Intensive_Activity_Scoring_Framework.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
