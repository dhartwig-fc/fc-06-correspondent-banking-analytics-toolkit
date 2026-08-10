"""Tests for the BA009 Transaction Laundering risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ba009_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, ba009_exposure_score,
    score_mcc_inconsistency, score_refund_chargeback_anomaly, score_third_party_indicators,
    score_volume_profile_mismatch,
)

CANON = {
    "volume_profile_mismatch": score_volume_profile_mismatch(1120000, 350000),
    "third_party_indicators": score_third_party_indicators(8),
    "mcc_inconsistency": score_mcc_inconsistency(1100, 2000),
    "refund_chargeback_anomaly": score_refund_chargeback_anomaly(156800, 1120000),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"volume_profile_mismatch": 0.30, "third_party_indicators": 0.25,
                                  "mcc_inconsistency": 0.25, "refund_chargeback_anomaly": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        ba009_exposure_score({"volume_profile_mismatch": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = ba009_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_volume_profile_mismatch_bands():
    assert score_volume_profile_mismatch(100000, 100000) == "Low"        # r=1.00
    assert score_volume_profile_mismatch(130000, 100000) == "Medium"     # r=1.30 (boundary)
    assert score_volume_profile_mismatch(180000, 100000) == "High"       # r=1.80 (boundary)
    assert score_volume_profile_mismatch(250000, 100000) == "Critical"   # r=2.50 (boundary)


def test_volume_profile_mismatch_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_volume_profile_mismatch(None, 100000)
    with pytest.raises(RiskModelError):
        score_volume_profile_mismatch(100000, None)


def test_volume_profile_mismatch_rejects_zero_declared():
    with pytest.raises(RiskModelError):
        score_volume_profile_mismatch(100000, 0)


def test_third_party_indicators_bands():
    assert score_third_party_indicators(1) == "Low"
    assert score_third_party_indicators(2) == "Medium"
    assert score_third_party_indicators(4) == "High"
    assert score_third_party_indicators(7) == "Critical"


def test_third_party_indicators_is_required():
    with pytest.raises(RiskModelError):
        score_third_party_indicators(None)


def test_mcc_inconsistency_bands():
    assert score_mcc_inconsistency(50, 1000) == "Low"        # r=0.05
    assert score_mcc_inconsistency(100, 1000) == "Medium"    # r=0.10 (boundary)
    assert score_mcc_inconsistency(250, 1000) == "High"      # r=0.25 (boundary)
    assert score_mcc_inconsistency(450, 1000) == "Critical"  # r=0.45 (boundary)


def test_mcc_inconsistency_requires_both_counts():
    with pytest.raises(RiskModelError):
        score_mcc_inconsistency(None, 1000)
    with pytest.raises(RiskModelError):
        score_mcc_inconsistency(50, None)


def test_mcc_inconsistency_rejects_zero_total():
    with pytest.raises(RiskModelError):
        score_mcc_inconsistency(50, 0)


def test_refund_chargeback_anomaly_bands():
    assert score_refund_chargeback_anomaly(1000, 100000) == "Low"        # r=0.01
    assert score_refund_chargeback_anomaly(2000, 100000) == "Medium"     # r=0.02 (boundary)
    assert score_refund_chargeback_anomaly(5000, 100000) == "High"       # r=0.05 (boundary)
    assert score_refund_chargeback_anomaly(10000, 100000) == "Critical"  # r=0.10 (boundary)


def test_refund_chargeback_anomaly_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_refund_chargeback_anomaly(None, 100000)
    with pytest.raises(RiskModelError):
        score_refund_chargeback_anomaly(1000, None)


def test_refund_chargeback_anomaly_rejects_zero_total():
    with pytest.raises(RiskModelError):
        score_refund_chargeback_anomaly(1000, 0)


def test_rounding_is_half_up():
    bands = {"volume_profile_mismatch": "Critical", "third_party_indicators": "Medium",
             "mcc_inconsistency": "High", "refund_chargeback_anomaly": "Low"}
    score, _b, w = ba009_exposure_score(bands)
    assert w["total"] == 58.75 and score == 59


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
