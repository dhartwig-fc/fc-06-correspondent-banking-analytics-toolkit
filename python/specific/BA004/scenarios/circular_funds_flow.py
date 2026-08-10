"""BA004 Circular Funds Flow scenario — the governed callable.

Pure `evaluate_circular_funds_flow`. Per originating account it reads the loop
closure (how much of the originated funds return to origin), the hop count
(how many intermediary accounts the loop passes through), the value
preservation (how little value is lost hop to hop across the loop), and the
timing compression (how rapidly the whole round trip completes), then scores
the four component bands.
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

from ba004_risk_model import (  # noqa: E402
    ba004_exposure_score, score_hop_count, score_loop_closure,
    score_timing_compression, score_value_preservation,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("accounts", "loop_members")

OUTPUT_COLUMNS = (
    "account_ref", "customer_name", "segment", "home_branch",
    "subject_entity_id", "subject_name",
    "originated_amount", "returned_amount", "hop_count",
    "avg_hop_retention_pct", "loop_duration_hours",
    "first_loop_member_name", "second_loop_member_name", "closure_member_name",
    "loop_closure_band", "hop_count_band", "value_preservation_band",
    "timing_compression_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "loop_closure": "share of originated funds that return to the origin account",
    "hop_count": "number of intermediary accounts the loop passes through",
    "value_preservation": "value retained hop to hop across the loop",
    "timing_compression": "speed with which the round trip completes",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(account, loop_members) -> Dict[str, Any]:
    account_ref = str(account["account_ref"])
    closure_member_name = str(account["closure_member_name"])

    closure = loop_members[loop_members["account_ref"] == account_ref]
    if closure.empty:
        raise ValueError("BA004 cannot score %s: loop-member record for account %s is missing." % (account_ref, account_ref))

    closure_band = score_loop_closure(account["returned_amount"], account["originated_amount"])
    hop_band = score_hop_count(account["hop_count"])
    value_band = score_value_preservation(account["avg_hop_retention_pct"])
    timing_band = score_timing_compression(account["loop_duration_hours"])

    bands = {
        "loop_closure": closure_band, "hop_count": hop_band,
        "value_preservation": value_band, "timing_compression": timing_band,
    }
    score, band, working = ba004_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "customer_name": str(account["customer_name"]),
        "segment": str(account["segment"]), "home_branch": str(account["home_branch"]),
        "subject_entity_id": account_ref, "subject_name": str(account["customer_name"]),
        "originated_amount": int(float(account["originated_amount"])),
        "returned_amount": int(float(account["returned_amount"])),
        "hop_count": int(float(account["hop_count"])),
        "avg_hop_retention_pct": float(account["avg_hop_retention_pct"]),
        "loop_duration_hours": float(account["loop_duration_hours"]),
        "first_loop_member_name": str(account["first_loop_member_name"]),
        "second_loop_member_name": str(account["second_loop_member_name"]),
        "closure_member_name": closure_member_name,
        "loop_closure_band": closure_band, "hop_count_band": hop_band,
        "value_preservation_band": value_band, "timing_compression_band": timing_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "BA004_CIRCULAR_FUNDS_FLOW",
        "risk_reason": "Originated funds complete a round trip back to the origin account through a "
                       "disguising chain of intermediaries with minimal value loss; dominant driver: %s." % dominant,
    }


def score_all(accounts, loop_members) -> pd.DataFrame:
    rows = [_score(a, loop_members) for _, a in accounts.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_circular_funds_flow(accounts, loop_members) -> pd.DataFrame:
    frames = {"accounts": accounts, "loop_members": loop_members}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("BA004 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"accounts": read("accounts.csv"), "loop_members": read("loop_members.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_circular_funds_flow(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "ba004_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "ba004_circular_funds_flow_alerts.csv", index=False)
    print("BA004 circular funds flow scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
