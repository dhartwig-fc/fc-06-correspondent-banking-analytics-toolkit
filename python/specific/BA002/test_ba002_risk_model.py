"""Tests for the BA002 Funnel Accounts risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ba002_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, ba002_exposure_score,
    score_beneficiary_concentration, score_geographic_dispersion, score_inflow_fan_in,
    score_rapid_passthrough,
)

CANON = {
    "geographic_dispersion": score_geographic_dispersion(7),
    "inflow_fan_in": score_inflow_fan_in(33),
    "rapid_passthrough": score_rapid_passthrough(3),
    "beneficiary_concentration": score_beneficiary_concentration(90000, 100000),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"geographic_dispersion": 0.30, "inflow_fan_in": 0.25,
                                  "rapid_passthrough": 0.25, "beneficiary_concentration": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        ba002_exposure_score({"geographic_dispersion": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = ba002_exposure_score(CANON)
    assert band == "Critical" and score == 84


def test_geographic_dispersion_bands():
    assert score_geographic_dispersion(2) == "Low"
    assert score_geographic_dispersion(3) == "Medium"
    assert score_geographic_dispersion(7) == "High"
    assert score_geographic_dispersion(8) == "Critical"


def test_geographic_dispersion_is_required():
    with pytest.raises(RiskModelError):
        score_geographic_dispersion(None)


def test_inflow_fan_in_bands():
    assert score_inflow_fan_in(5) == "Low"
    assert score_inflow_fan_in(15) == "Medium"
    assert score_inflow_fan_in(30) == "High"
    assert score_inflow_fan_in(31) == "Critical"


def test_inflow_fan_in_is_required():
    with pytest.raises(RiskModelError):
        score_inflow_fan_in(None)


def test_rapid_passthrough_bands():
    assert score_rapid_passthrough(72) == "Low"
    assert score_rapid_passthrough(24) == "Medium"
    assert score_rapid_passthrough(6) == "High"
    assert score_rapid_passthrough(5) == "Critical"


def test_rapid_passthrough_is_required():
    with pytest.raises(RiskModelError):
        score_rapid_passthrough(None)


def test_beneficiary_concentration_bands():
    assert score_beneficiary_concentration(1000, 10000) == "Low"      # r=0.10
    assert score_beneficiary_concentration(3500, 10000) == "Medium"   # r=0.35
    assert score_beneficiary_concentration(6500, 10000) == "High"     # r=0.65
    assert score_beneficiary_concentration(9000, 10000) == "Critical"  # r=0.90


def test_beneficiary_concentration_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_beneficiary_concentration(None, 10000)
    with pytest.raises(RiskModelError):
        score_beneficiary_concentration(1000, None)


def test_beneficiary_concentration_rejects_zero_total():
    with pytest.raises(RiskModelError):
        score_beneficiary_concentration(1000, 0)


def test_rounding_is_half_up():
    bands = {"geographic_dispersion": "Critical", "inflow_fan_in": "High",
             "rapid_passthrough": "Medium", "beneficiary_concentration": "Low"}
    score, _b, w = ba002_exposure_score(bands)
    assert w["total"] == 58.75 and score == 59


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
