"""BA008 Layering — correspondent-banking exposure risk model.

Layering is the classic middle stage of laundering: funds placed into the financial
system are pushed through a chain of transfers designed to sever the audit trail from
their source before they are integrated into legitimate-looking assets. Unlike BA004
Circular Funds Flow (which is engineered to return to the ORIGINATOR), a layering chain
has no obligation to close a loop -- its only job is to put distance, opacity and
jurisdictional friction between the seed account and wherever the funds end up.

The signature is DEPTH AND OPACITY: how many hops the chain takes before the trail goes
cold, how many of those intermediaries are shells or nominees rather than identifiable
counterparties, how many secrecy/offshore jurisdictions the chain crosses, and how much
the value is split into fragments (and re-merged) along the way to defeat simple
amount-matching.

Four components, from the macro framework:

    Chain Depth              0.30   number of transfer hops the seed account's funds
                                     pass through before the trail goes cold
    Intermediary Opacity     0.25   share of the chain's intermediaries that are
                                     shell/nominee entities rather than identifiable
                                     counterparties
    Jurisdiction Hopping     0.25   how many of the chain's hops route through a
                                     recognised secrecy/offshore jurisdiction
    Value Fragmentation      0.20   how many pieces the seed amount is split into
                                     (and re-merged from) along the chain

Graded. Estate conventions shared: midpoints 15/45/70/90, boundaries at 80, half-up,
missing != zero. Cites scoring-models/common/Risk_Scoring_Standards.md.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Mapping, Tuple

__all__ = [
    "RiskModelError", "BAND_SCORE", "COMPONENT_WEIGHTS", "RISK_BANDS", "band_of",
    "score_chain_depth", "score_intermediary_opacity", "score_jurisdiction_hopping",
    "score_value_fragmentation", "ba008_exposure_score",
]


class RiskModelError(ValueError):
    """Raised when the model cannot be computed from what it was given."""


BAND_SCORE: Dict[str, int] = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
COMPONENT_WEIGHTS: Dict[str, float] = {
    "chain_depth": 0.30, "intermediary_opacity": 0.25,
    "jurisdiction_hopping": 0.25, "value_fragmentation": 0.20,
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


def score_chain_depth(hop_count: Any) -> str:
    """The core layering signal: how many transfer hops the seed account's funds
    pass through before the trail goes cold. REQUIRED -- not measured is not zero
    hops."""
    hops = int(float(_require(hop_count, "hop_count")))
    if hops <= 2:
        return "Low"
    if hops <= 4:
        return "Medium"
    if hops <= 6:
        return "High"
    return "Critical"


def score_intermediary_opacity(opaque_intermediary_count: Any, total_intermediary_count: Any) -> str:
    """What share of the chain's intermediaries are shell/nominee entities rather
    than identifiable counterparties. Both counts are REQUIRED."""
    opaque = float(_require(opaque_intermediary_count, "opaque_intermediary_count"))
    total = float(_require(total_intermediary_count, "total_intermediary_count"))
    if total <= 0:
        raise RiskModelError("total_intermediary_count must be > 0 to compute a ratio")
    r = opaque / total
    if r < 0.20:
        return "Low"
    if r < 0.45:
        return "Medium"
    if r < 0.75:
        return "High"
    return "Critical"


def score_jurisdiction_hopping(secrecy_jurisdiction_hops: Any) -> str:
    """How many of the chain's hops route through a recognised secrecy/offshore
    jurisdiction. REQUIRED -- not measured is not zero secrecy hops."""
    n = int(float(_require(secrecy_jurisdiction_hops, "secrecy_jurisdiction_hops")))
    if n <= 0:
        return "Low"
    if n == 1:
        return "Medium"
    if n == 2:
        return "High"
    return "Critical"


def score_value_fragmentation(fragment_count: Any) -> str:
    """How many pieces the seed amount is split into (and re-merged from) along
    the chain -- a split-then-remerge pattern defeats simple amount-matching.
    REQUIRED -- not measured is not zero fragments."""
    n = int(float(_require(fragment_count, "fragment_count")))
    if n <= 2:
        return "Low"
    if n <= 4:
        return "Medium"
    if n <= 7:
        return "High"
    return "Critical"


def ba008_exposure_score(bands: Mapping[str, str]) -> Tuple[int, str, Dict[str, Any]]:
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
        "rounding": "half-up", "basis": "scoring-models/specific/BA008_Layering_Scoring_Framework.md. Band-midpoint mapping; boundaries at 80; half-up.",
    }
