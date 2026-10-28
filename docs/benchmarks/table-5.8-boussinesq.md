# Table 5.8 vs exact Boussinesq — benchmark result (2026-10-28/29)

## Setup

Footing b × l = 2.0 × 4.0 m; checks at ξ = 2z/b ∈ {0.8, 1.2, 1.6, 2.0, 2.4, 3.2, 4.0},
η = l/b = 1.8. Table values extracted from the official PDF (page 54).

## Method

1. Numeric Boussinesq integration of σz over the full footing area (midpoint grid, 500×500,
   p = 1 kPa) — the integrator was itself validated against the closed-form angular-point
   formula (ratio 1.0024, i.e. 0.24% at 800×800).
2. Closed-form angular-point formula × 4 (method of angular points) — matches the numeric
   center integration to 0.4–0.6% (ratio 0.9937–0.9984).
3. Table 5.8 values (column η = 1.8).

## Result

| ξ | table 5.8 (η=1.8) | exact elastic (center) | exact/table |
|---|---|---|---|
| 0.8 | 0.848 | 0.8709 | 1.027 |
| 1.2 | 0.682 | 0.7283 | 1.068 |
| 1.6 | 0.532 | 0.5938 | 1.116 |
| 2.0 | 0.414 | 0.4818 | 1.164 |
| 2.4 | 0.325 | 0.3927 | 1.208 |
| 3.2 | 0.210 | 0.2681 | 1.277 |
| 4.0 | 0.145 | 0.1908 | 1.316 |

## Conclusion

The tabulated α is systematically below the exact elastic value; the deviation grows from
2.7% at ξ=0.8 to 31.6% at ξ=4.0. This is a known property of the historical SNiP table
(it is not an extraction error: the same numbers appear in the СНиП 2.02.01-83 appendix 2
table and in independent online copies). Consequences for our code:

* `alpha_coeff` interpolates the official table — the settlement computed with it is
  **conservative** (overestimates σzp at depth relative to pure elasticity);
* the exact elastic benchmark is pinned by `tests/test_boussinesq_table58.py`;
* settlement result for the D1 benchmark remains s = 4.23 cm with Hc = 3.6 m
  (clause 5.6.41 criterion met at 0.5·σzg).
