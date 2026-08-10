[← Back to Portfolio](https://dhartwig-fc.github.io/dan-hartwig-portfolio/)

## FC-06 Correspondent Banking Analytics Toolkit

The Correspondent Banking Analytics Toolkit is a repository focused on transaction-monitoring
and account-behavioural intelligence for correspondent banking: structuring, funnel and mule
account activity, circular funds flow, rapid movement of funds, dormant reactivation, cash
intensive activity, layering, transaction laundering and peer group anomalies.

The repository explores how account behaviour, transaction flow, counterparty exposure and
peer-segment deviation can be combined to identify correspondent-banking risk that a single
transaction-level rule would miss — funds moved between correspondent, respondent and beneficiary
accounts, through nested relationships, in patterns that only resolve at the account or network
level.

The toolkit contains banking analytics typologies (BA001–BA010), exposure scoring frameworks,
network investigation patterns, detection methodologies and intelligence artefacts covering
account-behavioural monitoring, transaction-flow analysis, peer-segment anomaly detection and
correspondent/respondent banking exposure.

The objective is to demonstrate how intelligence-led transaction monitoring can evolve beyond
static rule thresholds and support a more holistic understanding of correspondent-banking risk,
control effectiveness and money-laundering typology exposure.

### Key Capability Areas

- Correspondent Banking Intelligence
- Transaction Monitoring Optimisation
- Account Behavioural Analytics
- Funnel & Mule Account Detection
- Network Intelligence
- Transaction Flow Analytics
- Peer Group Anomaly Detection
- Cash Intensive Activity Analytics
- Layering & Transaction Laundering Typologies
- Exposure Scoring Frameworks
- Detection Strategy
- Investigation Workflows

### The BA001–BA010 Family

| ID | Typology | Pattern | Subject |
|------|------|------|------|
| BA001 | Structuring | Sub-threshold cash broken up to evade CTR reporting | Customer account |
| BA002 | Funnel Accounts | Many geographically-dispersed deposits collected then moved out | Funnel account |
| BA003 | Mule Accounts | Personal accounts receiving/forwarding illicit funds | Mule account |
| BA004 | Circular Funds Flow | Round-tripping loop returning to origin | Originating account |
| BA005 | Rapid Movement | Funds in and immediately out (velocity / layering signal) | Account |
| BA006 | Dormant Reactivation | Long-dormant account suddenly active with large flows | Reactivated account |
| BA007 | Cash Intensive Activity | Cash disproportionate to declared business profile | Business account |
| BA008 | Layering | Complex transfer chains obscuring source | Seed account |
| BA009 | Transaction Laundering | A legitimate merchant account processing hidden third parties | Merchant account |
| BA010 | Peer Group Anomalies | Account behaviour deviating from its peer segment | Account |

See `typologies/BA_Typology_Register.md` for the full inventory and build waves.

### House Conventions

Every BA analytic follows the estate-wide conventions established by the fc-04/fc-05 toolkits:

- **W2 analytic contract** — each engine emits `risk_score` (int 0–100) and
  `classification = band(risk_score)`, `risk_drivers`, and full narrative sections, so the FC-10
  runtime can delegate to it without re-implementing scoring.
- **Band-midpoint scoring** — `BAND_SCORE = {Low: 15, Medium: 45, High: 70, Critical: 90}`,
  `RISK_BANDS = ((0,29,Low), (30,59,Medium), (60,79,High), (80,100,Critical))`, boundary at 80,
  `ROUND_HALF_UP` via `Decimal`. Every component scorer returns a band name, never a raw number;
  `RiskModelError` is raised (not defaulted to zero) when a required field is missing.
- **≥20-row real-named sample data** — every typology's sample-data CSVs ship at least 20 data
  rows per component, using real entity/account names (no bare ids), enforced live by
  `python/specific/test_sample_data_row_minimum.py` (no grandfathering for BA — every typology
  here is new).

### Repository Structure

```text
fc-06-correspondent-banking-analytics-toolkit/
├── typologies/                 # BA typology library + BA_Typology_Register.md
├── diagrams/                   # Enterprise typology diagrams
├── data-model/                 # Domain data dictionary and entity models
├── scoring-models/
│   ├── common/                 # Cross-analytic scoring standards, governance, calibration
│   └── specific/                # One exposure scoring framework per analytic
├── python/
│   └── specific/                # Per-analytic engine packages
│       └── BA0NN/               # risk model · scenario callable · schema · sample-data
│                                # · expected_outputs · executable tests
├── intelligence-products/
│   ├── common/                 # Product standards and templates
│   └── specific/BA0NN/          # Per-analytic intelligence products
└── operations/
    ├── common/                 # Alert triage, escalation, investigation standards
    └── specific/                # Per-analytic investigator playbooks
```

### Build Model

Each analytic is built as a **self-contained, independently tested engine** under
`python/specific/<ID>/`, mirroring the fc-04 TBML and fc-05 Sanctions toolkits. The engine is
proven standalone in this repository — risk model, scenario callable, schema, generated sample
data, expected outputs and its own test suite — **before** it is put through the FC-10 governed
runtime, where a thin adapter delegates to it. See `typologies/BA_Typology_Register.md` for the
scenario inventory and build waves.

### Strategic Focus

The repository demonstrates how correspondent-banking intelligence, network analytics and
transaction-flow analysis can be integrated into a modern transaction-monitoring operating model
capable of identifying structuring, mule and funnel activity, circular and rapid fund movement,
dormant-account reactivation, cash-intensive activity, layering, transaction laundering and
peer-group behavioural anomalies.
