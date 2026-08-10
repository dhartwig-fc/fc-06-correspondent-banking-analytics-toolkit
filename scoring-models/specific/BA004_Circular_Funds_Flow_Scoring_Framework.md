# BA004 Circular Funds Flow — Exposure Scoring Framework

Specialises the macro framework for circular funds flow. Implemented and validated by
`python/specific/BA004/ba004_risk_model.py`.

## Components and weights

| Component | Weight | What it measures |
|-----------|--------|------------------|
| Loop Closure | 35% | Share of originated funds that return to the origin account -- returned approx originated |
| Hop Count | 25% | How many intermediary accounts the loop passes through before closing |
| Value Preservation | 20% | How little value is lost hop to hop across the loop |
| Timing Compression | 20% | How rapidly the whole round trip completes, origin to origin |

## Component banding rules

### Loop Closure
`r = returned_amount / originated_amount`. Both amounts are REQUIRED;
`originated_amount` must be > 0.
- r < 0.50 → Low · r < 0.75 → Medium · r < 0.92 → High · otherwise → Critical

### Hop Count
`hop_count` is REQUIRED — the number of intermediary accounts the loop passes
through before closing back on the origin.
- ≤ 2 → Low · ≤ 4 → Medium · ≤ 6 → High · otherwise (≥ 7) → Critical

### Value Preservation
`avg_hop_retention_pct` is REQUIRED — the average fraction of value retained at
each hop across the loop. Ordinary correspondent-banking activity bleeds fees
and FX spread at every hop; a loop that returns almost lossless is not
behaving like trade finance.
- < 0.80 → Low · < 0.90 → Medium · < 0.97 → High · otherwise (≥ 0.97) → Critical

### Timing Compression
`loop_duration_hours` is REQUIRED — the hours from when funds leave the
origin to when they return.
- ≥ 720 → Low · ≥ 168 → Medium · ≥ 24 → High · otherwise (< 24) → Critical

## Scoring

Band midpoints (15/45/70/90), weighted sum, half-up rounding, boundaries at 80. Graded.

## Worked example — CYC019 (Piotr Zielinski)

| Component | Evidence | Band | Contribution |
|-----------|----------|------|--------------|
| Loop Closure | $97,000 of $100,000 originated returns to origin (r = 0.970) | Critical | 31.5 |
| Hop Count | 8 intermediary accounts before the loop closes | Critical | 22.5 |
| Value Preservation | 98.5% of value retained hop to hop across the loop | Critical | 18.0 |
| Timing Compression | Round trip completes in 8 hours | Critical | 18.0 |
| **Exposure score** | | | **90 / 100 — Critical** |

A clean account with all four components Low scores 15/100 (CYC001, Henrik Bergman). Alert
threshold: ≥ 80 — the sample data ships four accounts at or above it (CYC019 90, CYC020
86, CYC021 85, CYC022 83), proving the scorer discriminates rather than rubber-stamping
every row. CYC019 is the single highest-scoring account, which is deliberate: the FC-10
adapter builds its case/graph from the top-scored row, so the account that fuses onto
Gamma Imports Ltd has to be that row.
