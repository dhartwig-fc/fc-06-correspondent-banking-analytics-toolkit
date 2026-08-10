"""BA007 Cash Intensive Activity scenario — the governed callable.

Pure `evaluate_cash_intensive_activity`. Per business account it reads the cash ratio
(cash deposits vs total turnover, scaled against the business's declared peer-segment
cash norm), the profile excess (actual cash deposited vs the business's own declared
annual cash volume), the deposit regularity (how unnaturally even the deposit rhythm
is), and the commingling (how much of the deposited cash did not originate with the
business itself), then scores the four component bands.
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

from ba007_risk_model import (  # noqa: E402
    ba007_exposure_score, score_cash_ratio, score_commingling, score_deposit_regularity,
    score_profile_excess,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("accounts", "depositors")

OUTPUT_COLUMNS = (
    "account_ref", "customer_name", "segment", "home_branch",
    "subject_entity_id", "subject_name",
    "cash_deposits_amount", "total_turnover_amount", "peer_norm_cash_ratio",
    "declared_annual_cash_volume", "deposit_cv_pct", "third_party_deposit_amount",
    "total_deposit_amount", "top_depositor_name", "linked_entity_name",
    "cash_ratio_band", "profile_excess_band", "deposit_regularity_band",
    "commingling_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "cash_ratio": "cash ratio against the declared peer-segment norm",
    "profile_excess": "cash deposited in excess of the declared business profile",
    "deposit_regularity": "unnaturally even deposit rhythm",
    "commingling": "third-party funds commingled with the business's own cash",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(account, depositors) -> Dict[str, Any]:
    account_ref = str(account["account_ref"])
    linked_entity_name = str(account["linked_entity_name"])

    dep = depositors[depositors["account_ref"] == account_ref]
    if dep.empty:
        raise ValueError("BA007 cannot score %s: depositor record for account %s is missing." % (account_ref, account_ref))

    cash_band = score_cash_ratio(account["cash_deposits_amount"], account["total_turnover_amount"], account["peer_norm_cash_ratio"])
    profile_band = score_profile_excess(account["cash_deposits_amount"], account["declared_annual_cash_volume"])
    regularity_band = score_deposit_regularity(account["deposit_cv_pct"])
    commingling_band = score_commingling(account["third_party_deposit_amount"], account["total_deposit_amount"])

    bands = {
        "cash_ratio": cash_band, "profile_excess": profile_band,
        "deposit_regularity": regularity_band, "commingling": commingling_band,
    }
    score, band, working = ba007_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "customer_name": str(account["customer_name"]),
        "segment": str(account["segment"]), "home_branch": str(account["home_branch"]),
        "subject_entity_id": account_ref, "subject_name": str(account["customer_name"]),
        "cash_deposits_amount": int(float(account["cash_deposits_amount"])),
        "total_turnover_amount": int(float(account["total_turnover_amount"])),
        "peer_norm_cash_ratio": float(account["peer_norm_cash_ratio"]),
        "declared_annual_cash_volume": int(float(account["declared_annual_cash_volume"])),
        "deposit_cv_pct": float(account["deposit_cv_pct"]),
        "third_party_deposit_amount": int(float(account["third_party_deposit_amount"])),
        "total_deposit_amount": int(float(account["total_deposit_amount"])),
        "top_depositor_name": str(account["top_depositor_name"]),
        "linked_entity_name": linked_entity_name,
        "cash_ratio_band": cash_band, "profile_excess_band": profile_band,
        "deposit_regularity_band": regularity_band, "commingling_band": commingling_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "BA007_CASH_INTENSIVE_ACTIVITY",
        "risk_reason": "Cash deposits disproportionate to the declared business profile, with an "
                       "unnaturally even deposit rhythm and third-party funds commingled in; "
                       "dominant driver: %s." % dominant,
    }


def score_all(accounts, depositors) -> pd.DataFrame:
    rows = [_score(a, depositors) for _, a in accounts.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_cash_intensive_activity(accounts, depositors) -> pd.DataFrame:
    frames = {"accounts": accounts, "depositors": depositors}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("BA007 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"accounts": read("accounts.csv"), "depositors": read("depositors.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_cash_intensive_activity(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "ba007_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "ba007_cash_intensive_activity_alerts.csv", index=False)
    print("BA007 cash intensive activity scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
