# BA010 Peer Group Anomalies — Exposure Scoring Framework

Specialises the macro framework for peer-relative behavioural deviation.
Implemented and validated by `python/specific/BA010/ba010_risk_model.py`.

## Components and weights

| Component | Weight | What it measures |
|-----------|--------|------------------|
| Volume Z-Score | 30% | Deviation of transaction volume from the peer segment mean |
| Velocity Z-Score | 25% | Deviation of turnover velocity from the peer segment mean |
| Product Usage Deviation | 25% | Deviation of the account's product/channel mix breadth from its peers |
| Counterparty Diversity Z-Score | 20% | Deviation of counterparty breadth from the peer segment mean |

## Component banding rule (shared across all four)

`z = abs((own_value - peer_mean) / peer_std)`. All three inputs (the account's own
value, the peer segment's mean, the peer segment's standard deviation) are
REQUIRED — a peer segment with no measured mean/std cannot be compared against, and
that is a different finding from "measures as zero deviation". `peer_std` must be
strictly positive.

- z < 1 → Low · z < 2 → Medium · z < 3 → High · otherwise (z ≥ 3) → Critical

Unlike BA001–BA009's ratio- or count-based components, every BA010 component uses
this SAME banding rule — only the three inputs (own value, peer mean, peer std)
differ per component. The deviation is measured in standard deviations from the
account's own peer segment, not against a fixed absolute cut-line, so the same raw
number can be Low for one peer segment and Critical for another.

## Scoring

Band midpoints (15/45/70/90), weighted sum, half-up rounding, boundaries at 80. Graded.

## Worked example — PGA019 (Miriam Oduya)

| Component | Evidence | Band | Contribution |
|-----------|----------|------|--------------|
| Volume Z-Score | $355,000 own volume vs peer mean $250,000, std $25,000 (z = 4.20) | Critical | 27.0 |
| Velocity Z-Score | 27 own velocity vs peer mean 12, std 4 (z = 3.75) | Critical | 22.5 |
| Product Usage Deviation | 13 own product count vs peer mean 6, std 2 (z = 3.50) | Critical | 22.5 |
| Counterparty Diversity Z-Score | 20 own counterparty count vs peer mean 12, std 2 (z = 4.00) | Critical | 18.0 |
| **Exposure score** | | | **90 / 100 — Critical** |

A clean account with all four components Low scores 15/100 (PGA001, Elena
Marchetti). Alert threshold: ≥ 80 — the sample data ships four accounts at or above
it (PGA019 90, PGA020 86, PGA021/PGA022 85 each), proving the scorer discriminates
rather than rubber-stamping every row. PGA019 is the single highest-scoring account,
which is deliberate: the FC-10 adapter builds its case/graph from the top-scored
row, and PGA019's peer-segment deviation concentrates on a single anomalous
counterparty — **Alpha Trading Ltd**, the same real-world company already in the
estate network (NI001's REG-2001, NI004/PAT007's C001, and BA003/BA006's fc-06
bridges). Because Alpha Trading Ltd is a COMPANY, the fusion bridge is carried on
its exact name, the same pattern BA001/BA003/BA004/BA006/BA007/BA008 use — the
canonical entity resolver's name-union joins it across domains without needing a
shared local id.
