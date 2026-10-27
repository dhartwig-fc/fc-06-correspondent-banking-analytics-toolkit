"""Validate BA009 sample data + model consistency. Exits non-zero on failure."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from ba009_risk_model import COMPONENT_WEIGHTS  # noqa: E402
from scenarios import transaction_laundering as tl  # noqa: E402

DATA_DIR = SCRIPT_DIR / "sample-data"


def _fail(m: str) -> None:
    print("FAIL:", m)
    sys.exit(1)


def main() -> None:
    schema = json.loads((SCRIPT_DIR / "schema.json").read_text(encoding="utf-8"))
    for name, spec in schema["datasets"].items():
        path = DATA_DIR / spec["file"]
        if not path.is_file():
            _fail("dataset %s missing" % name)
        frame = pd.read_csv(path, dtype=str, keep_default_na=False)
        missing = [c for c in spec.get("required", []) if c not in frame.columns]
        if missing:
            _fail("%s missing columns %s" % (name, missing))
        if len(frame) < 20:
            _fail("%s has %d rows (< 20, BA009 is not grandfathered)" % (name, len(frame)))
    if {k: v["weight"] for k, v in schema["components"].items()} != COMPONENT_WEIGHTS:
        _fail("schema weights != model weights")
    if abs(sum(COMPONENT_WEIGHTS.values()) - 1.0) > 1e-9:
        _fail("weights do not sum to 1.0")

    scored = tl.score_all(**tl.build_frames_from_sample_data(DATA_DIR)).set_index("account_ref")
    if not (scored.loc["MER019"]["exposure_score"] == 90 and scored.loc["MER019"]["exposure_band"] == "Critical"):
        _fail("MER019 expected 90/Critical")
    if scored.loc["MER019"]["linked_individual_id"] != "P001":
        _fail("MER019 expected linked_individual_id P001 (the fusion bridge to John Cloverspindle)")
    if scored.loc["MER001"]["exposure_band"] != "Low":
        _fail("MER001 expected Low")
    if scored["exposure_score"].idxmax() != "MER019":
        _fail("MER019 (John Cloverspindle bridge) must be the single highest-scoring account -- the "
              "FC-10 adapter builds its case/graph from score_all's top row")

    alerts = tl.evaluate_transaction_laundering(**tl.build_frames_from_sample_data(DATA_DIR))
    if len(alerts) < 2:
        _fail("expected at least 2 Critical alerts, got %d" % len(alerts))
    if "MER019" not in set(alerts["account_ref"]):
        _fail("expected MER019 (John Cloverspindle bridge) among the alerts")

    print("PASS: BA009 schema, sample data and model are consistent.")
    print("  - %d datasets; MER019 = 90/Critical (John Cloverspindle bridge, top-scored); MER001 = Low; %d alert(s)"
          % (len(schema["datasets"]), len(alerts)))


if __name__ == "__main__":
    main()
