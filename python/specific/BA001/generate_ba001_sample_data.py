"""Generate synthetic sample data for BA001 Structuring.

22 customer accounts (>= the 2026-08-09 20-row standard; BA001 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  ACC001-ACC006   Low       (15-27)
  ACC007-ACC012   Medium    (34-48)
  ACC013-ACC018   High      (61-70)
  ACC019-ACC022   Critical  (81-90)  -- at least two, per the house standard

Fusion bridge: ACC019 (Dmitri Petrov, 90/Critical, the single highest-scoring account
in the set) wires its aggregated structured cash to **Gamma Imports Ltd** — an entity
already in the estate network (SAN002's tier-2 nominee, Marshall Islands) — so canonical
entity resolution joins BA001 onto the existing fused case. Being the top-scored account
matters: the FC-10 adapter builds its case/graph from the single highest exposure_score
row, so the Gamma bridge has to be that row, not merely A Critical row. ACC006 (Low, 27)
also names Gamma Imports Ltd as beneficiary, deliberately: naming the same downstream
entity is not itself the risk signal, the structuring PATTERN is.

Run:  python3 generate_ba001_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# customer_name, account_ref, segment, home_branch, total_cash_deposits, subthreshold_deposits,
# deposits_max_7d, distinct_locations, structured_in_amount, wired_out_amount, beneficiary_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"customer_name": "Sofia Rossi", "account_ref": "ACC001", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "total_cash_deposits": 45000,
     "subthreshold_deposits": 2600, "deposits_max_7d": 2, "distinct_locations": 1,
     "structured_in_amount": 16000, "wired_out_amount": 2200, "beneficiary_name": "Blue Harbour Logistics Ltd"},
    {"customer_name": "Liam O'Connor", "account_ref": "ACC002", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "total_cash_deposits": 47000,
     "subthreshold_deposits": 3100, "deposits_max_7d": 1, "distinct_locations": 2,
     "structured_in_amount": 15000, "wired_out_amount": 1800, "beneficiary_name": "Cedar & Vale Trading Ltd"},
    {"customer_name": "Grace Okafor", "account_ref": "ACC003", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "total_cash_deposits": 41000,
     "subthreshold_deposits": 8600, "deposits_max_7d": 2, "distinct_locations": 1,
     "structured_in_amount": 14000, "wired_out_amount": 1500, "beneficiary_name": "Northwind Freight Co"},
    {"customer_name": "Henrik Berg", "account_ref": "ACC004", "segment": "Small Business",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "total_cash_deposits": 44000,
     "subthreshold_deposits": 2900, "deposits_max_7d": 4, "distinct_locations": 1,
     "structured_in_amount": 13500, "wired_out_amount": 2000, "beneficiary_name": "Solano Exchange House"},
    {"customer_name": "Noor Hassan", "account_ref": "ACC005", "segment": "Retail",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "total_cash_deposits": 46000,
     "subthreshold_deposits": 3300, "deposits_max_7d": 2, "distinct_locations": 1,
     "structured_in_amount": 16500, "wired_out_amount": 5200, "beneficiary_name": "Kestrel Cash & Carry Ltd"},
    {"customer_name": "Diego Fernandez", "account_ref": "ACC006", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "total_cash_deposits": 48000,
     "subthreshold_deposits": 3400, "deposits_max_7d": 2, "distinct_locations": 2,
     "structured_in_amount": 15500, "wired_out_amount": 4800, "beneficiary_name": "Gamma Imports Ltd"},
    {"customer_name": "Astrid Lindqvist", "account_ref": "ACC007", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Riverside Branch", "total_cash_deposits": 40000,
     "subthreshold_deposits": 8800, "deposits_max_7d": 4, "distinct_locations": 2,
     "structured_in_amount": 17000, "wired_out_amount": 6000, "beneficiary_name": "Harborlight Export Co"},
    {"customer_name": "Rafael Costa", "account_ref": "ACC008", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "total_cash_deposits": 38000,
     "subthreshold_deposits": 17500, "deposits_max_7d": 2, "distinct_locations": 1,
     "structured_in_amount": 13000, "wired_out_amount": 1600, "beneficiary_name": "Meridian Bulk Traders Ltd"},
    {"customer_name": "Miguel Santos", "account_ref": "ACC009", "segment": "Retail",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "total_cash_deposits": 39000,
     "subthreshold_deposits": 8200, "deposits_max_7d": 7, "distinct_locations": 1,
     "structured_in_amount": 12500, "wired_out_amount": 1900, "beneficiary_name": "Falcon Ridge Commodities Ltd"},
    {"customer_name": "Anya Petrova", "account_ref": "ACC010", "segment": "Private Banking",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "total_cash_deposits": 37000,
     "subthreshold_deposits": 8100, "deposits_max_7d": 4, "distinct_locations": 3,
     "structured_in_amount": 12800, "wired_out_amount": 2100, "beneficiary_name": "Ashford & Pine Ltd"},
    {"customer_name": "Elena Vasquez", "account_ref": "ACC011", "segment": "Small Business",
     "home_branch": "Meridian Trust Bank - Central Branch", "total_cash_deposits": 36000,
     "subthreshold_deposits": 16200, "deposits_max_7d": 4, "distinct_locations": 1,
     "structured_in_amount": 14000, "wired_out_amount": 4900, "beneficiary_name": "Silverline Freight Partners"},
    {"customer_name": "Marcus Chen", "account_ref": "ACC012", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "total_cash_deposits": 39500,
     "subthreshold_deposits": 9200, "deposits_max_7d": 7, "distinct_locations": 2,
     "structured_in_amount": 13200, "wired_out_amount": 2300, "beneficiary_name": "Ravenwood Trading Co"},
    {"customer_name": "Fatima Al-Rashid", "account_ref": "ACC013", "segment": "Small Business",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "total_cash_deposits": 38000,
     "subthreshold_deposits": 17200, "deposits_max_7d": 7, "distinct_locations": 3,
     "structured_in_amount": 17000, "wired_out_amount": 12000, "beneficiary_name": "Delta Quay Exports Ltd"},
    {"customer_name": "Klaus Richter", "account_ref": "ACC014", "segment": "Private Banking",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "total_cash_deposits": 37500,
     "subthreshold_deposits": 16800, "deposits_max_7d": 8, "distinct_locations": 2,
     "structured_in_amount": 16800, "wired_out_amount": 12500, "beneficiary_name": "Amber Coast Traders Ltd"},
    {"customer_name": "Priya Nair", "account_ref": "ACC015", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "total_cash_deposits": 36500,
     "subthreshold_deposits": 16500, "deposits_max_7d": 5, "distinct_locations": 3,
     "structured_in_amount": 16200, "wired_out_amount": 12100, "beneficiary_name": "Union Bridge Commerce Ltd"},
    {"customer_name": "Carlos Mendoza", "account_ref": "ACC016", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Riverside Branch", "total_cash_deposits": 39000,
     "subthreshold_deposits": 17400, "deposits_max_7d": 7, "distinct_locations": 4,
     "structured_in_amount": 15900, "wired_out_amount": 6900, "beneficiary_name": "Cobalt Harbor Ltd"},
    {"customer_name": "Ingrid Larsen", "account_ref": "ACC017", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "total_cash_deposits": 37000,
     "subthreshold_deposits": 16400, "deposits_max_7d": 11, "distinct_locations": 3,
     "structured_in_amount": 14500, "wired_out_amount": 2600, "beneficiary_name": "Windward Export Group"},
    {"customer_name": "Yusuf Demir", "account_ref": "ACC018", "segment": "Private Banking",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "total_cash_deposits": 35000,
     "subthreshold_deposits": 24600, "deposits_max_7d": 7, "distinct_locations": 2,
     "structured_in_amount": 13800, "wired_out_amount": 2900, "beneficiary_name": "Marlow & Finch Trading Ltd"},
    {"customer_name": "Dmitri Petrov", "account_ref": "ACC019", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "total_cash_deposits": 34000,
     "subthreshold_deposits": 24000, "deposits_max_7d": 12, "distinct_locations": 6,
     "structured_in_amount": 19000, "wired_out_amount": 17200, "beneficiary_name": "Gamma Imports Ltd"},
    {"customer_name": "Maria Kovač", "account_ref": "ACC020", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "total_cash_deposits": 33500,
     "subthreshold_deposits": 23400, "deposits_max_7d": 8, "distinct_locations": 6,
     "structured_in_amount": 17800, "wired_out_amount": 12600, "beneficiary_name": "Highgate Commodities Ltd"},
    {"customer_name": "Aisha Rahman", "account_ref": "ACC021", "segment": "Private Banking",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "total_cash_deposits": 32000,
     "subthreshold_deposits": 23000, "deposits_max_7d": 8, "distinct_locations": 7,
     "structured_in_amount": 20000, "wired_out_amount": 18500, "beneficiary_name": "Ravenwood Trading Co"},
    {"customer_name": "Tomas Novak", "account_ref": "ACC022", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "total_cash_deposits": 33000,
     "subthreshold_deposits": 23500, "deposits_max_7d": 14, "distinct_locations": 5,
     "structured_in_amount": 18500, "wired_out_amount": 13300, "beneficiary_name": "Falcon Ridge Commodities Ltd"},
]

# beneficiary_name, account_ref, bank, jurisdiction, relationship, prior_alerts
BENEFICIARIES: List[Dict[str, Any]] = [
    {"beneficiary_name": "Blue Harbour Logistics Ltd", "account_ref": "ACC001", "bank": "Meridian Trust Bank",
     "jurisdiction": "Ireland", "relationship": "Logistics partner", "prior_alerts": 0},
    {"beneficiary_name": "Cedar & Vale Trading Ltd", "account_ref": "ACC002", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Canada", "relationship": "Trade counterparty", "prior_alerts": 0},
    {"beneficiary_name": "Northwind Freight Co", "account_ref": "ACC003", "bank": "Adriatic Union Bank",
     "jurisdiction": "Germany", "relationship": "Logistics partner", "prior_alerts": 0},
    {"beneficiary_name": "Solano Exchange House", "account_ref": "ACC004", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Hong Kong", "relationship": "Money service business", "prior_alerts": 1},
    {"beneficiary_name": "Kestrel Cash & Carry Ltd", "account_ref": "ACC005", "bank": "Helvetia Private Bank",
     "jurisdiction": "Switzerland", "relationship": "Retail supplier", "prior_alerts": 0},
    {"beneficiary_name": "Gamma Imports Ltd", "account_ref": "ACC006", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Marshall Islands", "relationship": "Import supplier", "prior_alerts": 0},
    {"beneficiary_name": "Harborlight Export Co", "account_ref": "ACC007", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Kingdom", "relationship": "Trade counterparty", "prior_alerts": 0},
    {"beneficiary_name": "Meridian Bulk Traders Ltd", "account_ref": "ACC008", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Cyprus", "relationship": "Trade counterparty", "prior_alerts": 1},
    {"beneficiary_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC009", "bank": "Adriatic Union Bank",
     "jurisdiction": "Panama", "relationship": "Commodities supplier", "prior_alerts": 1},
    {"beneficiary_name": "Ashford & Pine Ltd", "account_ref": "ACC010", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Singapore", "relationship": "Consulting retainer", "prior_alerts": 0},
    {"beneficiary_name": "Silverline Freight Partners", "account_ref": "ACC011", "bank": "Helvetia Private Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Logistics partner", "prior_alerts": 1},
    {"beneficiary_name": "Ravenwood Trading Co", "account_ref": "ACC012", "bank": "Meridian Trust Bank",
     "jurisdiction": "Turkey", "relationship": "Trade counterparty", "prior_alerts": 0},
    {"beneficiary_name": "Delta Quay Exports Ltd", "account_ref": "ACC013", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Hong Kong", "relationship": "Export supplier", "prior_alerts": 1},
    {"beneficiary_name": "Amber Coast Traders Ltd", "account_ref": "ACC014", "bank": "Adriatic Union Bank",
     "jurisdiction": "Cyprus", "relationship": "Trade counterparty", "prior_alerts": 1},
    {"beneficiary_name": "Union Bridge Commerce Ltd", "account_ref": "ACC015", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Panama", "relationship": "Contractor payment", "prior_alerts": 2},
    {"beneficiary_name": "Cobalt Harbor Ltd", "account_ref": "ACC016", "bank": "Helvetia Private Bank",
     "jurisdiction": "British Virgin Islands", "relationship": "Property developer", "prior_alerts": 1},
    {"beneficiary_name": "Windward Export Group", "account_ref": "ACC017", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Export supplier", "prior_alerts": 2},
    {"beneficiary_name": "Marlow & Finch Trading Ltd", "account_ref": "ACC018", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Hong Kong", "relationship": "Trade counterparty", "prior_alerts": 2},
    {"beneficiary_name": "Gamma Imports Ltd", "account_ref": "ACC019", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Marshall Islands", "relationship": "Import supplier", "prior_alerts": 2},
    {"beneficiary_name": "Highgate Commodities Ltd", "account_ref": "ACC020", "bank": "Adriatic Union Bank",
     "jurisdiction": "Panama", "relationship": "Commodities supplier", "prior_alerts": 3},
    {"beneficiary_name": "Ravenwood Trading Co", "account_ref": "ACC021", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Turkey", "relationship": "Trade counterparty", "prior_alerts": 3},
    {"beneficiary_name": "Falcon Ridge Commodities Ltd", "account_ref": "ACC022", "bank": "Helvetia Private Bank",
     "jurisdiction": "Panama", "relationship": "Commodities supplier", "prior_alerts": 2},
]

_TABLES = {"accounts.csv": ACCOUNTS, "beneficiaries.csv": BENEFICIARIES}


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
