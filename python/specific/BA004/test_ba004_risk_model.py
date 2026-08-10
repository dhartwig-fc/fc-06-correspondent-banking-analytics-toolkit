"""Tests for the BA004 Circular Funds Flow risk model. Run: python3 -m pytest -q"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ba004_risk_model import (  # noqa: E402
    BAND_SCORE, COMPONENT_WEIGHTS, RiskModelError, band_of, ba004_exposure_score,
    score_hop_count, score_loop_closure, score_timing_compression,
    score_value_preservation,
)

CANON = {
    "loop_closure": score_loop_closure(97000, 100000),
    "hop_count": score_hop_count(8),
    "value_preservation": score_value_preservation(0.985),
    "timing_compression": score_timing_compression(8),
}


def test_weights_documented():
    assert COMPONENT_WEIGHTS == {"loop_closure": 0.35, "hop_count": 0.25,
                                  "value_preservation": 0.20, "timing_compression": 0.20}


def test_weights_sum_to_one():
    assert abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) < 1e-9


def test_every_component_required():
    with pytest.raises(RiskModelError):
        ba004_exposure_score({"loop_closure": "Critical"})


def test_canonical_scores_critical():
    score, band, _ = ba004_exposure_score(CANON)
    assert band == "Critical" and score == 90


def test_loop_closure_bands():
    assert score_loop_closure(4000, 10000) == "Low"        # r=0.40
    assert score_loop_closure(6000, 10000) == "Medium"      # r=0.60
    assert score_loop_closure(8500, 10000) == "High"        # r=0.85
    assert score_loop_closure(9600, 10000) == "Critical"    # r=0.96


def test_loop_closure_requires_both_amounts():
    with pytest.raises(RiskModelError):
        score_loop_closure(None, 10000)
    with pytest.raises(RiskModelError):
        score_loop_closure(1000, None)


def test_loop_closure_rejects_zero_originated():
    with pytest.raises(RiskModelError):
        score_loop_closure(1000, 0)


def test_hop_count_bands():
    assert score_hop_count(2) == "Low"
    assert score_hop_count(4) == "Medium"
    assert score_hop_count(6) == "High"
    assert score_hop_count(7) == "Critical"


def test_hop_count_is_required():
    with pytest.raises(RiskModelError):
        score_hop_count(None)


def test_value_preservation_bands():
    assert score_value_preservation(0.75) == "Low"
    assert score_value_preservation(0.85) == "Medium"
    assert score_value_preservation(0.93) == "High"
    assert score_value_preservation(0.98) == "Critical"


def test_value_preservation_is_required():
    with pytest.raises(RiskModelError):
        score_value_preservation(None)


def test_timing_compression_bands():
    assert score_timing_compression(800) == "Low"
    assert score_timing_compression(200) == "Medium"
    assert score_timing_compression(30) == "High"
    assert score_timing_compression(10) == "Critical"


def test_timing_compression_is_required():
    with pytest.raises(RiskModelError):
        score_timing_compression(None)


def test_rounding_is_half_up():
    bands = {"loop_closure": "Low", "hop_count": "Medium",
             "value_preservation": "Low", "timing_compression": "Low"}
    score, _b, w = ba004_exposure_score(bands)
    assert w["total"] == 22.5 and score == 23


def test_band_boundaries():
    assert band_of(79) == "High" and band_of(80) == "Critical"


def test_band_scores_are_midpoints():
    assert BAND_SCORE == {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}
