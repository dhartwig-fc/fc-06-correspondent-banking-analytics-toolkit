"""Tests for the BA003 Mule Accounts risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ba003_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, ba003_exposure_score,
    score_account_youth, score_behavioural_mismatch, score_network_linkage,
    score_pass_through_ratio,
)

CANON = {
    "pass_through_ratio": score_pass_through_ratio(96000, 100000),
    "account_youth": score_account_youth(12),
    "behavioural_mismatch": score_behavioural_mismatch(92000, 3200),
    "network_linkage": score_network_linkage(6),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"pass_through_ratio": 0.30, "account_youth": 0.25,
                                  "behavioural_mismatch": 0.25, "network_linkage": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        ba003_exposure_score({"pass_through_ratio": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = ba003_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_pass_through_ratio_bands():
    assert score_pass_through_ratio(4000, 10000) == "Low"        # r=0.40
    assert score_pass_through_ratio(6000, 10000) == "Medium"     # r=0.60
    assert score_pass_through_ratio(8500, 10000) == "High"       # r=0.85
    assert score_pass_through_ratio(9600, 10000) == "Critical"   # r=0.96


def test_pass_through_ratio_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_pass_through_ratio(None, 10000)
    with pytest.raises(RiskModelError):
        score_pass_through_ratio(1000, None)


def test_pass_through_ratio_rejects_zero_inflow():
    with pytest.raises(RiskModelError):
        score_pass_through_ratio(1000, 0)


def test_account_youth_bands():
    assert score_account_youth(400) == "Low"
    assert score_account_youth(200) == "Medium"
    assert score_account_youth(65) == "High"
    assert score_account_youth(30) == "Critical"


def test_account_youth_is_required():
    with pytest.raises(RiskModelError):
        score_account_youth(None)


def test_behavioural_mismatch_bands():
    assert score_behavioural_mismatch(6000, 4000) == "Low"        # r=1.5
    assert score_behavioural_mismatch(24000, 4000) == "Medium"    # r=6.0
    assert score_behavioural_mismatch(60000, 4000) == "High"      # r=15.0
    assert score_behavioural_mismatch(100000, 4000) == "Critical"  # r=25.0


def test_behavioural_mismatch_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_behavioural_mismatch(None, 4000)
    with pytest.raises(RiskModelError):
        score_behavioural_mismatch(6000, None)


def test_behavioural_mismatch_rejects_zero_income():
    with pytest.raises(RiskModelError):
        score_behavioural_mismatch(6000, 0)


def test_network_linkage_bands():
    assert score_network_linkage(0) == "Low"
    assert score_network_linkage(1) == "Medium"
    assert score_network_linkage(3) == "High"
    assert score_network_linkage(4) == "Critical"


def test_network_linkage_is_required():
    with pytest.raises(RiskModelError):
        score_network_linkage(None)


def test_rounding_is_half_up():
    bands = {"pass_through_ratio": "Critical", "account_youth": "High",
             "behavioural_mismatch": "Medium", "network_linkage": "Low"}
    score, _b, w = ba003_exposure_score(bands)
    assert w["total"] == 58.75 and score == 59


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
