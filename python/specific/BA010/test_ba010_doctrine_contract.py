"""TT-BA010 (night 9, wave A): the BA010 Peer Group Anomalies engine against its doctrine.

Oracle, and nothing else: scoring-models/specific/BA010_Peer_Group_Anomalies_Scoring_Framework.md
(the shared |z| banding rule, weights, midpoints, half-up, alert at >= 80, all three inputs
REQUIRED, peer_std strictly positive), typologies/BA010_Peer_Group_Anomalies.md (bands
0-29/30-59/60-79/80-100, deviation "above (or below)" / "narrower or broader", the PGA019 worked
example) and the signed-off expected-outcome sheet BA010.md (2026-10-21; R1: the band table
governs over the doctrine's Python snippet). Every expected score below is hand-worked from
those numbers in a comment beside it. Inputs are CONSTRUCTED here: no sample-data file is read
and no sample entity's name is asserted.

Contributions per band (midpoint x weight), from the framework:
    volume        30%: L 4.5   M 13.5   H 21    C 27
    velocity      25%: L 3.75  M 11.25  H 17.5  C 22.5
    product usage 25%: L 3.75  M 11.25  H 17.5  C 22.5
    counterparty  20%: L 3     M 9      H 14    C 18

Peer baselines (the worked example's own segment statistics, distinct per component so a
column swap between components cannot hide): volume mean 250,000 std 25,000; velocity 12/4;
product count 6/2; counterparty count 12/2. own = mean + sign * std * z.
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

from ba010_risk_model import (  # noqa: E402
    RiskModelError, ba010_exposure_score, score_counterparty_diversity_zscore,
    score_product_usage_deviation, score_velocity_zscore, score_volume_zscore,
)

SCENARIO = BASE_DIR / "scenarios" / "peer_group_anomalies.py"
NAMES = ("volume_zscore", "velocity_zscore", "product_usage_deviation", "counterparty_diversity_zscore")
SCORERS = {"volume_zscore": score_volume_zscore, "velocity_zscore": score_velocity_zscore,
           "product_usage_deviation": score_product_usage_deviation,
           "counterparty_diversity_zscore": score_counterparty_diversity_zscore}
BAND_COLS = {"volume_zscore": "volume_zscore_band", "velocity_zscore": "velocity_zscore_band",
             "product_usage_deviation": "product_usage_deviation_band",
             "counterparty_diversity_zscore": "counterparty_diversity_zscore_band"}
# the three input columns per component, in (own, peer_mean, peer_std) order
INPUTS = {"volume_zscore": ("own_volume", "peer_mean_volume", "peer_std_volume"),
          "velocity_zscore": ("own_velocity", "peer_mean_velocity", "peer_std_velocity"),
          "product_usage_deviation": ("own_product_count", "peer_mean_product_count",
                                      "peer_std_product_count"),
          "counterparty_diversity_zscore": ("own_counterparty_count", "peer_mean_counterparty_count",
                                            "peer_std_counterparty_count")}
# a |z| that sits squarely inside each band (sign applied by the caller)
Z_OF = {"L": 0.5, "M": 1.5, "H": 2.5, "C": 3.5}
FULL = {"L": "Low", "M": "Medium", "H": "High", "C": "Critical"}


def _load():
    spec = spec_from_file_location("tt_ba010_doctrine_peer_group_anomalies", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def engine():
    return _load()


BASELINE = {"volume_zscore": (250_000.0, 25_000.0), "velocity_zscore": (12.0, 4.0),
            "product_usage_deviation": (6.0, 2.0), "counterparty_diversity_zscore": (12.0, 2.0)}


def _account(ref, code, sign=1.0, mean=None, std=None):
    """'CCHH' -> an account whose four components sit in those bands, framework order.
    mean/std, when given, replace every component's baseline."""
    row = {"customer_name": "Constructed Holder %s" % ref, "account_ref": ref,
           "segment": "Constructed Segment", "home_branch": "Constructed Branch %s" % ref,
           "peer_account_name": "Constructed Peer %s" % ref,
           "anomalous_counterparty_name": "Constructed Counterparty %s" % ref}
    for name, c in zip(NAMES, code):
        own, pm, ps = INPUTS[name]
        m, sd = BASELINE[name]
        m, sd = (m if mean is None else mean), (sd if std is None else std)
        row[own] = m + sign * sd * Z_OF[c]
        row[pm] = m
        row[ps] = sd
    return row


