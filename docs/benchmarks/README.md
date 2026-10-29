# External oracles for benchmarks (2026-10-29)

## Decision

Commercial-core cross-check (GEO5 / PLAXIS / Rocscience, ±5 %) is **cancelled** by the owner
(2026-10-29): no licensed access is planned. It is recorded in `traceability.yml` as
`status: cancelled`, not as a green check.

## Oracle stack that replaces it

| Oracle | Applied to | Tolerance | Status |
|---|---|---|---|
| Manual closed-form calculation, pinned by a test | D1 (R, s) | exact match | verified (`docs/manual-check-d1.md`) |
| Independent second implementation (different code, same normative method) | D1 | ≤ 5 % | verified (0.0 %) |
| Cross-tool comparison on the same input (xslope/pyslope/openpile vs hand formulas) | B1 slope, B3 axial pile | method-dependent, declared per case | in progress |
| Published verification cases (ISSMGE etc., free sources only) | optional | ±5 % | not run — to be added only if a free authoritative case is found |
| Exact elastic closed forms (Boussinesq / angular points) | table 5.8 α | documented deviation | verified (table is conservative by 3–32 %, `docs/benchmarks/table-5.8-boussinesq.md`) |

## Rule

A benchmark passes only against a declared oracle with a declared tolerance. Silence or a
"plausible number" is not a pass; an oracle that cannot run is `cancelled`/`not_run`, never green.
