"""BA010 Peer Group Anomalies scenario — the governed callable.

Pure `evaluate_peer_group_anomalies`. Per account it reads the volume z-score
(deviation of transaction volume from the peer segment mean), the velocity
z-score (turnover deviation), the product usage deviation (atypical product/
channel mix vs peers), and the counterparty diversity z-score (unusual breadth
of counterparties vs peers), then scores the four component bands.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "sample-data"
OUTPUT_DIR = BASE_DIR / "expected_outputs"

if str(BASE_DIR) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(BASE_DIR))

from ba010_risk_model import (  # noqa: E402
    ba010_exposure_score, score_counterparty_diversity_zscore, score_product_usage_deviation,
    score_velocity_zscore, score_volume_zscore,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("accounts", "peers")

OUTPUT_COLUMNS = (
    "account_ref", "customer_name", "segment", "home_branch",
    "subject_entity_id", "subject_name",
    "own_volume", "peer_mean_volume", "peer_std_volume",
    "own_velocity", "peer_mean_velocity", "peer_std_velocity",
    "own_product_count", "peer_mean_product_count", "peer_std_product_count",
    "own_counterparty_count", "peer_mean_counterparty_count", "peer_std_counterparty_count",
    "peer_account_name", "anomalous_counterparty_name",
    "volume_zscore_band", "velocity_zscore_band", "product_usage_deviation_band",
    "counterparty_diversity_zscore_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "volume_zscore": "transaction volume deviation from the peer segment",
    "velocity_zscore": "turnover velocity deviation from the peer segment",
    "product_usage_deviation": "atypical product/channel mix against the peer segment",
    "counterparty_diversity_zscore": "unusual counterparty breadth against the peer segment",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(account, peers) -> Dict[str, Any]:
    account_ref = str(account["account_ref"])
    peer_account_name = str(account["peer_account_name"])

    peer = peers[peers["account_ref"] == account_ref]
    if peer.empty:
        raise ValueError("BA010 cannot score %s: peer record for account %s is missing." % (account_ref, account_ref))

    volume_band = score_volume_zscore(account["own_volume"], account["peer_mean_volume"], account["peer_std_volume"])
    velocity_band = score_velocity_zscore(account["own_velocity"], account["peer_mean_velocity"], account["peer_std_velocity"])
    product_band = score_product_usage_deviation(
        account["own_product_count"], account["peer_mean_product_count"], account["peer_std_product_count"])
    counterparty_band = score_counterparty_diversity_zscore(
        account["own_counterparty_count"], account["peer_mean_counterparty_count"], account["peer_std_counterparty_count"])

    bands = {
        "volume_zscore": volume_band, "velocity_zscore": velocity_band,
        "product_usage_deviation": product_band, "counterparty_diversity_zscore": counterparty_band,
    }
    score, band, working = ba010_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "customer_name": str(account["customer_name"]),
        "segment": str(account["segment"]), "home_branch": str(account["home_branch"]),
        "subject_entity_id": account_ref, "subject_name": str(account["customer_name"]),
        "own_volume": int(float(account["own_volume"])),
        "peer_mean_volume": int(float(account["peer_mean_volume"])),
        "peer_std_volume": int(float(account["peer_std_volume"])),
        "own_velocity": int(float(account["own_velocity"])),
        "peer_mean_velocity": int(float(account["peer_mean_velocity"])),
        "peer_std_velocity": int(float(account["peer_std_velocity"])),
        "own_product_count": int(float(account["own_product_count"])),
        "peer_mean_product_count": int(float(account["peer_mean_product_count"])),
        "peer_std_product_count": int(float(account["peer_std_product_count"])),
        "own_counterparty_count": int(float(account["own_counterparty_count"])),
        "peer_mean_counterparty_count": int(float(account["peer_mean_counterparty_count"])),
        "peer_std_counterparty_count": int(float(account["peer_std_counterparty_count"])),
        "peer_account_name": peer_account_name,
        "anomalous_counterparty_name": str(account["anomalous_counterparty_name"]),
        "volume_zscore_band": volume_band, "velocity_zscore_band": velocity_band,
        "product_usage_deviation_band": product_band, "counterparty_diversity_zscore_band": counterparty_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "BA010_PEER_GROUP_ANOMALIES",
        "risk_reason": "Account behaviour deviates from its peer segment across volume, velocity, product usage "
                       "and counterparty diversity; dominant driver: %s." % dominant,
    }


def score_all(accounts, peers) -> pd.DataFrame:
    rows = [_score(a, peers) for _, a in accounts.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_peer_group_anomalies(accounts, peers) -> pd.DataFrame:
    frames = {"accounts": accounts, "peers": peers}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("BA010 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"accounts": read("accounts.csv"), "peers": read("peers.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_peer_group_anomalies(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "ba010_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "ba010_peer_group_anomalies_alerts.csv", index=False)
    print("BA010 peer group anomalies scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
