"""TT-BA004 (night 9, wave A): the BA004 Circular Funds Flow engine against its doctrine.

Oracle, and nothing else: scoring-models/specific/BA004_Circular_Funds_Flow_Scoring_Framework.md
(component cut-lines, weights, midpoints, half-up, alert at >= 80, every input REQUIRED,
originated_amount > 0), typologies/BA004_Circular_Funds_Flow.md (bands 0-29/30-59/60-79/80-100,
the CYC019 worked example) and the signed-off expected-outcome sheet BA004.md (2026-10-21;
R1: the band table governs over the doctrine's Python snippet; R3: near misses must not
alert). Every expected score below is hand-worked from those numbers in a comment beside
it. Inputs are CONSTRUCTED here: no sample-data file is read and no sample entity's name is
asserted.

Contributions per band (midpoint x weight), from the framework:
    loop closure       35%: L 5.25  M 15.75  H 24.5  C 31.5
    hop count          25%: L 3.75  M 11.25  H 17.5  C 22.5
    value preservation 20%: L 3     M 9      H 14    C 18
    timing compression 20%: L 3     M 9      H 14    C 18
"""

from __future__ import annotations

import json
import math
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from ba004_risk_model import (  # noqa: E402
    RiskModelError, band_of, ba004_exposure_score, score_hop_count, score_loop_closure,
    score_timing_compression, score_value_preservation,
)

SCENARIO = BASE_DIR / "scenarios" / "circular_funds_flow.py"
NAMES = ("loop_closure", "hop_count", "value_preservation", "timing_compression")
BAND_COLS = {"loop_closure": "loop_closure_band", "hop_count": "hop_count_band",
             "value_preservation": "value_preservation_band",
             "timing_compression": "timing_compression_band"}


