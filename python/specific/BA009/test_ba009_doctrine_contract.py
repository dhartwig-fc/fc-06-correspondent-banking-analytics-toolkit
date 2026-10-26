"""TT-BA009 (night 10, wave C): the BA009 Transaction Laundering engine against its doctrine.

Oracle, and nothing else: scoring-models/specific/BA009_Transaction_Laundering_Scoring_Framework.md
(components and weights L8-13, cut-lines L17-35, midpoints / half-up / boundary at 80 L39,
alert threshold >= 80 L52, all-Low clean merchant 15/100 L51, every input REQUIRED),
typologies/BA009_Transaction_Laundering.md (bands 0-29/30-59/60-79/80-100 L125, worked example
L112-121, Business Logic L131-138) and oracle rule R1 (the band table governs over the
doctrine's illustrative Python snippet, L163-168). No signed-off expected-outcome sheet exists
for BA009. Every expected score below is hand-worked from those numbers in a comment beside
it. Inputs are CONSTRUCTED here: no sample-data file is read and no sample entity's name is
asserted.

Contributions per band (midpoint x weight), from the framework:
    volume profile mismatch    30%: L 4.5   M 13.5   H 21    C 27
    third-party indicators     25%: L 3.75  M 11.25  H 17.5  C 22.5
    MCC inconsistency          25%: L 3.75  M 11.25  H 17.5  C 22.5
    refund/chargeback anomaly  20%: L 3     M 9      H 14    C 18
"""

from __future__ import annotations

import json
import math
import sys
from decimal import ROUND_HALF_UP, Decimal
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path

import pandas as pd
import pytest

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from ba009_risk_model import (  # noqa: E402
    band_of, ba009_exposure_score, score_mcc_inconsistency, score_refund_chargeback_anomaly,
    score_third_party_indicators, score_volume_profile_mismatch,
)

SCENARIO = BASE_DIR / "scenarios" / "transaction_laundering.py"
NAMES = ("volume_profile_mismatch", "third_party_indicators", "mcc_inconsistency",
         "refund_chargeback_anomaly")
BAND_COLS = {n: n + "_band" for n in NAMES}
FULL = {"L": "Low", "M": "Medium", "H": "High", "C": "Critical"}
#: framework L8-13 and L39, written out here (never imported from the engine)
DOCTRINE_WEIGHTS = (Decimal("0.30"), Decimal("0.25"), Decimal("0.25"), Decimal("0.20"))
DOCTRINE_MIDPOINTS = {"L": 15, "M": 45, "H": 70, "C": 90}
NUMERIC_INPUTS = ("processed_card_volume", "declared_business_volume", "unrelated_merchant_count",
                  "mcc_mismatched_txn_count", "total_txn_count", "refund_chargeback_amount",
                  "total_processed_amount")


