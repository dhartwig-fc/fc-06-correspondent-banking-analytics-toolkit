# BA003 – Mule Accounts

## Typology Overview

A mule account is a personal account used purely as a pass-through point: it receives
illicit funds from one or more originators and forwards them onward almost immediately,
retaining little or nothing for itself. It is the personal-account mirror of BA002 Funnel
Accounts — where funnelling hides behind volume and dispersion on the collection side,
muling hides behind an individual's identity and a thin personal-banking profile, moving
money at a controller's instruction rather than the account holder's own initiative.

The finding lives in four places: how closely outbound funds track inbound funds (near-zero
retention), how recently the account was opened relative to when the illicit flows begin,
how far the account's throughput departs from the holder's declared income or profile, and
whether the account shares a device or downstream beneficiary with other accounts already
known to be mules.

---

# Typology Classification

| Attribute | Value |
|------------|------------|
| Typology ID | BA003 |
| Category | Mule Activity |
| Risk Domain | Correspondent Banking Behavioural Analytics |
| Primary Threat | Personal-account pass-through of illicit funds under third-party control |
| Detection Type | Pass-through ratio & behavioural-profile analytics |
| Investigation Type | Mule Account Investigation |
| Risk Level | High |

---

# Typology Description

Mule account networks recruit or coerce individuals to open or hand over personal accounts,
then route illicit funds through them, through:

- Outbound funds tracking inbound funds almost 1:1, with near-zero balance retained
- Accounts opened shortly before the illicit flows begin — too young to have a real
  transaction history
- Monthly throughput far exceeding the account holder's declared income or stated profile
- Shared devices, IP addresses or downstream beneficiaries linking the account to other
  accounts already identified as mules
- A controller directing the timing and destination of outbound transfers, distinct from
  the account holder

---

# Typical Routing Structure

```text
Originators  (multiple, unrelated senders)
       │
       ▼
Mule Account  (thin personal-banking profile, newly opened)
       │
       ▼
Pass-through  (out approx in, near-zero retained)
       │
       ▼
Controller Instruction  (directs timing & destination)
       │
       ▼
Forwarding Destination  (the ultimate downstream recipient)
```

---

# FC-03 Network Intelligence Dependencies

| FC-03 Component | Purpose |
|------------|------------|
| ER001 Entity Resolution | Resolve the mule account, its originators, controller and forwarding destination |
| RD001 Relationship Discovery | Link the account to its originators, controller and forwarding destination |
| NS001 Network Risk Scoring | Aggregate mule exposure across the account's connections |
| NI012 Behavioural Pattern Network | Pass-through and behavioural-mismatch signatures |

---

# Key Risk Indicators

## Pass-through Ratio Indicators
- Outbound transfers landing within hours or days of the matching inbound funds
- Balance held on the account never accumulating despite regular large inflows

## Account Youth Indicators
- Account opened in the weeks immediately before illicit flows begin
- No prior transaction history consistent with genuine personal banking

## Behavioural Mismatch Indicators
- Monthly throughput many multiples of the declared salary or stated income
- Transaction profile inconsistent with the account holder's declared occupation

## Network Linkage Indicators
- Shared device or IP address with other accounts already flagged as mules
- Shared downstream beneficiary or forwarding destination across multiple accounts
- A controller instructing multiple, apparently unrelated account holders

---

# Exposure Scoring Framework

| Risk Category | Weight |
|------------|------------|
| Pass-through Ratio | 30% |
| Account Youth | 25% |
| Behavioural Mismatch | 25% |
| Network Linkage | 20% |

Band-midpoints 15/45/70/90, weighted sum, half-up, boundary at 80.

---

# Example Exposure Score — MUL019 Rosalind Fairweather

| Component | Evidence | Band |
|------------|----------|------|
| Pass-through Ratio | $96,000 of $100,000 inbound forwarded onward (ratio 0.960) | Critical |
| Account Youth | Account opened 12 days before the flows began | Critical |
| Behavioural Mismatch | $92,000 monthly throughput vs $3,200 declared income (ratio 28.75) | Critical |
| Network Linkage | 6 shared device/beneficiary links to other known mule accounts | Critical |

**Total Exposure Score: 90 / 100 — Critical** (the single highest-scoring account in the
sample data)

### Classification
- 0–29 = Low · 30–59 = Medium · 60–79 = High · 80–100 = Critical

---

# Business Logic

1. Resolve the mule account, its originators, its controller, and its forwarding destination.
2. Compute the pass-through ratio (total outbound / total inbound funds).
3. Compute the account's age in days since opening.
4. Compute the behavioural mismatch ratio (monthly throughput / declared monthly income).
5. Count the shared-device/shared-beneficiary links to other known mule accounts.
6. Score each of the four components against its band cut-lines.
7. Aggregate the weighted exposure score; escalate at or above the threshold.

---

# Detection Workflow

```text
Inbound/Outbound Reconciliation
       ↓
Pass-through Ratio Calculation
       ↓
Account Age & Behavioural Mismatch Analysis
       ↓
Network Linkage Assessment
       ↓
Exposure Scoring
       ↓
Investigator Escalation
```

---

# Python Analytics Example

```python
suspect = accounts[
    (accounts["pass_through_ratio_band"].isin(["High", "Critical"])) &
    (accounts["account_age_days"] <= 90) &
    (accounts["shared_link_count"] >= 2)
]
alerts = suspect[suspect["exposure_score"] >= 80]
```

---

# Investigator Outcome

```text
Account:               Rosalind Fairweather — MUL019
Home Branch:           Meridian Trust Bank - Uptown Branch
Account Age:            12 days
Total Inflow:           $100,000
Total Outflow:          $96,000 (pass-through ratio 0.960)
Declared Monthly Income: $3,200 · Monthly Throughput: $92,000 (ratio 28.75)
Shared Links:            6 (other known mule accounts)
Controller:             Marcus Vane
Forwarding Destination:  Alpha Trading Ltd
Exposure Score:         90 / 100
Investigation Outcome:  Escalate — newly-opened personal account pass-throughing funds
                         far beyond its declared profile, linked to other known mules
```

---

# Regulatory Relevance

- FATF Recommendations 10 & 13 (customer due diligence and correspondent banking)
- BSA money-mule and third-party-control provisions (31 U.S.C. § 5318(h))
- FinCEN money-mule advisories (Advisory FIN-2019-A003)
- Wolfsberg correspondent-banking due-diligence principles

---

# Related Typologies

- BA002 Funnel Accounts
- BA005 Rapid Movement
- BA009 Transaction Laundering

---

# Strategic Value

BA003 shows how pass-through and behavioural-profile intelligence defeats mule-network
exploitation: by quantifying how closely outbound funds track inbound funds, how young the
account is relative to when the flows began, how far throughput departs from the holder's
declared profile, and how many links tie the account to other known mules, it surfaces
accounts that would otherwise pass as an ordinary personal customer. As the third typology
in the fc-06 Correspondent Banking Analytics family, BA003 reuses BA001/BA002's file set,
scoring convention, and fc-10 wiring pattern verbatim, confirming the template continues to
replicate cleanly onto a personal-account subject.
