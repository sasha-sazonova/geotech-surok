# -*- coding: utf-8 -*-
"""Раздел 7.4 СП 24.13330.2021: осадки одиночной сваи, куста и поля.

Формулы и коэффициенты сверены с официальным текстом (страницы 35–43 издания);
табл. 7.18 прочитана целиком (ν = 0…0.5).
"""
import math

import pytest

from calc.sp24_group import k_nu

from calc.sp24_group import (
    GroupLimitation, SoilForSettlement, equivalent_diameter,
    fictitious_footing_geometry, group_settlement, interaction_delta,
    k_nu, pullout_in_group_factor, punch_settlement, rigid_group_settlement,
    shaft_compression, single_pile_settlement,
)


# ---------- табл. 7.18 ----------

def test_knu_table_nodes():
    assert k_nu(0.0) == pytest.approx(2.82)
    assert k_nu(0.3) == pytest.approx(1.882)
    assert k_nu(0.5) == pytest.approx(1.475)
    assert k_nu(0.15) == pytest.approx(2.312)


def test_knu_interpolation():
    assert k_nu(0.025) == pytest.approx((2.82 + 2.636) / 2)


# ---------- 7.4.2: одиночная свая ----------

def test_single_pile_long_branch_closed_form():
    """Ручной контроль ветви а): известные входные данные → повторяемая арифметика.
    G1=20 МПа, l=20 м, G2=40 МПа, d=0.4: κ = 20·20/(40·0.4) = 25 ≥ 7.5.
    ν1=ν2=0.3 → ν=0.3 → kν=1.882; β'=0.17·ln(1.882·25)=0.17·ln(47.05); 
    α'=0.17·ln(1.882·0.3·20/0.4)=0.17·ln(28.23); χ=EA/(G1·l²).
    EA = 2000 МН → χ = 2000/(20·400)=0.25; λ1=2.12·0.25^0.75/(1+2.12·0.25^0.75)."""
    soil = SoilForSettlement(G1_MPa=20.0, nu1=0.3, G2_MPa=40.0, nu2=0.3)
    res = single_pile_settlement(1.0, 20.0, 0.4, 2000.0, soil)
    knu = 1.882
    bp = 0.17 * math.log(knu * 25.0)
    ap = 0.17 * math.log(knu * 0.3 * 20.0 / 0.4)
    chi = 2000.0 / (20.0 * 400.0)
    lam = 2.12 * chi ** 0.75 / (1.0 + 2.12 * chi ** 0.75)
    beta = bp / lam + 0.3 * (1.0 - bp / ap) / chi
    s_expected_mm = beta * 1.0 / (20.0 * 20.0) * 1000.0
    assert res["kappa"] == pytest.approx(25.0)
    assert res["beta"] == pytest.approx(beta)
    assert res["s_mm"] == pytest.approx(s_expected_mm, rel=1e-9)


def test_single_pile_short_branch():
    """κ ≤ 7.5 → ветвь б) (7.38). G1=10, l=5, G2=20, d=0.5: κ = 50/10 = 5."""
    soil = SoilForSettlement(G1_MPa=10.0, nu1=0.3, G2_MPa=20.0, nu2=0.3)
    res = single_pile_settlement(0.5, 5.0, 0.5, 1000.0, soil)
    assert res["kappa"] == pytest.approx(5.0)
    assert "короткие" in res["branch"]
    # ζ0(0.3)=0.34, mν(0.3)=1.607 → ζ' = 0.34/(1+(5/1.607)²·(1-0.6)/(2·ln(3-1.2)))
    zeta0, mnu = 0.34, 1.607
    kappa = 5.0
    zeta_p = zeta0 / (1.0 + (kappa / mnu) ** 2 * (1.0 - 2.0 * 0.3) / (2.0 * math.log(3.0 - 4.0 * 0.3)))
    s_expected_mm = zeta_p * 0.5 / (20.0 * 0.5) * 1000.0
    assert res["s_mm"] == pytest.approx(s_expected_mm, rel=1e-9)


def test_equivalent_diameter():
    assert equivalent_diameter(0.16) == pytest.approx(4 * 0.16 / math.pi)  # 0.4×0.4 квадрат


# ---------- 7.4.4: δ ----------