def _load():
    spec = spec_from_file_location("tt_ba009_doctrine_transaction_laundering", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def engine():
    return _load()


def _bands(code):
    """'CHHC' -> the four component bands in framework order."""
    return dict(zip(NAMES, (FULL[c] for c in code)))


def _doctrine_score(code):
    total = sum(Decimal(DOCTRINE_MIDPOINTS[b]) * w for b, w in zip(code, DOCTRINE_WEIGHTS))
    return total, int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _merchant(ref, processed, declared, unrelated, mismatched, txns, returned, total_processed):
    return {"customer_name": "Constructed Merchant %s" % ref, "account_ref": ref,
            "segment": "Constructed Segment", "home_branch": "Constructed Branch",
            "processed_card_volume": processed, "declared_business_volume": declared,
            "unrelated_merchant_count": unrelated,
            "mcc_mismatched_txn_count": mismatched, "total_txn_count": txns,
            "refund_chargeback_amount": returned, "total_processed_amount": total_processed,
            "processor_name": "Constructed Processor %s" % ref,
            "hidden_merchant_name": "Constructed Hidden Merchant %s" % ref,
            "linked_individual_id": "CP-%s" % ref,
            "linked_individual_name": "Constructed Principal %s" % ref}


def _frames(*merchants):
    proc = pd.DataFrame([{"processor_name": m["processor_name"], "account_ref": m["account_ref"],
                          "bank": "Constructed Bank", "jurisdiction": "GB",
                          "relationship": "Card acquiring processor", "prior_alerts": 0}
                         for m in merchants])
    return {"merchants": pd.DataFrame(list(merchants)), "processors": proc}


def _worked(ref="T-WE"):
    # Framework worked example (L41-49): 1,120,000 processed vs 350,000 declared (r 3.20 C),
    # 8 unrelated sub-merchants (C), 1,100 of 2,000 mismatched (r 0.55 C), 156,800 of
    # 1,120,000 returned (r 0.14 C): 27+22.5+22.5+18 = 90 Critical.
    return _merchant(ref, 1120000, 350000, 8, 1100, 2000, 156800, 1120000)


# ---------------------------------------------------------------- check 2: boundaries
# Each cut-line from the framework (L20, L27, L31, L35): exactly at it, just below, just above.

@pytest.mark.parametrize("processed,band", [
    (129999, "Low"), (130000, "Medium"), (130001, "Medium"),          # r < 1.3 Low
    (179999, "Medium"), (180000, "High"), (180001, "High"),           # r < 1.8 Medium
    (249999, "High"), (250000, "Critical"), (250001, "Critical"),     # r < 2.5 High, else Critical
])
def test_volume_profile_mismatch_cut_lines(processed, band):
    assert score_volume_profile_mismatch(processed, 100000) == band


def test_volume_profile_mismatch_is_processed_over_declared():
    # r = 300000/100000 = 3.0 Critical; the inverse (0.33) would be Low.
    assert score_volume_profile_mismatch(300000, 100000) == "Critical"
    assert score_volume_profile_mismatch(100000, 300000) == "Low"


@pytest.mark.parametrize("count,band", [
    (0, "Low"), (1, "Low"), (2, "Medium"),          # n <= 1 Low
    (3, "Medium"), (4, "High"),                     # n <= 3 Medium
    (6, "High"), (7, "Critical"), (8, "Critical"),  # n <= 6 High, otherwise (>= 7) Critical
])
def test_third_party_indicators_cut_lines(count, band):
    assert score_third_party_indicators(count) == band


@pytest.mark.parametrize("mismatched,band", [
    (99, "Low"), (100, "Medium"), (101, "Medium"),          # r < 0.10 Low
    (249, "Medium"), (250, "High"), (251, "High"),          # r < 0.25 Medium
    (449, "High"), (450, "Critical"), (451, "Critical"),    # r < 0.45 High, else Critical
])
def test_mcc_inconsistency_cut_lines(mismatched, band):
    assert score_mcc_inconsistency(mismatched, 1000) == band


def test_mcc_inconsistency_is_mismatched_over_total():
    # r = 50/1000 = 0.05 Low; the inverse (20) would be Critical.
    assert score_mcc_inconsistency(50, 1000) == "Low"
    assert score_mcc_inconsistency(1000, 2000) == "Critical"      # r = 0.50


@pytest.mark.parametrize("returned,band", [
    (1999, "Low"), (2000, "Medium"), (2001, "Medium"),        # r < 0.02 Low
    (4999, "Medium"), (5000, "High"), (5001, "High"),         # r < 0.05 Medium
    (9999, "High"), (10000, "Critical"), (10001, "Critical"),  # r < 0.10 High, else Critical
])
def test_refund_chargeback_anomaly_cut_lines(returned, band):
    assert score_refund_chargeback_anomaly(returned, 100000) == band


def test_refund_chargeback_anomaly_is_returned_over_processed():
    # r = 1000/100000 = 0.01 Low; the inverse (100) would be Critical.
    assert score_refund_chargeback_anomaly(1000, 100000) == "Low"


@pytest.mark.parametrize("score,band", [
    (0, "Low"), (29, "Low"), (30, "Medium"), (59, "Medium"),
    (60, "High"), (79, "High"), (80, "Critical"), (100, "Critical"),
])
def test_score_band_table(score, band):
    # typologies/BA009_Transaction_Laundering.md L125
    assert band_of(score) == band


@pytest.mark.parametrize("code,score,band", [
    ("CCCC", 90, "Critical"),   # 27+22.5+22.5+18 = 90 (framework worked example)
    ("LLLL", 15, "Low"),        # 4.5+3.75+3.75+3 = 15 (framework L51)
    ("HCCH", 80, "Critical"),   # 21+22.5+22.5+14 = 80: exactly on the boundary
    ("CMCC", 79, "High"),       # 27+11.25+22.5+18 = 78.75 -> 79
    ("CCCM", 81, "Critical"),   # 27+22.5+22.5+9 = 81
    ("CHHC", 80, "Critical"),   # 27+17.5+17.5+18 = 80
    ("CLLL", 38, "Medium"),     # 27+3.75+3.75+3 = 37.5 -> 38 (half-up)
    ("MMMM", 45, "Medium"),
    ("HHHH", 70, "High"),
])
def test_weighted_midpoint_score(code, score, band):
    got_score, got_band, working = ba009_exposure_score(_bands(code))
    assert (got_score, got_band) == (score, band)
    assert len(working["components"]) == 4


def test_every_band_combination_scores_as_the_framework_says():
    """All 256 combinations: midpoint x weight (framework L8-13, L39), summed in exact decimal,
    half-up once. Catches a weight, a midpoint or a rounding rule drifting anywhere."""
    seen = 0
    for code in ("".join(c) for c in product("LMHC", repeat=4)):
        _total, expected = _doctrine_score(code)
        got_score, got_band, _w = ba009_exposure_score(_bands(code))
        assert (code, got_score, got_band) == (code, expected, band_of(expected))
        seen += 1
    assert seen == 256


def test_the_illustrative_snippet_is_implied_by_the_band_table():
    """R1: the band table governs. The doctrine's snippet (typology L163-168) also asks for a
    High/Critical volume band, >= 4 unrelated merchants and an MCC ratio >= 0.25. Under the
    framework's weights every combination reaching 80 already has all three, so the score
    alone is the doctrine's alert rule: hand-checked, the best combination with any one of
    them below High is CMCC/CCMC = 78.75 -> 79 or MCCC = 76.5 -> 77."""
    alerting = [c for c in ("".join(x) for x in product("LMHC", repeat=4))
                if ba009_exposure_score(_bands(c))[0] >= 80]
    assert len(alerting) == 10
    for code in alerting:
        assert code[0] in "HC" and code[1] in "HC" and code[2] in "HC", code


def test_half_up_rounding_on_an_exact_half():
    # LLML: 4.5 + 3.75 + 11.25 + 3 = 22.5 exactly. Half-up -> 23 (half-even would give 22).
    score, band, working = ba009_exposure_score(_bands("LLML"))
    assert working["total"] == 22.5
    assert (score, band) == (23, "Low")


def test_rounding_happens_once_and_cannot_lift_a_79_to_an_alert(engine):
    # CMCC: 27 + 11.25 + 22.5 + 18 = 78.75 -> half-up 79 High: below the >= 80 boundary.
    # r 300000/100000 = 3 (C); 3 unrelated (M); 500/1000 = 0.5 (C); 15000/100000 = 0.15 (C).
    # In the SAME frame, an alerting control (the worked example, 90).
    t = _merchant("T-7875", 300000, 100000, 3, 500, 1000, 15000, 100000)
    frames = _frames(t, _worked())
    scored = engine.score_all(**frames).set_index("account_ref")
    assert (scored.loc["T-7875", "exposure_score"], scored.loc["T-7875", "exposure_band"]) == (79, "High")
    assert json.loads(scored.loc["T-7875", "risk_components"])["total"] == 78.75
    assert list(engine.evaluate_transaction_laundering(**frames)["account_ref"]) == ["T-WE"]


def test_alert_threshold_is_inclusive_at_80(engine):
    # HCCH scores exactly 80 (21+22.5+22.5+14): framework L52 'Alert threshold: >= 80'.
    # r 200000/100000 = 2 (H); 7 unrelated (C); 450/1000 = 0.45 (C); 5000/100000 = 0.05 (H).
    # CMCC (79, above) in the same frame does not alert.
    t80 = _merchant("T-80", 200000, 100000, 7, 450, 1000, 5000, 100000)
    t79 = _merchant("T-79", 300000, 100000, 3, 500, 1000, 15000, 100000)
    frames = _frames(t80, t79)
    scored = engine.score_all(**frames).set_index("account_ref")
    assert scored.loc["T-80", "exposure_score"] == 80 and scored.loc["T-79", "exposure_score"] == 79
    assert list(engine.evaluate_transaction_laundering(**frames)["account_ref"]) == ["T-80"]


# ---------------------------------------------------------------- check 4: positives / near-misses

def test_worked_example_alerts_90_critical(engine):
    out = engine.evaluate_transaction_laundering(**_frames(_worked()))
    assert len(out) == 1
    row = out.iloc[0]
    assert (row["exposure_score"], row["exposure_band"]) == (90, "Critical")
    assert [row[BAND_COLS[n]] for n in NAMES] == ["Critical"] * 4
    assert (row["processed_card_volume"], row["declared_business_volume"]) == (1120000, 350000)
    assert (row["unrelated_merchant_count"], row["mcc_mismatched_txn_count"],
            row["total_txn_count"]) == (8, 1100, 2000)
    assert (row["refund_chargeback_amount"], row["total_processed_amount"]) == (156800, 1120000)
    assert row["subject_entity_id"] == "T-WE"
    assert row["processor_name"] == "Constructed Processor T-WE"
    assert row["hidden_merchant_name"] == "Constructed Hidden Merchant T-WE"
    assert row["linked_individual_id"] == "CP-T-WE"


def test_clean_merchant_scores_15_and_does_not_alert(engine):
    # Framework L51: all four Low scores 15/100. r 1.0 (L), 1 unrelated (L), 50/1000 = 0.05 (L),
    # 1000/100000 = 0.01 (L). Alerting control in the SAME frame.
    frames = _frames(_merchant("T-CLEAN", 100000, 100000, 1, 50, 1000, 1000, 100000), _worked())
    scored = engine.score_all(**frames).set_index("account_ref")
    assert len(scored) == 2
    assert (scored.loc["T-CLEAN", "exposure_score"], scored.loc["T-CLEAN", "exposure_band"]) == (15, "Low")
    assert list(engine.evaluate_transaction_laundering(**frames)["account_ref"]) == ["T-WE"]


# One positive and one near-miss per detection rule (component). The positive sits EXACTLY on the
# component's Critical cut-line; the near-miss moves only that component just under it (High).
PER_RULE = {
    # r 250000/100000 = 2.5 (C), 7 (C), 400/1000 = 0.40 (H), 10000/100000 = 0.10 (C):
    #   27+22.5+17.5+18 = 85 alert;   r 2.49999 (H): 21+22.5+17.5+18 = 79 no alert
    "volume_profile_mismatch": (_merchant("P-VO", 250000, 100000, 7, 400, 1000, 10000, 100000),
                                _merchant("N-VO", 249999, 100000, 7, 400, 1000, 10000, 100000), 85, 79),
    # 7 unrelated (C), r 2.0 (H), 450/1000 (C), 5000/100000 = 0.05 (H):
    #   21+22.5+22.5+14 = 80 alert;   6 unrelated (H): 21+17.5+22.5+14 = 75 no alert
    "third_party_indicators": (_merchant("P-TP", 200000, 100000, 7, 450, 1000, 5000, 100000),
                               _merchant("N-TP", 200000, 100000, 6, 450, 1000, 5000, 100000), 80, 75),
    # 450/1000 = 0.45 (C), r 2.0 (H), 7 (C), 0.05 (H):
    #   21+22.5+22.5+14 = 80 alert;   449/1000 (H): 21+22.5+17.5+14 = 75 no alert
    "mcc_inconsistency": (_merchant("P-MC", 200000, 100000, 7, 450, 1000, 5000, 100000),
                          _merchant("N-MC", 200000, 100000, 7, 449, 1000, 5000, 100000), 80, 75),
    # 10000/100000 = 0.10 (C), r 3.0 (C), 4 (H), 300/1000 (H):
    #   27+17.5+17.5+18 = 80 alert;   9999/100000 (H): 27+17.5+17.5+14 = 76 no alert
    "refund_chargeback_anomaly": (_merchant("P-RC", 300000, 100000, 4, 300, 1000, 10000, 100000),
                                  _merchant("N-RC", 300000, 100000, 4, 300, 1000, 9999, 100000), 80, 76),
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
    alerts = engine.evaluate_transaction_laundering(**frames)
    assert list(alerts["account_ref"]) == [positive["account_ref"]]


def test_alert_row_carries_its_own_working(engine):
    # P-VO above: CCHC = 27+22.5+17.5+18 = 85 Critical
    out = engine.evaluate_transaction_laundering(**_frames(PER_RULE["volume_profile_mismatch"][0]))
    working = json.loads(out.iloc[0]["risk_components"])
    assert set(working["components"]) == set(NAMES)
    assert working["score"] == 85 and working["band"] == "Critical"
    assert {n: c["band"] for n, c in working["components"].items()} == _bands("CCHC")


def test_the_reason_names_the_dominant_components_own_band(engine):
    # CLLL: 27+3.75+3.75+3 = 37.5 -> 38 Medium overall, but volume contributes the most (27)
    # and its OWN band is Critical. HCHH: 21+22.5+17.5+14 = 75 High overall; third-party
    # contributes the most (22.5, no tie) and its own band is Critical. The reason's
    # 'dominant driver' must name the largest contribution and carry THAT component's band.
    clll = _merchant("T-CLLL", 300000, 100000, 1, 50, 1000, 1000, 100000)
    hchh = _merchant("T-HCHH", 200000, 100000, 7, 300, 1000, 5000, 100000)
    scored = engine.score_all(**_frames(clll, hchh)).set_index("account_ref")
    assert (scored.loc["T-CLLL", "exposure_score"], scored.loc["T-CLLL", "exposure_band"]) == (38, "Medium")
    assert (scored.loc["T-HCHH", "exposure_score"], scored.loc["T-HCHH", "exposure_band"]) == (75, "High")
    assert scored.loc["T-CLLL", "risk_reason"].endswith(
        "dominant driver: processed card volume against the merchant's declared business volume (Critical).")
    assert scored.loc["T-HCHH", "risk_reason"].endswith(
        "dominant driver: unrelated sub-merchants funnelled through the processing relationship (Critical).")


def test_score_all_puts_the_highest_score_first(engine):
    # The fc-10 demo path builds its case from score_all's top row (framework L54-56).
    frames = _frames(_merchant("T-LOW", 100000, 100000, 1, 50, 1000, 1000, 100000), _worked("T-HIGH"))
    assert list(engine.score_all(**frames)["account_ref"]) == ["T-HIGH", "T-LOW"]


def test_every_merchant_needs_its_processor_record(engine):
    # Business Logic step 1 (L131): resolve the merchant account and its processor. A merchant
    # with no processor record is refused rather than scored.
    frames = _frames(_worked("T-A"), _worked("T-B"))
    frames["processors"] = frames["processors"][frames["processors"]["account_ref"] == "T-A"]
    assert len(engine.evaluate_transaction_laundering(**_frames(_worked("T-A")))) == 1
    with pytest.raises(ValueError, match="processor"):
        engine.evaluate_transaction_laundering(**frames)


# ---------------------------------------------------------------- required inputs

NAN = float("nan")


def test_a_missing_unrelated_merchant_count_refuses():
    # Framework L23: unrelated_merchant_count is REQUIRED ("not measured is not zero").
    # NaN is refused (int(float(nan)) raises ValueError).
    with pytest.raises(ValueError):
        score_third_party_indicators(NAN)


@pytest.mark.parametrize("scorer,args", [
    (score_volume_profile_mismatch, ("", "100000")), (score_volume_profile_mismatch, ("300000", "")),
    (score_third_party_indicators, ("",)),
    (score_mcc_inconsistency, ("", "1000")), (score_mcc_inconsistency, ("500", "")),
    (score_refund_chargeback_anomaly, ("", "100000")), (score_refund_chargeback_anomaly, ("15000", "")),
])
def test_the_model_refuses_a_blank_rather_than_scoring_it(scorer, args):
    # A blank read as zero would score a ratio of 0 Low and 0 unrelated merchants Low.
    assert scorer(*[a or "1" for a in args]) in ("Low", "Medium", "High", "Critical")
    with pytest.raises(ValueError):
        scorer(*args)


@pytest.mark.parametrize("field", NUMERIC_INPUTS)
def test_a_blank_input_as_read_from_csv_refuses(engine, field):
    # The sample reader reads every cell as a string with keep_default_na=False, so a missing
    # value arrives as "". Framework: every input is REQUIRED. Refuse, never score it as zero.
    merchant = {k: str(v) for k, v in _worked("T-BLANK").items()}
    assert len(engine.evaluate_transaction_laundering(**_frames(merchant))) == 1
    merchant[field] = ""
    with pytest.raises(ValueError):
        engine.evaluate_transaction_laundering(**_frames(merchant))


# ---------------------------------------------------------------- KNOWN D043 (cited)

@pytest.mark.parametrize("scorer,args", [
    (score_volume_profile_mismatch, (NAN, 100000)),
    (score_volume_profile_mismatch, (300000, NAN)),
    (score_mcc_inconsistency, (NAN, 1000)),
    (score_mcc_inconsistency, (500, NAN)),
    (score_refund_chargeback_anomaly, (NAN, 100000)),
    (score_refund_chargeback_anomaly, (15000, NAN)),
])
@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "KNOWN D043, cited: framework BA009 'Both amounts/counts are REQUIRED' (scoring-models/specific/"
    "BA009_Transaction_Laundering_Scoring_Framework.md:18,30,34) and the model's own 'missing != zero': "
    "a NaN passes ba009_risk_model.py:66-71 (_require checks None only), a NaN denominator also passes "
    "the '<= 0' guards at :88/:121/:140, every comparison at :91-97 / :124-130 / :143-149 is False, so it "
    "scores Critical -- measured: Failed: DID NOT RAISE <class 'ValueError'>"))
