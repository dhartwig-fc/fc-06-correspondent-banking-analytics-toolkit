# BA007 Cash Intensive Activity — Exposure Scoring Framework

Specialises the macro framework for cash-intensive businesses. Implemented and validated
by `python/specific/BA007/ba007_risk_model.py`.

## Components and weights

| Component | Weight | What it measures |
|-----------|--------|------------------|
| Cash Ratio | 35% | Cash deposits vs total turnover, scaled against the business's declared peer-segment cash norm |
| Profile Excess | 25% | Cash actually deposited vs the business's own declared annual cash volume |
| Deposit Regularity | 20% | How unnaturally even the deposit rhythm is (lower variability = worse) |
| Commingling | 20% | Share of deposited cash that did not originate with the business itself |

## Component banding rules

### Cash Ratio
`excess = (cash_deposits_amount / total_turnover_amount) / peer_norm_cash_ratio`. All
three inputs are REQUIRED. A business running at its own peer-segment cash norm scores
Low; one running multiples of it scores Critical.
- excess < 1.3 → Low · < 1.8 → Medium · < 2.5 → High · otherwise (≥ 2.5) → Critical

### Profile Excess
`r = cash_deposits_amount / declared_annual_cash_volume`. Both amounts are REQUIRED —
the declared volume is what the business told the bank when the account was profiled
for KYC.
- r < 1.1 → Low · r < 1.5 → Medium · r < 2.2 → High · otherwise → Critical

### Deposit Regularity
`deposit_cv_pct` is REQUIRED — the coefficient of variation (%) of individual deposit
sizes. Real cash businesses are noisy day to day; a suspiciously LOW coefficient of
variation means the deposits were engineered, not counted, so LOWER is worse.
- ≥ 45 → Low · ≥ 30 → Medium · ≥ 15 → High · otherwise (< 15) → Critical

### Commingling
`r = third_party_deposit_amount / total_deposit_amount`. Both amounts are REQUIRED.
- r < 0.05 → Low · r < 0.15 → Medium · r < 0.30 → High · otherwise → Critical

## Scoring

Band midpoints (15/45/70/90), weighted sum, half-up rounding, boundaries at 80. Graded.

## Worked example — CIA019 (Gamma Imports Ltd)

| Component | Evidence | Band | Contribution |
|-----------|----------|------|--------------|
| Cash Ratio | $760,000 cash of $820,000 turnover (92.7%), 3.09x the 30% peer-segment norm | Critical | 31.5 |
| Profile Excess | $760,000 deposited vs $300,000 declared annual cash volume (r = 2.53) | Critical | 22.5 |
| Deposit Regularity | Deposit coefficient of variation: 8% — unnaturally even | Critical | 18.0 |
| Commingling | $250,000 of $760,000 deposited cash from unrelated third parties (r = 0.329) | Critical | 18.0 |
| **Exposure score** | | | **90 / 100 — Critical** |

A clean business with all four components Low scores 15/100 (CIA001, Harborlight
Grocers Ltd). Alert threshold: ≥ 80 — the sample data ships four accounts at or above it
(CIA019 90, CIA020/CIA021/CIA022 86 each), proving the scorer discriminates rather than
rubber-stamping every row. CIA019 is the single highest-scoring account, which is
deliberate: the FC-10 adapter builds its case/graph from the top-scored row, and CIA019's
subject IS **Gamma Imports Ltd** — an entity already in the estate network — so the
account that fuses onto it has to be that row. Unlike BA001–BA006, where the bridge
entity is a CONNECTED entity, BA007 is a designated bridge typology where the SUBJECT
itself is the bridge.