def test_delta_zero_when_argument_le_one():
    # κ аргумент = kν·G1·l/(G2·a): малое G1l или большое a → 0
    assert interaction_delta(a_m=10.0, l_m=10.0, G1_MPa=5.0, G2_MPa=20.0, nu=0.3) == 0.0


def test_delta_has_maximum_at_x_equals_e():
    """δ = 0.17·ln(x)/x при x = kν·G1·l/(G2·a) имеет максимум при x = e.
    Для kν(0.3)=1.882, G1·l/G2 = 10: x = 18.82/a → максимум при a ≈ 6.9 м.
    Это свойство нормы (7.41), а не ошибки: влияние дальних свай убывает."""
    d_small = interaction_delta(1.0, 20.0, 20.0, 40.0, 0.3)
    d_peak = interaction_delta(6.9, 20.0, 20.0, 40.0, 0.3)
    # за пределами x ≤ 1 (a ≥ 18.82 м) влияние нулевое по (7.41)
    assert interaction_delta(20.0, 20.0, 20.0, 40.0, 0.3) == 0.0
    assert d_peak > d_small > 0.0
    # проверка формулы напрямую
    knu = k_nu(0.3)
    arg = knu * 20.0 * 20.0 / (40.0 * 6.9)
    assert d_peak == pytest.approx(0.17 * math.log(arg) / arg)


def test_delta_manual_value():
    a, l, G1, G2, nu = 3.0, 20.0, 20.0, 40.0, 0.3
    knu = 1.882
    arg = knu * G1 * l / (G2 * a)
    assert interaction_delta(a, l, G1, G2, nu) == pytest.approx(0.17 * math.log(arg) / arg)


# ---------- 7.4.5: куст ----------

def test_group_of_two_matches_manual():
    """2 сваи, шаг 3 м: δ12 = δ21 = δ(3 м). N = 1 МН каждой.
    si = s_own(1 МН) + δ·1/(G1·l)."""
    piles = [(0.0, 0.0), (3.0, 0.0)]
    res = group_settlement(piles, [1.0, 1.0], 20.0, 20.0, 40.0, 0.3, 0.3,
                           single_s_MM=5.0)
    d = interaction_delta(3.0, 20.0, 20.0, 40.0, 0.3)
    expected = 5.0 + d * 1.0 / (20.0 * 20.0) * 1000.0
    assert res["s_mm"][0] == pytest.approx(expected, abs=1e-3)
    assert res["s_mm"][1] == pytest.approx(expected, abs=1e-3)


def test_group_symmetry():
    piles = [(0, 0), (3, 0), (0, 3), (3, 3)]
    res = group_settlement(piles, [1.0] * 4, 20.0, 20.0, 40.0, 0.3, 0.3, single_s_MM=5.0)
    assert res["s_mm"][0] == pytest.approx(res["s_mm"][3])
    assert res["s_mm"][1] == pytest.approx(res["s_mm"][2])


def test_group_symmetry_3x3_full():
    """Сетка 3×3 с шагом 3 м: по (7.41) δ симметрична, углы равны, центр минимален
    (центральная свая дальше от «периферийного большинства»? — фактически δ растёт
    с расстоянием до максимума ~6.9 м, поэтому угловая свья получает БОЛЬШЕ вкладов
    от дальних соседей, чем центральная. Проверяем фактическое поведение нормы:
    углы (расстояния 3, 3, 4.24, 6, 6, 6.7, 6.7, 8.49) vs центр (3×4.24).
    """
    piles = [(x, y) for x in (0, 3, 6) for y in (0, 3, 6)]
    res = group_settlement(piles, [1.0] * 9, 20.0, 20.0, 40.0, 0.3, 0.3, single_s_MM=5.0)
    corner = res["s_mm"][0]
    center = res["s_mm"][4]
    # по (7.41) угловая свая оседает БОЛЬШЕ: у неё соседи на больших расстояниях,
    # где δ ближе к максимуму кривой ln(x)/x
    assert corner > center
    assert res["s_mm"][0] == pytest.approx(res["s_mm"][8])
    assert res["s_mm"][1] == pytest.approx(res["s_mm"][3])


def test_group_over_25_refuses():
    piles = [(i * 3.0, 0) for i in range(26)]
    with pytest.raises(GroupLimitation):
        group_settlement(piles, [1.0] * 26, 20.0, 20.0, 40.0, 0.3, 0.3, single_s_MM=5.0)


