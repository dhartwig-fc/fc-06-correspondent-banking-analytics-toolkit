# BA009 – Transaction Laundering

## Typology Overview

Transaction laundering is a legitimate-looking merchant account used as a payment
processing front for hidden third parties: a card-processing relationship underwritten
against one declared business is quietly used to clear volume for merchants — or
principals — the acquirer never screened. Unlike BA007 Cash Intensive Activity (physical
cash disproportionate to a declared profile), the tell here runs through the CARD RAILS
themselves.

The finding lives in how far processed card volume runs above what the merchant declared
at boarding, how many unrelated sub-merchants are folded into the one processing
relationship, how much of the transaction mix does not match the boarded merchant
category code (MCC), and how anomalous the refund/chargeback pattern is against genuine
commerce.

---

# Typology Classification

| Attribute | Value |
|------------|------------|
| Typology ID | BA009 |
| Category | Transaction Laundering |
| Risk Domain | Correspondent Banking Behavioural Analytics |
| Primary Threat | Undisclosed payment processing pass-through for hidden principals |
| Detection Type | Volume-profile & MCC-consistency analytics |
| Investigation Type | Merchant Payment Processing Investigation |
| Risk Level | High |

---

# Typology Description

Transaction laundering merchant accounts conceal an undisclosed processing relationship
behind a plausible storefront, through:

- Processed card volume running far above the merchant's own declared business volume
- Unrelated sub-merchants funnelled through the one boarded processing relationship
- A transaction mix inconsistent with the merchant category code the account was boarded
  under
- A refund/chargeback pattern consistent with laundering rather than genuine commerce
  (self-refunds, test transactions, an absent dispute cycle)

---

# Typical Routing Structure

```text
Hidden Third-Party Merchants  (unrelated businesses, unscreened)
       │
       ▼
Card Processing Volume  (disproportionate to declared business)      ← collected here
       │
       ▼
Merchant Account  (boarded storefront, the processing front)
       │
       ▼
Payment Processor  (clears the volume, unaware of the pass-through)
       │
       ▼
Undisclosed Principal  (the real beneficiary of the processed funds)
```

---

# FC-03 Network Intelligence Dependencies

| FC-03 Component | Purpose |
|------------|------------|
| ER001 Entity Resolution | Resolve the merchant account, its processor and hidden sub-merchants |
| RD001 Relationship Discovery | Link the account to its processor and unrelated sub-merchants |
| NS001 Network Risk Scoring | Aggregate processing exposure across the account's connections |
| NI012 Behavioural Pattern Network | Volume-profile and MCC-consistency behaviour |

---

# Key Risk Indicators

## Volume Profile Mismatch Indicators
- Processed card volume running multiples of the merchant's own declared business volume
- Volume growth with no plausible business explanation

## Third-Party Indicators
- Unrelated sub-merchants folded into the one boarded processing relationship
- Multiple unconnected storefronts settling to the same underlying account

## MCC Inconsistency Indicators
- Transaction types inconsistent with the boarded merchant category code
- A "retail goods" MCC clearing digital, subscription or cash-equivalent transaction types

## Refund/Chargeback Anomaly Indicators
- An elevated refund/chargeback rate with no genuine customer dispute cycle
- Self-refunds or test transactions inconsistent with real commerce

---

# Exposure Scoring Framework

| Risk Category | Weight |
|------------|------------|
| Volume Profile Mismatch | 30% |
| Third-Party Indicators | 25% |
| MCC Inconsistency | 25% |
| Refund/Chargeback Anomaly | 20% |

Band-midpoints 15/45/70/90, weighted sum, half-up, boundary at 80.

---

# Example Exposure Score — MER019 Lumen Digital Marketplace Ltd

| Component | Evidence | Band |
|------------|----------|------|
| Volume Profile Mismatch | $1,120,000 processed vs $350,000 declared business volume (3.20x) | Critical |
| Third-Party Indicators | 8 unrelated sub-merchants funnelled through the relationship | Critical |
| MCC Inconsistency | 1,100 of 2,000 transactions inconsistent with the boarded MCC (ratio 0.55) | Critical |
| Refund/Chargeback Anomaly | $156,800 of $1,120,000 processed returned (ratio 0.14) | Critical |

