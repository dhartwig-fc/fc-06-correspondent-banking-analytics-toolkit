"""Tests for the BA005 Rapid Movement risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ba005_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, ba005_exposure_score,
    score_dwell_time, score_onward_dispersion, score_value_match, score_velocity,
)

CANON = {
    "dwell_time": score_dwell_time(1),
    "velocity": score_velocity(300000, 10000),
    "onward_dispersion": score_onward_dispersion(9),
    "value_match": score_value_match(98000, 100000),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"dwell_time": 0.35, "velocity": 0.25,
                                  "onward_dispersion": 0.20, "value_match": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        ba005_exposure_score({"dwell_time": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = ba005_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_dwell_time_bands():
    assert score_dwell_time(960) == "Low"
    assert score_dwell_time(40) == "Medium"
    assert score_dwell_time(10) == "High"
    assert score_dwell_time(1) == "Critical"


def test_dwell_time_is_required():
    with pytest.raises(RiskModelError):
        score_dwell_time(None)


def test_velocity_bands():
    assert score_velocity(30000, 15000) == "Low"       # r=2.0
    assert score_velocity(60000, 15000) == "Medium"     # r=4.0
    assert score_velocity(150000, 12000) == "High"      # r=12.5
    assert score_velocity(300000, 10000) == "Critical"  # r=30.0


def test_velocity_requires_both_values():
    with pytest.raises(RiskModelError):
        score_velocity(None, 10000)
    with pytest.raises(RiskModelError):
        score_velocity(30000, None)


def test_velocity_rejects_zero_balance():
    with pytest.raises(RiskModelError):
        score_velocity(30000, 0)


def test_onward_dispersion_bands():
    assert score_onward_dispersion(1) == "Low"
    assert score_onward_dispersion(4) == "Medium"
    assert score_onward_dispersion(7) == "High"
    assert score_onward_dispersion(9) == "Critical"


def test_onward_dispersion_is_required():
    with pytest.raises(RiskModelError):
        score_onward_dispersion(None)


def test_value_match_bands():
    assert score_value_match(8000, 20000) == "Low"       # r=0.40
    assert score_value_match(45000, 70000) == "Medium"   # r=0.643
    assert score_value_match(68000, 80000) == "High"     # r=0.85
    assert score_value_match(98000, 100000) == "Critical"  # r=0.98


def test_value_match_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_value_match(None, 100000)
    with pytest.raises(RiskModelError):
        score_value_match(8000, None)


def test_value_match_rejects_zero_inbound():
    with pytest.raises(RiskModelError):
        score_value_match(8000, 0)


def test_rounding_is_half_up():
    bands = {"dwell_time": "Low", "velocity": "Medium",
             "onward_dispersion": "Low", "value_match": "Low"}
    score, _b, w = ba005_exposure_score(bands)
    assert w["total"] == 22.5 and score == 23


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
