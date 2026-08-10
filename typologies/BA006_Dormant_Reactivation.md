# BA006 – Dormant Reactivation

## Typology Overview

Dormant reactivation is the behavioural-anomaly signal at the far end of the account
lifecycle: an account that has sat idle -- sometimes for months, sometimes for years --
suddenly comes back to life with flows that dwarf anything it ever carried while active.
The finding is not any single transaction on its own; a large deposit or a new
counterparty can each look ordinary in isolation. What makes it a finding is the CONTRAST
between the account's long silence and the size, shape and speed of what happens the
moment it wakes up.

The signature lives in four places: how large the reactivating inflow is relative to what
the account used to carry every month before it went quiet, how long the account sat
dormant before that inflow landed (a longer silence makes the reactivation more
anomalous, not less -- a bank would ordinarily expect a truly dormant account to be
closed, not reawakened at scale), how much the account's behaviour after reactivation
deviates from its prior profile (new counterparties and geographies it never dealt with
before), and how quickly the reactivating funds drain back out again -- a wake-up-and-drain
pattern is a far stronger signal than a wake-up-and-settle one.

---

# Typology Classification

| Attribute | Value |
|------------|------------|
| Typology ID | BA006 |
| Category | Behavioural Anomaly |
| Risk Domain | Correspondent Banking Behavioural Analytics |
| Primary Threat | A long-dormant account reactivated as a conduit for large, fast-moving funds far outside its established profile |
| Detection Type | Dormancy & reactivation-shock analytics |
| Investigation Type | Dormant Reactivation Investigation |
| Risk Level | High |

---

# Typology Description

Dormant reactivation accounts wake up with flows out of step with their own history,
through:

- A reactivating inflow many multiples of the account's pre-dormancy average monthly
  activity -- the account did not gradually ramp back up, it spiked
- Dormancy stretching well beyond a normal quiet period, sometimes a year or more, before
  the reactivating inflow arrives
- Post-reactivation counterparties and geographies the account never transacted with
  during its active history -- the account's profile changes the moment it wakes
- Outbound amounts that closely track the reactivating inflow -- near-total pass-through,
  almost nothing retained once the account is active again
- A counterparty or correspondent bank that recurs across multiple reactivated accounts,
  revealing shared downstream infrastructure behind the reactivations

---

# Typical Routing Structure

```text
Dormancy  (account idle, no activity for an extended period)
       │
       ▼
Reactivating Inflow  (large deposit lands, account wakes up)
       │
       ▼
Reactivated Account  (funds rest only briefly)
       │
       ├──▶ First Reactivation Counterparty  (primary outbound leg, new to the profile)
       │
       └──▶ Second Reactivation Counterparty  (correspondent bank / further hop)
```

---

# FC-03 Network Intelligence Dependencies

| FC-03 Component | Purpose |
|------------|------------|
| ER001 Entity Resolution | Resolve the reactivated account, its prior counterparty, and every reactivation counterparty |
| RD001 Relationship Discovery | Link the account to its pre-dormancy relationship and each reactivation counterparty |
| NS001 Network Risk Scoring | Aggregate reactivation exposure across the account's flows |
| NI012 Behavioural Pattern Network | Dormancy and reactivation-shock signatures |

---

# Key Risk Indicators

## Reactivation Spike Indicators
- A reactivating inflow many multiples of the account's pre-dormancy average monthly
  activity
- No gradual ramp-up -- the account jumps straight to elevated activity

## Dormancy Length Indicators
- Extended idle periods, often exceeding a year, before the reactivating inflow lands
- No account-closure or re-KYC event during the dormant period

## Profile Deviation Indicators
- New counterparties appearing immediately after reactivation with no prior relationship
- New geographies inconsistent with the account's established footprint

## Immediate Outflow Indicators
- Outbound amounts tracking the reactivating inflow almost 1:1
- Round-number consistency between the reactivating inflow and the outbound leg
  inconsistent with genuine reactivated commercial activity

---

# Exposure Scoring Framework

| Risk Category | Weight |
|------------|------------|
| Reactivation Spike | 30% |
| Dormancy Length | 25% |
| Profile Deviation | 25% |
| Immediate Outflow | 20% |

