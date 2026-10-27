# BA007 – Cash Intensive Activity

## Typology Overview

A cash-intensive business is a legitimate cover for laundering physical cash: cash &
carry wholesalers, currency exchange houses, laundromats, and similar operators that
plausibly handle real cash every day. The tell is not the presence of cash — it is cash
disproportionate to the business's own declared profile, layered with the tells that
separate genuine trade volume from placement.

The finding lives in how far the cash ratio runs above the business's own peer-segment
norm, how far the cash actually deposited exceeds the volume the business declared when
the account was profiled, how suspiciously even the deposit rhythm is (real retail cash
is noisy; fabricated cash is not), and how much of the deposited cash did not originate
with the business itself.

---

# Typology Classification

| Attribute | Value |
|------------|------------|
| Typology ID | BA007 |
| Category | Cash Intensity |
| Risk Domain | Correspondent Banking Behavioural Analytics |
| Primary Threat | Cash placement disguised as legitimate business turnover |
| Detection Type | Cash-ratio & profile-deviation analytics |
| Investigation Type | Cash Intensive Business Investigation |
| Risk Level | High |

---

# Typology Description

Cash-intensive business accounts conceal placement behind a plausible cash-handling
cover, through:

- Cash deposits running far above the business's own peer-segment cash norm
- Cash actually deposited exceeding the volume the business declared for KYC
- A deposit rhythm that is unnaturally even — no business's daily cash is that smooth
- Third-party funds mixed into what should be the business's own till

---

# Typical Routing Structure

```text
Depositors / Linked Entities  (third-party funds, affiliated suppliers)
       │
       ▼
Cash Deposits  (disproportionate to declared turnover)          ← collected here
       │
       ▼
Cash Intensive Business Account  (cash & carry, exchange house, etc.)
       │
       ▼
Profile Excess / Regularity  (exceeds declared volume, unnaturally even)
       │
       ▼
Commingled Funds  (third-party cash mixed with the business's own)
```

---

# FC-03 Network Intelligence Dependencies

| FC-03 Component | Purpose |
|------------|------------|
| ER001 Entity Resolution | Resolve the business account, its linked entities and depositors |
| RD001 Relationship Discovery | Link the account to its depositors and linked entities |
| NS001 Network Risk Scoring | Aggregate cash-intensity exposure across the account's connections |
| NI012 Behavioural Pattern Network | Cash-ratio and deposit-rhythm behaviour |

---

# Key Risk Indicators

## Cash Ratio Indicators
- Cash share of turnover running multiples of the business's own peer-segment norm
- Cash-to-turnover ratio inconsistent with the declared business type

## Profile Excess Indicators
- Actual cash deposited materially exceeding the volume declared at KYC onboarding
- No plausible business explanation for the growth in cash handled

## Deposit Regularity Indicators
- Deposits landing with an unnaturally even size and cadence
- Coefficient of variation far below what a genuine retail cash business exhibits

## Commingling Indicators
- Deposited cash traceable to unrelated third parties, not the business's own sales
- Linked entities or depositors with no plausible commercial relationship to the account

---

# Exposure Scoring Framework

| Risk Category | Weight |
|------------|------------|
| Cash Ratio | 35% |
| Profile Excess | 25% |
| Deposit Regularity | 20% |
| Commingling | 20% |

Band-midpoints 15/45/70/90, weighted sum, half-up, boundary at 80.

---

# Example Exposure Score — CIA019 Gammavane Imports Ltd

| Component | Evidence | Band |
|------------|----------|------|
| Cash Ratio | $760,000 cash of $820,000 turnover, 3.09x the 30% peer-segment norm | Critical |
| Profile Excess | $760,000 deposited vs $300,000 declared annual cash volume (ratio 2.53) | Critical |
| Deposit Regularity | Deposit coefficient of variation: 8% — unnaturally even | Critical |
| Commingling | $250,000 of $760,000 deposited cash from unrelated third parties (ratio 0.329) | Critical |

**Total Exposure Score: 90 / 100 — Critical** (the single highest-scoring account in the
sample data)

### Classification
- 0–29 = Low · 30–59 = Medium · 60–79 = High · 80–100 = Critical

---

# Business Logic

1. Resolve the business account, its declared peer segment, and its linked entities.
2. Compute the cash ratio (cash deposits / turnover) and scale it against the peer norm.
3. Compute the profile excess ratio (cash deposited / declared annual cash volume).
4. Compute the deposit coefficient of variation across individual deposit sizes.
5. Compute the commingling ratio (third-party deposits / total deposits).
6. Score each of the four components against its band cut-lines.
7. Aggregate the weighted exposure score; escalate at or above the threshold.

---

# Detection Workflow

```text
Cash Deposit Screening
       ↓
Cash Ratio Calculation (vs peer norm)
       ↓
Profile Excess / Deposit Regularity Analysis
       ↓
Commingling Assessment
       ↓
Exposure Scoring
       ↓
Investigator Escalation
```

---

# Python Analytics Example

```python
suspect = accounts[
    (accounts["cash_ratio_band"].isin(["High", "Critical"])) &
    (accounts["deposit_cv_pct"] <= 20) &
    (accounts["third_party_deposit_amount"] / accounts["total_deposit_amount"] >= 0.15)
]
alerts = suspect[suspect["exposure_score"] >= 80]
```

---

# Investigator Outcome

```text
Account:               Gammavane Imports Ltd — CIA019
Home Branch:           Continental Correspondent Bank - Harbor Branch
Cash Deposits:          $760,000 of $820,000 turnover (peer norm 30%)
Declared Cash Volume:   $300,000
Deposit CV:             8% (unnaturally even)
Third-Party Deposits:   $250,000 of $760,000 (ratio 0.329)
Linked Entity:          Silverlake Provisioning Ltd (Marshall Islands)
Exposure Score:         90 / 100
Investigation Outcome:  Escalate — cash disproportionate to declared business profile,
                         unnaturally even deposit rhythm, third-party funds commingled in
```

---

# Regulatory Relevance

- FATF Recommendations 10 & 13 (customer due diligence and correspondent banking)
- BSA structuring and cash-intensive business provisions (31 U.S.C. § 5324, 31 CFR § 1010)
- FinCEN cash-intensive business and money services business advisories
- Wolfsberg correspondent-banking due-diligence principles

---

# Related Typologies

- BA001 Structuring
- BA003 Mule Accounts
- BA006 Dormant Reactivation

---

# Strategic Value

BA007 shows how excess-over-profile intelligence defeats cash placement disguised as
legitimate turnover: by quantifying the cash ratio against the business's own peer
norm, the profile excess against its declared cash volume, the deposit regularity, and
the commingling of third-party funds, it surfaces cash-intensive businesses that would
otherwise pass as ordinary retail cash handling. BA007 is the estate's designated
subject-as-bridge typology: unlike BA001–BA006, where the bridge entity is a connected
counterparty, BA007's top-scoring account IS Gammavane Imports Ltd itself, showing its own
cash-intensive behaviour fusing with its sanctions/network flags. As the seventh
typology in the fc-06 Correspondent Banking Analytics family, BA007 reuses BA001's file
set, scoring convention, and fc-10 wiring pattern verbatim, confirming the template
replicates cleanly even when the bridge shape differs.
