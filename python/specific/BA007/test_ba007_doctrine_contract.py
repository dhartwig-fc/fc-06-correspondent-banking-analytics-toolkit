"""TT-BA007 (night 10, wave C): the BA007 Cash Intensive Activity engine against its doctrine.

Oracle, and nothing else: scoring-models/specific/BA007_Cash_Intensive_Activity_Scoring_Framework.md
(F: weights F:8-13; cut-lines cash ratio F:18-21, profile excess F:24-27, deposit regularity
F:30-33, commingling F:36-37; every input REQUIRED F:18/24/30/36; midpoints / weighted sum /
half-up F:41; worked example F:43-51; clean account 15 F:53; alert at >= 80 F:54) and
typologies/BA007_Cash_Intensive_Activity.md (T: weights T:98-105, worked example T:109-119,
bands 0-29/30-59/60-79/80-100 T:122, business logic T:126-134, "escalate at or above" T:134).
No signed-off expected-outcome sheet exists for BA007 (wave C). Oracle rule R1 (2026-10-21):
the band table governs over the doctrine's Python snippet (T:158-165). Every expected score is
hand-worked in a comment beside it, or computed in the test from the framework's formula in
exact fractions. Inputs are CONSTRUCTED here: no sample-data file is read and no sample
entity's name is asserted. The worked example's NUMBERS come from the doctrine (T:113-116).

Contributions per band (midpoint x weight), from the framework:
    cash ratio          35%: L 5.25  M 15.75  H 24.5  C 31.5
    profile excess      25%: L 3.75  M 11.25  H 17.5  C 22.5
    deposit regularity  20%: L 3     M 9      H 14    C 18
    commingling         20%: L 3     M 9      H 14    C 18
Band codes below are in that order, e.g. "CCHH" = cash C, profile C, regularity H, commingling H.
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

from ba007_risk_model import (  # noqa: E402
    band_of, ba007_exposure_score, score_cash_ratio, score_commingling,
    score_deposit_regularity, score_profile_excess,
)

SCENARIO = BASE_DIR / "scenarios" / "cash_intensive_activity.py"
NAMES = ("cash_ratio", "profile_excess", "deposit_regularity", "commingling")
BAND_COLS = {n: n + "_band" for n in NAMES}
NAN = float("nan")

# F:8-13 and F:41, as exact fractions so the oracle carries no float error of its own.
WEIGHT = {"cash_ratio": Fraction(35, 100), "profile_excess": Fraction(25, 100),
          "deposit_regularity": Fraction(20, 100), "commingling": Fraction(20, 100)}
MIDPOINT = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}


def _load():
    spec = spec_from_file_location("tt_ba007_doctrine_cash_intensive_activity", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def engine():
    return _load()


def _bands(code):
    full = {"L": "Low", "M": "Medium", "H": "High", "C": "Critical"}
    return dict(zip(NAMES, (full[c] for c in code)))


def _account(ref, cash, turnover, peer, declared, cv, third_party, total_deposits):
    return {"customer_name": "Constructed Business %s" % ref, "account_ref": ref,
            "segment": "Constructed Segment", "home_branch": "Constructed Branch",
            "cash_deposits_amount": cash, "total_turnover_amount": turnover,
            "peer_norm_cash_ratio": peer, "declared_annual_cash_volume": declared,
            "deposit_cv_pct": cv, "third_party_deposit_amount": third_party,
            "total_deposit_amount": total_deposits,
            "top_depositor_name": "Constructed Depositor %s" % ref,
            "linked_entity_name": "Constructed Linked Entity %s" % ref}


def _frames(*accounts):
    acc = pd.DataFrame(list(accounts))
    dep = pd.DataFrame([{"linked_entity_name": a["linked_entity_name"], "account_ref": a["account_ref"],
                         "bank": "Constructed Bank", "jurisdiction": "GB",
                         "relationship": "Constructed", "prior_alerts": 0} for a in accounts])
    return {"accounts": acc, "depositors": dep}


# The doctrine's worked example (T:113-116, F:47-51), its numbers constructed here:
# 760,000 cash of 820,000 turnover against a 30% norm -> 3.09x C; 760,000 vs 300,000 declared
# r 2.53 C; CV 8% C; 250,000 of 760,000 third-party r 0.329 C: 31.5+22.5+18+18 = 90 Critical.
WORKED = _account("T-WE", 760000, 820000, 0.30, 300000, 8, 250000, 760000)
# F:53 clean: 30,000/100,000 vs 0.25 -> 1.2 L; 30,000 vs 30,000 r 1.0 L; CV 50 L;
# 1,000/30,000 r 0.033 L: 5.25+3.75+3+3 = 15 Low.
CLEAN = _account("T-CLEAN", 30000, 100000, 0.25, 30000, 50, 1000, 30000)


# ---------------------------------------------------------------- check 2: boundaries
# Each cut-line from the framework: exactly at it, just below and just above. Amounts at the
# line are chosen so the quotient is the cut-line's own float (the float cut-line class is
# pinned separately below as KNOWN N10-FLOATCUT).

@pytest.mark.parametrize("cash,band", [
    (32499, "Low"), (32500, "Medium"), (32501, "Medium"),          # excess < 1.3 Low
    (44999, "Medium"), (45000, "High"), (45001, "High"),           # < 1.8 Medium
    (62499, "High"), (62500, "Critical"), (62501, "Critical"),     # < 2.5 High, otherwise Critical
])
def test_cash_ratio_cut_lines(cash, band):
    # F:18-21, excess = (cash / 100,000 turnover) / 0.25 peer norm
    assert score_cash_ratio(cash, 100000, 0.25) == band


def test_cash_ratio_is_scaled_against_the_peer_norm():
    # F:18: the cash share is divided by the norm. 40% of turnover in cash is 4.0x a 10% norm
    # (C) but 0.8x a 50% norm (L): the same share, two bands, decided only by the norm.
    assert score_cash_ratio(40000, 100000, 0.10) == "Critical"
    assert score_cash_ratio(40000, 100000, 0.50) == "Low"


@pytest.mark.parametrize("cash,band", [
    (109999, "Low"), (110000, "Medium"), (110001, "Medium"),       # r < 1.1 Low
    (149999, "Medium"), (150000, "High"), (150001, "High"),        # r < 1.5 Medium
    (219999, "High"), (220000, "Critical"), (220001, "Critical"),  # r < 2.2 High, otherwise Critical
])
def test_profile_excess_cut_lines(cash, band):
    # F:24-27, r = cash / 100,000 declared
    assert score_profile_excess(cash, 100000) == band


@pytest.mark.parametrize("cv,band", [
    (45.01, "Low"), (45, "Low"), (44.99, "Medium"),        # >= 45 Low
    (30.01, "Medium"), (30, "Medium"), (29.99, "High"),    # >= 30 Medium
    (15.01, "High"), (15, "High"), (14.99, "Critical"),    # >= 15 High, otherwise (< 15) Critical
])
def test_deposit_regularity_cut_lines(cv, band):
    # F:30-33 -- LOWER variability is worse
    assert score_deposit_regularity(cv) == band


@pytest.mark.parametrize("third_party,band", [
    (4999, "Low"), (5000, "Medium"), (5001, "Medium"),         # r < 0.05 Low
    (14999, "Medium"), (15000, "High"), (15001, "High"),       # r < 0.15 Medium
    (29999, "High"), (30000, "Critical"), (30001, "Critical"),  # r < 0.30 High, otherwise Critical
])
def test_commingling_cut_lines(third_party, band):
    # F:36-37, r = third_party / 100,000 total deposits
    assert score_commingling(third_party, 100000) == band


@pytest.mark.parametrize("score,band", [
    (0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
    (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical"),
])
def test_score_band_table(score, band):
    # T:122 Classification: 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    assert band_of(score) == band


def _framework_score(bands):
    """F:41 by construction: band midpoint x weight, summed exactly, half-up, then T:122."""
    exact = sum(MIDPOINT[bands[n]] * WEIGHT[n] for n in NAMES)
    score = int(exact + Fraction(1, 2))          # half-up (every total here is positive)
    band = "Low" if score <= 29 else "Medium" if score <= 59 else "High" if score <= 79 else "Critical"
    return exact, score, band


ALL_CODES = ["".join(c) for c in itertools.product("LMHC", repeat=4)]


@pytest.mark.parametrize("code", ALL_CODES)
def test_every_band_combination_scores_the_framework_sum(code):
    """All 256 band combinations against the framework's formula in exact arithmetic."""
    bands = _bands(code)
    exact, score, band = _framework_score(bands)
    got_score, got_band, working = ba007_exposure_score(bands)
    assert (got_score, got_band) == (score, band)
    assert {n: working["components"][n]["band"] for n in NAMES} == bands
    assert working["total"] == pytest.approx(float(exact), abs=1e-9)


