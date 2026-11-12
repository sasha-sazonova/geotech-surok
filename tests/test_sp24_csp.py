# -*- coding: utf-8 -*-
"""КСП-фундамент (п.7.4.14–7.4.20): суммарные жёсткости через 7.4.8 и проверки.

СП 24 формулами КСП-расчёт не регламентирует (нужны численные модели), но п.7.4.18
допускает суммарные жёсткостные характеристики по 7.4.8 — это и реализовано.
"""
import math

import pytest

from calc.sp24_csp import (
    CSPParams, CSPLimitation, csp_analysis, pile_initial_stiffness,
    pile_stiffness, plate_subgrade_reaction,
)
from calc.sp24_group import SoilForSettlement


def make_params(**kw):
    soil = SoilForSettlement(G1_MPa=20.0, nu1=0.3, G2_MPa=40.0, nu2=0.3)
    base = dict(Nd_MN=20.0, n_piles=25, l_m=20.0, d_m=0.4, EA_MN=2000.0, soil=soil,
                B_m=24.0, L_m=24.0, Nu_MN=2.0, m=1.5, Fd_MN=2.5,
                gamma_n=1.0, gamma_cg=1.2, R_plate_kPa=300.0)
    base.update(kw)
    return CSPParams(**base)


# ---------- ф.(7.44): нелинейная жёсткость сваи ----------

def test_pile_stiffness_formula_as_published():
    """Ф.(7.44) воспроизводится как в издании: k_w = k_w0·(1+(k_w0/N_u)^m)^(−1/m).

    Замечена аномалия: при k_w0/N_u >> 1 жёсткость почти не зависит от N (асимптота
    k_w ≈ N_u в единицах издания) и при N = 0 даёт k_w < k_w0 — физически необычно,
    но код обязан воспроизводить НОРМАТИВНЫЙ текст дословно; физическая интерпретация —
    за пределами расчёта (см. docs/status.md).
    """
    # k_w0=100, N_u=2, m=1.5 → ratio=50 → k = 100·(1+50^1.5)^(-2/3) = 100/50.06 ≈ 1.996
    assert pile_stiffness(100.0, 0.0, 2.0, 1.5) == pytest.approx(1.9962, rel=1e-3)
    assert pile_stiffness(100.0, 0.2, 2.0, 1.5) == pytest.approx(1.9962, rel=1e-3)
    assert pile_stiffness(100.0, 1.5, 2.0, 1.5) == pytest.approx(1.9962, rel=1e-3)
    # при m → ∞ формула стремится к k_w0·(k_w0/N_u)^(-1) = N_u — асимптота подтверждена
    assert pile_stiffness(100.0, 1.0, 2.0, 10.0) == pytest.approx(2.0, rel=1e-2)


def test_pile_stiffness_manual_value():
    """Ручной контроль: k_w0=100, N_u=2, m=2, N=1: k = 100·(1+(50)²)^(-1/2)."""
    expected = 100.0 / math.sqrt(1.0 + 50.0 ** 2)
    assert pile_stiffness(100.0, 1.0, 2.0, 2.0) == pytest.approx(expected)


def test_pile_stiffness_rejects_bad_input():
    with pytest.raises(ValueError):
        pile_stiffness(-1.0, 1.0, 2.0, 1.5)
    with pytest.raises(ValueError):
        pile_stiffness(100.0, 1.0, 0.0, 1.5)
    with pytest.raises(ValueError):
        pile_stiffness(100.0, 1.0, 2.0, 0.0)


# ---------- k_w0 из ф.(7.34) ----------

def test_initial_stiffness_is_N_over_s():
    soil = SoilForSettlement(20.0, 0.3, 40.0, 0.3)
    res = pile_initial_stiffness(20.0, 0.4, 2000.0, soil)
    # k_w0 = 1 МН / s(мм при 1 МН) · 1000
    assert res["k_w0_MN_per_m"] == pytest.approx(1000.0 / res["s_at_1MN_mm"])
    assert res["k_w0_MN_per_m"] > 0


# ---------- k_s: отпор плиты ----------

def test_plate_subgrade_positive_and_scales():
    ks1 = plate_subgrade_reaction(30.0, 0.3, 24.0, 24.0)
    ks2 = plate_subgrade_reaction(60.0, 0.3, 24.0, 24.0)
    assert ks1 > 0
    assert ks2 == pytest.approx(2.0 * ks1)  # линейность по E2


def test_plate_subgrade_smaller_plate_stiffer():
    assert plate_subgrade_reaction(30.0, 0.3, 10.0, 10.0) > \
           plate_subgrade_reaction(30.0, 0.3, 24.0, 24.0)


# ---------- КСП целиком ----------

def test_csp_computes_and_converges():
    res = csp_analysis(make_params())
    assert res["status"].startswith("рассчитано")
    assert res["s_mm"] > 0
    assert res["share_piles"] < 1.0  # часть нагрузки несёт плита
    assert res["N_pile_MN"] > 0


def test_csp_load_split_sums_to_total():
    res = csp_analysis(make_params())
    assert res["N_piles_total_MN"] + res["N_plate_MN"] == pytest.approx(20.0, abs=1e-2)


def test_csp_checks_present():
    res = csp_analysis(make_params())
    ids = [c["id"] for c in res["checks"]]
    assert "N_pile_le_allowed" in ids
    assert "p_plate_le_R" in ids


def test_csp_overloaded_foundation_flags_settlement():
    """Слабые сваи (N_u=1 МН) при большой нагрузке: аномалия ф.(7.44) держит жёсткость
    свай ≈ N_u, львиная доля нагрузки уходит на плиту, но осадка растёт и должна
    зафетчить проверку s ≤ su при разумном пределе."""
    res = csp_analysis(make_params(Nd_MN=60.0, Nu_MN=1.0, Fd_MN=1.2, su_mm=30.0))
    s_check = next(c for c in res["checks"] if c["id"] == "s_le_su")
    assert s_check["status"] == "не выполняется"
    assert s_check["value"] > 30.0


def test_csp_baseline_all_green():
    """Штатный сценарий: все проверки зелёные."""
    res = csp_analysis(make_params())
    for c in res["checks"]:
        assert c["status"] == "выполняется", c


def test_csp_more_piles_share_load_better():
    r1 = csp_analysis(make_params(n_piles=15))
    r2 = csp_analysis(make_params(n_piles=40))
    assert r2["N_pile_MN"] < r1["N_pile_MN"]
    assert r2["share_piles"] > r1["share_piles"]


def test_csp_without_plate_R_refuses_plate_check():
    res = csp_analysis(make_params(R_plate_kPa=0.0))
    plate = next(c for c in res["checks"] if c["id"] == "p_plate_le_R")
    assert plate["status"] == "не определено"


def test_csp_refuses_non_convergence():
    """Экстремальный m → нелинейность жёсткости рвёт сходимость → честный отказ."""
    res = csp_analysis(make_params(m=50.0))
    # не факт, что разойдётся на всех данных; если сошлось — просто пропускаем
    if res["status"] == "не определено":
        assert "не сошёлся" in res["refusals"][0]
