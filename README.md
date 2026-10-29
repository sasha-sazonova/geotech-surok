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
├── calc/           calculation code: D1 foundation (R, settlement), D2 lateral pile
├── scenarios/      scenario cards in YAML with limits and assumptions
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

Spec **v1.6** · compute contour: 105 packages, import test 21/21, freeze recorded · async runner **v2** ·
live agent passed **6/6** acceptance checks including the anti-fallback trap.

**D1** — shallow foundation (coefficients re-verified against the official text of СП 22.13330.2016):
`p = 286.0 kPa` vs `R = 215.62 kPa` → check **fails** (+32.6 %);
settlement `s = 4.232 cm` vs `su = 10 cm` → **passes** (Hc = 3.6 m, п.5.6.41). A resized 2.4×2.8 m
footing passes bearing with a 1.9 % margin (`R = 218.82`, `p = 214.57` kPa).
**D2** — lateral pile (openpile 1.0.3): at H = 500 kN, y = 6.3 / 19.3 mm and Mmax = 890.5 / 1389 kNm
for the two stiffness calibrations; the СП 24.13330 route remains “not determined”.
Verification: manual reference (`docs/manual-check-d1.md`), 16 tests, traceability validator — CI green.

## License

Documentation and presentations: Apache-2.0 (see `LICENSE`, `NOTICE`).
Referenced open-source tools and normative documents remain with their respective authors;
normative texts are not included.

## Verification

The calculation core is covered by a verifiable chain: `traceability.yml` links every normative
clause (document → edition → clause → formula) to code symbols and tests; the validator fails the
build on orphan clauses, unreferenced tests, or a "verified" status without a dated source.

```bash
make verify (Python ≥ 3.10 required — Pint 0.24.4 has no py3.9 wheel)            # traceability validator + pytest
make regen             # regenerate golden files (only when results intentionally change)
docker build -t geotech-surok .   # clean-machine run of the same checks
```

Evidence today:

| Item | State |
|---|---|
| Manual independent calculation (R = 215.62 kPa; s = 4.232 cm) | `docs/manual-check-d1.md`, pinned by `test_manual_reference` |
| Normative text verified (СП 22.13330.2016, п.5.6.7/5.6.10/5.6.31/5.6.32/5.6.41, табл.5.4/5.5/5.8, прил.Г) | `docs/norm-sources/sp22-2016.md` |
| Golden / property / step / units / negative tests | `tests/` |
| Commercial-core cross-check | **cancelled** by owner; oracle stack = manual closed form + second implementation + cross-tool |