@pytest.mark.parametrize("code,score,band", [
    ("CCCC", 90, "Critical"),   # 31.5+22.5+18+18 = 90 (worked example, F:51)
    ("LLLL", 15, "Low"),        # 5.25+3.75+3+3 = 15 (F:53)
    ("HCCC", 83, "Critical"),   # 24.5+22.5+18+18 = 83
    ("CMCC", 79, "High"),       # 31.5+11.25+18+18 = 78.75 -> 79
    ("MCCC", 74, "High"),       # 15.75+22.5+18+18 = 74.25 -> 74
    ("CCMC", 81, "Critical"),   # 31.5+22.5+9+18 = 81
    ("CCCM", 81, "Critical"),   # 31.5+22.5+18+9 = 81
    ("CHHH", 77, "High"),       # 31.5+17.5+14+14 = 77
    ("LMLL", 23, "Low"),        # 5.25+11.25+3+3 = 22.5 exactly -> half-up 23 (half-even 22)
    ("MLLL", 26, "Low"),        # 15.75+3.75+3+3 = 25.5 exactly -> half-up 26
    ("CMHL", 60, "High"),       # 31.5+11.25+14+3 = 59.75 -> 60
])
def test_hand_worked_scores(code, score, band):
    got_score, got_band, _w = ba007_exposure_score(_bands(code))
    assert (got_score, got_band) == (score, band)


