# Network Investigation Guide

## Purpose

This guide defines the standard investigation methodology for the Financial Crime Network Intelligence Library.

Network Intelligence provides a reusable analytical capability used across multiple Financial Crime domains including:

- Trade-Based Money Laundering (TBML)
- Sanctions Exposure
- Correspondent Banking
- Transaction Monitoring
- Fraud Detection
- Capital Markets Surveillance

The objective is to identify hidden relationships, ownership structures, control mechanisms and connected-party risks that may not be visible through traditional customer or transaction reviews.

This guide serves as the operational standard for all Network Intelligence patterns.

---

# Network Intelligence Investigation Framework

```text
Source Data
    ↓

Entity Resolution
    ↓

Relationship Discovery
    ↓

Ownership & Control Analysis
    ↓

Network Pattern Detection
    ↓

Network Risk Assessment
    ↓

Domain Investigation Support
    ↓

Investigator Outcome
```

---

# Role of Network Intelligence

Network Intelligence is not normally an independent alerting function.

Instead, it enriches operational investigations by providing relationship-based risk indicators.

```text
Network Intelligence
        │
        ├── TBML Analytics
        ├── Sanctions Analytics
        ├── Correspondent Banking Analytics
        ├── Transaction Monitoring Analytics
        └── Fraud Analytics
```

Network findings should be considered supporting evidence rather than standalone conclusions.

---

# 1. Source Data Review

## Objective

Identify the datasets required to construct an accurate network view.

## Common Data Sources

| Source | Purpose |
|----------|----------|
| Customer KYC | Customer identity information |
| Counterparty Records | External relationship identification |
| Corporate Registry | Directors and shareholder data |
| Beneficial Ownership Data | Ownership structures |
| Address Data | Shared location indicators |
| Contact Data | Shared communications indicators |
| Trade Data | Commercial relationship analysis |
| Transaction Data | Financial activity analysis |
| Sanctions Data | Exposure assessment |
| Adverse Media | External risk intelligence |

## Investigator Questions

- Is sufficient data available?
- Are records complete?
- Are identifiers reliable?
- Is data quality acceptable?

### Output

- Data inventory
- Data quality assessment
- Investigation scope

---

# 2. Entity Resolution

## Objective

Resolve fragmented records into a single view of each real-world entity.

## Resolution Targets

| Entity Type |
|-------------|
| Person |
| Company |
| Beneficial Owner |
| Director |
| Vessel |
| Address |
| Account |
| Counterparty |

## Resolution Techniques

- Exact match
- Fuzzy match
- Identifier match
- Address standardisation
- Name normalisation
- Registration number matching
- Multi-attribute scoring

## Investigator Questions

- Are duplicates present?
- Is the same entity represented multiple times?
- Can confidence be increased through additional evidence?

### Output

- Resolved entities
- Match confidence scores
- Entity evidence pack

---

# 3. Relationship Discovery

## Objective

Identify meaningful relationships between entities.

## Relationship Categories

| Relationship | Example |
|-------------|---------|
| Owns | Shareholder relationship |
| Controls | Beneficial ownership |
| Directs | Common director |
| Shares Address | Registered office |
| Shares Contact | Email or phone |
| Trades With | Commercial relationship |
| Transacts With | Financial relationship |
| Manages | Operational control |
| Linked To | Risk association |

## Investigator Questions

- What relationship exists?
- Is it direct or indirect?
- How strong is the evidence?
- Is the relationship material?

### Output

- Relationship graph
- Supporting evidence
- Link confidence scores

---

# 4. Ownership and Control Analysis

## Objective

Determine ultimate ownership and control.

## Review Areas

- Direct ownership
- Indirect ownership
- Beneficial ownership
- Nominee ownership
- Director influence
- Ownership chains
- Complex structures
- Hidden controllers

## Risk Indicators

- Shared beneficial owner
- Shared director
- Nominee shareholder
- Offshore ownership
- Circular ownership
- Shell company involvement

## Investigator Questions

