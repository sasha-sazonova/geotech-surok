# -*- coding: utf-8 -*-
"""D2: независимая реализация сваи под горизонтальной нагрузкой и закрытая форма.

Закрывает пробел, найденный аудитом: в D2 расчёт вёлся только в openpile, «второй
реализации» не было. Здесь считается та же задача МКЭ (балка на упругом основании)
и сверяется (а) с точным решением полубесконечной балки, (б) с числами openpile.
"""
import math

import pytest

from calc.d2_pile import (
    PileSection, SandProfile, api_sand_py, elastic_semi_infinite_beam, solve_winkler,
)


SECTION = PileSection(D=1.2, t=0.022)
PROFILE = SandProfile(phi_deg=35.0, gamma=18.0, gamma_sub=18.0 - 9.81, water_depth=3.0)


def test_section_properties():
    d_in = 1.2 - 2 * 0.022
    I = math.pi * (1.2 ** 4 - d_in ** 4) / 64.0
    assert SECTION.I == pytest.approx(I, rel=1e-12)
    assert SECTION.EI == pytest.approx(210e6 * I, rel=1e-12)


def test_fem_matches_closed_form_elastic():
    """Главная проверка решателя: постоянная жёсткость → точное решение полубесконечной балки."""
    k = 20000.0  # кН/м³
    fem = solve_winkler(SECTION, PROFILE, L=40.0, H=500.0, k_const=k, n=160)
    exact = elastic_semi_infinite_beam(SECTION, k, 500.0)
    assert fem["y0_mm"] == pytest.approx(exact["y0_m"] * 1000.0, rel=0.005)
    assert fem["Mmax_kNm"] == pytest.approx(exact["Mmax_kNm"], rel=0.01)


def test_closed_form_scales_linearly():
    a = elastic_semi_infinite_beam(SECTION, 20000.0, 500.0)
    b = elastic_semi_infinite_beam(SECTION, 20000.0, 1000.0)
    assert b["y0_m"] == pytest.approx(2 * a["y0_m"], rel=1e-12)
    assert b["Mmax_kNm"] == pytest.approx(2 * a["Mmax_kNm"], rel=1e-12)


def test_stiffer_soil_gives_smaller_deflection():
    soft = elastic_semi_infinite_beam(SECTION, 10000.0, 500.0)
    stiff = elastic_semi_infinite_beam(SECTION, 40000.0, 500.0)
    assert stiff["y0_m"] < soft["y0_m"]


def test_api_py_curve_shape():
    """p-y: ноль при нуле, рост с глубиной и с перемещением, ограничение сверху."""
    py = api_sand_py(PROFILE, 1.2)
    y = [0.0, 0.001, 0.01, 0.1]
    z = 5.0
    p = [float(py(z, yi)) for yi in y]
    assert p[0] == pytest.approx(0.0, abs=1e-9)
    assert p[1] < p[2] < p[3]
    # предельное сопротивление не превышается
    z_arr = 5.0
    pu_shallow = (3.0 * z_arr + 3.8 * 1.2) * PROFILE.sigma_v(z_arr)
    pu_deep = 40.0 * 1.2 * PROFILE.sigma_v(z_arr)
    assert p[3] <= max(pu_shallow, pu_deep) + 1.0


def test_api_case_matches_openpile_within_declared_tolerance():
    """Сверка с openpile 1.0.3 (эталон D2): y = 6.275 мм, M = 890.5 кН·м при H = 500 кН.

    Допуск объявлен: ±8 % по перемещению, ±12 % по моменту — разница возникает из-за
    деталей реализации p-y (коэффициенты A, начальный модуль k), а не из-за ошибки.
    """
    res = solve_winkler(SECTION, PROFILE, L=24.0, H=500.0, n=120)
    assert res["y0_mm"] == pytest.approx(6.275, rel=0.08)
    assert res["Mmax_kNm"] == pytest.approx(890.5, rel=0.12)


def test_zero_load_gives_zero_deflection():
    res = solve_winkler(SECTION, PROFILE, L=24.0, H=0.0, n=60)
    assert res["y0_mm"] == pytest.approx(0.0, abs=1e-6)
