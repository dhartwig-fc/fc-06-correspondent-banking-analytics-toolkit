"""TT-BA001 (night 9, wave A): the BA001 Structuring engine against its doctrine.

Oracle, and nothing else: scoring-models/specific/BA001_Structuring_Scoring_Framework.md
(component cut-lines, weights, midpoints, half-up, alert at >= 80),
typologies/BA001_Structuring.md (bands 0-29/30-59/60-79/80-100, the ACC019 worked
example) and the signed-off expected-outcome sheet BA001.md (2026-10-21; R1: the band
table governs over the doctrine's Python filter snippet). Every expected score below is
hand-worked from those numbers in a comment beside it. Inputs are CONSTRUCTED here:
no sample-data file is read and no sample entity's name is asserted.

Contributions per band (midpoint x weight), from the framework:
    sub-threshold 35%: L 5.25  M 15.75  H 24.5  C 31.5
    temporal      25%: L 3.75  M 11.25  H 17.5  C 22.5
    multi-loc     20%: L 3     M 9      H 14    C 18
    aggregation   20%: L 3     M 9      H 14    C 18
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

from ba001_risk_model import (  # noqa: E402
    RiskModelError, band_of, ba001_exposure_score, score_aggregation_to_transfer,
    score_multi_location, score_sub_threshold_clustering, score_temporal_clustering,
)

SCENARIO = BASE_DIR / "scenarios" / "structuring.py"
NAMES = ("sub_threshold_clustering", "temporal_clustering", "multi_location", "aggregation_to_transfer")


def _load():
    spec = spec_from_file_location("tt_ba001_doctrine_structuring", SCENARIO)
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


def _account(ref, total, sub, max7d, locations, structured_in, wired_out):
    return {"account_ref": ref, "customer_name": "Constructed Depositor %s" % ref,
            "segment": "Retail", "home_branch": "Constructed Branch",
            "total_cash_deposits": total, "subthreshold_deposits": sub,
            "deposits_max_7d": max7d, "distinct_locations": locations,
            "structured_in_amount": structured_in, "wired_out_amount": wired_out,
            "beneficiary_name": "Constructed Beneficiary %s" % ref}


def _frames(*accounts):
    acc = pd.DataFrame(list(accounts))
    ben = pd.DataFrame([{"beneficiary_name": a["beneficiary_name"], "account_ref": a["account_ref"],
                         "bank": "Constructed Bank", "jurisdiction": "GB",
                         "relationship": "beneficiary", "prior_alerts": 0} for a in accounts])
    return {"accounts": acc, "beneficiaries": ben}


# ---------------------------------------------------------------- check 2: boundaries
# Each cut-line from the framework: exactly at it, just below, just above.

@pytest.mark.parametrize("sub,band", [
    (999, "Low"), (1000, "Medium"), (1001, "Medium"),        # r < 0.10 -> Low
    (2999, "Medium"), (3000, "High"), (3001, "High"),        # r < 0.30 -> Medium
    (5999, "High"), (6000, "Critical"), (6001, "Critical"),  # r < 0.60 -> High, otherwise Critical
])
def test_sub_threshold_ratio_cut_lines(sub, band):
    assert score_sub_threshold_clustering(sub, 10000) == band


@pytest.mark.parametrize("n,band", [
    (2, "Low"), (3, "Medium"),          # <= 2 Low
    (5, "Medium"), (6, "High"),         # <= 5 Medium
    (9, "High"), (10, "Critical"), (11, "Critical"),   # <= 9 High, >= 10 Critical
])
def test_temporal_count_cut_lines(n, band):
    assert score_temporal_clustering(n) == band


@pytest.mark.parametrize("n,band", [
    (1, "Low"), (2, "Medium"), (3, "High"),   # <= 1 Low, = 2 Medium
    (4, "High"), (5, "Critical"), (6, "Critical"),   # <= 4 High, >= 5 Critical
])
def test_multi_location_cut_lines(n, band):
    assert score_multi_location(n) == band


@pytest.mark.parametrize("wired,band", [
    (2499, "Low"), (2500, "Medium"), (2501, "Medium"),       # a < 0.25 -> Low
    (4999, "Medium"), (5000, "High"), (5001, "High"),        # a < 0.50 -> Medium
    (7999, "High"), (8000, "Critical"), (8001, "Critical"),  # a < 0.80 -> High, otherwise Critical
])
def test_aggregation_ratio_cut_lines(wired, band):
    assert score_aggregation_to_transfer(wired, 10000) == band


def test_aggregation_ratio_is_wired_out_over_structured_in():
    # a = wired_out / structured_in: 9000/10000 = 0.90 Critical; the inverse 10000/9000 would
    # also be Critical, so use 2000 of 10000 (0.20 Low) whose inverse (5.0) is Critical.
    assert score_aggregation_to_transfer(2000, 10000) == "Low"


def test_sub_threshold_ratio_is_sub_over_total():
    # r = 2000/10000 = 0.20 Medium; the inverse (5.0) would be Critical.
    assert score_sub_threshold_clustering(2000, 10000) == "Medium"


@pytest.mark.parametrize("score,band", [
    (0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
    (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical"),
])
def test_score_band_table(score, band):
    # typologies/BA001_Structuring.md Classification: 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    assert band_of(score) == band


@pytest.mark.parametrize("code,score,band", [
    ("CCCC", 90, "Critical"),   # 31.5+22.5+18+18 = 90 (framework worked example)
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
    got_score, got_band, working = ba001_exposure_score(_bands(code))
    assert (got_score, got_band) == (score, band)
    assert len(working["components"]) == 4


def test_half_up_rounding_on_an_exact_half():
    # LMLL: 5.25 + 11.25 + 3 + 3 = 22.5 exactly. Half-up -> 23 (half-even would give 22).
    score, band, working = ba001_exposure_score(_bands("LMLL"))
    assert working["total"] == 22.5
    assert (score, band) == (23, "Low")


def test_alert_threshold_is_inclusive_at_80(engine, monkeypatch):
    """No band combination scores exactly 80 (enumerated: 79 and 81 are the neighbours),
    so the >= 80 filter is checked by fixing the scorer's output at 80 and 79."""
    real = engine.ba001_exposure_score

    def fixed(bands, value):
        _s, _b, working = real(bands)
        return value, band_of(value), working

    accounts = _frames(_account("T80", 10000, 7000, 12, 6, 10000, 9000))
    monkeypatch.setattr(engine, "ba001_exposure_score", lambda b: fixed(b, 80))
    assert list(engine.evaluate_structuring(**accounts)["account_ref"]) == ["T80"]
    monkeypatch.setattr(engine, "ba001_exposure_score", lambda b: fixed(b, 79))
    assert len(engine.evaluate_structuring(**accounts)) == 0


