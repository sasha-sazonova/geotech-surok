# Status — 2026-10-24

## What exists

| Area | State |
|---|---|
| Engineering specification | v1.6, versioned, change log in appendix 13.6 |
| Compute contour `geotech-base` | Linux node: 105 packages, import test 21/21, freeze recorded |
| Pile contour `piles-py310` | separate environment (micromamba, Python 3.10.22, openpile 1.0.3) |
| Async jobs protocol | runner v2.1: per-job timeout, stdout capture, retention, SHA-256 manifests |
| Agent | live on OpenClaw: persona, workspace, memory discipline; 6/6 acceptance checks passed |
| Calculation code (canonical) | repo root `calc/d1_foundation.py` — verified D1 core; `calc/d2_pile/task.py` — pile benchmark |
| Reference case D1 (verified) | manual check + golden/property/step/units/negative tests; CI green |
| Document layer | pandoc + TeX for protocols and reports |
| License audit | 105 packages checked; GPL/LGPL classified; `groundhog` GPL — internal use only |

## D1 benchmark result (verified against the official СП text)

b×l = 2.0×2.4 m, d = 1.8 m, N = 1200 kN; clayey loam φ=16°, c=18 kPa, γ=18.5 kN/m³, E=9 MPa;
γc1=1.2, γc2=1.0, κ=1.0; α — table 5.8; σzp = α·p; β=0.8.

| Check | Value | Criterion | Status |
|---|---|---|---|
| `p ≤ R` | p = 286.0 kPa, R = 215.62 kPa | p ≤ R | **fails** (+32.6 %) |
| `s ≤ su` | s = 4.232 cm (Hc = 3.6 m) | su = 10 cm (app. G, table G.1) | **passes** |
| Resized 2.4×2.8 m | R = 218.82, p = 214.57 kPa; s = 3.595 cm | p ≤ R; s ≤ 10 cm | **passes** (1.9 % margin) |

## What is next

1. Commercial-core cross-check (±5 %): GEO5 / PLAXIS / Rocscience / ISSMGE — no licensed access yet.
2. Normative-layer contour for report packages (WeasyPrint / python-docx / pandoc).
3. Field/lab data pipeline (AGS4/GEF) wired to the D1 parameter passport.
4. `groundhog` (GPL) isolation decision before any commercial packaging.

## Known limits

- Settlement for d ≥ 5 m requires the σzγ term (п.5.6.34) — the code refuses.
- Rows 38/43 of table 5.5 restored by interpolation (OCR damage), flagged in docs/norm-sources.
- SP 24.13330 normative route for piles is absent in OSS.
- Heavy FEM solvers (Code_Aster/MOOSE/OGS/XC) are not runnable on the current hardware.