def test_half_up_rounding_on_an_exact_half():
    # LMLL: 5.25 + 11.25 + 3 + 3 = 22.5 exactly. Half-up -> 23 (half-even would give 22).
    score, band, working = ba007_exposure_score(_bands("LMLL"))
    assert working["total"] == 22.5
    assert (score, band) == (23, "Low")


def test_the_band_table_governs_the_doctrine_snippet():
    """T:158-165's snippet gates on cash ratio High/Critical, CV <= 20 and commingling >= 0.15.
    R1 (2026-10-21): the band table governs. The framework's band table alerts ten combinations
    (hand-derived from the contributions above), and two of them -- CCMC (CV in [30, 45)) and
    CCCM (commingling in [0.05, 0.15)) -- fall OUTSIDE the snippet. The alert tests below follow
    the band table."""
    alerting = sorted(c for c in ALL_CODES if _framework_score(_bands(c))[1] >= 80)
    assert alerting == sorted(["HCCC", "CHHC", "CHCH", "CHCC", "CCMC", "CCHH", "CCHC",
                               "CCCM", "CCCH", "CCCC"])
    for code in alerting:
        assert code[0] in "HC", code                       # the snippet's cash-ratio gate holds
        assert ba007_exposure_score(_bands(code))[0] >= 80


def test_alert_threshold_is_inclusive_at_80(engine):
    """F:54 '>= 80' / T:134 'at or above'. A CHHC account scores 81 and a CMCC account 79;
    80 itself is not reachable by any combination, so 'at or above' is checked through the
    filter at its nearest pair -- both in the SAME evaluate call."""
    # CHHC: 120,000/200,000 vs 0.2 = 3.0 C; 120,000 vs 80,000 r 1.5 H; CV 20 H; 30,000/100,000 C
    #   31.5+17.5+14+18 = 81 Critical, alerts
    at = _account("T-81", 120000, 200000, 0.2, 80000, 20, 30000, 100000)
    # CMCC: 3.0 C; 120,000 vs 100,000 r 1.2 M; CV 8 C; 0.30 C: 31.5+11.25+18+18 = 78.75 -> 79
    below = _account("T-79", 120000, 200000, 0.2, 100000, 8, 30000, 100000)
    frames = _frames(at, below)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert (scored.loc["T-81", "exposure_score"], scored.loc["T-81", "exposure_band"]) == (81, "Critical")
    assert (scored.loc["T-79", "exposure_score"], scored.loc["T-79", "exposure_band"]) == (79, "High")
    assert list(engine.evaluate_cash_intensive_activity(**frames)["account_ref"]) == ["T-81"]