def test_a_missing_value_refuses_rather_than_scoring_critical(scorer, args):
    assert any(isinstance(a, float) and math.isnan(a) for a in args)
    with pytest.raises(ValueError):
        scorer(*args)


@pytest.mark.parametrize("field", NUMERIC_INPUTS)
def test_a_missing_value_is_refused_by_the_callable(engine, field):
    """KNOWN D043 context: the MODEL scores the ratio NaNs Critical (xfails above); the callable
    refuses only because the output row casts int(float(nan)) at transaction_laundering.py:89-95.
    The refusal is the doctrine's outcome ('REQUIRED'), so it is pinned; that one such row takes
    every other alert in the frame down with it is a QUESTION for the owner."""
    merchant = _merchant("T-NAN", 100000, 100000, 1, 50, 1000, 1000, 100000)
    assert len(engine.evaluate_transaction_laundering(**_frames(merchant, _worked()))) == 1
    merchant[field] = NAN
    with pytest.raises(ValueError):
        engine.evaluate_transaction_laundering(**_frames(merchant, _worked()))


# ---------------------------------------------------------------- KNOWN N10-FLOATCUT (cited)

# Each pair is EXACT in decimal (multiply out to check): 13001.56 / 10001.20 = 1.3,
# 18001.53 / 10000.85 = 1.8, 25004.05 / 10001.62 = 2.5, 200.64 / 10032 = 0.02,
# 500.06 / 10001.20 = 0.05, 1000.05 / 10000.50 = 0.10.
@pytest.mark.parametrize("scorer,args,band", [
    (score_volume_profile_mismatch, (13001.56, 10001.20), "Medium"),      # r = 1.3 -> not "< 1.3"
    (score_volume_profile_mismatch, (18001.53, 10000.85), "High"),        # r = 1.8 -> not "< 1.8"
    (score_volume_profile_mismatch, (25004.05, 10001.62), "Critical"),    # r = 2.5 -> otherwise
    (score_refund_chargeback_anomaly, (200.64, 10032), "Medium"),         # r = 0.02
    (score_refund_chargeback_anomaly, (500.06, 10001.20), "High"),        # r = 0.05
    (score_refund_chargeback_anomaly, (1000.05, 10000.50), "Critical"),   # r = 0.10
])
@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "KNOWN N10-FLOATCUT, cited: framework BA009 cut-lines 'r < 1.3 / < 1.8 / < 2.5' (L20) and "
    "'r < 0.02 / < 0.05 / < 0.10' (L35): an exact decimal ratio of cent-valued amounts is computed in "
    "binary float (ba009_risk_model.py:90 and :142) and lands a hair under the cut-line, scoring the "
    "band BELOW -- measured: 'Low', 'Medium', 'High' (volume) and 'Low', 'Medium', 'High' (refund)"))
