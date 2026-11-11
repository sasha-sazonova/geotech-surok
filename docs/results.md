# Results — D1 / D2 (verified subset)

## D1 — shallow foundation (СП 22.13330.2016)

Inputs: b×l = 2.0×2.4 m, d = 1.8 m, N = 1200 kN; clayey loam φ = 16°, c = 18 kPa,
γ = 18.5 kN/m³, E = 9 MPa; fill above base γ′ = 17.5 kN/m³; water table 3.2 m.

Normative coefficients re-verified against the official text (PDF, 228 pp.):
γc1 = 1.2 (table 5.4, 0.25 < IL < 0.5), γc2 = 1.0 (L/H ≥ 4), κ = 1.0, Mγ/Mq/Mc = 0.36/2.43/4.99
(table 5.5, φ = 16°), γII averaged over b/2 (clause 5.6.10), α from table 5.8, σzp = α·p
(clause 5.6.32, eq. 5.17), β = 0.8 (clause 5.6.31, eq. 5.16), Hc per clause 5.6.41.

| Check | Value | Criterion | Status |
|---|---|---|---|
| p ≤ R | 286.0 vs 215.62 kPa | p ≤ R | **fails** (+32.6 %) |
| s ≤ su | 4.232 cm (Hc = 3.6 m) | su = 10 cm | **passes** |

Resized footing 2.4×2.8 m: R = 218.82 kPa, p = 214.57 kPa (passes, 1.9 % margin); s = 3.595 cm.

Independent hand calculation: `docs/manual-check-d1.md`; pinned by
`tests/test_manual_reference.py::test_manual_reference_matches`.

## D2 — lateral pile (openpile 1.0.3 + independent FEM)

Steel pipe D = 1.2 m, t = 22 mm, L = 24 m; sand φ = 35°, water table −3 m; free head, H = 500 kN.

| Model | y at head, mm | Mmax, kN·m |
|---|---|---|
| openpile, API sand, default stiffness | 6.275 | −890.5 |
| openpile, API sand, k = 5000 kN/m³ | 19.335 | −1389.0 |
| **Independent FEM, same API p-y** (this repo, `calc/d2_pile.py`) | **6.556** | **980.4** |
| Dunkirk model (Dr = 75 %, G0 = 80 MPa), valid range D = 2.0 m / L = 12 m | 1.961 | −1009.9 |

### Cross-check (closed 2026-11-11)

Two-level verification, both levels reproducible:

1. **Solver vs exact theory.** For a constant subgrade modulus the finite-element solution
   reproduces the closed-form semi-infinite beam: `y0 = 2Hλ/K`, `Mmax = 0.3224·H/λ` —
   agreement **0.09 %** on deflection and **0.1 %** on moment at n = 160.
2. **Independent implementation vs openpile.** Same API sand p-y curve, different solver:
   **+4.5 %** on head deflection (6.556 vs 6.275 mm) and **+10.1 %** on moment
   (980.4 vs 890.5 kN·m). Declared tolerance: ±8 % / ±12 %; difference traced to the details
   of the p-y implementation (A-factor and initial stiffness), not to a modelling error.

Dunkirk differs by 2.2–3.6× — that is a **different soil model with its own calibration**,
not a contradiction; it is used only as an order-of-magnitude reference and only inside its
stated validity range (D ≈ 2 m, L = 12 m).

### Statuses, stated explicitly

| Status | What it means here |
|---|---|
| calculation done | openpile run and independent FEM run, both reproducible |
| cross-check done | solver validated against exact theory (0.1 %) and against openpile (+4.5 % / +10.1 %) |
| normative route | **not determined, by design** — СП 24.13330.2021 regulates axial capacity and settlement of piles and does not define a p-y procedure for lateral load. Lateral analysis rests on the API/Reese engineering method, which is not a СП clause. This is a scope statement, not an unfinished item: a number labelled «по СП 24» here would be a false attribution. |

## Verification

`make verify` — traceability validator + 179 tests; `docker build` runs the same checks.
Any "verified" clause without a dated normative source fails the validator.
