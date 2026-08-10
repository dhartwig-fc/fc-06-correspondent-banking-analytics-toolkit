"""BA005 Rapid Movement scenario — the governed callable.

Pure `evaluate_rapid_movement`. Per account it reads the dwell time (how briefly funds
rest before clearing onward), the velocity (turnover relative to the account's own
balance), the onward dispersion (how many distinct destinations receive the outbound
leg), and the value match (how closely the outbound amount tracks the inbound amount),
then scores the four component bands.
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

from ba005_risk_model import (  # noqa: E402
    ba005_exposure_score, score_dwell_time, score_onward_dispersion,
    score_value_match, score_velocity,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("accounts", "destinations")

OUTPUT_COLUMNS = (
    "account_ref", "customer_name", "segment", "home_branch",
    "subject_entity_id", "subject_name",
    "inbound_amount", "outbound_amount", "dwell_time_hours", "avg_balance",
    "total_turnover_amount", "distinct_destination_count",
    "source_name", "first_destination_name", "second_destination_name",
    "dwell_time_band", "velocity_band", "onward_dispersion_band", "value_match_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "dwell_time": "brevity of the in-to-out dwell before funds clear onward",
    "velocity": "turnover relative to the account's own balance",
    "onward_dispersion": "spread of the outbound leg across distinct onward destinations",
    "value_match": "how closely the outbound amount tracks the inbound amount",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(account, destinations) -> Dict[str, Any]:
    account_ref = str(account["account_ref"])
    first_destination_name = str(account["first_destination_name"])

    dest = destinations[destinations["account_ref"] == account_ref]
    if dest.empty:
        raise ValueError("BA005 cannot score %s: destination record for account %s is missing." % (account_ref, account_ref))

    dwell_band = score_dwell_time(account["dwell_time_hours"])
    velocity_band = score_velocity(account["total_turnover_amount"], account["avg_balance"])
    dispersion_band = score_onward_dispersion(account["distinct_destination_count"])
    match_band = score_value_match(account["outbound_amount"], account["inbound_amount"])

    bands = {
        "dwell_time": dwell_band, "velocity": velocity_band,
        "onward_dispersion": dispersion_band, "value_match": match_band,
    }
    score, band, working = ba005_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "customer_name": str(account["customer_name"]),
        "segment": str(account["segment"]), "home_branch": str(account["home_branch"]),
        "subject_entity_id": account_ref, "subject_name": str(account["customer_name"]),
        "inbound_amount": int(float(account["inbound_amount"])),
        "outbound_amount": int(float(account["outbound_amount"])),
        "dwell_time_hours": float(account["dwell_time_hours"]),
        "avg_balance": int(float(account["avg_balance"])),
        "total_turnover_amount": int(float(account["total_turnover_amount"])),
        "distinct_destination_count": int(float(account["distinct_destination_count"])),
        "source_name": str(account["source_name"]),
        "first_destination_name": first_destination_name,
        "second_destination_name": str(account["second_destination_name"]),
        "dwell_time_band": dwell_band, "velocity_band": velocity_band,
        "onward_dispersion_band": dispersion_band, "value_match_band": match_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "BA005_RAPID_MOVEMENT",
        "risk_reason": "Funds clear onto and off the account almost immediately, at a velocity far "
                       "exceeding its own balance, dispersing across multiple onward destinations with "
                       "the outbound amount tracking the inbound amount near 1:1; dominant driver: %s." % dominant,
    }


def score_all(accounts, destinations) -> pd.DataFrame:
    rows = [_score(a, destinations) for _, a in accounts.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_rapid_movement(accounts, destinations) -> pd.DataFrame:
    frames = {"accounts": accounts, "destinations": destinations}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("BA005 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"accounts": read("accounts.csv"), "destinations": read("destinations.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_rapid_movement(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "ba005_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "ba005_rapid_movement_alerts.csv", index=False)
    print("BA005 rapid movement scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
