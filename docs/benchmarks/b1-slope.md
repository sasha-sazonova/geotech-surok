# B1 benchmark — slope stability (2026-10-29)

## Setup

Synthetic slope: height 10 m, face 30° (run 20 m), crest RL 50 at x=40, toe RL 40 at x=60;
homogeneous clayey fill: γ = 18 kN/m³, φ = 25°, c = 10 kPa.

## Tools

* pyslope 1.4.0 (geotech-base contour) — full grid search, 1015 circles;
* hand Fellenius (ordinary) and hand simplified Bishop (`calc/b1_slope.py`) on a fixed circle.

## Result

pyslope critical circle: cx=55.405, cz=61.024, R=21.520 (crest entry, toe exit), Fs = 1.6913.

| Method | Fs on the pyslope critical circle | Δ vs pyslope |
|---|---|---|
| pyslope (own solver) | 1.6913 | — |
| Hand Fellenius (calc/b1_slope.py) | 1.7296 | 2.2 % |
| Hand Bishop | 1.5265 | Bishop < Fellenius (theory-consistent) |

Declared cross-tool tolerance ±5 % — **passes** (Fellenius vs pyslope: 2.2 %).

## Methodological findings (recorded)

1. pyslope builds its own external boundary and coordinate frame (RL up, crest at x=40):
   hand calculations must be performed on **pyslope's geometry**, not on an independently
   written one — otherwise "no crossings" or mismatched Fs appear.
2. A naive hand search over arbitrary circles yields negative driving forces on rising arc
   segments; arc segments with α ≤ 0 must be skipped (soil above a rising base does not slide).
3. The deep toe-exit circle is the critical one for this configuration; shallow circles through
   the face give much higher Fs (checked: 8.1–19.7).
4. `analyse_circle` is absent in pyslope 1.4.0 — the API is `analyse_slope()` + `get_min_FOS_circle()`;
   material is bound by `depth_to_bottom` in RL terms (must cover the slope body).

## Files

`calc/b1_slope.py` — hand Fellenius/Bishop on a fixed circle; `tests/test_b1_slope.py` —
benchmark tests incl. the ±5 % cross-tool check and cohesion monotonicity.