# ---------------------------------------------------------------- check 4: positives / near-misses

def test_worked_example_alerts_90_critical(engine):
    # Framework worked example: $24,000 of $34,000 sub-threshold (r 0.706), 12 deposits in 7 days,
    # 6 locations, $17,200 wired of $19,000 (a 0.905): all Critical -> 90 Critical, alerts.
    out = engine.evaluate_structuring(**_frames(_account("T-WE", 34000, 24000, 12, 6, 19000, 17200)))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["exposure_score"], row["exposure_band"]) == (90, "Critical")
    assert [row[n + "_band"] for n in NAMES] == ["Critical"] * 4
    # the signals the sheet says must be present on a true alert
    assert (row["subthreshold_deposits"], row["total_cash_deposits"]) == (24000, 34000)
    assert (row["deposits_max_7d"], row["distinct_locations"]) == (12, 6)
    assert (row["structured_in_amount"], row["wired_out_amount"]) == (19000, 17200)
    assert row["beneficiary_name"] == "Constructed Beneficiary T-WE"


def test_clean_account_scores_15_and_does_not_alert(engine):
    # Framework: all four components Low -> 15/100, no alert.
    frames = _frames(_account("T-CLEAN", 50000, 1000, 1, 1, 10000, 1000))
    scored = engine.score_all(**frames)
    assert (scored.iloc[0]["exposure_score"], scored.iloc[0]["exposure_band"]) == (15, "Low")
    assert len(engine.evaluate_structuring(**frames)) == 0


def test_one_elevated_component_does_not_alert(engine):
    # Sheet FP: "one with a single elevated component" must not alert. CLLL = 41 Medium.
    frames = _frames(_account("T-ONE", 10000, 9000, 1, 1, 10000, 1000))
    assert len(engine.score_all(**frames)) == 1
    assert len(engine.evaluate_structuring(**frames)) == 0


