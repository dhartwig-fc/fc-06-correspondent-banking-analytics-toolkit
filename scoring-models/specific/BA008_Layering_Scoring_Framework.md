# BA008 Layering — Exposure Scoring Framework

Specialises the macro framework for layering. Implemented and validated by
`python/specific/BA008/ba008_risk_model.py`.

## Components and weights

| Component | Weight | What it measures |
|-----------|--------|------------------|
| Chain Depth | 30% | Number of transfer hops the seed account's funds pass through before the trail goes cold |
| Intermediary Opacity | 25% | Share of the chain's intermediaries that are shell/nominee entities rather than identifiable counterparties |
| Jurisdiction Hopping | 25% | How many of the chain's hops route through a recognised secrecy/offshore jurisdiction |
| Value Fragmentation | 20% | How many pieces the seed amount is split into (and re-merged from) along the chain |

## Component banding rules

### Chain Depth
`hop_count` is REQUIRED — the number of transfer hops the seed account's funds pass
through before the trail goes cold.
- ≤ 2 → Low · ≤ 4 → Medium · ≤ 6 → High · otherwise (≥ 7) → Critical

### Intermediary Opacity
`r = opaque_intermediary_count / total_intermediary_count`. Both counts are REQUIRED;
`total_intermediary_count` must be > 0.
- r < 0.20 → Low · r < 0.45 → Medium · r < 0.75 → High · otherwise → Critical

### Jurisdiction Hopping
`secrecy_jurisdiction_hops` is REQUIRED — the count of the chain's hops that route
through a recognised secrecy/offshore jurisdiction.
- 0 → Low · 1 → Medium · 2 → High · otherwise (≥ 3) → Critical

### Value Fragmentation
`fragment_count` is REQUIRED — the number of pieces the seed amount is split into (and
re-merged from) along the chain, a split-then-remerge pattern that defeats simple
amount-matching.
- ≤ 2 → Low · ≤ 4 → Medium · ≤ 7 → High · otherwise (≥ 8) → Critical

## Scoring

Band midpoints (15/45/70/90), weighted sum, half-up rounding, boundaries at 80. Graded.

## Worked example — LAY019 (Katarina Novak)

| Component | Evidence | Band | Contribution |
|-----------|----------|------|--------------|
| Chain Depth | 9 transfer hops before the trail goes cold | Critical | 27.0 |
| Intermediary Opacity | 8 of 9 intermediaries are shell/nominee entities (r = 0.889) | Critical | 22.5 |
| Jurisdiction Hopping | 4 hops route through a recognised secrecy/offshore jurisdiction | Critical | 22.5 |
| Value Fragmentation | Seed amount split into 9 fragments along the chain | Critical | 18.0 |
| **Exposure score** | | | **90 / 100 — Critical** |

A clean account with all four components Low scores 15/100 (LAY001, Emil Novotny). Alert
threshold: ≥ 80 — the sample data ships four accounts at or above it (LAY019 90, LAY021
86, LAY020 85, LAY022 84), proving the scorer discriminates rather than rubber-stamping
every row. LAY019 is the single highest-scoring account, which is deliberate: the FC-10
adapter builds its case/graph from the top-scored row, so the account that fuses onto
Gamma Imports Ltd has to be that row.
