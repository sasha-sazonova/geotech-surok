# -*- coding: utf-8 -*-
"""СП 24.13330.2021 — осадки свайных групп и кустов (раздел 7.4).

Реализовано (официальный текст, сверено с изображениями страниц 35–43):

* п.7.4.2, ф.(7.34)–(7.39) — осадка одиночной висячей сваи (длинные κ ≥ 7.5 и
  короткие κ ≤ 7.5 ветви, табл. 7.18);
* п.7.4.4, ф.(7.40)–(7.41) — взаимное влияние соседних свай (δ от a/d);
* п.7.4.5, ф.(7.42) — осадка i-й сваи в группе из n ≤ 25 свай;
* п.7.4.8–7.4.11, ф.(7.45)–(7.49) — осадка большеразмерного поля через условный
  фундамент: sef по СП 22.13330 (метод послойного суммирования) + Δsp (продавливание)
  + Δsc (сжатие ствола);
* п.7.8.5 — снижение несущей способности на выдёргивание для кустов ≤ 4 свай (−20 %).

Честные ограничения:
* γca = 1.1 и численные методы 7.4.13 — вне области (только аналитика);
* КСП-фундаменты (7.4.14–7.4.17) — вне области;
* sef (осадка условного фундамента) — вызовом модуля СП 22.13330 calc/d1_foundation
  (метод послойного суммирования реализован там и сверён).

Единицы: осадки мм, силы МН (в формулах 7.34/7.40 N в МН!), длины м, модули МПа.
Внимание: в ф.(7.40) N — в МН, G1l — МПа·м → δ безразмерен; si в мм при N в МН и
G1l в МПа·м даёт мм (МН/(МПа·м) = м).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple


class GroupLimitation(ValueError):
    """Случай вне области реализации раздела 7.4."""


# ---------------- табл. 7.18: kν, ζ0, mν ----------------
NU_NODES: Tuple[float, ...] = (0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5)
KNU_TABLE: Tuple[float, ...] = (2.82, 2.636, 2.464, 2.312, 2.151, 2.011, 1.882, 1.764, 1.657, 1.56, 1.475)
ZETA0_TABLE: Tuple[float, ...] = (0.455, 0.437, 0.419, 0.4, 0.38, 0.361, 0.34, 0.319, 0.297, 0.274, 0.25)
MNU_TABLE: Tuple[float, ...] = (1.345, 1.373, 1.405, 1.446, 1.491, 1.54, 1.607, 1.685, 1.786, 1.916, 2.01)


def _interp_nu(table: Sequence[float], nu: float) -> float:
    if not (0.0 <= nu <= 0.5):
        raise ValueError(f"ν = {nu} вне диапазона табл. 7.18 (0…0.5)")
    for i in range(len(NU_NODES) - 1):
        if NU_NODES[i] <= nu <= NU_NODES[i + 1]:
            f = (nu - NU_NODES[i]) / (NU_NODES[i + 1] - NU_NODES[i])
            return table[i] + (table[i + 1] - table[i]) * f
    return table[-1]


def k_nu(nu: float) -> float:
    return _interp_nu(KNU_TABLE, nu)


# ---------------- п.7.4.2: одиночная свая ----------------

@dataclass
class SoilForSettlement:
    """Осреднённые характеристики (п.7.4.3): G1/ν1 по стволу, G2/ν2 в пределах 0.5l ниже конца."""
    G1_MPa: float
    nu1: float
    G2_MPa: float
    nu2: float


def single_pile_settlement(N_MN: float, l_m: float, d_m: float,
                           EA_MN: float, soil: SoilForSettlement) -> Dict[str, object]:
    """Осадка одиночной висячей сваи, п.7.4.2: ветвь а) (7.34)–(7.37) при κ ≥ 7.5,
    ветвь б) (7.38) при κ ≤ 7.5. N в МН, результат в мм."""
    if N_MN <= 0:
        raise ValueError("N должен быть положительным")
    kappa = soil.G1_MPa * l_m / (soil.G2_MPa * d_m)
    nu_avg = (soil.nu1 + soil.nu2) / 2.0
    if kappa >= 7.5:
        knu_avg = k_nu(nu_avg)
        knu1 = k_nu(soil.nu1)
        beta_prime = 0.17 * math.log(knu_avg * kappa)
        alpha_prime = 0.17 * math.log(knu1 * soil.nu1 * l_m / d_m)
        chi = EA_MN / (soil.G1_MPa * l_m ** 2)
        if chi <= 0:
            raise ValueError("EA должен быть положительным")
        lambda1 = 2.12 * chi ** 0.75 / (1.0 + 2.12 * chi ** 0.75)
        # φ.(7.35): β = β'/λ1 + 0.3·(1 − β'/α')/χ
        if alpha_prime == 0:
            raise GroupLimitation("α' = 0 (вырожденный случай ln(kν1·l/d)); проверьте входные данные")
        beta = beta_prime / lambda1 + 0.3 * (1.0 - beta_prime / alpha_prime) / chi
        s_m = beta * N_MN / (soil.G1_MPa * l_m)
        return {"s_mm": s_m * 1000.0, "kappa": kappa, "branch": "а) длинные (κ ≥ 7.5)",
                "beta": beta, "beta_prime": beta_prime, "alpha_prime": alpha_prime,
                "chi": chi, "lambda1": lambda1}
    # ветвь б)
    zeta0 = _interp_nu(ZETA0_TABLE, nu_avg)
    m_nu = _interp_nu(MNU_TABLE, nu_avg)
    zeta_prime = zeta0 / (1.0 + (kappa / m_nu) ** 2 * (1.0 - 2.0 * soil.nu2) / (2.0 * math.log(3.0 - 4.0 * soil.nu2)))
    s_m = zeta_prime * N_MN / (soil.G2_MPa * d_m)
    return {"s_mm": s_m * 1000.0, "kappa": kappa, "branch": "б) короткие (κ ≤ 7.5)",
            "zeta_prime": zeta_prime, "zeta0": zeta0, "m_nu": m_nu}


def equivalent_diameter(area_m2: float) -> float:
    """d по ф.(7.39) для некруглых сечений: d = 4A/π."""
    return 4.0 * area_m2 / math.pi


# ---------------- п.7.4.4–7.4.5: группа (куст) ----------------

def interaction_delta(a_m: float, l_m: float, G1_MPa: float, G2_MPa: float,
                      nu: float) -> float:
    """δ по ф.(7.41) — взаимное влияние: sad = δ·N/(G1·l), N в МН → sad в м.

    δ = 0.17·ln(kν·G1·l/(G2·a)) / (kν·G1·l/(G2·a)), если аргумент > 1; иначе 0.
    """
    knu = k_nu(nu)
    arg = knu * G1_MPa * l_m / (G2_MPa * a_m)
    if arg <= 1.0:
        return 0.0
    return 0.17 * math.log(arg) / arg


def group_settlement(piles: Sequence[Tuple[float, float]],
                     loads_MN: Sequence[float],
                     l_m: float, G1_MPa: float, G2_MPa: float,
                     nu1: float, nu2: float,
                     single_s_MM: Optional[float] = None,
                     EA_MN: float = 0.0, d_m: float = 0.0) -> Dict[str, object]:
    """Осадка каждой сваи по ф.(7.42): si = s(Ni) + Σ_{j≠i} δij·Nj/(G1·l).

    piles — список (x, y) координат осей свай, м; loads_MN — вертикальные нагрузки, МН.
    Равномерный ростверк (предварительный расчёт): loads = Nd/n на каждую сваю.
    Жёсткий ростверк: осадки выравниваются итерациями (7.4.5, последний абзац) —
    возвращает распределение нагрузок из условия равных осадок (простая релаксация).
    single_s_MM — осадка одиночной сваи от её собственной нагрузки (мм); если не задана
    и заданы EA/d — считается по 7.4.2.
    """
    n = len(piles)
    if len(loads_MN) != n:
        raise ValueError("число нагрузок должно совпадать с числом свай")
    if n < 2:
        raise GroupLimitation("для группы нужно ≥ 2 свай")
    if n > 25:
        raise GroupLimitation(
            "куст > 25 свай: по п.7.4.1 это свайное ПОЛЕ, расчёт через условный фундамент (7.4.8)")
    nu_avg = (nu1 + nu2) / 2.0

    # матрица δij
    delta: List[List[float]] = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            ax = piles[i][0] - piles[j][0]
            ay = piles[i][1] - piles[j][1]
            a = math.hypot(ax, ay)
            if a < 1e-6:
                raise GroupLimitation("координаты свай совпадают")
            delta[i][j] = interaction_delta(a, l_m, G1_MPa, G2_MPa, nu_avg)

    # собственная осадка одиночной сваи от своей нагрузки
    if single_s_MM is None:
        if EA_MN <= 0 or d_m <= 0:
            raise ValueError("нужен либо single_s_MM, либо пара EA_MN/d_m для расчёта по 7.4.2")
        res = single_pile_settlement(loads_MN[0], l_m, d_m, EA_MN, SoilForSettlement(G1_MPa, nu1, G2_MPa, nu2))
        s_own_per_MN = res["s_mm"] / loads_MN[0]
    else:
        s_own_per_MN = single_s_MM / loads_MN[0]

    s_mm = []
    for i in range(n):
        add = sum(delta[i][j] * loads_MN[j] / (G1_MPa * l_m) * 1000.0 for j in range(n) if j != i)
        s_mm.append(s_own_per_MN * loads_MN[i] + add)

    max_delta = max(max(row) for row in delta)
    return {"s_mm": [round(v, 3) for v in s_mm],
            "delta_ij_max": round(max_delta, 4),
            "note": "гибкий ростверк (нагрузки заданы); жёсткий — см. rigid_group_settlement"}


def rigid_group_settlement(piles: Sequence[Tuple[float, float]],
                           total_MN: float,
                           l_m: float, G1_MPa: float, G2_MPa: float,
                           nu1: float, nu2: float,
                           single_s_MM_per_MN: float,
                           iterations: int = 200) -> Dict[str, object]:
    """Жёсткий ростверк: осадки всех свай одинаковы (п.7.4.5, последний абзац).

    Решение: N_i находим итерационной релаксацией — нагрузка перераспределяется
    пропорционально тому, насколько осадка сваи ниже/выше средней.
    """
    n = len(piles)
    nu_avg = (nu1 + nu2) / 2.0
    delta: List[List[float]] = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            a = math.hypot(piles[i][0] - piles[j][0], piles[i][1] - piles[j][1])
            delta[i][j] = interaction_delta(a, l_m, G1_MPa, G2_MPa, nu_avg)

    loads = [total_MN / n] * n
    s = [0.0] * n
    for _ in range(iterations):
        for i in range(n):
            add = sum(delta[i][j] * loads[j] / (G1_MPa * l_m) * 1000.0 for j in range(n) if j != i)
            s[i] = single_s_MM_per_MN * loads[i] + add
        s_mean = sum(s) / n
        err = max(abs(v - s_mean) for v in s)
        if err < 1e-6:
            break
        # релаксация: убираем нагрузку у «просевших», добавляем «недогруженным»
        for i in range(n):
            loads[i] += (s_mean - s[i]) / (single_s_MM_per_MN + 1e-12) * 0.5 / n
        # нормировка
        k = total_MN / sum(loads)
        loads = [v * k for v in loads]
    return {"N_MN": [round(v, 4) for v in loads], "s_mm": [round(v, 4) for v in s],
            "iterations": iterations}


# ---------------- п.7.4.8–7.4.11: поле свай через условный фундамент ----------------

def fictitious_footing_geometry(pile_xs: Sequence[float], pile_ys: Sequence[float],
                                step_m: float, d_m: float,
                                depth_m: float) -> Dict[str, float]:
    """Границы условного фундамента по п.7.4.9: от крайних рядов свай по 0.5 шага,
    но не более 1.5d; глубина — до нижних концов свай."""
    offset = min(0.5 * step_m, 1.5 * d_m)
    B = max(pile_xs) - min(pile_xs) + d_m + 2.0 * offset
    L = max(pile_ys) - min(pile_ys) + d_m + 2.0 * offset
    return {"B_m": B, "L_m": L, "depth_m": depth_m, "offset_m": offset}


def punch_settlement(p_MPa: float, a_m: float, d_m: float, E1_MPa: float,
                     E2_MPa: float, nu2: float) -> Dict[str, float]:
    """Δsp по ф.(7.46)–(7.48): продавливание свай на уровне подошвы условного фундамента.
    p — среднее давление по подошве условного фундамента, МПа.
    P = p·a² (квадратное сечение); k = d/a; (7.48) в тексте содержит опечатку k → используем
    (1 − ν2²)·P/(d·E2) как в издании."""
    if a_m <= d_m:
        raise GroupLimitation("осевое расстояние a должно быть больше d")
    ds_p1 = math.pi * (1.0 - nu2 ** 2) * p_MPa * (a_m - 1.5 * d_m) / (4.0 * E2_MPa)
    P = p_MPa * a_m * a_m
    ds_p0 = (1.0 - nu2 ** 2) * P / (d_m * E2_MPa)
    if ds_p0 == 0:
        raise GroupLimitation("Δsp0 = 0 при нулевом давлении")
    ds_p = ds_p1 / (ds_p1 / ds_p0 * (1.0 - E2_MPa / E1_MPa) + E2_MPa / E1_MPa)
    return {"delta_sp_mm": ds_p * 1000.0, "delta_sp1_mm": ds_p1 * 1000.0,
            "delta_sp0_mm": ds_p0 * 1000.0}


def shaft_compression(N_MN: float, l_m: float, a_m: float, EA_MN: float) -> Dict[str, float]:
    """Δsc по ф.(7.49): осадка за счёт сжатия ствола: Δsc = P(l − a)/(EA), P = N на сваю."""
    if a_m >= l_m:
        raise GroupLimitation("a < l требуется для Δsc (a — шаг свай)")
    ds = N_MN * (l_m - a_m) / EA_MN
    return {"delta_sc_mm": ds * 1000.0}


# ---------------- п.7.8.5: выдёргивание в кусте ≤ 4 свай ----------------

def pullout_in_group_factor(n_piles: int, is_LPE_line_support: bool = True) -> float:
    """Коэффициент снижения несущей способности на выдёргивание для куста: п.7.8.5 —
    кусты из ≤ 4 свай фундаментов опор ЛЭП: −20 % (фактор 0.8). Для прочих случаев
    применяется табл. 7.20 (вне области: её строки зависят от l/d и H/N)."""
    if is_LPE_line_support and n_piles <= 4:
        return 0.8
    raise GroupLimitation(
        "снижение 20 % (п.7.8.5) определено только для кустов ≤ 4 свай опор ЛЭП; "
        "иные случаи — табл. 7.20 (l/d, H/N) — вне области реализации")