# One positive and one near-miss per detection rule (component). The positive sits EXACTLY on the
# component's Critical cut-line; the near-miss moves only that component just below it.
PER_RULE = {
    # sub-threshold at r = 0.60 (C) with temporal 7 (H), 3 locations (H), a = 0.90 (C):
    #   31.5+17.5+14+18 = 81 alert;   r = 0.5999 (H): 24.5+17.5+14+18 = 74 no alert
    "sub_threshold_clustering": (_account("P-SUB", 10000, 6000, 7, 3, 10000, 9000),
                                 _account("N-SUB", 10000, 5999, 7, 3, 10000, 9000), 81, 74),
    # temporal at 10 (C) with r 0.70 (C), 3 locations (H), a 0.70 (H):
    #   31.5+22.5+14+14 = 82 alert;   9 (H): 31.5+17.5+14+14 = 77 no alert
    "temporal_clustering": (_account("P-TMP", 10000, 7000, 10, 3, 10000, 7000),
                            _account("N-TMP", 10000, 7000, 9, 3, 10000, 7000), 82, 77),
    # locations at 5 (C) with r 0.70 (C), temporal 7 (H), a 0.70 (H):
    #   31.5+17.5+18+14 = 81 alert;   4 (H): 31.5+17.5+14+14 = 77 no alert
    "multi_location": (_account("P-LOC", 10000, 7000, 7, 5, 10000, 7000),
                       _account("N-LOC", 10000, 7000, 7, 4, 10000, 7000), 81, 77),
    # aggregation at a = 0.80 (C) with r 0.70 (C), temporal 7 (H), 3 locations (H):
    #   31.5+17.5+14+18 = 81 alert;   a = 0.7999 (H): 31.5+17.5+14+14 = 77 no alert
    "aggregation_to_transfer": (_account("P-AGG", 10000, 7000, 7, 3, 10000, 8000),
                                _account("N-AGG", 10000, 7000, 7, 3, 10000, 7999), 81, 77),
}


@pytest.mark.parametrize("rule", sorted(PER_RULE))
def test_positive_and_near_miss_per_rule(engine, rule):
    positive, near, pos_score, near_score = PER_RULE[rule]
    frames = _frames(positive, near)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert scored.loc[positive["account_ref"], rule + "_band"] == "Critical"
    assert scored.loc[near["account_ref"], rule + "_band"] == "High"
    assert (scored.loc[positive["account_ref"], "exposure_score"],
            scored.loc[positive["account_ref"], "exposure_band"]) == (pos_score, "Critical")
    assert scored.loc[near["account_ref"], "exposure_score"] == near_score
    assert scored.loc[near["account_ref"], "exposure_band"] == "High"
    alerts = engine.evaluate_structuring(**frames)
    assert list(alerts["account_ref"]) == [positive["account_ref"]]


def test_alert_row_carries_its_own_working(engine):
    out = engine.evaluate_structuring(**_frames(_account("T-W", 10000, 7000, 10, 3, 10000, 7000)))
    working = json.loads(out.iloc[0]["risk_components"])
    assert set(working["components"]) == set(NAMES)
    assert working["score"] == 82 and working["band"] == "Critical"   # CCHH = 82


def test_score_all_puts_the_highest_score_first(engine):
    # The fc-10 demo path builds its case from score_all's top row (framework line 50-52).
    frames = _frames(_account("T-LOW", 50000, 1000, 1, 1, 10000, 1000),
                     _account("T-HIGH", 34000, 24000, 12, 6, 19000, 17200))
    assert list(engine.score_all(**frames)["account_ref"]) == ["T-HIGH", "T-LOW"]


# ---------------------------------------------------------------- defects

NAN = float("nan")


@pytest.mark.parametrize("scorer,args", [
    (score_sub_threshold_clustering, (NAN, 10000)),
    (score_sub_threshold_clustering, (1000, NAN)),
    (score_aggregation_to_transfer, (NAN, 10000)),
    (score_aggregation_to_transfer, (1000, NAN)),
])
@pytest.mark.xfail(strict=True, reason=(
    "DEFECT: framework BA001 'Both amounts are REQUIRED' (scoring-models/specific/"
    "BA001_Structuring_Scoring_Framework.md:18,30) and the model's own 'missing != zero': "
    "a missing (NaN) amount passes ba001_risk_model.py:50-51 (_require checks None only) and "
    "every '<' comparison at :73-79 / :115-121 is False, so it scores Critical -- measured: "
    "Failed: DID NOT RAISE <class 'ValueError'>"))
def test_a_missing_amount_refuses_rather_than_scoring_critical(scorer, args):
    assert any(isinstance(a, float) and math.isnan(a) for a in args)
    with pytest.raises(ValueError):
        scorer(*args)