def test_the_alert_filter_is_at_or_above_not_above(engine, monkeypatch):
    """The 80 itself, through the governed filter: no band combination totals 80, so the
    threshold is lowered to each account's own score to prove the comparison is inclusive.
    81 (CHHC) at threshold 81 alerts; 79 (CMCC) does not."""
    at = _account("T-81", 120000, 200000, 0.2, 80000, 20, 30000, 100000)
    below = _account("T-79", 120000, 200000, 0.2, 100000, 8, 30000, 100000)
    monkeypatch.setattr(engine, "ALERT_THRESHOLD", 81)
    assert list(engine.evaluate_cash_intensive_activity(**_frames(at, below))["account_ref"]) == ["T-81"]


# ---------------------------------------------------------------- check 4: positives / near-misses

def test_worked_example_alerts_90_critical(engine):
    out = engine.evaluate_cash_intensive_activity(**_frames(WORKED))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["exposure_score"], row["exposure_band"]) == (90, "Critical")
    assert [row[BAND_COLS[n]] for n in NAMES] == ["Critical"] * 4
    # the evidence T:172-179 says the investigator sees
    assert (row["cash_deposits_amount"], row["total_turnover_amount"], row["peer_norm_cash_ratio"]) == \
        (760000, 820000, 0.30)
    assert (row["declared_annual_cash_volume"], row["deposit_cv_pct"]) == (300000, 8)
    assert (row["third_party_deposit_amount"], row["total_deposit_amount"]) == (250000, 760000)
    assert row["linked_entity_name"] == "Constructed Linked Entity T-WE"
    assert row["subject_entity_id"] == "T-WE" and row["subject_name"] == "Constructed Business T-WE"
    assert row["alert_type"] == "BA007_CASH_INTENSIVE_ACTIVITY"


def test_clean_account_scores_15_and_does_not_alert(engine):
    # F:53 all four Low scores 15/100. Alerting control in the SAME frame: the worked example.
    frames = _frames(CLEAN, WORKED)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert (scored.loc["T-CLEAN", "exposure_score"], scored.loc["T-CLEAN", "exposure_band"]) == (15, "Low")
    assert list(engine.evaluate_cash_intensive_activity(**frames)["account_ref"]) == ["T-WE"]


def test_a_genuine_cash_business_at_its_peer_norm_does_not_alert(engine):
    """T:7 'The tell is not the presence of cash'. A business banking 90% of its turnover in
    cash, AT its own 90% peer norm (excess 1.0, L), within its declared volume (r 1.0, L),
    noisy (CV 60, L), with none of it from third parties (r 0, L): 15 Low, no alert. Control:
    the worked example in the same call."""
    genuine = _account("T-CASHCO", 90000, 100000, 0.90, 90000, 60, 0, 90000)
    frames = _frames(genuine, WORKED)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert (scored.loc["T-CASHCO", "exposure_score"], scored.loc["T-CASHCO", "cash_ratio_band"]) == (15, "Low")
    assert list(engine.evaluate_cash_intensive_activity(**frames)["account_ref"]) == ["T-WE"]


