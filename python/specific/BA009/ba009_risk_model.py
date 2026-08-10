"""BA009 Transaction Laundering — correspondent-banking exposure risk model.

Transaction laundering is a legitimate-looking merchant account used as a payment
processing front for hidden third parties: a card-processing relationship that was
underwritten against one declared business is quietly used to clear volume for
merchants (or principals) the acquirer never screened. Unlike BA007 Cash Intensive
Activity (physical cash disproportionate to a declared profile), the tell here runs
through the CARD RAILS themselves -- payment volume that outruns the merchant's own
declared business, transaction types that do not match the merchant category code
(MCC) the account was boarded under, a funnel of unrelated sub-merchants routed
through the one processing relationship, and a refund/chargeback pattern consistent
with laundering rather than genuine commerce (test transactions, self-refunds, no real
customer dispute cycle).

The signature is UNDISCLOSED PASS-THROUGH: how far processed card volume runs above
what the merchant declared at boarding, how many unrelated sub-merchants are folded
into the one processing relationship, how much of the transaction mix does not match
the boarded MCC, and how anomalous the refund/chargeback pattern is against genuine
commerce.

Four components, from the macro framework:

    Volume Profile Mismatch    0.30   processed card/payment volume vs the merchant's
                                        own declared business volume at boarding
    Third-Party Indicators     0.25   count of unrelated sub-merchants funnelled
                                        through the one processing relationship
    MCC Inconsistency          0.25   share of transactions inconsistent with the
                                        merchant category code the account was boarded
                                        under
    Refund/Chargeback Anomaly  0.20   share of processed value returned as refunds or
                                        chargebacks -- inconsistent with genuine
                                        commerce

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites scoring-models/common/Risk_Scoring_Standards.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_volume_profile_mismatch", "score_third_party_indicators",
    "score_mcc_inconsistency", "score_refund_chargeback_anomaly", "ba009_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "volume_profile_mismatch": 0.30, "third_party_indicators": 0.25,
    "mcc_inconsistency": 0.25, "refund_chargeback_anomaly": 0.20,
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


def score_volume_profile_mismatch(processed_card_volume: Any, declared_business_volume: Any) -> str:
    """The core laundering signal: processed card/payment volume against what the
    merchant declared as its own business volume at boarding. A merchant clearing at
    its declared profile scores Low; one clearing multiples of it scores Critical.
    Both amounts are REQUIRED."""
    processed = float(_require(processed_card_volume, "processed_card_volume"))
    declared = float(_require(declared_business_volume, "declared_business_volume"))
    if declared <= 0:
        raise RiskModelError("declared_business_volume must be > 0 to compute a ratio")
    r = processed / declared
    if r < 1.3:
        return "Low"
    if r < 1.8:
        return "Medium"
    if r < 2.5:
        return "High"
    return "Critical"


def score_third_party_indicators(unrelated_merchant_count: Any) -> str:
    """How many unrelated sub-merchants are funnelled through the one processing
    relationship -- the hallmark of transaction laundering (an aggregator boarding
    hidden merchants under a single legitimate storefront). REQUIRED -- not measured
    is not zero unrelated merchants."""
    n = int(float(_require(unrelated_merchant_count, "unrelated_merchant_count")))
    if n <= 1:
        return "Low"
    if n <= 3:
        return "Medium"
    if n <= 6:
        return "High"
    return "Critical"


def score_mcc_inconsistency(mcc_mismatched_txn_count: Any, total_txn_count: Any) -> str:
    """What share of transactions are inconsistent with the merchant category code
    (MCC) the account was boarded under -- e.g. a "gift shop" MCC clearing digital
    subscription or cash-equivalent transaction types. Both counts are REQUIRED."""
    mismatched = float(_require(mcc_mismatched_txn_count, "mcc_mismatched_txn_count"))
    total = float(_require(total_txn_count, "total_txn_count"))
    if total <= 0:
        raise RiskModelError("total_txn_count must be > 0 to compute a ratio")
    r = mismatched / total
    if r < 0.10:
        return "Low"
    if r < 0.25:
        return "Medium"
    if r < 0.45:
        return "High"
    return "Critical"


def score_refund_chargeback_anomaly(refund_chargeback_amount: Any, total_processed_amount: Any) -> str:
    """Share of processed value returned as refunds or chargebacks -- genuine commerce
    carries a modest, explainable return rate; a laundering front often shows an
    elevated rate from self-refunds, test transactions or an absent dispute cycle.
    Both amounts are REQUIRED."""
    returned = float(_require(refund_chargeback_amount, "refund_chargeback_amount"))
    total = float(_require(total_processed_amount, "total_processed_amount"))
    if total <= 0:
        raise RiskModelError("total_processed_amount must be > 0 to compute a ratio")
    r = returned / total
    if r < 0.02:
        return "Low"
    if r < 0.05:
        return "Medium"
    if r < 0.10:
        return "High"
    return "Critical"


def ba009_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "scoring-models/specific/BA009_Transaction_Laundering_Scoring_Framework.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
