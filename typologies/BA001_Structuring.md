# BA001 – Structuring

## Typology Overview

Structuring — known colloquially as "smurfing" — is the deliberate breaking-up of cash
deposits into amounts just under a currency-transaction reporting threshold (in the US,
the $10,000 CTR line) to keep individual deposits below the reporting trigger while the
account accumulates a large aggregate cash position. The structured cash is then moved
onward — wired out to a single beneficiary — turning a pattern of small, evasive deposits
into a laundering leg.

The finding is a clustering finding: it lives in the share of cash deposits sitting just
under the reporting line, how tightly those deposits cluster in time, how many distinct
branches or ATMs they are spread across, and how much of the structured cash is
subsequently wired to one downstream beneficiary.

---

# Typology Classification

| Attribute | Value |
|------------|------------|
| Typology ID | BA001 |
| Category | Cash Structuring |
| Risk Domain | Correspondent Banking Behavioural Analytics |
| Primary Threat | CTR-evasion cash structuring |
| Detection Type | Deposit-pattern & aggregation analytics |
| Investigation Type | Cash Structuring Investigation |
| Risk Level | High |

---

# Typology Description

Structuring networks seek to keep cash deposits below the reporting radar while still
moving a large aggregate sum, through:

- Multiple deposits each individually below the CTR reporting line
- Deposits clustered tightly in a short rolling window (days, not weeks)
- Deposits spread across several branches or ATMs to avoid a single teller noticing
  the pattern
- Structured cash subsequently aggregated and wired out to one beneficiary

---

# Typical Routing Structure

```text
Depositor  (customer account)
       │
       ▼
Sub-threshold Cash Deposits  (multiple, each < CTR line)   ← structured here
       │
       ▼
Home Branch / Multiple Branches & ATMs  (spread to avoid detection)
       │
       ▼
Aggregated Structured Cash  (accumulates on the account)
       │
       ▼
Beneficiary  (wired out downstream)
```

---

# FC-03 Network Intelligence Dependencies

| FC-03 Component | Purpose |
|------------|------------|
| ER001 Entity Resolution | Resolve the customer account, home branch and beneficiary |
| RD001 Relationship Discovery | Link the account to its depositing branches and beneficiary |
| NS001 Network Risk Scoring | Aggregate structuring exposure across the account's connections |
| NI012 Behavioural Pattern Network | Deposit-clustering and cross-branch behaviour |

---

# Key Risk Indicators

## Sub-threshold Clustering Indicators
- High share of cash deposits sitting just under the CTR reporting line
- Deposit amounts clustered near (but under) the threshold rather than spread naturally
- Round-number deposits inconsistent with the account's declared cash profile

## Temporal Clustering Indicators
- Multiple deposits inside a rolling 7-day window
- Deposit cadence inconsistent with normal payroll/business cash cycles

## Multi-location Indicators
- Deposits spread across several branches or ATMs on the same day or in the same window
- Geographic spread inconsistent with the customer's declared home location

## Aggregation-to-transfer Indicators
- Structured-in cash wired out to a single downstream beneficiary
- Wire timing shortly after the structured cash accumulates (short dwell)

---

# Exposure Scoring Framework

| Risk Category | Weight |
|------------|------------|
| Sub-threshold Clustering | 35% |
| Temporal Clustering | 25% |
| Multi-location | 20% |
| Aggregation to Transfer | 20% |

Band-midpoints 15/45/70/90, weighted sum, half-up, boundary at 80.

---

# Example Exposure Score — ACC019 Dmitri Mosstumble

| Component | Evidence | Band |
|------------|----------|------|
| Sub-threshold Clustering | $24,000 of $34,000 cash deposits sub-threshold (ratio 0.706) | Critical |
| Temporal Clustering | 12 deposits inside the busiest rolling 7-day window | Critical |
| Multi-location | Deposits spread across 6 distinct branches/ATMs | Critical |
| Aggregation to Transfer | $17,200 wired out of $19,000 structured in (ratio 0.905), to Gammavane Imports Ltd | Critical |

**Total Exposure Score: 90 / 100 — Critical** (the single highest-scoring account in the
sample data)

### Classification
- 0–29 = Low · 30–59 = Medium · 60–79 = High · 80–100 = Critical

---

# Business Logic

1. Resolve the account, its home branch, and its beneficiary.
2. Compute the sub-threshold cash ratio (sub-threshold deposits / total cash deposits).
3. Compute the temporal clustering of deposits inside a rolling 7-day window.
4. Count the distinct branches/ATMs the deposits are spread across.
5. Compute the aggregation-to-transfer ratio (wired out / structured in).
6. Score each of the four components against its band cut-lines.
7. Aggregate the weighted exposure score; escalate at or above the threshold.

---

# Detection Workflow

```text
Cash Deposit Screening
       ↓
Sub-threshold Ratio Calculation
       ↓
Temporal / Multi-location Clustering Analysis
       ↓
Aggregation-to-Transfer Assessment
       ↓
Exposure Scoring
       ↓
Investigator Escalation
```

---

# Python Analytics Example

```python
suspect = accounts[
    (accounts["sub_threshold_clustering_band"].isin(["High", "Critical"])) &
    (accounts["deposits_max_7d"] >= 6) &
    (accounts["distinct_locations"] >= 2)
]
alerts = suspect[suspect["exposure_score"] >= 80]
```

---

# Investigator Outcome

```text
Account:              Dmitri Mosstumble — ACC019
Home Branch:          Meridian Trust Bank - Uptown Branch
Total Cash Deposits:  $34,000 (12 deposits in the busiest 7-day window)
Sub-threshold Ratio:  0.706 ($24,000 of $34,000)
Distinct Locations:   6 branches/ATMs
Structured In:        $19,000 → Wired Out: $17,200 (ratio 0.905)
Beneficiary:          Gammavane Imports Ltd (Marshall Islands)
Exposure Score:       90 / 100
Investigation Outcome:  Escalate — CTR-evasion structuring with aggregation to a
                         single downstream beneficiary
```

---

# Regulatory Relevance

- FATF Recommendations 10 & 13 (customer due diligence and correspondent banking)
- BSA/CTR structuring provisions (31 U.S.C. § 5324)
- FinCEN structuring advisories and SAR guidance
- Wolfsberg correspondent-banking due-diligence principles

---

# Related Typologies

- BA002 Funnel Accounts
- BA005 Rapid Movement
- BA003 Mule Accounts

---

# Strategic Value

BA001 shows how deposit-pattern intelligence defeats reporting-threshold evasion: by
quantifying the sub-threshold clustering, the temporal and multi-location spread, and the
aggregation-to-transfer step, it surfaces cash that has been deliberately structured to
stay under the radar and would otherwise clear one deposit at a time. As the template
typology for the fc-06 Correspondent Banking Analytics family, its file set, scoring
convention, and fc-10 wiring pattern are what every subsequent BA0NN typology replicates.
