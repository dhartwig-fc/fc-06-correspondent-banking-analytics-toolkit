# BA009 Transaction Laundering — Exposure Scoring Framework

Specialises the macro framework for undisclosed payment-processing pass-through.
Implemented and validated by `python/specific/BA009/ba009_risk_model.py`.

## Components and weights

| Component | Weight | What it measures |
|-----------|--------|------------------|
| Volume Profile Mismatch | 30% | Processed card/payment volume vs the merchant's own declared business volume at boarding |
| Third-Party Indicators | 25% | Count of unrelated sub-merchants funnelled through the one processing relationship |
| MCC Inconsistency | 25% | Share of transactions inconsistent with the merchant category code (MCC) the account was boarded under |
| Refund/Chargeback Anomaly | 20% | Share of processed value returned as refunds or chargebacks -- inconsistent with genuine commerce |

## Component banding rules

### Volume Profile Mismatch
`r = processed_card_volume / declared_business_volume`. Both amounts are REQUIRED — the
declared volume is what the merchant told the acquirer at boarding.
- r < 1.3 → Low · r < 1.8 → Medium · r < 2.5 → High · otherwise → Critical

### Third-Party Indicators
`unrelated_merchant_count` is REQUIRED — not measured is not zero unrelated merchants.
The count of unrelated sub-merchants funnelled through the one processing relationship,
the hallmark of an aggregator boarding hidden merchants under a single legitimate
storefront.
- n ≤ 1 → Low · n ≤ 3 → Medium · n ≤ 6 → High · otherwise (≥ 7) → Critical

### MCC Inconsistency
`r = mcc_mismatched_txn_count / total_txn_count`. Both counts are REQUIRED.
- r < 0.10 → Low · r < 0.25 → Medium · r < 0.45 → High · otherwise → Critical

### Refund/Chargeback Anomaly
`r = refund_chargeback_amount / total_processed_amount`. Both amounts are REQUIRED.
- r < 0.02 → Low · r < 0.05 → Medium · r < 0.10 → High · otherwise → Critical

## Scoring

Band midpoints (15/45/70/90), weighted sum, half-up rounding, boundaries at 80. Graded.

## Worked example — MER019 (Lumen Digital Marketplace Ltd)

| Component | Evidence | Band | Contribution |
|-----------|----------|------|--------------|
| Volume Profile Mismatch | $1,120,000 processed vs $350,000 declared business volume (r = 3.20) | Critical | 27.0 |
| Third-Party Indicators | 8 unrelated sub-merchants funnelled through the relationship | Critical | 22.5 |
| MCC Inconsistency | 1,100 of 2,000 transactions inconsistent with the boarded MCC (r = 0.55) | Critical | 22.5 |
| Refund/Chargeback Anomaly | $156,800 of $1,120,000 processed returned as refunds/chargebacks (r = 0.14) | Critical | 18.0 |
| **Exposure score** | | | **90 / 100 — Critical** |

A clean merchant with all four components Low scores 15/100 (MER001, Bramblewood Home
Goods Ltd). Alert threshold: ≥ 80 — the sample data ships four accounts at or above it
(MER019 90, MER020 86, MER021/MER022 85 each), proving the scorer discriminates rather
than rubber-stamping every row. MER019 is the single highest-scoring account, which is
deliberate: the FC-10 adapter builds its case/graph from the top-scored row, and MER019
is quietly processing card volume on behalf of an undisclosed principal — **John Smith**,
the PEP already in the estate network. Because John Smith is a PERSON, the fusion bridge
is carried on the shared local id (`linked_individual_id` = "P001", the same id NI001 and
SAN005 use for him), not on the name: the canonical resolver's person guard never merges
two person nodes on name alone, only on a shared id.
