# Risk Scoring Standards

## Purpose

This document defines the common standards used when designing Financial Crime risk scoring models.

The objective is to ensure consistent, explainable and auditable risk scoring across AML, TBML, Network Intelligence, Correspondent Banking and Capital Markets surveillance use cases.

---

## Scoring Principles

All risk models should be:

- Explainable
- Transparent
- Repeatable
- Auditable
- Calibrated
- Independent of investigator judgement

Scores should be derived from observable risk indicators.

---

## Standard Risk Scale

| Score Range | Risk Rating | Priority |
|-------------|------------|-----------|
| 0-29 | Low | Monitor |
| 30-59 | Medium | Review |
| 60-79 | High | Investigate |
| 80-100 | Critical | Immediate Escalation |

---

## Risk Indicator Categories

### Customer Risk

Examples:

- High Risk Industry
- Politically Exposed Person (PEP)
- Sanctions Exposure
- Adverse Media
- Offshore Structures

---

### Geographic Risk

Examples:

- High Risk Jurisdiction
- Sanctioned Country
- Trade Corridor Risk
- Corruption Exposure

---

### Transaction Risk

Examples:

- Unusual Transaction Value
- Rapid Movement of Funds
- Structuring Activity
- Circular Transactions
- Invoice Anomalies

---

### Network Risk

Examples:

- Shared Ownership
- Shared Directors
- Multi-Hop Relationships
- Hidden Beneficial Ownership
- High Risk Counterparties

---

### Behavioural Risk

Examples:

- Sudden Activity Changes
- Dormant Account Activation
- Velocity Changes
- New Counterparty Behaviour

---

## Weighting Standards

Recommended weighting ranges:

| Category | Weight |
|-----------|---------|
| Customer Risk | 20-30% |
| Geographic Risk | 10-20% |
| Transaction Risk | 30-40% |
| Network Risk | 15-25% |
| Behavioural Risk | 10-20% |

Weights should be adjusted according to typology requirements.

---

## Risk Indicator Design

Each indicator should include:

- Description
- Business rationale
- Data source
- Calculation logic
- Weight
- Threshold
- Expected outcome

---

## Alert Threshold Standards

| Score | Action |
|---------|---------|
| 0-29 | No Alert |
| 30-59 | Queue Review |
| 60-79 | Generate Alert |
| 80-100 | Escalate Priority Alert |

---

## Model Governance

All models should be reviewed for:

- False Positive Rate
- False Negative Risk
- Alert Volumes
- Investigator Feedback
- Regulatory Alignment

---

## Calibration Requirements

Models should be recalibrated:

- Quarterly
- Following major typology changes
- Following regulatory findings
- Following material alert volume changes

---

## Documentation Standards

Every scoring model must contain:

- Business Objective
- Risk Indicators
- Weighting Methodology
- Scoring Logic
- Alert Thresholds
- Calibration Approach
- Governance Controls

---

Financial Crime Analytics Standards
Risk Scoring Framework v1.0
