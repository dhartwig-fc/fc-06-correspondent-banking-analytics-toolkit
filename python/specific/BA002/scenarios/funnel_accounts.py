"""BA002 Funnel Accounts scenario — the governed callable.

Pure `evaluate_funnel_accounts`. Per account it reads the geographic dispersion of
its source depositors (how many distinct regions feed it), the inflow fan-in (how
many distinct depositors), the rapid passthrough (how short the in-to-out dwell
is), and the beneficiary concentration (how much of the outbound funds go to one
beneficiary), then scores the four component bands.
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

from ba002_risk_model import (  # noqa: E402
    ba002_exposure_score, score_beneficiary_concentration, score_geographic_dispersion,
    score_inflow_fan_in, score_rapid_passthrough,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("accounts", "beneficiaries")

OUTPUT_COLUMNS = (
    "account_ref", "customer_name", "segment", "home_branch",
    "subject_entity_id", "subject_name",
    "distinct_source_regions", "distinct_depositors", "total_inflow_amount", "max_dwell_hours",
    "top_beneficiary_amount", "total_outflow_amount", "top_depositor_name", "beneficiary_name",
    "geographic_dispersion_band", "inflow_fan_in_band", "rapid_passthrough_band",
    "beneficiary_concentration_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "geographic_dispersion": "geographic dispersion of source depositors",
    "inflow_fan_in": "inflow fan-in from distinct depositors",
    "rapid_passthrough": "rapid in-to-out passthrough",
    "beneficiary_concentration": "beneficiary concentration on a single downstream entity",
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
        raise ValueError("BA002 cannot score %s: beneficiary record for account %s is missing." % (account_ref, account_ref))

    geo_band = score_geographic_dispersion(account["distinct_source_regions"])
    fanin_band = score_inflow_fan_in(account["distinct_depositors"])
    passthrough_band = score_rapid_passthrough(account["max_dwell_hours"])
    benef_band = score_beneficiary_concentration(account["top_beneficiary_amount"], account["total_outflow_amount"])

    bands = {
        "geographic_dispersion": geo_band, "inflow_fan_in": fanin_band,
        "rapid_passthrough": passthrough_band, "beneficiary_concentration": benef_band,
    }
    score, band, working = ba002_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "customer_name": str(account["customer_name"]),
        "segment": str(account["segment"]), "home_branch": str(account["home_branch"]),
        "subject_entity_id": account_ref, "subject_name": str(account["customer_name"]),
        "distinct_source_regions": int(float(account["distinct_source_regions"])),
        "distinct_depositors": int(float(account["distinct_depositors"])),
        "total_inflow_amount": int(float(account["total_inflow_amount"])),
        "max_dwell_hours": int(float(account["max_dwell_hours"])),
        "top_beneficiary_amount": int(float(account["top_beneficiary_amount"])),
        "total_outflow_amount": int(float(account["total_outflow_amount"])),
        "top_depositor_name": str(account["top_depositor_name"]),
        "beneficiary_name": beneficiary_name,
        "geographic_dispersion_band": geo_band, "inflow_fan_in_band": fanin_band,
        "rapid_passthrough_band": passthrough_band, "beneficiary_concentration_band": benef_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "BA002_FUNNEL_ACCOUNTS",
        "risk_reason": "Deposits collected from geographically-dispersed depositors and rapidly funnelled "
                       "onward to a concentrated beneficiary; dominant driver: %s." % dominant,
    }


def score_all(accounts, beneficiaries) -> pd.DataFrame:
    rows = [_score(a, beneficiaries) for _, a in accounts.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_funnel_accounts(accounts, beneficiaries) -> pd.DataFrame:
    frames = {"accounts": accounts, "beneficiaries": beneficiaries}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("BA002 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"accounts": read("accounts.csv"), "beneficiaries": read("beneficiaries.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_funnel_accounts(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "ba002_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "ba002_funnel_accounts_alerts.csv", index=False)
    print("BA002 funnel accounts scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
