"""TT-BA008 (night 10, wave C): the BA008 Layering engine against its doctrine.

Oracle, and nothing else: scoring-models/specific/BA008_Layering_Scoring_Framework.md
(F: component cut-lines F:20/25/30/36, weights F:8-13, every input REQUIRED and
total_intermediary_count > 0 F:18/23-24/28/33, midpoints / weighted sum / half-up F:40,
alert at >= 80 F:52-53, worked example LAY019 F:42-50, clean account 15/100 F:52) and
typologies/BA008_Layering.md (T: weights T:106-113, bands 0-29/30-59/60-79/80-100 T:130,
"escalate at or above the threshold" T:144, the doctrine snippet T:168-175). No signed-off
expected-outcome sheet exists for BA008 (wave C); oracle rule R1 (2026-10-21) makes the band
table govern over the snippet. Every expected score below is hand-worked from those numbers
in a comment beside it, or computed in the test from the framework's formula with exact
fractions. Inputs are CONSTRUCTED here: no sample-data file is read and no sample entity's
name is asserted.

Contributions per band (midpoint x weight), from the framework:
    chain depth           30%: L 4.5   M 13.5   H 21    C 27
    intermediary opacity  25%: L 3.75  M 11.25  H 17.5  C 22.5
    jurisdiction hopping  25%: L 3.75  M 11.25  H 17.5  C 22.5
    value fragmentation   20%: L 3     M 9      H 14    C 18

What the engine does NOT do, so no test here pretends it does: it reconstructs no chain.
Hop count, opaque/total intermediaries, secrecy hops and fragment count arrive pre-counted on
the account row (schema.json); the intermediaries frame is read only to require a row per
account. So there is no time window between hops, no amount tolerance and no loop detection
to test (the doctrine T:8-10 says a layering chain has no obligation to close a loop).
Those are recorded as owner QUESTIONS in the package report, not pinned.
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

from ba008_risk_model import (  # noqa: E402
    RiskModelError, band_of, ba008_exposure_score, score_chain_depth,
    score_intermediary_opacity, score_jurisdiction_hopping, score_value_fragmentation,
)

SCENARIO = BASE_DIR / "scenarios" / "layering.py"
NAMES = ("chain_depth", "intermediary_opacity", "jurisdiction_hopping", "value_fragmentation")
BAND_COLS = {n: n + "_band" for n in NAMES}
NAN = float("nan")

# F:8-13 and F:40, as exact fractions so the oracle carries no float error of its own.
WEIGHT = {"chain_depth": Fraction(30, 100), "intermediary_opacity": Fraction(25, 100),
          "jurisdiction_hopping": Fraction(25, 100), "value_fragmentation": Fraction(20, 100)}
MIDPOINT = {"Low": 15, "Medium": 45, "High": 70, "Critical": 90}


def _load():
    spec = spec_from_file_location("tt_ba008_doctrine_layering", SCENARIO)
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


def _account(ref, hops, opaque, total, secrecy, fragments, holder=None):
    return {"customer_name": holder or "Constructed Holder %s" % ref, "account_ref": ref,
            "segment": "Retail", "home_branch": "Constructed Branch",
            "chain_depth": hops, "opaque_intermediary_count": opaque,
            "total_intermediary_count": total, "secrecy_jurisdiction_hops": secrecy,
            "fragment_count": fragments,
            "first_intermediary_name": "Constructed First Hop %s" % ref,
            "second_intermediary_name": "Constructed Second Hop %s" % ref,
            "destination_name": "Constructed Destination %s" % ref}


def _frames(*accounts):
    acc = pd.DataFrame(list(accounts))
    inter = pd.DataFrame([{"destination_name": a["destination_name"], "account_ref": a["account_ref"],
                           "bank": "Constructed Bank", "jurisdiction": "Constructed Jurisdiction",
                           "relationship": "Constructed", "prior_alerts": 0} for a in accounts])
    return {"accounts": acc, "intermediaries": inter}


# The framework worked example LAY019 (F:42-50, T:117-126), constructed: 9 hops (C), 8 of 9
# intermediaries opaque (r 0.889, C), 4 secrecy hops (C), 9 fragments (C):
# 27 + 22.5 + 22.5 + 18 = 90 Critical, alerts.
WORKED = _account("T-WE", 9, 8, 9, 4, 9)


# ---------------------------------------------------------------- check 2: boundaries
# Each cut-line from the framework: exactly at it, just below and just above.

@pytest.mark.parametrize("hops,band", [
    (1, "Low"), (2, "Low"), (3, "Medium"),          # <= 2 Low
    (4, "Medium"), (5, "High"),                     # <= 4 Medium
    (6, "High"), (7, "Critical"), (8, "Critical"),  # <= 6 High, otherwise (>= 7) Critical
])
def test_chain_depth_cut_lines(hops, band):
    # F:20
    assert score_chain_depth(hops) == band


@pytest.mark.parametrize("opaque,band", [
    (19, "Low"), (20, "Medium"), (21, "Medium"),        # r < 0.20 Low
    (44, "Medium"), (45, "High"), (46, "High"),         # r < 0.45 Medium
    (74, "High"), (75, "Critical"), (76, "Critical"),   # r < 0.75 High, otherwise Critical
])
def test_intermediary_opacity_cut_lines(opaque, band):
    # F:25, r = opaque / total over 100 intermediaries
    assert score_intermediary_opacity(opaque, 100) == band


def test_every_exact_opacity_cut_line_bands_up():
    """F:25 is strict ('r < 0.20 -> Low'), so a ratio exactly ON a cut-line takes the higher
    band. The N10-FLOATCUT class (BA002/BA003) misfires when a quotient lands a hair under its
    line; sweep every integer pair up to 200 intermediaries whose EXACT ratio is a cut-line.
    Non-vacuity: the sweep must find each line many times."""
    lines = {Fraction(1, 5): "Medium", Fraction(9, 20): "High", Fraction(3, 4): "Critical"}
    seen = {k: 0 for k in lines}
    for total in range(1, 201):
        for opaque in range(0, total + 1):
            r = Fraction(opaque, total)
            if r in lines:
                seen[r] += 1
                assert score_intermediary_opacity(opaque, total) == lines[r], (opaque, total)
    assert min(seen.values()) >= 10, seen


def test_intermediary_opacity_is_opaque_over_total():
    # F:23 r = opaque / total. 1 of 10 is r 0.10 Low; the inverse (10.0) would be Critical.
    assert score_intermediary_opacity(1, 10) == "Low"


@pytest.mark.parametrize("secrecy,band", [
    (0, "Low"), (1, "Medium"), (2, "High"), (3, "Critical"), (4, "Critical"),  # F:30
])
def test_jurisdiction_hopping_cut_lines(secrecy, band):
    assert score_jurisdiction_hopping(secrecy) == band


@pytest.mark.parametrize("fragments,band", [
    (1, "Low"), (2, "Low"), (3, "Medium"),          # <= 2 Low
    (4, "Medium"), (5, "High"),                     # <= 4 Medium
    (7, "High"), (8, "Critical"), (9, "Critical"),  # <= 7 High, otherwise (>= 8) Critical
])
def test_value_fragmentation_cut_lines(fragments, band):
    # F:36
    assert score_value_fragmentation(fragments) == band


@pytest.mark.parametrize("score,band", [
    (0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
    (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical"),
])
def test_score_band_table(score, band):
    # T:130 Classification: 0-29 Low, 30-59 Medium, 60-79 High, 80-100 Critical
    assert band_of(score) == band


def _framework_score(bands):
    """F:40 by construction: band midpoint x weight, summed exactly, half-up, then T:130."""
    exact = sum(MIDPOINT[bands[n]] * WEIGHT[n] for n in NAMES)
    score = int(exact + Fraction(1, 2))          # half-up (every total here is positive)
    band = "Low" if score <= 29 else "Medium" if score <= 59 else "High" if score <= 79 else "Critical"
    return exact, score, band


ALL_CODES = ["".join(c) for c in itertools.product("LMHC", repeat=4)]


@pytest.mark.parametrize("code", ALL_CODES)
def test_every_band_combination_scores_the_framework_sum(code):
    """All 256 band combinations against the framework's formula in exact arithmetic, so a
    float sum that lands a hair under an x.5 cannot round the wrong way unnoticed."""
    bands = _bands(code)
    exact, score, band = _framework_score(bands)
    got_score, got_band, working = ba008_exposure_score(bands)
    assert (got_score, got_band) == (score, band)
    assert {n: working["components"][n]["band"] for n in NAMES} == bands
    assert working["total"] == pytest.approx(float(exact), abs=1e-9)


@pytest.mark.parametrize("code,score,band", [
    ("CCCC", 90, "Critical"),   # 27+22.5+22.5+18 = 90 (worked example LAY019, F:50)
    ("LLLL", 15, "Low"),        # 4.5+3.75+3.75+3 = 15 (F:52 clean account 15/100)
    ("CHHC", 80, "Critical"),   # 27+17.5+17.5+18 = 80 exactly: the threshold itself
    ("HCCH", 80, "Critical"),   # 21+22.5+22.5+14 = 80 exactly
    ("HHCC", 79, "High"),       # 21+17.5+22.5+18 = 79
    ("CMCC", 79, "High"),       # 27+11.25+22.5+18 = 78.75 -> 79
    ("CCCM", 81, "Critical"),   # 27+22.5+22.5+9 = 81
    ("CCCL", 75, "High"),       # 27+22.5+22.5+3 = 75
    ("LLML", 23, "Low"),        # 4.5+3.75+11.25+3 = 22.5 exactly -> half-up 23 (half-even: 22)
    ("MHHC", 67, "High"),       # 13.5+17.5+17.5+18 = 66.5 exactly -> half-up 67 (half-even: 66)
])
def test_hand_worked_scores(code, score, band):
    got_score, got_band, _w = ba008_exposure_score(_bands(code))
    assert (got_score, got_band) == (score, band)


def test_the_doctrine_snippet_is_implied_by_the_band_table():
    """T:168-175's snippet gates on opacity High/Critical, chain_depth >= 5 and secrecy hops
    >= 2 before the >= 80 rule. R1: the band table governs; this checks the two do not
    disagree -- every combination the framework puts at or above 80 has chain depth >= High
    (>= 5 hops, F:20), opacity >= High and jurisdiction hopping >= High (>= 2, F:30).
    Non-vacuity: ten combinations alert."""
    alerting = [c for c in ALL_CODES if _framework_score(_bands(c))[1] >= 80]
    assert len(alerting) == 10
    for code in alerting:
        assert code[0] in "HC" and code[1] in "HC" and code[2] in "HC", code
        assert ba008_exposure_score(_bands(code))[0] >= 80


def test_alert_threshold_is_inclusive_at_80(engine):
    """F:52-53 / T:144 'at or above'. CHHC scores exactly 80 and alerts; HHCC scores 79 and
    does not -- both in the SAME evaluate call."""
    # 7 hops C, 5 of 10 opaque (r 0.50) H, 2 secrecy hops H, 8 fragments C: 27+17.5+17.5+18 = 80
    at = _account("T-80", 7, 5, 10, 2, 8)
    # 5 hops H, 5 of 10 opaque H, 3 secrecy hops C, 8 fragments C: 21+17.5+22.5+18 = 79
    below = _account("T-79", 5, 5, 10, 3, 8)
    frames = _frames(at, below)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert (scored.loc["T-80", "exposure_score"], scored.loc["T-80", "exposure_band"]) == (80, "Critical")
    assert (scored.loc["T-79", "exposure_score"], scored.loc["T-79", "exposure_band"]) == (79, "High")
    assert list(engine.evaluate_layering(**frames)["account_ref"]) == ["T-80"]


# ---------------------------------------------------------------- check 4: positives / near-misses

def test_worked_example_alerts_90_critical(engine):
    out = engine.evaluate_layering(**_frames(WORKED))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["exposure_score"], row["exposure_band"]) == (90, "Critical")
    assert [row[BAND_COLS[n]] for n in NAMES] == ["Critical"] * 4
    # the evidence T:182-191 says the investigator sees
    assert (row["chain_depth"], row["opaque_intermediary_count"], row["total_intermediary_count"],
            row["secrecy_jurisdiction_hops"], row["fragment_count"]) == (9, 8, 9, 4, 9)
    assert (row["first_intermediary_name"], row["second_intermediary_name"], row["destination_name"]) == \
        ("Constructed First Hop T-WE", "Constructed Second Hop T-WE", "Constructed Destination T-WE")
    assert row["subject_entity_id"] == "T-WE" and row["subject_name"] == "Constructed Holder T-WE"
    assert row["alert_type"] == "BA008_LAYERING"


def test_clean_account_scores_15_and_does_not_alert(engine):
    # F:52: all four Low scores 15/100. 1 hop L, 1 of 10 opaque (r 0.10) L, 0 secrecy L,
    # 1 fragment L. Alerting control in the SAME frame: the worked example, 90 Critical.
    frames = _frames(_account("T-CLEAN", 1, 1, 10, 0, 1), WORKED)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert (scored.loc["T-CLEAN", "exposure_score"], scored.loc["T-CLEAN", "exposure_band"]) == (15, "Low")
    assert list(engine.evaluate_layering(**frames)["account_ref"]) == ["T-WE"]


def test_a_deep_chain_through_identifiable_onshore_counterparties_does_not_alert(engine):
    """T:12-16: the finding is depth AND opacity AND jurisdiction AND fragmentation. A deep,
    fragmented chain (9 hops C, 9 fragments C) through identifiable counterparties (0 of 9
    opaque, L) in no secrecy jurisdiction (0, L): 27+3.75+3.75+18 = 52.5 -> 53 Medium, no
    alert. Control: the worked example."""
    frames = _frames(_account("T-ONSHORE", 9, 0, 9, 0, 9), WORKED)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert (scored.loc["T-ONSHORE", "exposure_score"], scored.loc["T-ONSHORE", "exposure_band"]) == (53, "Medium")
    assert list(engine.evaluate_layering(**frames)["account_ref"]) == ["T-WE"]


# One positive and one near-miss per detection rule (component). The positive sits EXACTLY on
# the component's cut-line; the near-miss moves only that component one step below it.
PER_RULE = {
    # 7 hops (C) with r 0.50 H, 2 secrecy H, 8 fragments C: 27+17.5+17.5+18 = 80 alert;
    #   6 hops (H): 21+17.5+17.5+18 = 74 no alert
    "chain_depth": (_account("P-CD", 7, 5, 10, 2, 8),
                    _account("N-CD", 6, 5, 10, 2, 8), 80, 74, "Critical", "High"),
    # r 0.75 (C) with 5 hops H, 3 secrecy C, 5 fragments H: 21+22.5+22.5+14 = 80 alert;
    #   r 0.74 (H): 21+17.5+22.5+14 = 75 no alert
    "intermediary_opacity": (_account("P-IO", 5, 75, 100, 3, 5),
                             _account("N-IO", 5, 74, 100, 3, 5), 80, 75, "Critical", "High"),
    # 3 secrecy hops (C) with 5 hops H, r 0.75 C, 5 fragments H: 21+22.5+22.5+14 = 80 alert;
    #   2 secrecy hops (H): 21+22.5+17.5+14 = 75 no alert
    "jurisdiction_hopping": (_account("P-JH", 5, 3, 4, 3, 5),
                             _account("N-JH", 5, 3, 4, 2, 5), 80, 75, "Critical", "High"),
    # 8 fragments (C) with 7 hops C, r 0.50 H, 2 secrecy H: 27+17.5+17.5+18 = 80 alert;
    #   7 fragments (H): 27+17.5+17.5+14 = 76 no alert
    "value_fragmentation": (_account("P-VF", 7, 5, 10, 2, 8),
                            _account("N-VF", 7, 5, 10, 2, 7), 80, 76, "Critical", "High"),
    # the Medium line: 3 fragments (M) with 7 hops C, r 0.80 C, 4 secrecy C: 27+22.5+22.5+9 = 81
    #   alert; 2 fragments (L): 27+22.5+22.5+3 = 75 no alert
    "value_fragmentation_medium": (_account("P-VM", 7, 8, 10, 4, 3),
                                   _account("N-VM", 7, 8, 10, 4, 2), 81, 75, "Medium", "Low"),
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
    alerts = engine.evaluate_layering(**frames)
    assert list(alerts["account_ref"]) == [positive["account_ref"]]


def test_each_input_feeds_its_own_component(engine):
    """Distinct values per input, so wiring an input to the wrong component cannot pass:
    3 hops M, 6 of 10 opaque H, 0 secrecy L, 8 fragments C ->
    13.5+17.5+3.75+18 = 52.75 -> 53 Medium."""
    out = engine.score_all(**_frames(_account("T-MIX", 3, 6, 10, 0, 8)))
    row = out.iloc[0]
    assert [row[BAND_COLS[n]] for n in NAMES] == ["Medium", "High", "Low", "Critical"]
    assert (row["exposure_score"], row["exposure_band"]) == (53, "Medium")


def test_alert_row_carries_its_own_working(engine):
    # CHHC: 27+17.5+17.5+18 = 80 Critical
    out = engine.evaluate_layering(**_frames(_account("T-W", 7, 5, 10, 2, 8)))
    assert len(out) == 1
    working = json.loads(out.iloc[0]["risk_components"])
    assert set(working["components"]) == set(NAMES)
    assert working["score"] == 80 and working["band"] == "Critical"
    assert {n: working["components"][n]["weight"] for n in NAMES} == {n: float(WEIGHT[n]) for n in NAMES}


def test_score_all_puts_the_highest_score_first(engine):
    # F:55-57: the fc-10 demo path builds its case from score_all's top row.
    frames = _frames(_account("T-LOW", 1, 1, 10, 0, 1), WORKED)
    assert list(engine.score_all(**frames)["account_ref"]) == ["T-WE", "T-LOW"]


# ---------------------------------------------------------------- required inputs (F:18/23/28/33)

REQUIRED = ("chain_depth", "opaque_intermediary_count", "total_intermediary_count",
            "secrecy_jurisdiction_hops", "fragment_count")


@pytest.mark.parametrize("field", REQUIRED)
def test_a_blank_required_input_is_refused_not_scored_as_zero(engine, field):
    """The sample reader yields '' for a blank cell (dtype=str, keep_default_na=False). A blank
    must refuse, never read as zero hops / zero secrecy hops / zero fragments (all Low). The
    worked example scores first, so the refusal is the blank's doing."""
    account = dict(WORKED)
    assert len(engine.evaluate_layering(**_frames(account))) == 1
    account[field] = ""
    with pytest.raises(ValueError):
        engine.evaluate_layering(**_frames(account))


