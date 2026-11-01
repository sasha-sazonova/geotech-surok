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


class UnverifiedNormValue(ValueError):
    """A calculation would depend on a table cell that is not verified.

    Rows 38 and 43 of табл. 5.5 are damaged in the source PDF (the text layer
    shows «А Н .» and «ЗЛ2» instead of Mγ).  The Mγ values stored for those two
    rows are reconstructions, so any calculation that actually uses them must
    refuse instead of returning a plausible-looking number.
    """


class InsufficientData(ValueError):
    """The input does not describe the soil over the depth the norm requires."""


# Ячейки, которые нельзя использовать, пока они не подтверждены печатным оригиналом.
# 01.11.2026: строки 38 и 43 подтверждены по изображению печатного издания (с. 36–37):
# Mγ(38) = 2,11; Mγ(43) = 3,12. Механизм оставлен пустым как страховка для будущих изданий.
RESTORED_ROWS: Dict[int, str] = {}

# Происхождение значений, которые раньше были реконструкцией.
TABLE55_PROVENANCE: Dict[int, str] = {
    38: "печатное издание, с. 36: Mγ = 2,11 (подтверждено 2026-11-01)",
    43: "печатное издание, с. 37: Mγ = 3,12 (подтверждено 2026-11-01)",
}

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


# --- табл. 5.9: k_e для крена при внецентренной нагрузке (п.5.6.44)
TILT_ETA: Tuple[float, ...] = (1.0, 1.2, 1.5, 2.0, 3.0, 5.0, 10.0)
TILT_KE_LARGER: Tuple[float, ...] = (0.50, 0.57, 0.68, 0.82, 1.17, 1.42, 2.00)
TILT_KE_SMALLER: Tuple[float, ...] = (0.50, 0.43, 0.36, 0.28, 0.20, 0.12, 0.07)
TILT_KE_CIRCLE = 0.75

# --- табл. 5.10: коэффициент поперечной деформации ν (диапазоны)
POISSON_TABLE: Dict[str, Tuple[float, float]] = {
    "крупнообломочные": (0.27, 0.27),
    "пески и супеси": (0.30, 0.35),
    "суглинки": (0.35, 0.37),
    "глины IL<=0": (0.20, 0.30),
    "глины 0<IL<=0.25": (0.30, 0.38),
    "глины 0.25<IL<=1": (0.38, 0.45),
}


def tilt_ke(eta: float, along: str = "larger") -> float:
    """k_e по табл. 5.9; along = 'larger' | 'smaller' | 'circle'."""
    if along == "circle":
        return TILT_KE_CIRCLE
    row = TILT_KE_LARGER if along == "larger" else TILT_KE_SMALLER
    if eta <= TILT_ETA[0]:
        return row[0]
    if eta >= TILT_ETA[-1]:
        return row[-1]
    for i in range(len(TILT_ETA) - 1):
        if TILT_ETA[i] <= eta <= TILT_ETA[i + 1]:
            return _linear(eta, TILT_ETA[i], TILT_ETA[i + 1], row[i], row[i + 1])
    return row[-1]


