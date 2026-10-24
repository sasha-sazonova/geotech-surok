# -*- coding: utf-8 -*-
"""D1 — shallow foundation: bearing resistance R and settlement s.

Normative basis (verified against the official text of СП 22.13330.2016;
see docs/norm-sources/sp22-2016.md for pages and retrieval date):

* п.5.6.7, formula (5.7) — design bearing resistance R;
* табл. 5.4 — γc1, γc2;
* табл. 5.5 — Mγ, Mq, Mc;
* п.5.6.10 — averaging of γ below the footing over z = b/2 (b < 10 m);
* п.5.6.31, formula (5.16) — settlement by layer summation, β = 0.8,
  layer thickness ≤ 0.4·b (second term σzγ may be omitted for d < 5 m, п.5.6.34);
* п.5.6.32, formula (5.17), табл. 5.8 — σzp = α·p;
* п.5.6.41 — lower boundary of the compressible thickness σzp ≈ 0.5·σzg,
  Hc ≥ b/2 for b < 10 m;
* прил. Г, табл. Г.1, п.1 — su = 10 cm for industrial/civil buildings
  with a full reinforced-concrete frame.

Units: kN, m, kPa. The module uses plain floats; dimensional checks are done
in tests/test_units.py with pint.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

GAMMA_W = 9.81  # kN/m3, water unit weight

# --- табл. 5.5 (Mγ, Mq, Mc). Rows 38 and 43 were restored by linear
# interpolation between verified neighbours because of OCR damage in the
# source PDF; they are flagged in docs/norm-sources/sp22-2016.md.
M_TABLE: Dict[int, Tuple[float, float, float]] = {
    0: (0.00, 1.00, 3.14), 1: (0.01, 1.06, 3.23), 2: (0.03, 1.12, 3.32),
    3: (0.04, 1.18, 3.41), 4: (0.06, 1.25, 3.51), 5: (0.08, 1.32, 3.61),
    6: (0.10, 1.39, 3.71), 7: (0.12, 1.47, 3.82), 8: (0.14, 1.55, 3.93),
    9: (0.16, 1.64, 4.05), 10: (0.18, 1.73, 4.17), 11: (0.21, 1.83, 4.29),
    12: (0.23, 1.94, 4.42), 13: (0.26, 2.05, 4.55), 14: (0.29, 2.17, 4.69),
    15: (0.32, 2.30, 4.84), 16: (0.36, 2.43, 4.99), 17: (0.39, 2.57, 5.15),
    18: (0.43, 2.73, 5.31), 19: (0.47, 2.89, 5.48), 20: (0.51, 3.06, 5.66),
    21: (0.56, 3.24, 5.84), 22: (0.61, 3.44, 6.04), 23: (0.66, 3.65, 6.24),
    24: (0.72, 3.87, 6.45), 25: (0.78, 4.11, 6.67), 26: (0.84, 4.37, 6.90),
    27: (0.91, 4.64, 7.14), 28: (0.98, 4.93, 7.40), 29: (1.06, 5.25, 7.67),
    30: (1.15, 5.59, 7.95), 31: (1.24, 5.95, 8.24), 32: (1.34, 6.34, 8.55),
    33: (1.44, 6.76, 8.88), 34: (1.55, 7.22, 9.22), 35: (1.68, 7.71, 9.58),
    36: (1.81, 8.24, 9.97), 37: (1.95, 8.81, 10.37), 38: (2.11, 9.44, 10.80),
    39: (2.28, 10.11, 11.25), 40: (2.46, 10.85, 11.73), 41: (2.66, 11.64, 12.24),
    42: (2.88, 12.51, 12.79), 43: (3.12, 13.46, 13.37), 44: (3.38, 14.50, 13.98),
    45: (3.66, 15.64, 14.64),
}

# --- табл. 5.8: α for ξ = 2z/b. Columns: η = l/b = 1.0, 1.4, 1.8, 2.4, 3.2, 5.0.
ALPHA_XI: Tuple[float, ...] = (0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2,
                               3.6, 4.0, 4.4, 4.8, 5.2, 5.6, 6.0, 6.4, 6.8, 7.2)
ALPHA_ETA: Tuple[float, ...] = (1.0, 1.4, 1.8, 2.4, 3.2, 5.0)
ALPHA_ROWS: Tuple[Tuple[float, ...], ...] = (
    (1.000, 1.000, 1.000, 1.000, 1.000, 1.000),
    (0.949, 0.960, 0.972, 0.975, 0.976, 0.977),
    (0.756, 0.800, 0.848, 0.866, 0.876, 0.879),
    (0.547, 0.606, 0.682, 0.717, 0.739, 0.749),
    (0.390, 0.449, 0.532, 0.578, 0.612, 0.629),
    (0.285, 0.336, 0.414, 0.463, 0.505, 0.530),
    (0.214, 0.257, 0.325, 0.374, 0.419, 0.449),
    (0.165, 0.201, 0.260, 0.304, 0.349, 0.383),
    (0.130, 0.160, 0.210, 0.251, 0.294, 0.329),
    (0.106, 0.131, 0.173, 0.209, 0.250, 0.285),
    (0.087, 0.108, 0.145, 0.176, 0.214, 0.248),
    (0.073, 0.091, 0.123, 0.150, 0.185, 0.218),
    (0.062, 0.077, 0.105, 0.130, 0.161, 0.192),
    (0.053, 0.067, 0.091, 0.113, 0.141, 0.170),
    (0.046, 0.058, 0.079, 0.099, 0.124, 0.152),
    (0.040, 0.051, 0.070, 0.087, 0.110, 0.136),
    (0.036, 0.045, 0.062, 0.077, 0.099, 0.122),
    (0.031, 0.040, 0.055, 0.069, 0.088, 0.110),
    (0.028, 0.036, 0.049, 0.062, 0.080, 0.100),
)


def _linear(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    if x1 == x0:
        return y0
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def M_coefficients(phi_deg: float) -> Tuple[float, float, float]:
    """Mγ, Mq, Mc from табл. 5.5 with linear interpolation."""
    if not (0.0 <= phi_deg <= 45.0):
        raise ValueError("phi outside table 5.5 range 0..45 deg")
    lo = int(phi_deg)
    hi = min(lo + 1, 45)
    f = phi_deg - lo
    a, b = M_TABLE[lo], M_TABLE[hi]
    return (_linear(f, 0, 1, a[0], b[0]),
            _linear(f, 0, 1, a[1], b[1]),
            _linear(f, 0, 1, a[2], b[2]))


def alpha_coeff(xi: float, eta: float) -> float:
    """α from табл. 5.8 for ξ = 2z/b and η = l/b (linear interpolation)."""
    if xi <= ALPHA_XI[0]:
        return 1.0
    if xi >= ALPHA_XI[-1]:
        row = ALPHA_ROWS[-1]
        return _interp_eta(row, eta)
    for i in range(len(ALPHA_XI) - 1):
        if ALPHA_XI[i] <= xi <= ALPHA_XI[i + 1]:
            f = (xi - ALPHA_XI[i]) / (ALPHA_XI[i + 1] - ALPHA_XI[i])
            r0, r1 = ALPHA_ROWS[i], ALPHA_ROWS[i + 1]
            v0 = _interp_eta(r0, eta)
            v1 = _interp_eta(r1, eta)
            return v0 + (v1 - v0) * f
    return _interp_eta(ALPHA_ROWS[-1], eta)


def _interp_eta(row: Sequence[float], eta: float) -> float:
    if eta <= ALPHA_ETA[0]:
        return row[0]
    if eta >= ALPHA_ETA[-1]:
        return row[-1]
    for j in range(len(ALPHA_ETA) - 1):
        if ALPHA_ETA[j] <= eta <= ALPHA_ETA[j + 1]:
            return _linear(eta, ALPHA_ETA[j], ALPHA_ETA[j + 1], row[j], row[j + 1])
    return row[-1]



def _gamma_integral(layer: Layer, lo: float, hi: float, water_line: float) -> float:
    """Integral of unit weight between depths lo..hi, splitting at the water table."""
    if hi <= lo:
        return 0.0
    wl_depth = -water_line
    cuts = [lo, hi]
    if lo < wl_depth < hi:
        cuts = [lo, wl_depth, hi]
    total = 0.0
    for a, b in zip(cuts[:-1], cuts[1:]):
        mid_depth = (a + b) / 2.0
        g = layer.gamma - GAMMA_W if mid_depth > wl_depth else layer.gamma
        total += g * (b - a)
    return total


@dataclass
class Layer:
    top: float          # elevation, m (negative down)
    bottom: float
    gamma: float        # total unit weight, kN/m3
    E_kpa: float

    @property
    def thickness(self) -> float:
        return self.top - self.bottom


def effective_gamma(layer: Layer, elevation_mid: float, water_line: float) -> float:
    """Total or submerged unit weight depending on the water table."""
    return layer.gamma - GAMMA_W if elevation_mid < water_line else layer.gamma


@dataclass
class D1Params:
    b: float = 2.0
    l: float = 2.4
    d: float = 1.8
    N: float = 1200.0
    gamma_f: float = 20.0
    phi_deg: float = 16.0
    c_kpa: float = 18.0
    gamma_c1: float = 1.2      # табл. 5.4, clayey 0.25 < IL < 0.5
    gamma_c2: float = 1.0      # табл. 5.4, L/H ≥ 4 or flexible scheme
    kappa: float = 1.0         # п.5.6.7: 1.0 if φ,c from direct tests
    kz: float = 1.0            # b < 10 m
    db: float = 0.0            # no basement
    gamma_above: float = 17.5  # unit weight above the base (planning fill), kN/m3
    water_line: float = -3.2   # elevation, m
    data_bottom: float = -5.8  # lowest known elevation
    su_cm: float = 10.0        # прил. Г, табл. Г.1, п.1 (RC frame)
    layers: List[Layer] = field(default_factory=lambda: [
        Layer(top=0.0, bottom=-1.8, gamma=17.5, E_kpa=9000.0),   # planning fill above the base
        Layer(top=-1.8, bottom=-5.8, gamma=18.5, E_kpa=9000.0), # ИГЭ-1 (clayey loam)
    ])
    moment_kNm: Optional[float] = None

    @property
    def A(self) -> float:
        return self.b * self.l

    def pressure_kpa(self) -> float:
        return self.N / self.A + self.gamma_f * self.d


def average_gamma_below(params: D1Params, depth: float) -> float:
    """п.5.6.10: average γ over z = b/2 below the footing (b < 10 m)."""
    z0, z1 = params.d, params.d + depth
    total, length = 0.0, z1 - z0
    for layer in params.layers:
        lo = max(z0, -layer.top)   # depth coordinates positive down
        hi = min(z1, -layer.bottom)
        if hi <= lo:
            continue
        total += _gamma_integral(layer, lo, hi, params.water_line)
    if length <= 0:
        raise ValueError("invalid averaging depth")
    return total / length


def average_gamma_above(params: D1Params) -> float:
    """γ' above the base; below the water table the submerged weight is used."""
    if params.d <= -params.water_line:
        return params.gamma_above
    above_wl = -params.water_line
    return ((params.gamma_above * above_wl
             + (params.gamma_above - GAMMA_W) * (params.d - above_wl)) / params.d)


