# Correspondent Banking Analytics Model Calibration Guide

## Purpose

This guide defines the approach for monitoring, evaluating and calibrating the Correspondent
Banking Analytics detection analytics (BA001–BA010).

The objective is to optimise:

- Detection effectiveness
- Investigator efficiency
- False positive reduction
- Alert prioritisation
- Scenario performance

while maintaining regulatory effectiveness.

---

## Calibration Lifecycle

```text
Typology
  ↓
Detection Logic
  ↓
Exposure Scoring
  ↓
Alert Generation
  ↓
Investigator Review
  ↓
Case Outcome
  ↓
Performance Analysis
  ↓
Model Calibration
  ↓
Scenario Improvement
```

---

## Calibration Objectives

| Objective | Description |
|------------|------------|
| Improve Detection Quality | Increase identification of genuine correspondent-banking laundering activity |
| Reduce False Positives | Reduce unnecessary investigations |
| Improve Investigator Efficiency | Focus effort on highest-exposure alerts |
| Improve Prioritisation | Enhance alert triage accuracy |
| Maintain Regulatory Compliance | Ensure effective transaction-monitoring controls |

---

## Key Performance Indicators

| KPI | Description |
|------------|------------|
| Alert Volume | Total alerts generated |
| False Positive Rate | Percentage of alerts closed without concern |
| True Positive Rate | Percentage of alerts resulting in escalation |
| SAR Conversion Rate | Percentage of alerts resulting in SAR consideration |
| Average Investigation Time | Time required to review alerts |
| Alert-to-Case Ratio | Efficiency of alert generation |
| Investigator Override Rate | Frequency of investigator disagreement |

---

## Calibration Inputs

| Input Source | Purpose |
|------------|------------|
| Alert Outcomes | Measure scenario effectiveness |
| Investigator Feedback | Identify logic weaknesses |
| SAR Decisions | Measure risk identification quality |
| Account & Transaction Data Updates | Keep behavioural baselines current |
| Peer Segment Data | Improve peer-deviation accuracy |
| Correspondent / Respondent Relationship Data | Detect changing nested-banking behaviour |
| Regulatory Findings | Ensure compliance alignment |
| Quality Assurance Reviews | Validate operational performance |

---

## Calibration Parameters

> Per-analytic thresholds and component weights are defined in each analytic's own scoring
> framework under `scoring-models/specific/`. The values below are the toolkit's *starting*
> conventions; an analytic overrides them where its typology requires.

### Detection Thresholds (defaults)

| Parameter | Initial Setting |
|------------|------------|
| Structuring aggregation confidence | 0.85 |
| Material exposure score | 60 |
| Critical exposure score | 80 |
| Minimum pass-through ratio considered (mule accounts) | 85% |

---

### Exposure Components (illustrative — BA001 Structuring)

| Exposure Component | Initial Weight |
|------------|------------|
| Sub-Threshold Clustering | 35% |
| Temporal Clustering | 25% |
| Multi-Location Deposits | 20% |
| Aggregation-To-Transfer | 20% |

---

### Multipliers

| Multiplier | Initial Value |
|------------|------------|
| Confirmed structuring below CTR threshold | 2.0x |
| Flow reaches a known mule/funnel network | 1.5x |
| High-risk jurisdiction or corridor | 1.25x |
| Repeat behaviour | 1.2x |

---

## Example Calibration Scenarios

### Scenario 1 – Excessive False Positives

Observation:

```text
False Positive Rate = 85%
```

Potential Actions:

- Raise the material-exposure threshold
- Tighten indirect-exposure decay so distant links contribute less
- Reduce sensitivity to weak single-signal matches

---

### Scenario 2 – Missed High-Risk Cases

Observation:

```text
Known laundering activity not detected
```

Potential Actions:

- Lower the exposure threshold
- Increase behavioural-mismatch weighting
- Increase jurisdiction / corridor weighting

---

### Scenario 3 – Excessive Alert Volumes

Observation:

```text
Investigator queues exceed capacity
```

Potential Actions:

- Raise score thresholds
- Increase prioritisation requirements
- Suppress low-materiality alerts

---

## Calibration Decision Framework

| Observation | Potential Action |
|------------|------------|
| High False Positive Rate | Increase thresholds |
| Low Detection Rate | Reduce thresholds |
| Missed Behavioural Exposure | Increase behavioural-mismatch weighting |
| High Jurisdiction Exposure | Increase corridor / flag weighting |
| Excessive Alert Volumes | Tighten scoring criteria |
| Strong SAR Conversion | Preserve current configuration |

---

## Governance Controls

| Control | Purpose |
|------------|------------|
| Calibration Approval Process | Ensure controlled model changes |
| Change Documentation | Maintain audit trail |
| Performance Monitoring | Measure effectiveness |
| Independent Review | Validate changes |
| Regulatory Oversight | Ensure compliance alignment |

---

## Relationship To Repository Components

| Repository Component | Purpose |
|------------|------------|
| Typologies | Define laundering behaviour |
| Diagrams | Visualise relationships |
| Scoring Models | Quantify exposure |
| Python Analytics | Implement logic |
| Alert Triage Framework | Prioritise alerts |
| Investigator Playbooks | Operational response |
| Model Calibration Guide | Continuous improvement |

---

Financial Crime Correspondent Banking Analytics Toolkit

Operational Framework: Correspondent Banking Analytics Model Calibration Guide