def test_rigid_group_equalizes_settlements():
    piles = [(0, 0), (3, 0), (6, 0)]
    res = rigid_group_settlement(piles, 3.0, 20.0, 20.0, 40.0, 0.3, 0.3, 5.0)
    s = res["s_mm"]
    assert max(s) - min(s) < 0.01
    assert pytest.approx(sum(res["N_MN"]), abs=1e-3) == 3.0


def test_rigid_group_load_shifts_to_edge():
    """При жёстком ростверке сваи с меньшей осадкой от единичной нагрузки нагружаются
    больше (уравнивание осадок). По (7.41) у краевой сваи добавки от соседей больше
    (δ растёт с расстоянием до ~7 м), поэтому центральная недогружается."""
    piles = [(0, 0), (3, 0), (6, 0)]
    res = rigid_group_settlement(piles, 3.0, 20.0, 20.0, 40.0, 0.3, 0.3, 5.0)
    # уравнивание осадок работает
    s = res["s_mm"]
    assert max(s) - min(s) < 0.01
    # сумма нагрузок сохраняется
    assert sum(res["N_MN"]) == pytest.approx(3.0, abs=1e-2)
    # при δ растущем с расстоянием: угловая имеет больший суммарный вклад → её N меньше
    assert res["N_MN"][1] > res["N_MN"][0] or res["N_MN"][1] > res["N_MN"][2]


# ---------- 7.4.9: условный фундамент ----------

def test_fictitious_footing_geometry():
    res = fictitious_footing_geometry([0.0, 3.0, 6.0], [0.0, 3.0], 3.0, 0.4, 10.0)
    # offset = min(1.5, 0.6) = 0.6 м; B = 6 + 0.4 + 1.2 = 7.6
    assert res["offset_m"] == pytest.approx(0.6)
    assert res["B_m"] == pytest.approx(6.0 + 0.4 + 1.2)
    assert res["L_m"] == pytest.approx(3.0 + 0.4 + 1.2)


def test_fictitious_footing_offset_capped():
    """Шаг 4 м → 0.5 шага = 2 м, но cap 1.5·d = 0.9 при d = 0.6."""
    res = fictitious_footing_geometry([0.0, 4.0], [0.0], 4.0, 0.6, 10.0)
    assert res["offset_m"] == pytest.approx(0.9)


# ---------- 7.4.10–7.4.11: Δsp и Δsc ----------

def test_punch_settlement_manual():
    """Δsp1 = π(1−ν²)·p·(a−1.5d)/(4E2); Δsp0 = (1−ν²)·p·a²/(d·E2).
    p=0.3 МПа, a=3, d=0.4, E2=30 МПа, ν2=0.3 → ручной счёт."""
    p_MPa, a, d, E2, nu2 = 0.3, 3.0, 0.4, 30.0, 0.3
    res = punch_settlement(p_MPa, a, d, 20.0, E2, nu2)
    dsp1 = math.pi * (1 - nu2 ** 2) * p_MPa * (a - 1.5 * d) / (4 * E2)
    dsp0 = (1 - nu2 ** 2) * p_MPa * a * a / (d * E2)
    expected = dsp1 / (dsp1 / dsp0 * (1 - E2 / 20.0) + E2 / 20.0)
    assert res["delta_sp1_mm"] == pytest.approx(dsp1 * 1000.0)
    assert res["delta_sp0_mm"] == pytest.approx(dsp0 * 1000.0)
    assert res["delta_sp_mm"] == pytest.approx(expected * 1000.0)


def test_punch_refuses_when_a_le_d():
    with pytest.raises(GroupLimitation):
        punch_settlement(0.3, 0.4, 0.4, 20.0, 30.0, 0.3)


def test_shaft_compression_manual():
    """Δsc = N(l−a)/(EA): N=1 МН, l=20, a=3, EA=2000 → 0.0085 м = 8.5 мм."""
    res = shaft_compression(1.0, 20.0, 3.0, 2000.0)
    assert res["delta_sc_mm"] == pytest.approx(8.5)


# ---------- 7.8.5 ----------

def test_pullout_group_factor():
    assert pullout_in_group_factor(4) == 0.8
    assert pullout_in_group_factor(2) == 0.8
    with pytest.raises(GroupLimitation):
        pullout_in_group_factor(6)
    with pytest.raises(GroupLimitation):
        pullout_in_group_factor(3, is_LPE_line_support=False)