def bearing_resistance(params: D1Params) -> Dict[str, float]:
    """R by п.5.6.7, formula (5.7)."""
    Mg, Mq, Mc = M_coefficients(params.phi_deg)
    gII = average_gamma_below(params, params.b / 2.0)
    gIIp = average_gamma_above(params)
    R = (params.gamma_c1 * params.gamma_c2 / params.kappa) * (
        Mg * params.kz * params.b * gII
        + Mq * gIIp * params.d
        + (Mq - 1.0) * params.db * gIIp
        + Mc * params.c_kpa
    )
    return {
        "R_kPa": R, "Mg": Mg, "Mq": Mq, "Mc": Mc,
        "gamma_II": gII, "gamma_IIp": gIIp,
    }


def sigma_zg(params: D1Params, z_below_base: float) -> float:
    """Vertical stress from self-weight at depth z below the footing base."""
    depth = params.d + z_below_base
    stress = 0.0
    remaining = depth
    for layer in sorted(params.layers, key=lambda L: -L.top):
        top_depth = -layer.top
        bottom_depth = -layer.bottom
        if bottom_depth <= 0:
            continue
        lo = max(0.0, top_depth)
        hi = min(depth, bottom_depth)
        if hi <= lo:
            continue
        stress += _gamma_integral(layer, lo, hi, params.water_line)
    # layers above the topmost known layer are not modelled
    return stress


