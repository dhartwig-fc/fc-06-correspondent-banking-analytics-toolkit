"""Generate synthetic sample data for BA004 Circular Funds Flow.

22 originating accounts (>= the 2026-08-09 20-row standard; BA004 is NOT
grandfathered), spread across all four exposure bands so the scorer visibly
discriminates rather than rubber-stamping every row:

  CYC001-CYC006   Low       (15-26)
  CYC007-CYC012   Medium    (35-51)
  CYC013-CYC018   High      (61-70)
  CYC019-CYC022   Critical  (83-90)  -- at least two, per the house standard

Fusion bridge: CYC019 (Piotr Kettlecrumb, 90/Critical, the single highest-scoring
account in the set) closes its loop through **Gammavane Imports Ltd** as its first
loop member -- an entity already in the estate network (BA001's ACC019 /
SAN002's tier-2 nominee, id C003) -- so canonical entity resolution joins
BA004 onto the existing fused case. Being the top-scored account matters: the
FC-10 adapter builds its case/graph from the single highest exposure_score
row, so the Gamma bridge has to be that row, not merely a Critical row.
CYC019 also routes its second hop through **Continental Correspondent Bank**,
a bank shared across the BA004/BA005/BA008 correspondent-banking chain (per
the fc-06 design). CYC006 (Low, 21) also names Gammavane Imports Ltd as its
second loop member, deliberately: naming the same downstream entity is not
itself the risk signal, the closed-loop PATTERN is. Continental Correspondent
Bank recurs as a second loop member across several other rows too (CYC005,
CYC010, CYC015, CYC020), consistent with it being a shared correspondent
bank the wider BA0NN family will keep referencing.

Run:  python3 generate_ba004_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# customer_name, account_ref, segment, home_branch, originated_amount, returned_amount,
# hop_count, avg_hop_retention_pct, loop_duration_hours, first_loop_member_name,
# second_loop_member_name, closure_member_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"customer_name": "Henrik Vellumthimble", "account_ref": "CYC001", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - North Branch", "originated_amount": 35000,
     "returned_amount": 11900, "hop_count": 1, "avg_hop_retention_pct": 0.70,
     "loop_duration_hours": 960, "first_loop_member_name": "Harrow Peak Ventures",
     "second_loop_member_name": "Adriatic Union Bank", "closure_member_name": "Rosemont Harbour Ltd"},
    {"customer_name": "Sofia Thistlewhistle", "account_ref": "CYC002", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "originated_amount": 38000,
     "returned_amount": 15200, "hop_count": 2, "avg_hop_retention_pct": 0.72,
     "loop_duration_hours": 1100, "first_loop_member_name": "Silvermoor Trading Ltd",
     "second_loop_member_name": "Pacific Rim Commercial Bank", "closure_member_name": "Talbridge Commerce Co"},
    {"customer_name": "Malik Kettlewhistle", "account_ref": "CYC003", "segment": "Private Banking",
     "home_branch": "Adriatic Union Bank - Old Port Branch", "originated_amount": 40000,
     "returned_amount": 24000, "hop_count": 1, "avg_hop_retention_pct": 0.68,
     "loop_duration_hours": 1300, "first_loop_member_name": "Vantage Cove Holdings",
     "second_loop_member_name": "Helvetia Private Bank", "closure_member_name": "Wrenfield Exports Ltd"},
    {"customer_name": "Priya Flintcrumb", "account_ref": "CYC004", "segment": "Retail",
     "home_branch": "Pacific Rim Commercial Bank - Summit Branch", "originated_amount": 42000,
     "returned_amount": 16000, "hop_count": 3, "avg_hop_retention_pct": 0.75,
     "loop_duration_hours": 900, "first_loop_member_name": "Ashford Meridian Group",
     "second_loop_member_name": "Meridian Trust Bank", "closure_member_name": "Cobalt Reach Holdings"},
    {"customer_name": "Lucas Umberthimble", "account_ref": "CYC005", "segment": "Small Business",
     "home_branch": "Helvetia Private Bank - Bayview Branch", "originated_amount": 37000,
     "returned_amount": 13000, "hop_count": 1, "avg_hop_retention_pct": 0.85,
     "loop_duration_hours": 1050, "first_loop_member_name": "Larkspur Commerce Ltd",
     "second_loop_member_name": "Continental Correspondent Bank", "closure_member_name": "Sable Crest Trading"},
    {"customer_name": "Elena Mosstumblea", "account_ref": "CYC006", "segment": "Private Banking",
     "home_branch": "Meridian Trust Bank - North Branch", "originated_amount": 44000,
     "returned_amount": 17000, "hop_count": 2, "avg_hop_retention_pct": 0.74,
     "loop_duration_hours": 400, "first_loop_member_name": "Windmere Export Co",
     "second_loop_member_name": "Gammavane Imports Ltd", "closure_member_name": "Quillfiddle Cargo Ltd"},
    {"customer_name": "Oskar Nettlewhistle", "account_ref": "CYC007", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "originated_amount": 46000,
     "returned_amount": 27600, "hop_count": 3, "avg_hop_retention_pct": 0.85,
     "loop_duration_hours": 400, "first_loop_member_name": "Corvus Bay Trading",
     "second_loop_member_name": "Pacific Rim Commercial Bank", "closure_member_name": "Nightshade Export Group"},
    {"customer_name": "Amara Tallowmote", "account_ref": "CYC008", "segment": "Small Business",
     "home_branch": "Adriatic Union Bank - Old Port Branch", "originated_amount": 48000,
     "returned_amount": 29800, "hop_count": 4, "avg_hop_retention_pct": 0.86,
     "loop_duration_hours": 350, "first_loop_member_name": "Thistledown Holdings",
     "second_loop_member_name": "Helvetia Private Bank", "closure_member_name": "Fenmoor Trading Ltd"},
    {"customer_name": "Ravi Wrenquill", "account_ref": "CYC009", "segment": "Private Banking",
     "home_branch": "Pacific Rim Commercial Bank - Summit Branch", "originated_amount": 45000,
     "returned_amount": 18000, "hop_count": 3, "avg_hop_retention_pct": 0.84,
     "loop_duration_hours": 300, "first_loop_member_name": "Ferrowick Commerce Ltd",
     "second_loop_member_name": "Meridian Trust Bank", "closure_member_name": "Thistlefiddle Commerce Ltd"},
    {"customer_name": "Ingeborg Mossspindle", "account_ref": "CYC010", "segment": "Retail",
     "home_branch": "Helvetia Private Bank - Bayview Branch", "originated_amount": 50000,
     "returned_amount": 32500, "hop_count": 5, "avg_hop_retention_pct": 0.85,
     "loop_duration_hours": 350, "first_loop_member_name": "Halcyon Ridge Traders",
     "second_loop_member_name": "Continental Correspondent Bank", "closure_member_name": "Brackenfield Holdings"},
    {"customer_name": "Salim Pebblebutton", "account_ref": "CYC011", "segment": "Small Business",
     "home_branch": "Meridian Trust Bank - North Branch", "originated_amount": 52000,
     "returned_amount": 32800, "hop_count": 4, "avg_hop_retention_pct": 0.93,
     "loop_duration_hours": 380, "first_loop_member_name": "Bramblespindle & Parsleywhistle Ltd",
     "second_loop_member_name": "Adriatic Union Bank", "closure_member_name": "Cloverdale Traders"},
    {"customer_name": "Noor Willowcrumb", "account_ref": "CYC012", "segment": "Private Banking",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "originated_amount": 49000,
     "returned_amount": 29900, "hop_count": 3, "avg_hop_retention_pct": 0.85,
     "loop_duration_hours": 60, "first_loop_member_name": "Ebonfield Exports",
     "second_loop_member_name": "Pacific Rim Commercial Bank", "closure_member_name": "Wistow Export Co"},
    {"customer_name": "Milo Hollowfiddle", "account_ref": "CYC013", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Port Branch", "originated_amount": 55000,
     "returned_amount": 46800, "hop_count": 5, "avg_hop_retention_pct": 0.93,
     "loop_duration_hours": 60, "first_loop_member_name": "Quilcastle Trading Group",
     "second_loop_member_name": "Helvetia Private Bank", "closure_member_name": "Ironhollow Trading Ltd"},
    {"customer_name": "Anika Umberquill", "account_ref": "CYC014", "segment": "Small Business",
     "home_branch": "Pacific Rim Commercial Bank - Summit Branch", "originated_amount": 58000,
     "returned_amount": 51000, "hop_count": 6, "avg_hop_retention_pct": 0.94,
     "loop_duration_hours": 45, "first_loop_member_name": "Wrenmoor Commerce Co",
     "second_loop_member_name": "Meridian Trust Bank", "closure_member_name": "Larchmont Cargo Group"},
    {"customer_name": "Yusuf Ivycrumb", "account_ref": "CYC015", "segment": "Private Banking",
     "home_branch": "Helvetia Private Bank - Bayview Branch", "originated_amount": 56000,
     "returned_amount": 33600, "hop_count": 5, "avg_hop_retention_pct": 0.92,
     "loop_duration_hours": 50, "first_loop_member_name": "Falkridge Traders",
     "second_loop_member_name": "Continental Correspondent Bank", "closure_member_name": "Duskwater Holdings"},
    {"customer_name": "Bianca Marrowfiddle", "account_ref": "CYC016", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - North Branch", "originated_amount": 57000,
     "returned_amount": 46700, "hop_count": 4, "avg_hop_retention_pct": 0.93,
     "loop_duration_hours": 55, "first_loop_member_name": "Cindervale Export Ltd",
     "second_loop_member_name": "Adriatic Union Bank", "closure_member_name": "Farrowgate Traders"},
    {"customer_name": "Callum Wrenkettle", "account_ref": "CYC017", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "originated_amount": 59000,
     "returned_amount": 49600, "hop_count": 5, "avg_hop_retention_pct": 0.86,
     "loop_duration_hours": 48, "first_loop_member_name": "Moorhaven Trading Group",
     "second_loop_member_name": "Pacific Rim Commercial Bank", "closure_member_name": "Kingsbrook Export Ltd"},
    {"customer_name": "Zainab Nettlemote", "account_ref": "CYC018", "segment": "Private Banking",
     "home_branch": "Adriatic Union Bank - Old Port Branch", "originated_amount": 60000,
     "returned_amount": 51600, "hop_count": 6, "avg_hop_retention_pct": 0.94,
     "loop_duration_hours": 300, "first_loop_member_name": "Elderglen Holdings",
     "second_loop_member_name": "Helvetia Private Bank", "closure_member_name": "Hollowmere Trading Co"},
    {"customer_name": "Piotr Kettlecrumb", "account_ref": "CYC019", "segment": "Retail",
     "home_branch": "Pacific Rim Commercial Bank - Summit Branch", "originated_amount": 100000,
     "returned_amount": 97000, "hop_count": 8, "avg_hop_retention_pct": 0.985,
     "loop_duration_hours": 8, "first_loop_member_name": "Gammavane Imports Ltd",
     "second_loop_member_name": "Continental Correspondent Bank", "closure_member_name": "Thornwick Holdings"},
    {"customer_name": "Helena Lanternquill", "account_ref": "CYC020", "segment": "Small Business",
     "home_branch": "Helvetia Private Bank - Bayview Branch", "originated_amount": 95000,
     "returned_amount": 90300, "hop_count": 9, "avg_hop_retention_pct": 0.98,
     "loop_duration_hours": 60, "first_loop_member_name": "Ravensmere Cargo Ltd",
     "second_loop_member_name": "Continental Correspondent Bank", "closure_member_name": "Stonefield Export Ltd"},
    {"customer_name": "Ahmed Mossbristle", "account_ref": "CYC021", "segment": "Private Banking",
     "home_branch": "Meridian Trust Bank - North Branch", "originated_amount": 92000,
     "returned_amount": 88300, "hop_count": 6, "avg_hop_retention_pct": 0.975,
     "loop_duration_hours": 15, "first_loop_member_name": "Thistlewood Export Co",
     "second_loop_member_name": "Adriatic Union Bank", "closure_member_name": "Marlowbridge Traders"},
    {"customer_name": "Greta Duskwhistle", "account_ref": "CYC022", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Exchange Branch", "originated_amount": 90000,
     "returned_amount": 79200, "hop_count": 10, "avg_hop_retention_pct": 0.99,
     "loop_duration_hours": 10, "first_loop_member_name": "Brindlewood Trading Ltd",
     "second_loop_member_name": "Pacific Rim Commercial Bank", "closure_member_name": "Ravenscar Commerce Group"},
]

# closure_member_name, account_ref, bank, jurisdiction, relationship, prior_alerts
LOOP_MEMBERS: List[Dict[str, Any]] = [
    {"closure_member_name": "Rosemont Harbour Ltd", "account_ref": "CYC001", "bank": "Helvetia Private Bank",
     "jurisdiction": "Ireland", "relationship": "Unverified intermediary", "prior_alerts": 0},
    {"closure_member_name": "Talbridge Commerce Co", "account_ref": "CYC002", "bank": "Meridian Trust Bank",
     "jurisdiction": "Canada", "relationship": "Unverified intermediary", "prior_alerts": 0},
    {"closure_member_name": "Wrenfield Exports Ltd", "account_ref": "CYC003", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Germany", "relationship": "Unverified intermediary", "prior_alerts": 0},
    {"closure_member_name": "Cobalt Reach Holdings", "account_ref": "CYC004", "bank": "Adriatic Union Bank",
     "jurisdiction": "Hong Kong", "relationship": "Unverified intermediary", "prior_alerts": 0},
    {"closure_member_name": "Sable Crest Trading", "account_ref": "CYC005", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Switzerland", "relationship": "Unverified intermediary", "prior_alerts": 0},
    {"closure_member_name": "Quillfiddle Cargo Ltd", "account_ref": "CYC006", "bank": "Helvetia Private Bank",
     "jurisdiction": "United Kingdom", "relationship": "Unverified intermediary", "prior_alerts": 0},
    {"closure_member_name": "Nightshade Export Group", "account_ref": "CYC007", "bank": "Meridian Trust Bank",
     "jurisdiction": "Cyprus", "relationship": "Unverified intermediary", "prior_alerts": 1},
    {"closure_member_name": "Fenmoor Trading Ltd", "account_ref": "CYC008", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Panama", "relationship": "Unverified intermediary", "prior_alerts": 1},
    {"closure_member_name": "Thistlefiddle Commerce Ltd", "account_ref": "CYC009", "bank": "Adriatic Union Bank",
     "jurisdiction": "Singapore", "relationship": "Unverified intermediary", "prior_alerts": 1},
    {"closure_member_name": "Brackenfield Holdings", "account_ref": "CYC010", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Money service business", "prior_alerts": 1},
    {"closure_member_name": "Cloverdale Traders", "account_ref": "CYC011", "bank": "Helvetia Private Bank",
     "jurisdiction": "Turkey", "relationship": "Unverified intermediary", "prior_alerts": 1},
    {"closure_member_name": "Wistow Export Co", "account_ref": "CYC012", "bank": "Meridian Trust Bank",
     "jurisdiction": "British Virgin Islands", "relationship": "Unverified intermediary", "prior_alerts": 1},
    {"closure_member_name": "Ironhollow Trading Ltd", "account_ref": "CYC013", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Ireland", "relationship": "Unverified intermediary", "prior_alerts": 2},
    {"closure_member_name": "Larchmont Cargo Group", "account_ref": "CYC014", "bank": "Adriatic Union Bank",
     "jurisdiction": "Canada", "relationship": "Unverified intermediary", "prior_alerts": 2},
    {"closure_member_name": "Duskwater Holdings", "account_ref": "CYC015", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Germany", "relationship": "Unverified intermediary", "prior_alerts": 2},
    {"closure_member_name": "Farrowgate Traders", "account_ref": "CYC016", "bank": "Helvetia Private Bank",
     "jurisdiction": "Hong Kong", "relationship": "Unverified intermediary", "prior_alerts": 2},
    {"closure_member_name": "Kingsbrook Export Ltd", "account_ref": "CYC017", "bank": "Meridian Trust Bank",
     "jurisdiction": "Switzerland", "relationship": "Unverified intermediary", "prior_alerts": 2},
    {"closure_member_name": "Hollowmere Trading Co", "account_ref": "CYC018", "bank": "Continental Correspondent Bank",
     "jurisdiction": "United Kingdom", "relationship": "Unverified intermediary", "prior_alerts": 2},
    {"closure_member_name": "Thornwick Holdings", "account_ref": "CYC019", "bank": "Adriatic Union Bank",
     "jurisdiction": "Cyprus", "relationship": "Unverified intermediary", "prior_alerts": 3},
    {"closure_member_name": "Stonefield Export Ltd", "account_ref": "CYC020", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Panama", "relationship": "Unverified intermediary", "prior_alerts": 3},
    {"closure_member_name": "Marlowbridge Traders", "account_ref": "CYC021", "bank": "Helvetia Private Bank",
     "jurisdiction": "Singapore", "relationship": "Unverified intermediary", "prior_alerts": 3},
    {"closure_member_name": "Ravenscar Commerce Group", "account_ref": "CYC022", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Unverified intermediary", "prior_alerts": 3},
]

_TABLES = {"accounts.csv": ACCOUNTS, "loop_members.csv": LOOP_MEMBERS}


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
