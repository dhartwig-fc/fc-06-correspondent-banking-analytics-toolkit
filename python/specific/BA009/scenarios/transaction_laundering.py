"""BA009 Transaction Laundering scenario — the governed callable.

Pure `evaluate_transaction_laundering`. Per merchant account it reads the volume
profile mismatch (processed card volume vs the merchant's own declared business
volume), the third-party indicators (how many unrelated sub-merchants are funnelled
through the one processing relationship), the MCC inconsistency (share of transactions
that do not match the boarded merchant category code), and the refund/chargeback
anomaly (share of processed value returned, inconsistent with genuine commerce), then
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

from ba009_risk_model import (  # noqa: E402
    ba009_exposure_score, score_mcc_inconsistency, score_refund_chargeback_anomaly,
    score_third_party_indicators, score_volume_profile_mismatch,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("merchants", "processors")

OUTPUT_COLUMNS = (
    "account_ref", "customer_name", "segment", "home_branch",
    "subject_entity_id", "subject_name",
    "processed_card_volume", "declared_business_volume",
    "unrelated_merchant_count",
    "mcc_mismatched_txn_count", "total_txn_count",
    "refund_chargeback_amount", "total_processed_amount",
    "processor_name", "hidden_merchant_name",
    "linked_individual_id", "linked_individual_name",
    "volume_profile_mismatch_band", "third_party_indicators_band",
    "mcc_inconsistency_band", "refund_chargeback_anomaly_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "volume_profile_mismatch": "processed card volume against the merchant's declared business volume",
    "third_party_indicators": "unrelated sub-merchants funnelled through the processing relationship",
    "mcc_inconsistency": "transactions inconsistent with the boarded merchant category code",
    "refund_chargeback_anomaly": "refund/chargeback rate inconsistent with genuine commerce",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(account, processors) -> Dict[str, Any]:
    account_ref = str(account["account_ref"])
    processor_name = str(account["processor_name"])

    proc = processors[processors["account_ref"] == account_ref]
    if proc.empty:
        raise ValueError("BA009 cannot score %s: processor record for account %s is missing." % (account_ref, account_ref))

    volume_band = score_volume_profile_mismatch(account["processed_card_volume"], account["declared_business_volume"])
    third_party_band = score_third_party_indicators(account["unrelated_merchant_count"])
    mcc_band = score_mcc_inconsistency(account["mcc_mismatched_txn_count"], account["total_txn_count"])
    refund_band = score_refund_chargeback_anomaly(account["refund_chargeback_amount"], account["total_processed_amount"])

    bands = {
        "volume_profile_mismatch": volume_band, "third_party_indicators": third_party_band,
        "mcc_inconsistency": mcc_band, "refund_chargeback_anomaly": refund_band,
    }
    score, band, working = ba009_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "customer_name": str(account["customer_name"]),
        "segment": str(account["segment"]), "home_branch": str(account["home_branch"]),
        "subject_entity_id": account_ref, "subject_name": str(account["customer_name"]),
        "processed_card_volume": int(float(account["processed_card_volume"])),
        "declared_business_volume": int(float(account["declared_business_volume"])),
        "unrelated_merchant_count": int(float(account["unrelated_merchant_count"])),
        "mcc_mismatched_txn_count": int(float(account["mcc_mismatched_txn_count"])),
        "total_txn_count": int(float(account["total_txn_count"])),
        "refund_chargeback_amount": int(float(account["refund_chargeback_amount"])),
        "total_processed_amount": int(float(account["total_processed_amount"])),
        "processor_name": processor_name,
        "hidden_merchant_name": str(account["hidden_merchant_name"]),
        "linked_individual_id": str(account["linked_individual_id"]),
        "linked_individual_name": str(account["linked_individual_name"]),
        "volume_profile_mismatch_band": volume_band, "third_party_indicators_band": third_party_band,
        "mcc_inconsistency_band": mcc_band, "refund_chargeback_anomaly_band": refund_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "BA009_TRANSACTION_LAUNDERING",
        "risk_reason": "Card processing volume disproportionate to the merchant's declared business, with "
                       "unrelated sub-merchants funnelled through the relationship and a transaction mix "
                       "inconsistent with the boarded merchant category code; dominant driver: %s." % dominant,
    }


def score_all(merchants, processors) -> pd.DataFrame:
    rows = [_score(a, processors) for _, a in merchants.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_transaction_laundering(merchants, processors) -> pd.DataFrame:
    frames = {"merchants": merchants, "processors": processors}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("BA009 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"merchants": read("merchants.csv"), "processors": read("processors.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_transaction_laundering(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "ba009_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "ba009_transaction_laundering_alerts.csv", index=False)
    print("BA009 transaction laundering scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
