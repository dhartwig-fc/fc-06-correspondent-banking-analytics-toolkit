"""Generate synthetic sample data for BA006 Dormant Reactivation.

22 accounts (>= the 2026-08-09 20-row standard; BA006 is NOT grandfathered), spread across
all four exposure bands so the scorer visibly discriminates rather than rubber-stamping
every row:

  DR001-DR006   Low       (15)
  DR007-DR012   Medium    (45)
  DR013-DR018   High      (70)
  DR019-DR022   Critical  (84-90) -- at least two, per the house standard

Fusion bridge: DR019 (Viktor Tallowbristle, 90/Critical, the single highest-scoring account in
the set) reactivates into **Alpha Trading Ltd** as its first reactivation counterparty --
the same real-world entity already in the estate network (BA003's MUL019 forwarding
destination / NI004's C001 / NI001's REG-2001) -- so canonical entity resolution joins BA006
onto the existing fused case. Being the top-scored account matters: the FC-10 adapter builds
its case/graph from the single highest exposure_score row, so the Alpha Trading Ltd bridge
has to be that row, not merely a Critical row. DR019 also clears its second leg through
**Continental Correspondent Bank**, the bank shared across the BA004/BA005/BA006/BA008
correspondent-banking chain (per the fc-06 design).

Run:  python3 generate_ba006_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# customer_name, account_ref, segment, home_branch, prior_counterparty_name,
# pre_dormancy_avg_monthly_activity, reactivation_amount, dormancy_days,
# new_counterparty_count, outflow_amount, first_reactivation_counterparty_name,
# second_reactivation_counterparty_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"customer_name": "Aiden Kettletumble", "account_ref": "DR001", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - North Branch", "prior_counterparty_name": "Oakhurst Employer Services Ltd",
     "pre_dormancy_avg_monthly_activity": 6000, "reactivation_amount": 7200, "dormancy_days": 35,
     "new_counterparty_count": 0, "outflow_amount": 1500,
     "first_reactivation_counterparty_name": "Hazelmoor Trading Co", "second_reactivation_counterparty_name": "Adriatic Union Bank"},
    {"customer_name": "Sofia Sorrelwisp", "account_ref": "DR002", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "prior_counterparty_name": "Pinegate Payroll Solutions",
     "pre_dormancy_avg_monthly_activity": 6500, "reactivation_amount": 9750, "dormancy_days": 45,
     "new_counterparty_count": 1, "outflow_amount": 2500,
     "first_reactivation_counterparty_name": "Brightwater Commerce Ltd", "second_reactivation_counterparty_name": "Pacific Rim Commercial Bank"},
    {"customer_name": "Noah Hazelbutton", "account_ref": "DR003", "segment": "Private Banking",
     "home_branch": "Adriatic Union Bank - Old Port Branch", "prior_counterparty_name": "Elmsworth Pension Trust",
     "pre_dormancy_avg_monthly_activity": 7000, "reactivation_amount": 12600, "dormancy_days": 55,
     "new_counterparty_count": 1, "outflow_amount": 3000,
     "first_reactivation_counterparty_name": "Fernbridge Exports", "second_reactivation_counterparty_name": "Helvetia Private Bank"},
    {"customer_name": "Elena Ashquill", "account_ref": "DR004", "segment": "Retail",
     "home_branch": "Pacific Rim Commercial Bank - Summit Branch", "prior_counterparty_name": "Brackenfield Utilities Co",
     "pre_dormancy_avg_monthly_activity": 7500, "reactivation_amount": 16500, "dormancy_days": 65,
     "new_counterparty_count": 2, "outflow_amount": 4000,
     "first_reactivation_counterparty_name": "Cinderquill Holdings", "second_reactivation_counterparty_name": "Meridian Trust Bank"},
    {"customer_name": "Malik Brindlequill", "account_ref": "DR005", "segment": "Small Business",
     "home_branch": "Helvetia Private Bank - Bayview Branch", "prior_counterparty_name": "Thistledown Insurance Group",
     "pre_dormancy_avg_monthly_activity": 8000, "reactivation_amount": 19200, "dormancy_days": 75,
     "new_counterparty_count": 2, "outflow_amount": 3600,
     "first_reactivation_counterparty_name": "Cobblestone Traders", "second_reactivation_counterparty_name": "Continental Correspondent Bank"},
    {"customer_name": "Ingrid Duskbristle", "account_ref": "DR006", "segment": "Private Banking",
     "home_branch": "Meridian Trust Bank - North Branch", "prior_counterparty_name": "Oakhurst Employer Services Ltd",
     "pre_dormancy_avg_monthly_activity": 8500, "reactivation_amount": 22950, "dormancy_days": 85,
     "new_counterparty_count": 2, "outflow_amount": 9000,
     "first_reactivation_counterparty_name": "Thistlefiddle Commerce Ltd", "second_reactivation_counterparty_name": "Adriatic Union Bank"},
    {"customer_name": "Ravi Hollowtumble", "account_ref": "DR007", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "prior_counterparty_name": "Pinegate Payroll Solutions",
     "pre_dormancy_avg_monthly_activity": 6000, "reactivation_amount": 19800, "dormancy_days": 95,
     "new_counterparty_count": 3, "outflow_amount": 10500,
     "first_reactivation_counterparty_name": "Willowbutton Exports", "second_reactivation_counterparty_name": "Pacific Rim Commercial Bank"},
    {"customer_name": "Chiara Thistlebristle", "account_ref": "DR008", "segment": "Small Business",
     "home_branch": "Adriatic Union Bank - Old Port Branch", "prior_counterparty_name": "Elmsworth Pension Trust",
     "pre_dormancy_avg_monthly_activity": 6500, "reactivation_amount": 27300, "dormancy_days": 110,
     "new_counterparty_count": 3, "outflow_amount": 15000,
     "first_reactivation_counterparty_name": "Thornfield Trading Co", "second_reactivation_counterparty_name": "Helvetia Private Bank"},
    {"customer_name": "Youssef Fernbutton", "account_ref": "DR009", "segment": "Private Banking",
     "home_branch": "Pacific Rim Commercial Bank - Summit Branch", "prior_counterparty_name": "Brackenfield Utilities Co",
     "pre_dormancy_avg_monthly_activity": 7000, "reactivation_amount": 36400, "dormancy_days": 125,
     "new_counterparty_count": 4, "outflow_amount": 22000,
     "first_reactivation_counterparty_name": "Meadowlark Holdings", "second_reactivation_counterparty_name": "Meridian Trust Bank"},
    {"customer_name": "Katarina Puddletumble", "account_ref": "DR010", "segment": "Retail",
     "home_branch": "Helvetia Private Bank - Bayview Branch", "prior_counterparty_name": "Thistledown Insurance Group",
     "pre_dormancy_avg_monthly_activity": 7500, "reactivation_amount": 45000, "dormancy_days": 140,
     "new_counterparty_count": 4, "outflow_amount": 29000,
     "first_reactivation_counterparty_name": "Duskwood Commerce Ltd", "second_reactivation_counterparty_name": "Continental Correspondent Bank"},
    {"customer_name": "Liam Flintwisp", "account_ref": "DR011", "segment": "Small Business",
     "home_branch": "Meridian Trust Bank - North Branch", "prior_counterparty_name": "Oakhurst Employer Services Ltd",
     "pre_dormancy_avg_monthly_activity": 8000, "reactivation_amount": 52000, "dormancy_days": 155,
     "new_counterparty_count": 4, "outflow_amount": 34000,
     "first_reactivation_counterparty_name": "Ironbark Traders", "second_reactivation_counterparty_name": "Adriatic Union Bank"},
    {"customer_name": "Fatima Brindlewisp", "account_ref": "DR012", "segment": "Private Banking",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "prior_counterparty_name": "Pinegate Payroll Solutions",
     "pre_dormancy_avg_monthly_activity": 8500, "reactivation_amount": 59500, "dormancy_days": 170,
     "new_counterparty_count": 4, "outflow_amount": 42000,
     "first_reactivation_counterparty_name": "Silverlake Exports", "second_reactivation_counterparty_name": "Pacific Rim Commercial Bank"},
    {"customer_name": "Anders Nettlewhistle", "account_ref": "DR013", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Port Branch", "prior_counterparty_name": "Elmsworth Pension Trust",
     "pre_dormancy_avg_monthly_activity": 6000, "reactivation_amount": 52000, "dormancy_days": 190,
     "new_counterparty_count": 5, "outflow_amount": 40000,
     "first_reactivation_counterparty_name": "Wrenfield Trading Co", "second_reactivation_counterparty_name": "Helvetia Private Bank"},
    {"customer_name": "Beatriz Wrenbutton", "account_ref": "DR014", "segment": "Small Business",
     "home_branch": "Pacific Rim Commercial Bank - Summit Branch", "prior_counterparty_name": "Brackenfield Utilities Co",
     "pre_dormancy_avg_monthly_activity": 6500, "reactivation_amount": 68000, "dormancy_days": 215,
     "new_counterparty_count": 5, "outflow_amount": 54000,
     "first_reactivation_counterparty_name": "Bramblewood Holdings", "second_reactivation_counterparty_name": "Meridian Trust Bank"},
    {"customer_name": "Dorian Rushquill", "account_ref": "DR015", "segment": "Private Banking",
     "home_branch": "Helvetia Private Bank - Bayview Branch", "prior_counterparty_name": "Thistledown Insurance Group",
     "pre_dormancy_avg_monthly_activity": 7000, "reactivation_amount": 84000, "dormancy_days": 240,
     "new_counterparty_count": 6, "outflow_amount": 68000,
     "first_reactivation_counterparty_name": "Hazelthimble Commerce Ltd", "second_reactivation_counterparty_name": "Continental Correspondent Bank"},
    {"customer_name": "Priya Rushthimble", "account_ref": "DR016", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - North Branch", "prior_counterparty_name": "Oakhurst Employer Services Ltd",
     "pre_dormancy_avg_monthly_activity": 7500, "reactivation_amount": 105000, "dormancy_days": 270,
     "new_counterparty_count": 6, "outflow_amount": 88000,
     "first_reactivation_counterparty_name": "Foxglove Traders", "second_reactivation_counterparty_name": "Adriatic Union Bank"},
    {"customer_name": "Magnus Willowquill", "account_ref": "DR017", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "prior_counterparty_name": "Pinegate Payroll Solutions",
     "pre_dormancy_avg_monthly_activity": 8000, "reactivation_amount": 128000, "dormancy_days": 300,
     "new_counterparty_count": 7, "outflow_amount": 110000,
     "first_reactivation_counterparty_name": "Willowmere Exports", "second_reactivation_counterparty_name": "Pacific Rim Commercial Bank"},
    {"customer_name": "Isabelle Puddlekettle", "account_ref": "DR018", "segment": "Private Banking",
     "home_branch": "Adriatic Union Bank - Old Port Branch", "prior_counterparty_name": "Elmsworth Pension Trust",
     "pre_dormancy_avg_monthly_activity": 8500, "reactivation_amount": 153000, "dormancy_days": 330,
     "new_counterparty_count": 7, "outflow_amount": 138000,
     "first_reactivation_counterparty_name": "Stagbrook Trading Co", "second_reactivation_counterparty_name": "Helvetia Private Bank"},
    {"customer_name": "Viktor Tallowbristle", "account_ref": "DR019", "segment": "Retail",
     "home_branch": "Pacific Rim Commercial Bank - Summit Branch", "prior_counterparty_name": "Brackenfield Utilities Co",
     "pre_dormancy_avg_monthly_activity": 8000, "reactivation_amount": 200000, "dormancy_days": 730,
     "new_counterparty_count": 10, "outflow_amount": 190000,
     "first_reactivation_counterparty_name": "Alpha Trading Ltd", "second_reactivation_counterparty_name": "Continental Correspondent Bank"},
    {"customer_name": "Sarah Thistlemote", "account_ref": "DR020", "segment": "Small Business",
     "home_branch": "Helvetia Private Bank - Bayview Branch", "prior_counterparty_name": "Thistledown Insurance Group",
     "pre_dormancy_avg_monthly_activity": 9000, "reactivation_amount": 135000, "dormancy_days": 400,
     "new_counterparty_count": 9, "outflow_amount": 128000,
     "first_reactivation_counterparty_name": "Blue Harbour Logistics Ltd", "second_reactivation_counterparty_name": "Continental Correspondent Bank"},
    {"customer_name": "Hassan Ashthimble", "account_ref": "DR021", "segment": "Private Banking",
     "home_branch": "Meridian Trust Bank - North Branch", "prior_counterparty_name": "Oakhurst Employer Services Ltd",
     "pre_dormancy_avg_monthly_activity": 8500, "reactivation_amount": 212500, "dormancy_days": 300,
     "new_counterparty_count": 9, "outflow_amount": 200000,
     "first_reactivation_counterparty_name": "Cedar & Vale Trading Ltd", "second_reactivation_counterparty_name": "Adriatic Union Bank"},
    {"customer_name": "Greta Gorsebutton", "account_ref": "DR022", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "prior_counterparty_name": "Pinegate Payroll Solutions",
     "pre_dormancy_avg_monthly_activity": 9000, "reactivation_amount": 225000, "dormancy_days": 500,
     "new_counterparty_count": 9, "outflow_amount": 180000,
     "first_reactivation_counterparty_name": "Northwind Freight Co", "second_reactivation_counterparty_name": "Pacific Rim Commercial Bank"},
]

# first_reactivation_counterparty_name, account_ref, bank, jurisdiction, relationship, prior_alerts
COUNTERPARTIES: List[Dict[str, Any]] = [
    {"first_reactivation_counterparty_name": "Hazelmoor Trading Co", "account_ref": "DR001", "bank": "Adriatic Union Bank",
     "jurisdiction": "Ireland", "relationship": "Unverified counterparty", "prior_alerts": 0},
    {"first_reactivation_counterparty_name": "Brightwater Commerce Ltd", "account_ref": "DR002", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Canada", "relationship": "Unverified counterparty", "prior_alerts": 0},
    {"first_reactivation_counterparty_name": "Fernbridge Exports", "account_ref": "DR003", "bank": "Helvetia Private Bank",
     "jurisdiction": "Germany", "relationship": "Unverified counterparty", "prior_alerts": 0},
    {"first_reactivation_counterparty_name": "Cinderquill Holdings", "account_ref": "DR004", "bank": "Meridian Trust Bank",
     "jurisdiction": "Hong Kong", "relationship": "Unverified counterparty", "prior_alerts": 0},
    {"first_reactivation_counterparty_name": "Cobblestone Traders", "account_ref": "DR005", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Switzerland", "relationship": "Unverified counterparty", "prior_alerts": 0},
    {"first_reactivation_counterparty_name": "Thistlefiddle Commerce Ltd", "account_ref": "DR006", "bank": "Adriatic Union Bank",
     "jurisdiction": "United Kingdom", "relationship": "Unverified counterparty", "prior_alerts": 0},
    {"first_reactivation_counterparty_name": "Willowbutton Exports", "account_ref": "DR007", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Cyprus", "relationship": "Unverified counterparty", "prior_alerts": 1},
    {"first_reactivation_counterparty_name": "Thornfield Trading Co", "account_ref": "DR008", "bank": "Helvetia Private Bank",
     "jurisdiction": "Panama", "relationship": "Unverified counterparty", "prior_alerts": 1},
    {"first_reactivation_counterparty_name": "Meadowlark Holdings", "account_ref": "DR009", "bank": "Meridian Trust Bank",
     "jurisdiction": "Singapore", "relationship": "Unverified counterparty", "prior_alerts": 1},
    {"first_reactivation_counterparty_name": "Duskwood Commerce Ltd", "account_ref": "DR010", "bank": "Continental Correspondent Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Money service business", "prior_alerts": 1},
    {"first_reactivation_counterparty_name": "Ironbark Traders", "account_ref": "DR011", "bank": "Adriatic Union Bank",
     "jurisdiction": "Turkey", "relationship": "Unverified counterparty", "prior_alerts": 1},
    {"first_reactivation_counterparty_name": "Silverlake Exports", "account_ref": "DR012", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "British Virgin Islands", "relationship": "Unverified counterparty", "prior_alerts": 1},
    {"first_reactivation_counterparty_name": "Wrenfield Trading Co", "account_ref": "DR013", "bank": "Helvetia Private Bank",
     "jurisdiction": "Ireland", "relationship": "Unverified counterparty", "prior_alerts": 2},
    {"first_reactivation_counterparty_name": "Bramblewood Holdings", "account_ref": "DR014", "bank": "Meridian Trust Bank",
     "jurisdiction": "Canada", "relationship": "Unverified counterparty", "prior_alerts": 2},
    {"first_reactivation_counterparty_name": "Hazelthimble Commerce Ltd", "account_ref": "DR015", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Germany", "relationship": "Unverified counterparty", "prior_alerts": 2},
    {"first_reactivation_counterparty_name": "Foxglove Traders", "account_ref": "DR016", "bank": "Adriatic Union Bank",
     "jurisdiction": "Hong Kong", "relationship": "Unverified counterparty", "prior_alerts": 2},
    {"first_reactivation_counterparty_name": "Willowmere Exports", "account_ref": "DR017", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Switzerland", "relationship": "Unverified counterparty", "prior_alerts": 2},
    {"first_reactivation_counterparty_name": "Stagbrook Trading Co", "account_ref": "DR018", "bank": "Helvetia Private Bank",
     "jurisdiction": "United Kingdom", "relationship": "Unverified counterparty", "prior_alerts": 2},
    {"first_reactivation_counterparty_name": "Alpha Trading Ltd", "account_ref": "DR019", "bank": "Adriatic Union Bank",
     "jurisdiction": "Cyprus", "relationship": "Reactivation counterparty (network entity)", "prior_alerts": 3},
    {"first_reactivation_counterparty_name": "Blue Harbour Logistics Ltd", "account_ref": "DR020", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Panama", "relationship": "Unverified counterparty", "prior_alerts": 3},
    {"first_reactivation_counterparty_name": "Cedar & Vale Trading Ltd", "account_ref": "DR021", "bank": "Helvetia Private Bank",
     "jurisdiction": "Singapore", "relationship": "Money service business", "prior_alerts": 3},
    {"first_reactivation_counterparty_name": "Northwind Freight Co", "account_ref": "DR022", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Unverified counterparty", "prior_alerts": 3},
]

_TABLES = {"accounts.csv": ACCOUNTS, "counterparties.csv": COUNTERPARTIES}


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
