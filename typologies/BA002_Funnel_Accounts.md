# BA002 – Funnel Accounts

## Typology Overview

A funnel account is a collection point: it receives many small, geographically-dispersed
deposits from unrelated depositors, then rapidly moves the aggregated funds onward to a
single downstream beneficiary before the pattern can be reviewed. It is the collection-side
mirror of BA001 Structuring — where structuring conceals the deposit pattern beneath a
reporting line, funnelling conceals the collection pattern behind volume and dispersion,
then clears the account out fast.

The finding is a fan-in / fan-out finding: it lives in how many distinct regions the
depositors are drawn from, how many distinct unrelated depositors feed the account, how
briefly the funnelled cash dwells on the account before it clears onward, and how much of
the outbound funds concentrate on one downstream beneficiary.

---

# Typology Classification

| Attribute | Value |
|------------|------------|
| Typology ID | BA002 |
| Category | Funnel Activity |
| Risk Domain | Correspondent Banking Behavioural Analytics |
| Primary Threat | Fan-in deposit collection with rapid onward clearance |
| Detection Type | Deposit-dispersion & passthrough-velocity analytics |
| Investigation Type | Funnel Account Investigation |
| Risk Level | High |

---

# Typology Description

Funnel account networks collect widely-dispersed small deposits and clear them out fast,
through:

- Deposits sourced from many distinct, geographically-dispersed regions
- A large number of distinct, apparently unrelated depositors feeding one account
- A short dwell between the funds landing and clearing onward — no accumulation, no
  business rationale for the pause
- Outbound funds concentrated on one downstream beneficiary rather than dispersed onward

---

# Typical Routing Structure

```text
Many Depositors  (geographically dispersed, unrelated)
       │
       ▼
Fan-in Deposits  (multiple, small, distinct regions)     ← collected here
       │
       ▼
Funnel Account  (brief dwell — no accumulation)
       │
       ▼
Rapid Passthrough  (short in-to-out dwell)
       │
       ▼
Beneficiary  (outbound funds concentrated on one entity)
```

---

# FC-03 Network Intelligence Dependencies

| FC-03 Component | Purpose |
|------------|------------|
| ER001 Entity Resolution | Resolve the funnel account, its depositors and its beneficiary |
| RD001 Relationship Discovery | Link the account to its source depositors and beneficiary |
| NS001 Network Risk Scoring | Aggregate funnelling exposure across the account's connections |
| NI012 Behavioural Pattern Network | Fan-in / fan-out and dwell-time behaviour |

---

# Key Risk Indicators

## Geographic Dispersion Indicators
- Deposits sourced from many distinct regions inconsistent with a single local customer base
- Depositor locations with no plausible relationship to the account holder's declared
  business or residence

## Inflow Fan-in Indicators
- A large number of distinct, apparently unrelated depositors feeding one account
- Deposit sizes individually unremarkable, but the depositor count itself is anomalous

## Rapid Passthrough Indicators
- Funds clearing onward within hours of landing, with no plausible accumulation purpose
- Passthrough timing inconsistent with the account's declared business cycle

## Beneficiary Concentration Indicators
- Outbound funds concentrated on a single downstream beneficiary rather than dispersed
- Beneficiary already flagged elsewhere in the network

---

# Exposure Scoring Framework

| Risk Category | Weight |
|------------|------------|
| Geographic Dispersion | 30% |
| Inflow Fan-in | 25% |
| Rapid Passthrough | 25% |
| Beneficiary Concentration | 20% |

Band-midpoints 15/45/70/90, weighted sum, half-up, boundary at 80.

---

# Example Exposure Score — FUN019 Zara Tallowwisp

| Component | Evidence | Band |
|------------|----------|------|
| Geographic Dispersion | Deposits drawn from 9 distinct regions | Critical |
| Inflow Fan-in | 33 distinct depositors feeding the account | Critical |
| Rapid Passthrough | Longest dwell before clearing onward: 3 hours | Critical |
| Beneficiary Concentration | $90,000 of $100,000 outbound to one beneficiary (ratio 0.900), Zeta Commodities Ltd | Critical |

**Total Exposure Score: 90 / 100 — Critical** (the single highest-scoring account in the
sample data)

### Classification
- 0–29 = Low · 30–59 = Medium · 60–79 = High · 80–100 = Critical

---

# Business Logic

1. Resolve the funnel account, its source depositors, and its beneficiary.
2. Count the distinct regions the source depositors are drawn from.
3. Count the distinct depositors feeding the account.
4. Compute the longest in-to-out dwell before the funds clear onward.
5. Compute the beneficiary concentration ratio (top beneficiary amount / total outflow).
6. Score each of the four components against its band cut-lines.
7. Aggregate the weighted exposure score; escalate at or above the threshold.

---

# Detection Workflow

```text
Deposit Screening
       ↓
Geographic Dispersion Calculation
       ↓
Inflow Fan-in / Rapid Passthrough Analysis
       ↓
Beneficiary Concentration Assessment
       ↓
Exposure Scoring
       ↓
Investigator Escalation
```

---

# Python Analytics Example

```python
suspect = accounts[
    (accounts["geographic_dispersion_band"].isin(["High", "Critical"])) &
    (accounts["distinct_depositors"] >= 16) &
    (accounts["max_dwell_hours"] <= 24)
]
alerts = suspect[suspect["exposure_score"] >= 80]
```

---

# Investigator Outcome

```text
Account:               Zara Tallowwisp — FUN019
Home Branch:           Meridian Trust Bank - Uptown Branch
Distinct Regions:      9
Distinct Depositors:   33
Total Inflow:           $103,000
Longest Dwell:          3 hours
Total Outflow:          $100,000 → Top Beneficiary: $90,000 (ratio 0.900)
Beneficiary:            Zeta Commodities Ltd (Marshall Islands)
Exposure Score:         90 / 100
Investigation Outcome:  Escalate — geographically-dispersed fan-in collection with rapid
                         passthrough to a concentrated beneficiary
```

---

# Regulatory Relevance

- FATF Recommendations 10 & 13 (customer due diligence and correspondent banking)
- BSA structuring and layering provisions (31 U.S.C. § 5324, 31 CFR § 1010)
- FinCEN funnel-account and money-mule advisories
- Wolfsberg correspondent-banking due-diligence principles

---

# Related Typologies

- BA001 Structuring
- BA003 Mule Accounts
- BA005 Rapid Movement

---

# Strategic Value

BA002 shows how fan-in/fan-out intelligence defeats collection-side layering: by
quantifying the geographic dispersion of depositors, the inflow fan-in, the rapid
passthrough, and the beneficiary concentration step, it surfaces accounts that exist only
to collect and clear — a pattern a single-deposit review would never see. As the second
typology in the fc-06 Correspondent Banking Analytics family, BA002 reuses BA001's file
set, scoring convention, and fc-10 wiring pattern verbatim, confirming the template
replicates cleanly.
