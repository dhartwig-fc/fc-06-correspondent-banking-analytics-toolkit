# BA010 – Peer Group Anomalies

## Typology Overview

Most correspondent-banking analytics compare an account against a fixed, absolute
threshold — a dollar cut-line, a transaction count, a ratio. Peer group anomaly
detection compares an account against the STATISTICAL PROFILE OF ITS OWN PEER
SEGMENT instead: accounts of a similar type, size and declared business purpose.
A transaction volume that is unremarkable for a high-turnover corporate current
account can be a strong deviation signal for a retail deposit account, and vice
versa — a fixed threshold misses this, a peer-relative model does not.

The finding lives in how far the account's own transaction volume, turnover
velocity, product/channel usage and counterparty breadth sit from its peer
segment's mean, measured in standard deviations (a z-score), not in the raw
number itself.

---

# Typology Classification

| Attribute | Value |
|------------|------------|
| Typology ID | BA010 |
| Category | Peer Group Anomalies |
| Risk Domain | Correspondent Banking Behavioural Analytics |
| Primary Threat | Behaviour concealed by blending into an absolute-threshold blind spot but standing out against its true peer segment |
| Detection Type | Peer-relative statistical (z-score) analytics |
| Investigation Type | Behavioural Peer-Comparison Investigation |
| Risk Level | High |

---

# Typology Description

Peer group anomaly accounts conceal exposure behind the fact that no single
absolute threshold fits every account type, through:

- Transaction volume running many standard deviations above (or below) the peer
  segment's mean volume
- Turnover velocity inconsistent with how the peer segment typically moves funds
- An atypical product/channel mix — narrower or broader than the peer segment's
  norm — inconsistent with a declared business purpose
- Counterparty breadth (unusually concentrated or unusually wide) that deviates
  from how the peer segment typically transacts

---

# Typical Routing Structure

```text
Peer Segment Reference Accounts  (the statistical baseline: mean + std per metric)
       │
       ▼
Subject Account  (own volume / velocity / product mix / counterparty breadth)   ← collected here
       │
       ▼
Deviation Measurement  (z-score per component against the peer segment)
       │
       ▼
Anomalous Counterparty  (the concentration that drives the deviation)
```

---

# FC-03 Network Intelligence Dependencies

| FC-03 Component | Purpose |
|------------|------------|
| ER001 Entity Resolution | Resolve the subject account, its peer segment and its anomalous counterparties |
| RD001 Relationship Discovery | Link the account to its peer-group reference accounts and anomalous counterparties |
| NS001 Network Risk Scoring | Aggregate deviation exposure across the account's connections |
| NI012 Behavioural Pattern Network | Peer-relative volume/velocity/product/counterparty behaviour |

---

# Key Risk Indicators

## Volume Z-Score Indicators
- Transaction volume running multiple standard deviations above the peer segment mean
- Volume growth with no plausible peer-consistent business explanation

## Velocity Z-Score Indicators
- Turnover velocity (transactions per period) inconsistent with the peer segment's norm
- A rate of fund movement that outpaces the segment's typical pattern

## Product Usage Deviation Indicators
- A product/channel footprint markedly narrower or wider than the peer segment's norm
- Usage inconsistent with the account's declared segment and business purpose

## Counterparty Diversity Z-Score Indicators
- An unusually wide or unusually concentrated counterparty footprint against the peer norm
- A single anomalous counterparty accounting for a peer-inconsistent share of activity

---

# Exposure Scoring Framework

| Risk Category | Weight |
|------------|------------|
| Volume Z-Score | 30% |
| Velocity Z-Score | 25% |
| Product Usage Deviation | 25% |
| Counterparty Diversity Z-Score | 20% |

Band-midpoints 15/45/70/90, weighted sum, half-up, boundary at 80. Every component
is banded on |z|, not on the raw value: |z| < 1 Low, < 2 Medium, < 3 High, otherwise
Critical.

---

# Example Exposure Score — PGA019 Miriam Oduya

| Component | Evidence | Band |
|------------|----------|------|
| Volume Z-Score | $355,000 own volume vs peer mean $250,000, std $25,000 (z = 4.20) | Critical |
| Velocity Z-Score | 27 own velocity vs peer mean 12, std 4 (z = 3.75) | Critical |
| Product Usage Deviation | 13 own product count vs peer mean 6, std 2 (z = 3.50) | Critical |
| Counterparty Diversity Z-Score | 20 own counterparty count vs peer mean 12, std 2 (z = 4.00) | Critical |

