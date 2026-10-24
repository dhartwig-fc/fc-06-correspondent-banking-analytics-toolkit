"""Generate synthetic sample data for BA007 Cash Intensive Activity.

22 cash-intensive business accounts (>= the 2026-08-09 20-row standard; BA007 is NOT
grandfathered), spread across all four exposure bands so the scorer visibly
discriminates rather than rubber-stamping every row:

  CIA001-CIA006   Low       (15)
  CIA007-CIA012   Medium    (45)
  CIA013-CIA018   High      (65)
  CIA019-CIA022   Critical  (86-90)  -- at least two, per the house standard

Fusion bridge: CIA019 (**Gammavane Imports Ltd**, 90/Critical, the single highest-scoring
account in the set) IS the bridge -- unlike BA001-BA006, where the bridge entity is a
CONNECTED entity, BA007 is a designated bridge typology where the SUBJECT ITSELF is
Gammavane Imports Ltd, an entity already in the estate network (SAN002's tier-2 nominee
C003 / BA001's and BA004's beneficiary). This shows Gamma's own cash-intensive
behaviour fusing with its sanctions/network flags. Being the top-scored account
matters: the FC-10 adapter builds its case/graph from the single highest
exposure_score row, so Gamma has to be that row, not merely a Critical row.
CIA020 (Kestrel Cash & Carry Ltd) and CIA021 (Solano Exchange House) are the other two
named cash-intensive archetypes from the shared entity universe, also Critical but
strictly below Gamma so the bridge is unambiguous.

Run:  python3 generate_ba007_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# customer_name, account_ref, segment, home_branch, cash_deposits_amount,
# total_turnover_amount, peer_norm_cash_ratio, declared_annual_cash_volume,
# deposit_cv_pct, third_party_deposit_amount, total_deposit_amount, top_depositor_name,
# linked_entity_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"customer_name": "Harborlight Grocers Ltd", "account_ref": "CIA001", "segment": "Grocery Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "cash_deposits_amount": 42000,
     "total_turnover_amount": 520000, "peer_norm_cash_ratio": 0.15, "declared_annual_cash_volume": 45000,
     "deposit_cv_pct": 55, "third_party_deposit_amount": 800, "total_deposit_amount": 42000,
     "top_depositor_name": "Elena Puddlefiddle", "linked_entity_name": "Coral Bay Provisions Ltd"},
    {"customer_name": "Union Square Bakery", "account_ref": "CIA002", "segment": "Bakery",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "cash_deposits_amount": 38000,
     "total_turnover_amount": 480000, "peer_norm_cash_ratio": 0.15, "declared_annual_cash_volume": 40000,
     "deposit_cv_pct": 60, "third_party_deposit_amount": 500, "total_deposit_amount": 38000,
     "top_depositor_name": "Tobias Saltquill", "linked_entity_name": "Wrenfield Supply Co"},
    {"customer_name": "Riverside Hardware Co", "account_ref": "CIA003", "segment": "Hardware Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "cash_deposits_amount": 51000,
     "total_turnover_amount": 600000, "peer_norm_cash_ratio": 0.15, "declared_annual_cash_volume": 54000,
     "deposit_cv_pct": 50, "third_party_deposit_amount": 1200, "total_deposit_amount": 51000,
     "top_depositor_name": "Priya Hazelwhistle", "linked_entity_name": "Thistlefiddle Distributors Ltd"},
    {"customer_name": "Marblecrest Pharmacy", "account_ref": "CIA004", "segment": "Pharmacy",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "cash_deposits_amount": 60000,
     "total_turnover_amount": 700000, "peer_norm_cash_ratio": 0.15, "declared_annual_cash_volume": 62000,
     "deposit_cv_pct": 58, "third_party_deposit_amount": 900, "total_deposit_amount": 60000,
     "top_depositor_name": "Marco Cindercrumb", "linked_entity_name": "Thistledown Trading Co"},
    {"customer_name": "Cobblestone Deli", "account_ref": "CIA005", "segment": "Food Service",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "cash_deposits_amount": 47000,
     "total_turnover_amount": 560000, "peer_norm_cash_ratio": 0.15, "declared_annual_cash_volume": 50000,
     "deposit_cv_pct": 52, "third_party_deposit_amount": 700, "total_deposit_amount": 47000,
     "top_depositor_name": "Fatima Brindlewisp", "linked_entity_name": "Larkspur Wholesale Ltd"},
    {"customer_name": "Lantern Hill Bookstore", "account_ref": "CIA006", "segment": "Retail - Books",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "cash_deposits_amount": 55000,
     "total_turnover_amount": 640000, "peer_norm_cash_ratio": 0.15, "declared_annual_cash_volume": 58000,
     "deposit_cv_pct": 47, "third_party_deposit_amount": 1000, "total_deposit_amount": 55000,
     "top_depositor_name": "Owen Saltwisp", "linked_entity_name": "Millbrook Commerce Group"},
    {"customer_name": "Golden Anchor Diner", "account_ref": "CIA007", "segment": "Food Service",
     "home_branch": "Continental Correspondent Bank - Riverside Branch", "cash_deposits_amount": 130000,
     "total_turnover_amount": 480000, "peer_norm_cash_ratio": 0.16, "declared_annual_cash_volume": 92000,
     "deposit_cv_pct": 38, "third_party_deposit_amount": 8000, "total_deposit_amount": 130000,
     "top_depositor_name": "Ingrid Hazelwisp", "linked_entity_name": "Foxglove Import Co"},
    {"customer_name": "Silver Fox Salon & Spa", "account_ref": "CIA008", "segment": "Personal Care",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "cash_deposits_amount": 145000,
     "total_turnover_amount": 540000, "peer_norm_cash_ratio": 0.16, "declared_annual_cash_volume": 103000,
     "deposit_cv_pct": 35, "third_party_deposit_amount": 10000, "total_deposit_amount": 145000,
     "top_depositor_name": "Rafael Lanternquill", "linked_entity_name": "Thistlekettle & Sons Trading"},
    {"customer_name": "Hazelthimble Car Wash", "account_ref": "CIA009", "segment": "Vehicle Services",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "cash_deposits_amount": 120000,
     "total_turnover_amount": 430000, "peer_norm_cash_ratio": 0.16, "declared_annual_cash_volume": 86000,
     "deposit_cv_pct": 40, "third_party_deposit_amount": 7500, "total_deposit_amount": 120000,
     "top_depositor_name": "Noor Copperbristle", "linked_entity_name": "Ivory Coast Provisioning Ltd"},
    {"customer_name": "Blue Ridge Laundromat", "account_ref": "CIA010", "segment": "Laundry Services",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "cash_deposits_amount": 155000,
     "total_turnover_amount": 580000, "peer_norm_cash_ratio": 0.16, "declared_annual_cash_volume": 110000,
     "deposit_cv_pct": 33, "third_party_deposit_amount": 11000, "total_deposit_amount": 155000,
     "top_depositor_name": "Callum Wrenkettle", "linked_entity_name": "Juniper Ridge Holdings"},
    {"customer_name": "Emberton Vending Co", "account_ref": "CIA011", "segment": "Vending Operations",
     "home_branch": "Meridian Trust Bank - Central Branch", "cash_deposits_amount": 135000,
     "total_turnover_amount": 500000, "peer_norm_cash_ratio": 0.16, "declared_annual_cash_volume": 96000,
     "deposit_cv_pct": 36, "third_party_deposit_amount": 9000, "total_deposit_amount": 135000,
     "top_depositor_name": "Sofia Sorrelkettle", "linked_entity_name": "Cloverwisp Mercantile Co"},
    {"customer_name": "Trailside Convenience Mart", "account_ref": "CIA012", "segment": "Convenience Retail",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "cash_deposits_amount": 165000,
     "total_turnover_amount": 620000, "peer_norm_cash_ratio": 0.16, "declared_annual_cash_volume": 118000,
     "deposit_cv_pct": 32, "third_party_deposit_amount": 12000, "total_deposit_amount": 165000,
     "top_depositor_name": "Aditya Juniperbristle", "linked_entity_name": "Emberfiddle Distribution Ltd"},
    {"customer_name": "Highcairn Point Amusement Arcade", "account_ref": "CIA013", "segment": "Amusement & Gaming",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "cash_deposits_amount": 260000,
     "total_turnover_amount": 620000, "peer_norm_cash_ratio": 0.22, "declared_annual_cash_volume": 140000,
     "deposit_cv_pct": 24, "third_party_deposit_amount": 22000, "total_deposit_amount": 260000,
     "top_depositor_name": "Beatrix Nettlewhistle", "linked_entity_name": "Moorland Supply Group"},
    {"customer_name": "Nightingale Nightclub Group", "account_ref": "CIA014", "segment": "Hospitality & Nightlife",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "cash_deposits_amount": 300000,
     "total_turnover_amount": 700000, "peer_norm_cash_ratio": 0.22, "declared_annual_cash_volume": 165000,
     "deposit_cv_pct": 22, "third_party_deposit_amount": 28000, "total_deposit_amount": 300000,
     "top_depositor_name": "Julian Parsleybristle", "linked_entity_name": "Nightjar Trading Co"},
    {"customer_name": "Palermo Pizzeria Chain", "account_ref": "CIA015", "segment": "Food Service",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "cash_deposits_amount": 240000,
     "total_turnover_amount": 560000, "peer_norm_cash_ratio": 0.22, "declared_annual_cash_volume": 128000,
     "deposit_cv_pct": 26, "third_party_deposit_amount": 20000, "total_deposit_amount": 240000,
     "top_depositor_name": "Camila Yarrowcrumb", "linked_entity_name": "Oakhurst Provisions Ltd"},
    {"customer_name": "Coastal Fuel & Mart", "account_ref": "CIA016", "segment": "Fuel & Convenience",
     "home_branch": "Continental Correspondent Bank - Riverside Branch", "cash_deposits_amount": 330000,
     "total_turnover_amount": 760000, "peer_norm_cash_ratio": 0.22, "declared_annual_cash_volume": 178000,
     "deposit_cv_pct": 20, "third_party_deposit_amount": 32000, "total_deposit_amount": 330000,
     "top_depositor_name": "Dawit Tallowspindle", "linked_entity_name": "Pinehollow Wholesale Ltd"},
    {"customer_name": "Ridgeline Pawn Exchange", "account_ref": "CIA017", "segment": "Pawn & Secondhand",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "cash_deposits_amount": 280000,
     "total_turnover_amount": 640000, "peer_norm_cash_ratio": 0.22, "declared_annual_cash_volume": 152000,
     "deposit_cv_pct": 23, "third_party_deposit_amount": 25000, "total_deposit_amount": 280000,
     "top_depositor_name": "Freya Puddlethimble", "linked_entity_name": "Quillfeather Commerce Ltd"},
    {"customer_name": "Sunset Strip Casino Cage", "account_ref": "CIA018", "segment": "Gaming & Casino",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "cash_deposits_amount": 350000,
     "total_turnover_amount": 800000, "peer_norm_cash_ratio": 0.22, "declared_annual_cash_volume": 190000,
     "deposit_cv_pct": 19, "third_party_deposit_amount": 35000, "total_deposit_amount": 350000,
     "top_depositor_name": "Mateus Quillmote", "linked_entity_name": "Ravensworth Trading Co"},
    {"customer_name": "Gammavane Imports Ltd", "account_ref": "CIA019", "segment": "Import / Trading",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "cash_deposits_amount": 760000,
     "total_turnover_amount": 820000, "peer_norm_cash_ratio": 0.30, "declared_annual_cash_volume": 300000,
     "deposit_cv_pct": 8, "third_party_deposit_amount": 250000, "total_deposit_amount": 760000,
     "top_depositor_name": "Naledi Marrowmote", "linked_entity_name": "Silverlake Provisioning Ltd"},
    {"customer_name": "Kestrel Cash & Carry Ltd", "account_ref": "CIA020", "segment": "Cash & Carry Wholesale",
     "home_branch": "Meridian Trust Bank - Central Branch", "cash_deposits_amount": 640000,
     "total_turnover_amount": 700000, "peer_norm_cash_ratio": 0.35, "declared_annual_cash_volume": 260000,
     "deposit_cv_pct": 10, "third_party_deposit_amount": 100000, "total_deposit_amount": 640000,
     "top_depositor_name": "Piotr Kettlecrumb", "linked_entity_name": "Wrenbristle Wholesale Group"},
    {"customer_name": "Solano Exchange House", "account_ref": "CIA021", "segment": "Currency Exchange",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "cash_deposits_amount": 590000,
     "total_turnover_amount": 650000, "peer_norm_cash_ratio": 0.32, "declared_annual_cash_volume": 240000,
     "deposit_cv_pct": 11, "third_party_deposit_amount": 92000, "total_deposit_amount": 590000,
     "top_depositor_name": "Rosalind Thimblespindle", "linked_entity_name": "Junipercrumb Exchange Partners"},
    {"customer_name": "Ironclad Bullion Exchange Ltd", "account_ref": "CIA022", "segment": "Bullion & Currency Exchange",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "cash_deposits_amount": 520000,
     "total_turnover_amount": 590000, "peer_norm_cash_ratio": 0.34, "declared_annual_cash_volume": 210000,
     "deposit_cv_pct": 12, "third_party_deposit_amount": 80000, "total_deposit_amount": 520000,
     "top_depositor_name": "Sami Sorrelwhistle", "linked_entity_name": "Vesper Bullion Partners Ltd"},
]

# linked_entity_name, account_ref, bank, jurisdiction, relationship, prior_alerts
DEPOSITORS: List[Dict[str, Any]] = [
    {"linked_entity_name": "Coral Bay Provisions Ltd", "account_ref": "CIA001", "bank": "Meridian Trust Bank",
     "jurisdiction": "Ireland", "relationship": "Goods supplier", "prior_alerts": 0},
    {"linked_entity_name": "Wrenfield Supply Co", "account_ref": "CIA002", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Canada", "relationship": "Ingredient supplier", "prior_alerts": 0},
    {"linked_entity_name": "Thistlefiddle Distributors Ltd", "account_ref": "CIA003", "bank": "Adriatic Union Bank",
     "jurisdiction": "Germany", "relationship": "Stock distributor", "prior_alerts": 0},
    {"linked_entity_name": "Thistledown Trading Co", "account_ref": "CIA004", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Hong Kong", "relationship": "Pharmaceutical distributor", "prior_alerts": 1},
    {"linked_entity_name": "Larkspur Wholesale Ltd", "account_ref": "CIA005", "bank": "Helvetia Private Bank",
     "jurisdiction": "France", "relationship": "Food supplier", "prior_alerts": 0},
    {"linked_entity_name": "Millbrook Commerce Group", "account_ref": "CIA006", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Kingdom", "relationship": "Stock distributor", "prior_alerts": 0},
    {"linked_entity_name": "Foxglove Import Co", "account_ref": "CIA007", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Cyprus", "relationship": "Ingredient supplier", "prior_alerts": 1},
    {"linked_entity_name": "Thistlekettle & Sons Trading", "account_ref": "CIA008", "bank": "Adriatic Union Bank",
     "jurisdiction": "Panama", "relationship": "Supply agent", "prior_alerts": 1},
    {"linked_entity_name": "Ivory Coast Provisioning Ltd", "account_ref": "CIA009", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Singapore", "relationship": "Equipment supplier", "prior_alerts": 0},
    {"linked_entity_name": "Juniper Ridge Holdings", "account_ref": "CIA010", "bank": "Helvetia Private Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Equipment lessor", "prior_alerts": 1},
    {"linked_entity_name": "Cloverwisp Mercantile Co", "account_ref": "CIA011", "bank": "Meridian Trust Bank",
     "jurisdiction": "Turkey", "relationship": "Stock supplier", "prior_alerts": 1},
    {"linked_entity_name": "Emberfiddle Distribution Ltd", "account_ref": "CIA012", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Hong Kong", "relationship": "Stock distributor", "prior_alerts": 1},
    {"linked_entity_name": "Moorland Supply Group", "account_ref": "CIA013", "bank": "Adriatic Union Bank",
     "jurisdiction": "Cyprus", "relationship": "Equipment supplier", "prior_alerts": 1},
    {"linked_entity_name": "Nightjar Trading Co", "account_ref": "CIA014", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Panama", "relationship": "Beverage supplier", "prior_alerts": 2},
    {"linked_entity_name": "Oakhurst Provisions Ltd", "account_ref": "CIA015", "bank": "Meridian Trust Bank",
     "jurisdiction": "British Virgin Islands", "relationship": "Ingredient supplier", "prior_alerts": 1},
    {"linked_entity_name": "Pinehollow Wholesale Ltd", "account_ref": "CIA016", "bank": "Continental Correspondent Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Fuel supplier", "prior_alerts": 2},
    {"linked_entity_name": "Quillfeather Commerce Ltd", "account_ref": "CIA017", "bank": "Adriatic Union Bank",
     "jurisdiction": "Hong Kong", "relationship": "Goods consignor", "prior_alerts": 2},
    {"linked_entity_name": "Ravensworth Trading Co", "account_ref": "CIA018", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Panama", "relationship": "Gaming equipment supplier", "prior_alerts": 2},
    {"linked_entity_name": "Silverlake Provisioning Ltd", "account_ref": "CIA019", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Marshall Islands", "relationship": "Import consignor", "prior_alerts": 3},
    {"linked_entity_name": "Wrenbristle Wholesale Group", "account_ref": "CIA020", "bank": "Meridian Trust Bank",
     "jurisdiction": "Panama", "relationship": "Wholesale consignor", "prior_alerts": 3},
    {"linked_entity_name": "Junipercrumb Exchange Partners", "account_ref": "CIA021", "bank": "Adriatic Union Bank",
     "jurisdiction": "Turkey", "relationship": "Currency wholesaler", "prior_alerts": 3},
    {"linked_entity_name": "Vesper Bullion Partners Ltd", "account_ref": "CIA022", "bank": "Helvetia Private Bank",
     "jurisdiction": "Panama", "relationship": "Bullion consignor", "prior_alerts": 2},
]

_TABLES = {"accounts.csv": ACCOUNTS, "depositors.csv": DEPOSITORS}


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
