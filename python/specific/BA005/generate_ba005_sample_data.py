"""Generate synthetic sample data for BA005 Rapid Movement.

22 accounts (>= the 2026-08-09 20-row standard; BA005 is NOT grandfathered), spread
across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  RM001-RM006   Low       (15)
  RM007-RM012   Medium    (45)
  RM013-RM018   High      (70)
  RM019-RM022   Critical  (83-90) -- at least two, per the house standard

Fusion bridge: RM019 (Dmitri Petrov, 90/Critical, the single highest-scoring account in
the set) clears its outbound leg through **Zeta Commodities Ltd** as its first onward
destination -- the same real-world entity already in the estate network (BA002's FUN019
beneficiary / NI004's C006) -- so canonical entity resolution joins BA005 onto the
existing fused case. Being the top-scored account matters: the FC-10 adapter builds its
case/graph from the single highest exposure_score row, so the Zeta bridge has to be that
row, not merely a Critical row. RM019 also routes its second leg through **Continental
Correspondent Bank**, the bank shared across the BA004/BA005/BA008 correspondent-banking
chain (per the fc-06 design). Continental Correspondent Bank recurs as a second onward
destination across several other rows too (RM005, RM010, RM015, RM020, RM022), consistent
with it being a shared correspondent bank the wider BA0NN family keeps referencing.

Run:  python3 generate_ba005_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# customer_name, account_ref, segment, home_branch, source_name, inbound_amount,
# outbound_amount, dwell_time_hours, avg_balance, total_turnover_amount,
# distinct_destination_count, first_destination_name, second_destination_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"customer_name": "Ingrid Solberg", "account_ref": "RM001", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - North Branch", "source_name": "Blue Harbour Logistics Ltd",
     "inbound_amount": 20000, "outbound_amount": 8000, "dwell_time_hours": 960,
     "avg_balance": 15000, "total_turnover_amount": 30000, "distinct_destination_count": 1,
     "first_destination_name": "Hollow Pine Traders", "second_destination_name": "Adriatic Union Bank"},
    {"customer_name": "Mateus Silva", "account_ref": "RM002", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "source_name": "Cedar & Vale Trading Ltd",
     "inbound_amount": 21000, "outbound_amount": 9000, "dwell_time_hours": 900,
     "avg_balance": 14000, "total_turnover_amount": 32000, "distinct_destination_count": 2,
     "first_destination_name": "Amberlight Commerce Ltd", "second_destination_name": "Pacific Rim Commercial Bank"},
    {"customer_name": "Chidi Obiora", "account_ref": "RM003", "segment": "Private Banking",
     "home_branch": "Adriatic Union Bank - Old Port Branch", "source_name": "Northwind Freight Co",
     "inbound_amount": 22000, "outbound_amount": 9500, "dwell_time_hours": 850,
     "avg_balance": 13500, "total_turnover_amount": 34000, "distinct_destination_count": 1,
     "first_destination_name": "Driftwood Export Co", "second_destination_name": "Helvetia Private Bank"},
    {"customer_name": "Freya Andersen", "account_ref": "RM004", "segment": "Retail",
     "home_branch": "Pacific Rim Commercial Bank - Summit Branch", "source_name": "Solano Exchange House",
     "inbound_amount": 23000, "outbound_amount": 10500, "dwell_time_hours": 800,
     "avg_balance": 13000, "total_turnover_amount": 36000, "distinct_destination_count": 2,
     "first_destination_name": "Silverline Holdings", "second_destination_name": "Meridian Trust Bank"},
    {"customer_name": "Hana Kobayashi", "account_ref": "RM005", "segment": "Small Business",
     "home_branch": "Helvetia Private Bank - Bayview Branch", "source_name": "Kestrel Cash & Carry Ltd",
     "inbound_amount": 24000, "outbound_amount": 11000, "dwell_time_hours": 750,
     "avg_balance": 16000, "total_turnover_amount": 38000, "distinct_destination_count": 1,
     "first_destination_name": "Cinder Bay Trading", "second_destination_name": "Continental Correspondent Bank"},
    {"customer_name": "Rafael Torres", "account_ref": "RM006", "segment": "Private Banking",
     "home_branch": "Meridian Trust Bank - North Branch", "source_name": "Blue Harbour Logistics Ltd",
     "inbound_amount": 25000, "outbound_amount": 12000, "dwell_time_hours": 700,
     "avg_balance": 17000, "total_turnover_amount": 40000, "distinct_destination_count": 2,
     "first_destination_name": "Wrenhaven Commerce Ltd", "second_destination_name": "Adriatic Union Bank"},
    {"customer_name": "Amina Diallo", "account_ref": "RM007", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "source_name": "Cedar & Vale Trading Ltd",
     "inbound_amount": 70000, "outbound_amount": 45000, "dwell_time_hours": 40,
     "avg_balance": 15000, "total_turnover_amount": 60000, "distinct_destination_count": 3,
     "first_destination_name": "Foxglen Export Group", "second_destination_name": "Pacific Rim Commercial Bank"},
    {"customer_name": "Lars Eriksson", "account_ref": "RM008", "segment": "Small Business",
     "home_branch": "Adriatic Union Bank - Old Port Branch", "source_name": "Northwind Freight Co",
     "inbound_amount": 72000, "outbound_amount": 48000, "dwell_time_hours": 36,
     "avg_balance": 14000, "total_turnover_amount": 64000, "distinct_destination_count": 4,
     "first_destination_name": "Marlstone Traders", "second_destination_name": "Helvetia Private Bank"},
    {"customer_name": "Nadia Petrova", "account_ref": "RM009", "segment": "Private Banking",
     "home_branch": "Pacific Rim Commercial Bank - Summit Branch", "source_name": "Solano Exchange House",
     "inbound_amount": 74000, "outbound_amount": 50000, "dwell_time_hours": 30,
     "avg_balance": 13000, "total_turnover_amount": 68000, "distinct_destination_count": 3,
     "first_destination_name": "Ashcombe Holdings", "second_destination_name": "Meridian Trust Bank"},
    {"customer_name": "Kwame Mensah", "account_ref": "RM010", "segment": "Retail",
     "home_branch": "Helvetia Private Bank - Bayview Branch", "source_name": "Kestrel Cash & Carry Ltd",
     "inbound_amount": 76000, "outbound_amount": 53000, "dwell_time_hours": 24,
     "avg_balance": 12000, "total_turnover_amount": 70000, "distinct_destination_count": 4,
     "first_destination_name": "Brackenridge Trading Co", "second_destination_name": "Continental Correspondent Bank"},
    {"customer_name": "Sanne de Vries", "account_ref": "RM011", "segment": "Small Business",
     "home_branch": "Meridian Trust Bank - North Branch", "source_name": "Blue Harbour Logistics Ltd",
     "inbound_amount": 78000, "outbound_amount": 55000, "dwell_time_hours": 20,
     "avg_balance": 11500, "total_turnover_amount": 74000, "distinct_destination_count": 3,
     "first_destination_name": "Thistlewood Commerce", "second_destination_name": "Adriatic Union Bank"},
    {"customer_name": "Diego Fernandez", "account_ref": "RM012", "segment": "Private Banking",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "source_name": "Cedar & Vale Trading Ltd",
     "inbound_amount": 80000, "outbound_amount": 58000, "dwell_time_hours": 14,
     "avg_balance": 11000, "total_turnover_amount": 78000, "distinct_destination_count": 4,
     "first_destination_name": "Copperfield Exports Ltd", "second_destination_name": "Pacific Rim Commercial Bank"},
    {"customer_name": "Yara Haddad", "account_ref": "RM013", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Port Branch", "source_name": "Northwind Freight Co",
     "inbound_amount": 80000, "outbound_amount": 68000, "dwell_time_hours": 10,
     "avg_balance": 12000, "total_turnover_amount": 150000, "distinct_destination_count": 5,
     "first_destination_name": "Ravenswood Traders", "second_destination_name": "Helvetia Private Bank"},
    {"customer_name": "Erik Solheim", "account_ref": "RM014", "segment": "Small Business",
     "home_branch": "Pacific Rim Commercial Bank - Summit Branch", "source_name": "Solano Exchange House",
     "inbound_amount": 82000, "outbound_amount": 70000, "dwell_time_hours": 8,
     "avg_balance": 11000, "total_turnover_amount": 160000, "distinct_destination_count": 6,
     "first_destination_name": "Hawthorn Bay Holdings", "second_destination_name": "Meridian Trust Bank"},
    {"customer_name": "Priya Chandran", "account_ref": "RM015", "segment": "Private Banking",
     "home_branch": "Helvetia Private Bank - Bayview Branch", "source_name": "Kestrel Cash & Carry Ltd",
     "inbound_amount": 84000, "outbound_amount": 72000, "dwell_time_hours": 6,
     "avg_balance": 10500, "total_turnover_amount": 170000, "distinct_destination_count": 5,
     "first_destination_name": "Millbrook Export Co", "second_destination_name": "Continental Correspondent Bank"},
    {"customer_name": "Tariq Aziz", "account_ref": "RM016", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - North Branch", "source_name": "Blue Harbour Logistics Ltd",
     "inbound_amount": 86000, "outbound_amount": 75000, "dwell_time_hours": 5,
     "avg_balance": 10000, "total_turnover_amount": 180000, "distinct_destination_count": 7,
     "first_destination_name": "Stonebridge Commerce Ltd", "second_destination_name": "Adriatic Union Bank"},
    {"customer_name": "Elin Johansson", "account_ref": "RM017", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "source_name": "Cedar & Vale Trading Ltd",
     "inbound_amount": 88000, "outbound_amount": 77000, "dwell_time_hours": 4,
     "avg_balance": 9800, "total_turnover_amount": 185000, "distinct_destination_count": 6,
     "first_destination_name": "Larchfield Traders", "second_destination_name": "Pacific Rim Commercial Bank"},
    {"customer_name": "Marco Rinaldi", "account_ref": "RM018", "segment": "Private Banking",
     "home_branch": "Adriatic Union Bank - Old Port Branch", "source_name": "Northwind Freight Co",
     "inbound_amount": 90000, "outbound_amount": 78000, "dwell_time_hours": 3,
     "avg_balance": 9500, "total_turnover_amount": 188000, "distinct_destination_count": 7,
     "first_destination_name": "Windermere Holdings", "second_destination_name": "Helvetia Private Bank"},
    {"customer_name": "Dmitri Petrov", "account_ref": "RM019", "segment": "Retail",
     "home_branch": "Pacific Rim Commercial Bank - Summit Branch", "source_name": "Kestrel Cash & Carry Ltd",
     "inbound_amount": 100000, "outbound_amount": 98000, "dwell_time_hours": 1,
     "avg_balance": 10000, "total_turnover_amount": 300000, "distinct_destination_count": 9,
     "first_destination_name": "Zeta Commodities Ltd", "second_destination_name": "Continental Correspondent Bank"},
    {"customer_name": "Aisha Rahman", "account_ref": "RM020", "segment": "Small Business",
     "home_branch": "Helvetia Private Bank - Bayview Branch", "source_name": "Blue Harbour Logistics Ltd",
     "inbound_amount": 97000, "outbound_amount": 88000, "dwell_time_hours": 1.5,
     "avg_balance": 9800, "total_turnover_amount": 280000, "distinct_destination_count": 8,
     "first_destination_name": "Northwind Freight Co", "second_destination_name": "Continental Correspondent Bank"},
    {"customer_name": "Tomas Novak", "account_ref": "RM021", "segment": "Private Banking",
     "home_branch": "Meridian Trust Bank - North Branch", "source_name": "Cedar & Vale Trading Ltd",
     "inbound_amount": 92000, "outbound_amount": 90000, "dwell_time_hours": 1,
     "avg_balance": 9500, "total_turnover_amount": 150000, "distinct_destination_count": 10,
     "first_destination_name": "Solano Exchange House", "second_destination_name": "Adriatic Union Bank"},
    {"customer_name": "Maria Kovač", "account_ref": "RM022", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "source_name": "Solano Exchange House",
     "inbound_amount": 90000, "outbound_amount": 88000, "dwell_time_hours": 5,
     "avg_balance": 9000, "total_turnover_amount": 310000, "distinct_destination_count": 12,
     "first_destination_name": "Cedar & Vale Trading Ltd", "second_destination_name": "Continental Correspondent Bank"},
]

# first_destination_name, account_ref, bank, jurisdiction, relationship, prior_alerts
DESTINATIONS: List[Dict[str, Any]] = [
    {"first_destination_name": "Hollow Pine Traders", "account_ref": "RM001", "bank": "Adriatic Union Bank",
     "jurisdiction": "Ireland", "relationship": "Unverified counterparty", "prior_alerts": 0},
    {"first_destination_name": "Amberlight Commerce Ltd", "account_ref": "RM002", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Canada", "relationship": "Unverified counterparty", "prior_alerts": 0},
    {"first_destination_name": "Driftwood Export Co", "account_ref": "RM003", "bank": "Helvetia Private Bank",
     "jurisdiction": "Germany", "relationship": "Unverified counterparty", "prior_alerts": 0},
    {"first_destination_name": "Silverline Holdings", "account_ref": "RM004", "bank": "Meridian Trust Bank",
     "jurisdiction": "Hong Kong", "relationship": "Unverified counterparty", "prior_alerts": 0},
    {"first_destination_name": "Cinder Bay Trading", "account_ref": "RM005", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Switzerland", "relationship": "Unverified counterparty", "prior_alerts": 0},
    {"first_destination_name": "Wrenhaven Commerce Ltd", "account_ref": "RM006", "bank": "Adriatic Union Bank",
     "jurisdiction": "United Kingdom", "relationship": "Unverified counterparty", "prior_alerts": 0},
    {"first_destination_name": "Foxglen Export Group", "account_ref": "RM007", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Cyprus", "relationship": "Unverified counterparty", "prior_alerts": 1},
    {"first_destination_name": "Marlstone Traders", "account_ref": "RM008", "bank": "Helvetia Private Bank",
     "jurisdiction": "Panama", "relationship": "Unverified counterparty", "prior_alerts": 1},
    {"first_destination_name": "Ashcombe Holdings", "account_ref": "RM009", "bank": "Meridian Trust Bank",
     "jurisdiction": "Singapore", "relationship": "Unverified counterparty", "prior_alerts": 1},
    {"first_destination_name": "Brackenridge Trading Co", "account_ref": "RM010", "bank": "Continental Correspondent Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Money service business", "prior_alerts": 1},
    {"first_destination_name": "Thistlewood Commerce", "account_ref": "RM011", "bank": "Adriatic Union Bank",
     "jurisdiction": "Turkey", "relationship": "Unverified counterparty", "prior_alerts": 1},
    {"first_destination_name": "Copperfield Exports Ltd", "account_ref": "RM012", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "British Virgin Islands", "relationship": "Unverified counterparty", "prior_alerts": 1},
    {"first_destination_name": "Ravenswood Traders", "account_ref": "RM013", "bank": "Helvetia Private Bank",
     "jurisdiction": "Ireland", "relationship": "Unverified counterparty", "prior_alerts": 2},
    {"first_destination_name": "Hawthorn Bay Holdings", "account_ref": "RM014", "bank": "Meridian Trust Bank",
     "jurisdiction": "Canada", "relationship": "Unverified counterparty", "prior_alerts": 2},
    {"first_destination_name": "Millbrook Export Co", "account_ref": "RM015", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Germany", "relationship": "Unverified counterparty", "prior_alerts": 2},
    {"first_destination_name": "Stonebridge Commerce Ltd", "account_ref": "RM016", "bank": "Adriatic Union Bank",
     "jurisdiction": "Hong Kong", "relationship": "Unverified counterparty", "prior_alerts": 2},
    {"first_destination_name": "Larchfield Traders", "account_ref": "RM017", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Switzerland", "relationship": "Unverified counterparty", "prior_alerts": 2},
    {"first_destination_name": "Windermere Holdings", "account_ref": "RM018", "bank": "Helvetia Private Bank",
     "jurisdiction": "United Kingdom", "relationship": "Unverified counterparty", "prior_alerts": 2},
    {"first_destination_name": "Zeta Commodities Ltd", "account_ref": "RM019", "bank": "Adriatic Union Bank",
     "jurisdiction": "Cyprus", "relationship": "Onward beneficiary (network entity)", "prior_alerts": 3},
    {"first_destination_name": "Northwind Freight Co", "account_ref": "RM020", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Panama", "relationship": "Unverified counterparty", "prior_alerts": 3},
    {"first_destination_name": "Solano Exchange House", "account_ref": "RM021", "bank": "Helvetia Private Bank",
     "jurisdiction": "Singapore", "relationship": "Money service business", "prior_alerts": 3},
    {"first_destination_name": "Cedar & Vale Trading Ltd", "account_ref": "RM022", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Unverified counterparty", "prior_alerts": 3},
]

_TABLES = {"accounts.csv": ACCOUNTS, "destinations.csv": DESTINATIONS}


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
