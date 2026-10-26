"""TT-BA002 (night 10, wave C): the BA002 Funnel Accounts engine against its doctrine.

Oracle, and nothing else: scoring-models/specific/BA002_Funnel_Accounts_Scoring_Framework.md
(F: component cut-lines F:20/25/30/34, weights F:8-13, midpoints / weighted sum / half-up F:38,
every input REQUIRED F:18/23/28/33, alert at >= 80 F:50-51) and
typologies/BA002_Funnel_Accounts.md (T: bands 0-29/30-59/60-79/80-100 T:124, the FUN019
worked example T:111-120, threshold "escalate at or above" T:136). No signed-off
expected-outcome sheet exists for BA002 (wave C); oracle rule R1 (2026-10-21) makes the band
table govern over the doctrine's Python snippet (T:161-166). Every expected score below is
hand-worked from those numbers in a comment beside it, or computed in the test from the
framework's formula with exact fractions. Inputs are CONSTRUCTED here: no sample-data file
is read and no sample entity's name is asserted.

Contributions per band (midpoint x weight), from the framework:
    geographic dispersion     30%: L 4.5   M 13.5   H 21    C 27
    inflow fan-in             25%: L 3.75  M 11.25  H 17.5  C 22.5
    rapid passthrough         25%: L 3.75  M 11.25  H 17.5  C 22.5
    beneficiary concentration 20%: L 3     M 9      H 14    C 18
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from ba002_risk_model import (  # noqa: E402
    RiskModelError, band_of, ba002_exposure_score, score_beneficiary_concentration,
    score_geographic_dispersion, score_inflow_fan_in, score_rapid_passthrough,
)

SCENARIO = BASE_DIR / "scenarios" / "funnel_accounts.py"
NAMES = ("geographic_dispersion", "inflow_fan_in", "rapid_passthrough", "beneficiary_concentration")
BAND_COLS = {n: n + "_band" for n in NAMES}
NAN = float("nan")

# F:8-13 and F:38, as exact fractions so the oracle carries no float error of its own.
WEIGHT = {"geographic_dispersion": Fraction(30, 100), "inflow_fan_in": Fraction(25, 100),
          "rapid_passthrough": Fraction(25, 100), "beneficiary_concentration": Fraction(20, 100)}
MIDPOINT = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}


def _load():
    spec = spec_from_file_location("tt_ba002_doctrine_funnel_accounts", SCENARIO)
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


def _account(ref, regions, depositors, dwell, top, total, inflow=None):
    return {"customer_name": "Constructed Holder %s" % ref, "account_ref": ref,
            "segment": "Retail", "home_branch": "Constructed Branch",
            "distinct_source_regions": regions, "distinct_depositors": depositors,
            "total_inflow_amount": total if inflow is None else inflow,
            "max_dwell_hours": dwell, "top_beneficiary_amount": top,
            "total_outflow_amount": total,
            "top_depositor_name": "Constructed Depositor %s" % ref,
            "beneficiary_name": "Constructed Beneficiary %s" % ref}


def _frames(*accounts):
    acc = pd.DataFrame(list(accounts))
    ben = pd.DataFrame([{"beneficiary_name": a["beneficiary_name"], "account_ref": a["account_ref"],
                         "bank": "Constructed Bank", "jurisdiction": "GB",
                         "relationship": "Constructed", "prior_alerts": 0} for a in accounts])
    return {"accounts": acc, "beneficiaries": ben}


# The framework worked example FUN019 (F:40-48, T:111-120), constructed: 9 regions (C),
# 33 depositors (C), 3 h dwell (C), 90,000 of 100,000 outbound (r 0.900, C):
# 27 + 22.5 + 22.5 + 18 = 90 Critical, alerts.
WORKED = _account("T-WE", 9, 33, 3, 90000, 100000, inflow=103000)


# ---------------------------------------------------------------- check 2: boundaries
# Each cut-line from the framework: exactly at it, just below and just above.

@pytest.mark.parametrize("regions,band", [
    (2, "Low"), (3, "Medium"),                        # <= 2 Low
    (4, "Medium"), (5, "High"),                       # <= 4 Medium
    (7, "High"), (8, "Critical"), (9, "Critical"),    # <= 7 High, otherwise (>= 8) Critical
])
def test_geographic_dispersion_cut_lines(regions, band):
    # F:20
    assert score_geographic_dispersion(regions) == band


@pytest.mark.parametrize("depositors,band", [
    (5, "Low"), (6, "Medium"),                          # <= 5 Low
    (15, "Medium"), (16, "High"),                       # <= 15 Medium
    (30, "High"), (31, "Critical"), (32, "Critical"),   # <= 30 High, otherwise (>= 31) Critical
])
def test_inflow_fan_in_cut_lines(depositors, band):
    # F:25
    assert score_inflow_fan_in(depositors) == band


@pytest.mark.parametrize("hours,band", [
    (72.01, "Low"), (72, "Low"), (71.99, "Medium"),     # >= 72 Low
    (24.01, "Medium"), (24, "Medium"), (23.99, "High"),  # >= 24 Medium
    (6.01, "High"), (6, "High"), (5.99, "Critical"),     # >= 6 High, otherwise (< 6) Critical
])
def test_rapid_passthrough_cut_lines(hours, band):
    # F:30 -- shorter dwell is worse
    assert score_rapid_passthrough(hours) == band


@pytest.mark.parametrize("top,band", [
    (2499, "Low"), (2500, "Medium"), (2501, "Medium"),        # r < 0.25 Low
    (4999, "Medium"), (5000, "High"), (5001, "High"),         # r < 0.50 Medium
    (7999, "High"), (8000, "Critical"), (8001, "Critical"),   # r < 0.80 High, otherwise Critical
])
def test_beneficiary_concentration_cut_lines(top, band):
    # F:34, r = top / total over a 10,000 outflow
    assert score_beneficiary_concentration(top, 10000) == band


def test_beneficiary_concentration_is_top_over_total():
    # F:33 r = top_beneficiary_amount / total_outflow_amount. 2,000 of 10,000 is r 0.20 Low;
    # the inverse (5.0) would be Critical.
    assert score_beneficiary_concentration(2000, 10000) == "Low"


@pytest.mark.parametrize("score,band", [
    (0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
    (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical"),
])
def test_score_band_table(score, band):
    # T:124 Classification: 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    assert band_of(score) == band


def _framework_score(bands):
    """F:38 by construction: band midpoint x weight, summed exactly, half-up, then T:124."""
    exact = sum(MIDPOINT[bands[n]] * WEIGHT[n] for n in NAMES)
    score = int(exact + Fraction(1, 2))          # half-up (every total here is positive)
    band = "Low" if score <= 29 else "Medium" if score <= 59 else "High" if score <= 79 else "Critical"
    return exact, score, band


ALL_CODES = ["".join(c) for c in itertools.product("LMHC", repeat=4)]


@pytest.mark.parametrize("code", ALL_CODES)
def test_every_band_combination_scores_the_framework_sum(code):
    """All 256 band combinations against the framework's formula in exact arithmetic,
    so a float sum that lands a hair under an x.5 cannot round the wrong way unnoticed."""
    bands = _bands(code)
    exact, score, band = _framework_score(bands)
    got_score, got_band, working = ba002_exposure_score(bands)
    assert (got_score, got_band) == (score, band)
    assert {n: working["components"][n]["band"] for n in NAMES} == bands
    assert working["total"] == pytest.approx(float(exact), abs=1e-9)


@pytest.mark.parametrize("code,score,band", [
    ("CCCC", 90, "Critical"),   # 27+22.5+22.5+18 = 90 (worked example FUN019, F:48)
    ("LLLL", 15, "Low"),        # 4.5+3.75+3.75+3 = 15 (F:50 clean account 15/100)
    ("CHHC", 80, "Critical"),   # 27+17.5+17.5+18 = 80 exactly: the threshold itself
    ("HHCC", 79, "High"),       # 21+17.5+22.5+18 = 79
    ("CCCM", 81, "Critical"),   # 27+22.5+22.5+9 = 81
    ("CCCL", 75, "High"),       # 27+22.5+22.5+3 = 75
    ("CCLC", 71, "High"),       # 27+22.5+3.75+18 = 71.25 -> 71
    ("LLML", 23, "Low"),        # 4.5+3.75+11.25+3 = 22.5 exactly -> half-up 23 (half-even: 22)
    ("CHMM", 65, "High"),       # 27+17.5+11.25+9 = 64.75 -> 65
])
def test_hand_worked_scores(code, score, band):
    got_score, got_band, _w = ba002_exposure_score(_bands(code))
    assert (got_score, got_band) == (score, band)


def test_half_up_rounding_on_an_exact_half():
    # LLML: 4.5 + 3.75 + 11.25 + 3 = 22.5 exactly. Half-up -> 23 (half-even would give 22).
    score, band, working = ba002_exposure_score(_bands("LLML"))
    assert working["total"] == 22.5
    assert (score, band) == (23, "Low")


def test_the_doctrine_snippet_is_implied_by_the_band_table():
    """T:161-166's snippet gates on geo High/Critical, >= 16 depositors and <= 24 h dwell. R1:
    the band table governs; this checks the two do not disagree -- every combination the
    framework puts at or above 80 has geo >= High, fan-in >= High (>= 16) and dwell >= High
    (< 24 h). Non-vacuity: ten combinations alert."""
    alerting = [c for c in ALL_CODES if _framework_score(_bands(c))[1] >= 80]
    assert len(alerting) == 10
    for code in alerting:
        assert code[0] in "HC" and code[1] in "HC" and code[2] in "HC", code
        assert ba002_exposure_score(_bands(code))[0] >= 80


def test_alert_threshold_is_inclusive_at_80(engine):
    """F:50-51 / T:136 'at or above'. CHHC scores exactly 80 and alerts; HHCC scores 79 and
    does not -- both in the SAME evaluate call."""
    # 8 regions C, 16 depositors H, 12 h H, 9,000/10,000 r 0.90 C: 27+17.5+17.5+18 = 80
    at = _account("T-80", 8, 16, 12, 9000, 10000)
    # 5 regions H, 16 depositors H, 3 h C, r 0.90 C: 21+17.5+22.5+18 = 79
    below = _account("T-79", 5, 16, 3, 9000, 10000)
    frames = _frames(at, below)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert (scored.loc["T-80", "exposure_score"], scored.loc["T-80", "exposure_band"]) == (80, "Critical")
    assert (scored.loc["T-79", "exposure_score"], scored.loc["T-79", "exposure_band"]) == (79, "High")
    assert list(engine.evaluate_funnel_accounts(**frames)["account_ref"]) == ["T-80"]


# ---------------------------------------------------------------- check 4: positives / near-misses

def test_worked_example_alerts_90_critical(engine):
    out = engine.evaluate_funnel_accounts(**_frames(WORKED))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["exposure_score"], row["exposure_band"]) == (90, "Critical")
    assert [row[BAND_COLS[n]] for n in NAMES] == ["Critical"] * 4
    # the evidence T:174-182 says the investigator sees
    assert (row["distinct_source_regions"], row["distinct_depositors"], row["max_dwell_hours"]) == (9, 33, 3)
    assert (row["top_beneficiary_amount"], row["total_outflow_amount"], row["total_inflow_amount"]) == \
        (90000, 100000, 103000)
    assert row["beneficiary_name"] == "Constructed Beneficiary T-WE"
    assert row["subject_entity_id"] == "T-WE" and row["subject_name"] == "Constructed Holder T-WE"
    assert row["alert_type"] == "BA002_FUNNEL_ACCOUNTS"


def test_clean_account_scores_15_and_does_not_alert(engine):
    # F:50: all four Low scores 15/100. 1 region L, 3 depositors L, 90 h L, 1,500/10,000 r 0.15 L.
    # Alerting control in the SAME frame: the worked example, 90 Critical.
    frames = _frames(_account("T-CLEAN", 1, 3, 90, 1500, 10000), WORKED)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert (scored.loc["T-CLEAN", "exposure_score"], scored.loc["T-CLEAN", "exposure_band"]) == (15, "Low")
    assert list(engine.evaluate_funnel_accounts(**frames)["account_ref"]) == ["T-WE"]


def test_a_dispersed_collection_that_accumulates_does_not_alert(engine):
    """T:40 'no accumulation' is the passthrough signal: a dispersed, many-depositor account
    that HOLDS its funds (96 h, L) is not a funnel. 9 C, 33 C, 96 h L, r 0.90 C:
    27+22.5+3.75+18 = 71.25 -> 71 High, no alert. Control: the worked example."""
    frames = _frames(_account("T-HOLD", 9, 33, 96, 90000, 100000), WORKED)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert (scored.loc["T-HOLD", "exposure_score"], scored.loc["T-HOLD", "exposure_band"]) == (71, "High")
    assert list(engine.evaluate_funnel_accounts(**frames)["account_ref"]) == ["T-WE"]


# One positive and one near-miss per detection rule (component). The positive sits EXACTLY on
# the component's cut-line (passthrough: just inside it, < 6); the near-miss moves only that
# component just outside it.
PER_RULE = {
    # 8 regions (C) with 16 H, 3 h C, r 0.70 H: 27+17.5+22.5+14 = 81 alert;
    #   7 regions (H): 21+17.5+22.5+14 = 75 no alert
    "geographic_dispersion": (_account("P-GD", 8, 16, 3, 7000, 10000),
                              _account("N-GD", 7, 16, 3, 7000, 10000), 81, 75, "Critical", "High"),
    # 31 depositors (C) with 5 regions H, 3 h C, r 0.90 C: 21+22.5+22.5+18 = 84 alert;
    #   30 depositors (H): 21+17.5+22.5+18 = 79 no alert
    "inflow_fan_in": (_account("P-FI", 5, 31, 3, 9000, 10000),
                      _account("N-FI", 5, 30, 3, 9000, 10000), 84, 79, "Critical", "High"),
    # 5.99 h (C) with 5 regions H, 31 C, r 0.90 C: 21+22.5+22.5+18 = 84 alert;
    #   6 h (H): 21+22.5+17.5+18 = 79 no alert
    "rapid_passthrough": (_account("P-RP", 5, 31, 5.99, 9000, 10000),
                          _account("N-RP", 5, 31, 6, 9000, 10000), 84, 79, "Critical", "High"),
    # r 0.80 (C) with 8 C, 16 H, 12 h H: 27+17.5+17.5+18 = 80 alert;
    #   r 0.7999 (H): 27+17.5+17.5+14 = 76 no alert
    "beneficiary_concentration": (_account("P-BC", 8, 16, 12, 8000, 10000),
                                  _account("N-BC", 8, 16, 12, 7999, 10000), 80, 76, "Critical", "High"),
    # the Medium line: r 0.25 (M) with 8 C, 31 C, 3 h C: 27+22.5+22.5+9 = 81 alert;
    #   r 0.2499 (L): 27+22.5+22.5+3 = 75 no alert
    "beneficiary_concentration_medium": (_account("P-BM", 8, 31, 3, 2500, 10000),
                                         _account("N-BM", 8, 31, 3, 2499, 10000), 81, 75, "Medium", "Low"),
}


@pytest.mark.parametrize("rule", sorted(PER_RULE))
def test_positive_and_near_miss_per_rule(engine, rule):
    positive, near, pos_score, near_score, pos_band, near_band = PER_RULE[rule]
    col = BAND_COLS[rule.replace("_medium", "")]
    frames = _frames(positive, near)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert scored.loc[positive["account_ref"], col] == pos_band
    assert scored.loc[near["account_ref"], col] == near_band
    assert (scored.loc[positive["account_ref"], "exposure_score"],
            scored.loc[positive["account_ref"], "exposure_band"]) == (pos_score, "Critical")
    assert (scored.loc[near["account_ref"], "exposure_score"],
            scored.loc[near["account_ref"], "exposure_band"]) == (near_score, "High")
    alerts = engine.evaluate_funnel_accounts(**frames)
    assert list(alerts["account_ref"]) == [positive["account_ref"]]


def test_each_input_feeds_its_own_component(engine):
    """Distinct values per input, so swapping two inputs between components cannot pass:
    4 regions M, 20 depositors H, 30 h M, r 0.10 L -> 13.5+17.5+11.25+3 = 45.25 -> 45 Medium."""
    out = engine.score_all(**_frames(_account("T-MIX", 4, 20, 30, 1000, 10000)))
    row = out.iloc[0]
    assert [row[BAND_COLS[n]] for n in NAMES] == ["Medium", "High", "Medium", "Low"]
    assert (row["exposure_score"], row["exposure_band"]) == (45, "Medium")


def test_alert_row_carries_its_own_working(engine):
    # CHHC: 27+17.5+17.5+18 = 80 Critical
    out = engine.evaluate_funnel_accounts(**_frames(_account("T-W", 8, 16, 12, 9000, 10000)))
    working = json.loads(out.iloc[0]["risk_components"])
    assert set(working["components"]) == set(NAMES)
    assert working["score"] == 80 and working["band"] == "Critical"
    assert {n: working["components"][n]["weight"] for n in NAMES} == {n: float(WEIGHT[n]) for n in NAMES}


def test_score_all_puts_the_highest_score_first(engine):
    # F:53-55: the fc-10 demo path builds its case from score_all's top row.
    frames = _frames(_account("T-LOW", 1, 3, 90, 1500, 10000), WORKED)
    assert list(engine.score_all(**frames)["account_ref"]) == ["T-WE", "T-LOW"]


# ---------------------------------------------------------------- required inputs (F:18/23/28/33)

REQUIRED = ("distinct_source_regions", "distinct_depositors", "max_dwell_hours",
            "top_beneficiary_amount", "total_outflow_amount")


@pytest.mark.parametrize("field", REQUIRED)
def test_a_blank_required_input_is_refused_not_scored_as_zero(engine, field):
    """The sample reader yields '' for a blank cell (dtype=str, keep_default_na=False). A blank
    must refuse, never read as zero regions / zero depositors / zero hours (zero hours would
    score Critical). The worked example scores first, so the refusal is the blank's doing."""
    account = dict(WORKED)
    assert len(engine.evaluate_funnel_accounts(**_frames(account))) == 1
    account[field] = ""
    with pytest.raises(ValueError):
        engine.evaluate_funnel_accounts(**_frames(account))


