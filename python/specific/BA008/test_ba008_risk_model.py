"""Tests for the BA008 Layering risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ba008_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, ba008_exposure_score,
    score_chain_depth, score_intermediary_opacity, score_jurisdiction_hopping,
    score_value_fragmentation,
)

CANON = {
    "chain_depth": score_chain_depth(9),
    "intermediary_opacity": score_intermediary_opacity(8, 9),
    "jurisdiction_hopping": score_jurisdiction_hopping(4),
    "value_fragmentation": score_value_fragmentation(9),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"chain_depth": 0.30, "intermediary_opacity": 0.25,
                                  "jurisdiction_hopping": 0.25, "value_fragmentation": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        ba008_exposure_score({"chain_depth": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = ba008_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_chain_depth_bands():
    assert score_chain_depth(2) == "Low"
    assert score_chain_depth(4) == "Medium"
    assert score_chain_depth(6) == "High"
    assert score_chain_depth(7) == "Critical"


def test_chain_depth_is_required():
    with pytest.raises(RiskModelError):
        score_chain_depth(None)


def test_intermediary_opacity_bands():
    assert score_intermediary_opacity(1, 10) == "Low"       # r=0.10
    assert score_intermediary_opacity(3, 10) == "Medium"    # r=0.30
    assert score_intermediary_opacity(6, 10) == "High"      # r=0.60
    assert score_intermediary_opacity(9, 10) == "Critical"  # r=0.90


def test_intermediary_opacity_requires_both_counts():
    with pytest.raises(RiskModelError):
        score_intermediary_opacity(None, 10)
    with pytest.raises(RiskModelError):
        score_intermediary_opacity(1, None)


def test_intermediary_opacity_rejects_zero_total():
    with pytest.raises(RiskModelError):
        score_intermediary_opacity(1, 0)


def test_jurisdiction_hopping_bands():
    assert score_jurisdiction_hopping(0) == "Low"
    assert score_jurisdiction_hopping(1) == "Medium"
    assert score_jurisdiction_hopping(2) == "High"
    assert score_jurisdiction_hopping(3) == "Critical"


def test_jurisdiction_hopping_is_required():
    with pytest.raises(RiskModelError):
        score_jurisdiction_hopping(None)


def test_value_fragmentation_bands():
    assert score_value_fragmentation(2) == "Low"
    assert score_value_fragmentation(4) == "Medium"
    assert score_value_fragmentation(7) == "High"
    assert score_value_fragmentation(8) == "Critical"


def test_value_fragmentation_is_required():
    with pytest.raises(RiskModelError):
        score_value_fragmentation(None)


def test_rounding_is_half_up():
    bands = {"chain_depth": "Low", "intermediary_opacity": "Medium",
             "jurisdiction_hopping": "Low", "value_fragmentation": "Low"}
    score, _b, w = ba008_exposure_score(bands)
    assert w["total"] == 22.5 and score == 23


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
