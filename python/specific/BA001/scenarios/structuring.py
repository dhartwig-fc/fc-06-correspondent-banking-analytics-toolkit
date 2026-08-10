"""BA001 Structuring scenario — the governed callable.

Pure `evaluate_structuring`. Per account it reads the sub-threshold cash clustering
(how much of the cash sits just under the CTR reporting line), the temporal clustering
(deposits inside a rolling 7-day window), the multi-location spread (branches/ATMs),
and the aggregation-to-transfer step (structured cash wired onward to a beneficiary),
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

from ba001_risk_model import (  # noqa: E402
    ba001_exposure_score, score_aggregation_to_transfer, score_multi_location,
    score_sub_threshold_clustering, score_temporal_clustering,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("accounts", "beneficiaries")

OUTPUT_COLUMNS = (
    "account_ref", "customer_name", "segment", "home_branch",
    "subject_entity_id", "subject_name",
    "total_cash_deposits", "subthreshold_deposits", "deposits_max_7d", "distinct_locations",
    "structured_in_amount", "wired_out_amount", "beneficiary_name",
    "sub_threshold_clustering_band", "temporal_clustering_band", "multi_location_band",
    "aggregation_to_transfer_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "sub_threshold_clustering": "sub-threshold cash clustering",
    "temporal_clustering": "temporal deposit clustering",
    "multi_location": "multi-location deposit spread",
    "aggregation_to_transfer": "aggregation-to-transfer to a single beneficiary",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(account, beneficiaries) -> Dict[str, Any]:
    account_ref = str(account["account_ref"])
    beneficiary_name = str(account["beneficiary_name"])

    ben = beneficiaries[beneficiaries["account_ref"] == account_ref]
    if ben.empty:
        raise ValueError("BA001 cannot score %s: beneficiary record for account %s is missing." % (account_ref, account_ref))

    sub_band = score_sub_threshold_clustering(account["subthreshold_deposits"], account["total_cash_deposits"])
    temporal_band = score_temporal_clustering(account["deposits_max_7d"])
    multi_band = score_multi_location(account["distinct_locations"])
    agg_band = score_aggregation_to_transfer(account["wired_out_amount"], account["structured_in_amount"])

    bands = {
        "sub_threshold_clustering": sub_band, "temporal_clustering": temporal_band,
        "multi_location": multi_band, "aggregation_to_transfer": agg_band,
    }
    score, band, working = ba001_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "customer_name": str(account["customer_name"]),
        "segment": str(account["segment"]), "home_branch": str(account["home_branch"]),
        "subject_entity_id": account_ref, "subject_name": str(account["customer_name"]),
        "total_cash_deposits": int(float(account["total_cash_deposits"])),
        "subthreshold_deposits": int(float(account["subthreshold_deposits"])),
        "deposits_max_7d": int(float(account["deposits_max_7d"])),
        "distinct_locations": int(float(account["distinct_locations"])),
        "structured_in_amount": int(float(account["structured_in_amount"])),
        "wired_out_amount": int(float(account["wired_out_amount"])),
        "beneficiary_name": beneficiary_name,
        "sub_threshold_clustering_band": sub_band, "temporal_clustering_band": temporal_band,
        "multi_location_band": multi_band, "aggregation_to_transfer_band": agg_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "BA001_STRUCTURING",
        "risk_reason": "Cash structured beneath the CTR reporting line and aggregated onward; "
                       "dominant driver: %s." % dominant,
    }


def score_all(accounts, beneficiaries) -> pd.DataFrame:
    rows = [_score(a, beneficiaries) for _, a in accounts.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_structuring(accounts, beneficiaries) -> pd.DataFrame:
    frames = {"accounts": accounts, "beneficiaries": beneficiaries}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("BA001 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"accounts": read("accounts.csv"), "beneficiaries": read("beneficiaries.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_structuring(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "ba001_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "ba001_structuring_alerts.csv", index=False)
    print("BA001 structuring scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
