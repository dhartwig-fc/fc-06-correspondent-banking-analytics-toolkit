# BA006 Dormant Reactivation — Exposure Scoring Framework

Specialises the macro framework for dormant reactivation. Implemented and validated by
`python/specific/BA006/ba006_risk_model.py`.

## Components and weights

| Component | Weight | What it measures |
|-----------|--------|------------------|
| Reactivation Spike | 30% | Magnitude of the reactivating inflow relative to the account's pre-dormancy average monthly activity |
| Dormancy Length | 25% | How long the account sat dormant before reactivating -- longer dormancy is worse |
| Profile Deviation | 25% | New counterparties/geographies that appear after reactivation and were never part of the prior profile |
| Immediate Outflow | 20% | How closely the outbound amount after reactivation tracks the reactivating inflow -- wake up and drain |

## Component banding rules

### Reactivation Spike
`r = reactivation_amount / pre_dormancy_avg_monthly_activity`. Both values are REQUIRED;
`pre_dormancy_avg_monthly_activity` must be > 0.
- r < 3 → Low · r < 8 → Medium · r < 20 → High · otherwise (≥ 20) → Critical

### Dormancy Length
`dormancy_days` is REQUIRED — the days the account sat idle before the reactivating
inflow landed. Longer dormancy is worse.
- < 90 → Low · < 180 → Medium · < 365 → High · otherwise (≥ 365) → Critical

### Profile Deviation
`new_counterparty_count` is REQUIRED — the number of counterparties/geographies that
appear after reactivation and were never part of the account's prior profile.
- ≤ 2 → Low · ≤ 4 → Medium · ≤ 7 → High · otherwise (≥ 8) → Critical

### Immediate Outflow
`r = outflow_amount / reactivation_amount`. Both amounts are REQUIRED;
`reactivation_amount` must be > 0.
- r < 0.50 → Low · r < 0.75 → Medium · r < 0.92 → High · otherwise (≥ 0.92) → Critical

## Scoring

Band midpoints (15/45/70/90), weighted sum, half-up rounding, boundaries at 80. Graded.

## Worked example — DR019 (Viktor Tallowbristle)

| Component | Evidence | Band | Contribution |
|-----------|----------|------|--------------|
| Reactivation Spike | $200,000 reactivating inflow against an $8,000 pre-dormancy monthly average (r = 25.0) | Critical | 27.0 |
| Dormancy Length | Account sat dormant for 730 days (2 years) before reactivating | Critical | 22.5 |
| Profile Deviation | 10 new counterparties/geographies never seen in the prior profile | Critical | 22.5 |
| Immediate Outflow | $190,000 of $200,000 reactivating inflow drains back out (r = 0.950) | Critical | 18.0 |
| **Exposure score** | | | **90 / 100 — Critical** |

A clean account with all four components Low scores 15/100 (DR001, Aiden Kettletumble). Alert
threshold: ≥ 80 — the sample data ships four accounts at or above it (DR019 90, DR022 86,
DR021 85, DR020 84), proving the scorer discriminates rather than rubber-stamping every
row. DR019 is the single highest-scoring account, which is deliberate: the FC-10 adapter
builds its case/graph from the top-scored row, so the account that fuses onto Alpha
Trading Ltd has to be that row.
