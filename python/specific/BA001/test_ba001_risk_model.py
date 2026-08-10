"""Tests for the BA001 Structuring risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ba001_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, ba001_exposure_score,
    score_aggregation_to_transfer, score_multi_location, score_sub_threshold_clustering,
    score_temporal_clustering,
)

CANON = {
    "sub_threshold_clustering": score_sub_threshold_clustering(24000, 34000),
    "temporal_clustering": score_temporal_clustering(12),
    "multi_location": score_multi_location(4),
    "aggregation_to_transfer": score_aggregation_to_transfer(17200, 19000),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"sub_threshold_clustering": 0.35, "temporal_clustering": 0.25,
                                  "multi_location": 0.20, "aggregation_to_transfer": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        ba001_exposure_score({"sub_threshold_clustering": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = ba001_exposure_score(CANON)
    assert band == "Critical" and score == 86


def test_sub_threshold_clustering_bands():
    assert score_sub_threshold_clustering(5000, 100000) == "Low"       # r=0.05
    assert score_sub_threshold_clustering(20000, 100000) == "Medium"   # r=0.20
    assert score_sub_threshold_clustering(45000, 100000) == "High"     # r=0.45
    assert score_sub_threshold_clustering(65000, 100000) == "Critical"  # r=0.65


def test_sub_threshold_clustering_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_sub_threshold_clustering(None, 100000)
    with pytest.raises(RiskModelError):
        score_sub_threshold_clustering(5000, None)


def test_sub_threshold_clustering_rejects_zero_total():
    with pytest.raises(RiskModelError):
        score_sub_threshold_clustering(1000, 0)


def test_temporal_clustering_bands():
    assert score_temporal_clustering(2) == "Low"
    assert score_temporal_clustering(5) == "Medium"
    assert score_temporal_clustering(9) == "High"
    assert score_temporal_clustering(10) == "Critical"


def test_temporal_clustering_is_required():
    with pytest.raises(RiskModelError):
        score_temporal_clustering(None)


def test_multi_location_bands():
    assert score_multi_location(1) == "Low"
    assert score_multi_location(2) == "Medium"
    assert score_multi_location(4) == "High"
    assert score_multi_location(5) == "Critical"


def test_multi_location_is_required():
    with pytest.raises(RiskModelError):
        score_multi_location(None)


def test_aggregation_to_transfer_bands():
    assert score_aggregation_to_transfer(1000, 10000) == "Low"      # a=0.10
    assert score_aggregation_to_transfer(3500, 10000) == "Medium"   # a=0.35
    assert score_aggregation_to_transfer(6500, 10000) == "High"     # a=0.65
    assert score_aggregation_to_transfer(9000, 10000) == "Critical"  # a=0.90


def test_aggregation_to_transfer_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_aggregation_to_transfer(None, 10000)
    with pytest.raises(RiskModelError):
        score_aggregation_to_transfer(1000, None)


def test_aggregation_to_transfer_rejects_zero_structured_in():
    with pytest.raises(RiskModelError):
        score_aggregation_to_transfer(1000, 0)


def test_rounding_is_half_up():
    bands = {"sub_threshold_clustering": "Critical", "temporal_clustering": "High",
             "multi_location": "Medium", "aggregation_to_transfer": "Low"}
    score, _b, w = ba001_exposure_score(bands)
    assert w["total"] == 61.0 and score == 61


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
