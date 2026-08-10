# BA005 Rapid Movement — Exposure Scoring Framework

Specialises the macro framework for rapid movement. Implemented and validated by
`python/specific/BA005/ba005_risk_model.py`.

## Components and weights

| Component | Weight | What it measures |
|-----------|--------|------------------|
| Dwell Time | 35% | How briefly funds are held before clearing onward -- shorter dwell is worse |
| Velocity | 25% | Turnover relative to the account's own balance |
| Onward Dispersion | 20% | How many distinct onward destinations receive the outbound leg |
| Value Match | 20% | How closely the outbound amount tracks the inbound amount -- out approx in |

## Component banding rules

### Dwell Time
`dwell_time_hours` is REQUIRED — the hours funds rest on the account between
clearing in and clearing back out. Shorter dwell is worse.
- ≥ 48 → Low · ≥ 12 → Medium · ≥ 2 → High · otherwise (< 2) → Critical

### Velocity
`r = total_turnover_amount / avg_balance`. Both values are REQUIRED;
`avg_balance` must be > 0.
- r < 3 → Low · r < 8 → Medium · r < 20 → High · otherwise (≥ 20) → Critical

### Onward Dispersion
`distinct_destination_count` is REQUIRED — the number of distinct onward
destinations the outbound leg is spread across.
- ≤ 2 → Low · ≤ 4 → Medium · ≤ 7 → High · otherwise (≥ 8) → Critical

### Value Match
`r = outbound_amount / inbound_amount`. Both amounts are REQUIRED;
`inbound_amount` must be > 0.
- r < 0.50 → Low · r < 0.75 → Medium · r < 0.92 → High · otherwise (≥ 0.92) → Critical

## Scoring

Band midpoints (15/45/70/90), weighted sum, half-up rounding, boundaries at 80. Graded.

## Worked example — RM019 (Dmitri Petrov)

| Component | Evidence | Band | Contribution |
|-----------|----------|------|--------------|
| Dwell Time | Funds clear in 1 hour before moving onward | Critical | 31.5 |
| Velocity | $300,000 turnover against a $10,000 average balance (r = 30.0) | Critical | 22.5 |
| Onward Dispersion | Outbound leg spreads across 9 distinct destinations | Critical | 18.0 |
| Value Match | $98,000 of $100,000 inbound clears back out (r = 0.980) | Critical | 18.0 |
| **Exposure score** | | | **90 / 100 — Critical** |

A clean account with all four components Low scores 15/100 (RM001, Ingrid Solberg). Alert
threshold: ≥ 80 — the sample data ships four accounts at or above it (RM019 90, RM020 86,
RM021 85, RM022 83), proving the scorer discriminates rather than rubber-stamping every
row. RM019 is the single highest-scoring account, which is deliberate: the FC-10 adapter
builds its case/graph from the top-scored row, so the account that fuses onto Zeta
Commodities Ltd has to be that row.
