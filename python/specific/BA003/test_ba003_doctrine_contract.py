"""TT-BA003 (night 10, wave C): the BA003 Mule Accounts engine against its doctrine.

Oracle, and nothing else (no signed-off expected-outcome sheet exists for BA003):
scoring-models/specific/BA003_Mule_Accounts_Scoring_Framework.md (F: component cut-lines
F:17-34, weights F:8-13, midpoints / weighted sum / half-up / boundary at 80 F:38, every
input REQUIRED, inflow and income > 0, the MUL019 worked example F:40-48, the all-Low 15
F:50, alert >= 80 F:50-51), typologies/BA003_Mule_Accounts.md (T: weights T:104-111, bands
T:127-128, the worked example T:115-125) and owner oracle rule R1 (2026-10-21: where the
typology's Python snippet T:164-171 disagrees with the band table, the band table governs).
Every expected score below is hand-worked from those numbers in a comment beside it. Inputs
are CONSTRUCTED here: no sample-data file is read and no sample entity's name is asserted.

Contributions per band (midpoint x weight), from F:
    pass-through ratio    30%: L 4.5   M 13.5   H 21    C 27
    account youth         25%: L 3.75  M 11.25  H 17.5  C 22.5
    behavioural mismatch  25%: L 3.75  M 11.25  H 17.5  C 22.5
    network linkage       20%: L 3     M 9      H 14    C 18
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

from ba003_risk_model import (  # noqa: E402
    RiskModelError, band_of, ba003_exposure_score, score_account_youth,
    score_behavioural_mismatch, score_network_linkage, score_pass_through_ratio,
)

SCENARIO = BASE_DIR / "scenarios" / "mule_accounts.py"
NAMES = ("pass_through_ratio", "account_youth", "behavioural_mismatch", "network_linkage")
BAND_COLS = {n: n + "_band" for n in NAMES}


def _load():
    spec = spec_from_file_location("tt_ba003_doctrine_mule_accounts", SCENARIO)
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


def _account(ref, inflow, outflow, age, income, throughput, links):
    return {"customer_name": "Constructed Holder %s" % ref, "account_ref": ref,
            "segment": "Retail", "home_branch": "Constructed Branch",
            "total_inflow_amount": inflow, "total_outflow_amount": outflow,
            "account_age_days": age, "declared_monthly_income": income,
            "monthly_throughput_amount": throughput, "shared_link_count": links,
            "top_originator_name": "Constructed Originator %s" % ref,
            "controller_name": "Constructed Controller %s" % ref,
            "beneficiary_name": "Constructed Destination %s" % ref}


def _frames(*accounts):
    acc = pd.DataFrame(list(accounts))
    bens = pd.DataFrame([{"beneficiary_name": a["beneficiary_name"], "account_ref": a["account_ref"],
                          "bank": "Constructed Bank", "jurisdiction": "GB",
                          "relationship": "Unverified payee", "prior_alerts": 0} for a in accounts])
    return {"accounts": acc, "beneficiaries": bens}


# The framework's worked example (F:40-48): $96,000 of $100,000 forwarded (r 0.960, C), 12 days
# old (C), $92,000 throughput vs $3,200 income (r 28.75, C), 6 links (C): 27+22.5+22.5+18 = 90.
WORKED = ("T-WE", 100000, 96000, 12, 3200, 92000, 6)
# All-Low background (F:50 'a clean account with all four components Low scores 15'):
# r 0.30 (L), 800 days (L), r 1.5 (L), 0 links (L): 4.5+3.75+3.75+3 = 15.
CLEAN = ("T-BG", 40000, 12000, 800, 4000, 6000, 0)


# ---------------------------------------------------------------- check 2: boundaries
# Each cut-line from F:17-34: exactly at it, just below, just above.

@pytest.mark.parametrize("outflow,band", [
    (4999, "Low"), (5000, "Medium"), (5001, "Medium"),        # r < 0.50 -> Low
    (7499, "Medium"), (7500, "High"), (7501, "High"),         # r < 0.75 -> Medium
    (9199, "High"), (9200, "Critical"), (9201, "Critical"),   # r < 0.92 -> High, otherwise Critical
])
def test_pass_through_cut_lines(outflow, band):
    assert score_pass_through_ratio(outflow, 10000) == band


def test_pass_through_is_outflow_over_inflow():
    # F:18 r = total_outflow_amount / total_inflow_amount. 3000 out of 10000 in = 0.30 Low;
    # the inverse (3.33) would be Critical.
    assert score_pass_through_ratio(3000, 10000) == "Low"


@pytest.mark.parametrize("inflow", [0, -1, -10000])
def test_pass_through_refuses_inflow_not_above_zero(inflow):
    # F:19 "total_inflow_amount must be > 0".
    with pytest.raises(RiskModelError):
        score_pass_through_ratio(5000, inflow)


@pytest.mark.parametrize("age,band", [
    (366, "Low"), (365, "Low"), (364, "Medium"),     # >= 365 Low
    (181, "Medium"), (180, "Medium"), (179, "High"),  # >= 180 Medium
    (61, "High"), (60, "High"), (59, "Critical"),     # >= 60 High, otherwise (< 60) Critical
    (0, "Critical"),
])
def test_account_youth_cut_lines(age, band):
    assert score_account_youth(age) == band


@pytest.mark.parametrize("throughput,band", [
    (2999, "Low"), (3000, "Medium"), (3001, "Medium"),        # r < 3 -> Low
    (7999, "Medium"), (8000, "High"), (8001, "High"),         # r < 8 -> Medium
    (19999, "High"), (20000, "Critical"), (20001, "Critical"),  # r < 20 -> High, otherwise Critical
])
def test_behavioural_mismatch_cut_lines(throughput, band):
    assert score_behavioural_mismatch(throughput, 1000) == band


def test_behavioural_mismatch_is_throughput_over_income():
    # F:27 r = monthly_throughput_amount / declared_monthly_income. 1000 vs 25000 = 0.04 Low;
    # the inverse (25) would be Critical.
    assert score_behavioural_mismatch(1000, 25000) == "Low"


@pytest.mark.parametrize("income", [0, -1, -3200])
def test_behavioural_mismatch_refuses_income_not_above_zero(income):
    # F:28 "declared_monthly_income must be > 0".
    with pytest.raises(RiskModelError):
        score_behavioural_mismatch(9000, income)


@pytest.mark.parametrize("links,band", [
    (0, "Low"), (1, "Medium"), (2, "High"), (3, "High"), (4, "Critical"), (6, "Critical"),
])  # F:34 <= 0 Low, <= 1 Medium, <= 3 High, otherwise (>= 4) Critical
def test_network_linkage_cut_lines(links, band):
    assert score_network_linkage(links) == band


@pytest.mark.parametrize("score,band", [
    (0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
    (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical"),
])
def test_score_band_table(score, band):
    # T:127-128 Classification: 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    assert band_of(score) == band


@pytest.mark.parametrize("code,score,band", [
    ("CCCC", 90, "Critical"),   # 27+22.5+22.5+18 = 90 (worked example, F:48)
    ("LLLL", 15, "Low"),        # 4.5+3.75+3.75+3 = 15 (F:50)
    ("CHHC", 80, "Critical"),   # 27+17.5+17.5+18 = 80 exactly: the alert boundary
    ("HCCH", 80, "Critical"),   # 21+22.5+22.5+14 = 80 exactly
    ("HHCC", 79, "High"),       # 21+17.5+22.5+18 = 79
    ("CCCH", 86, "Critical"),   # 27+22.5+22.5+14 = 86
    ("CHCC", 85, "Critical"),   # 27+17.5+22.5+18 = 85
    ("HCCC", 84, "Critical"),   # 21+22.5+22.5+18 = 84
    ("CHHH", 76, "High"),       # 27+17.5+17.5+14 = 76
    ("CLLL", 38, "Medium"),     # 27+3.75+3.75+3 = 37.5 -> 38 (half-up)
    ("MMMM", 45, "Medium"),     # every component at the Medium midpoint
    ("HHHH", 70, "High"),       # every component at the High midpoint
])
def test_weighted_midpoint_score(code, score, band):
    got_score, got_band, working = ba003_exposure_score(_bands(code))
    assert (got_score, got_band) == (score, band)
    assert {k: v["weight"] for k, v in working["components"].items()} == {
        "pass_through_ratio": 0.30, "account_youth": 0.25,
        "behavioural_mismatch": 0.25, "network_linkage": 0.20}   # F:8-13


def test_half_up_rounding_on_an_exact_half():
    # LMLL: 4.5 + 11.25 + 3.75 + 3 = 22.5 exactly. Half-up -> 23 (half-even would give 22).
    score, band, working = ba003_exposure_score(_bands("LMLL"))
    assert working["total"] == 22.5
    assert (score, band) == (23, "Low")


def test_alert_threshold_is_inclusive_at_80(engine):
    # F:50-51 alert at >= 80. CHHC scores exactly 80 (pass r 0.92 C, 120 days H, r 10 H, 4 links C);
    # HHCC scores 79 (r 0.80 H, 120 days H, r 25 C, 4 links C). Same evaluate call.
    frames = _frames(_account("T-80", 10000, 9200, 120, 1000, 10000, 4),
                     _account("T-79", 10000, 8000, 120, 1000, 25000, 4))
    scored = engine.score_all(**frames).set_index("account_ref")
    assert scored.loc["T-80", "exposure_score"] == 80
    assert scored.loc["T-79", "exposure_score"] == 79
    assert list(engine.evaluate_mule_accounts(**frames)["account_ref"]) == ["T-80"]


# ---------------------------------------------------------------- check 4: positives / near-misses

def test_worked_example_alerts_90_critical(engine):
    out = engine.evaluate_mule_accounts(**_frames(_account(*WORKED)))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["exposure_score"], row["exposure_band"]) == (90, "Critical")
    assert [row[BAND_COLS[n]] for n in NAMES] == ["Critical"] * 4
    assert (row["total_inflow_amount"], row["total_outflow_amount"]) == (100000, 96000)
    assert (row["declared_monthly_income"], row["monthly_throughput_amount"]) == (3200, 92000)
    assert (row["account_age_days"], row["shared_link_count"]) == (12, 6)
    assert row["controller_name"] == "Constructed Controller T-WE"
    assert row["subject_entity_id"] == "T-WE"


def test_background_clean_account_scores_15_and_does_not_alert(engine):
    frames = _frames(_account(*CLEAN), _account(*WORKED))
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert (scored.loc["T-BG", "exposure_score"], scored.loc["T-BG", "exposure_band"]) == (15, "Low")
    assert list(engine.evaluate_mule_accounts(**frames)["account_ref"]) == ["T-WE"]


# One positive and one near-miss per detection rule (component). The positive sits EXACTLY on the
# component's Critical cut-line (youth: just inside it, < 60); the near-miss moves only that
# component just outside it.
PER_RULE = {
    # r = 0.92 (C), 120 days (H), r 10 (H), 4 links (C): 27+17.5+17.5+18 = 80 alert;
    # r = 0.9199 (H): 21+17.5+17.5+18 = 74 no alert
    "pass_through_ratio": (_account("P-PT", 10000, 9200, 120, 1000, 10000, 4),
                           _account("N-PT", 10000, 9199, 120, 1000, 10000, 4), 80, 74),
    # 59 days (C) with r 0.95 (C), r 10 (H), 2 links (H): 27+22.5+17.5+14 = 81 alert;
    # 60 days (H): 27+17.5+17.5+14 = 76 no alert
    "account_youth": (_account("P-AY", 10000, 9500, 59, 1000, 10000, 2),
                      _account("N-AY", 10000, 9500, 60, 1000, 10000, 2), 81, 76),
    # r = 20 (C) with r 0.95 (C), 120 days (H), 2 links (H): 27+17.5+22.5+14 = 81 alert;
    # r = 19.999 (H): 27+17.5+17.5+14 = 76 no alert
    "behavioural_mismatch": (_account("P-BM", 10000, 9500, 120, 1000, 20000, 2),
                             _account("N-BM", 10000, 9500, 120, 1000, 19999, 2), 81, 76),
    # 4 links (C) with r 0.95 (C), 120 days (H), r 10 (H): 27+17.5+17.5+18 = 80 alert;
    # 3 links (H): 27+17.5+17.5+14 = 76 no alert
    "network_linkage": (_account("P-NL", 10000, 9500, 120, 1000, 10000, 4),
                        _account("N-NL", 10000, 9500, 120, 1000, 10000, 3), 80, 76),
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
    assert (scored.loc[near["account_ref"], "exposure_score"],
            scored.loc[near["account_ref"], "exposure_band"]) == (near_score, "High")
    alerts = engine.evaluate_mule_accounts(**frames)
    assert list(alerts["account_ref"]) == [positive["account_ref"]]


def test_the_typology_snippet_prefilter_does_not_govern(engine):
    """Owner rule R1 (2026-10-21): T:164-171's snippet pre-filters on pass-through High/Critical,
    age <= 90 and links >= 2; the framework alerts on the score alone (F:50-51), and the band
    table governs. Both accounts below fail the snippet and must still alert:
      T-OLD  r 0.95 (C), 120 days (H, but > 90), r 10 (H), 4 links (C): 27+17.5+17.5+18 = 80
      T-ONE  r 0.95 (C), 30 days (C), r 25 (C), 1 link (M, but < 2):  27+22.5+22.5+9 = 81
    The clean background is the non-alerting control in the same call."""
    frames = _frames(_account("T-OLD", 10000, 9500, 120, 1000, 10000, 4),
                     _account("T-ONE", 10000, 9500, 30, 1000, 25000, 1),
                     _account(*CLEAN))
    scored = engine.score_all(**frames).set_index("account_ref")
    assert (scored.loc["T-OLD", "exposure_score"], scored.loc["T-ONE", "exposure_score"]) == (80, 81)
    assert sorted(engine.evaluate_mule_accounts(**frames)["account_ref"]) == ["T-OLD", "T-ONE"]


def test_alert_row_carries_its_own_working(engine):
    # CCCH: r 0.95 C, 30 days C, r 25 C, 2 links H = 27+22.5+22.5+14 = 86 Critical
    out = engine.evaluate_mule_accounts(**_frames(_account("T-W", 10000, 9500, 30, 1000, 25000, 2)))
    working = json.loads(out.iloc[0]["risk_components"])
    assert set(working["components"]) == set(NAMES)
    assert working["score"] == 86 and working["band"] == "Critical"
    assert "pass-through" in out.iloc[0]["risk_reason"]   # dominant driver: pass-through (27)


def test_score_all_puts_the_highest_score_first(engine):
    # The fc-10 demo path builds its case from score_all's top row (F:53-55).
    frames = _frames(_account(*CLEAN), _account(*WORKED))
    assert list(engine.score_all(**frames)["account_ref"]) == ["T-WE", "T-BG"]


# ---------------------------------------------------------------- required inputs

NAN = float("nan")


@pytest.mark.parametrize("field", ["total_inflow_amount", "total_outflow_amount",
                                   "account_age_days", "declared_monthly_income",
                                   "monthly_throughput_amount", "shared_link_count"])
@pytest.mark.parametrize("missing", ["", NAN])
def test_the_callable_refuses_an_account_with_a_missing_input(engine, field, missing):
    """F:18,23,27,32: every input is REQUIRED. The worked example scores 90 with every input
    present; with `field` blank or NaN the callable must refuse rather than score. (For NaN the
    refusal is incidental -- the int() casts at mule_accounts.py:84-89 and ba003_risk_model.py
    :92,:123 -- see the D043 witness below for the model functions on their own.)"""
    account = _account(*WORKED)
    assert len(engine.evaluate_mule_accounts(**_frames(account))) == 1
    account[field] = missing
    with pytest.raises(ValueError):
        engine.evaluate_mule_accounts(**_frames(account))


# ---------------------------------------------------------------- known items (cited)

@pytest.mark.parametrize("scorer,args", [
    (score_pass_through_ratio, (NAN, 10000)),
    (score_pass_through_ratio, (9000, NAN)),
    (score_behavioural_mismatch, (NAN, 1000)),
    (score_behavioural_mismatch, (9000, NAN)),
])
@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: F:18,27 'Both amounts are REQUIRED'; ba003_risk_model.py:56-61 _require "
    "checks None only, so a NaN amount makes every comparison at :79-85 / :111-117 False and the "
    "component scores Critical -- measured: Failed: DID NOT RAISE <class 'ValueError'>. In BA003 "
    "the callable still refuses NaN by accident at the int() casts (mule_accounts.py:84-89), so "
    "NaN does not flip an alert end to end"))
def test_a_missing_amount_refuses_rather_than_scoring_critical(scorer, args):
    assert any(isinstance(a, float) and math.isnan(a) for a in args)
    with pytest.raises(ValueError):
        scorer(*args)


# ---------------------------------------------------------------- defects

@pytest.mark.parametrize("outflow,inflow,band", [
    ("920.92", "1001", "Critical"),       # 920.92 / 1001 = 0.92 exactly
    ("750.06", "1000.08", "High"),        # 750.06 / 1000.08 = 0.75 exactly
])
@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "DEFECT: F:20 'r < 0.75 -> Medium · r < 0.92 -> High · otherwise -> Critical': a ratio EXACTLY "
    "at the cut-line belongs to the upper band, but ba003_risk_model.py:78 computes r in binary "
    "float, so 920.92/1001 (= 0.92) gives 0.9199999999999999 -> High and 750.06/1000.08 (= 0.75) "
    "gives 0.7499999999999999 -> Medium -- measured: AssertionError 'High' == 'Critical' / "
    "'Medium' == 'High'"))
def test_pass_through_exactly_at_a_decimal_cut_line(outflow, inflow, band):
    assert score_pass_through_ratio(outflow, inflow) == band


@pytest.mark.parametrize("throughput,income,band", [
    ("3000.24", "1000.08", "Medium"),     # = 3 exactly
    ("20001.60", "1000.08", "Critical"),  # = 20 exactly
])
@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "DEFECT: F:29 'r < 3 -> Low · r < 8 -> Medium · r < 20 -> High · otherwise -> Critical': a "
    "ratio EXACTLY at the cut-line belongs to the upper band, but ba003_risk_model.py:110 computes "
    "r in binary float, so 3000.24/1000.08 (= 3) gives 2.9999999999999996 -> Low and "
    "20001.60/1000.08 (= 20) gives 19.999999999999996 -> High -- measured: AssertionError "
    "'Low' == 'Medium' / 'High' == 'Critical'"))
def test_behavioural_mismatch_exactly_at_a_decimal_cut_line(throughput, income, band):
    assert score_behavioural_mismatch(throughput, income) == band


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "DEFECT: same float cut-line, end to end: a constructed account forwarding 920.92 of 1001 "
    "(r = 0.92, F:20 Critical) with 120 days (H), r 10 (H) and 4 links (C) scores CHHC = 80 and "
    "must alert (F:50-51); scenarios/mule_accounts.py:68 -> ba003_risk_model.py:78 bands it High, "
    "HHHC = 74, and evaluate_mule_accounts drops it -- measured: AssertionError, alerts "
    "['T-INT'] != ['T-CENT', 'T-INT']"))
def test_a_cent_amount_at_the_cut_line_still_alerts(engine):
    # Alerting control in the SAME call: the whole-dollar twin (9200 of 10000), also CHHC = 80.
    frames = _frames(_account("T-CENT", "1001", "920.92", "120", "1000", "10000", "4"),
                     _account("T-INT", "10000", "9200", "120", "1000", "10000", "4"))
    assert len(engine.score_all(**frames)) == 2
    assert sorted(engine.evaluate_mule_accounts(**frames)["account_ref"]) == ["T-CENT", "T-INT"]
