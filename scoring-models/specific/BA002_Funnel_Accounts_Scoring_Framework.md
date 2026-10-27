# BA002 Funnel Accounts — Exposure Scoring Framework

Specialises the macro framework for funnel accounts. Implemented and validated by
`python/specific/BA002/ba002_risk_model.py`.

## Components and weights

| Component | Weight | What it measures |
|-----------|--------|------------------|
| Geographic Dispersion | 30% | Count/spread of distinct depositor regions feeding the account |
| Inflow Fan-in | 25% | Number of distinct source depositors |
| Rapid Passthrough | 25% | How short the in-to-out dwell is (shorter = worse) |
| Beneficiary Concentration | 20% | Share of outbound funds concentrated on a single downstream beneficiary |

## Component banding rules

### Geographic Dispersion
`distinct_source_regions` is REQUIRED — the count of distinct regions the depositors are
drawn from.
- ≤ 2 → Low · ≤ 4 → Medium · ≤ 7 → High · otherwise (≥ 8) → Critical

### Inflow Fan-in
`distinct_depositors` is REQUIRED — the count of distinct, unrelated depositors feeding
the account.
- ≤ 5 → Low · ≤ 15 → Medium · ≤ 30 → High · otherwise (≥ 31) → Critical

### Rapid Passthrough
`max_dwell_hours` is REQUIRED — the longest the funnelled cash sits on the account before
it clears onward. Shorter dwell is worse.
- ≥ 72 → Low · ≥ 24 → Medium · ≥ 6 → High · otherwise (< 6) → Critical

### Beneficiary Concentration
`r = top_beneficiary_amount / total_outflow_amount`. Both amounts are REQUIRED.
- r < 0.25 → Low · r < 0.50 → Medium · r < 0.80 → High · otherwise → Critical

## Scoring

Band midpoints (15/45/70/90), weighted sum, half-up rounding, boundaries at 80. Graded.

## Worked example — FUN019 (Zara Tallowwisp)

| Component | Evidence | Band | Contribution |
|-----------|----------|------|--------------|
| Geographic Dispersion | Deposits drawn from 9 distinct regions | Critical | 27.0 |
| Inflow Fan-in | 33 distinct depositors feeding the account | Critical | 22.5 |
| Rapid Passthrough | Longest dwell before clearing onward: 3 hours | Critical | 22.5 |
| Beneficiary Concentration | $90,000 of $100,000 outbound funds to one beneficiary (r = 0.900), Zeta Commodities Ltd | Critical | 18.0 |
| **Exposure score** | | | **90 / 100 — Critical** |

A clean account with all four components Low scores 15/100 (FUN001, Wei Juniperkettle). Alert
threshold: ≥ 80 — the sample data ships four accounts at or above it (FUN019 90, FUN020
86, FUN021 85, FUN022 84), proving the scorer discriminates rather than rubber-stamping
every row. FUN019 is the single highest-scoring account, which is deliberate: the FC-10
adapter builds its case/graph from the top-scored row, so the account that fuses onto
Zeta Commodities Ltd has to be that row.
