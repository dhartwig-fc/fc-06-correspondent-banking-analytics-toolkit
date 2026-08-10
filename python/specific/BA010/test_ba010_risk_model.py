"""Tests for the BA010 Peer Group Anomalies risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ba010_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, ba010_exposure_score,
    score_counterparty_diversity_zscore, score_product_usage_deviation, score_velocity_zscore,
    score_volume_zscore,
)

CANON = {
    "volume_zscore": score_volume_zscore(355000, 250000, 25000),
    "velocity_zscore": score_velocity_zscore(27, 12, 4),
    "product_usage_deviation": score_product_usage_deviation(13, 6, 2),
    "counterparty_diversity_zscore": score_counterparty_diversity_zscore(20, 12, 2),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"volume_zscore": 0.30, "velocity_zscore": 0.25,
                                  "product_usage_deviation": 0.25, "counterparty_diversity_zscore": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        ba010_exposure_score({"volume_zscore": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = ba010_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_volume_zscore_bands():
    assert score_volume_zscore(250000, 250000, 25000) == "Low"        # z=0.00
    assert score_volume_zscore(275000, 250000, 25000) == "Medium"     # z=1.00 (boundary)
    assert score_volume_zscore(300000, 250000, 25000) == "High"       # z=2.00 (boundary)
    assert score_volume_zscore(325000, 250000, 25000) == "Critical"   # z=3.00 (boundary)


def test_volume_zscore_is_symmetric_on_sign():
    assert score_volume_zscore(200000, 250000, 25000) == "High"       # z=-2.00 (boundary)
    assert score_volume_zscore(225000, 250000, 25000) == "Medium"     # z=-1.00 (boundary)


def test_volume_zscore_requires_all_three():
    with pytest.raises(RiskModelError):
        score_volume_zscore(None, 250000, 25000)
    with pytest.raises(RiskModelError):
        score_volume_zscore(250000, None, 25000)
    with pytest.raises(RiskModelError):
        score_volume_zscore(250000, 250000, None)


def test_volume_zscore_rejects_zero_std():
    with pytest.raises(RiskModelError):
        score_volume_zscore(300000, 250000, 0)


def test_velocity_zscore_bands():
    assert score_velocity_zscore(12, 12, 4) == "Low"        # z=0.00
    assert score_velocity_zscore(16, 12, 4) == "Medium"     # z=1.00 (boundary)
    assert score_velocity_zscore(20, 12, 4) == "High"       # z=2.00 (boundary)
    assert score_velocity_zscore(24, 12, 4) == "Critical"   # z=3.00 (boundary)


def test_velocity_zscore_is_required():
    with pytest.raises(RiskModelError):
        score_velocity_zscore(None, 12, 4)


def test_product_usage_deviation_bands():
    assert score_product_usage_deviation(6, 6, 2) == "Low"        # z=0.00
    assert score_product_usage_deviation(8, 6, 2) == "Medium"     # z=1.00 (boundary)
    assert score_product_usage_deviation(10, 6, 2) == "High"      # z=2.00 (boundary)
    assert score_product_usage_deviation(12, 6, 2) == "Critical"  # z=3.00 (boundary)
    assert score_product_usage_deviation(1, 6, 2) == "High"       # a narrow footprint also deviates (z=-2.5)


def test_product_usage_deviation_rejects_zero_std():
    with pytest.raises(RiskModelError):
        score_product_usage_deviation(8, 6, 0)


def test_counterparty_diversity_zscore_bands():
    assert score_counterparty_diversity_zscore(12, 12, 2) == "Low"        # z=0.00
    assert score_counterparty_diversity_zscore(14, 12, 2) == "Medium"     # z=1.00 (boundary)
    assert score_counterparty_diversity_zscore(16, 12, 2) == "High"       # z=2.00 (boundary)
    assert score_counterparty_diversity_zscore(18, 12, 2) == "Critical"   # z=3.00 (boundary)


def test_counterparty_diversity_zscore_requires_all_three():
    with pytest.raises(RiskModelError):
        score_counterparty_diversity_zscore(None, 12, 2)
    with pytest.raises(RiskModelError):
        score_counterparty_diversity_zscore(14, None, 2)
    with pytest.raises(RiskModelError):
        score_counterparty_diversity_zscore(14, 12, None)


def test_rounding_is_half_up():
    bands = {"volume_zscore": "Critical", "velocity_zscore": "Medium",
             "product_usage_deviation": "High", "counterparty_diversity_zscore": "Low"}
    score, _b, w = ba010_exposure_score(bands)
    assert w["total"] == 58.75 and score == 59


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