def settlement(params: D1Params, h: Optional[float] = None) -> Dict[str, object]:
    """s by п.5.6.31 (5.16), σzp by п.5.6.32 (5.17), Hc by п.5.6.41."""
    p = params.pressure_kpa()
    if params.d >= 5.0:
        return {"status": "не определено (d ≥ 5 м: требуется учёт σzγ, п.5.6.34)",
                "s_cm": None, "Hc_m": None, "truncated": True}
    if params.data_bottom >= -params.d:
        return {"status": "не определено (нет данных о грунте ниже подошвы)",
                "s_cm": None, "Hc_m": None, "truncated": True}
    h = h if h is not None else min(0.4 * params.b, 0.4)
    eta = params.l / params.b
    beta = 0.8
    s = 0.0
    z = 0.0
    Hc = None
    z_max_data = -params.data_bottom - params.d  # available thickness below base
    while z < z_max_data - 1e-9:
        z_next = min(z + h, z_max_data)
        dz = z_next - z
        zm = z + dz / 2.0
        sp = alpha_coeff(2.0 * zm / params.b, eta) * p
        E = _E_at(params, params.d + zm)
        s += beta * sp * dz / E
        sg = sigma_zg(params, z_next)
        if sp <= 0.5 * sg:
            Hc = z_next
            break
        z = z_next
    if Hc is None:
        return {"status": "не определено (граница сжимаемой толщи вне данных)",
                "s_cm": s * 100.0, "Hc_m": None, "truncated": True}
    Hc = max(Hc, params.b / 2.0)
    # п.5.6.41: if the layer below Hc has E < 7 MPa, extend to 0.2·σzg
    below = params.d + Hc + 1e-9
    E_below = _E_at(params, below)
    if E_below < 7000.0:
        return {"status": "не определено (ниже Hc слой E < 7 МПа: правило 5.6.41 требует расширения толщи)",
                "s_cm": s * 100.0, "Hc_m": Hc, "truncated": False}
    s_cm = s * 100.0
    status = "выполняется" if s_cm <= params.su_cm else "не выполняется"
    return {"status": status, "s_cm": s_cm, "Hc_m": Hc, "truncated": False}


