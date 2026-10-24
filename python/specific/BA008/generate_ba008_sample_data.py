"""Generate synthetic sample data for BA008 Layering.

22 seed accounts (>= the 2026-08-09 20-row standard; BA008 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  LAY001-LAY006   Low       (15-24)
  LAY007-LAY012   Medium    (42-53)
  LAY013-LAY018   High      (63-79)
  LAY019-LAY022   Critical  (84-90)  -- at least two, per the house standard

Fusion bridge: LAY019 (Katarina Parsleythimble, 90/Critical, the single highest-scoring account
in the set) routes its layering chain's first hop through **Gammavane Imports Ltd** -- an
entity already in the estate network (BA001/BA004's bridge, SAN002's tier-2 nominee,
id C003) -- so canonical entity resolution joins BA008 onto the existing fused case.
Being the top-scored account matters: the FC-10 adapter builds its case/graph from the
single highest exposure_score row, so the Gamma bridge has to be that row, not merely a
Critical row. LAY019 also routes its second hop through **Continental Correspondent
Bank**, the correspondent bank already shared across BA004/BA005/BA006's chains -- the
recurring correspondent-banking infrastructure the fc-06 design anticipated BA008 would
reference (see BA004's generator note). LAY006 (Low, 15) also names Gammavane Imports Ltd as
its second intermediary, deliberately: naming the same downstream entity is not itself
the risk signal, the deep-opaque-cross-border-fragmented layering PATTERN is.

Run:  python3 generate_ba008_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# customer_name, account_ref, segment, home_branch, chain_depth, opaque_intermediary_count,
# total_intermediary_count, secrecy_jurisdiction_hops, fragment_count,
# first_intermediary_name, second_intermediary_name, destination_name
ACCOUNTS: List[Dict[str, Any]] = [
    {"customer_name": "Emil Pebblefiddle", "account_ref": "LAY001", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "chain_depth": 1,
     "opaque_intermediary_count": 1, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 0,
     "fragment_count": 1, "first_intermediary_name": "Birchwood Nominee Services",
     "second_intermediary_name": "Corvellis Trade Partners", "destination_name": "Wrenfield Mercantile Ltd"},
    {"customer_name": "Camila Lanternquill", "account_ref": "LAY002", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "chain_depth": 3,
     "opaque_intermediary_count": 1, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 0,
     "fragment_count": 1, "first_intermediary_name": "Larkhaven Consultants",
     "second_intermediary_name": "Bramblespindle Bay Holdings", "destination_name": "Thistlewood Traders"},
    {"customer_name": "Aiden Kettletumble", "account_ref": "LAY003", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "chain_depth": 1,
     "opaque_intermediary_count": 3, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 0,
     "fragment_count": 1, "first_intermediary_name": "Thimblemote Nominees Ltd",
     "second_intermediary_name": "Delmore Trading Co", "destination_name": "Featherstone Holdings"},
    {"customer_name": "Farida Copperbristle", "account_ref": "LAY004", "segment": "Private Banking",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "chain_depth": 1,
     "opaque_intermediary_count": 1, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 1,
     "fragment_count": 1, "first_intermediary_name": "Cinderfield Partners",
     "second_intermediary_name": "Hollowgate Ventures", "destination_name": "Bramblewick Traders"},
    {"customer_name": "Lukas Mossfiddle", "account_ref": "LAY005", "segment": "Retail",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "chain_depth": 1,
     "opaque_intermediary_count": 1, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 0,
     "fragment_count": 3, "first_intermediary_name": "Millbrook Nominee Group",
     "second_intermediary_name": "Sandhurst Commerce Ltd", "destination_name": "Ravensdale Holdings"},
    {"customer_name": "Naomi Bramblequill", "account_ref": "LAY006", "segment": "Small Business",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "chain_depth": 2,
     "opaque_intermediary_count": 1, "total_intermediary_count": 8, "secrecy_jurisdiction_hops": 0,
     "fragment_count": 2, "first_intermediary_name": "Northgate Trading Partners",
     "second_intermediary_name": "Gammavane Imports Ltd", "destination_name": "Coldwater Mercantile Co"},
    {"customer_name": "Ibrahim Kettlewhistle", "account_ref": "LAY007", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Riverside Branch", "chain_depth": 4,
     "opaque_intermediary_count": 4, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 1,
     "fragment_count": 4, "first_intermediary_name": "Ferngrove Holdings",
     "second_intermediary_name": "Whitmore Trading Group", "destination_name": "Larchfield Ventures"},
    {"customer_name": "Valentina Marrowfiddle", "account_ref": "LAY008", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "chain_depth": 6,
     "opaque_intermediary_count": 4, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 1,
     "fragment_count": 4, "first_intermediary_name": "Cobblestone Traders",
     "second_intermediary_name": "Marrowthimble Holdings", "destination_name": "Millgate Ventures"},
    {"customer_name": "Hana Cloverthimble", "account_ref": "LAY009", "segment": "Private Banking",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "chain_depth": 4,
     "opaque_intermediary_count": 6, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 1,
     "fragment_count": 4, "first_intermediary_name": "Redmoor Commerce Ltd",
     "second_intermediary_name": "Blackfriar Traders", "destination_name": "Sunnydale Holdings"},
    {"customer_name": "Dmitri Flintquill", "account_ref": "LAY010", "segment": "Retail",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "chain_depth": 4,
     "opaque_intermediary_count": 4, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 2,
     "fragment_count": 4, "first_intermediary_name": "Elmswood Trading Co",
     "second_intermediary_name": "Farley Holdings", "destination_name": "Kingswell Traders"},
    {"customer_name": "Priya Ivykettle", "account_ref": "LAY011", "segment": "Small Business",
     "home_branch": "Meridian Trust Bank - Central Branch", "chain_depth": 4,
     "opaque_intermediary_count": 4, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 1,
     "fragment_count": 6, "first_intermediary_name": "Oakhaven Ventures",
     "second_intermediary_name": "Priorswood Trading", "destination_name": "Thimblecrumb Cross Holdings"},
    {"customer_name": "Marcus Larchbutton", "account_ref": "LAY012", "segment": "Private Banking",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "chain_depth": 2,
     "opaque_intermediary_count": 6, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 1,
     "fragment_count": 4, "first_intermediary_name": "Larchquill Holdings",
     "second_intermediary_name": "Greystone Traders", "destination_name": "Hallowfield Ventures"},
    {"customer_name": "Zara Tallowwisp", "account_ref": "LAY013", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "chain_depth": 4,
     "opaque_intermediary_count": 6, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 2,
     "fragment_count": 6, "first_intermediary_name": "Wrenbristle Trading Group",
     "second_intermediary_name": "Rushbristle Holdings", "destination_name": "Junipercrumb Traders"},
    {"customer_name": "Bjorn Yarrowkettle", "account_ref": "LAY014", "segment": "Small Business",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "chain_depth": 6,
     "opaque_intermediary_count": 6, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 2,
     "fragment_count": 6, "first_intermediary_name": "Marrowwhistle Commerce Ltd",
     "second_intermediary_name": "Duskcrumb Traders", "destination_name": "Blackmoor Holdings"},
    {"customer_name": "Isabela Brindlemote", "account_ref": "LAY015", "segment": "Private Banking",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "chain_depth": 8,
     "opaque_intermediary_count": 6, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 2,
     "fragment_count": 6, "first_intermediary_name": "Ravensworth Trading Co",
     "second_intermediary_name": "Elderbrook Holdings", "destination_name": "Thistlebutton Traders"},
    {"customer_name": "Anwar Gorsefiddle", "account_ref": "LAY016", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "chain_depth": 6,
     "opaque_intermediary_count": 9, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 2,
     "fragment_count": 6, "first_intermediary_name": "Thistlekettle Trading Group",
     "second_intermediary_name": "Sedgemoor Holdings", "destination_name": "Puddlewhistle Traders"},
    {"customer_name": "Greta Brackenfiddle", "account_ref": "LAY017", "segment": "Small Business",
     "home_branch": "Continental Correspondent Bank - Riverside Branch", "chain_depth": 6,
     "opaque_intermediary_count": 6, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 3,
     "fragment_count": 6, "first_intermediary_name": "Wexford Commerce Ltd",
     "second_intermediary_name": "Aldergate Holdings", "destination_name": "Kestrel Point Traders"},
    {"customer_name": "Rafael Quillmote", "account_ref": "LAY018", "segment": "Private Banking",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "chain_depth": 6,
     "opaque_intermediary_count": 9, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 2,
     "fragment_count": 9, "first_intermediary_name": "Ferntumble Trading Co",
     "second_intermediary_name": "Millhaven Holdings", "destination_name": "Stonebridge Traders"},
    {"customer_name": "Katarina Parsleythimble", "account_ref": "LAY019", "segment": "Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "chain_depth": 9,
     "opaque_intermediary_count": 8, "total_intermediary_count": 9, "secrecy_jurisdiction_hops": 4,
     "fragment_count": 9, "first_intermediary_name": "Gammavane Imports Ltd",
     "second_intermediary_name": "Continental Correspondent Bank", "destination_name": "Solano Exchange House"},
    {"customer_name": "Youssef Thistletumble", "account_ref": "LAY020", "segment": "Small Business",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "chain_depth": 8,
     "opaque_intermediary_count": 9, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 2,
     "fragment_count": 9, "first_intermediary_name": "Kingsbridge Nominee Trust",
     "second_intermediary_name": "Thistlefiddle Holdings", "destination_name": "Fairhaven Traders"},
    {"customer_name": "Ingrid Hazelwisp", "account_ref": "LAY021", "segment": "Private Banking",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "chain_depth": 8,
     "opaque_intermediary_count": 9, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 3,
     "fragment_count": 6, "first_intermediary_name": "Blackthorn Nominee Services",
     "second_intermediary_name": "Ravensbourne Holdings", "destination_name": "Wysteria Traders"},
    {"customer_name": "Chidi Sorrelthimble", "account_ref": "LAY022", "segment": "Retail",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "chain_depth": 6,
     "opaque_intermediary_count": 9, "total_intermediary_count": 10, "secrecy_jurisdiction_hops": 3,
     "fragment_count": 9, "first_intermediary_name": "Nettlefiddle Trading Co",
     "second_intermediary_name": "Marchmont Holdings", "destination_name": "Thistledown Traders"},
]

# destination_name, account_ref, bank, jurisdiction, relationship, prior_alerts
INTERMEDIARIES: List[Dict[str, Any]] = [
    {"destination_name": "Wrenfield Mercantile Ltd", "account_ref": "LAY001", "bank": "Meridian Trust Bank",
     "jurisdiction": "Ireland", "relationship": "Unverified intermediary", "prior_alerts": 0},
    {"destination_name": "Thistlewood Traders", "account_ref": "LAY002", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Canada", "relationship": "Unverified intermediary", "prior_alerts": 0},
    {"destination_name": "Featherstone Holdings", "account_ref": "LAY003", "bank": "Adriatic Union Bank",
     "jurisdiction": "Germany", "relationship": "Unverified intermediary", "prior_alerts": 0},
    {"destination_name": "Bramblewick Traders", "account_ref": "LAY004", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Cyprus", "relationship": "Unverified intermediary", "prior_alerts": 0},
    {"destination_name": "Ravensdale Holdings", "account_ref": "LAY005", "bank": "Helvetia Private Bank",
     "jurisdiction": "Switzerland", "relationship": "Unverified intermediary", "prior_alerts": 0},
    {"destination_name": "Coldwater Mercantile Co", "account_ref": "LAY006", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Kingdom", "relationship": "Unverified intermediary", "prior_alerts": 0},
    {"destination_name": "Larchfield Ventures", "account_ref": "LAY007", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Cyprus", "relationship": "Unverified intermediary", "prior_alerts": 1},
    {"destination_name": "Millgate Ventures", "account_ref": "LAY008", "bank": "Adriatic Union Bank",
     "jurisdiction": "Hong Kong", "relationship": "Unverified intermediary", "prior_alerts": 1},
    {"destination_name": "Sunnydale Holdings", "account_ref": "LAY009", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Panama", "relationship": "Unverified intermediary", "prior_alerts": 1},
    {"destination_name": "Kingswell Traders", "account_ref": "LAY010", "bank": "Helvetia Private Bank",
     "jurisdiction": "British Virgin Islands", "relationship": "Unverified intermediary", "prior_alerts": 1},
    {"destination_name": "Thimblecrumb Cross Holdings", "account_ref": "LAY011", "bank": "Meridian Trust Bank",
     "jurisdiction": "Singapore", "relationship": "Unverified intermediary", "prior_alerts": 1},
    {"destination_name": "Hallowfield Ventures", "account_ref": "LAY012", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Turkey", "relationship": "Unverified intermediary", "prior_alerts": 1},
    {"destination_name": "Junipercrumb Traders", "account_ref": "LAY013", "bank": "Adriatic Union Bank",
     "jurisdiction": "Panama", "relationship": "Unverified intermediary", "prior_alerts": 2},
    {"destination_name": "Blackmoor Holdings", "account_ref": "LAY014", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Cayman Islands", "relationship": "Unverified intermediary", "prior_alerts": 2},
    {"destination_name": "Thistlebutton Traders", "account_ref": "LAY015", "bank": "Helvetia Private Bank",
     "jurisdiction": "Marshall Islands", "relationship": "Unverified intermediary", "prior_alerts": 2},
    {"destination_name": "Puddlewhistle Traders", "account_ref": "LAY016", "bank": "Meridian Trust Bank",
     "jurisdiction": "British Virgin Islands", "relationship": "Unverified intermediary", "prior_alerts": 2},
    {"destination_name": "Kestrel Point Traders", "account_ref": "LAY017", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Cayman Islands", "relationship": "Unverified intermediary", "prior_alerts": 2},
    {"destination_name": "Stonebridge Traders", "account_ref": "LAY018", "bank": "Adriatic Union Bank",
     "jurisdiction": "Panama", "relationship": "Unverified intermediary", "prior_alerts": 3},
    {"destination_name": "Solano Exchange House", "account_ref": "LAY019", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Hong Kong", "relationship": "Money service business", "prior_alerts": 3},
    {"destination_name": "Fairhaven Traders", "account_ref": "LAY020", "bank": "Helvetia Private Bank",
     "jurisdiction": "Marshall Islands", "relationship": "Unverified intermediary", "prior_alerts": 3},
    {"destination_name": "Wysteria Traders", "account_ref": "LAY021", "bank": "Meridian Trust Bank",
     "jurisdiction": "Cayman Islands", "relationship": "Unverified intermediary", "prior_alerts": 3},
    {"destination_name": "Thistledown Traders", "account_ref": "LAY022", "bank": "Continental Correspondent Bank",
     "jurisdiction": "British Virgin Islands", "relationship": "Unverified intermediary", "prior_alerts": 3},
]

_TABLES = {"accounts.csv": ACCOUNTS, "intermediaries.csv": INTERMEDIARIES}


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
