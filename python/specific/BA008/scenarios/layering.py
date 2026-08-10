"""BA008 Layering scenario — the governed callable.

Pure `evaluate_layering`. Per seed account it reads the chain depth (how many transfer
hops the funds pass through before the trail goes cold), the intermediary opacity (what
share of the chain's intermediaries are shells/nominees), the jurisdiction hopping (how
many hops route through a secrecy/offshore jurisdiction), and the value fragmentation
(how many pieces the seed amount is split into along the chain), then scores the four
component bands.
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

from ba008_risk_model import (  # noqa: E402
    ba008_exposure_score, score_chain_depth, score_intermediary_opacity,
    score_jurisdiction_hopping, score_value_fragmentation,
)

ALERT_THRESHOLD = 80

REQUIRED_FRAMES = ("accounts", "intermediaries")

OUTPUT_COLUMNS = (
    "account_ref", "customer_name", "segment", "home_branch",
    "subject_entity_id", "subject_name",
    "chain_depth", "opaque_intermediary_count", "total_intermediary_count",
    "secrecy_jurisdiction_hops", "fragment_count",
    "first_intermediary_name", "second_intermediary_name", "destination_name",
    "chain_depth_band", "intermediary_opacity_band", "jurisdiction_hopping_band",
    "value_fragmentation_band",
    "exposure_score", "exposure_band", "risk_components", "alert_type", "risk_reason",
)

_DRIVER_LABEL = {
    "chain_depth": "transfer-chain depth before the trail goes cold",
    "intermediary_opacity": "share of shell/nominee intermediaries in the chain",
    "jurisdiction_hopping": "hops routed through secrecy/offshore jurisdictions",
    "value_fragmentation": "split-then-remerge value fragmentation",
}


def _dominant_driver(working: Dict[str, Any]) -> str:
    components = working["components"]
    top = max(components.items(), key=lambda kv: kv[1]["contribution"])
    name, detail = top
    return "%s (%s)" % (_DRIVER_LABEL[name], detail["band"])


def _score(account, intermediaries) -> Dict[str, Any]:
    account_ref = str(account["account_ref"])
    destination_name = str(account["destination_name"])

    dest = intermediaries[intermediaries["account_ref"] == account_ref]
    if dest.empty:
        raise ValueError("BA008 cannot score %s: intermediary record for account %s is missing." % (account_ref, account_ref))

    chain_band = score_chain_depth(account["chain_depth"])
    opacity_band = score_intermediary_opacity(account["opaque_intermediary_count"], account["total_intermediary_count"])
    jurisdiction_band = score_jurisdiction_hopping(account["secrecy_jurisdiction_hops"])
    fragmentation_band = score_value_fragmentation(account["fragment_count"])

    bands = {
        "chain_depth": chain_band, "intermediary_opacity": opacity_band,
        "jurisdiction_hopping": jurisdiction_band, "value_fragmentation": fragmentation_band,
    }
    score, band, working = ba008_exposure_score(bands)
    dominant = _dominant_driver(working)

    return {
        "account_ref": account_ref, "customer_name": str(account["customer_name"]),
        "segment": str(account["segment"]), "home_branch": str(account["home_branch"]),
        "subject_entity_id": account_ref, "subject_name": str(account["customer_name"]),
        "chain_depth": int(float(account["chain_depth"])),
        "opaque_intermediary_count": int(float(account["opaque_intermediary_count"])),
        "total_intermediary_count": int(float(account["total_intermediary_count"])),
        "secrecy_jurisdiction_hops": int(float(account["secrecy_jurisdiction_hops"])),
        "fragment_count": int(float(account["fragment_count"])),
        "first_intermediary_name": str(account["first_intermediary_name"]),
        "second_intermediary_name": str(account["second_intermediary_name"]),
        "destination_name": destination_name,
        "chain_depth_band": chain_band, "intermediary_opacity_band": opacity_band,
        "jurisdiction_hopping_band": jurisdiction_band, "value_fragmentation_band": fragmentation_band,
        "exposure_score": score, "exposure_band": band, "risk_components": json.dumps(working, sort_keys=True),
        "alert_type": "BA008_LAYERING",
        "risk_reason": "Funds pushed through a deep, opaque, cross-border transfer chain designed to sever "
                       "the audit trail from the seed account; dominant driver: %s." % dominant,
    }


def score_all(accounts, intermediaries) -> pd.DataFrame:
    rows = [_score(a, intermediaries) for _, a in accounts.iterrows()]
    frame = pd.DataFrame(rows, columns=list(OUTPUT_COLUMNS))
    return frame.sort_values("exposure_score", ascending=False).reset_index(drop=True)


def evaluate_layering(accounts, intermediaries) -> pd.DataFrame:
    frames = {"accounts": accounts, "intermediaries": intermediaries}
    absent = [n for n in REQUIRED_FRAMES if frames.get(n) is None]
    if absent:
        raise ValueError("BA008 cannot be scored. These frames are absent: " + ", ".join(absent))
    scored = score_all(**frames)
    return scored[scored["exposure_score"] >= ALERT_THRESHOLD].copy()[list(OUTPUT_COLUMNS)]


def build_frames_from_sample_data(data_dir: Path = DATA_DIR) -> Dict[str, pd.DataFrame]:
    read = lambda n: pd.read_csv(data_dir / n, dtype=str, keep_default_na=False)  # noqa: E731
    return {"accounts": read("accounts.csv"), "intermediaries": read("intermediaries.csv")}


def run_scenario(data_dir: Path = DATA_DIR, output_dir: Path = OUTPUT_DIR) -> pd.DataFrame:
    frames = build_frames_from_sample_data(data_dir)
    scored = score_all(**frames)
    alerts = evaluate_layering(**frames)
    output_dir.mkdir(parents=True, exist_ok=True)
    scored.to_csv(output_dir / "ba008_exposure_scores.csv", index=False)
    alerts.to_csv(output_dir / "ba008_layering_alerts.csv", index=False)
    print("BA008 layering scenario completed; %d accounts, %d alert(s)" % (len(scored), len(alerts)))
    return alerts


if __name__ == "__main__":
    run_scenario()
