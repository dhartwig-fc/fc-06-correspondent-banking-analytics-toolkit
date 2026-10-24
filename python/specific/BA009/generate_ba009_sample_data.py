"""Generate synthetic sample data for BA009 Transaction Laundering.

22 merchant accounts (>= the 2026-08-09 20-row standard; BA009 is NOT grandfathered),
spread across all four exposure bands so the scorer visibly discriminates rather than
rubber-stamping every row:

  MER001-MER006   Low       (15)
  MER007-MER012   Medium    (45)
  MER013-MER018   High      (70)
  MER019-MER022   Critical  (85-90)  -- at least two, per the house standard

Fusion bridge: MER019 (Lumen Digital Marketplace Ltd, 90/Critical, the single
highest-scoring account in the set) is quietly processing card volume on behalf of an
undisclosed principal -- **John Cloverspindle**, the PEP already in the estate network (NI001's
widest-reach director, SAN005's PEP hit, id P001). Unlike BA001-BA006/BA008 (where the
bridge is a connected COMPANY, matched on its exact name) John Cloverspindle is a PERSON, and
the canonical entity resolver's person guard deliberately refuses to merge two person
nodes on name alone -- two different people can share a name. So the bridge here is
carried on the SHARED LOCAL ID: MER019's `linked_individual_id` column is the literal
network id "P001", not the string "John Cloverspindle" -- the same pattern SAN005 uses for its
own John Cloverspindle PEP hit (see fc-10 manifests/san005.yaml). Canonical resolution then
joins BA009's P001 occurrence to NI001's and SAN005's P001 occurrence on id, not on name.
MER020 (Nightshade Vape & Tobacco Ltd), MER021 (Ironvale Bullion & Coin Ltd) and MER022
(Halcyon Gaming Credits Ltd) are the other three Critical-band merchants, also alerting
but strictly below MER019 so the bridge row is unambiguous.

Run:  python3 generate_ba009_sample_data.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent / "sample-data"

# customer_name, account_ref, segment, home_branch, processed_card_volume,
# declared_business_volume, unrelated_merchant_count, mcc_mismatched_txn_count,
# total_txn_count, refund_chargeback_amount, total_processed_amount, processor_name,
# hidden_merchant_name, linked_individual_id, linked_individual_name
MERCHANTS: List[Dict[str, Any]] = [
    {"customer_name": "Bramblewood Home Goods Ltd", "account_ref": "MER001", "segment": "Home Goods Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "processed_card_volume": 462000,
     "declared_business_volume": 420000, "unrelated_merchant_count": 1, "mcc_mismatched_txn_count": 35,
     "total_txn_count": 700, "refund_chargeback_amount": 4620, "total_processed_amount": 462000,
     "processor_name": "Meridian PayLink Processing", "hidden_merchant_name": "Quickcart Traders Ltd",
     "linked_individual_id": "Maria Brackentumble", "linked_individual_name": "Maria Bračkentumble"},
    {"customer_name": "Larkspur Digital Books Co", "account_ref": "MER002", "segment": "Digital Books & Media",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "processed_card_volume": 518400,
     "declared_business_volume": 480000, "unrelated_merchant_count": 0, "mcc_mismatched_txn_count": 26,
     "total_txn_count": 650, "refund_chargeback_amount": 4147, "total_processed_amount": 518400,
     "processor_name": "Continental Merchant Services", "hidden_merchant_name": "SwiftBuy Distribution Co",
     "linked_individual_id": "Dmitri Mosstumble", "linked_individual_name": "Dmitri Mosstumble"},
    {"customer_name": "Cinder & Co Apparel Ltd", "account_ref": "MER003", "segment": "Apparel Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "processed_card_volume": 575000,
     "declared_business_volume": 500000, "unrelated_merchant_count": 1, "mcc_mismatched_txn_count": 56,
     "total_txn_count": 800, "refund_chargeback_amount": 8050, "total_processed_amount": 575000,
     "processor_name": "Adriatic Card Clearing Ltd", "hidden_merchant_name": "NimbusSale Goods Ltd",
     "linked_individual_id": "Aisha Ivybutton", "linked_individual_name": "Aisha Ivybutton"},
    {"customer_name": "Wavecrest Electronics Ltd", "account_ref": "MER004", "segment": "Consumer Electronics",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "processed_card_volume": 683200,
     "declared_business_volume": 610000, "unrelated_merchant_count": 1, "mcc_mismatched_txn_count": 43,
     "total_txn_count": 720, "refund_chargeback_amount": 7515, "total_processed_amount": 683200,
     "processor_name": "Pacific Gateway Payments", "hidden_merchant_name": "PrimeLoop Retail Ltd",
     "linked_individual_id": "Tomas Parsleythimble", "linked_individual_name": "Tomas Parsleythimble"},
    {"customer_name": "Thistlewood Pet Supplies Ltd", "account_ref": "MER005", "segment": "Pet Supplies Retail",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "processed_card_volume": 425100,
     "declared_business_volume": 390000, "unrelated_merchant_count": 0, "mcc_mismatched_txn_count": 30,
     "total_txn_count": 600, "refund_chargeback_amount": 3826, "total_processed_amount": 425100,
     "processor_name": "Helvetia Settlement Partners", "hidden_merchant_name": "Vanta Point Commerce Ltd",
     "linked_individual_id": "Maria Brackentumble", "linked_individual_name": "Maria Bračkentumble"},
    {"customer_name": "Amberglow Craft Supplies Ltd", "account_ref": "MER006", "segment": "Craft Supplies Retail",
     "home_branch": "Continental Correspondent Bank - Riverside Branch", "processed_card_volume": 649000,
     "declared_business_volume": 550000, "unrelated_merchant_count": 1, "mcc_mismatched_txn_count": 60,
     "total_txn_count": 750, "refund_chargeback_amount": 10384, "total_processed_amount": 649000,
     "processor_name": "Meridian PayLink Processing", "hidden_merchant_name": "Coalridge Mercantile Co",
     "linked_individual_id": "Dmitri Mosstumble", "linked_individual_name": "Dmitri Mosstumble"},
    {"customer_name": "Foxglove Fitness Gear Ltd", "account_ref": "MER007", "segment": "Fitness Equipment Retail",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "processed_card_volume": 560000,
     "declared_business_volume": 400000, "unrelated_merchant_count": 2, "mcc_mismatched_txn_count": 140,
     "total_txn_count": 1000, "refund_chargeback_amount": 14560, "total_processed_amount": 560000,
     "processor_name": "Continental Merchant Services", "hidden_merchant_name": "Everline Trading Ltd",
     "linked_individual_id": "Aisha Ivybutton", "linked_individual_name": "Aisha Ivybutton"},
    {"customer_name": "Driftwood Home Decor Co", "account_ref": "MER008", "segment": "Home Decor Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "processed_card_volume": 713000,
     "declared_business_volume": 460000, "unrelated_merchant_count": 3, "mcc_mismatched_txn_count": 187,
     "total_txn_count": 1100, "refund_chargeback_amount": 22103, "total_processed_amount": 713000,
     "processor_name": "Adriatic Card Clearing Ltd", "hidden_merchant_name": "Brightfold Supply Co",
     "linked_individual_id": "Tomas Parsleythimble", "linked_individual_name": "Tomas Parsleythimble"},
    {"customer_name": "Bramblespindle Lane Toys Ltd", "account_ref": "MER009", "segment": "Toys & Games Retail",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "processed_card_volume": 754000,
     "declared_business_volume": 520000, "unrelated_merchant_count": 2, "mcc_mismatched_txn_count": 240,
     "total_txn_count": 1200, "refund_chargeback_amount": 21112, "total_processed_amount": 754000,
     "processor_name": "Pacific Gateway Payments", "hidden_merchant_name": "Meadowspring Goods Ltd",
     "linked_individual_id": "Maria Brackentumble", "linked_individual_name": "Maria Bračkentumble"},
    {"customer_name": "Sable Ridge Outdoor Co", "account_ref": "MER010", "segment": "Outdoor Equipment Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "processed_card_volume": 615600,
     "declared_business_volume": 380000, "unrelated_merchant_count": 3, "mcc_mismatched_txn_count": 158,
     "total_txn_count": 1050, "refund_chargeback_amount": 22162, "total_processed_amount": 615600,
     "processor_name": "Helvetia Settlement Partners", "hidden_merchant_name": "Oakcastle Distribution Ltd",
     "linked_individual_id": "Dmitri Mosstumble", "linked_individual_name": "Dmitri Mosstumble"},
    {"customer_name": "Hollowbrook Beauty Ltd", "account_ref": "MER011", "segment": "Beauty & Cosmetics Retail",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "processed_card_volume": 750000,
     "declared_business_volume": 500000, "unrelated_merchant_count": 2, "mcc_mismatched_txn_count": 218,
     "total_txn_count": 1150, "refund_chargeback_amount": 24750, "total_processed_amount": 750000,
     "processor_name": "Meridian PayLink Processing", "hidden_merchant_name": "Palisade Retail Group",
     "linked_individual_id": "Aisha Ivybutton", "linked_individual_name": "Aisha Ivybutton"},
    {"customer_name": "Quill & Ink Stationery Co", "account_ref": "MER012", "segment": "Stationery Retail",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "processed_card_volume": 748000,
     "declared_business_volume": 440000, "unrelated_merchant_count": 3, "mcc_mismatched_txn_count": 275,
     "total_txn_count": 1250, "refund_chargeback_amount": 29920, "total_processed_amount": 748000,
     "processor_name": "Continental Merchant Services", "hidden_merchant_name": "Fernwood Traders Ltd",
     "linked_individual_id": "Tomas Parsleythimble", "linked_individual_name": "Tomas Parsleythimble"},
    {"customer_name": "Cobalt Peak Electronics Ltd", "account_ref": "MER013", "segment": "Consumer Electronics",
     "home_branch": "Continental Correspondent Bank - Riverside Branch", "processed_card_volume": 665000,
     "declared_business_volume": 350000, "unrelated_merchant_count": 4, "mcc_mismatched_txn_count": 448,
     "total_txn_count": 1600, "refund_chargeback_amount": 38570, "total_processed_amount": 665000,
     "processor_name": "Adriatic Card Clearing Ltd", "hidden_merchant_name": "Grayhollow Commerce Ltd",
     "linked_individual_id": "Maria Brackentumble", "linked_individual_name": "Maria Bračkentumble"},
    {"customer_name": "Ravenswood Fashion Ltd", "account_ref": "MER014", "segment": "Fashion Retail",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "processed_card_volume": 840500,
     "declared_business_volume": 410000, "unrelated_merchant_count": 5, "mcc_mismatched_txn_count": 576,
     "total_txn_count": 1800, "refund_chargeback_amount": 54632, "total_processed_amount": 840500,
     "processor_name": "Pacific Gateway Payments", "hidden_merchant_name": "Sabertooth Supply Ltd",
     "linked_individual_id": "Dmitri Mosstumble", "linked_individual_name": "Dmitri Mosstumble"},
    {"customer_name": "Ember Hollow Games Ltd", "account_ref": "MER015", "segment": "Video Games Retail",
     "home_branch": "Meridian Trust Bank - Central Branch", "processed_card_volume": 817000,
     "declared_business_volume": 380000, "unrelated_merchant_count": 4, "mcc_mismatched_txn_count": 595,
     "total_txn_count": 1700, "refund_chargeback_amount": 57190, "total_processed_amount": 817000,
     "processor_name": "Helvetia Settlement Partners", "hidden_merchant_name": "Windmere Goods Co",
     "linked_individual_id": "Aisha Ivybutton", "linked_individual_name": "Aisha Ivybutton"},
    {"customer_name": "Willowmere Jewellery Ltd", "account_ref": "MER016", "segment": "Jewellery Retail",
     "home_branch": "Continental Correspondent Bank - Harbor Branch", "processed_card_volume": 838500,
     "declared_business_volume": 430000, "unrelated_merchant_count": 6, "mcc_mismatched_txn_count": 722,
     "total_txn_count": 1900, "refund_chargeback_amount": 62888, "total_processed_amount": 838500,
     "processor_name": "Meridian PayLink Processing", "hidden_merchant_name": "Larkfield Distribution Ltd",
     "linked_individual_id": "Tomas Parsleythimble", "linked_individual_name": "Tomas Parsleythimble"},
    {"customer_name": "Frostgate Appliances Ltd", "account_ref": "MER017", "segment": "Home Appliances Retail",
     "home_branch": "Adriatic Union Bank - Old Town Branch", "processed_card_volume": 900000,
     "declared_business_volume": 400000, "unrelated_merchant_count": 5, "mcc_mismatched_txn_count": 800,
     "total_txn_count": 2000, "refund_chargeback_amount": 73800, "total_processed_amount": 900000,
     "processor_name": "Continental Merchant Services", "hidden_merchant_name": "Thimblemote Retail Ltd",
     "linked_individual_id": "Maria Brackentumble", "linked_individual_name": "Maria Bračkentumble"},
    {"customer_name": "Stonebridge Digital Media Ltd", "account_ref": "MER018", "segment": "Digital Media Retail",
     "home_branch": "Pacific Rim Commercial Bank - Marina Branch", "processed_card_volume": 1057500,
     "declared_business_volume": 450000, "unrelated_merchant_count": 6, "mcc_mismatched_txn_count": 882,
     "total_txn_count": 2100, "refund_chargeback_amount": 93060, "total_processed_amount": 1057500,
     "processor_name": "Adriatic Card Clearing Ltd", "hidden_merchant_name": "Copperline Trading Co",
     "linked_individual_id": "Dmitri Mosstumble", "linked_individual_name": "Dmitri Mosstumble"},
    {"customer_name": "Lumen Digital Marketplace Ltd", "account_ref": "MER019", "segment": "Online Marketplace",
     "home_branch": "Helvetia Private Bank - Lakeside Branch", "processed_card_volume": 1120000,
     "declared_business_volume": 350000, "unrelated_merchant_count": 8, "mcc_mismatched_txn_count": 1100,
     "total_txn_count": 2000, "refund_chargeback_amount": 156800, "total_processed_amount": 1120000,
     "processor_name": "Continental Merchant Services", "hidden_merchant_name": "Silverbrook Merchants Ltd",
     "linked_individual_id": "P001", "linked_individual_name": "John Cloverspindle"},
    {"customer_name": "Nightshade Vape & Tobacco Ltd", "account_ref": "MER020", "segment": "Vape & Tobacco Retail",
     "home_branch": "Continental Correspondent Bank - Riverside Branch", "processed_card_volume": 1219800,
     "declared_business_volume": 380000, "unrelated_merchant_count": 9, "mcc_mismatched_txn_count": 1250,
     "total_txn_count": 2200, "refund_chargeback_amount": 85386, "total_processed_amount": 1219800,
     "processor_name": "Pacific Gateway Payments", "hidden_merchant_name": "Thornfield Supply Ltd",
     "linked_individual_id": "Maria Brackentumble", "linked_individual_name": "Maria Bračkentumble"},
    {"customer_name": "Ironvale Bullion & Coin Ltd", "account_ref": "MER021", "segment": "Bullion & Coin Dealer",
     "home_branch": "Meridian Trust Bank - Uptown Branch", "processed_card_volume": 1098000,
     "declared_business_volume": 360000, "unrelated_merchant_count": 5, "mcc_mismatched_txn_count": 1050,
     "total_txn_count": 2100, "refund_chargeback_amount": 131760, "total_processed_amount": 1098000,
     "processor_name": "Adriatic Card Clearing Ltd", "hidden_merchant_name": "Wrenhaven Commerce Ltd",
     "linked_individual_id": "Dmitri Mosstumble", "linked_individual_name": "Dmitri Mosstumble"},
    {"customer_name": "Halcyon Gaming Credits Ltd", "account_ref": "MER022", "segment": "Digital Gaming Credits",
     "home_branch": "Meridian Trust Bank - Central Branch", "processed_card_volume": 986000,
     "declared_business_volume": 340000, "unrelated_merchant_count": 8, "mcc_mismatched_txn_count": 700,
     "total_txn_count": 2000, "refund_chargeback_amount": 128180, "total_processed_amount": 986000,
     "processor_name": "Helvetia Settlement Partners", "hidden_merchant_name": "Fallowmoor Traders Ltd",
     "linked_individual_id": "Aisha Ivybutton", "linked_individual_name": "Aisha Ivybutton"},
]

# processor_name, account_ref, bank, jurisdiction, relationship, prior_alerts
PROCESSORS: List[Dict[str, Any]] = [
    {"processor_name": "Meridian PayLink Processing", "account_ref": "MER001", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Kingdom", "relationship": "Card acquiring processor", "prior_alerts": 0},
    {"processor_name": "Continental Merchant Services", "account_ref": "MER002", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Ireland", "relationship": "Card acquiring processor", "prior_alerts": 0},
    {"processor_name": "Adriatic Card Clearing Ltd", "account_ref": "MER003", "bank": "Adriatic Union Bank",
     "jurisdiction": "Germany", "relationship": "Card acquiring processor", "prior_alerts": 0},
    {"processor_name": "Pacific Gateway Payments", "account_ref": "MER004", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Hong Kong", "relationship": "Card acquiring processor", "prior_alerts": 1},
    {"processor_name": "Helvetia Settlement Partners", "account_ref": "MER005", "bank": "Helvetia Private Bank",
     "jurisdiction": "Switzerland", "relationship": "Card acquiring processor", "prior_alerts": 0},
    {"processor_name": "Meridian PayLink Processing", "account_ref": "MER006", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Kingdom", "relationship": "Card acquiring processor", "prior_alerts": 0},
    {"processor_name": "Continental Merchant Services", "account_ref": "MER007", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Cyprus", "relationship": "Card acquiring processor", "prior_alerts": 1},
    {"processor_name": "Adriatic Card Clearing Ltd", "account_ref": "MER008", "bank": "Adriatic Union Bank",
     "jurisdiction": "Panama", "relationship": "Card acquiring processor", "prior_alerts": 1},
    {"processor_name": "Pacific Gateway Payments", "account_ref": "MER009", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Singapore", "relationship": "Card acquiring processor", "prior_alerts": 0},
    {"processor_name": "Helvetia Settlement Partners", "account_ref": "MER010", "bank": "Helvetia Private Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Card acquiring processor", "prior_alerts": 1},
    {"processor_name": "Meridian PayLink Processing", "account_ref": "MER011", "bank": "Meridian Trust Bank",
     "jurisdiction": "Turkey", "relationship": "Card acquiring processor", "prior_alerts": 1},
    {"processor_name": "Continental Merchant Services", "account_ref": "MER012", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Hong Kong", "relationship": "Card acquiring processor", "prior_alerts": 1},
    {"processor_name": "Adriatic Card Clearing Ltd", "account_ref": "MER013", "bank": "Adriatic Union Bank",
     "jurisdiction": "Cyprus", "relationship": "Card acquiring processor", "prior_alerts": 1},
    {"processor_name": "Pacific Gateway Payments", "account_ref": "MER014", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Panama", "relationship": "Card acquiring processor", "prior_alerts": 2},
    {"processor_name": "Helvetia Settlement Partners", "account_ref": "MER015", "bank": "Helvetia Private Bank",
     "jurisdiction": "British Virgin Islands", "relationship": "Card acquiring processor", "prior_alerts": 1},
    {"processor_name": "Meridian PayLink Processing", "account_ref": "MER016", "bank": "Meridian Trust Bank",
     "jurisdiction": "United Arab Emirates", "relationship": "Card acquiring processor", "prior_alerts": 2},
    {"processor_name": "Continental Merchant Services", "account_ref": "MER017", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Hong Kong", "relationship": "Card acquiring processor", "prior_alerts": 2},
    {"processor_name": "Adriatic Card Clearing Ltd", "account_ref": "MER018", "bank": "Adriatic Union Bank",
     "jurisdiction": "Panama", "relationship": "Card acquiring processor", "prior_alerts": 2},
    {"processor_name": "Continental Merchant Services", "account_ref": "MER019", "bank": "Continental Correspondent Bank",
     "jurisdiction": "Marshall Islands", "relationship": "Card acquiring processor", "prior_alerts": 3},
    {"processor_name": "Pacific Gateway Payments", "account_ref": "MER020", "bank": "Pacific Rim Commercial Bank",
     "jurisdiction": "Panama", "relationship": "Card acquiring processor", "prior_alerts": 3},
    {"processor_name": "Adriatic Card Clearing Ltd", "account_ref": "MER021", "bank": "Adriatic Union Bank",
     "jurisdiction": "Turkey", "relationship": "Card acquiring processor", "prior_alerts": 3},
    {"processor_name": "Helvetia Settlement Partners", "account_ref": "MER022", "bank": "Helvetia Private Bank",
     "jurisdiction": "Panama", "relationship": "Card acquiring processor", "prior_alerts": 2},
]

_TABLES = {"merchants.csv": MERCHANTS, "processors.csv": PROCESSORS}


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
