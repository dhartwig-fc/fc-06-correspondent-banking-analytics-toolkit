# Correspondent Banking Analytics Typology Register

## Purpose

Master inventory of the Correspondent Banking Analytics scenarios.

---

## Build Status

- **BA001 Structuring — BUILT** (Phase B, 2026-08-10). The reference implementation every
  other BA0NN typology mirrors: fc-06 analytic + >=20-row real-named sample data + docs +
  diagram, fc-10 generic delegation adapter + star graph + registry entry + manifest,
  manufactures STAGE518/stage364 clean, and fuses onto **Gamma Imports Ltd** in the
  estate network via canonical entity resolution (ACC019, 90/Critical).
- **BA002 Funnel Accounts — BUILT** (Phase C, 2026-08-10). Mirrors BA001's file set
  exactly: fc-06 analytic + 22-row real-named sample data + docs + diagram, fc-10 generic
  delegation adapter + star graph + registry entry + manifest, manufactures
  STAGE518/stage364 clean, and fuses onto **Zeta Commodities Ltd** in the estate network
  via canonical entity resolution (FUN019, 90/Critical).
- **BA003 Mule Accounts — BUILT** (Phase C, 2026-08-10). Mirrors BA001/BA002's file set
  exactly: fc-06 analytic + 22-row real-named sample data + docs + diagram, fc-10 generic
  delegation adapter + star graph + registry entry + manifest, manufactures
  STAGE518/stage364 clean, and fuses onto **Alpha Trading Ltd** in the estate network
  via canonical entity resolution (MUL019, 90/Critical).
- **BA004 Circular Funds Flow — BUILT** (Phase C, 2026-08-10). Mirrors BA001/BA002/BA003's
  file set exactly: fc-06 analytic + 22-row real-named sample data + docs + diagram, fc-10
  generic delegation adapter + star graph + registry entry + manifest, manufactures
  STAGE518/stage364 clean, and fuses onto **Gamma Imports Ltd** in the estate network
  via canonical entity resolution (CYC019, 90/Critical). Its second loop member,
  Continental Correspondent Bank, is the first recurring shared bank in the family.
- **BA005 Rapid Movement — BUILT** (Phase C, 2026-08-10). Mirrors BA001–BA004's file set
  exactly: fc-06 analytic + 22-row real-named sample data + docs + diagram, fc-10 generic
  delegation adapter + star graph + registry entry + manifest, manufactures
  STAGE518/stage364 clean, and fuses onto **Zeta Commodities Ltd** in the estate network
  via canonical entity resolution (RM019, 90/Critical). Its second onward destination,
  Continental Correspondent Bank, recurs as the shared correspondent bank across
  BA004/BA005.
- **BA006 Dormant Reactivation — BUILT** (Phase C, 2026-08-10). Mirrors BA001–BA005's file
  set exactly: fc-06 analytic + 22-row real-named sample data + docs + diagram, fc-10
  generic delegation adapter + star graph + registry entry + manifest, manufactures
  STAGE518/stage364 clean, and fuses onto **Alpha Trading Ltd** in the estate network via
  canonical entity resolution (DR019, 90/Critical). Its second reactivation counterparty,
  Continental Correspondent Bank, recurs as the shared correspondent bank across
  BA004/BA005/BA006.
- **BA007 Cash Intensive Activity — BUILT** (Phase C, 2026-08-10). Mirrors BA001–BA006's
  file set exactly: fc-06 analytic + 22-row real-named sample data + docs + diagram,
  fc-10 generic delegation adapter + star graph + registry entry + manifest, manufactures
  STAGE518/stage364 clean, and fuses onto **Gamma Imports Ltd** in the estate network via
  canonical entity resolution (CIA019, 90/Critical). BA007 is the estate's designated
  subject-as-bridge typology: unlike BA001–BA006, where the bridge entity is a connected
  counterparty, BA007's top-scoring account IS Gamma Imports Ltd itself.
