"""BA010 Peer Group Anomalies — correspondent-banking exposure risk model.

Peer group anomaly detection compares an account's own behaviour against the
statistical profile of its declared peer segment (accounts of a similar type,
size and business purpose) rather than against a fixed absolute threshold. A
tell that would be unremarkable for a high-turnover corporate account can be a
strong deviation signal for a retail deposit account, and vice versa — the
finding lives in how far the account sits from its OWN peer segment's mean,
measured in standard deviations (a z-score), not in an absolute dollar or
count cut-line.

Four components, from the macro framework:

    Volume Z-Score                 0.30   deviation of transaction volume from
                                            the peer segment mean
    Velocity Z-Score               0.25   deviation of turnover velocity from
                                            the peer segment mean
    Product Usage Deviation        0.25   deviation of the account's product/
                                            channel mix breadth from its peers
    Counterparty Diversity Z-Score 0.20   deviation of counterparty breadth
                                            (unusual concentration or spread)
                                            from the peer segment mean

Every component is a z-score: `z = (own_value - peer_mean) / peer_std`, banded
on |z| rather than on the raw value, since the same raw number means different
things in different peer segments. Graded. Estate conventions shared:
midpoints 15/45/70/90, boundaries at 80, half-up, missing != zero. Cites
scoring-models/common/Risk_Scoring_Standards.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_volume_zscore", "score_velocity_zscore", "score_product_usage_deviation",
    "score_counterparty_diversity_zscore", "ba010_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "volume_zscore": 0.30, "velocity_zscore": 0.25,
    "product_usage_deviation": 0.25, "counterparty_diversity_zscore": 0.20,
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


def _zscore_band(own_value: Any, peer_mean: Any, peer_std: Any, label: str) -> str:
    """Shared z-score banding: |z| < 1 Low, < 2 Medium, < 3 High, otherwise
    Critical. All three inputs are REQUIRED -- a peer segment with no measured
    mean/std cannot be compared against, and that is a different finding from
    "measures as zero deviation"."""
    own = float(_require(own_value, "%s (own value)" % label))
    mean = float(_require(peer_mean, "%s (peer_mean)" % label))
    std = float(_require(peer_std, "%s (peer_std)" % label))
    if std <= 0:
        raise RiskModelError("%s: peer_std must be > 0 to compute a z-score" % label)
    z = abs((own - mean) / std)
    if z < 1:
        return "Low"
    if z < 2:
        return "Medium"
    if z < 3:
        return "High"
    return "Critical"


def score_volume_zscore(own_volume: Any, peer_mean_volume: Any, peer_std_volume: Any) -> str:
    """How far the account's transaction volume sits from its peer segment's
    mean volume, in standard deviations. All three amounts are REQUIRED."""
    return _zscore_band(own_volume, peer_mean_volume, peer_std_volume, "volume_zscore")


def score_velocity_zscore(own_velocity: Any, peer_mean_velocity: Any, peer_std_velocity: Any) -> str:
    """How far the account's turnover velocity (transactions per period) sits
    from its peer segment's mean velocity, in standard deviations. All three
    amounts are REQUIRED."""
    return _zscore_band(own_velocity, peer_mean_velocity, peer_std_velocity, "velocity_zscore")


def score_product_usage_deviation(own_product_count: Any, peer_mean_product_count: Any,
                                   peer_std_product_count: Any) -> str:
    """How far the account's product/channel mix breadth sits from its peer
    segment's mean -- an atypically narrow or wide product footprint against
    the segment norm. All three counts are REQUIRED."""
    return _zscore_band(own_product_count, peer_mean_product_count, peer_std_product_count,
                         "product_usage_deviation")


def score_counterparty_diversity_zscore(own_counterparty_count: Any, peer_mean_counterparty_count: Any,
                                         peer_std_counterparty_count: Any) -> str:
    """How far the account's distinct-counterparty breadth sits from its peer
    segment's mean -- an unusually concentrated or unusually wide counterparty
    footprint against the segment norm. All three counts are REQUIRED."""
    return _zscore_band(own_counterparty_count, peer_mean_counterparty_count,
                         peer_std_counterparty_count, "counterparty_diversity_zscore")


def ba010_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "scoring-models/specific/BA010_Peer_Group_Anomalies_Scoring_Framework.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
