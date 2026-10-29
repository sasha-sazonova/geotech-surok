# B3 benchmark — axial pile, API unit formulas (2026-10-29)

## Setup

Steel pipe D = 1.2 m (t = 22 mm), L = 24 m, plugged; sand φ = 35°, γ = 18 kN/m³,
water table −3 m; δ = 30° (steel), K = 0.8.

## Method

openpile 1.0.3 `API_sand_axial.unit_shaft_friction / unit_tip_resistance`
vs hand API RP2A formulas f = K·σv′·tanδ, σv′ by geostatics; tip Nq = 40.

## Result (jobs b3-axial-003)

| z, m | f hand, kPa | f openpile, kPa | dev |
|---|---|---|---|
| 1 | 8.31 | 8.31 | 0.0 % |
| 3 | 24.94 | 24.94 | 0.0 % |
| 5 | 32.51 | 32.51 | 0.0 % |
| 10 | 51.42 | 51.42 | 0.0 % |
| 15 | 70.34 | 70.34 | 0.0 % |
| 20 | 89.25 | 89.25 | 0.0 % |
| 23 | 100.60 | 95.70 | −4.87 % (built-in API fmax cap) |

Tip: qp = 9039.6 kPa — exact match with Nq(40)·σv′(24 m).

Max deviation 4.87 % ≤ 5 % — **passes**. The deviation near the tip is the built-in API
fmax limit, i.e. part of the method, documented upstream.

## Notes

* openpile does not compute a total capacity Q directly — it builds t-z/Q-z springs for
  settlement analysis; capacity-type results above are the hand reference pinned for testing.
* SP 24.13330 normative route remains **not determined** (strategic gap).
