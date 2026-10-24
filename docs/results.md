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

## D2 — lateral pile (openpile 1.0.3, synthetic benchmark)

Steel pipe D = 1.2 m, t = 22 mm, L = 24 m; sand φ = 35°, water table −3 m; free head.

| Model | H = 500 kN: y, mm | Mmax, kN·m |
|---|---|---|
| API sand, default stiffness | 6.275 | −890.5 |
| API sand, k = 5000 kN/m³ | 19.335 | −1389.0 |
| Dunkirk (Dr = 75 %, G0 = 80 MPa), valid range D = 2.0 m / L = 12 m | 1.961 | −1009.9 |

Status: calculation done; linearity 5.00–5.21 at 5× load; Broms upper bound ≈ 12 000 kN;
СП 24.13330 normative route — **not determined** (no OSS implementation);
cross-model Dunkirk differs by 2.2–3.6× (different calibrations, one order of magnitude).

## Verification

`make verify` — traceability validator + 16 tests; `docker build` runs the same checks.
Any "verified" clause without a dated normative source fails the validator.