# One positive and one near-miss per detection rule (component cut-line). The positive sits ON
# the cut-line (regularity: just inside it); the near-miss moves only that component one band
# down, and the exposure score drops below 80. The Low/Medium lines of cash ratio and profile
# excess cannot move an alert (cash M caps at 74, profile M at 79) and are covered above.
PER_RULE = {
    # cash 2.5 (C): 62,500/100,000 vs 0.25; declared 25,000 r 2.5 C; CV 8 C; 20,000/100,000 H
    #   CCCH 31.5+22.5+18+14 = 86;  62,499 -> 2.49996 H: HCCH 24.5+22.5+18+14 = 79
    "cash_ratio_2_5": ("cash_ratio",
                       _account("P-CR25", 62500, 100000, 0.25, 25000, 8, 20000, 100000),
                       _account("N-CR25", 62499, 100000, 0.25, 25000, 8, 20000, 100000),
                       86, 79, "Critical", "High"),
    # cash 1.8 (H): 45,000/100,000 vs 0.25; declared 20,000 r 2.25 C; CV 8 C; 0.30 C
    #   HCCC 83;  44,999 -> M: MCCC 15.75+22.5+18+18 = 74.25 -> 74
    "cash_ratio_1_8": ("cash_ratio",
                       _account("P-CR18", 45000, 100000, 0.25, 20000, 8, 30000, 100000),
                       _account("N-CR18", 44999, 100000, 0.25, 20000, 8, 30000, 100000),
                       83, 74, "High", "Medium"),
    # profile 2.2 (C): 110,000 vs 50,000; cash 110,000/200,000 vs 0.2 = 2.75 C; CV 20 H; 0.20 H
    #   CCHH 31.5+22.5+14+14 = 82;  declared 50,001 -> r 2.19996 H: CHHH 77
    "profile_excess_2_2": ("profile_excess",
                           _account("P-PE22", 110000, 200000, 0.2, 50000, 20, 20000, 100000),
                           _account("N-PE22", 110000, 200000, 0.2, 50001, 20, 20000, 100000),
                           82, 77, "Critical", "High"),
    # profile 1.5 (H): 120,000 vs 80,000; cash 3.0 C; CV 8 C; 0.30 C
    #   CHCC 31.5+17.5+18+18 = 85;  declared 80,001 -> M: CMCC 78.75 -> 79
    "profile_excess_1_5": ("profile_excess",
                           _account("P-PE15", 120000, 200000, 0.2, 80000, 8, 30000, 100000),
                           _account("N-PE15", 120000, 200000, 0.2, 80001, 8, 30000, 100000),
                           85, 79, "High", "Medium"),
    # regularity CV 14.99 (C): cash 3.0 C; r 1.5 H; 0.20 H
    #   CHCH 31.5+17.5+18+14 = 81;  CV 15 -> H: CHHH 77
    "deposit_regularity_15": ("deposit_regularity",
                              _account("P-DR15", 120000, 200000, 0.2, 80000, 14.99, 20000, 100000),
                              _account("N-DR15", 120000, 200000, 0.2, 80000, 15, 20000, 100000),
                              81, 77, "Critical", "High"),
    # regularity CV 29.99 (H): cash 3.0 C; 120,000 vs 50,000 r 2.4 C; 0.20 H
    #   CCHH 82;  CV 30 -> M: CCMH 31.5+22.5+9+14 = 77
    "deposit_regularity_30": ("deposit_regularity",
                              _account("P-DR30", 120000, 200000, 0.2, 50000, 29.99, 20000, 100000),
                              _account("N-DR30", 120000, 200000, 0.2, 50000, 30, 20000, 100000),
                              82, 77, "High", "Medium"),
    # regularity CV 44.99 (M): cash 3.0 C; r 2.4 C; 0.30 C -- CV above the snippet's 20 (R1)
    #   CCMC 81;  CV 45 -> L: CCLC 31.5+22.5+3+18 = 75
    "deposit_regularity_45": ("deposit_regularity",
                              _account("P-DR45", 120000, 200000, 0.2, 50000, 44.99, 30000, 100000),
                              _account("N-DR45", 120000, 200000, 0.2, 50000, 45, 30000, 100000),
                              81, 75, "Medium", "Low"),
    # commingling 0.30 (C): cash 3.0 C; r 1.5 H; CV 20 H
    #   CHHC 81;  29,999 -> H: CHHH 77
    "commingling_0_30": ("commingling",
                         _account("P-CM30", 120000, 200000, 0.2, 80000, 20, 30000, 100000),
                         _account("N-CM30", 120000, 200000, 0.2, 80000, 20, 29999, 100000),
                         81, 77, "Critical", "High"),
    # commingling 0.15 (H): cash 3.0 C; r 2.4 C; CV 20 H
    #   CCHH 82;  14,999 -> M: CCHM 77
    "commingling_0_15": ("commingling",
                         _account("P-CM15", 120000, 200000, 0.2, 50000, 20, 15000, 100000),
                         _account("N-CM15", 120000, 200000, 0.2, 50000, 20, 14999, 100000),
                         82, 77, "High", "Medium"),
    # commingling 0.05 (M): cash 3.0 C; r 2.4 C; CV 8 C -- below the snippet's 0.15 (R1)
    #   CCCM 81;  4,999 -> L: CCCL 31.5+22.5+18+3 = 75
    "commingling_0_05": ("commingling",
                         _account("P-CM05", 120000, 200000, 0.2, 50000, 8, 5000, 100000),
                         _account("N-CM05", 120000, 200000, 0.2, 50000, 8, 4999, 100000),
                         81, 75, "Medium", "Low"),
}