@pytest.mark.parametrize("scorer", [score_geographic_dispersion, score_inflow_fan_in])
def test_a_missing_count_refuses(scorer):
    # F:18/23 REQUIRED. NaN is refused (int(float(nan)) raises ValueError).
    with pytest.raises(ValueError):
        scorer(NAN)


@pytest.mark.parametrize("field", ["max_dwell_hours", "top_beneficiary_amount", "total_outflow_amount"])
def test_the_callable_refuses_an_account_with_a_missing_amount(engine, field):
    """End to end, a NaN dwell or amount is refused -- but only by the DISPLAY cast at
    scenarios/funnel_accounts.py:86-88 (int(float(nan)) raises), not by the model, which
    scores it Critical (KNOWN D043 below). 5 regions H, 16 H, 96 h L, r 0.10 L:
    21+17.5+3.75+3 = 45.25 -> 45, no alert, with every input present."""
    account = _account("T-NAN", 5, 16, 96, 1000, 10000)
    assert engine.score_all(**_frames(account)).iloc[0]["exposure_score"] == 45
    account[field] = NAN
    with pytest.raises(ValueError):
        engine.evaluate_funnel_accounts(**_frames(account))


# ---------------------------------------------------------------- known items

@pytest.mark.parametrize("scorer,args", [
    (score_rapid_passthrough, (NAN,)),
    (score_beneficiary_concentration, (NAN, 10000)),
    (score_beneficiary_concentration, (9000, NAN)),
])
@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: framework BA002 'max_dwell_hours is REQUIRED' / 'Both amounts are "
    "REQUIRED' (BA002_Funnel_Accounts_Scoring_Framework.md:28,33) and the model's own 'missing "
    "!= zero': a NaN passes ba002_risk_model.py:55-60 (_require checks None only), every "
    "comparison at :100-106 / :115-124 is False, so the component scores Critical -- measured: "
    "Failed: DID NOT RAISE <class 'ValueError'>. End to end it is refused only by the display "
    "cast at scenarios/funnel_accounts.py:86-88"))