def _E_at(params: D1Params, depth: float) -> float:
    elevation = -depth
    for layer in params.layers:
        if layer.bottom <= elevation <= layer.top:
            return layer.E_kpa
    return params.layers[-1].E_kpa


def analyze(params: D1Params) -> Dict[str, object]:
    """Full D1 check with explicit statuses and refusals."""
    refusals: List[str] = []
    checks: List[Dict[str, object]] = []
    if params.moment_kNm not in (None, 0, 0.0):
        refusals.append("крен/краевые давления: момент задан, проверка не реализована")
    if params.data_bottom >= -params.d:
        refusals.append("нет данных о грунте ниже подошвы")
    R = bearing_resistance(params)
    p = params.pressure_kpa()
    checks.append({
        "id": "p_le_R", "clause": "СП 22.13330.2016, п.5.6.7, ф.(5.7)",
        "value": p, "criterion": R["R_kPa"],
        "status": "выполняется" if p <= R["R_kPa"] else "не выполняется",
    })
    sres = settlement(params)
    checks.append({
        "id": "s_le_su", "clause": "СП 22.13330.2016, п.5.6.31, ф.(5.16); п.5.6.41; прил. Г, табл. Г.1",
        "value": sres.get("s_cm"), "criterion": params.su_cm,
        "status": sres["status"],
    })
    return {
        "R_kPa": round(R["R_kPa"], 2), "p_kPa": round(p, 2),
        "Mg": round(R["Mg"], 3), "Mq": round(R["Mq"], 3), "Mc": round(R["Mc"], 3),
        "gamma_II": round(R["gamma_II"], 3), "gamma_IIp": round(R["gamma_IIp"], 3),
        "settlement": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in sres.items()},
        "checks": checks, "refusals": refusals,
    }
