# Data Dictionary

## Purpose

This data dictionary defines the core data elements required to support the Correspondent
Banking Analytics suite (BA001–BA010).

The model supports:

- Account and transaction behavioural monitoring
- Correspondent / respondent banking relationship analysis
- Funnel, mule and structuring detection
- Circular and rapid fund-movement analysis
- Cash-intensive and merchant transaction-laundering detection
- Peer-segment behavioural deviation analysis
- Exposure scoring
- Alert generation
- Intelligence product production

The authoritative field-level model for the Python layer lives beside each analytic under
`python/specific/<ID>/`; this dictionary is the domain-level summary. Individual analytics add
per-entity model documents to this folder as their data requirements are specified.

---

## Core Entities

| Entity | Description |
|--------|--------------|
| Account | Deposit, current, business or merchant account under assessment |
| Customer | Account holder — individual or business — with a KYC profile |
| Correspondent Bank | Bank providing services to a respondent bank in another jurisdiction |
| Respondent Bank | Bank receiving correspondent banking services (nested-relationship exposure) |
| Beneficiary | Ultimate recipient of an outbound transfer |
| Originator | Party initiating an inbound transfer |
| Branch / Location | Physical deposit or withdrawal location (BA001 multi-location) |
| Merchant Account | Payment acceptance account (BA009) |
| Transaction | Deposit, withdrawal, transfer or payment event being analysed |
| Peer Segment | Cohort of accounts sharing declared profile characteristics (BA010) |
| Alert | Generated correspondent-banking exposure alert |

---

## Exposure Model

Exposure is assessed as a weighted composite of component scores. Not every analytic uses
every component; each analytic's scoring framework (`scoring-models/specific/`) states its own
components and weights. The suite-wide vocabulary is:

| Component | Meaning |
|-----------|---------|
| Sub-Threshold / Structuring Exposure | Cash activity broken up to evade reporting thresholds (BA001) |
| Fan-In / Fan-Out Exposure | Many-to-one or one-to-many flow concentration (BA002 Funnel) |
| Pass-Through Exposure | Out-approximates-in flow with minimal retention (BA003 Mule) |
| Loop / Circularity Exposure | Funds returning to their origin through intermediate hops (BA004) |
| Velocity Exposure | Speed of fund movement relative to balance or history (BA005 Rapid Movement) |
| Reactivation Exposure | Magnitude and profile deviation of a dormant account's reactivation (BA006) |
| Cash Intensity Exposure | Cash volume disproportionate to declared business profile (BA007) |
| Chain / Layering Exposure | Depth, opacity and jurisdiction-hopping of an intermediary chain (BA008) |
| Merchant / Third-Party Exposure | Hidden third-party processing behind a merchant account (BA009) |
| Peer Deviation Exposure | Statistical deviation from an account's peer segment (BA010) |
| Counterparty Exposure | Risk carried by originating, forwarding or beneficiary counterparties |
| Jurisdiction Exposure | High-risk countries or corridors |

---

## Exposure Bands

| Score Range | Exposure Band | Priority |
|-------------|---------------|----------|
| 0–29 | Low | Monitor |
| 30–59 | Medium | Review |
| 60–79 | High | Investigate |
| 80–100 | Critical | Immediate Escalation |

---

## Data Model Principle

The data model is intentionally simple and synthetic. It is designed to demonstrate
analytical logic, exposure scoring and investigation outputs rather than replicate a
production correspondent-banking data model.
