# BA004 – Circular Funds Flow

## Typology Overview

A circular funds flow is a round-tripping loop: funds leave an originating account, pass
through one or more intermediary accounts, and return to the same origin (or an account
under the same control) having taken on the appearance of unrelated third-party activity
along the way. It is BA003 Mule Accounts run backwards — where a mule forwards funds
onward and never sees them again, a circular flow is engineered so the ORIGINATOR gets the
funds back, laundered through the round trip itself.

The finding lives in four places: how much of what left the origin actually comes back to
it, how many hops the loop takes to disguise the trip, how little value is lost along the
way (ordinary correspondent banking bleeds fees and FX spread at every hop; a loop that
returns almost lossless is not behaving like trade finance), and how quickly the whole
round trip completes.

---

# Typology Classification

| Attribute | Value |
|------------|------------|
| Typology ID | BA004 |
| Category | Round-Tripping |
| Risk Domain | Correspondent Banking Behavioural Analytics |
| Primary Threat | Round-tripped funds disguised as unrelated third-party activity |
| Detection Type | Loop-closure & value-preservation analytics |
| Investigation Type | Circular Funds Flow Investigation |
| Risk Level | High |

---

# Typology Description

Circular funds flow networks route an account's own money back to itself through a
disguising chain of intermediaries, through:

- Outbound funds returning to the origin account almost 1:1, closing the loop
- Multiple intermediary accounts carrying the funds between origin and return, each hop
  adding distance from the original source
- Near-lossless value retention hop to hop — real trade finance and correspondent banking
  bleed fees and FX spread; a loop that loses almost nothing is not ordinary business
- The whole round trip completing in hours or days rather than the weeks a genuine
  multi-party trade chain would take
- A closure account or correspondent bank that recurs across multiple loops, revealing
  the same infrastructure servicing more than one round trip

---

# Typical Routing Structure

```text
Originating Account  (funds leave here)
       │
       ▼
First Loop Member  (first intermediary hop)
       │
       ▼
Second Loop Member  (correspondent bank / further hop)
       │
       ▼
Closure Account  (final hop before the loop closes)
       │
       ▼
Originating Account  (funds return -- the loop closes)
```

---

# FC-03 Network Intelligence Dependencies

| FC-03 Component | Purpose |
|------------|------------|
| ER001 Entity Resolution | Resolve the originating account and every loop member |
| RD001 Relationship Discovery | Link the origin to each intermediary and the closure account |
| NS001 Network Risk Scoring | Aggregate circular-flow exposure across the loop |
| NI012 Behavioural Pattern Network | Loop-closure and timing-compression signatures |

---

# Key Risk Indicators

## Loop Closure Indicators
- Funds returning to the origin account within the same reporting cycle they left it
- Balance movements that net to near-zero over the round trip despite large gross flows

## Hop Count Indicators
- Multiple intermediary accounts carrying the funds between origin and return
- Intermediaries with no independent commercial rationale for holding the funds

## Value Preservation Indicators
- Amounts moving hop to hop with negligible fee or FX erosion
- Round-number consistency across legs inconsistent with genuine trade settlement

## Timing Compression Indicators
- The full round trip completing in hours or a few days
- Legs scheduled back-to-back rather than at a pace consistent with real commercial timing

---

# Exposure Scoring Framework

| Risk Category | Weight |
|------------|------------|
| Loop Closure | 35% |
| Hop Count | 25% |
| Value Preservation | 20% |
| Timing Compression | 20% |

Band-midpoints 15/45/70/90, weighted sum, half-up, boundary at 80.

---

# Example Exposure Score — CYC019 Piotr Kettlecrumb

| Component | Evidence | Band |
|------------|----------|------|
| Loop Closure | $97,000 of $100,000 originated returns to origin (ratio 0.970) | Critical |
| Hop Count | 8 intermediary accounts before the loop closes | Critical |
| Value Preservation | 98.5% of value retained hop to hop across the loop | Critical |
| Timing Compression | Round trip completes in 8 hours | Critical |

**Total Exposure Score: 90 / 100 — Critical** (the single highest-scoring account in the
sample data)

### Classification
- 0–29 = Low · 30–59 = Medium · 60–79 = High · 80–100 = Critical

---

# Business Logic

1. Resolve the originating account and every loop member (first hop, second hop, closure).
2. Compute the loop closure ratio (returned amount / originated amount).
3. Count the intermediary accounts (hops) the loop passes through before closing.
4. Compute the average hop retention percentage (value preserved hop to hop).
5. Compute the loop duration in hours from origination to return.
6. Score each of the four components against its band cut-lines.
7. Aggregate the weighted exposure score; escalate at or above the threshold.

---

# Detection Workflow

```text
Origin/Return Reconciliation
       ↓
Loop Closure Ratio Calculation
       ↓
Hop Count & Value Preservation Analysis
       ↓
Timing Compression Assessment
       ↓
Exposure Scoring
       ↓
Investigator Escalation
```

---

# Python Analytics Example

```python
suspect = accounts[
    (accounts["loop_closure_band"].isin(["High", "Critical"])) &
    (accounts["hop_count"] >= 5) &
    (accounts["loop_duration_hours"] <= 48)
]
alerts = suspect[suspect["exposure_score"] >= 80]
```

---

# Investigator Outcome

```text
Account:               Piotr Kettlecrumb — CYC019
Home Branch:           Pacific Rim Commercial Bank - Summit Branch
Originated Amount:     $100,000
Returned Amount:       $97,000 (loop closure ratio 0.970)
Hop Count:              8 intermediary accounts
Value Retained:         98.5% hop to hop
Loop Duration:          8 hours
First Loop Member:      Gammavane Imports Ltd
Second Loop Member:     Continental Correspondent Bank
Closure Member:         Thornwick Holdings
Exposure Score:         90 / 100
Investigation Outcome:  Escalate — funds round-trip back to the origin account through a
                         disguising multi-hop chain with near-lossless value retention
```

---

# Regulatory Relevance

- FATF Recommendations 10 & 13 (customer due diligence and correspondent banking)
- BSA layering and structuring provisions (31 U.S.C. § 5318(h))
- FinCEN advisories on round-tripping and trade-based value transfer
- Wolfsberg correspondent-banking due-diligence principles

---

# Related Typologies

- BA003 Mule Accounts
- BA005 Rapid Movement
- BA008 Layering

---

# Strategic Value

BA004 shows how loop-closure and value-preservation intelligence defeats round-tripping
concealment: by quantifying how much of what left an account comes back to it, how many
hops disguise the trip, how little value is lost along the way, and how quickly the whole
round trip completes, it surfaces accounts that would otherwise pass as ordinary
correspondent-banking counterparties on each individual leg. As the fourth typology in the
fc-06 Correspondent Banking Analytics family, BA004 reuses BA001/BA002/BA003's file set,
scoring convention, and fc-10 wiring pattern verbatim, and its Gammavane Imports Ltd bridge
confirms the estate network keeps absorbing new fc-06 findings onto entities it already
knows.
