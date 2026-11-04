# -*- coding: utf-8 -*-
"""Давление грунта на подпорную стену и проверки устойчивости стены.

Расчётная часть — собственные формулы (Rankine/Coulomb, СП 22.13330.2016 п.5.6,
СП 542.1325800.2024 для подпорных стен). Кросс-проверка — geoeq 0.1.3 (Apache-2.0),
если пакет установлен; при его отсутствии расчёт не подменяется, а помечается
«кросс-проверка не выполнялась».

Область: вертикальная гладкая/шероховатая стена, однородный грунт, пригрузка на
поверхности, УГВ; активное и пассивное давление, глубина трещины отрыва, проверки
сдвига, опрокидывания и краевых давлений под подошвой.

Вне области (возвращается отказ): слоистый грунт, наклонная стена/поверхность,
сейсмика, армирование, этапность, шпунт (см. sheet_pile_blum — по Блюму).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

GAMMA_W = 9.81

try:  # необязательная кросс-проверка
    from geoeq.design import K0 as _K0, Ka as _Ka, Kp as _Kp, earth_pressure as _geo_ep
    GEOEQ_AVAILABLE = True
except Exception:  # pragma: no cover
    GEOEQ_AVAILABLE = False


# ---------------- коэффициенты бокового давления ----------------

def ka_rankine(phi_deg: float) -> float:
    """K_a = tan²(45° − φ/2) — активное давление, сыпучий грунт."""
    return math.tan(math.radians(45.0 - phi_deg / 2.0)) ** 2


def kp_rankine(phi_deg: float) -> float:
    """K_p = tan²(45° + φ/2) — пассивное давление."""
    return math.tan(math.radians(45.0 + phi_deg / 2.0)) ** 2


def k0_jaky(phi_deg: float) -> float:
    """K_0 = 1 − sin φ — боковое давление покоя (Jaky)."""
    return 1.0 - math.sin(math.radians(phi_deg))


def ka_coulomb(phi_deg: float, delta_deg: float = 0.0, beta_deg: float = 0.0,
               alpha_deg: float = 90.0) -> float:
    """K_a по Кулону для плоской стены (alpha — угол наклона стены к горизонту, град).

    beta — наклон поверхности грунта за стеной, delta — трение грунта по стене.
    """
    phi = math.radians(phi_deg)
    delta = math.radians(delta_deg)
    beta = math.radians(beta_deg)
    alpha = math.radians(alpha_deg)
    num = math.sin(alpha + phi) ** 2
    den = (math.sin(alpha) ** 2
           * math.sin(alpha - delta)
           * (1.0 + math.sqrt(math.sin(phi + delta) * math.sin(phi - beta)
                              / (math.sin(alpha - delta) * math.sin(alpha + beta)))) ** 2)
    if den <= 0:
        raise ValueError("недопустимая комбинация углов для формулы Кулона")
    return num / den


# ---------------- эпюра активного давления ----------------

@dataclass
class WallSoil:
    gamma: float = 18.0          # удельный вес, кН/м³
    phi_deg: float = 30.0
    c_kpa: float = 0.0
    surcharge_kpa: float = 0.0   # равномерная пригрузка на поверхности
    water_table_m: Optional[float] = None   # глубина УГВ от поверхности (м), None — нет


def active_pressure_profile(H_m: float, soil: WallSoil,
                            n_points: int = 11) -> Dict[str, object]:
    """Эпюра активного давления по глубине: σ_a(z) = (q + γz)·K_a − 2c·√K_a (+ вода).

    Возвращает узлы, равнодействующую, плечо и глубину трещины отрыва.
    """
    if H_m <= 0:
        raise ValueError("высота стены должна быть положительной")
    ka = ka_rankine(soil.phi_deg)
    sqrt_ka = math.sqrt(ka)
    coh = 2.0 * soil.c_kpa * sqrt_ka

    # глубина трещины отрыва: σ_a = (q + γz)·K_a − 2c·√K_a = 0
    #   → z = (2c/√K_a − q)/γ
    z_crack = max(0.0, (2.0 * soil.c_kpa / sqrt_ka - soil.surcharge_kpa) / soil.gamma) \
        if soil.gamma > 0 else 0.0
    z_crack = min(z_crack, H_m)

    nodes = []
    for i in range(n_points):
        z = H_m * i / (n_points - 1)
        sigma = (soil.surcharge_kpa + soil.gamma * z) * ka - coh
        u = 0.0
        if soil.water_table_m is not None and z > soil.water_table_m:
            # ниже УГВ: эффективное давление по submerged weight + гидростатика
            z_below = z - soil.water_table_m
            sigma_eff = ((soil.surcharge_kpa + soil.gamma * soil.water_table_m)
                         * ka - coh
                         + (soil.gamma - GAMMA_W) * z_below * ka)
            sigma = sigma_eff
            u = GAMMA_W * z_below
        nodes.append({"z_m": round(z, 3), "sigma_a_kPa": round(max(sigma, 0.0), 3),
                      "u_kPa": round(u, 3)})

    # равнодействующая численно (трапеции) по активному давлению (без воды)
    total = 0.0
    moment = 0.0
    for i in range(len(nodes) - 1):
        z1, z2 = nodes[i]["z_m"], nodes[i + 1]["z_m"]
        s1, s2 = nodes[i]["sigma_a_kPa"], nodes[i + 1]["sigma_a_kPa"]
        dz = z2 - z1
        f = 0.5 * (s1 + s2) * dz
        zc = z1 + dz * (s1 + 2 * s2) / (3 * (s1 + s2)) if (s1 + s2) > 0 else z1
        total += f
        moment += f * zc
    arm = moment / total if total > 0 else 0.0

    return {
        "Ka": round(ka, 5),
        "nodes": nodes,
        "Ea_kN_per_m": round(total, 2),
        "arm_m": round(arm, 3),
        "tension_crack_m": round(z_crack, 3),
        "coulomb_Ka": round(ka_coulomb(soil.phi_deg, delta_deg=2.0 * soil.phi_deg / 3.0), 5),
    }


# ---------------- проверки устойчивости стены ----------------

def sliding_check(vertical_kN: float, horizontal_kN: float, mu: float = 0.5,
                  c_base_kpa: float = 0.0, base_width_m: float = 0.0,
                  passive_kN: float = 0.0, fs_required: float = 1.5) -> Dict[str, object]:
    """Проверка на сдвиг: FS = (V·tanδ + c·B + E_p) / ΣH."""
    if horizontal_kN <= 0:
        return {"fs": None, "status": "не применимо (нет сдвигающей нагрузки)"}
    resisting = vertical_kN * mu + c_base_kpa * base_width_m + passive_kN
    fs = resisting / horizontal_kN
    return {"fs": round(fs, 3), "criterion": fs_required,
            "status": "выполняется" if fs >= fs_required else "не выполняется",
            "resisting_kN": round(resisting, 2), "driving_kN": round(horizontal_kN, 2)}


def overturning_check(resisting_moments_kNm: float, driving_moments_kNm: float,
                      fs_required: float = 1.5) -> Dict[str, object]:
    """Проверка на опрокидывание: FS = ΣM_уд / ΣM_опр."""
    if driving_moments_kNm <= 0:
        return {"fs": None, "status": "не применимо (нет опрокидывающего момента)"}
    fs = resisting_moments_kNm / driving_moments_kNm
    return {"fs": round(fs, 3), "criterion": fs_required,
            "status": "выполняется" if fs >= fs_required else "не выполняется"}


def bearing_check(vertical_kN: float, moment_kNm: float, width_m: float,
                  R_kpa: Optional[float] = None) -> Dict[str, object]:
    """Краевые давления под подошвой: q_max/min = V/B·(1 ± 6e/B), e = M/V."""
    if width_m <= 0:
        raise ValueError("ширина подошвы должна быть положительной")
    if vertical_kN <= 0:
        raise ValueError("вертикальная нагрузка должна быть положительной")
    e = moment_kNm / vertical_kN
    q_mean = vertical_kN / width_m
    within_kern = abs(e) <= width_m / 6.0 + 1e-9
    if within_kern:
        q_max = q_mean * (1.0 + 6.0 * e / width_m)
        q_min = q_mean * (1.0 - 6.0 * e / width_m)
    else:
        # отрыв подошвы: треугольная эпюра на длине 3(B/2 − e)
        q_max = 2.0 * vertical_kN / (3.0 * (width_m / 2.0 - e))
        q_min = 0.0
    out = {"eccentricity_m": round(e, 3), "within_kern": within_kern,
           "q_mean_kPa": round(q_mean, 2), "q_max_kPa": round(q_max, 2),
           "q_min_kPa": round(q_min, 2)}
    if R_kpa is not None:
        out["status"] = "выполняется" if q_max <= 1.2 * R_kpa else "не выполняется"
        out["criterion"] = f"q_max ≤ 1.2·R = {1.2 * R_kpa:.1f} кПа"
    else:
        out["status"] = "не определено (не задано расчётное сопротивление R)"
    return out


def sheet_pile_blum(gamma: float, H_m: float, phi_deg: float,
                    c_kpa: float = 0.0) -> Dict[str, object]:
    """Глубина заделки шпунта (консоль) по упрощённому методу Блюма."""
    if not GEOEQ_AVAILABLE:
        return {"status": "не определено (geoeq не установлен — метод Блюма недоступен)"}
    from geoeq.design import sheet_pile as _sp
    res = _sp(gamma=gamma, H=H_m, phi=phi_deg, c=c_kpa)
    return {"status": "рассчитано",
            "D_theory_m": round(float(res["D_theory"]), 3),
            "D_design_m": round(float(res["D_design"]), 3),
            "Ka": round(float(res["Ka"]), 4), "Kp": round(float(res["Kp"]), 4),
            "method": res.get("method", "Blum")}


def crosscheck_geoeq(H_m: float, soil: WallSoil) -> Dict[str, object]:
    """Сверка коэффициентов и равнодействующей с geoeq (если установлен)."""
    if not GEOEQ_AVAILABLE:
        return {"status": "кросс-проверка не выполнялась (geoeq не установлен)"}
    ep = _geo_ep(gamma=soil.gamma, H=H_m, phi=soil.phi_deg, c=soil.c_kpa,
                 kind="active", surcharge=soil.surcharge_kpa)
    ours = active_pressure_profile(H_m, soil)
    return {
        "status": "сверено",
        "Ka_ours": ours["Ka"], "Ka_geoeq": round(float(ep["K"]), 5),
        "Ea_ours_kN_per_m": ours["Ea_kN_per_m"],
        "Ea_geoeq_kN_per_m": round(float(ep["P_soil"]), 2),
        "delta_Ka_pct": round(abs(ours["Ka"] - float(ep["K"])) / float(ep["K"]) * 100.0, 3),
        "delta_Ea_pct": round(abs(ours["Ea_kN_per_m"] - float(ep["P_soil"]))
                              / float(ep["P_soil"]) * 100.0, 3),
    }
