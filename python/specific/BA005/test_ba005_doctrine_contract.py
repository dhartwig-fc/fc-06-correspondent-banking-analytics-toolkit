"""TT-BA005 (night 10, wave C): the BA005 Rapid Movement engine against its doctrine.

Oracle, and nothing else: scoring-models/specific/BA005_Rapid_Movement_Scoring_Framework.md
(component cut-lines L18-35, weights L10-13, midpoints / half-up / boundary at 80 L39, alert
threshold >= 80 L52, every input REQUIRED, avg_balance and inbound_amount > 0),
typologies/BA005_Rapid_Movement.md (bands 0-29/30-59/60-79/80-100 L124, the worked example
L110-118, Business Logic L129-136) and oracle rule R1 (the band table governs over the
doctrine's illustrative Python snippet, L161-166). No signed-off expected-outcome sheet
exists for BA005. Every expected score below is hand-worked from those numbers in a comment
beside it. Inputs are CONSTRUCTED here: no sample-data file is read and no sample entity's
name is asserted.

Contributions per band (midpoint x weight), from the framework:
    dwell time         35%: L 5.25  M 15.75  H 24.5  C 31.5
    velocity           25%: L 3.75  M 11.25  H 17.5  C 22.5
    onward dispersion  20%: L 3     M 9      H 14    C 18
    value match        20%: L 3     M 9      H 14    C 18
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

from ba005_risk_model import (  # noqa: E402
    RiskModelError, band_of, ba005_exposure_score, score_dwell_time, score_onward_dispersion,
    score_value_match, score_velocity,
)

SCENARIO = BASE_DIR / "scenarios" / "rapid_movement.py"
NAMES = ("dwell_time", "velocity", "onward_dispersion", "value_match")
BAND_COLS = {n: n + "_band" for n in NAMES}
NUMERIC_INPUTS = ("inbound_amount", "outbound_amount", "dwell_time_hours", "avg_balance",
                  "total_turnover_amount", "distinct_destination_count")


def _load():
    spec = spec_from_file_location("tt_ba005_doctrine_rapid_movement", SCENARIO)
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


def _account(ref, inbound, outbound, dwell, balance, turnover, destinations):
    return {"customer_name": "Constructed Holder %s" % ref, "account_ref": ref,
            "segment": "Corporate", "home_branch": "Constructed Branch",
            "source_name": "Constructed Source %s" % ref,
            "inbound_amount": inbound, "outbound_amount": outbound,
            "dwell_time_hours": dwell, "avg_balance": balance,
            "total_turnover_amount": turnover, "distinct_destination_count": destinations,
            "first_destination_name": "Constructed First Onward %s" % ref,
            "second_destination_name": "Constructed Second Onward %s" % ref}


def _frames(*accounts):
    acc = pd.DataFrame(list(accounts))
    dest = pd.DataFrame([{"first_destination_name": a["first_destination_name"],
                          "account_ref": a["account_ref"], "bank": "Constructed Bank",
                          "jurisdiction": "GB", "relationship": "onward",
                          "prior_alerts": 0} for a in accounts])
    return {"accounts": acc, "destinations": dest}


def _worked(ref="T-WE"):
    # Framework worked example (L41-49): $100,000 in, $98,000 out (r 0.980 C), 1 hour (C),
    # $300,000 turnover on a $10,000 balance (r 30.0 C), 9 destinations (C):
    # 31.5+22.5+18+18 = 90 Critical.
    return _account(ref, 100000, 98000, 1, 10000, 300000, 9)


# ---------------------------------------------------------------- check 2: boundaries
# Each cut-line from the framework: exactly at it, just below, just above.

@pytest.mark.parametrize("hours,band", [
    (48.01, "Low"), (48, "Low"), (47.99, "Medium"),        # >= 48 Low
    (12.01, "Medium"), (12, "Medium"), (11.99, "High"),    # >= 12 Medium
    (2.01, "High"), (2, "High"), (1.99, "Critical"),       # >= 2 High, otherwise (< 2) Critical
])
def test_dwell_time_cut_lines(hours, band):
    assert score_dwell_time(hours) == band


@pytest.mark.parametrize("turnover,band", [
    (29999, "Low"), (30000, "Medium"), (30001, "Medium"),        # r < 3 Low
    (79999, "Medium"), (80000, "High"), (80001, "High"),         # r < 8 Medium
    (199999, "High"), (200000, "Critical"), (200001, "Critical"),  # r < 20 High, >= 20 Critical
])
def test_velocity_cut_lines(turnover, band):
    assert score_velocity(turnover, 10000) == band


def test_velocity_is_turnover_over_balance():
    # r = 20000/10000 = 2.0 Low; the inverse (0.5) would also be Low, so use a large ratio:
    # r = 250000/10000 = 25 Critical; the inverse (0.04) would be Low.
    assert score_velocity(250000, 10000) == "Critical"
    assert score_velocity(10000, 250000) == "Low"


@pytest.mark.parametrize("balance", [0, -1, -10000])
def test_velocity_refuses_balance_not_above_zero(balance):
    # Framework L24: "avg_balance must be > 0".
    with pytest.raises(RiskModelError):
        score_velocity(30000, balance)


@pytest.mark.parametrize("count,band", [
    (2, "Low"), (3, "Medium"),                        # <= 2 Low
    (4, "Medium"), (5, "High"),                       # <= 4 Medium
    (7, "High"), (8, "Critical"), (9, "Critical"),    # <= 7 High, otherwise (>= 8) Critical
])
def test_onward_dispersion_cut_lines(count, band):
    assert score_onward_dispersion(count) == band


@pytest.mark.parametrize("outbound,band", [
    (4999, "Low"), (5000, "Medium"), (5001, "Medium"),         # r < 0.50 Low
    (7499, "Medium"), (7500, "High"), (7501, "High"),          # r < 0.75 Medium
    (9199, "High"), (9200, "Critical"), (9201, "Critical"),    # r < 0.92 High, >= 0.92 Critical
])
def test_value_match_cut_lines(outbound, band):
    assert score_value_match(outbound, 10000) == band


def test_value_match_is_outbound_over_inbound():
    # r = 4000/10000 = 0.40 Low; the inverse (2.5) would be Critical.
    assert score_value_match(4000, 10000) == "Low"


@pytest.mark.parametrize("inbound", [0, -1, -10000])
def test_value_match_refuses_inbound_not_above_zero(inbound):
    # Framework L34: "inbound_amount must be > 0".
    with pytest.raises(RiskModelError):
        score_value_match(5000, inbound)


@pytest.mark.parametrize("score,band", [
    (0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
    (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical"),
])
def test_score_band_table(score, band):
    # typologies/BA005_Rapid_Movement.md L124: 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    assert band_of(score) == band


@pytest.mark.parametrize("code,score,band", [
    ("CCCC", 90, "Critical"),   # 31.5+22.5+18+18 = 90 (framework worked example)
    ("LLLL", 15, "Low"),        # 5.25+3.75+3+3 = 15 (framework L51: clean account 15/100)
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
    got_score, got_band, working = ba005_exposure_score(_bands(code))
    assert (got_score, got_band) == (score, band)
    assert len(working["components"]) == 4


def test_half_up_rounding_on_an_exact_half():
    # LMLL: 5.25 + 11.25 + 3 + 3 = 22.5 exactly. Half-up -> 23 (half-even would give 22).
    score, band, working = ba005_exposure_score(_bands("LMLL"))
    assert working["total"] == 22.5
    assert (score, band) == (23, "Low")


def test_rounding_happens_once_and_cannot_lift_a_79_to_an_alert(engine):
    # CMCC: 31.5 + 11.25 + 18 + 18 = 78.75 -> half-up 79 High: below the >= 80 boundary.
    # In the SAME frame, an alerting control (the worked example, 90).
    # dwell 1 h C; r 50000/10000 = 5 M; 9 destinations C; r 9800/10000 = 0.98 C.
    t = _account("T-7875", 10000, 9800, 1, 10000, 50000, 9)
    frames = _frames(t, _worked())
    scored = engine.score_all(**frames).set_index("account_ref")
    assert (scored.loc["T-7875", "exposure_score"], scored.loc["T-7875", "exposure_band"]) == (79, "High")
    assert json.loads(scored.loc["T-7875", "risk_components"])["total"] == 78.75
    assert list(engine.evaluate_rapid_movement(**frames)["account_ref"]) == ["T-WE"]


def test_alert_threshold_is_inclusive_at_80(engine, monkeypatch):
    """With these weights no band combination scores exactly 80 (79 and 81 are the
    neighbours), so the >= 80 filter (framework L52) is checked by fixing the scorer's output
    at 80 and 79."""
    real = engine.ba005_exposure_score

    def fixed(bands, value):
        _s, _b, working = real(bands)
        return value, band_of(value), working

    frames = _frames(_worked("T80"))
    monkeypatch.setattr(engine, "ba005_exposure_score", lambda b: fixed(b, 80))
    assert list(engine.evaluate_rapid_movement(**frames)["account_ref"]) == ["T80"]
    monkeypatch.setattr(engine, "ba005_exposure_score", lambda b: fixed(b, 79))
    assert len(engine.evaluate_rapid_movement(**frames)) == 0


# ---------------------------------------------------------------- check 4: positives / near-misses

def test_worked_example_alerts_90_critical(engine):
    out = engine.evaluate_rapid_movement(**_frames(_worked()))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["exposure_score"], row["exposure_band"]) == (90, "Critical")
    assert [row[BAND_COLS[n]] for n in NAMES] == ["Critical"] * 4
    assert (row["inbound_amount"], row["outbound_amount"]) == (100000, 98000)
    assert (row["dwell_time_hours"], row["avg_balance"], row["total_turnover_amount"],
            row["distinct_destination_count"]) == (1.0, 10000, 300000, 9)
    assert row["subject_entity_id"] == "T-WE"
    assert row["first_destination_name"] == "Constructed First Onward T-WE"
    assert row["second_destination_name"] == "Constructed Second Onward T-WE"


def test_clean_account_scores_15_and_does_not_alert(engine):
    # Framework L51: all four Low scores 15/100. 960 h (L), r 30000/15000 = 2 (L),
    # 1 destination (L), r 8000/20000 = 0.40 (L). Alerting control in the SAME frame.
    frames = _frames(_account("T-CLEAN", 20000, 8000, 960, 15000, 30000, 1), _worked())
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert (scored.loc["T-CLEAN", "exposure_score"], scored.loc["T-CLEAN", "exposure_band"]) == (15, "Low")
    assert list(engine.evaluate_rapid_movement(**frames)["account_ref"]) == ["T-WE"]


# One positive and one near-miss per detection rule (component). The positive sits EXACTLY on the
# component's Critical cut-line (dwell: just inside it, < 2); the near-miss moves only that
# component just outside it.
PER_RULE = {
    # dwell 1.99 h (C), r 100000/10000 = 10 (H), 5 destinations (H), r 9500/10000 = 0.95 (C):
    #   31.5+17.5+14+18 = 81 alert;   2 h (H): 24.5+17.5+14+18 = 74 no alert
    "dwell_time": (_account("P-DW", 10000, 9500, 1.99, 10000, 100000, 5),
                   _account("N-DW", 10000, 9500, 2, 10000, 100000, 5), 81, 74),
    # r 200000/10000 = 20 (C), 1 h (C), 5 destinations (H), r 0.85 (H):
    #   31.5+22.5+14+14 = 82 alert;   r 19.9999 (H): 31.5+17.5+14+14 = 77 no alert
    "velocity": (_account("P-VE", 10000, 8500, 1, 10000, 200000, 5),
                 _account("N-VE", 10000, 8500, 1, 10000, 199999, 5), 82, 77),
    # 8 destinations (C), 1 h (C), r 10 (H), r 0.85 (H):
    #   31.5+17.5+18+14 = 81 alert;   7 destinations (H): 31.5+17.5+14+14 = 77 no alert
    "onward_dispersion": (_account("P-OD", 10000, 8500, 1, 10000, 100000, 8),
                          _account("N-OD", 10000, 8500, 1, 10000, 100000, 7), 81, 77),
    # r 9200/10000 = 0.92 (C), 1 h (C), r 10 (H), 5 destinations (H):
    #   31.5+17.5+14+18 = 81 alert;   r 0.9199 (H): 31.5+17.5+14+14 = 77 no alert
    "value_match": (_account("P-VM", 10000, 9200, 1, 10000, 100000, 5),
                    _account("N-VM", 10000, 9199, 1, 10000, 100000, 5), 81, 77),
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
    alerts = engine.evaluate_rapid_movement(**frames)
    assert list(alerts["account_ref"]) == [positive["account_ref"]]


def test_alert_row_carries_its_own_working(engine):
    # P-VE above: CCHH = 31.5+22.5+14+14 = 82 Critical
    out = engine.evaluate_rapid_movement(**_frames(PER_RULE["velocity"][0]))
    working = json.loads(out.iloc[0]["risk_components"])
    assert set(working["components"]) == set(NAMES)
    assert working["score"] == 82 and working["band"] == "Critical"
    assert {n: c["band"] for n, c in working["components"].items()} == _bands("CCHH")


def test_score_all_puts_the_highest_score_first(engine):
    # The fc-10 demo path builds its case from score_all's top row (framework L54-56).
    frames = _frames(_account("T-LOW", 20000, 8000, 960, 15000, 30000, 1), _worked("T-HIGH"))
    assert list(engine.score_all(**frames)["account_ref"]) == ["T-HIGH", "T-LOW"]


def test_every_account_needs_its_destination_record(engine):
    # Business Logic step 1 (L130): resolve every onward destination. An alerting account
    # with no destination record is refused rather than scored.
    frames = _frames(_worked("T-A"), _worked("T-B"))
    frames["destinations"] = frames["destinations"][frames["destinations"]["account_ref"] == "T-A"]
    assert len(engine.evaluate_rapid_movement(**_frames(_worked("T-A")))) == 1
    with pytest.raises(ValueError, match="destination"):
        engine.evaluate_rapid_movement(**frames)


# ---------------------------------------------------------------- required inputs

NAN = float("nan")


def test_a_missing_destination_count_refuses():
    # Framework L28: distinct_destination_count is REQUIRED. NaN is refused
    # (int(float(nan)) raises ValueError).
    with pytest.raises(ValueError):
        score_onward_dispersion(NAN)


@pytest.mark.parametrize("scorer,args", [
    (score_dwell_time, ("",)),
    (score_velocity, ("", "10000")), (score_velocity, ("300000", "")),
    (score_onward_dispersion, ("",)),
    (score_value_match, ("", "10000")), (score_value_match, ("9800", "")),
])
def test_the_model_refuses_a_blank_rather_than_scoring_it(scorer, args):
    # The model itself must refuse, not lean on the callable's output cast: a blank read
    # as zero would score dwell 0 h Critical and a ratio of 0 Low (framework: REQUIRED).
    assert scorer(*[a or "1" for a in args]) in ("Low", "Medium", "High", "Critical")
    with pytest.raises(ValueError):
        scorer(*args)


@pytest.mark.parametrize("field", NUMERIC_INPUTS)
def test_a_blank_input_as_read_from_csv_refuses(engine, field):
    # The sample reader reads every cell as a string with keep_default_na=False, so a
    # missing value arrives as "". Framework: every input is REQUIRED; "not measured is
    # not zero". The callable must refuse, never score the blank as zero.
    account = {k: str(v) for k, v in _worked("T-BLANK").items()}
    assert len(engine.evaluate_rapid_movement(**_frames(account))) == 1
    account[field] = ""
    with pytest.raises(ValueError):
        engine.evaluate_rapid_movement(**_frames(account))


# ---------------------------------------------------------------- KNOWN D043 (cited)

@pytest.mark.parametrize("scorer,args", [
    (score_dwell_time, (NAN,)),
    (score_velocity, (NAN, 10000)),
    (score_velocity, (300000, NAN)),
    (score_value_match, (NAN, 10000)),
    (score_value_match, (9800, NAN)),
])
@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: framework BA005 'REQUIRED' (scoring-models/specific/BA005_Rapid_Movement_"
    "Scoring_Framework.md:18,23,33) and the model's own 'missing != zero': a NaN passes "
    "ba005_risk_model.py:58-63 (_require checks None only), every comparison at :78-84 / :96-102 / "
    ":127-133 is False, and avg_balance NaN also passes the '> 0' guard at :93, so it scores "
    "Critical -- measured: Failed: DID NOT RAISE <class 'ValueError'>"))
def test_a_missing_value_refuses_rather_than_scoring_critical(scorer, args):
    assert any(isinstance(a, float) and math.isnan(a) for a in args)
    with pytest.raises(ValueError):
        scorer(*args)


@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited, measured effect in BA005: a missing (NaN) dwell_time_hours is scored "
    "Critical (ba005_risk_model.py:77-84), lifting a 79 High non-alert to 86 Critical, and "
    "evaluate_rapid_movement ALERTS it (rapid_movement.py:67,85 -- float(nan) survives the output "
    "cast) instead of refusing -- measured: Failed: DID NOT RAISE <class 'ValueError'>"))
def test_a_missing_dwell_flips_a_non_alert_into_an_alert(engine):
    # dwell 5 h (H), r 300000/10000 = 30 (C), 9 destinations (C), r 0.85 (H):
    # 24.5+22.5+18+14 = 79 High, no alert. Alerting control in the SAME frame.
    account = _account("T-NAN", 10000, 8500, 5, 10000, 300000, 9)
    frames = _frames(account, _worked())
    scored = engine.score_all(**frames).set_index("account_ref")
    assert scored.loc["T-NAN", "exposure_score"] == 79
    assert list(engine.evaluate_rapid_movement(**frames)["account_ref"]) == ["T-WE"]
    account["dwell_time_hours"] = NAN
    with pytest.raises(ValueError):
        engine.evaluate_rapid_movement(**_frames(account, _worked()))


@pytest.mark.parametrize("field", ["inbound_amount", "outbound_amount", "avg_balance",
                                   "total_turnover_amount"])
def test_a_missing_amount_is_refused_by_the_callable(engine, field):
    """KNOWN D043 context: the MODEL scores these NaNs Critical (xfails above); the callable
    refuses only because the output row casts int(float(nan)) at rapid_movement.py:83-87.
    The refusal is the doctrine's outcome ('REQUIRED'), so it is pinned; whether one such row
    should take every other alert in the frame down with it is a QUESTION for the owner."""
    account = _account("T-NAN", 10000, 8500, 5, 10000, 300000, 9)
    assert len(engine.evaluate_rapid_movement(**_frames(account, _worked()))) == 1
    account[field] = NAN
    with pytest.raises(ValueError):
        engine.evaluate_rapid_movement(**_frames(account, _worked()))


# ---------------------------------------------------------------- defects

# Each pair is EXACT in decimal: 9208.74 / 10009.50 = 0.92, 7503.03 / 10004.04 = 0.75,
# 30002.37 / 10000.79 = 3, 200015.80 / 10000.79 = 20 (multiply out to check).
@pytest.mark.parametrize("scorer,args,band", [
    (score_value_match, (9208.74, 10009.50), "Critical"),   # r = 0.92 -> ">= 0.92 Critical"
    (score_value_match, (7503.03, 10004.04), "High"),       # r = 0.75 -> not "< 0.75", so High
    (score_velocity, (30002.37, 10000.79), "Medium"),       # r = 3 -> not "< 3", so Medium
    (score_velocity, (200015.80, 10000.79), "Critical"),    # r = 20 -> ">= 20 Critical"
])
@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "DEFECT: framework BA005 cut-lines 'r < 0.75 -> Medium', 'otherwise (>= 0.92) -> Critical' "
    "(L35) and 'r < 3 -> Low', 'otherwise (>= 20) -> Critical' (L25): an exact decimal ratio of "
    "cent-valued amounts is computed in binary float (ba005_risk_model.py:95 and :126) and lands "
    "a hair under the cut-line, scoring the band BELOW -- measured: 9208.74/10009.50 -> 'High', "
    "7503.03/10004.04 -> 'Medium', 30002.37/10000.79 -> 'Low', 200015.80/10000.79 -> 'High'"))
def test_an_exact_decimal_ratio_on_a_cut_line_takes_the_doctrine_band(scorer, args, band):
    assert scorer(*args) == band


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "DEFECT: same float cut-line, end to end: an account whose outbound leg is EXACTLY 92% of the "
    "inbound (9208.74 of 10009.50; framework L35 '>= 0.92 -> Critical') scores value match High "
    "(ba005_risk_model.py:126,131), 77 High instead of 81 Critical, and evaluate_rapid_movement "
    "drops the alert -- measured: AssertionError, alerts ['P-INT'] only"))
def test_an_exact_92_percent_pass_through_alerts(engine):
    # Same shape as PER_RULE['value_match']: 1 h (C), r 10 (H), 5 destinations (H), r 0.92 (C):
    # 31.5+17.5+14+18 = 81 Critical, alerts. P-INT is the integer-amount control (9200/10000).
    cents = _account("P-CENT", 10009.50, 9208.74, 1, 10000, 100000, 5)
    control = PER_RULE["value_match"][0].copy()
    control["account_ref"] = "P-INT"
    control["first_destination_name"] = "Constructed First Onward P-INT"
    alerts = engine.evaluate_rapid_movement(**_frames(control, cents))
    assert len(alerts) >= 1
    assert sorted(alerts["account_ref"]) == ["P-CENT", "P-INT"]
