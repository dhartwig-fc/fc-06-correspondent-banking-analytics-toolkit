"""Generate synthetic sample data for BA002 Funnel Accounts.

22 funnel accounts (>= the 2026-08-09 20-row standard; BA002 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  FUN001-FUN006   Low       (15-29)
  FUN007-FUN012   Medium    (36-51)
  FUN013-FUN018   High      (63-76)
  FUN019-FUN022   Critical  (84-90)  -- at least two, per the house standard

Fusion bridge: FUN019 (Zara Ahmed, 90/Critical, the single highest-scoring account
in the set) funnels its collected deposits out to **Zeta Commodities Ltd** — an
entity already in the estate network (NI004 / PAT010's C006) — so canonical entity
resolution joins BA002 onto the existing fused case. Being the top-scored account
matters: the FC-10 adapter builds its case/graph from the single highest exposure_score
row, so the Zeta bridge has to be that row, not merely a Critical row. FUN005 (Low, 29)
also names Zeta Commodities Ltd as beneficiary, deliberately: naming the same downstream
entity is not itself the risk signal, the funnelling PATTERN is.

Run:  python3 generate_ba002_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# customer_name, account_ref, segment, home_branch, distinct_source_regions,
# distinct_depositors, total_inflow_amount, max_dwell_hours, top_beneficiary_amount,
# total_outflow_amount, top_depositor_name, beneficiary_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"customer_name": "Wei Zhang", "account_ref": "FUN001", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "distinct_source_regions": 1,
     "distinct_depositors": 3, "total_inflow_amount": 43500, "max_dwell_hours": 90,
     "top_beneficiary_amount": 6300, "total_outflow_amount": 42000,
     "top_depositor_name": "James Whitfield", "beneficiary_name": "Nova Horizon Traders Ltd"},
    {"customer_name": "Amara Okonkwo", "account_ref": "FUN002", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "distinct_source_regions": 2,
     "distinct_depositors": 5, "total_inflow_amount": 40200, "max_dwell_hours": 110,
     "top_beneficiary_amount": 14400, "total_outflow_amount": 39000,
     "top_depositor_name": "Consuela Reyes", "beneficiary_name": "Silverpine Commerce Ltd"},
    {"customer_name": "Lukas Hoffmann", "account_ref": "FUN003", "segment": "Small Business",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "distinct_source_regions": 2,
     "distinct_depositors": 4, "total_inflow_amount": 45300, "max_dwell_hours": 40,
     "top_beneficiary_amount": 6600, "total_outflow_amount": 44000,
     "top_depositor_name": "Tobias Lindgren", "beneficiary_name": "Meridian Bay Holdings"},
    {"customer_name": "Isabela Alves", "account_ref": "FUN004", "segment": "Retail",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "distinct_source_regions": 4,
     "distinct_depositors": 3, "total_inflow_amount": 42200, "max_dwell_hours": 96,
     "top_beneficiary_amount": 6200, "total_outflow_amount": 41000,
     "top_depositor_name": "Priya Chandran", "beneficiary_name": "Crestwood Import Co"},
    {"customer_name": "Ravi Patel", "account_ref": "FUN005", "segment": "Small Business",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "distinct_source_regions": 1,
     "distinct_depositors": 4, "total_inflow_amount": 47500, "max_dwell_hours": 30,
     "top_beneficiary_amount": 17000, "total_outflow_amount": 46000,
     "top_depositor_name": "Omar El-Sayed", "beneficiary_name": "Zeta Commodities Ltd"},
    {"customer_name": "Chiara Bianchi", "account_ref": "FUN006", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "distinct_source_regions": 2,
     "distinct_depositors": 10, "total_inflow_amount": 44300, "max_dwell_hours": 100,
     "top_beneficiary_amount": 6400, "total_outflow_amount": 43000,
     "top_depositor_name": "Beatrice Dubois", "beneficiary_name": "Harborstone Ventures Ltd"},
    {"customer_name": "Sven Andersson", "account_ref": "FUN007", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Riverside Branch", "distinct_source_regions": 3,
     "distinct_depositors": 5, "total_inflow_amount": 48500, "max_dwell_hours": 32,
     "top_beneficiary_amount": 17400, "total_outflow_amount": 47000,
     "top_depositor_name": "Anton Kowalczyk", "beneficiary_name": "Amberfield Trading Co"},
    {"customer_name": "Layla Haddad", "account_ref": "FUN008", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "distinct_source_regions": 2,
     "distinct_depositors": 11, "total_inflow_amount": 46400, "max_dwell_hours": 28,
     "top_beneficiary_amount": 16600, "total_outflow_amount": 45000,
     "top_depositor_name": "Farida Khalil", "beneficiary_name": "Bluecrest Export Group"},
    {"customer_name": "Boris Ivanov", "account_ref": "FUN009", "segment": "Retail",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "distinct_source_regions": 4,
     "distinct_depositors": 9, "total_inflow_amount": 49500, "max_dwell_hours": 26,
     "top_beneficiary_amount": 7200, "total_outflow_amount": 48000,
     "top_depositor_name": "Nikolai Volkov", "beneficiary_name": "Ironvale Commerce Ltd"},
    {"customer_name": "Nadia Farouk", "account_ref": "FUN010", "segment": "Private Banking",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "distinct_source_regions": 4,
     "distinct_depositors": 13, "total_inflow_amount": 53500, "max_dwell_hours": 24,
     "top_beneficiary_amount": 19200, "total_outflow_amount": 52000,
     "top_depositor_name": "Grace Muthoni", "beneficiary_name": "Whitmore Global Traders"},
    {"customer_name": "Emeka Chukwu", "account_ref": "FUN011", "segment": "Small Business",
     "home_branch": "Meridian Trust Bank - Central Branch", "distinct_source_regions": 4,
     "distinct_depositors": 14, "total_inflow_amount": 56500, "max_dwell_hours": 25,
     "top_beneficiary_amount": 35800, "total_outflow_amount": 55000,
     "top_depositor_name": "Diego Salazar", "beneficiary_name": "Coral Bay Exports Ltd"},
    {"customer_name": "Katarina Novakova", "account_ref": "FUN012", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "distinct_source_regions": 4,
     "distinct_depositors": 12, "total_inflow_amount": 59500, "max_dwell_hours": 8,
     "top_beneficiary_amount": 21500, "total_outflow_amount": 58000,
     "top_depositor_name": "Elin Karlsson", "beneficiary_name": "Granite Peak Holdings"},
    {"customer_name": "Hassan Al-Fayed", "account_ref": "FUN013", "segment": "Small Business",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "distinct_source_regions": 7,
     "distinct_depositors": 24, "total_inflow_amount": 62500, "max_dwell_hours": 9,
     "top_beneficiary_amount": 39600, "total_outflow_amount": 61000,
     "top_depositor_name": "Youssef Benali", "beneficiary_name": "Fenwick & Cole Trading"},
    {"customer_name": "Ines Moreau", "account_ref": "FUN014", "segment": "Private Banking",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "distinct_source_regions": 6,
     "distinct_depositors": 22, "total_inflow_amount": 65500, "max_dwell_hours": 11,
     "top_beneficiary_amount": 23700, "total_outflow_amount": 64000,
     "top_depositor_name": "Sana Malik", "beneficiary_name": "Redstone Commodities Ltd"},
    {"customer_name": "Oleg Petrenko", "account_ref": "FUN015", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "distinct_source_regions": 5,
     "distinct_depositors": 27, "total_inflow_amount": 61500, "max_dwell_hours": 32,
     "top_beneficiary_amount": 39000, "total_outflow_amount": 60000,
     "top_depositor_name": "Petra Novak", "beneficiary_name": "Solstice Trading Group"},
    {"customer_name": "Sara Lindberg", "account_ref": "FUN016", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Riverside Branch", "distinct_source_regions": 4,
     "distinct_depositors": 28, "total_inflow_amount": 63500, "max_dwell_hours": 7,
     "top_beneficiary_amount": 40300, "total_outflow_amount": 62000,
     "top_depositor_name": "Kwame Asante", "beneficiary_name": "Palmetto Export Co"},
    {"customer_name": "Adeyemi Balogun", "account_ref": "FUN017", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "distinct_source_regions": 7,
     "distinct_depositors": 25, "total_inflow_amount": 67500, "max_dwell_hours": 9,
     "top_beneficiary_amount": 59400, "total_outflow_amount": 66000,
     "top_depositor_name": "Ling Wei", "beneficiary_name": "Windrose Commerce Ltd"},
    {"customer_name": "Mikhail Sokolov", "account_ref": "FUN018", "segment": "Private Banking",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "distinct_source_regions": 8,
     "distinct_depositors": 23, "total_inflow_amount": 71500, "max_dwell_hours": 10,
     "top_beneficiary_amount": 45500, "total_outflow_amount": 70000,
     "top_depositor_name": "Ravi Menon", "beneficiary_name": "Kestrel Bay Holdings"},
    {"customer_name": "Zara Ahmed", "account_ref": "FUN019", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "distinct_source_regions": 9,
     "distinct_depositors": 33, "total_inflow_amount": 103000, "max_dwell_hours": 3,
     "top_beneficiary_amount": 90000, "total_outflow_amount": 100000,
     "top_depositor_name": "Aroha Ngata", "beneficiary_name": "Zeta Commodities Ltd"},
    {"customer_name": "Peter Kowalski", "account_ref": "FUN020", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "distinct_source_regions": 9,
     "distinct_depositors": 32, "total_inflow_amount": 92500, "max_dwell_hours": 4,
     "top_beneficiary_amount": 58500, "total_outflow_amount": 90000,
     "top_depositor_name": "Bashir Rahman", "beneficiary_name": "Everline Traders Ltd"},
    {"customer_name": "Yasmin Saleh", "account_ref": "FUN021", "segment": "Private Banking",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "distinct_source_regions": 9,
     "distinct_depositors": 31, "total_inflow_amount": 97500, "max_dwell_hours": 9,
     "top_beneficiary_amount": 85500, "total_outflow_amount": 95000,
     "top_depositor_name": "Chloe Fontaine", "beneficiary_name": "Northgate Commodities Ltd"},
    {"customer_name": "Ahmet Yildiz", "account_ref": "FUN022", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "distinct_source_regions": 7,
     "distinct_depositors": 34, "total_inflow_amount": 90500, "max_dwell_hours": 3,
     "top_beneficiary_amount": 79200, "total_outflow_amount": 88000,
     "top_depositor_name": "Dmitri Volkov", "beneficiary_name": "Stonebridge Export Group"},
]

# beneficiary_name, account_ref, bank, jurisdiction, relationship, prior_alerts
BENEFICIARIES: List[Dict[str, Any]] = [
    {"beneficiary_name": "Nova Horizon Traders Ltd", "account_ref": "FUN001", "bank": "Meridian Trust Bank",
     "jurisdiction": "Ireland", "relationship": "Trade counterparty", "prior_alerts": 0},
    {"beneficiary_name": "Silverpine Commerce Ltd", "account_ref": "FUN002", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Canada", "relationship": "Logistics partner", "prior_alerts": 0},
    {"beneficiary_name": "Meridian Bay Holdings", "account_ref": "FUN003", "bank": "Adriatic Union Bank",
     "jurisdiction": "Germany", "relationship": "Contractor payment", "prior_alerts": 0},
    {"beneficiary_name": "Crestwood Import Co", "account_ref": "FUN004", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Hong Kong", "relationship": "Import supplier", "prior_alerts": 1},
    {"beneficiary_name": "Zeta Commodities Ltd", "account_ref": "FUN005", "bank": "Helvetia Private Bank",
     "jurisdiction": "Marshall Islands", "relationship": "Commodities supplier", "prior_alerts": 0},
    {"beneficiary_name": "Harborstone Ventures Ltd", "account_ref": "FUN006", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Kingdom", "relationship": "Consulting retainer", "prior_alerts": 0},
    {"beneficiary_name": "Amberfield Trading Co", "account_ref": "FUN007", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Cyprus", "relationship": "Trade counterparty", "prior_alerts": 1},
    {"beneficiary_name": "Bluecrest Export Group", "account_ref": "FUN008", "bank": "Adriatic Union Bank",
     "jurisdiction": "Panama", "relationship": "Export supplier", "prior_alerts": 1},
    {"beneficiary_name": "Ironvale Commerce Ltd", "account_ref": "FUN009", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Singapore", "relationship": "Trade counterparty", "prior_alerts": 0},
    {"beneficiary_name": "Whitmore Global Traders", "account_ref": "FUN010", "bank": "Helvetia Private Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Logistics partner", "prior_alerts": 1},
    {"beneficiary_name": "Coral Bay Exports Ltd", "account_ref": "FUN011", "bank": "Meridian Trust Bank",
     "jurisdiction": "Turkey", "relationship": "Export supplier", "prior_alerts": 1},
    {"beneficiary_name": "Granite Peak Holdings", "account_ref": "FUN012", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Hong Kong", "relationship": "Contractor payment", "prior_alerts": 1},
    {"beneficiary_name": "Fenwick & Cole Trading", "account_ref": "FUN013", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Cyprus", "relationship": "Trade counterparty", "prior_alerts": 1},
    {"beneficiary_name": "Redstone Commodities Ltd", "account_ref": "FUN014", "bank": "Helvetia Private Bank",
     "jurisdiction": "Panama", "relationship": "Commodities supplier", "prior_alerts": 2},
    {"beneficiary_name": "Solstice Trading Group", "account_ref": "FUN015", "bank": "Meridian Trust Bank",
     "jurisdiction": "British Virgin Islands", "relationship": "Trade counterparty", "prior_alerts": 1},
    {"beneficiary_name": "Palmetto Export Co", "account_ref": "FUN016", "bank": "Continental Correspondent Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Export supplier", "prior_alerts": 2},
    {"beneficiary_name": "Windrose Commerce Ltd", "account_ref": "FUN017", "bank": "Adriatic Union Bank",
     "jurisdiction": "Hong Kong", "relationship": "Trade counterparty", "prior_alerts": 2},
    {"beneficiary_name": "Kestrel Bay Holdings", "account_ref": "FUN018", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Panama", "relationship": "Commodities supplier", "prior_alerts": 2},
    {"beneficiary_name": "Zeta Commodities Ltd", "account_ref": "FUN019", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Marshall Islands", "relationship": "Commodities supplier", "prior_alerts": 2},
    {"beneficiary_name": "Everline Traders Ltd", "account_ref": "FUN020", "bank": "Adriatic Union Bank",
     "jurisdiction": "Panama", "relationship": "Trade counterparty", "prior_alerts": 3},
    {"beneficiary_name": "Northgate Commodities Ltd", "account_ref": "FUN021", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Turkey", "relationship": "Commodities supplier", "prior_alerts": 3},
    {"beneficiary_name": "Stonebridge Export Group", "account_ref": "FUN022", "bank": "Helvetia Private Bank",
     "jurisdiction": "Panama", "relationship": "Export supplier", "prior_alerts": 2},
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
