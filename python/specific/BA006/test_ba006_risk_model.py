"""Tests for the BA006 Dormant Reactivation risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ba006_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, ba006_exposure_score,
    score_dormancy_length, score_immediate_outflow, score_profile_deviation,
    score_reactivation_spike,
)

CANON = {
    "reactivation_spike": score_reactivation_spike(200000, 8000),
    "dormancy_length": score_dormancy_length(730),
    "profile_deviation": score_profile_deviation(10),
    "immediate_outflow": score_immediate_outflow(190000, 200000),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"reactivation_spike": 0.30, "dormancy_length": 0.25,
                                  "profile_deviation": 0.25, "immediate_outflow": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        ba006_exposure_score({"reactivation_spike": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = ba006_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_reactivation_spike_bands():
    assert score_reactivation_spike(9000, 6000) == "Low"        # r=1.5
    assert score_reactivation_spike(30000, 6000) == "Medium"    # r=5.0
    assert score_reactivation_spike(90000, 6000) == "High"      # r=15.0
    assert score_reactivation_spike(200000, 8000) == "Critical"  # r=25.0


def test_reactivation_spike_requires_both_values():
    with pytest.raises(RiskModelError):
        score_reactivation_spike(None, 6000)
    with pytest.raises(RiskModelError):
        score_reactivation_spike(9000, None)


def test_reactivation_spike_rejects_zero_baseline():
    with pytest.raises(RiskModelError):
        score_reactivation_spike(9000, 0)


def test_dormancy_length_bands():
    assert score_dormancy_length(35) == "Low"
    assert score_dormancy_length(95) == "Medium"
    assert score_dormancy_length(190) == "High"
    assert score_dormancy_length(730) == "Critical"


def test_dormancy_length_is_required():
    with pytest.raises(RiskModelError):
        score_dormancy_length(None)


def test_profile_deviation_bands():
    assert score_profile_deviation(0) == "Low"
    assert score_profile_deviation(3) == "Medium"
    assert score_profile_deviation(7) == "High"
    assert score_profile_deviation(10) == "Critical"


def test_profile_deviation_is_required():
    with pytest.raises(RiskModelError):
        score_profile_deviation(None)


def test_immediate_outflow_bands():
    assert score_immediate_outflow(1500, 7200) == "Low"       # r=0.208
    assert score_immediate_outflow(10500, 19800) == "Medium"  # r=0.530
    assert score_immediate_outflow(40000, 52000) == "High"    # r=0.769
    assert score_immediate_outflow(190000, 200000) == "Critical"  # r=0.95


def test_immediate_outflow_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_immediate_outflow(None, 200000)
    with pytest.raises(RiskModelError):
        score_immediate_outflow(1500, None)


def test_immediate_outflow_rejects_zero_reactivation():
    with pytest.raises(RiskModelError):
        score_immediate_outflow(1500, 0)


def test_rounding_is_half_up():
    bands = {"reactivation_spike": "Low", "dormancy_length": "Medium",
             "profile_deviation": "Low", "immediate_outflow": "Low"}
    score, _b, w = ba006_exposure_score(bands)
    assert w["total"] == 22.5 and score == 23


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
