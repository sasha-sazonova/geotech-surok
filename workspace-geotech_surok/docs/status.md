# Status — 24.10.2026

## What exists

| Area | State |
|---|---|
| Engineering specification | v1.6, versioned, change log in appendix 13.6 |
| Compute contour `geotech-base` | Linux node: 105 packages, import test 21/21, freeze recorded |
| Pile contour `piles-py310` | separate environment: OpenPile requires Python 3.8–3.10 |
| Async jobs protocol | runner v2: per-job timeout, stdout capture, retention, SHA-256 manifests |
| Agent | live on OpenClaw: persona, workspace, memory discipline; 6/6 acceptance checks passed |
| Calculation code | `calc/d1_foundation` (bearing resistance + settlement) and `calc/d2_pile` (lateral pile) |
| Reference case D1 v2 | protocol + traceability table + two independent implementations, divergence 0.0% |
| Document layer | pandoc + TeX for protocols and reports |
| License audit | 105 packages checked; GPL/LGPL classified; one GPL package (`groundhog`), no blockers for internal use |
| Package registry | `envs/packages.csv`: 105 rows with version, licence, PyPI and repository links |

## D1 benchmark result (v2, 23.10.2026)

| Check | Value | Criterion | Status |
|---|---|---|---|
| `p ≤ R` | p = 286.0 kPa, R = 217.42 kPa | p ≤ R | **fails** (31.5% over) |
| `s ≤ su` | s ≥ 4.43 cm (lower bound) | su = 10 cm | **not determined** — compressible layer truncated at 4.0 m |
| Two implementations | deviation 0.0% | ≤ 5% | passes |

The benchmark deliberately returns a failing check and an undetermined one — that is the intended
behaviour, not a defect.

## What is next

1. D2 pile protocol: complete the cross-check against an independent solution and record limits.
2. Normative-layer contour for report packages (WeasyPrint / python-docx / pandoc).
3. Field/lab data pipeline (AGS4/GEF) wired to the D1 parameter passport.
4. Review of `groundhog` (GPL) isolation before any commercial packaging.

## Known limits

- Heavy FEM solvers (Code_Aster/MOOSE/OGS/XC) are not runnable on the current hardware.
- The second batch of geotechnical packages (mesh, point clouds, seismology) is not installed yet.
- Everything normative must be re-verified against official editions before production use.
