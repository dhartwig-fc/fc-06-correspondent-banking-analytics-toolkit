"""Tests for the BA010 Peer Group Anomalies governed callable (loaded as the runtime loads it)."""

from __future__ import annotations

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent
SCENARIO = BASE_DIR / "scenarios" / "peer_group_anomalies.py"

ADAPTER_REQUIRED_COLUMNS = {
    "account_ref", "subject_entity_id", "subject_name", "exposure_score", "exposure_band",
    "alert_type", "risk_reason", "risk_components", "home_branch", "peer_account_name",
    "anomalous_counterparty_name",
}


def _load():
    spec = spec_from_file_location("fc06_ba010_governed_peer_group_anomalies", SCENARIO)
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def governed():
    return _load()


@pytest.fixture(scope="module")
def frames(governed):
    return governed.build_frames_from_sample_data()


def test_import_is_inert(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    before = set(p.name for p in tmp_path.iterdir())
    _load()
    assert set(p.name for p in tmp_path.iterdir()) == before


def test_callable_exists(governed):
    assert callable(getattr(governed, "evaluate_peer_group_anomalies", None))


@pytest.mark.parametrize("dropped", ["accounts", "peers"])
def test_each_frame_required(governed, frames, dropped):
    kwargs = dict(frames)
    kwargs[dropped] = None
    with pytest.raises(ValueError) as e:
        governed.evaluate_peer_group_anomalies(**kwargs)
    assert dropped in str(e.value)


def test_refuses_unmatched_peer(governed, frames):
    kwargs = dict(frames)
    kwargs["peers"] = frames["peers"].iloc[0:0]
    with pytest.raises(ValueError) as e:
        governed.evaluate_peer_group_anomalies(**kwargs)
    assert "peer" in str(e.value).lower()


def test_at_least_one_alert_present(governed, frames):
    out = governed.evaluate_peer_group_anomalies(**frames)
    assert len(out) >= 1 and ADAPTER_REQUIRED_COLUMNS <= set(out.columns)


def test_every_alert_is_at_or_above_threshold(governed, frames):
    out = governed.evaluate_peer_group_anomalies(**frames)
    assert (out["exposure_score"] >= governed.ALERT_THRESHOLD).all()


def test_clean_account_is_not_alerted(governed, frames):
    clean = {**frames, "accounts": frames["accounts"][frames["accounts"]["account_ref"] == "PGA001"]}
    out = governed.evaluate_peer_group_anomalies(**clean)
    assert len(out) == 0


def test_the_alpha_trading_bridge_alerts_critical(governed, frames):
    """PGA019's account holder (Miriam Oduya) deviates from her peer segment across
    every component and her anomalous counterparty is Alpha Trading Ltd -- the same
    real-world company already in the estate network (NI001/NI004/PAT007, and
    BA003/BA006's mule/dormant-reactivation bridges) -- so the fusion bridge must clear
    the alert threshold at Critical, proving it is a real alerting subject, not a
    decorative row. It is also the single highest-scoring account in the set, which
    matters: the FC-10 adapter builds its case/graph from score_all's top row, so the
    Alpha Trading Ltd bridge has to be carried by that row."""
    scored = governed.score_all(**frames)
    top = scored.iloc[0]
    assert top["account_ref"] == "PGA019" and top["customer_name"] == "Miriam Oduya"
    assert top["anomalous_counterparty_name"] == "Alpha Trading Ltd"
    row = governed.evaluate_peer_group_anomalies(**frames)
    bridge = row[row["account_ref"] == "PGA019"].iloc[0]
    assert bridge["anomalous_counterparty_name"] == "Alpha Trading Ltd"
    assert bridge["exposure_score"] == 90 and bridge["exposure_band"] == "Critical"


def test_working_reconstructs(governed, frames):
    out = governed.evaluate_peer_group_anomalies(**frames)
    w = json.loads(out.iloc[0]["risk_components"])
    total = sum(c["contribution"] for c in w["components"].values())
    assert abs(total - w["total"]) < 0.01


def test_one_scorer(governed):
    assert SCENARIO.read_text(encoding="utf-8").count("ba010_exposure_score(") == 1


def test_threshold_named_once(governed):
    assert governed.ALERT_THRESHOLD == 80
    assert ">= 80" not in SCENARIO.read_text(encoding="utf-8")