def _frames(*accounts):
    peers = [{"peer_account_name": a["peer_account_name"], "account_ref": a["account_ref"],
              "bank": "Constructed Bank", "jurisdiction": "GB",
              "relationship": "Peer segment reference account", "prior_alerts": 0} for a in accounts]
    return {"accounts": pd.DataFrame(list(accounts)), "peers": pd.DataFrame(peers)}


def _scored_one(engine, account):
    out = engine.score_all(**_frames(account))
    assert len(out) == 1                                   # non-vacuity: one real row scored
    return out.iloc[0]


# ---------------------------------------------------------------- check 2: |z| boundaries

@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("z,band", [
    # framework: z < 1 Low . z < 2 Medium . z < 3 High . otherwise (z >= 3) Critical
    (0.99, "Low"), (1.00, "Medium"), (1.01, "Medium"),
    (1.99, "Medium"), (2.00, "High"), (2.01, "High"),
    (2.99, "High"), (3.00, "Critical"), (3.01, "Critical"),
])
@pytest.mark.parametrize("sign", [1, -1])
def test_every_component_bands_on_abs_z_either_side_of_each_cut_line(name, z, band, sign):
    # mean 1000, std 100: own = 1000 +/- 100*z (integer offsets, so z is exact at each cut-line)
    own = 1000 + sign * round(100 * z)
    assert SCORERS[name](own, 1000, 100) == band


@pytest.mark.parametrize("name", NAMES)
def test_a_negative_peer_std_is_refused_not_folded_into_abs(name):
    # framework: "peer_std must be strictly positive"
    with pytest.raises(RiskModelError):
        SCORERS[name](130, 100, -10)


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("pos", [0, 1, 2])
def test_every_input_of_every_component_is_required(name, pos):
    args = [130, 100, 10]
    args[pos] = None
    with pytest.raises(RiskModelError):
        SCORERS[name](*args)


# ---------------------------------------------------------------- check 2: score boundaries

@pytest.mark.parametrize("code,score,band,alerts", [
    # 21+22.5+22.5+14 = 80.0 -> exactly at the threshold: Critical, alerts
    ("HCCH", 80, "Critical", True),
    # 27+17.5+17.5+18 = 80.0 -> at the threshold by another route
    ("CHHC", 80, "Critical", True),
    # 21+17.5+22.5+18 = 79.0 -> just below: High, no alert
    ("HHCC", 79, "High", False),
    # 27+22.5+17.5+14 = 81.0 -> just above
    ("CCHH", 81, "Critical", True),
    # worked example (PGA019 shape): 27+22.5+22.5+18 = 90 Critical
    ("CCCC", 90, "Critical", True),
    # framework: "a clean account with all four components Low scores 15/100"
    ("LLLL", 15, "Low", False),
    # half-up: 27+11.25+11.25+9 = 58.5 -> 59 (banker's rounding would give 58), Medium
    ("CMMM", 59, "Medium", False),
    # 21+22.5+22.5+3 = 69.0 High: three extreme components but a Low counterparty, no alert
    ("HCCL", 69, "High", False),
    # band edges: 4.5+7.5+18 = 30.0 Medium (low edge of 30-59)
    ("LLLC", 30, "Medium", False),
    # 13.5+7.5+3 = 24.0 Low
    ("MLLL", 24, "Low", False),
    # 21+35+3 = 59.0 Medium (top edge of 30-59); 27+35+3 = 65 would be High
    ("HHHL", 59, "Medium", False),
    # 27+17.5+11.25+14 = 69.75 -> 70 High (half-up of a .75)
    ("CHMH", 70, "High", False),
])
def test_score_band_and_alert_from_the_framework(engine, code, score, band, alerts):
    row = _scored_one(engine, _account("T-" + code, code))
    for name, c in zip(NAMES, code):
        assert row[BAND_COLS[name]] == FULL[c]
    assert (row["exposure_score"], row["exposure_band"]) == (score, band)
    alerted = engine.evaluate_peer_group_anomalies(**_frames(_account("T-" + code, code)))
    assert len(alerted) == (1 if alerts else 0)


