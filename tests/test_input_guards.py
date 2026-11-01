# -*- coding: utf-8 -*-
"""Защиты от молчаливо неверных входных данных.

Каждый тест соответствует дефекту, найденному при самоаудите 2026-11-01:
до исправления система возвращала правдоподобное число вместо отказа.
"""
import pytest

from calc.d1_foundation import (
    D1Params, InsufficientData, Layer, analyze, bearing_resistance,
)


def deep_layers():
    return [
        Layer(top=0.0, bottom=-3.0, gamma=17.5, E_kpa=9000.0),
        Layer(top=-3.0, bottom=-20.0, gamma=18.5, E_kpa=9000.0),
    ]


def test_kz_for_wide_footing_follows_clause_5_6_7():
    """b ≥ 10 м: kz = z0/b + 0.2, иначе R завышается на ~13 %."""
    params = D1Params(b=12.0, l=15.0, d=3.0, N=8000.0, data_bottom=-20.0,
                      layers=deep_layers())
    assert params.kz_value == pytest.approx(8.0 / 12.0 + 0.2)
    narrow = D1Params(b=2.0, l=2.4)
    assert narrow.kz_value == 1.0


def test_kz_override_still_wins():
    params = D1Params(b=12.0, l=15.0, d=3.0, N=8000.0, data_bottom=-20.0,
                      kz=1.0, layers=deep_layers())
    assert params.kz_value == 1.0


def test_missing_soil_over_averaging_depth_is_refused():
    """Слои на 1 м при требуемых 3 м (b/2): раньше γ считалась по нулям."""
    params = D1Params(b=6.0, l=6.0, d=1.0, N=2000.0, data_bottom=-4.0,
                      layers=[Layer(top=0.0, bottom=-1.0, gamma=17.5, E_kpa=9000.0),
                              Layer(top=-1.0, bottom=-2.0, gamma=18.5, E_kpa=9000.0)])
    with pytest.raises(InsufficientData):
        bearing_resistance(params)
    result = analyze(params)
    assert result["R_kPa"] is None
    assert result["checks"][0]["status"] == "не определено"


@pytest.mark.parametrize("kwargs", [
    {"water_line": 1.0},   # УГВ выше поверхности земли — ловушка со знаком
    {"d": -1.0},
    {"b": 0.0},
    {"data_bottom": 0.5},
])
def test_invalid_inputs_are_rejected_loudly(kwargs):
    with pytest.raises(ValueError):
        D1Params(**kwargs)


def test_baseline_unchanged_after_guards():
    """Защиты не должны менять проектный случай D1."""
    result = analyze(D1Params())
    assert result["R_kPa"] == pytest.approx(215.62, abs=0.01)
    assert result["settlement"]["s_cm"] == pytest.approx(4.232, abs=0.002)
