# BA008 – Layering

## Typology Overview

Layering is the classic middle stage of money laundering: funds already placed into the
financial system are pushed through a chain of transfers designed to sever the audit trail
from their source before the proceeds are integrated into legitimate-looking assets.
Unlike BA004 Circular Funds Flow (engineered to return to the originator), a layering
chain has no obligation to close a loop — its only job is to put distance, opacity and
jurisdictional friction between the seed account and wherever the funds end up.

The finding lives in four places: how many hops the chain takes before the trail goes
cold, how many of those intermediaries are shells or nominees rather than identifiable
counterparties, how many secrecy or offshore jurisdictions the chain crosses, and how much
the value is split into fragments — and re-merged — along the way to defeat simple
amount-matching.

---

# Typology Classification

| Attribute | Value |
|------------|------------|
| Typology ID | BA008 |
| Category | Layering |
| Risk Domain | Correspondent Banking Behavioural Analytics |
| Primary Threat | Complex transfer chains obscuring the source of funds |
| Detection Type | Chain-depth & opacity analytics |
| Investigation Type | Layering Investigation |
| Risk Level | High |

---

# Typology Description

Layering networks push a seed account's funds through a chain built to obscure their
origin, through:

- Multiple transfer hops between the seed account and the funds' eventual destination,
  each hop adding distance from the original source
- Intermediaries that are shell companies or nominee entities rather than identifiable
  counterparties with an independent commercial rationale
- Cross-border routing through recognised secrecy or offshore jurisdictions, chosen for
  weak beneficial-ownership transparency rather than genuine commercial need
- The seed amount split into multiple fragments and re-merged downstream, defeating
  simple amount-matching across the chain
- A correspondent bank or intermediary that recurs across multiple chains, revealing the
  same infrastructure servicing more than one layering pattern

---

# Typical Routing Structure

```text
Seed Account  (funds originate here)
       │
       ▼
First Intermediary  (opening hop, often a shell/nominee)
       │
       ▼
Second Intermediary  (correspondent bank / further hop)
       │
       ▼
Additional Intermediary Hops  (chain depth, jurisdiction hopping, fragmentation)
       │
       ▼
Destination  (funds land here, source obscured)
```

---

# FC-03 Network Intelligence Dependencies

| FC-03 Component | Purpose |
|------------|------------|
| ER001 Entity Resolution | Resolve the seed account and every intermediary in the chain |
| RD001 Relationship Discovery | Link the seed account to each intermediary hop and the destination |
| NS001 Network Risk Scoring | Aggregate layering exposure across the transfer chain |
| NI012 Behavioural Pattern Network | Chain-depth and jurisdiction-hopping signatures |

---

# Key Risk Indicators

## Chain Depth Indicators
- Multiple transfer hops between the seed account and the funds' eventual destination
- A trail that goes cold well before it reaches an identifiable beneficial owner

## Intermediary Opacity Indicators
- Intermediaries that are shell companies or nominee entities with no independent
  commercial rationale for holding the funds
- Corporate registries that show recently-formed entities with no verifiable trading history

## Jurisdiction Hopping Indicators
- Cross-border routing through recognised secrecy or offshore jurisdictions
- Jurisdiction choices inconsistent with the seed account's declared business geography

## Value Fragmentation Indicators
- The seed amount split into multiple fragments across the chain
- Fragments re-merged downstream in combinations that defeat simple amount-matching

---

# Exposure Scoring Framework

| Risk Category | Weight |
|------------|------------|
| Chain Depth | 30% |
| Intermediary Opacity | 25% |
| Jurisdiction Hopping | 25% |
| Value Fragmentation | 20% |

Band-midpoints 15/45/70/90, weighted sum, half-up, boundary at 80.

---

# Example Exposure Score — LAY019 Katarina Novak

| Component | Evidence | Band |
|------------|----------|------|
| Chain Depth | 9 transfer hops before the trail goes cold | Critical |
| Intermediary Opacity | 8 of 9 intermediaries are shell/nominee entities (ratio 0.889) | Critical |
| Jurisdiction Hopping | 4 hops route through a recognised secrecy/offshore jurisdiction | Critical |
| Value Fragmentation | Seed amount split into 9 fragments along the chain | Critical |

**Total Exposure Score: 90 / 100 — Critical** (the single highest-scoring account in the
sample data)

### Classification
- 0–29 = Low · 30–59 = Medium · 60–79 = High · 80–100 = Critical

---

# Business Logic

1. Resolve the seed account and every intermediary in the chain (first hop, second hop,
   destination).
2. Count the transfer hops (chain depth) the funds pass through before the trail goes cold.
3. Compute the intermediary opacity ratio (opaque/shell intermediaries / total
   intermediaries).
4. Count the hops that route through a recognised secrecy/offshore jurisdiction.
5. Count the fragments the seed amount is split into along the chain.
6. Score each of the four components against its band cut-lines.
7. Aggregate the weighted exposure score; escalate at or above the threshold.

---

# Detection Workflow

```text
Transfer-Chain Reconstruction
       ↓
Chain Depth Calculation
       ↓
Intermediary Opacity & Jurisdiction Hopping Analysis
       ↓
Value Fragmentation Assessment
       ↓
Exposure Scoring
       ↓
Investigator Escalation
```

---

# Python Analytics Example

```python
suspect = accounts[
    (accounts["intermediary_opacity_band"].isin(["High", "Critical"])) &
    (accounts["chain_depth"] >= 5) &
    (accounts["secrecy_jurisdiction_hops"] >= 2)
]
alerts = suspect[suspect["exposure_score"] >= 80]
```

---

# Investigator Outcome

```text
Account:                Katarina Novak — LAY019
Home Branch:             Adriatic Union Bank - Old Town Branch
Chain Depth:              9 transfer hops
Intermediary Opacity:     8 of 9 intermediaries opaque (ratio 0.889)
Jurisdiction Hopping:     4 secrecy/offshore hops
Value Fragmentation:      9 fragments
First Intermediary:       Gamma Imports Ltd
Second Intermediary:      Continental Correspondent Bank
Destination:              Solano Exchange House
Exposure Score:           90 / 100
Investigation Outcome:  Escalate — funds pushed through a deep, opaque, cross-border
                         transfer chain designed to sever the audit trail from the seed
                         account
```

---

# Regulatory Relevance

- FATF Recommendations 10 & 13 (customer due diligence and correspondent banking)
- BSA layering and structuring provisions (31 U.S.C. § 5318(h))
- FinCEN advisories on layering, shell companies and secrecy-jurisdiction routing
- Wolfsberg correspondent-banking due-diligence principles

---

# Related Typologies

- BA004 Circular Funds Flow
- BA003 Mule Accounts
- BA009 Transaction Laundering

---

# Strategic Value

BA008 shows how chain-depth and opacity intelligence defeats layering concealment: by
quantifying how many hops disguise the trail, how many intermediaries are shells rather
than identifiable counterparties, how many secrecy-jurisdiction hops the chain crosses,
and how the seed amount is fragmented and re-merged along the way, it surfaces transfer
chains that would otherwise pass as ordinary correspondent-banking activity on each
individual leg. As the eighth typology in the fc-06 Correspondent Banking Analytics
family, BA008 reuses BA001–BA007's file set, scoring convention, and fc-10 wiring pattern
verbatim, and its Gamma Imports Ltd / Continental Correspondent Bank bridge confirms the
estate network keeps absorbing new fc-06 findings onto entities and infrastructure it
already knows.