**Total Exposure Score: 90 / 100 — Critical** (the single highest-scoring account in the
sample data)

### Classification
- 0–29 = Low · 30–59 = Medium · 60–79 = High · 80–100 = Critical

---

# Business Logic

1. Resolve the merchant account, its declared business profile, and its processor.
2. Compute the volume profile mismatch ratio (processed card volume / declared business
   volume).
3. Count the unrelated sub-merchants funnelled through the processing relationship.
4. Compute the MCC inconsistency ratio (mismatched transactions / total transactions).
5. Compute the refund/chargeback anomaly ratio (returned value / total processed value).
6. Score each of the four components against its band cut-lines.
7. Aggregate the weighted exposure score; escalate at or above the threshold.

---

# Detection Workflow

```text
Card Processing Screening
       ↓
Volume Profile Mismatch Calculation
       ↓
Third-Party / MCC Consistency Analysis
       ↓
Refund/Chargeback Assessment
       ↓
Exposure Scoring
       ↓
Investigator Escalation
```

---

# Python Analytics Example

```python
suspect = merchants[
    (merchants["volume_profile_mismatch_band"].isin(["High", "Critical"])) &
    (merchants["unrelated_merchant_count"] >= 4) &
    (merchants["mcc_mismatched_txn_count"] / merchants["total_txn_count"] >= 0.25)
]
alerts = suspect[suspect["exposure_score"] >= 80]
```

---

# Investigator Outcome

```text
Account:                Lumen Digital Marketplace Ltd — MER019
Home Branch:             Helvetia Private Bank - Lakeside Branch
Processed Volume:        $1,120,000 of $350,000 declared (3.20x)
Unrelated Merchants:      8 sub-merchants
MCC Mismatch:             1,100 of 2,000 transactions (ratio 0.55)
Refund/Chargeback:        $156,800 of $1,120,000 (ratio 0.14)
Processor:                Continental Merchant Services
Undisclosed Principal:    John Cloverspindle (P001) — the network's PEP
Exposure Score:           90 / 100
Investigation Outcome:    Escalate — card processing volume disproportionate to declared
                          business, unrelated sub-merchants funnelled through, transaction
                          mix inconsistent with the boarded MCC, processing quietly for an
                          undisclosed PEP
```

---

# Regulatory Relevance

- FATF Recommendations 10 & 13 (customer due diligence and correspondent banking)
- BSA transaction-laundering and money-transmission provisions (31 U.S.C. § 5324, 31 CFR §
  1010)
- Card network merchant-boarding and factoring/aggregation rules (Visa/Mastercard
  operating regulations)
- Wolfsberg correspondent-banking due-diligence principles

---

# Related Typologies

- BA001 Structuring
- BA007 Cash Intensive Activity
- BA008 Layering

---

# Strategic Value

BA009 shows how undisclosed-pass-through intelligence defeats a merchant account used as
a payment processing front: by quantifying the volume profile mismatch against the
merchant's own declared business, the count of unrelated sub-merchants funnelled through
the relationship, the MCC inconsistency of the transaction mix, and the refund/chargeback
anomaly, it surfaces transaction laundering that would otherwise pass as ordinary card
processing growth. BA009 is the estate's designated PERSON-bridge typology: unlike
BA001–BA006/BA008 (which bridge onto a connected COMPANY, matched on its exact name),
MER019 quietly processes card volume for **John Cloverspindle**, the network's PEP — a real
person, not a company. The canonical entity resolver's person guard deliberately refuses
to merge two person nodes on name alone (two different people can share a name), so the
bridge is carried on the shared local id (P001) instead, the same pattern SAN005 uses for
its own John Cloverspindle PEP hit. As the ninth typology in the fc-06 Correspondent Banking
Analytics family, BA009 reuses BA001's file set, scoring convention, and fc-10 wiring
pattern verbatim, confirming the template replicates cleanly even when the bridge is a
person rather than a company.