def test_the_working_records_half_up_on_a_half_total():
    bands = dict(zip(NAMES, ("Critical", "Medium", "Medium", "Medium")))
    score, band, working = ba010_exposure_score(bands)
    assert working["total"] == 58.5 and score == 59 and band == "Medium"


# ---------------------------------------------------------------- check 4: positives / near misses

def test_rule_component_wiring_each_component_reads_its_own_three_columns(engine):
    """Each component Critical alone, the rest Low. Volume C: 27+3.75+3.75+3 = 37.5 -> 38;
    velocity C or product C: 4.5+22.5+3.75+3 = 33.75 -> 34; counterparty C: 4.5+7.5+18 = 30."""
    expected = {"CLLL": 38, "LCLL": 34, "LLCL": 34, "LLLC": 30}
    accounts = [_account("T-W" + code, code) for code in expected]
    out = engine.score_all(**_frames(*accounts)).set_index("account_ref")
    assert len(out) == 4
    for code, score in expected.items():
        r = out.loc["T-W" + code]
        assert [r[BAND_COLS[n]] for n in NAMES] == [FULL[c] for c in code]
        assert r["exposure_score"] == score and r["exposure_band"] == "Medium"


def test_rule_either_direction_an_account_far_below_its_peers_alerts(engine):
    # typology: "many standard deviations above (or below)", "narrower or broader": all four at
    # z = -3.5 (own 650 vs mean 1000, std 100) -> CCCC = 90 Critical, alerts
    acct = _account("T-BELOW", "CCCC", sign=-1.0, mean=1000.0, std=100.0)
    row = _scored_one(engine, acct)
    assert (row["exposure_score"], row["exposure_band"]) == (90, "Critical")
    assert len(engine.evaluate_peer_group_anomalies(**_frames(acct))) == 1


def test_near_miss_high_absolute_volume_unremarkable_for_its_own_segment(engine):
    """Sheet near miss: volume anomalous against an absolute cut-line but in line with its own
    high-turnover segment. Every component within 1 sd: LLLL = 15, no alert."""
    acct = _account("T-BIGPEER", "LLLL", mean=5_000_000.0, std=1_000_000.0)
    assert acct["own_volume"] == 5_500_000.0
    row = _scored_one(engine, acct)
    assert (row["exposure_score"], row["exposure_band"]) == (15, "Low")
    assert len(engine.evaluate_peer_group_anomalies(**_frames(acct))) == 0


def test_inverse_near_miss_modest_raw_volume_extreme_for_a_low_volume_segment(engine):
    """Sheet: modest raw volume extreme against a low-volume segment must alert when the
    weighted score reaches 80. Volume 60,000 vs mean 20,000 std 5,000 (z = 8): C; others C:
    90 Critical. The same raw 60,000 against a segment of mean 50,000, std 20,000 (z = 0.5) is Low."""
    acct = _account("T-SMALLPEER", "CCCC")
    acct.update(own_volume=60_000.0, peer_mean_volume=20_000.0, peer_std_volume=5_000.0)
    row = _scored_one(engine, acct)
    assert row["volume_zscore_band"] == "Critical"
    assert (row["exposure_score"], row["exposure_band"]) == (90, "Critical")
    assert len(engine.evaluate_peer_group_anomalies(**_frames(acct))) == 1
    assert score_volume_zscore(60_000, 50_000, 20_000) == "Low"


