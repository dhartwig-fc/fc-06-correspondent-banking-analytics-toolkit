# BA003 Mule Accounts — Exposure Scoring Framework

Specialises the macro framework for mule accounts. Implemented and validated by
`python/specific/BA003/ba003_risk_model.py`.

## Components and weights

| Component | Weight | What it measures |
|-----------|--------|------------------|
| Pass-through Ratio | 30% | Share of inbound funds forwarded onward -- out approx in, near-zero retained |
| Account Youth | 25% | How recently the account was opened |
| Behavioural Mismatch | 25% | Monthly throughput vs the holder's declared income/profile |
| Network Linkage | 20% | Shared device/beneficiary links to other known mule accounts |

## Component banding rules

### Pass-through Ratio
`r = total_outflow_amount / total_inflow_amount`. Both amounts are REQUIRED;
`total_inflow_amount` must be > 0.
- r < 0.50 → Low · r < 0.75 → Medium · r < 0.92 → High · otherwise → Critical

### Account Youth
`account_age_days` is REQUIRED — the number of days since the account was opened.
- ≥ 365 → Low · ≥ 180 → Medium · ≥ 60 → High · otherwise (< 60) → Critical

### Behavioural Mismatch
`r = monthly_throughput_amount / declared_monthly_income`. Both amounts are REQUIRED;
`declared_monthly_income` must be > 0.
- r < 3 → Low · r < 8 → Medium · r < 20 → High · otherwise → Critical

### Network Linkage
`shared_link_count` is REQUIRED — the number of shared-device/shared-beneficiary links
to other accounts already known to be mules.
- ≤ 0 → Low · ≤ 1 → Medium · ≤ 3 → High · otherwise (≥ 4) → Critical

## Scoring

Band midpoints (15/45/70/90), weighted sum, half-up rounding, boundaries at 80. Graded.

## Worked example — MUL019 (Rosalind Fairweather)

| Component | Evidence | Band | Contribution |
|-----------|----------|------|--------------|
| Pass-through Ratio | $96,000 of $100,000 inbound forwarded onward (r = 0.960) | Critical | 27.0 |
| Account Youth | Account opened 12 days before the flows began | Critical | 22.5 |
| Behavioural Mismatch | $92,000 monthly throughput vs $3,200 declared income (r = 28.75) | Critical | 22.5 |
| Network Linkage | 6 shared device/beneficiary links to other known mule accounts | Critical | 18.0 |
| **Exposure score** | | | **90 / 100 — Critical** |

A clean account with all four components Low scores 15/100 (MUL001, Owen Bennett). Alert
threshold: ≥ 80 — the sample data ships four accounts at or above it (MUL019 90, MUL020
86, MUL021 85, MUL022 84), proving the scorer discriminates rather than rubber-stamping
every row. MUL019 is the single highest-scoring account, which is deliberate: the FC-10
adapter builds its case/graph from the top-scored row, so the account that fuses onto
Alpha Trading Ltd has to be that row.