@pytest.mark.parametrize("rule", sorted(PER_RULE))
def test_positive_and_near_miss_per_rule(engine, rule):
    component, positive, near, pos_score, near_score, pos_band, near_band = PER_RULE[rule]
    col = BAND_COLS[component]
    frames = _frames(positive, near)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    p, n = positive["account_ref"], near["account_ref"]
    assert (scored.loc[p, col], scored.loc[n, col]) == (pos_band, near_band)
    # only the rule's component differs between the pair
    for other in NAMES:
        if other != component:
            assert scored.loc[p, BAND_COLS[other]] == scored.loc[n, BAND_COLS[other]], other
    assert (scored.loc[p, "exposure_score"], scored.loc[p, "exposure_band"]) == (pos_score, "Critical")
    assert (scored.loc[n, "exposure_score"], scored.loc[n, "exposure_band"]) == (near_score, "High")
    assert list(engine.evaluate_cash_intensive_activity(**frames)["account_ref"]) == [p]


def test_each_input_feeds_its_own_component(engine):
    """Denominators per F:18/24/36, with inputs chosen so a swapped denominator changes a band:
    cash 40,000 / turnover 80,000 = 0.5 vs 0.25 -> 2.0 H (over total deposits 100,000 it would
    be 1.6 M); 40,000 vs 30,000 declared r 1.33 M (over turnover 0.5 L); CV 10 C; third-party
    3,000 / total deposits 100,000 r 0.03 L (over cash deposits 0.075 M).
    HMCL: 24.5+11.25+18+3 = 56.75 -> 57 Medium."""
    out = engine.score_all(**_frames(_account("T-MIX", 40000, 80000, 0.25, 30000, 10, 3000, 100000)))
    row = out.iloc[0]
    assert [row[BAND_COLS[n]] for n in NAMES] == ["High", "Medium", "Critical", "Low"]
    assert (row["exposure_score"], row["exposure_band"]) == (57, "Medium")


def test_half_up_end_to_end(engine):
    # LMLL: 30,000/100,000 vs 0.25 = 1.2 L; 30,000 vs 25,000 r 1.2 M; CV 50 L; 1,000/100,000 L
    #   5.25+11.25+3+3 = 22.5 -> 23 Low (half-even would give 22)
    row = engine.score_all(**_frames(_account("T-HALF", 30000, 100000, 0.25, 25000, 50, 1000, 100000))).iloc[0]
    assert (row["exposure_score"], row["exposure_band"]) == (23, "Low")


def test_alert_row_carries_its_own_working(engine):
    out = engine.evaluate_cash_intensive_activity(**_frames(WORKED))
    working = json.loads(out.iloc[0]["risk_components"])
    assert set(working["components"]) == set(NAMES)
    assert working["score"] == 90 and working["band"] == "Critical"
    assert {n: working["components"][n]["weight"] for n in NAMES} == {n: float(WEIGHT[n]) for n in NAMES}


def test_score_all_puts_the_highest_score_first(engine):
    # F:56-58: the fc-10 demo path builds its case from score_all's top row.
    frames = _frames(CLEAN, WORKED)
    assert list(engine.score_all(**frames)["account_ref"]) == ["T-WE", "T-CLEAN"]


# ---------------------------------------------------------------- required inputs (F:18/24/30/36)

REQUIRED = ("cash_deposits_amount", "total_turnover_amount", "peer_norm_cash_ratio",
            "declared_annual_cash_volume", "deposit_cv_pct", "third_party_deposit_amount",
            "total_deposit_amount")


@pytest.mark.parametrize("field", REQUIRED)
def test_a_blank_required_input_is_refused_not_scored_as_zero(engine, field):
    """The sample reader yields '' for a blank cell (dtype=str, keep_default_na=False). A blank
    must refuse, never read as zero (a zero CV would score Critical; zero third-party Low).
    The worked example alerts first, so the refusal is the blank's doing."""
    account = dict(WORKED)
    assert len(engine.evaluate_cash_intensive_activity(**_frames(account))) == 1
    account[field] = ""
    with pytest.raises(ValueError):
        engine.evaluate_cash_intensive_activity(**_frames(account))


@pytest.mark.parametrize("scorer,args", [
    (score_cash_ratio, ("", 100000, 0.25)), (score_cash_ratio, (30000, "", 0.25)),
    (score_cash_ratio, (30000, 100000, "")), (score_profile_excess, ("", 100000)),
    (score_profile_excess, (30000, "")), (score_deposit_regularity, ("",)),
    (score_commingling, ("", 100000)), (score_commingling, (1000, "")),
])
def test_the_model_refuses_a_blank_input_itself(scorer, args):
    """F:18/24/30/36 REQUIRED, in the model, not only at the scenario's display casts: a blank
    is refused by each component scorer. Control: the same scorer with the blank filled."""
    filled = tuple(30000 if a == "" else a for a in args)
    filled = (50,) if scorer is score_deposit_regularity else filled
    assert scorer(*filled) in ("Low", "Medium", "High", "Critical")
    with pytest.raises(ValueError):
        scorer(*args)