def test_a_missing_value_refuses_rather_than_scoring_critical(scorer, args):
    assert any(isinstance(a, float) and math.isnan(a) for a in args)
    with pytest.raises(ValueError):
        scorer(*args)


# ---------------------------------------------------------------- defects

@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "DEFECT: framework BA002 'r < 0.80 -> High, otherwise -> Critical' "
    "(BA002_Funnel_Accounts_Scoring_Framework.md:34): 80,000.04 of 100,000.05 is r = 0.80 "
    "exactly, but ba002_risk_model.py:117-121 compares the float quotient (0.7999999999999999) "
    "-- measured: AssertionError, 'High' == 'Critical'"))
def test_an_exact_080_ratio_with_cents_is_critical():
    assert Fraction("80000.04") / Fraction("100000.05") == Fraction(4, 5)
    assert score_beneficiary_concentration(80000.04, 100000.05) == "Critical"


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "DEFECT: same cut-line, end to end: an account at r = 0.80 exactly (80,000.04 of 100,000.05) "
    "with 8 regions C, 16 depositors H, 12 h H must score 27+17.5+17.5+18 = 80 and ALERT; "
    "ba002_risk_model.py:117-121 bands it High, so it scores 76 and evaluate_funnel_accounts "
    "(scenarios/funnel_accounts.py:112) drops it -- measured: AssertionError, alert set "
    "['P-WHOLE'] (the whole-dollar control) instead of ['P-WHOLE', 'P-CENTS']"))
def test_an_exact_080_ratio_with_cents_alerts(engine):
    whole = _account("P-WHOLE", 8, 16, 12, 80000, 100000)       # r 0.80 exactly, whole dollars
    cents = _account("P-CENTS", 8, 16, 12, 80000.04, 100000.05)  # r 0.80 exactly, with cents
    frames = _frames(whole, cents)
    assert len(engine.score_all(**frames)) == 2
    assert list(engine.evaluate_funnel_accounts(**frames)["account_ref"]) == ["P-WHOLE", "P-CENTS"]
