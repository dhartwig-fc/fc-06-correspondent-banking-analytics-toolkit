"""BA006 Dormant Reactivation scenario — the governed callable.

Pure `evaluate_dormant_reactivation`. Per account it reads the reactivation spike (the
reactivating inflow relative to pre-dormancy average monthly activity), the dormancy
length (how long the account sat idle before waking up), the profile deviation (new
counterparties/geographies never seen in the prior profile), and the immediate outflow
(how closely the outbound leg after reactivation tracks the reactivating inflow), then
scores the four component bands.
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

from ba006_risk_model import (  # noqa: E402
    ba006_exposure_score, score_dormancy_length, score_immediate_outflow,
    score_profile_deviation, score_reactivation_spike,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("accounts", "counterparties")

OUTPUT_COLUMNS = (
    "account_ref", "customer_name", "segment", "home_branch",
    "subject_entity_id", "subject_name",
    "reactivation_amount", "pre_dormancy_avg_monthly_activity", "dormancy_days",
    "new_counterparty_count", "outflow_amount",
    "prior_counterparty_name", "first_reactivation_counterparty_name",
    "second_reactivation_counterparty_name",
    "reactivation_spike_band", "dormancy_length_band", "profile_deviation_band",
    "immediate_outflow_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "reactivation_spike": "magnitude of the reactivating inflow against pre-dormancy average activity",
    "dormancy_length": "length of time the account sat dormant before reactivating",
    "profile_deviation": "new counterparties/geographies never seen in the account's prior profile",
    "immediate_outflow": "how closely the outbound leg after reactivation tracks the reactivating inflow",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(account, counterparties) -> Dict[str, Any]:
    account_ref = str(account["account_ref"])
    first_reactivation_counterparty_name = str(account["first_reactivation_counterparty_name"])

    cp = counterparties[counterparties["account_ref"] == account_ref]
    if cp.empty:
        raise ValueError("BA006 cannot score %s: counterparty record for account %s is missing." % (account_ref, account_ref))

    spike_band = score_reactivation_spike(account["reactivation_amount"], account["pre_dormancy_avg_monthly_activity"])
    dormancy_band = score_dormancy_length(account["dormancy_days"])
    deviation_band = score_profile_deviation(account["new_counterparty_count"])
    outflow_band = score_immediate_outflow(account["outflow_amount"], account["reactivation_amount"])

    bands = {
        "reactivation_spike": spike_band, "dormancy_length": dormancy_band,
        "profile_deviation": deviation_band, "immediate_outflow": outflow_band,
    }
    score, band, working = ba006_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "customer_name": str(account["customer_name"]),
        "segment": str(account["segment"]), "home_branch": str(account["home_branch"]),
        "subject_entity_id": account_ref, "subject_name": str(account["customer_name"]),
        "reactivation_amount": int(float(account["reactivation_amount"])),
        "pre_dormancy_avg_monthly_activity": int(float(account["pre_dormancy_avg_monthly_activity"])),
        "dormancy_days": float(account["dormancy_days"]),
        "new_counterparty_count": int(float(account["new_counterparty_count"])),
        "outflow_amount": int(float(account["outflow_amount"])),
        "prior_counterparty_name": str(account["prior_counterparty_name"]),
        "first_reactivation_counterparty_name": first_reactivation_counterparty_name,
        "second_reactivation_counterparty_name": str(account["second_reactivation_counterparty_name"]),
        "reactivation_spike_band": spike_band, "dormancy_length_band": dormancy_band,
        "profile_deviation_band": deviation_band, "immediate_outflow_band": outflow_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "BA006_DORMANT_REACTIVATION",
        "risk_reason": "A long-dormant account has reactivated with an inflow far exceeding its "
                       "pre-dormancy average activity, after sitting idle well beyond a normal "
                       "cycle, dealing with counterparties and geographies outside its prior "
                       "profile, and draining back out almost as fast as it arrived; dominant "
                       "driver: %s." % dominant,
    }


def score_all(accounts, counterparties) -> pd.DataFrame:
    rows = [_score(a, counterparties) for _, a in accounts.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_dormant_reactivation(accounts, counterparties) -> pd.DataFrame:
    frames = {"accounts": accounts, "counterparties": counterparties}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("BA006 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"accounts": read("accounts.csv"), "counterparties": read("counterparties.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_dormant_reactivation(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "ba006_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "ba006_dormant_reactivation_alerts.csv", index=False)
    print("BA006 dormant reactivation scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
