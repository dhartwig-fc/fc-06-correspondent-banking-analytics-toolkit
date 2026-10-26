"""TT-BA006 (night 10, wave C): the BA006 Dormant Reactivation engine against its doctrine.

Oracle, and nothing else (no signed-off expected-outcome sheet exists for BA006):
scoring-models/specific/BA006_Dormant_Reactivation_Scoring_Framework.md (F: weights F:8-13,
component cut-lines F:17-35, midpoints / weighted sum / half-up / boundary at 80 F:39, every
input REQUIRED, baseline and reactivation amount > 0, the DR019 worked example F:41-49, the
all-Low 15 F:51, alert >= 80 F:51-52), typologies/BA006_Dormant_Reactivation.md (T: weights
T:109-116, the worked example T:120-130, bands T:133, business logic T:139-149) and owner
oracle rule R1 (2026-10-21: where the typology's Python snippet T:174-179 disagrees with the
band table, the band table governs). Every expected score below is hand-worked from those
numbers in a comment beside it. Inputs are CONSTRUCTED here: no sample-data file is read and
no sample entity's name is asserted.

Contributions per band (midpoint x weight), from F:
    reactivation spike   30%: L 4.5   M 13.5   H 21    C 27
    dormancy length      25%: L 3.75  M 11.25  H 17.5  C 22.5
    profile deviation    25%: L 3.75  M 11.25  H 17.5  C 22.5
    immediate outflow    20%: L 3     M 9      H 14    C 18
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

from ba006_risk_model import (  # noqa: E402
    RiskModelError, band_of, ba006_exposure_score, score_dormancy_length,
    score_immediate_outflow, score_profile_deviation, score_reactivation_spike,
)

SCENARIO = BASE_DIR / "scenarios" / "dormant_reactivation.py"
NAMES = ("reactivation_spike", "dormancy_length", "profile_deviation", "immediate_outflow")
BAND_COLS = {n: n + "_band" for n in NAMES}


def _load():
    spec = spec_from_file_location("tt_ba006_doctrine_dormant_reactivation", SCENARIO)
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


def _account(ref, baseline, reactivation, days, new_cps, outflow):
    return {"customer_name": "Constructed Holder %s" % ref, "account_ref": ref,
            "segment": "Retail", "home_branch": "Constructed Branch",
            "prior_counterparty_name": "Constructed Prior %s" % ref,
            "pre_dormancy_avg_monthly_activity": baseline, "reactivation_amount": reactivation,
            "dormancy_days": days, "new_counterparty_count": new_cps, "outflow_amount": outflow,
            "first_reactivation_counterparty_name": "Constructed First %s" % ref,
            "second_reactivation_counterparty_name": "Constructed Second %s" % ref}


def _frames(*accounts):
    acc = pd.DataFrame(list(accounts))
    cps = pd.DataFrame([{"first_reactivation_counterparty_name": a["first_reactivation_counterparty_name"],
                         "account_ref": a["account_ref"], "bank": "Constructed Bank",
                         "jurisdiction": "GB", "relationship": "Unverified counterparty",
                         "prior_alerts": 0} for a in accounts])
    return {"accounts": acc, "counterparties": cps}


# The framework's worked example (F:41-49): $200,000 against an $8,000 monthly average (r 25.0, C),
# 730 days (C), 10 new counterparties (C), $190,000 of $200,000 drains out (r 0.950, C):
# 27+22.5+22.5+18 = 90.
WORKED = ("T-WE", 8000, 200000, 730, 10, 190000)
# All-Low background (F:51 'a clean account with all four components Low scores 15'):
# r 2 (L), 30 days (L), 1 new counterparty (L), r 0.25 (L): 4.5+3.75+3.75+3 = 15.
CLEAN = ("T-BG", 6000, 12000, 30, 1, 3000)


# ---------------------------------------------------------------- check 2: boundaries
# Each cut-line from F:17-35: exactly at it, just below, just above.

@pytest.mark.parametrize("reactivation,band", [
    (2999, "Low"), (3000, "Medium"), (3001, "Medium"),          # r < 3 -> Low
    (7999, "Medium"), (8000, "High"), (8001, "High"),           # r < 8 -> Medium
    (19999, "High"), (20000, "Critical"), (20001, "Critical"),  # r < 20 -> High, otherwise Critical
])
def test_reactivation_spike_cut_lines(reactivation, band):
    assert score_reactivation_spike(reactivation, 1000) == band


def test_spike_is_reactivation_over_pre_dormancy_baseline():
    # F:18 r = reactivation_amount / pre_dormancy_avg_monthly_activity. 1000 against a 25000
    # baseline = 0.04 Low; the inverse (25) would be Critical.
    assert score_reactivation_spike(1000, 25000) == "Low"


@pytest.mark.parametrize("baseline", [0, -1, -8000])
def test_spike_refuses_a_baseline_not_above_zero(baseline):
    # F:19 "pre_dormancy_avg_monthly_activity must be > 0".
    with pytest.raises(RiskModelError):
        score_reactivation_spike(200000, baseline)


@pytest.mark.parametrize("days,band", [
    (0, "Low"),
    (89, "Low"), (90, "Medium"), (91, "Medium"),        # < 90 Low
    (179, "Medium"), (180, "High"), (181, "High"),      # < 180 Medium
    (364, "High"), (365, "Critical"), (366, "Critical"),  # < 365 High, otherwise (>= 365) Critical
])
def test_dormancy_length_cut_lines(days, band):
    # F:25; the edge of each period belongs to the LONGER band (longer dormancy is worse, F:24).
    assert score_dormancy_length(days) == band


@pytest.mark.parametrize("n,band", [
    (0, "Low"), (2, "Low"), (3, "Medium"), (4, "Medium"),
    (5, "High"), (7, "High"), (8, "Critical"), (10, "Critical"),
])  # F:30 <= 2 Low, <= 4 Medium, <= 7 High, otherwise (>= 8) Critical
def test_profile_deviation_cut_lines(n, band):
    assert score_profile_deviation(n) == band


@pytest.mark.parametrize("outflow,band", [
    (4999, "Low"), (5000, "Medium"), (5001, "Medium"),        # r < 0.50 -> Low
    (7499, "Medium"), (7500, "High"), (7501, "High"),         # r < 0.75 -> Medium
    (9199, "High"), (9200, "Critical"), (9201, "Critical"),   # r < 0.92 -> High, otherwise Critical
])
def test_immediate_outflow_cut_lines(outflow, band):
    assert score_immediate_outflow(outflow, 10000) == band


def test_outflow_is_outflow_over_reactivation():
    # F:33 r = outflow_amount / reactivation_amount. 3000 out of 10000 = 0.30 Low; the inverse
    # (3.33) would be Critical.
    assert score_immediate_outflow(3000, 10000) == "Low"


@pytest.mark.parametrize("reactivation", [0, -1, -200000])
def test_outflow_refuses_a_reactivation_not_above_zero(reactivation):
    # F:34 "reactivation_amount must be > 0".
    with pytest.raises(RiskModelError):
        score_immediate_outflow(5000, reactivation)


@pytest.mark.parametrize("score,band", [
    (0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
    (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical"),
])
def test_score_band_table(score, band):
    # T:133 Classification: 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    assert band_of(score) == band


@pytest.mark.parametrize("code,score,band", [
    ("CCCC", 90, "Critical"),   # 27+22.5+22.5+18 = 90 (worked example, F:49)
    ("LLLL", 15, "Low"),        # 4.5+3.75+3.75+3 = 15 (F:51)
    ("CHHC", 80, "Critical"),   # 27+17.5+17.5+18 = 80 exactly: the alert boundary
    ("HCCH", 80, "Critical"),   # 21+22.5+22.5+14 = 80 exactly
    ("HHCC", 79, "High"),       # 21+17.5+22.5+18 = 79
    ("CCCH", 86, "Critical"),   # 27+22.5+22.5+14 = 86
    ("CHCC", 85, "Critical"),   # 27+17.5+22.5+18 = 85
    ("HCCC", 84, "Critical"),   # 21+22.5+22.5+18 = 84
    ("CMCC", 79, "High"),       # 27+11.25+22.5+18 = 78.75 -> 79
    ("CLLL", 38, "Medium"),     # 27+3.75+3.75+3 = 37.5 -> 38 (half-up)
    ("MMMM", 45, "Medium"),     # every component at the Medium midpoint
    ("HHHH", 70, "High"),       # every component at the High midpoint
])
def test_weighted_midpoint_score(code, score, band):
    got_score, got_band, working = ba006_exposure_score(_bands(code))
    assert (got_score, got_band) == (score, band)
    assert {k: v["weight"] for k, v in working["components"].items()} == {
        "reactivation_spike": 0.30, "dormancy_length": 0.25,
        "profile_deviation": 0.25, "immediate_outflow": 0.20}   # F:8-13


def test_half_up_rounding_on_an_exact_half():
    # LMLL: 4.5 + 11.25 + 3.75 + 3 = 22.5 exactly. Half-up -> 23 (half-even would give 22).
    score, band, working = ba006_exposure_score(_bands("LMLL"))
    assert working["total"] == 22.5
    assert (score, band) == (23, "Low")


def test_alert_threshold_is_inclusive_at_80(engine):
    # F:51-52 alert at >= 80. CHHC scores exactly 80 (r 20 C, 200 days H, 6 new H, r 0.95 C);
    # HHCC scores 79 (r 10 H, 200 days H, 10 new C, r 0.95 C). Same evaluate call.
    frames = _frames(_account("T-80", 1000, 20000, 200, 6, 19000),
                     _account("T-79", 1000, 10000, 200, 10, 9500))
    scored = engine.score_all(**frames).set_index("account_ref")
    assert scored.loc["T-80", "exposure_score"] == 80
    assert scored.loc["T-79", "exposure_score"] == 79
    assert list(engine.evaluate_dormant_reactivation(**frames)["account_ref"]) == ["T-80"]


# ---------------------------------------------------------------- check 4: positives / near-misses

def test_worked_example_alerts_90_critical(engine):
    out = engine.evaluate_dormant_reactivation(**_frames(_account(*WORKED)))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["exposure_score"], row["exposure_band"]) == (90, "Critical")
    assert [row[BAND_COLS[n]] for n in NAMES] == ["Critical"] * 4
    assert (row["pre_dormancy_avg_monthly_activity"], row["reactivation_amount"]) == (8000, 200000)
    assert (row["dormancy_days"], row["new_counterparty_count"], row["outflow_amount"]) == (730, 10, 190000)
    assert row["first_reactivation_counterparty_name"] == "Constructed First T-WE"
    assert row["subject_entity_id"] == "T-WE"


def test_background_clean_account_scores_15_and_does_not_alert(engine):
    frames = _frames(_account(*CLEAN), _account(*WORKED))
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert (scored.loc["T-BG", "exposure_score"], scored.loc["T-BG", "exposure_band"]) == (15, "Low")
    assert list(engine.evaluate_dormant_reactivation(**frames)["account_ref"]) == ["T-WE"]


# One positive and one near-miss per detection rule (component). The positive sits EXACTLY on the
# component's Critical cut-line; the near-miss moves only that component just under it.
PER_RULE = {
    # r = 20 (C), 400 days (C), 6 new (H), r 0.80 (H): 27+22.5+17.5+14 = 81 alert;
    # r = 19.999 (H): 21+22.5+17.5+14 = 75 no alert
    "reactivation_spike": (_account("P-RS", 1000, 20000, 400, 6, 16000),
                           _account("N-RS", 1000, 19999, 400, 6, 16000), 81, 75),
    # 365 days (C) with r 25 (C), 6 new (H), r 0.80 (H): 27+22.5+17.5+14 = 81 alert;
    # 364 days (H): 27+17.5+17.5+14 = 76 no alert
    "dormancy_length": (_account("P-DL", 1000, 25000, 365, 6, 20000),
                        _account("N-DL", 1000, 25000, 364, 6, 20000), 81, 76),
    # 8 new (C) with r 25 (C), 200 days (H), r 0.80 (H): 27+17.5+22.5+14 = 81 alert;
    # 7 new (H): 27+17.5+17.5+14 = 76 no alert
    "profile_deviation": (_account("P-PD", 1000, 25000, 200, 8, 20000),
                          _account("N-PD", 1000, 25000, 200, 7, 20000), 81, 76),
    # r = 0.92 (C) with r 20 (C), 200 days (H), 6 new (H): 27+17.5+17.5+18 = 80 alert;
    # 18399/20000 = 0.91995 (H): 27+17.5+17.5+14 = 76 no alert
    "immediate_outflow": (_account("P-IO", 1000, 20000, 200, 6, 18400),
                          _account("N-IO", 1000, 20000, 200, 6, 18399), 80, 76),
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
    alerts = engine.evaluate_dormant_reactivation(**frames)
    assert list(alerts["account_ref"]) == [positive["account_ref"]]


def test_an_account_dormant_under_180_days_cannot_alert(engine):
    """From F's weights alone: with dormancy Medium (11.25) and every other component Critical the
    best total is 27+11.25+22.5+18 = 78.75 -> 79, under 80. So dormancy must reach High (>= 180
    days, F:25) before an account can alert -- the typology's 'dormancy beyond a normal quiet
    period' (T:45-46). 179 days scores 79 and does not alert; 180 days (H) scores
    27+17.5+22.5+18 = 85 and alerts, in the same call."""
    frames = _frames(_account("T-179", 1000, 25000, 179, 10, 23750),
                     _account("T-180", 1000, 25000, 180, 10, 23750))
    scored = engine.score_all(**frames).set_index("account_ref")
    assert (scored.loc["T-179", "dormancy_length_band"], scored.loc["T-179", "exposure_score"]) == ("Medium", 79)
    assert (scored.loc["T-180", "dormancy_length_band"], scored.loc["T-180", "exposure_score"]) == ("High", 85)
    assert list(engine.evaluate_dormant_reactivation(**frames)["account_ref"]) == ["T-180"]


def test_the_typology_snippet_is_not_needed_to_alert(engine):
    """Owner rule R1 (2026-10-21): the band table governs, not T:174-179's snippet. The snippet
    adds no outflow test, so the score alone decides: T-OUTM has outflow only Medium
    (r 0.60, 9) with r 25 (C), 400 days (C), 10 new (C): 27+22.5+22.5+9 = 81 and alerts;
    T-OUTL with outflow Low (r 0.10, 3): 27+22.5+22.5+3 = 75 does not."""
    frames = _frames(_account("T-OUTM", 1000, 25000, 400, 10, 15000),
                     _account("T-OUTL", 1000, 25000, 400, 10, 2500))
    scored = engine.score_all(**frames).set_index("account_ref")
    assert (scored.loc["T-OUTM", "exposure_score"], scored.loc["T-OUTL", "exposure_score"]) == (81, 75)
    assert list(engine.evaluate_dormant_reactivation(**frames)["account_ref"]) == ["T-OUTM"]


def test_alert_row_carries_its_own_working(engine):
    # CCCH: r 25 C, 400 days C, 10 new C, r 0.80 H = 27+22.5+22.5+14 = 86 Critical
    out = engine.evaluate_dormant_reactivation(**_frames(_account("T-W", 1000, 25000, 400, 10, 20000)))
    working = json.loads(out.iloc[0]["risk_components"])
    assert set(working["components"]) == set(NAMES)
    assert working["score"] == 86 and working["band"] == "Critical"
    assert "reactivating inflow" in out.iloc[0]["risk_reason"]   # dominant driver: the spike (27)


def test_score_all_puts_the_highest_score_first(engine):
    # The fc-10 demo path builds its case from score_all's top row (F:53-56).
    frames = _frames(_account(*CLEAN), _account(*WORKED))
    assert list(engine.score_all(**frames)["account_ref"]) == ["T-WE", "T-BG"]


# ---------------------------------------------------------------- required inputs

NAN = float("nan")
FIELDS = ("pre_dormancy_avg_monthly_activity", "reactivation_amount", "dormancy_days",
          "new_counterparty_count", "outflow_amount")


@pytest.mark.parametrize("field", FIELDS)
def test_the_callable_refuses_an_account_with_a_blank_input(engine, field):
    """F:18,23,28,33: every input is REQUIRED ('not measured is not zero'). The worked example
    alerts at 90 with every input present; with `field` blank the callable must refuse."""
    account = _account(*WORKED)
    assert len(engine.evaluate_dormant_reactivation(**_frames(account))) == 1
    account[field] = ""
    with pytest.raises(ValueError):
        engine.evaluate_dormant_reactivation(**_frames(account))


@pytest.mark.parametrize("field", [f for f in FIELDS if f != "dormancy_days"])
def test_the_callable_refuses_a_nan_amount_or_count(engine, field):
    """Same rule for NaN. The refusal is INCIDENTAL: the int(float()) output casts at
    dormant_reactivation.py:86-90 (and ba006_risk_model.py:110 for the count) raise on NaN.
    dormancy_days has no such cast (dormant_reactivation.py:88 is float()): see the D043 witness."""
    account = _account(*WORKED)
    account[field] = NAN
    with pytest.raises(ValueError):
        engine.evaluate_dormant_reactivation(**_frames(account))


# ---------------------------------------------------------------- known items (cited)

@pytest.mark.parametrize("scorer,args", [
    (score_reactivation_spike, (NAN, 1000)),
    (score_reactivation_spike, (25000, NAN)),
    (score_dormancy_length, (NAN,)),
    (score_immediate_outflow, (NAN, 10000)),
    (score_immediate_outflow, (9000, NAN)),
])
@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: F:18,23,33 inputs are REQUIRED; ba006_risk_model.py:60-65 _require checks "
    "None only, so a NaN makes every comparison at :83-89 / :97-103 / :129-135 False and the "
    "component scores Critical -- measured: Failed: DID NOT RAISE <class 'ValueError'>"))
def test_a_missing_value_refuses_rather_than_scoring_critical(scorer, args):
    assert any(isinstance(a, float) and math.isnan(a) for a in args)
    with pytest.raises(ValueError):
        scorer(*args)


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "KNOWN D043, cited: its BA006 effect is an ALERT FLIP. F:23 'dormancy_days is REQUIRED'; a NaN "
    "dormancy bands Critical (ba006_risk_model.py:96-103) and, unlike the other inputs, is never "
    "cast to int (dormant_reactivation.py:88 float()), so nothing refuses it. T-NAN (r 25 C, NaN "
    "days, 10 new C, r 0.95 C) scores CCCC = 90 and alerts; with any measured dormancy under 90 "
    "days it would score 27+3.75+22.5+18 = 71 -- measured: AssertionError, alerts "
    "['T-NAN', 'T-WE'] != ['T-WE']"))
def test_a_nan_dormancy_does_not_alert(engine):
    # Alerting control in the SAME call: the worked example (90).
    frames = _frames(_account("T-NAN", 8000, 200000, NAN, 10, 190000), _account(*WORKED))
    assert len(engine.score_all(**frames)) == 2
    assert sorted(engine.evaluate_dormant_reactivation(**frames)["account_ref"]) == ["T-WE"]


# ---------------------------------------------------------------- defects

@pytest.mark.parametrize("reactivation,baseline,band", [
    ("3000.24", "1000.08", "Medium"),     # = 3 exactly
    ("20001.60", "1000.08", "Critical"),  # = 20 exactly
])
@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "DEFECT: F:20 'r < 3 -> Low · r < 8 -> Medium · r < 20 -> High · otherwise -> Critical': a "
    "ratio EXACTLY at the cut-line belongs to the upper band, but ba006_risk_model.py:82 computes "
    "r in binary float, so 3000.24/1000.08 (= 3) gives 2.9999999999999996 -> Low and "
    "20001.60/1000.08 (= 20) gives 19.999999999999996 -> High -- measured: AssertionError "
    "'Low' == 'Medium' / 'High' == 'Critical'"))
def test_reactivation_spike_exactly_at_a_decimal_cut_line(reactivation, baseline, band):
    assert score_reactivation_spike(reactivation, baseline) == band


@pytest.mark.parametrize("outflow,reactivation,band", [
    ("920.92", "1001", "Critical"),       # 920.92 / 1001 = 0.92 exactly
    ("750.06", "1000.08", "High"),        # 750.06 / 1000.08 = 0.75 exactly
])
@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "DEFECT: F:35 'r < 0.75 -> Medium · r < 0.92 -> High · otherwise -> Critical': a ratio EXACTLY "
    "at the cut-line belongs to the upper band, but ba006_risk_model.py:128 computes r in binary "
    "float, so 920.92/1001 (= 0.92) gives 0.9199999999999999 -> High and 750.06/1000.08 (= 0.75) "
    "gives 0.7499999999999999 -> Medium -- measured: AssertionError 'High' == 'Critical' / "
    "'Medium' == 'High'"))
def test_immediate_outflow_exactly_at_a_decimal_cut_line(outflow, reactivation, band):
    assert score_immediate_outflow(outflow, reactivation) == band


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "DEFECT: same float cut-line, end to end: T-CS reactivates 20001.60 against a 1000.08 baseline "
    "(r = 20, F:20 Critical) with 400 days (C), 6 new (H), r 0.80 (H): CCHH = 81, must alert "
    "(F:51-52); ba006_risk_model.py:82 bands the spike High, HCHH = 75, and "
    "evaluate_dormant_reactivation drops it -- measured: AssertionError, alerts ['T-WS'] != "
    "['T-CS', 'T-WS']"))
def test_a_cent_spike_at_the_cut_line_still_alerts(engine):
    # Alerting control in the SAME call: the whole-dollar twin (20000 of 1000), also CCHH = 81.
    frames = _frames(_account("T-CS", "1000.08", "20001.60", "400", "6", "16001.28"),
                     _account("T-WS", "1000", "20000", "400", "6", "16000"))
    assert len(engine.score_all(**frames)) == 2
    assert sorted(engine.evaluate_dormant_reactivation(**frames)["account_ref"]) == ["T-CS", "T-WS"]


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "DEFECT: same float cut-line, end to end: T-CO drains 920.92 of a 1001 reactivation (r = 0.92, "
    "F:35 Critical) with r 25.025 (C), 200 days (H), 6 new (H): CHHC = 80, must alert (F:51-52); "
    "ba006_risk_model.py:128 bands the outflow High, CHHH = 76, and evaluate_dormant_reactivation "
    "drops it -- measured: AssertionError, alerts ['T-WO'] != ['T-CO', 'T-WO']"))
def test_a_cent_outflow_at_the_cut_line_still_alerts(engine):
    # Alerting control in the SAME call: the whole-dollar twin (18400 of 20000), also CHHC = 80.
    frames = _frames(_account("T-CO", "40", "1001", "200", "6", "920.92"),
                     _account("T-WO", "1000", "20000", "200", "6", "18400"))
    assert len(engine.score_all(**frames)) == 2
    assert sorted(engine.evaluate_dormant_reactivation(**frames)["account_ref"]) == ["T-CO", "T-WO"]
