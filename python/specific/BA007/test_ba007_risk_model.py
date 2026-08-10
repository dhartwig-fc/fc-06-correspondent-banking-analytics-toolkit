"""Tests for the BA007 Cash Intensive Activity risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ba007_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, ba007_exposure_score,
    score_cash_ratio, score_commingling, score_deposit_regularity, score_profile_excess,
)

CANON = {
    "cash_ratio": score_cash_ratio(760000, 820000, 0.30),
    "profile_excess": score_profile_excess(760000, 300000),
    "deposit_regularity": score_deposit_regularity(8),
    "commingling": score_commingling(250000, 760000),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"cash_ratio": 0.35, "profile_excess": 0.25,
                                  "deposit_regularity": 0.20, "commingling": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        ba007_exposure_score({"cash_ratio": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = ba007_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_cash_ratio_bands():
    assert score_cash_ratio(25000, 100000, 0.25) == "Low"       # excess 1.00
    assert score_cash_ratio(32500, 100000, 0.25) == "Medium"    # excess 1.30 (boundary)
    assert score_cash_ratio(45000, 100000, 0.25) == "High"      # excess 1.80 (boundary)
    assert score_cash_ratio(62500, 100000, 0.25) == "Critical"  # excess 2.50 (boundary)


def test_cash_ratio_requires_all_three():
    with pytest.raises(RiskModelError):
        score_cash_ratio(None, 100000, 0.25)
    with pytest.raises(RiskModelError):
        score_cash_ratio(25000, None, 0.25)
    with pytest.raises(RiskModelError):
        score_cash_ratio(25000, 100000, None)


def test_cash_ratio_rejects_zero_turnover_or_peer_norm():
    with pytest.raises(RiskModelError):
        score_cash_ratio(25000, 0, 0.25)
    with pytest.raises(RiskModelError):
        score_cash_ratio(25000, 100000, 0)


def test_profile_excess_bands():
    assert score_profile_excess(100000, 100000) == "Low"        # r=1.00
    assert score_profile_excess(110000, 100000) == "Medium"     # r=1.10 (boundary)
    assert score_profile_excess(150000, 100000) == "High"       # r=1.50 (boundary)
    assert score_profile_excess(220000, 100000) == "Critical"   # r=2.20 (boundary)


def test_profile_excess_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_profile_excess(None, 100000)
    with pytest.raises(RiskModelError):
        score_profile_excess(100000, None)


def test_profile_excess_rejects_zero_declared():
    with pytest.raises(RiskModelError):
        score_profile_excess(100000, 0)


def test_deposit_regularity_bands():
    assert score_deposit_regularity(45) == "Low"
    assert score_deposit_regularity(30) == "Medium"
    assert score_deposit_regularity(15) == "High"
    assert score_deposit_regularity(14) == "Critical"


def test_deposit_regularity_is_required():
    with pytest.raises(RiskModelError):
        score_deposit_regularity(None)


def test_commingling_bands():
    assert score_commingling(4000, 100000) == "Low"        # r=0.04
    assert score_commingling(5000, 100000) == "Medium"     # r=0.05 (boundary)
    assert score_commingling(15000, 100000) == "High"      # r=0.15 (boundary)
    assert score_commingling(30000, 100000) == "Critical"  # r=0.30 (boundary)


def test_commingling_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_commingling(None, 100000)
    with pytest.raises(RiskModelError):
        score_commingling(4000, None)


def test_commingling_rejects_zero_total():
    with pytest.raises(RiskModelError):
        score_commingling(4000, 0)


def test_rounding_is_half_up():
    bands = {"cash_ratio": "Critical", "profile_excess": "Medium",
             "deposit_regularity": "High", "commingling": "Low"}
    score, _b, w = ba007_exposure_score(bands)
    assert w["total"] == 59.75 and score == 60


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