def test_an_exact_decimal_ratio_on_a_cut_line_takes_the_doctrine_band(scorer, args, band):
    assert scorer(*args) == band


@pytest.mark.xfail(strict=True, raises=AssertionError, reason=(
    "KNOWN N10-FLOATCUT, cited, measured effect in BA009: a merchant processing EXACTLY 2.5x its "
    "declared volume (25004.05 of 10001.62; framework L20 'otherwise -> Critical') scores volume High "
    "(ba009_risk_model.py:90,95), 79 High instead of 85 Critical, and evaluate_transaction_laundering "
    "drops the alert -- measured: AssertionError, alerts ['P-INT'] only"))
def test_an_exact_2_5x_volume_alerts(engine):
    # Same shape as PER_RULE['volume_profile_mismatch']: r 2.5 (C), 7 (C), 0.40 (H), 0.10 (C):
    # 27+22.5+17.5+18 = 85 Critical, alerts. P-INT is the integer-amount control (250000/100000).
    cents = _merchant("P-CENT", 25004.05, 10001.62, 7, 400, 1000, 10000, 100000)
    control = _merchant("P-INT", 250000, 100000, 7, 400, 1000, 10000, 100000)
    alerts = engine.evaluate_transaction_laundering(**_frames(control, cents))
    assert len(alerts) >= 1
    assert sorted(alerts["account_ref"]) == ["P-CENT", "P-INT"]
