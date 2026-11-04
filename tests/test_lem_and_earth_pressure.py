# -*- coding: utf-8 -*-
"""Основа LEM (xslope) и давление грунта/подпорные стены (geoeq) — приёмочные проверки."""
import math

import pytest

from calc.earth_pressure import (
    GEOEQ_AVAILABLE, WallSoil, active_pressure_profile, bearing_check,
    crosscheck_geoeq, ka_coulomb, ka_rankine, k0_jaky, kp_rankine,
    overturning_check, sheet_pile_blum, sliding_check,
)
from calc.lem_slope import Circle, SlopeModel, available as lem_available, factor_of_safety

requires_xslope = pytest.mark.skipif(not lem_available(), reason="xslope не установлен")
requires_geoeq = pytest.mark.skipif(not GEOEQ_AVAILABLE, reason="geoeq не установлен")


# ---------------- коэффициенты давления ----------------

def test_rankine_coefficients_analytic():
    assert ka_rankine(30) == pytest.approx(1 / 3, rel=1e-9)
    assert kp_rankine(30) == pytest.approx(3.0, rel=1e-9)
    assert ka_rankine(0) == pytest.approx(1.0)
    assert kp_rankine(0) == pytest.approx(1.0)


def test_ka_times_kp_is_one():
    for phi in (10, 20, 25, 35, 40):
        assert ka_rankine(phi) * kp_rankine(phi) == pytest.approx(1.0, rel=1e-9)


def test_k0_jaky():
    assert k0_jaky(30) == pytest.approx(0.5, rel=1e-9)
    assert k0_jaky(0) == pytest.approx(1.0)


def test_coulomb_below_rankine_with_friction():
    """Трение по стене снижает активное давление: K_a(Кулон) < K_a(Ранкин)."""
    assert ka_coulomb(30, delta_deg=20) < ka_rankine(30)


# ---------------- эпюра ----------------

def test_active_pressure_resultant_matches_hand_calc():
    """q=10, γ=18, H=6, φ=30 (c=0): σ_top=3.33, σ_bot=39.33, Ea=128 кН/м, плечо 3.844 м."""
    soil = WallSoil(gamma=18, phi_deg=30, c_kpa=0, surcharge_kpa=10)
    r = active_pressure_profile(6.0, soil)
    assert r["nodes"][0]["sigma_a_kPa"] == pytest.approx(10 * 1 / 3, abs=0.01)
    assert r["nodes"][-1]["sigma_a_kPa"] == pytest.approx((10 + 18 * 6) / 3, abs=0.01)
    assert r["Ea_kN_per_m"] == pytest.approx(128.0, abs=0.5)


def test_tension_crack_depth_for_cohesive_soil():
    """z_c = 2c/(γ√K_a): c=10, γ=18, φ=30 → 2·10/(18·0.5774) = 1.924 м."""
    soil = WallSoil(gamma=18, phi_deg=30, c_kpa=10)
    r = active_pressure_profile(6.0, soil)
    assert r["tension_crack_m"] == pytest.approx(2 * 10 / (18 * math.sqrt(1 / 3)), abs=0.01)


def test_water_increases_pressure():
    dry = active_pressure_profile(6.0, WallSoil(gamma=18, phi_deg=30))
    wet = active_pressure_profile(6.0, WallSoil(gamma=18, phi_deg=30, water_table_m=2.0))
    assert wet["nodes"][-1]["u_kPa"] > 0
    assert wet["nodes"][-1]["sigma_a_kPa"] + wet["nodes"][-1]["u_kPa"] > dry["nodes"][-1]["sigma_a_kPa"]


# ---------------- проверки стены ----------------

def test_sliding_check():
    r = sliding_check(vertical_kN=200, horizontal_kN=80, mu=0.5)
    assert r["fs"] == pytest.approx(1.25)
    assert r["status"] == "не выполняется"


def test_sliding_passive_resistance_helps():
    r = sliding_check(vertical_kN=200, horizontal_kN=80, mu=0.5, passive_kN=60)
    assert r["fs"] == pytest.approx((100 + 60) / 80)
    assert r["status"] == "выполняется"


def test_overturning_check():
    assert overturning_check(400, 200)["fs"] == pytest.approx(2.0)
    assert overturning_check(200, 200)["status"] == "не выполняется"


def test_bearing_within_kern():
    r = bearing_check(vertical_kN=200, moment_kNm=60, width_m=2.0, R_kpa=250)
    assert r["eccentricity_m"] == pytest.approx(0.3)
    assert r["within_kern"] is True
    assert r["q_max_kPa"] == pytest.approx(190.0)
    assert r["q_min_kPa"] == pytest.approx(10.0)


def test_bearing_outside_kern_triangular():
    r = bearing_check(vertical_kN=200, moment_kNm=160, width_m=2.0)
    assert r["within_kern"] is False
    # q_max = 2V/(3(B/2 − e)), e = 0.8 → 400/(3·0.2) = 666.7
    assert r["q_max_kPa"] == pytest.approx(666.67, abs=0.1)
    assert r["q_min_kPa"] == 0.0


# ---------------- кросс-проверка geoeq ----------------

@requires_geoeq
def test_geoeq_crosscheck_matches():
    soil = WallSoil(gamma=18, phi_deg=30, surcharge_kpa=10)
    r = crosscheck_geoeq(6.0, soil)
    assert r["delta_Ka_pct"] < 0.1
    assert r["delta_Ea_pct"] < 1.0


@requires_geoeq
def test_sheet_pile_blum():
    r = sheet_pile_blum(18, 5, 30)
    assert r["status"] == "рассчитано"
    assert r["D_design_m"] > r["D_theory_m"] > 0


# ---------------- LEM: семь методов ----------------

@requires_xslope
def test_all_seven_methods_run_and_agree():
    """На круге B1 все 7 методов дают FS в диапазоне 1.5…1.8, разброс < 0.2."""
    m = SlopeModel(crest_x=40, crest_y=10, toe_x=60, toe_y=0, base_depth=0.5)
    c = Circle(55.405, 21.024, 21.520)
    r = factor_of_safety(m, c, workdir="/tmp")
    assert set(r["fs"]) == {"oms", "bishop", "janbu", "corps", "lowe", "spencer", "mprice"}
    assert all(1.4 < v < 1.9 for v in r["fs"].values())
    assert r["spread"] < 0.2
    assert r["status"] == "рассчитано"


@requires_xslope
def test_lem_matches_our_hand_methods():
    """Ключевая проверка: движок и наш ручной код совпадают в пределах 1 %."""
    from calc.b1_slope import SlopeSpec, bishop_fellenius_on_circle

    m = SlopeModel(crest_x=40, crest_y=10, toe_x=60, toe_y=0, base_depth=0.5)
    c = Circle(55.405, 21.024, 21.520)
    r = factor_of_safety(m, c, methods=("oms", "bishop"), workdir="/tmp")

    spec = SlopeSpec()  # та же геометрия, но в RL: бровка 50, подошва 40
    cx, cz, R = 55.405, 61.024, 21.520
    ours_f = bishop_fellenius_on_circle(spec, cx, cz, R, method="fellenius",
                                        x_hi_override=60.0)["fs"]
    ours_b = bishop_fellenius_on_circle(spec, cx, cz, R, method="bishop",
                                        x_hi_override=60.0)["fs"]
    assert r["fs"]["oms"] == pytest.approx(ours_f, rel=0.01)
    assert r["fs"]["bishop"] == pytest.approx(ours_b, rel=0.01)