- BA008–BA010 — planned (Phase C), per the build waves below.

---

| ID | Name | Category | Pattern | Subject |
|------|------|------|------|------|
| BA001 | Structuring | Cash Structuring | Sub-threshold cash broken up to evade CTR reporting | Customer account |
| BA002 | Funnel Accounts | Funnel Activity | Many geographically-dispersed deposits collected then moved out | Funnel account |
| BA003 | Mule Accounts | Mule Activity | Personal accounts receiving/forwarding illicit funds | Mule account |
| BA004 | Circular Funds Flow | Round-Tripping | Round-tripping loop returning to origin | Originating account |
| BA005 | Rapid Movement | Velocity / Layering | Funds in and immediately out (velocity / layering signal) | Account |
| BA006 | Dormant Reactivation | Behavioural Anomaly | Long-dormant account suddenly active with large flows | Reactivated account |
| BA007 | Cash Intensive Activity | Cash Intensity | Cash disproportionate to declared business profile | Business account |
| BA008 | Layering | Layering | Complex transfer chains obscuring source | Seed account |
| BA009 | Transaction Laundering | Transaction Laundering | A legitimate merchant account processing hidden third parties | Merchant account |
| BA010 | Peer Group Anomalies | Behavioural Anomaly | Account behaviour deviating from its peer segment | Account |

---

## Build Waves

### Wave 1 — Cash & Account-Origination Behaviour

- BA001 Structuring
- BA002 Funnel Accounts
- BA003 Mule Accounts

### Wave 2 — Fund-Movement Patterns

- BA004 Circular Funds Flow
- BA005 Rapid Movement
- BA006 Dormant Reactivation

### Wave 3 — Business & Complex Structures

- BA007 Cash Intensive Activity
- BA008 Layering
- BA009 Transaction Laundering
- BA010 Peer Group Anomalies

---

## Fusion Bridges

At least these BA typologies deliberately name an entity already in the estate network so
canonical resolution joins them into a fused case:

- BA007 Cash Intensive Activity → subject account of **Gamma Imports Ltd**.
- BA003 Mule Accounts → forwards to **Alpha Trading Ltd**.
- BA002 Funnel Accounts → beneficiary **Zeta Commodities Ltd**.
- BA004 Circular Funds Flow → cycles through **Gamma Imports Ltd** as its first loop
  member (also names **Continental Correspondent Bank** as a recurring second loop member).
- BA005 Rapid Movement → clears through **Zeta Commodities Ltd** as its first onward
  destination (also names **Continental Correspondent Bank** as its recurring second
  onward destination, shared with BA004).
- BA006 Dormant Reactivation → reactivates into **Alpha Trading Ltd** as its first
  reactivation counterparty (also names **Continental Correspondent Bank** as its
  recurring second reactivation counterparty, shared with BA004/BA005).
- BA009 Transaction Laundering → processes for **John Smith** (the network PEP).

The other three typologies fuse as honest correspondent-banking subgraphs and can bridge via
new banks shared across BA typologies (e.g. Continental Correspondent Bank appears in BA004,
BA005, BA006 and BA008).

---

## Enterprise Standard Requirements

Every Correspondent Banking Analytics analytic should include (mirroring the fc-04 TBML001 /
fc-05 SAN003 pattern):

- Typology definition (`typologies/`)
- Enterprise diagram (`diagrams/`)
- Exposure scoring framework (`scoring-models/specific/`)
- Python engine package (`python/specific/<ID>/`): risk model, scenario callable,
  `schema.json`, generated sample data (>= 20 real-named rows per component), `expected_outputs/`,
  and executable tests
- Investigator playbook (`operations/specific/`, where applicable)
- Intelligence products (`intelligence-products/specific/<ID>/`)
- Data requirements & schema design
- Model governance linkage

Each engine is built and tested **standalone** in this repository before it is put through the
FC-10 governed runtime, where a thin adapter delegates to it.
