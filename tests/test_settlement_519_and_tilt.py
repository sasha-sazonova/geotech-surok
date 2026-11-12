# -*- coding: utf-8 -*-
"""Формула (5.19), правило 5.6.41 про слой E ≤ 7 МПа и крен по 5.6.44–5.6.45.

Формулы взяты с изображений печатного издания СП 22.13330.2016 (с. 45, 48, 49),
а не из текстового слоя PDF — он в этих местах повреждён.
"""
import pytest

from calc.d1_foundation import (
    D1Params, Layer, analyze, settlement, sigma_zg0, tilt, tilt_ke,
)


def deep(**kw):
    base = dict(b=2.0, l=2.4, d=6.0, N=1200.0, data_bottom=-20.0, water_line=-3.2,
                layers=[Layer(top=0.0, bottom=-6.0, gamma=17.5, E_kpa=9000.0),
                        Layer(top=-6.0, bottom=-20.0, gamma=18.5, E_kpa=9000.0)])
    base.update(kw)
    return D1Params(**base)


# ---------- (5.19): p ≤ σzg,0 ----------

def test_formula_519_when_pressure_below_own_weight():
    params = deep(N=10.0, gamma_f=1.0)  # p ≈ 8 кПа << σzg,0 ≈ 77 кПа
    res = settlement(params)
    assert res["formula"].startswith("5.19")
    assert res["s_cm"] is not None and res["s_cm"] > 0


def test_formula_516_when_pressure_above_own_weight():
    params = deep()
    res = settlement(params)
    assert res["formula"] == "5.16"
    assert params.pressure_kpa() > sigma_zg0(params)


def test_519_uses_secondary_modulus():
    """(5.19) делит на E_e, поэтому «мягкая» разгрузка увеличивает осадку."""
    soft = deep(N=10.0, gamma_f=1.0)
    for layer in soft.layers:
        layer.E_unload_kpa = layer.E_kpa  # E_e = E вместо 5E
    assert settlement(soft)["s_cm"] > settlement(deep(N=10.0, gamma_f=1.0))["s_cm"]


# ---------- 5.6.41: слой E ≤ 7 МПа ----------

def test_weak_layer_extends_compressible_thickness():
    strong = D1Params()
    weak = D1Params(layers=[Layer(top=0.0, bottom=-1.8, gamma=17.5, E_kpa=9000.0),
                            Layer(top=-1.8, bottom=-5.8, gamma=18.5, E_kpa=5000.0)])
    r_strong, r_weak = settlement(strong), settlement(weak)
    assert r_weak["Hc_m"] > r_strong["Hc_m"]
    assert r_weak["s_cm"] > r_strong["s_cm"]


def test_baseline_settlement_unchanged():
    res = settlement(D1Params())
    assert res["s_cm"] == pytest.approx(4.232, abs=0.002)
    assert res["Hc_m"] == pytest.approx(3.6, abs=0.05)


# ---------- крен 5.6.44 ----------

def test_tilt_ke_table_values():
    assert tilt_ke(1.0, "larger") == pytest.approx(0.50)
    assert tilt_ke(1.2, "larger") == pytest.approx(0.57)
    assert tilt_ke(10.0, "larger") == pytest.approx(2.00)
    assert tilt_ke(1.5, "smaller") == pytest.approx(0.36)
    assert tilt_ke(1.0, "circle") == pytest.approx(0.75)


def test_tilt_requires_poisson():
    res = tilt(D1Params(moment_kNm=120.0))
    assert res["i"] is None
    assert "табл. 5.10" in res["status"]


def test_tilt_matches_closed_form_for_uniform_soil():
    params = D1Params(moment_kNm=120.0, poisson=0.35)
    res = tilt(params)
    D_manual = (1.0 - 0.35 ** 2) / 9000.0
    i_manual = D_manual * 0.57 * 1200.0 * 0.1 / (2.4 / 2.0) ** 3
    assert res["D_avg"] == pytest.approx(D_manual, rel=1e-9)
    assert res["i"] == pytest.approx(i_manual, rel=1e-9)


def test_tilt_is_linear_in_moment():
    a = tilt(D1Params(moment_kNm=100.0, poisson=0.35))["i"]
    b = tilt(D1Params(moment_kNm=200.0, poisson=0.35))["i"]
    assert b == pytest.approx(2.0 * a, rel=1e-9)


def test_tilt_absent_without_moment():
    assert tilt(D1Params())["i"] is None


def test_analyze_reports_tilt_check_when_moment_given():
    result = analyze(D1Params(moment_kNm=120.0, poisson=0.35, tilt_limit=0.005))
    ids = [c["id"] for c in result["checks"]]
    assert "i_le_iu" in ids
    tilt_check = next(c for c in result["checks"] if c["id"] == "i_le_iu")
    assert tilt_check["status"] in ("выполняется", "не выполняется")