def test_r1_the_band_table_governs_over_the_python_snippet(engine):
    """Typology Python example also demands counterparty |z| >= 2. Sheet BA010.4 / R1: the
    scoring band table governs. CCCM: 27+22.5+22.5+9 = 81 Critical -> alerts although the
    counterparty |z| is 1.5."""
    acct = _account("T-R1", "CCCM")
    row = _scored_one(engine, acct)
    assert (row["exposure_score"], row["exposure_band"]) == (81, "Critical")
    assert len(engine.evaluate_peer_group_anomalies(**_frames(acct))) == 1


def test_a_peer_segment_with_a_zero_std_is_refused_end_to_end(engine):
    acct = _account("T-STD0", "CCCC")
    acct["peer_std_velocity"] = 0.0
    with pytest.raises(ValueError):
        engine.evaluate_peer_group_anomalies(**_frames(acct))


def test_a_mixed_batch_alerts_exactly_the_accounts_at_or_above_80(engine):
    codes = {"T-A": "CCCC", "T-B": "HCCH", "T-C": "HHCC", "T-D": "LLLL", "T-E": "CCCM"}
    accounts = [_account(ref, code) for ref, code in codes.items()]
    out = engine.evaluate_peer_group_anomalies(**_frames(*accounts))
    # 90, 80, 79, 15, 81 -> alerts at 90, 80, 81
    assert sorted(out["account_ref"]) == ["T-A", "T-B", "T-E"]
    assert out["subject_entity_id"].tolist() == out["account_ref"].tolist()
    w = json.loads(out.iloc[0]["risk_components"])
    assert set(w["components"]) == set(NAMES)


# ---------------------------------------------------------------- defects

NAN = float("nan")


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("pos", [0, 1, 2])
@pytest.mark.xfail(strict=True, raises=pytest.fail.Exception, reason=(
    "DEFECT: framework BA010 'All three inputs ... are REQUIRED -- a peer segment with no measured "
    "mean/std ... is a different finding from measures as zero deviation' (scoring-models/specific/"
    "BA010_Peer_Group_Anomalies_Scoring_Framework.md:17-21): a missing (NaN) own value, peer_mean or "
    "peer_std passes ba010_risk_model.py:59-60 (_require checks None only), `std <= 0` at :82 is "
    "False for NaN, z is NaN and every comparison at :85-90 is False, so it bands Critical -- "
    "measured: Failed: DID NOT RAISE <class 'ValueError'>. LATENT: score_all/evaluate refuse only "
    "incidentally at the int(float()) display casts (scenarios/peer_group_anomalies.py:88-99). "
    "Sibling of BA001 D1 / BA004 D-BA004-1"))
def test_a_missing_value_refuses_rather_than_banding_critical(name, pos):
    args = [130.0, 100.0, 10.0]
    args[pos] = NAN
    assert any(isinstance(a, float) and math.isnan(a) for a in args)
    with pytest.raises(ValueError):
        SCORERS[name](*args)


@pytest.mark.parametrize("field", ["own_volume", "peer_mean_volume", "peer_std_volume"])
def test_the_callable_refuses_an_account_with_a_missing_peer_baseline(engine, field):
    """Same REQUIRED rule, end to end. MEASURED: unlike the risk model (defect above), the
    callable does refuse -- but only INCIDENTALLY, at the display cast
    int(float(nan)) in scenarios/peer_group_anomalies.py:88-99, after the NaN has already been
    banded Critical at :70. This test pins the refusal, so removing those casts goes red."""
    # HHCC = 21+17.5+22.5+18 = 79 High with every input present: no alert
    acct = _account("T-NAN", "HHCC")
    assert _scored_one(engine, acct)["exposure_score"] == 79
    assert len(engine.evaluate_peer_group_anomalies(**_frames(acct))) == 0
    acct[field] = NAN
    with pytest.raises(ValueError):
        engine.evaluate_peer_group_anomalies(**_frames(acct))
