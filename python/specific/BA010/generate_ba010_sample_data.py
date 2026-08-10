"""Generate synthetic sample data for BA010 Peer Group Anomalies.

22 accounts (>= the 2026-08-09 20-row standard; BA010 is NOT grandfathered), spread
across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  PGA001-PGA006   Low       (15)
  PGA007-PGA012   Medium    (45)
  PGA013-PGA018   High      (70)
  PGA019-PGA022   Critical  (85-90)  -- at least two, per the house standard

Every component is a peer-relative z-score: `z = (own_value - peer_mean) /
peer_std`. Rather than hand-typing raw numbers and hoping they land in the right
band, this generator derives each account's four raw values from a small,
readable table of TARGET z-scores per component plus its peer segment's
(mean, std) -- the same two peer segments ("Retail Deposit Accounts" and
"Business Current Accounts") that a real peer-group model would carry. The
raw values are then rounded to realistic integers, and the actual z-score the
model will recompute from those rounded values is what determines the band --
verified consistent with the target by `validate_ba010_schema.py`.

Fusion bridge: PGA019 (Miriam Oduya, 90/Critical, the single highest-scoring
account in the set) deviates from its peer segment on every component --
Critical volume, velocity, product-usage and counterparty-diversity z-scores --
and its anomalous counterparty is **Alpha Trading Ltd**, the same real-world
entity already in the estate network (NI001's REG-2001, NI004/PAT007's C001,
and BA003/BA006's mule/dormant-reactivation bridge). Unlike a peer-group
account (a person, name-matched loosely), Alpha Trading Ltd is a COMPANY, so
canonical entity resolution's name-union joins it across domains the same way
BA001/BA003/BA004/BA006/BA007/BA008 already do. PGA020, PGA021 and PGA022 are
the other three Critical-band accounts, also alerting but strictly below
PGA019 so the bridge row is unambiguous (each has exactly one component
downgraded to High, mirroring BA009's MER020/MER021/MER022 shape).

Run:  python3 generate_ba010_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Tuple

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# Peer segment reference stats: (mean, std) per metric. Product-usage and
# counterparty-diversity share one baseline across segments (a bank's product
# catalogue and typical counterparty breadth do not vary as sharply by segment
# as raw transaction volume/velocity do); volume and velocity are segment-specific.
SEGMENT_STATS: Dict[str, Dict[str, Tuple[float, float]]] = {
    "Retail Deposit Accounts": {"volume": (250000.0, 25000.0), "velocity": (12.0, 4.0)},
    "Business Current Accounts": {"volume": (600000.0, 60000.0), "velocity": (20.0, 4.0)},
}
PRODUCT_STATS = (6.0, 2.0)       # (mean, std), both segments
COUNTERPARTY_STATS = (12.0, 2.0)  # (mean, std), both segments

BANKS = [
    "Meridian Trust Bank - Central Branch", "Continental Correspondent Bank - Harbor Branch",
    "Adriatic Union Bank - Old Town Branch", "Pacific Rim Commercial Bank - Marina Branch",
    "Helvetia Private Bank - Lakeside Branch",
]

PEERS = ["Nadia Kowalska", "Emeka Obi", "Sven Andersson", "Camille Fontaine", "Rosa Herrera", "Dov Levin"]
PEER_JURISDICTIONS = ["United Kingdom", "Ireland", "Germany", "Hong Kong", "Switzerland", "Cyprus"]

COUNTERPARTIES = [
    "Blue Harbour Logistics Ltd", "Cedar & Vale Trading Ltd", "Northwind Freight Co",
    "Solano Exchange House", "Kestrel Cash & Carry Ltd", "Gamma Imports Ltd",
    "Zeta Commodities Ltd", "Fenwick Overseas Trading Ltd",
]

# customer_name, account_ref, segment, z_volume, z_velocity, z_product, z_counterparty, counterparty_override
_ROWS: List[Tuple[str, str, str, float, float, float, float, str]] = [
    ("Elena Marchetti", "PGA001", "Retail Deposit Accounts", 0.40, 0.50, 0.35, 0.55, None),
    ("Youssef El-Amin", "PGA002", "Business Current Accounts", 0.50, 0.35, 0.55, 0.40, None),
    ("Freya Lindqvist", "PGA003", "Retail Deposit Accounts", -0.45, 0.55, 0.40, 0.50, None),
    ("Marcus Delacroix", "PGA004", "Business Current Accounts", 0.55, -0.40, 0.50, 0.35, None),
    ("Priya Nair", "PGA005", "Retail Deposit Accounts", 0.35, 0.50, -0.55, 0.45, None),
    ("Callum Ashworth", "PGA006", "Business Current Accounts", 0.50, 0.40, 0.45, -0.35, None),
    ("Ingrid Solheim", "PGA007", "Retail Deposit Accounts", 1.40, 1.50, 1.35, 1.55, None),
    ("Rafael Duarte", "PGA008", "Business Current Accounts", 1.50, 1.35, 1.55, 1.40, None),
    ("Noor Haddad", "PGA009", "Retail Deposit Accounts", -1.45, 1.55, 1.40, 1.50, None),
    ("Bjorn Kallio", "PGA010", "Business Current Accounts", 1.55, -1.40, 1.50, 1.35, None),
    ("Amara Chukwu", "PGA011", "Retail Deposit Accounts", 1.35, 1.50, -1.55, 1.45, None),
    ("Lucas Bergman", "PGA012", "Business Current Accounts", 1.50, 1.40, 1.45, -1.35, None),
    ("Sana Farooqi", "PGA013", "Retail Deposit Accounts", 2.40, 2.50, 2.35, 2.55, None),
    ("Oskar Lindberg", "PGA014", "Business Current Accounts", 2.50, 2.35, 2.55, 2.40, None),
    ("Wren Fairweather", "PGA015", "Retail Deposit Accounts", -2.45, 2.55, 2.40, 2.50, None),
    ("Kofi Boateng", "PGA016", "Business Current Accounts", 2.55, -2.40, 2.50, 2.35, None),
    ("Isla Mactavish", "PGA017", "Retail Deposit Accounts", 2.35, 2.50, -2.55, 2.45, None),
    ("Henrik Solberg", "PGA018", "Business Current Accounts", 2.50, 2.40, 2.45, -2.35, None),
    ("Miriam Oduya", "PGA019", "Retail Deposit Accounts", 4.20, 3.80, 3.60, 4.00, "Alpha Trading Ltd"),
    ("Tobias Reinholt", "PGA020", "Business Current Accounts", 3.60, 3.90, 3.40, 2.50, None),
    ("Layla Mansour", "PGA021", "Retail Deposit Accounts", 3.50, 2.50, 3.60, 3.70, None),
    ("Gustav Ahonen", "PGA022", "Business Current Accounts", 3.80, 3.50, 2.50, 3.90, None),
]


def _round_metric(value: float, integer: bool) -> Any:
    return round(value) if integer else round(value, 2)


def _build_account(row_index: int, spec: Tuple[str, str, str, float, float, float, float, str]) -> Dict[str, Any]:
    customer_name, account_ref, segment, z_vol, z_vel, z_prod, z_cp, counterparty_override = spec
    stats = SEGMENT_STATS[segment]
    vol_mean, vol_std = stats["volume"]
    vel_mean, vel_std = stats["velocity"]
    prod_mean, prod_std = PRODUCT_STATS
    cp_mean, cp_std = COUNTERPARTY_STATS

    own_volume = round(vol_mean + z_vol * vol_std)
    own_velocity = round(vel_mean + z_vel * vel_std)
    own_product_count = round(prod_mean + z_prod * prod_std)
    own_counterparty_count = round(cp_mean + z_cp * cp_std)

    peer_account_name = PEERS[row_index % len(PEERS)]
    anomalous_counterparty_name = counterparty_override or COUNTERPARTIES[row_index % len(COUNTERPARTIES)]
    home_branch = BANKS[row_index % len(BANKS)]

    return {
        "customer_name": customer_name, "account_ref": account_ref, "segment": segment,
        "home_branch": home_branch,
        "own_volume": own_volume, "peer_mean_volume": int(vol_mean), "peer_std_volume": int(vol_std),
        "own_velocity": own_velocity, "peer_mean_velocity": int(vel_mean), "peer_std_velocity": int(vel_std),
        "own_product_count": own_product_count, "peer_mean_product_count": int(prod_mean),
        "peer_std_product_count": int(prod_std),
        "own_counterparty_count": own_counterparty_count,
        "peer_mean_counterparty_count": int(cp_mean), "peer_std_counterparty_count": int(cp_std),
        "peer_account_name": peer_account_name,
        "anomalous_counterparty_name": anomalous_counterparty_name,
    }


ACCOUNTS: List[Dict[str, Any]] = [_build_account(i, spec) for i, spec in enumerate(_ROWS)]

PEER_ACCOUNTS: List[Dict[str, Any]] = [
    {
        "peer_account_name": account["peer_account_name"],
        "account_ref": account["account_ref"],
        "bank": account["home_branch"].split(" - ")[0],
        "jurisdiction": PEER_JURISDICTIONS[i % len(PEER_JURISDICTIONS)],
        "relationship": "Peer segment reference account",
        "prior_alerts": 0 if i % 3 else 1,
    }
    for i, account in enumerate(ACCOUNTS)
]

_TABLES = {"accounts.csv": ACCOUNTS, "peers.csv": PEER_ACCOUNTS}


def generate(data_dir: Path = DATA_DIR) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in _TABLES.items():
        with (data_dir / name).open("w", newline="", encoding="utf-8") as h:
            w = csv.DictWriter(h, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        print("wrote %s (%d rows)" % (name, len(rows)))


if __name__ == "__main__":
    generate()