@pytest.mark.parametrize("field", ["cash_deposits_amount", "total_turnover_amount",
                                   "declared_annual_cash_volume", "third_party_deposit_amount",
                                   "total_deposit_amount"])
def test_a_missing_amount_is_refused_end_to_end(engine, field):
    """End to end a NaN AMOUNT is refused -- but only by the DISPLAY cast at
    scenarios/cash_intensive_activity.py:85-91 (int(float(nan)) raises), not by the model.
    The clean account scores 15 with every input present."""
    account = dict(CLEAN)
    assert engine.score_all(**_frames(account)).iloc[0]["exposure_score"] == 15
    account[field] = NAN
    with pytest.raises(ValueError):
        engine.evaluate_cash_intensive_activity(**_frames(account))


# ---------------------------------------------------------------- known items

@pytest.mark.parametrize("field", ["peer_norm_cash_ratio", "deposit_cv_pct"])
@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: framework BA007 'All three inputs are REQUIRED' / 'deposit_cv_pct is "
    "REQUIRED' (BA007_Cash_Intensive_Activity_Scoring_Framework.md:18-19,30): a NaN passes "
    "ba007_risk_model.py:61-66 (_require checks None only), every comparison at :89-95 / "
    ":121-127 is False, so the component scores Critical, and unlike the amounts these two are "
    "displayed through float() not int(float()) (scenarios/cash_intensive_activity.py:87,89), so "
    "nothing refuses end to end. Measured effect: the account scores 90 Critical and ALERTS "
    "(64 / 75 with the value present) -- Failed: DID NOT RAISE <class 'ValueError'>"))
def test_a_missing_norm_or_cv_is_refused_rather_than_alerting(engine, field):
    # Present: peer 0.90 -> 120,000/200,000 / 0.9 = 0.67 L (LCCC 5.25+58.5 = 63.75 -> 64), or
    # CV 50 L (CCLC 31.5+22.5+3+18 = 75). Neither alerts.
    account = _account("T-NAN", 120000, 200000, 0.90 if field == "peer_norm_cash_ratio" else 0.2,
                       50000, 50 if field == "deposit_cv_pct" else 8, 30000, 100000)
    assert list(engine.evaluate_cash_intensive_activity(**_frames(account, WORKED))["account_ref"]) == ["T-WE"]
    account[field] = NAN
    assert math.isnan(account[field])
    with pytest.raises(ValueError):
        engine.evaluate_cash_intensive_activity(**_frames(account, WORKED))


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "KNOWN N10-FLOATCUT, cited: framework BA007 'excess < 1.8 -> Medium, < 2.5 -> High' "
    "(BA007_Cash_Intensive_Activity_Scoring_Framework.md:21): 36,000 cash of 100,000 turnover "
    "against a 0.20 norm is excess 1.8 exactly, but ba007_risk_model.py:88-93 compares the "
    "float (0.36 / 0.2 = 1.7999999999999998), bands it Medium, so the account scores 74 and "
    "does not alert -- measured: AssertionError, alert set ['P-EXACT'] (the 0.25-norm control) "
    "instead of ['P-EXACT', 'P-FLOAT']. Whole dollars suffice here: the ratio is two divisions"))
def test_an_exact_1_8_cash_excess_alerts(engine):
    # HCCC 24.5+22.5+18+18 = 83 for both: declared 15,000 (r 3.0 / 2.4, C), CV 8 C, 0.30 C
    exact = _account("P-EXACT", 45000, 100000, 0.25, 15000, 8, 30000, 100000)   # 0.45/0.25 = 1.8
    floaty = _account("P-FLOAT", 36000, 100000, 0.20, 15000, 8, 30000, 100000)  # 0.36/0.20 = 1.8
    assert Fraction(36000, 100000) / Fraction("0.20") == Fraction("1.8")
    frames = _frames(exact, floaty)
    assert len(engine.score_all(**frames)) == 2
    assert sorted(engine.evaluate_cash_intensive_activity(**frames)["account_ref"]) == ["P-EXACT", "P-FLOAT"]
