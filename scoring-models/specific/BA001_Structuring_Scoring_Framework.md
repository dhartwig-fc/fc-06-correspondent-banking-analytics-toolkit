# BA001 Structuring — Exposure Scoring Framework

Specialises the macro framework for cash structuring. Implemented and validated by
`python/specific/BA001/ba001_risk_model.py`.

## Components and weights

| Component | Weight | What it measures |
|-----------|--------|------------------|
| Sub-threshold Clustering | 35% | Share of cash deposits sitting just under the CTR reporting line |
| Temporal Clustering | 25% | How many deposits land inside a rolling 7-day window |
| Multi-location | 20% | Deposits spread across distinct branches/ATMs |
| Aggregation to Transfer | 20% | Structured-in cash wired out to a single beneficiary |

## Component banding rules

### Sub-threshold Clustering
`r = subthreshold_deposits / total_cash_deposits`. Both amounts are REQUIRED.
- r < 0.10 → Low · r < 0.30 → Medium · r < 0.60 → High · otherwise → Critical

### Temporal Clustering
`max_deposits_7d` is REQUIRED — the busiest rolling 7-day deposit count.
- ≤ 2 → Low · ≤ 5 → Medium · ≤ 9 → High · otherwise (≥ 10) → Critical

### Multi-location
`distinct_locations` is REQUIRED — the count of distinct branches/ATMs used.
- ≤ 1 → Low · = 2 → Medium · ≤ 4 → High · otherwise (≥ 5) → Critical

### Aggregation to Transfer
`a = wired_out / structured_in`. Both amounts are REQUIRED.
- a < 0.25 → Low · a < 0.50 → Medium · a < 0.80 → High · otherwise → Critical

## Scoring

Band midpoints (15/45/70/90), weighted sum, half-up rounding, boundaries at 80. Graded.

## Worked example — ACC019 (Dmitri Mosstumble)

| Component | Evidence | Band | Contribution |
|-----------|----------|------|--------------|
| Sub-threshold Clustering | $24,000 of $34,000 cash deposits sub-threshold (r = 0.706) | Critical | 31.5 |
| Temporal Clustering | 12 deposits in the busiest rolling 7-day window | Critical | 22.5 |
| Multi-location | Deposits spread across 6 distinct branches/ATMs | Critical | 18.0 |
| Aggregation to Transfer | $17,200 wired out of $19,000 structured in (a = 0.905), to Gammavane Imports Ltd | Critical | 18.0 |
| **Exposure score** | | | **90 / 100 — Critical** |

A clean account with all four components Low scores 15/100 (ACC001, Sofia Marrowfiddle). Alert
threshold: ≥ 80 — the sample data ships four accounts at or above it (ACC019 90, ACC020
81, ACC021 85, ACC022 86), proving the scorer discriminates rather than rubber-stamping
every row. ACC019 is the single highest-scoring account, which is deliberate: the FC-10
adapter builds its case/graph from the top-scored row, so the account that fuses onto
Gammavane Imports Ltd has to be that row.