def _linear(x: float, x0: float, x1: float, y0: float, y1: float) -> float:
    if x1 == x0:
        return y0
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def M_coefficients(phi_deg: float, allow_restored: bool = False) -> Tuple[float, float, float]:
    """Mγ, Mq, Mc from табл. 5.5 with linear interpolation.

    Raises UnverifiedNormValue when the interpolation actually uses row 38 or
    row 43, because Mγ in those rows is a reconstruction (see RESTORED_ROWS).
    Pass allow_restored=True only for sensitivity studies, never for a result.
    """
    if not (0.0 <= phi_deg <= 45.0):
        raise ValueError("phi outside table 5.5 range 0..45 deg")
    lo = int(phi_deg)
    hi = min(lo + 1, 45)
    f = phi_deg - lo
    used = [lo] if f == 0 else [lo, hi]
    bad = [row for row in used if row in RESTORED_ROWS]
    if bad and not allow_restored:
        detail = "; ".join(f"φ={row}: {RESTORED_ROWS[row]}" for row in bad)
        raise UnverifiedNormValue(
            "табл. 5.5: ячейка не подтверждена печатным оригиналом — " + detail)
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
    # E_e — модуль по ветви вторичного нагружения (п.5.6.31, ф.(5.16)).
    # При отсутствии опытных данных примечание 1 к 5.6.31 для категорий 1-2
    # допускает E_e ≈ 5·E; None означает именно это допущение.
    E_unload_kpa: Optional[float] = None

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
    kz: Optional[float] = None  # None → по п.5.6.7: 1 при b < 10 м, иначе z0/b + 0.2 (z0 = 8 м)
    db: float = 0.0            # no basement
    gamma_above: float = 17.5  # unit weight above the base (planning fill), kN/m3
    water_line: float = -3.2   # elevation, m
    data_bottom: float = -5.8  # lowest known elevation
    su_cm: float = 10.0        # прил. Г, табл. Г.1, п.1 (RC frame)
    # п.5.6.33: в расчёте σzγ берутся размеры в плане котлована, а не фундамента.
    pit_b: Optional[float] = None
    pit_l: Optional[float] = None
    layers: List[Layer] = field(default_factory=lambda: [
        Layer(top=0.0, bottom=-1.8, gamma=17.5, E_kpa=9000.0),   # planning fill above the base
        Layer(top=-1.8, bottom=-5.8, gamma=18.5, E_kpa=9000.0), # ИГЭ-1 (clayey loam)
    ])
    moment_kNm: Optional[float] = None
    moment_along: str = "larger"   # 'larger' | 'smaller' | 'circle' — табл. 5.9
    poisson: Optional[float] = None  # ν по табл. 5.10; без него крен не считается
    tilt_limit: Optional[float] = None  # предельный крен i_u, задаётся проектом

    def __post_init__(self) -> None:
        if self.b <= 0 or self.l <= 0:
            raise ValueError("b и l должны быть положительными")
        if self.d < 0:
            raise ValueError("d не может быть отрицательной")
        if self.water_line > 0:
            raise ValueError(
                "water_line — отметка УГВ в тех же координатах, что и подошва: "
                "0 = поверхность земли, отрицательные значения ниже. "
                f"Получено {self.water_line}; если УГВ выше поверхности, это уровень "
                "верховодки/подтопления — задайте 0.0 и опишите его отдельно")
        if self.data_bottom >= 0:
            raise ValueError("data_bottom — самая низкая известная отметка, должна быть < 0")

    @property
    def A(self) -> float:
        return self.b * self.l

    @property
    def kz_value(self) -> float:
        """п.5.6.7: kz = 1 при b < 10 м; kz = z0/b + 0.2 при b ≥ 10 м (z0 = 8 м)."""
        if self.kz is not None:
            return self.kz
        if self.b < 10.0:
            return 1.0
        return 8.0 / self.b + 0.2

    def pressure_kpa(self) -> float:
        return self.N / self.A + self.gamma_f * self.d


def average_gamma_below(params: D1Params, depth: float) -> float:
    """п.5.6.10: average γ over z = b/2 below the footing (b < 10 m).

    Raises InsufficientData when the layers do not cover the whole averaging depth:
    a missing layer must not be silently replaced by zero weight.
    """
    z0, z1 = params.d, params.d + depth
    total, length = 0.0, z1 - z0
    covered = 0.0
    for layer in params.layers:
        lo = max(z0, -layer.top)   # depth coordinates positive down
        hi = min(z1, -layer.bottom)
        if hi <= lo:
            continue
        covered += hi - lo
        total += _gamma_integral(layer, lo, hi, params.water_line)
    if length <= 0:
        raise ValueError("invalid averaging depth")
    if covered < length - 1e-9:
        raise InsufficientData(
            f"γII: слои покрывают {covered:.2f} м из {length:.2f} м (z = b/2 ниже подошвы); "
            "нужны данные о грунте на всю глубину осреднения")
    return total / length


