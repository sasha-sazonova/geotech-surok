# Surok — geotechnical agent with a traceable normative chain

[![verify](https://github.com/sasha-sazonova/geotech-surok/actions/workflows/verify.yml/badge.svg)](https://github.com/sasha-sazonova/geotech-surok/actions/workflows/verify.yml)

**A calculation is only worth something if it can be checked.** Surok prepares, runs and verifies
geotechnical calculations over open-source solvers, wrapping every number in the chain
`data → clause → formula → implementation → test → report`, and treats **“not determined”**
as a first-class result.

- Landing: <https://sasha-sazonova.github.io/geotech-surok/>
- Presentation: [EN](https://sasha-sazonova.github.io/geotech-surok/presentation/en/) · [RU](https://sasha-sazonova.github.io/geotech-surok/presentation/ru/)
- Specification: [TZ v1.6](https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/docs/TZ-geotech-surok.md)

## What it is for

| Problem | What the agent does |
|---|---|
| Calculations live in proprietary silos; the report is retyped by hand | keeps a normative registry with editions, amendments and check dates |
| Expert review asks for provenance and gets a screenshot | builds a traceability table from source data to the clause |
| A missing check silently becomes a green tick | returns “not determined” and stops instead of guessing |
| Results cannot be reproduced | runs in frozen environments with checksums and a job journal |

The agent prepares, calculates and checks. A specialist signs and releases.

## Install in four commands

```bash
git clone https://github.com/sasha-sazonova/geotech-surok.git
cd geotech-surok
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.lock
make verify        # expect: TRACEABILITY: OK + 78 passed
make quickstart    # first calculation (SP 22.13330.2016)
```

Only Python >= 3.9 and git are required. Docker, Windows notes and troubleshooting —
[INSTALL.en.md](INSTALL.en.md). Verified on a clean machine: 27 s install, 78 tests pass.

## How to use

1. **Brief** — object, design stage, what to calculate and to which code.
2. **Data** — investigation report, GEF/CPT, AGS4, boreholes, SPT, groundwater, loads, geometry.
3. **Calculation** — route from the registry, frozen environment, cross-tool verification.
4. **Report** — formulas with substituted numbers, check statuses, limits, traceability table.

If input data is missing, the agent produces a question list and stops until it is answered.

## Repository map

```
workspace-geotech_surok/          the agent workspace (mirrors the live one)
├── AGENTS.md SOUL.md IDENTITY.md TOOLS.md DESCRIPTION.md USER.md
├── norms/          normative registry: 9 confirmed, 11 queued, registry.csv
├── methods/        modules, verification levels, acceptance rules
├── workflows/      P-1 investigation, P-2 slopes, P-3 piles, P-4 reports, jobs protocol
├── tools/          67 OSS tools + 13-class coverage map + licence policy
├── calc/           calculation code: d1_foundation (R, settlement, tilt), b1_slope,
│                   sp24_piles, sp24_group, sp24_csp
├── scenarios/      YAML scenarios for calculation without coding
├── examples/       quickstart_d1.py — calculation with a "your data" block
├── tests/          150 tests: golden, property-based, dimensional, negative, SP 24
├── procedures/     calculation status policy and acceptance checklist
├── envs/           contour freezes + packages.csv (105 packages, licences, links)
├── reports/        protocols and traceability tables per revision
└── docs/           TZ v1.6, competitor analysis, status
presentation/       ru/ and en/ decks (purpose, usage, architecture, evidence)
index.html          bilingual landing page (GitHub Pages root)
```

| Section | Link |
|---|---|
| Agent workspace | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok> |
| Normative registry | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/norms> |
| Methods | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/methods> |
| Workflows | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/workflows> |
| Tools | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/tools> |
| Calculation code | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/calc> |
| Environments and packages | <https://github.com/sasha-sazonova/geotech-surok/tree/main/workspace-geotech_surok/envs> |
| D1 protocol | <https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/reports/d1-foundation-v2/protocol.md> |
| Status | <https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/docs/status.md> |
| Competitor analysis | <https://github.com/sasha-sazonova/geotech-surok/blob/main/workspace-geotech_surok/docs/competitor-analysis.md> |
| What we can do (EN) | <https://sasha-sazonova.github.io/geotech-surok/coverage/en/> |

## Design pillars

1. **Traceability** — every number resolves to a clause, an edition and a tool version.
2. **Honest statuses** — implemented / reproduced / normative route verified / not determined.
3. **Reproducibility by contract** — frozen environments, recorded host, SHA-256 checksums.
4. **Async compute** — job directory with input, status and output; three retries, then an honest “no result”.
5. **Human in the loop** — the agent prepares; a specialist signs.

## Status

Spec **v1.6** · compute contour: 105 packages, import test 21/21, freeze recorded ·
runner **v3** (contour preflight + health monitoring) · agent passed **6/6** acceptance checks.

**What is computed today** (all pinned by tests — 150 tests, traceability 26 clauses / 120 tests):

| Block | Norm | Implemented | Key numbers |
|---|---|---|---|
| **D1 — shallow foundation** | SP 22.13330.2016 | R by (5.7); settlement by (5.16) with both terms including `d ≥ 5 m`; formula (5.19) for `p ≤ σzg,0`; compressible-thickness extension for a layer with `E ≤ 7 MPa` (5.6.41); **tilt** by (5.24)–(5.26) with tables 5.9/5.10 | p = 286.0 vs R = 215.62 kPa → fails (+32.6 %); s = 4.232 cm ≤ 10 cm; Hc = 3.6 m; 2.4×2.8 m footing: R = 218.82, p = 214.57, s = 3.595 |
| **D2 — laterally loaded pile** | openpile 1.0.3 (p-y) | two-layer model, two stiffness calibrations | H = 500 kN: y = 6.3 / 19.3 mm, Mmax = 890.5 / 1389 kNm |
| **SP 24 — bearing capacity** | SP 24.13330.2021 | end-bearing piles (7.5–7.8); driven piles (7.9) with **table 7.2 in full** (sands and clays IL 0.1…0.6) plus tables 7.3/7.4; pull-out (7.11); bored piles (7.13) with table 7.6 | example: medium sand at d = 10 m → R = 5000 kPa; clay IL = 0.1 at d = 10 m → R = 7300 kPa |
| **SP 24 — pile settlement** | SP 24.13330.2021 | single pile (7.34–7.39, table 7.18, both κ branches); interaction (7.40–7.42); group n ≤ 25 with flexible and rigid cap | δ = 0.17·ln(x)/x — maximum at x = e (a property of the norm) |
| **SP 24 — pile field** | SP 24.13330.2021 | fictitious footing (7.45–7.49): `sef` via SP 22 + punch Δsp + shaft compression Δsc; boundaries per 7.4.9 | — |
| **SP 24 — combined pile-raft (CSP)** | SP 24.13330.2021 | combined stiffness per 7.4.18/7.4.8; nonlinear pile stiffness (7.44); plate subgrade reaction (7.4.20); load split with three checks | 25 piles, Nd = 20 MN → settlement ≈ 5 mm, 96 % carried by piles |
| **Slope stability — LEM** | limit equilibrium methods (not a norm clause) | 7 methods: OMS/Fellenius, Bishop, Janbu, Corps, Lowe–Karafiath, Spencer, Morgenstern–Price; automatic critical-circle search (xslope 1.0.7 engine, Apache-2.0) | on the B1 circle: OMS 1.590, Bishop 1.692, spread across 7 methods 0.147 |
| **Earth pressure and retaining walls** | SP 22.13330.2016 / SP 542.1325800.2024 (partial) | K_a/K_p Rankine, Coulomb K_a, diagram with water table and surcharge, tension crack, sliding/overturning factors, edge pressures, Blum sheet pile | Ka and Ea cross-checked against geoeq: ΔKa 0.001 %, ΔEa 0.0 % |

**Cross-tool benchmarks:** B1 slope (our Fellenius/Bishop vs the xslope engine — agreement ≤0.02 %; the earlier pyslope "2.2 %" claim is withdrawn as a false green status),
B2 table 5.8 vs exact Boussinesq (table is conservative by 3–32 %),
B3 axial pile (API unit formulas vs hand calculation — 0.0 %).

**Deliberately not computed** (returns "not determined", never a guess): edge pressures under moment;
piles in soils where the printed norm shows a dash in the table; CSP edge effects; numerical methods
7.4.13 and 7.5; negative friction.

Verification: manual reference (`docs/manual-check-d1.md`), **150 tests**, traceability validator
(26 clauses, 120 tests) — CI green (verify + docker). Full SP 24 coverage matrix:
[`docs/sp24-coverage.md`](docs/sp24-coverage.md).

### Quick start

```bash
make verify      # traceability + tests
make quickstart  # D1 calculation with default data
make scenario    # calculation from a YAML scenario (no coding)
```

## License

Documentation and presentations: Apache-2.0 (see `LICENSE`, `NOTICE`).
Referenced open-source tools and normative documents remain with their respective authors;
normative texts are not included.

## Verification

The calculation core is covered by a verifiable chain: `traceability.yml` links every normative
clause (document → edition → clause → formula) to code symbols and tests; the validator fails the
build on orphan clauses, unreferenced tests, or a "verified" status without a dated source.

```bash
make verify      # traceability validator + pytest (Python >= 3.9)
make regen       # regenerate golden files (only when results intentionally change)
make quickstart  # first calculation: examples/quickstart_d1.py
docker build -t geotech-surok . && docker run --rm geotech-surok   # clean-machine run of the same checks
```

Step-by-step install from scratch — [INSTALL.en.md](INSTALL.en.md).

Evidence today:

| Item | State |
|---|---|
| Manual independent calculation (R = 215.62 kPa; s = 4.232 cm) | `docs/manual-check-d1.md`, pinned by `test_manual_reference` |
| Normative text verified (СП 22.13330.2016, п.5.6.7/5.6.10/5.6.31/5.6.32/5.6.41, табл.5.4/5.5/5.8, прил.Г) | `docs/norm-sources/sp22-2016.md` |
| Golden / property / step / units / negative tests | `tests/` |
| Commercial-core cross-check | **cancelled** by owner; oracle stack = manual closed form + second implementation + cross-tool |
