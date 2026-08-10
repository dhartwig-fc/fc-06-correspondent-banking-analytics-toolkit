"""Generate synthetic sample data for BA003 Mule Accounts.

22 personal mule accounts (>= the 2026-08-09 20-row standard; BA003 is NOT
grandfathered), spread across all four exposure bands so the scorer visibly
discriminates rather than rubber-stamping every row:

  MUL001-MUL006   Low       (15-24)
  MUL007-MUL012   Medium    (45-50)
  MUL013-MUL018   High      (70-76)
  MUL019-MUL022   Critical  (84-90)  -- at least two, per the house standard

Fusion bridge: MUL019 (Rosalind Fairweather, 90/Critical, the single
highest-scoring account in the set) forwards its pass-through funds to **Alpha
Trading Ltd** -- an entity already in the estate network (NI001's REG-2001,
NI004/PAT007's C001) -- so canonical entity resolution joins BA003 onto the
existing fused case. Being the top-scored account matters: the FC-10 adapter
builds its case/graph from the single highest exposure_score row, so the Alpha
bridge has to be that row, not merely a Critical row. MUL006 (Low, 24) also
names Alpha Trading Ltd as its forwarding destination, deliberately: naming the
same downstream entity is not itself the risk signal, the mule PATTERN is.

Run:  python3 generate_ba003_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# customer_name, account_ref, segment, home_branch, total_inflow_amount, total_outflow_amount,
# account_age_days, declared_monthly_income, monthly_throughput_amount, shared_link_count,
# top_originator_name, controller_name, beneficiary_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"customer_name": "Owen Bennett", "account_ref": "MUL001", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "total_inflow_amount": 42000,
     "total_outflow_amount": 15000, "account_age_days": 820, "declared_monthly_income": 4200,
     "monthly_throughput_amount": 6500, "shared_link_count": 0,
     "top_originator_name": "Priya Chandran", "controller_name": "N/A", "beneficiary_name": "Blue Harbour Logistics Ltd"},
    {"customer_name": "Freya Sinclair", "account_ref": "MUL002", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "total_inflow_amount": 38000,
     "total_outflow_amount": 14000, "account_age_days": 900, "declared_monthly_income": 3800,
     "monthly_throughput_amount": 7200, "shared_link_count": 0,
     "top_originator_name": "Consuela Reyes", "controller_name": "N/A", "beneficiary_name": "Cedar & Vale Trading Ltd"},
    {"customer_name": "Marco Esposito", "account_ref": "MUL003", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "total_inflow_amount": 45000,
     "total_outflow_amount": 20000, "account_age_days": 500, "declared_monthly_income": 4500,
     "monthly_throughput_amount": 8800, "shared_link_count": 0,
     "top_originator_name": "Tobias Lindgren", "controller_name": "N/A", "beneficiary_name": "Northwind Freight Co"},
    {"customer_name": "Ingrid Solheim", "account_ref": "MUL004", "segment": "Private Banking",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "total_inflow_amount": 40000,
     "total_outflow_amount": 16500, "account_age_days": 760, "declared_monthly_income": 4000,
     "monthly_throughput_amount": 9500, "shared_link_count": 1,
     "top_originator_name": "Farida Khalil", "controller_name": "N/A", "beneficiary_name": "Solano Exchange House"},
    {"customer_name": "Tariq Aziz", "account_ref": "MUL005", "segment": "Retail",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "total_inflow_amount": 43000,
     "total_outflow_amount": 17000, "account_age_days": 630, "declared_monthly_income": 4300,
     "monthly_throughput_amount": 10200, "shared_link_count": 0,
     "top_originator_name": "Omar El-Sayed", "controller_name": "N/A", "beneficiary_name": "Kestrel Cash & Carry Ltd"},
    {"customer_name": "Camille Laurent", "account_ref": "MUL006", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "total_inflow_amount": 41000,
     "total_outflow_amount": 21000, "account_age_days": 390, "declared_monthly_income": 4100,
     "monthly_throughput_amount": 11500, "shared_link_count": 0,
     "top_originator_name": "Beatrice Dubois", "controller_name": "N/A", "beneficiary_name": "Alpha Trading Ltd"},
    {"customer_name": "Bjorn Eriksson", "account_ref": "MUL007", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Riverside Branch", "total_inflow_amount": 46000,
     "total_outflow_amount": 28000, "account_age_days": 260, "declared_monthly_income": 3800,
     "monthly_throughput_amount": 21000, "shared_link_count": 1,
     "top_originator_name": "Anton Kowalczyk", "controller_name": "Erik Lindholm", "beneficiary_name": "Amberfield Trading Co"},
    {"customer_name": "Nadia Volkova", "account_ref": "MUL008", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "total_inflow_amount": 44000,
     "total_outflow_amount": 30000, "account_age_days": 300, "declared_monthly_income": 3600,
     "monthly_throughput_amount": 19500, "shared_link_count": 1,
     "top_originator_name": "Youssef Benali", "controller_name": "Pavel Sokolov", "beneficiary_name": "Bluecrest Export Group"},
    {"customer_name": "Ethan Walsh", "account_ref": "MUL009", "segment": "Small Business",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "total_inflow_amount": 47000,
     "total_outflow_amount": 33000, "account_age_days": 210, "declared_monthly_income": 4000,
     "monthly_throughput_amount": 27000, "shared_link_count": 1,
     "top_originator_name": "Nikolai Volkov", "controller_name": "Declan Murphy", "beneficiary_name": "Ironvale Commerce Ltd"},
    {"customer_name": "Sofia Marchetti", "account_ref": "MUL010", "segment": "Retail",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "total_inflow_amount": 48000,
     "total_outflow_amount": 31000, "account_age_days": 280, "declared_monthly_income": 3900,
     "monthly_throughput_amount": 22500, "shared_link_count": 1,
     "top_originator_name": "Grace Muthoni", "controller_name": "Luca Ferrara", "beneficiary_name": "Whitmore Global Traders"},
    {"customer_name": "Rustam Karimov", "account_ref": "MUL011", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "total_inflow_amount": 45500,
     "total_outflow_amount": 34000, "account_age_days": 190, "declared_monthly_income": 3700,
     "monthly_throughput_amount": 26500, "shared_link_count": 2,
     "top_originator_name": "Diego Salazar", "controller_name": "Aziz Rahimov", "beneficiary_name": "Coral Bay Exports Ltd"},
    {"customer_name": "Delphine Moreau", "account_ref": "MUL012", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "total_inflow_amount": 46500,
     "total_outflow_amount": 30500, "account_age_days": 320, "declared_monthly_income": 3850,
     "monthly_throughput_amount": 23000, "shared_link_count": 1,
     "top_originator_name": "Elin Karlsson", "controller_name": "Henri Fabron", "beneficiary_name": "Granite Peak Holdings"},
    {"customer_name": "Connor McAllister", "account_ref": "MUL013", "segment": "Retail",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "total_inflow_amount": 52000,
     "total_outflow_amount": 43000, "account_age_days": 95, "declared_monthly_income": 3000,
     "monthly_throughput_amount": 45000, "shared_link_count": 3,
     "top_originator_name": "Sana Malik", "controller_name": "Ray Doherty", "beneficiary_name": "Fenwick & Cole Trading"},
    {"customer_name": "Leila Amari", "account_ref": "MUL014", "segment": "Retail",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "total_inflow_amount": 54000,
     "total_outflow_amount": 45000, "account_age_days": 80, "declared_monthly_income": 2800,
     "monthly_throughput_amount": 42000, "shared_link_count": 2,
     "top_originator_name": "Petra Novak", "controller_name": "Nabil Toure", "beneficiary_name": "Redstone Commodities Ltd"},
    {"customer_name": "Viktor Hlavac", "account_ref": "MUL015", "segment": "Small Business",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "total_inflow_amount": 56000,
     "total_outflow_amount": 49000, "account_age_days": 70, "declared_monthly_income": 3100,
     "monthly_throughput_amount": 48000, "shared_link_count": 3,
     "top_originator_name": "Kwame Asante", "controller_name": "Milan Dvorak", "beneficiary_name": "Solstice Trading Group"},
    {"customer_name": "Amina Diallo", "account_ref": "MUL016", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "total_inflow_amount": 53000,
     "total_outflow_amount": 49500, "account_age_days": 110, "declared_monthly_income": 2900,
     "monthly_throughput_amount": 40000, "shared_link_count": 2,
     "top_originator_name": "Ling Wei", "controller_name": "Ousmane Ba", "beneficiary_name": "Palmetto Export Co"},
    {"customer_name": "Patrick Doyle", "account_ref": "MUL017", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Riverside Branch", "total_inflow_amount": 58000,
     "total_outflow_amount": 50500, "account_age_days": 65, "declared_monthly_income": 3200,
     "monthly_throughput_amount": 65000, "shared_link_count": 3,
     "top_originator_name": "Ravi Menon", "controller_name": "Sean Brennan", "beneficiary_name": "Windrose Commerce Ltd"},
    {"customer_name": "Elif Kaya", "account_ref": "MUL018", "segment": "Retail",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "total_inflow_amount": 55000,
     "total_outflow_amount": 46500, "account_age_days": 90, "declared_monthly_income": 3000,
     "monthly_throughput_amount": 44000, "shared_link_count": 2,
     "top_originator_name": "Chloe Fontaine", "controller_name": "Baris Aydin", "beneficiary_name": "Kestrel Bay Holdings"},
    {"customer_name": "Rosalind Fairweather", "account_ref": "MUL019", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "total_inflow_amount": 100000,
     "total_outflow_amount": 96000, "account_age_days": 12, "declared_monthly_income": 3200,
     "monthly_throughput_amount": 92000, "shared_link_count": 6,
     "top_originator_name": "Aroha Ngata", "controller_name": "Marcus Vane", "beneficiary_name": "Alpha Trading Ltd"},
    {"customer_name": "Damian Wozniak", "account_ref": "MUL020", "segment": "Retail",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "total_inflow_amount": 92000,
     "total_outflow_amount": 86000, "account_age_days": 25, "declared_monthly_income": 3500,
     "monthly_throughput_amount": 84000, "shared_link_count": 3,
     "top_originator_name": "Bashir Rahman", "controller_name": "Tomasz Krol", "beneficiary_name": "Everline Traders Ltd"},
    {"customer_name": "Naledi Mokoena", "account_ref": "MUL021", "segment": "Retail",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "total_inflow_amount": 88000,
     "total_outflow_amount": 82000, "account_age_days": 30, "declared_monthly_income": 3400,
     "monthly_throughput_amount": 45000, "shared_link_count": 5,
     "top_originator_name": "Chloe Fontaine", "controller_name": "Sipho Ndlovu", "beneficiary_name": "Northgate Commodities Ltd"},
    {"customer_name": "Kenji Watanabe", "account_ref": "MUL022", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "total_inflow_amount": 95000,
     "total_outflow_amount": 82500, "account_age_days": 18, "declared_monthly_income": 3300,
     "monthly_throughput_amount": 88000, "shared_link_count": 5,
     "top_originator_name": "Dmitri Volkov", "controller_name": "Haruto Sato", "beneficiary_name": "Stonebridge Export Group"},
]

# beneficiary_name, account_ref, bank, jurisdiction, relationship, prior_alerts
BENEFICIARIES: List[Dict[str, Any]] = [
    {"beneficiary_name": "Blue Harbour Logistics Ltd", "account_ref": "MUL001", "bank": "Meridian Trust Bank",
     "jurisdiction": "Ireland", "relationship": "Unverified payee", "prior_alerts": 0},
    {"beneficiary_name": "Cedar & Vale Trading Ltd", "account_ref": "MUL002", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Canada", "relationship": "Unverified payee", "prior_alerts": 0},
    {"beneficiary_name": "Northwind Freight Co", "account_ref": "MUL003", "bank": "Adriatic Union Bank",
     "jurisdiction": "Germany", "relationship": "Unverified payee", "prior_alerts": 0},
    {"beneficiary_name": "Solano Exchange House", "account_ref": "MUL004", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Hong Kong", "relationship": "Money service business", "prior_alerts": 1},
    {"beneficiary_name": "Kestrel Cash & Carry Ltd", "account_ref": "MUL005", "bank": "Helvetia Private Bank",
     "jurisdiction": "Switzerland", "relationship": "Unverified payee", "prior_alerts": 0},
    {"beneficiary_name": "Alpha Trading Ltd", "account_ref": "MUL006", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Kingdom", "relationship": "Unverified payee", "prior_alerts": 0},
    {"beneficiary_name": "Amberfield Trading Co", "account_ref": "MUL007", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Cyprus", "relationship": "Unverified payee", "prior_alerts": 1},
    {"beneficiary_name": "Bluecrest Export Group", "account_ref": "MUL008", "bank": "Adriatic Union Bank",
     "jurisdiction": "Panama", "relationship": "Unverified payee", "prior_alerts": 1},
    {"beneficiary_name": "Ironvale Commerce Ltd", "account_ref": "MUL009", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Singapore", "relationship": "Unverified payee", "prior_alerts": 1},
    {"beneficiary_name": "Whitmore Global Traders", "account_ref": "MUL010", "bank": "Helvetia Private Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Unverified payee", "prior_alerts": 1},
    {"beneficiary_name": "Coral Bay Exports Ltd", "account_ref": "MUL011", "bank": "Meridian Trust Bank",
     "jurisdiction": "Turkey", "relationship": "Unverified payee", "prior_alerts": 2},
    {"beneficiary_name": "Granite Peak Holdings", "account_ref": "MUL012", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Hong Kong", "relationship": "Unverified payee", "prior_alerts": 1},
    {"beneficiary_name": "Fenwick & Cole Trading", "account_ref": "MUL013", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Cyprus", "relationship": "Unverified payee", "prior_alerts": 2},
    {"beneficiary_name": "Redstone Commodities Ltd", "account_ref": "MUL014", "bank": "Helvetia Private Bank",
     "jurisdiction": "Panama", "relationship": "Unverified payee", "prior_alerts": 2},
    {"beneficiary_name": "Solstice Trading Group", "account_ref": "MUL015", "bank": "Adriatic Union Bank",
     "jurisdiction": "British Virgin Islands", "relationship": "Unverified payee", "prior_alerts": 2},
    {"beneficiary_name": "Palmetto Export Co", "account_ref": "MUL016", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Unverified payee", "prior_alerts": 2},
    {"beneficiary_name": "Windrose Commerce Ltd", "account_ref": "MUL017", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Hong Kong", "relationship": "Unverified payee", "prior_alerts": 3},
    {"beneficiary_name": "Kestrel Bay Holdings", "account_ref": "MUL018", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Panama", "relationship": "Unverified payee", "prior_alerts": 2},
    {"beneficiary_name": "Alpha Trading Ltd", "account_ref": "MUL019", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Kingdom", "relationship": "Unverified payee", "prior_alerts": 3},
    {"beneficiary_name": "Everline Traders Ltd", "account_ref": "MUL020", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Panama", "relationship": "Unverified payee", "prior_alerts": 3},
    {"beneficiary_name": "Northgate Commodities Ltd", "account_ref": "MUL021", "bank": "Helvetia Private Bank",
     "jurisdiction": "Turkey", "relationship": "Unverified payee", "prior_alerts": 3},
    {"beneficiary_name": "Stonebridge Export Group", "account_ref": "MUL022", "bank": "Meridian Trust Bank",
     "jurisdiction": "Panama", "relationship": "Unverified payee", "prior_alerts": 3},
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