def average_gamma_above(params: D1Params) -> float:
    """γ' above the base; below the water table the submerged weight is used."""
    if params.d <= -params.water_line:
        return params.gamma_above
    above_wl = -params.water_line
    return ((params.gamma_above * above_wl
             + (params.gamma_above - GAMMA_W) * (params.d - above_wl)) / params.d)


def sigma_zg0(params: D1Params) -> float:
    """σzg,0 — own-weight stress at the footing base (п.5.6.33, planning by cut)."""
    return average_gamma_above(params) * params.d


def _E_unload_at(params: D1Params, depth: float) -> float:
    """Модуль по ветви вторичного нагружения E_e для глубины depth (вниз от 0)."""
    elevation = -depth
    for layer in params.layers:
        if layer.bottom <= elevation <= layer.top:
            if layer.E_unload_kpa is not None:
                return layer.E_unload_kpa
            return 5.0 * layer.E_kpa  # примечание 1 к п.5.6.31
    last = params.layers[-1]
    return last.E_unload_kpa if last.E_unload_kpa is not None else 5.0 * last.E_kpa


def bearing_resistance(params: D1Params, allow_restored: bool = False) -> Dict[str, float]:
    """R by п.5.6.7, formula (5.7)."""
    Mg, Mq, Mc = M_coefficients(params.phi_deg, allow_restored=allow_restored)
    gII = average_gamma_below(params, params.b / 2.0)
    gIIp = average_gamma_above(params)
    R = (params.gamma_c1 * params.gamma_c2 / params.kappa) * (
        Mg * params.kz_value * params.b * gII
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


def settlement(params: D1Params, h: Optional[float] = None,
               include_unloading: Optional[bool] = None) -> Dict[str, object]:
    """s by п.5.6.31 (5.16), σzp by п.5.6.32 (5.17), σzγ by п.5.6.33 (5.18), Hc by п.5.6.41.

    Formula (5.16) has two terms:

        s = β · Σ [ σzp,i / E_i  −  σzγ,i / E_e,i ] · h_i

    where σzγ,i = α·σzg,0 (5.18) uses the plan dimensions of the PIT, not of
    the footing (п.5.6.33), and E_e is the secondary-loading modulus.
    Per п.5.6.34 the second term may be omitted for pits shallower than 5 m;
    that is the default behaviour here for d < 5 m, and omitting it for deeper
    pits is only allowed explicitly via include_unloading=False.
    """
    p = params.pressure_kpa()
    sg0 = sigma_zg0(params)
    if include_unloading is None:
        include_unloading = params.d >= 5.0
    if params.d >= 5.0 and not include_unloading:
        return {"status": "не определено (d ≥ 5 м: второе слагаемое σzγ по п.5.6.34 опускать нельзя)",
                "s_cm": None, "Hc_m": None, "truncated": True}
    if params.data_bottom >= -params.d:
        return {"status": "не определено (нет данных о грунте ниже подошвы)",
                "s_cm": None, "Hc_m": None, "truncated": True}
    # п.5.6.35: при p ≤ σzg,0 осадку считают по формуле (5.19) —
    # s = β·Σ σzp,i·h_i / E_e,i (модуль вторичного нагружения, без вычитания σzγ).
    unloading_from_excavation = p > sg0
    h = h if h is not None else min(0.4 * params.b, 0.4)
    eta = params.l / params.b
    pit_b = params.pit_b if params.pit_b else params.b
    pit_l = params.pit_l if params.pit_l else params.l
    eta_pit = pit_l / pit_b
    beta = 0.8
    s = 0.0
    history: List[Tuple[float, float]] = []  # (z_next, накопленная s)
    z = 0.0
    Hc = None
    z_max_data = -params.data_bottom - params.d  # available thickness below base
    # п.5.6.41: если граница толщи попадает в слой E ≤ 7 МПа (или такой слой лежит
    # сразу ниже Hc), этот слой включают в толщу, а Hc берут как минимум из подошвы
    # слоя и глубины, где σzp = 0.2·σzg.
    criterion = 0.5
    weak_bottom = None
    while z < z_max_data - 1e-9:
        z_next = min(z + h, z_max_data)
        dz = z_next - z
        zm = z + dz / 2.0
        sp = alpha_coeff(2.0 * zm / params.b, eta) * p
        E = _E_at(params, params.d + zm)
        if unloading_from_excavation:
            term = sp / E
            if include_unloading:
                sg_alpha = alpha_coeff(2.0 * zm / pit_b, eta_pit) * sg0
                term -= sg_alpha / _E_unload_at(params, params.d + zm)
        else:
            term = sp / _E_unload_at(params, params.d + zm)  # (5.19)
        s += beta * term * dz
        history.append((z_next, s))
        sg = sigma_zg(params, z_next)
        if sp <= criterion * sg:
            if criterion == 0.5:
                E_below = _E_at(params, params.d + z_next + 1e-9)
                if E_below <= 7000.0:
                    criterion = 0.2
                    weak_bottom = _layer_bottom_depth(params, params.d + z_next + 1e-9) - params.d
                    continue
            Hc = z_next
            break
        z = z_next
    if Hc is None:
        # п.5.6.41: подошва слабого слоя — законная граница толщи, если она в данных
        if weak_bottom is not None and weak_bottom <= z_max_data + 1e-9:
            Hc = weak_bottom
        else:
            return {"status": "не определено (граница сжимаемой толщи вне данных)",
                    "s_cm": s * 100.0, "Hc_m": None, "truncated": True}
    if weak_bottom is not None:
        Hc = min(Hc, weak_bottom)
    Hc = max(Hc, params.b / 2.0)
    # осадка считается только до Hc: сумма по шагам, попавшим в толщу
    s = next((val for z_end, val in history if z_end >= Hc - 1e-9), s)
    s_cm = s * 100.0
    status = "выполняется" if s_cm <= params.su_cm else "не выполняется"
    return {"status": status, "s_cm": s_cm, "Hc_m": Hc, "truncated": False,
            "unloading_included": include_unloading,
            "formula": "5.16" if unloading_from_excavation else "5.19 (p ≤ σzg,0)",
            "sigma_zg0_kPa": sg0}


def _layer_bottom_depth(params: D1Params, depth: float) -> float:
    """Глубина подошвы (вниз от 0) слоя, в котором находится заданная глубина."""
    elevation = -depth
    for layer in params.layers:
        if layer.bottom <= elevation <= layer.top:
            return -layer.bottom
    return depth


def tilt(params: D1Params) -> Dict[str, object]:
    """Крен фундамента i по п.5.6.44 ф.(5.24)–(5.25), D̄ по п.5.6.45 ф.(5.26).

        i = D̄ · k_e · N · e / (a/2)³ ,   D = (1 − ν²)/E

    D̄ — среднее по сжимаемой толще: D̄ = Σ(σzp,i·h_i·(1−ν²)/E_i) / Σ(σzp,i·h_i).
    Требует ν (табл. 5.10) и направление момента; без них — честный отказ.
    """
    if params.moment_kNm in (None, 0, 0.0):
        return {"status": "не применимо (момент не задан)", "i": None}
    if params.poisson is None:
        return {"status": "не определено (нужен коэффициент поперечной деформации ν по табл. 5.10)",
                "i": None}
    sres = settlement(params)
    if sres.get("Hc_m") is None:
        return {"status": f"не определено (нет Hc: {sres['status']})", "i": None}
    Hc = float(sres["Hc_m"])

    # D̄ по (5.26): веса A_i = σzp,i·h_i, посчитанные по той же сетке, что и осадка
    p_press = params.pressure_kpa()
    eta = params.l / params.b
    h = min(0.4 * params.b, 0.4)
    z = 0.0
    num = den = 0.0
    while z < Hc - 1e-9:
        z_next = min(z + h, Hc)
        dz = z_next - z
        zm = z + dz / 2.0
        a_i = alpha_coeff(2.0 * zm / params.b, eta) * p_press * dz
        e_i = _E_at(params, params.d + zm)
        num += a_i * (1.0 - params.poisson ** 2) / e_i
        den += a_i
        z = z_next
    if den <= 0:
        return {"status": "не определено (не удалось построить эпюру σzp)", "i": None}
    D_avg = num / den

    n_load = params.N
    ecc = params.moment_kNm / n_load if n_load else 0.0
    eta_ratio = params.l / params.b
    if params.moment_along == "circle":
        a = params.b
    elif params.moment_along == "smaller":
        a = min(params.b, params.l)
    else:
        a = max(params.b, params.l)
    ke = tilt_ke(eta_ratio, params.moment_along)
    i_value = D_avg * ke * n_load * ecc / (a / 2.0) ** 3

    if params.tilt_limit is None:
        status = "не определено (предельный крен i_u не задан; вычисленное значение — справочно)"
    else:
        status = "выполняется" if i_value <= params.tilt_limit else "не выполняется"
    return {"status": status, "i": i_value, "ke": ke, "D_avg": D_avg,
            "ecc_m": ecc, "a_m": a, "Hc_m": Hc}


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
    if params.moment_kNm not in (None, 0, 0.0) and params.poisson is None:
        refusals.append("крен: не задан коэффициент поперечной деформации ν (табл. 5.10)")
    if params.moment_kNm not in (None, 0, 0.0):
        refusals.append("краевые давления: проверка не реализована (крен — реализован)")
    if params.data_bottom >= -params.d:
        refusals.append("нет данных о грунте ниже подошвы")
    p = params.pressure_kpa()
    try:
        R = bearing_resistance(params)
    except (UnverifiedNormValue, InsufficientData) as exc:
        refusals.append(f"R: не определено — {exc}")
        R = None
    if R is None:
        checks.append({
            "id": "p_le_R", "clause": "СП 22.13330.2016, п.5.6.7, ф.(5.7)",
            "value": p, "criterion": None, "status": "не определено",
        })
    else:
        checks.append({
            "id": "p_le_R", "clause": "СП 22.13330.2016, п.5.6.7, ф.(5.7)",
            "value": p, "criterion": R["R_kPa"],
            "status": "выполняется" if p <= R["R_kPa"] else "не выполняется",
        })
    tres = tilt(params)
    if tres.get("i") is not None:
        checks.append({
            "id": "i_le_iu", "clause": "СП 22.13330.2016, п.5.6.44, ф.(5.24)–(5.26)",
            "value": tres["i"], "criterion": params.tilt_limit, "status": tres["status"],
        })
    sres = settlement(params)
    checks.append({
        "id": "s_le_su", "clause": "СП 22.13330.2016, п.5.6.31, ф.(5.16); п.5.6.41; прил. Г, табл. Г.1",
        "value": sres.get("s_cm"), "criterion": params.su_cm,
        "status": sres["status"],
    })
    if R is None:
        return {
            "R_kPa": None, "p_kPa": round(p, 2),
            "Mg": None, "Mq": None, "Mc": None,
            "gamma_II": None, "gamma_IIp": None,
            "settlement": {k: (round(v, 3) if isinstance(v, float) else v)
                           for k, v in sres.items()},
            "tilt": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in tres.items()},
            "checks": checks, "refusals": refusals,
        }
    return {
        "R_kPa": round(R["R_kPa"], 2), "p_kPa": round(p, 2),
        "Mg": round(R["Mg"], 3), "Mq": round(R["Mq"], 3), "Mc": round(R["Mc"], 3),
        "gamma_II": round(R["gamma_II"], 3), "gamma_IIp": round(R["gamma_IIp"], 3),
        "settlement": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in sres.items()},
        "tilt": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in tres.items()},
        "checks": checks, "refusals": refusals,
    }
