# BA005 – Rapid Movement

## Typology Overview

Rapid movement is the velocity / layering signal at the heart of correspondent-banking
monitoring: funds land on an account and clear back out again almost immediately, resting
only long enough to register a balance change before they are gone. It is not defined by
who sent the money or where it ends up — those can look entirely ordinary on any single
leg — it is defined by HOW FAST the funds move and HOW MUCH volume passes through an
account relative to what it normally holds.

The finding lives in four places: how briefly the funds dwell on the account before
clearing onward, how large the turnover is relative to the account's own balance (an
account that turns over many multiples of its balance every cycle is not behaving like an
ordinary deposit account), how widely the outbound leg disperses across multiple onward
destinations rather than settling with one counterparty, and how closely the outbound
amount tracks the inbound amount — near-total pass-through with almost nothing retained.

---

# Typology Classification

| Attribute | Value |
|------------|------------|
| Typology ID | BA005 |
| Category | Velocity / Layering |
| Risk Domain | Correspondent Banking Behavioural Analytics |
| Primary Threat | Funds moved through an account too fast and too disproportionately to its balance to be genuine banking activity |
| Detection Type | Dwell-time & velocity analytics |
| Investigation Type | Rapid Movement Investigation |
| Risk Level | High |

---

# Typology Description

Rapid movement accounts pass funds through with almost no friction, through:

- Inbound funds clearing back out again within hours, sometimes minutes, of arrival
- Turnover many multiples of the account's own average balance — the account is a
  conduit, not a store of value
- The outbound leg splitting across multiple onward destinations rather than settling
  with a single counterparty, dispersing the funds' onward path
- Outbound amounts that closely track inbound amounts — near-total pass-through, almost
  nothing retained on the account
- A correspondent bank or onward destination that recurs across multiple rapid-movement
  accounts, revealing shared downstream infrastructure

---

# Typical Routing Structure

```text
Source  (funds arrive here)
       │
       ▼
Rapid Movement Account  (funds rest briefly)
       │
       ├──▶ First Onward Destination  (primary outbound leg)
       │
       └──▶ Second Onward Destination  (correspondent bank / further hop)
```

---

# FC-03 Network Intelligence Dependencies

| FC-03 Component | Purpose |
|------------|------------|
| ER001 Entity Resolution | Resolve the rapid movement account, its source and every onward destination |
| RD001 Relationship Discovery | Link the account to its source and each onward destination |
| NS001 Network Risk Scoring | Aggregate velocity exposure across the account's flows |
| NI012 Behavioural Pattern Network | Dwell-time and dispersion signatures |

---

# Key Risk Indicators

## Dwell Time Indicators
- Inbound funds clearing back out within hours of arrival
- Balance spikes that resolve to near-baseline within the same reporting cycle

## Velocity Indicators
- Turnover many multiples of the account's own average balance
- Throughput inconsistent with the account's declared purpose or segment

## Onward Dispersion Indicators
- Outbound funds splitting across several distinct onward destinations
- Destinations with no independent commercial rationale for receiving the funds

## Value Match Indicators
- Outbound amounts tracking inbound amounts almost 1:1
- Round-number consistency between inbound and outbound legs inconsistent with genuine
  fee-bearing commercial settlement

---

# Exposure Scoring Framework

| Risk Category | Weight |
|------------|------------|
| Dwell Time | 35% |
| Velocity | 25% |
| Onward Dispersion | 20% |
| Value Match | 20% |

Band-midpoints 15/45/70/90, weighted sum, half-up, boundary at 80.

---

# Example Exposure Score — RM019 Dmitri Petrov

| Component | Evidence | Band |
|------------|----------|------|
| Dwell Time | Funds clear in 1 hour before moving onward | Critical |
| Velocity | $300,000 turnover against a $10,000 average balance (ratio 30.0) | Critical |
| Onward Dispersion | Outbound leg spreads across 9 distinct destinations | Critical |
| Value Match | $98,000 of $100,000 inbound clears back out (ratio 0.980) | Critical |

**Total Exposure Score: 90 / 100 — Critical** (the single highest-scoring account in the
sample data)

### Classification
- 0–29 = Low · 30–59 = Medium · 60–79 = High · 80–100 = Critical

---

# Business Logic

1. Resolve the account, its source, and every onward destination (first, second).
2. Compute the dwell time from inbound clearing to outbound clearing.
3. Compute the velocity ratio (total turnover amount / average balance).
4. Count the distinct onward destinations the outbound leg disperses across.
5. Compute the value match ratio (outbound amount / inbound amount).
6. Score each of the four components against its band cut-lines.
7. Aggregate the weighted exposure score; escalate at or above the threshold.

---

# Detection Workflow

```text
Inbound/Outbound Reconciliation
       ↓
Dwell Time Calculation
       ↓
Velocity & Onward Dispersion Analysis
       ↓
Value Match Assessment
       ↓
Exposure Scoring
       ↓
Investigator Escalation
```

---

# Python Analytics Example

```python
suspect = accounts[
    (accounts["dwell_time_band"].isin(["High", "Critical"])) &
    (accounts["distinct_destination_count"] >= 5) &
    (accounts["total_turnover_amount"] / accounts["avg_balance"] >= 8)
]
alerts = suspect[suspect["exposure_score"] >= 80]
```

---

# Investigator Outcome

```text
Account:                 Dmitri Petrov — RM019
Home Branch:              Pacific Rim Commercial Bank - Summit Branch
Inbound Amount:           $100,000
Outbound Amount:          $98,000 (value match ratio 0.980)
Dwell Time:                1 hour
Velocity:                  $300,000 turnover / $10,000 balance (ratio 30.0)
Onward Dispersion:         9 distinct destinations
Source:                    Kestrel Cash & Carry Ltd
First Onward Destination:  Zeta Commodities Ltd
Second Onward Destination: Continental Correspondent Bank
Exposure Score:            90 / 100
Investigation Outcome:     Escalate — funds clear through the account almost
                            immediately, at a velocity far exceeding its own balance,
                            dispersing across multiple onward destinations with the
                            outbound amount tracking the inbound amount near 1:1
```

---

# Regulatory Relevance

- FATF Recommendations 10 & 13 (customer due diligence and correspondent banking)
- BSA layering and structuring provisions (31 U.S.C. § 5318(h))
- FinCEN advisories on rapid-movement / pass-through account activity
- Wolfsberg correspondent-banking due-diligence principles

---

# Related Typologies

- BA002 Funnel Accounts
- BA004 Circular Funds Flow
- BA008 Layering

---

# Strategic Value

BA005 shows how dwell-time and velocity intelligence defeats rapid-movement concealment:
by quantifying how briefly funds rest on an account before clearing onward, how large the
turnover is relative to the account's own balance, how widely the outbound leg disperses
across onward destinations, and how closely the outbound amount tracks the inbound amount,
it surfaces accounts that would otherwise pass as ordinary correspondent-banking
counterparties on each individual leg. As the fifth typology in the fc-06 Correspondent
Banking Analytics family, BA005 reuses BA001/BA002/BA003/BA004's file set, scoring
convention, and fc-10 wiring pattern verbatim, and its Zeta Commodities Ltd bridge confirms
the estate network keeps absorbing new fc-06 findings onto entities it already knows.