**Total Exposure Score: 90 / 100 — Critical** (the single highest-scoring account in
the sample data)

### Classification
- 0–29 = Low · 30–59 = Medium · 60–79 = High · 80–100 = Critical

---

# Business Logic

1. Resolve the subject account and its declared peer segment.
2. Compute the volume z-score (own transaction volume vs the peer segment's mean
   and standard deviation).
3. Compute the velocity z-score (own turnover velocity vs the peer segment's mean
   and standard deviation).
4. Compute the product usage deviation z-score (own product/channel count vs the
   peer segment's mean and standard deviation).
5. Compute the counterparty diversity z-score (own distinct-counterparty count vs
   the peer segment's mean and standard deviation).
6. Score each of the four components against its |z| band cut-lines.
7. Aggregate the weighted exposure score; escalate at or above the threshold.

---

# Detection Workflow

```text
Peer Segment Assignment
       ↓
Volume / Velocity Z-Score Calculation
       ↓
Product Usage / Counterparty Diversity Deviation Analysis
       ↓
Anomalous Counterparty Identification
       ↓
Exposure Scoring
       ↓
Investigator Escalation
```

---

# Python Analytics Example

```python
suspect = accounts[
    (accounts["volume_zscore_band"].isin(["High", "Critical"])) &
    (accounts["velocity_zscore_band"].isin(["High", "Critical"])) &
    (abs(accounts["own_counterparty_count"] - accounts["peer_mean_counterparty_count"])
     / accounts["peer_std_counterparty_count"] >= 2)
]
alerts = suspect[suspect["exposure_score"] >= 80]
```

---

# Investigator Outcome

```text
Account:                Miriam Oduya — PGA019
Home Branch:             Pacific Rim Commercial Bank - Marina Branch
Peer Segment:             Retail Deposit Accounts
Volume:                   $355,000 vs peer mean $250,000, std $25,000 (z = 4.20)
Velocity:                 27 vs peer mean 12, std 4 (z = 3.75)
Product Usage:            13 products vs peer mean 6, std 2 (z = 3.50)
Counterparty Diversity:   20 counterparties vs peer mean 12, std 2 (z = 4.00)
Anomalous Counterparty:   Alpha Trading Ltd
Exposure Score:           90 / 100
Investigation Outcome:    Escalate — the account deviates from its peer segment on
                          every measured dimension, and the deviation concentrates
                          on a single anomalous counterparty already flagged
                          elsewhere in the estate network
```

---

# Regulatory Relevance

- FATF Recommendations 10 & 13 (customer due diligence and correspondent banking)
- BSA suspicious-activity and ongoing-monitoring provisions (31 U.S.C. § 5318(g), 31
  CFR § 1020.320)
- Wolfsberg correspondent-banking due-diligence and transaction-monitoring principles
- Basel Committee guidance on sound management of risks related to money laundering

---

# Related Typologies

- BA001 Structuring
- BA007 Cash Intensive Activity
- BA009 Transaction Laundering

---

# Strategic Value

BA010 shows how peer-relative intelligence defeats an absolute-threshold blind spot:
by quantifying volume, velocity, product usage and counterparty diversity as
deviations from the account's own peer segment rather than against a fixed
cut-line, it surfaces behaviour that would pass unremarked under a one-size-fits-all
threshold but stands out sharply against the segment it actually belongs to. As the
tenth and final typology in the fc-06 Correspondent Banking Analytics family, BA010
reuses BA001's file set, scoring convention, and fc-10 wiring pattern verbatim, and
proves the template extends cleanly even when every component is a statistical
z-score rather than a direct ratio or count. Its top-scoring account, PGA019 (Miriam
Oduya), deviates from its peer segment on every measured dimension, and the anomaly
concentrates on **Alpha Trading Ltd** — the same real-world company already fused
into the estate network by NI001, NI004 and PAT007, and already an fc-06 bridge for
BA003 and BA006 — completing the ten-typology fc-06 build with the family's third
bridge onto that entity.