@pytest.mark.parametrize("field", REQUIRED)
def test_a_none_required_input_is_refused_by_the_model(field):
    # F 'REQUIRED': None is refused by the model's own _require (RiskModelError).
    account = dict(WORKED)
    account[field] = None
    with pytest.raises(RiskModelError):
        score_chain_depth(account["chain_depth"])
        score_intermediary_opacity(account["opaque_intermediary_count"], account["total_intermediary_count"])
        score_jurisdiction_hopping(account["secrecy_jurisdiction_hops"])
        score_value_fragmentation(account["fragment_count"])


@pytest.mark.parametrize("total", [0, 0.0, "0"])
def test_a_zero_intermediary_total_is_refused(total):
    # F:24 total_intermediary_count must be > 0.
    with pytest.raises(RiskModelError):
        score_intermediary_opacity(0, total)


@pytest.mark.parametrize("scorer", [score_chain_depth, score_jurisdiction_hopping, score_value_fragmentation])
def test_a_missing_count_refuses(scorer):
    # F:18/28/33 REQUIRED. NaN is refused (int(float(nan)) raises ValueError).
    with pytest.raises(ValueError):
        scorer(NAN)


@pytest.mark.parametrize("field", ["opaque_intermediary_count", "total_intermediary_count"])
def test_the_callable_refuses_an_account_with_a_missing_intermediary_count(engine, field):
    """End to end, a NaN opacity count is refused -- but only by the DISPLAY cast at
    scenarios/layering.py:86-87 (int(float(nan)) raises), not by the model, which scores it
    Critical (KNOWN D043 below). Control first: 3 hops M, 1 of 10 L, 0 L, 1 L:
    13.5+3.75+3.75+3 = 24 Low, scored, with every input present."""
    account = _account("T-NAN", 3, 1, 10, 0, 1)
    assert engine.score_all(**_frames(account)).iloc[0]["exposure_score"] == 24
    account[field] = NAN
    with pytest.raises(ValueError):
        engine.evaluate_layering(**_frames(account))


# ---------------------------------------------------------------- known items

@pytest.mark.parametrize("args", [(NAN, 10), (8, NAN)])
@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: framework BA008 'Both counts are REQUIRED' "
    "(BA008_Layering_Scoring_Framework.md:23) and the model's own 'missing != zero': a NaN "
    "passes ba008_risk_model.py:60-65 (_require checks None only), every comparison at :97-103 "
    "is False, so opacity scores Critical -- measured: Failed: DID NOT RAISE <class "
    "'ValueError'>. End to end it is refused only by the display cast at scenarios/layering.py:86-87"))
def test_a_missing_intermediary_count_refuses_rather_than_scoring_critical(args):
    assert any(isinstance(a, float) and math.isnan(a) for a in args)
    with pytest.raises(ValueError):
        score_intermediary_opacity(*args)
