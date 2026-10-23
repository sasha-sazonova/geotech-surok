# Status — 2026-10-23

## What exists

| Area | State |
|---|---|
| Engineering specification | v1.6, versioned, change log in appendix 13.6 |
| Compute contour `geotech-base` | installed on a Linux node: 105 packages, import test 21/21, freeze recorded |
| Async jobs protocol | runner v2: per-job timeout, stdout capture, retention, SHA-256 manifests |
| Agent | live on OpenClaw: persona, workspace, memory discipline; 6/6 acceptance checks passed |
| Document layer | pandoc + TeX for protocols and reports |
| License audit | 105 packages checked; GPL/LGPL classified; no blockers for internal use |

## What is next

1. **D1 benchmark** — shallow foundations: bearing resistance `R` and settlement by СП 22.13330,
   traceability table, honest “not determined” statuses.
2. Pile contour (SP 24.13330) and normative-layer contour (report packages).
3. Field/lab data pipeline (AGS4/GEF) and cross-tool verification.

## Known limits

- Heavy FEM solvers (Code_Aster/MOOSE/OGS/XC) are not runnable on the current hardware;
  they require a dedicated compute host or containers.
- The second batch of geotechnical packages (mesh, point clouds, seismology) is not installed yet.
- Everything normative must be re-verified against official editions before production use.