- Who ultimately controls the entity?
- Are ownership layers concealing control?
- Is ownership unusually complex?

### Output

- Ownership structure
- Control assessment
- Ownership risk indicators

---

# 5. Network Pattern Detection

## Objective

Apply standard Network Intelligence patterns.

## Pattern Library

| Pattern ID | Pattern |
|------------|---------|
| NI001 | Shared Director |
| NI002 | Shared Beneficial Owner |
| NI003 | Shared Address |
| NI004 | Shared Contact Information |
| NI005 | Circular Ownership |
| NI006 | Common Intermediary |
| NI007 | Shell Company Cluster |
| NI008 | Sanctions Proximity |
| NI009 | Trade Counterparty Network |
| NI010 | Payment Network Cluster |

## Investigator Questions

- Which pattern is present?
- Is the pattern explainable?
- Does the pattern increase risk?

### Output

- Pattern identification
- Supporting rationale
- Pattern risk assessment

---

# 6. Network Risk Assessment

## Objective

Assess the significance of the identified network.

## Risk Factors

| Factor | Description |
|----------|-------------|
| Relationship Strength | Evidence supporting link |
| Relationship Type | Ownership vs contact data |
| Proximity to Risk Entity | Number of hops |
| Jurisdiction Risk | Geographic exposure |
| Behavioural Risk | Activity concerns |
| Pattern Frequency | Repeated behaviour |
| Data Confidence | Quality of evidence |

## Risk Ratings

| Score | Rating |
|---------|---------|
| 0-30 | Low |
| 31-60 | Medium |
| 61-80 | High |
| 81-100 | Critical |

### Output

- Network Risk Score
- Risk rationale
- Escalation recommendation

---

# 7. Domain Investigation Support

## Objective

Translate network findings into operational investigation value.

### TBML Example

```text
TBML001 Over Invoicing
        ↓
NI002 Shared Beneficial Owner
        ↓
Potential Related-Party Trading
```

### Sanctions Example

```text
SAN002 Shadow Fleet
        ↓
NI008 Sanctions Proximity
        ↓
Indirect Sanctions Exposure
```

### Correspondent Banking Example

```text
Nested Banking Relationship
        ↓
NI006 Common Intermediary
        ↓
Hidden Counterparty Exposure
```

### Output

- Investigation enrichment
- Supporting evidence
- Escalation rationale

---

# 8. Investigator Outcome

## Possible Outcomes

| Outcome | Description |
|----------|-------------|
| No Material Finding | Relationship not significant |
| Additional Information Required | More evidence needed |
| Risk Confirmed | Relationship materially increases risk |
| Escalate Investigation | Enhanced review required |
| SAR Consideration | Suspicious activity indicators identified |
| Scenario Feedback | Used for model improvement |

---

# Standard Investigator Summary

```text
Network analysis identified a relationship between Entity A and Entity B.

The relationship is supported by ownership, directorship, transactional or operational evidence.

The relationship increases risk because it indicates hidden control, connected-party activity, sanctions exposure or other financial crime concerns.

The network risk has been assessed as [Low / Medium / High / Critical].

Recommended action:
Close / Monitor / Request Information / Escalate.
```

---

# Governance Principles

Network Intelligence findings should always be reviewed alongside:

- Customer risk profile
- Counterparty risk profile
- Transaction activity
- Trade activity
- Sanctions screening
- Adverse media
- Domain-specific typology indicators

Network Intelligence provides relationship evidence and risk context but should not be treated as standalone proof of financial crime.

---

# Related Pattern Files

- NI001_Shared_Director.md
- NI002_Shared_Beneficial_Owner.md
- NI003_Shared_Address.md
- NI004_Shared_Contact_Information.md
- NI005_Circular_Ownership.md
- NI006_Common_Intermediary.md
- NI007_Shell_Company_Cluster.md
- NI008_Sanctions_Proximity.md
- NI009_Trade_Counterparty_Network.md
- NI010_Payment_Network_Cluster.md