Band-midpoints 15/45/70/90, weighted sum, half-up, boundary at 80.

---

# Example Exposure Score — DR019 Viktor Andreev

| Component | Evidence | Band |
|------------|----------|------|
| Reactivation Spike | $200,000 reactivating inflow against an $8,000 pre-dormancy monthly average (ratio 25.0) | Critical |
| Dormancy Length | Account sat dormant for 730 days (2 years) before reactivating | Critical |
| Profile Deviation | 10 new counterparties/geographies never seen in the prior profile | Critical |
| Immediate Outflow | $190,000 of $200,000 reactivating inflow clears back out (ratio 0.950) | Critical |

**Total Exposure Score: 90 / 100 — Critical** (the single highest-scoring account in the
sample data)

### Classification
- 0–29 = Low · 30–59 = Medium · 60–79 = High · 80–100 = Critical

---

# Business Logic

1. Resolve the account, its pre-dormancy counterparty, and every reactivation
   counterparty (first, second).
2. Compute the reactivation spike ratio (reactivation amount / pre-dormancy average
   monthly activity).
3. Compute the dormancy length in days between the account's last activity and the
   reactivating inflow.
4. Count the new counterparties/geographies appearing after reactivation that were not
   part of the prior profile.
5. Compute the immediate outflow ratio (outflow amount / reactivation amount).
6. Score each of the four components against its band cut-lines.
7. Aggregate the weighted exposure score; escalate at or above the threshold.

---

# Detection Workflow

```text
Dormancy Period Reconstruction
       ↓
Reactivation Spike Calculation
       ↓
Profile Deviation Analysis
       ↓
Immediate Outflow Assessment
       ↓
Exposure Scoring
       ↓
Investigator Escalation
```

---

# Python Analytics Example

```python
suspect = accounts[
    (accounts["dormancy_length_band"].isin(["High", "Critical"])) &
    (accounts["new_counterparty_count"] >= 5) &
    (accounts["reactivation_amount"] / accounts["pre_dormancy_avg_monthly_activity"] >= 8)
]
alerts = suspect[suspect["exposure_score"] >= 80]
```

---

# Investigator Outcome

```text
Account:                  Viktor Andreev — DR019
Home Branch:               Pacific Rim Commercial Bank - Summit Branch
Pre-Dormancy Activity:      $8,000/month average
Reactivating Inflow:        $200,000 (ratio 25.0)
Dormancy Length:            730 days (2 years)
Profile Deviation:          10 new counterparties/geographies
Outflow:                    $190,000 (immediate outflow ratio 0.950)
Prior Counterparty:         Brackenfield Utilities Co
First Reactivation Counterparty: Alpha Trading Ltd
Second Reactivation Counterparty: Continental Correspondent Bank
Exposure Score:             90 / 100
Investigation Outcome:      Escalate — a long-dormant account has reactivated with an
                             inflow far exceeding its pre-dormancy average activity,
                             after sitting idle well beyond a normal cycle, dealing with
                             counterparties and geographies outside its prior profile,
                             and draining back out almost as fast as it arrived
```

---

# Regulatory Relevance

- FATF Recommendations 10 & 13 (customer due diligence and correspondent banking)
- BSA layering and structuring provisions (31 U.S.C. § 5318(h))
- FinCEN advisories on dormant-account reactivation and pass-through activity
- Wolfsberg correspondent-banking due-diligence principles

---

# Related Typologies

- BA003 Mule Accounts
- BA005 Rapid Movement
- BA010 Peer Group Anomalies

---

# Strategic Value

BA006 shows how dormancy and reactivation-shock intelligence defeats the sleeper-account
concealment pattern: by quantifying how large the reactivating inflow is relative to the
account's own pre-dormancy history, how long the account sat idle before waking up, how
much its post-reactivation behaviour deviates from its established profile, and how
closely the outbound leg tracks the reactivating inflow, it surfaces accounts that would
otherwise pass as ordinary reactivated customers on any single transaction. As the sixth
typology in the fc-06 Correspondent Banking Analytics family, BA006 reuses
BA001–BA005's file set, scoring convention, and fc-10 wiring pattern verbatim, and its
Alpha Trading Ltd bridge confirms the estate network keeps absorbing new fc-06 findings
onto entities it already knows.