def _load():
    spec = spec_from_file_location("tt_ba004_doctrine_circular_funds_flow", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def engine():
    return _load()


def _bands(code):
    """'CHHC' -> the four component bands in framework order."""
    full = {"L": "Low", "M": "Medium", "H": "High", "C": "Critical"}
    return dict(zip(NAMES, (full[c] for c in code)))


def _account(ref, originated, returned, hops, retention, hours):
    return {"customer_name": "Constructed Originator %s" % ref, "account_ref": ref,
            "segment": "Corporate", "home_branch": "Constructed Branch",
            "originated_amount": originated, "returned_amount": returned,
            "hop_count": hops, "avg_hop_retention_pct": retention,
            "loop_duration_hours": hours,
            "first_loop_member_name": "Constructed First Hop %s" % ref,
            "second_loop_member_name": "Constructed Second Hop %s" % ref,
            "closure_member_name": "Constructed Closure %s" % ref}


def _frames(*accounts):
    acc = pd.DataFrame(list(accounts))
    members = pd.DataFrame([{"closure_member_name": a["closure_member_name"],
                             "account_ref": a["account_ref"], "bank": "Constructed Bank",
                             "jurisdiction": "GB", "relationship": "closure",
                             "prior_alerts": 0} for a in accounts])
    return {"accounts": acc, "loop_members": members}


# ---------------------------------------------------------------- check 2: boundaries
# Each cut-line from the framework: exactly at it, just below, just above.

@pytest.mark.parametrize("returned,band", [
    (4999, "Low"), (5000, "Medium"), (5001, "Medium"),        # r < 0.50 -> Low
    (7499, "Medium"), (7500, "High"), (7501, "High"),         # r < 0.75 -> Medium
    (9199, "High"), (9200, "Critical"), (9201, "Critical"),   # r < 0.92 -> High, otherwise Critical
])
def test_loop_closure_cut_lines(returned, band):
    assert score_loop_closure(returned, 10000) == band


def test_loop_closure_is_returned_over_originated():
    # r = 3000/10000 = 0.30 Low; the inverse (3.33) would be Critical.
    assert score_loop_closure(3000, 10000) == "Low"


@pytest.mark.parametrize("originated", [0, -1, -10000])
def test_loop_closure_refuses_originated_not_above_zero(originated):
    # Framework: "originated_amount must be > 0".
    with pytest.raises(RiskModelError):
        score_loop_closure(5000, originated)


@pytest.mark.parametrize("hops,band", [
    (2, "Low"), (3, "Medium"),                       # <= 2 Low
    (4, "Medium"), (5, "High"),                      # <= 4 Medium
    (6, "High"), (7, "Critical"), (8, "Critical"),   # <= 6 High, otherwise (>= 7) Critical
])
def test_hop_count_cut_lines(hops, band):
    assert score_hop_count(hops) == band


@pytest.mark.parametrize("retention,band", [
    (0.7999, "Low"), (0.80, "Medium"), (0.8001, "Medium"),     # < 0.80 Low
    (0.8999, "Medium"), (0.90, "High"), (0.9001, "High"),      # < 0.90 Medium
    (0.9699, "High"), (0.97, "Critical"), (0.9701, "Critical"),  # < 0.97 High, >= 0.97 Critical
])
def test_value_preservation_cut_lines(retention, band):
    assert score_value_preservation(retention) == band


@pytest.mark.parametrize("hours,band", [
    (720.01, "Low"), (720, "Low"), (719.99, "Medium"),       # >= 720 Low
    (168.01, "Medium"), (168, "Medium"), (167.99, "High"),   # >= 168 Medium
    (24.01, "High"), (24, "High"), (23.99, "Critical"),      # >= 24 High, otherwise (< 24) Critical
])
def test_timing_compression_cut_lines(hours, band):
    assert score_timing_compression(hours) == band


@pytest.mark.parametrize("score,band", [
    (0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
    (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical"),
])
def test_score_band_table(score, band):
    # typologies/BA004_Circular_Funds_Flow.md Classification: 0-29 Low, 30-59 Medium,
    # 60-79 High, 80-100 Critical
    assert band_of(score) == band


@pytest.mark.parametrize("code,score,band", [
    ("CCCC", 90, "Critical"),   # 31.5+22.5+18+18 = 90 (framework worked example CYC019)
    ("LLLL", 15, "Low"),        # 5.25+3.75+3+3 = 15 (framework: clean account 15/100)
    ("CLLL", 41, "Medium"),     # 31.5+3.75+3+3 = 41.25 -> 41
    ("LCLL", 34, "Medium"),     # 5.25+22.5+3+3 = 33.75 -> 34
    ("LLCL", 30, "Medium"),     # 5.25+3.75+18+3 = 30
    ("LLLC", 30, "Medium"),     # 5.25+3.75+3+18 = 30
    ("CHHC", 81, "Critical"),   # 31.5+17.5+14+18 = 81
    ("HCCH", 79, "High"),       # 24.5+22.5+18+14 = 79
    ("MMMM", 45, "Medium"),     # every component at the Medium midpoint
    ("HHHH", 70, "High"),       # every component at the High midpoint
])
def test_weighted_midpoint_score(code, score, band):
    got_score, got_band, working = ba004_exposure_score(_bands(code))
    assert (got_score, got_band) == (score, band)
    assert len(working["components"]) == 4


def test_half_up_rounding_on_an_exact_half():
    # LMLL: 5.25 + 11.25 + 3 + 3 = 22.5 exactly. Half-up -> 23 (half-even would give 22).
    score, band, working = ba004_exposure_score(_bands("LMLL"))
    assert working["total"] == 22.5
    assert (score, band) == (23, "Low")


def test_alert_threshold_is_inclusive_at_80(engine, monkeypatch):
    """With these weights no band combination scores exactly 80 (79 and 81 are the
    neighbours), so the >= 80 filter is checked by fixing the scorer's output at 80 and 79."""
    real = engine.ba004_exposure_score

    def fixed(bands, value):
        _s, _b, working = real(bands)
        return value, band_of(value), working

    frames = _frames(_account("T80", 10000, 9700, 8, 0.985, 8))
    monkeypatch.setattr(engine, "ba004_exposure_score", lambda b: fixed(b, 80))
    assert list(engine.evaluate_circular_funds_flow(**frames)["account_ref"]) == ["T80"]
    monkeypatch.setattr(engine, "ba004_exposure_score", lambda b: fixed(b, 79))
    assert len(engine.evaluate_circular_funds_flow(**frames)) == 0


# ---------------------------------------------------------------- check 4: positives / near-misses

def test_worked_example_alerts_90_critical(engine):
    # Framework worked example: $97,000 of $100,000 returns (r 0.970), 8 hops, 98.5% retained,
    # 8 hours: all Critical -> 31.5+22.5+18+18 = 90 Critical, alerts.
    out = engine.evaluate_circular_funds_flow(**_frames(_account("T-WE", 100000, 97000, 8, 0.985, 8)))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["exposure_score"], row["exposure_band"]) == (90, "Critical")
    assert [row[BAND_COLS[n]] for n in NAMES] == ["Critical"] * 4
    # the signals the sheet says must be present on a true alert
    assert (row["returned_amount"], row["originated_amount"]) == (97000, 100000)
    assert (row["hop_count"], row["avg_hop_retention_pct"], row["loop_duration_hours"]) == (8, 0.985, 8.0)
    assert row["closure_member_name"] == "Constructed Closure T-WE"
    assert row["subject_entity_id"] == "T-WE"


def test_background_one_way_flow_scores_15_and_does_not_alert(engine):
    # Sheet background: ordinary one-way flow, no return to origin. r = 0 (L), 1 hop (L),
    # 70% retained (L), 960 hours (L): 15/100 (framework: all-Low scores 15), no alert.
    frames = _frames(_account("T-BG", 50000, 0, 1, 0.70, 960))
    scored = engine.score_all(**frames)
    assert (scored.iloc[0]["exposure_score"], scored.iloc[0]["exposure_band"]) == (15, "Low")
    assert len(engine.evaluate_circular_funds_flow(**frames)) == 0


def test_sheet_near_miss_eroded_and_slow_return_does_not_alert(engine):
    # Sheet near miss: funds return, but with fee/FX erosion and weeks-long timing.
    # r 0.97 (C), 5 hops (H), 85% retained (M), 400 hours (M): 31.5+17.5+9+9 = 67 High, no alert.
    frames = _frames(_account("T-NM", 10000, 9700, 5, 0.85, 400))
    scored = engine.score_all(**frames)
    assert (scored.iloc[0]["exposure_score"], scored.iloc[0]["exposure_band"]) == (67, "High")
    assert len(engine.evaluate_circular_funds_flow(**frames)) == 0


# One positive and one near-miss per detection rule (component). The positive sits EXACTLY on the
# component's Critical cut-line (timing: just inside it, < 24); the near-miss moves only that
# component just outside it.
PER_RULE = {
    # closure r = 0.92 (C) with 5 hops (H), 0.93 (H), 8 h (C):
    #   31.5+17.5+14+18 = 81 alert;   r = 0.9199 (H): 24.5+17.5+14+18 = 74 no alert
    "loop_closure": (_account("P-LC", 10000, 9200, 5, 0.93, 8),
                     _account("N-LC", 10000, 9199, 5, 0.93, 8), 81, 74),
    # 7 hops (C) with r 0.97 (C), 0.93 (H), 48 h (H):
    #   31.5+22.5+14+14 = 82 alert;   6 hops (H): 31.5+17.5+14+14 = 77 no alert
    "hop_count": (_account("P-HC", 10000, 9700, 7, 0.93, 48),
                  _account("N-HC", 10000, 9700, 6, 0.93, 48), 82, 77),
    # retention 0.97 (C) with r 0.97 (C), 5 hops (H), 48 h (H):
    #   31.5+17.5+18+14 = 81 alert;   0.9699 (H): 31.5+17.5+14+14 = 77 no alert
    "value_preservation": (_account("P-VP", 10000, 9700, 5, 0.97, 48),
                           _account("N-VP", 10000, 9700, 5, 0.9699, 48), 81, 77),
    # 23.99 h (C) with r 0.97 (C), 5 hops (H), 0.93 (H):
    #   31.5+17.5+14+18 = 81 alert;   24 h (H): 31.5+17.5+14+14 = 77 no alert
    "timing_compression": (_account("P-TC", 10000, 9700, 5, 0.93, 23.99),
                           _account("N-TC", 10000, 9700, 5, 0.93, 24), 81, 77),
}


@pytest.mark.parametrize("rule", sorted(PER_RULE))
def test_positive_and_near_miss_per_rule(engine, rule):
    positive, near, pos_score, near_score = PER_RULE[rule]
    frames = _frames(positive, near)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert scored.loc[positive["account_ref"], BAND_COLS[rule]] == "Critical"
    assert scored.loc[near["account_ref"], BAND_COLS[rule]] == "High"
    assert (scored.loc[positive["account_ref"], "exposure_score"],
            scored.loc[positive["account_ref"], "exposure_band"]) == (pos_score, "Critical")
    assert scored.loc[near["account_ref"], "exposure_score"] == near_score
    assert scored.loc[near["account_ref"], "exposure_band"] == "High"
    alerts = engine.evaluate_circular_funds_flow(**frames)
    assert list(alerts["account_ref"]) == [positive["account_ref"]]


def test_alert_row_carries_its_own_working(engine):
    # r 0.97 C, 7 C, 0.93 H, 48 h H = CCHH: 31.5+22.5+14+14 = 82 Critical
    out = engine.evaluate_circular_funds_flow(**_frames(_account("T-W", 10000, 9700, 7, 0.93, 48)))
    working = json.loads(out.iloc[0]["risk_components"])
    assert set(working["components"]) == set(NAMES)
    assert working["score"] == 82 and working["band"] == "Critical"


def test_score_all_puts_the_highest_score_first(engine):
    # The fc-10 demo path builds its case from score_all's top row (framework, final paragraph).
    frames = _frames(_account("T-LOW", 50000, 0, 1, 0.70, 960),
                     _account("T-HIGH", 100000, 97000, 8, 0.985, 8))
    assert list(engine.score_all(**frames)["account_ref"]) == ["T-HIGH", "T-LOW"]


# ---------------------------------------------------------------- required inputs

NAN = float("nan")


def test_a_missing_hop_count_refuses():
    # Framework: hop_count is REQUIRED. NaN is refused (int(float(nan)) raises ValueError).
    with pytest.raises(ValueError):
        score_hop_count(NAN)


# ---------------------------------------------------------------- defects

@pytest.mark.parametrize("scorer,args", [
    (score_loop_closure, (NAN, 10000)),
    (score_loop_closure, (9000, NAN)),
    (score_value_preservation, (NAN,)),
    (score_timing_compression, (NAN,)),
])
@pytest.mark.xfail(strict=True, reason=(
    "DEFECT: framework BA004 'Both amounts are REQUIRED' / 'avg_hop_retention_pct is REQUIRED' / "
    "'loop_duration_hours is REQUIRED' (scoring-models/specific/BA004_Circular_Funds_Flow_Scoring_"
    "Framework.md:18,28,35) and the model's own 'missing != zero': a missing (NaN) value passes "
    "ba004_risk_model.py:60-61 (_require checks None only), every comparison at :83-89 / :112-118 / "
    ":125-131 is False, so it scores Critical -- measured: Failed: DID NOT RAISE <class "
    "'ValueError'>. Sibling of BA001 D1"))
def test_a_missing_value_refuses_rather_than_scoring_critical(scorer, args):
    assert any(isinstance(a, float) and math.isnan(a) for a in args)
    with pytest.raises(ValueError):
        scorer(*args)


@pytest.mark.parametrize("field", ["avg_hop_retention_pct", "loop_duration_hours"])
@pytest.mark.xfail(strict=True, reason=(
    "DEFECT: same REQUIRED rule, end to end: a constructed account whose retention or duration is "
    "missing (NaN) is scored Critical on that component, lifting a 77 High non-alert to 81 Critical, and "
    "ALERTED by evaluate_circular_funds_flow (scenarios/circular_funds_flow.py:71-72 -> "
    "ba004_risk_model.py:111,124) instead of refusing -- measured: Failed: DID NOT RAISE <class "
    "'ValueError'>. Sibling of BA001 D1"))
def test_the_callable_refuses_an_account_with_a_missing_input(engine, field):
    # r 0.97 C, 5 hops H, 0.93 H, 48 h H = 31.5+17.5+14+14 = 77 High with every input present (no
    # alert); with `field` missing it must refuse rather than score.
    account = _account("T-NAN", 10000, 9700, 5, 0.93, 48)
    assert engine.score_all(**_frames(account)).iloc[0]["exposure_score"] == 77
    assert len(engine.evaluate_circular_funds_flow(**_frames(account))) == 0
    account[field] = NAN
    with pytest.raises(ValueError):
        engine.evaluate_circular_funds_flow(**_frames(account))
