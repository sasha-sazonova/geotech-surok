# -*- coding: utf-8 -*-
"""Settlement with the second term of (5.16) — п.5.6.33, 5.6.34, 5.6.35.

Official text (verified PDF, pp. 43-44):
  s = β·Σ [ σzp,i/E_i − σzγ,i/E_e,i ]·h_i        (5.16)
  σzp = α·p                                       (5.17)
  σzγ = α·σzg,0                                   (5.18)
  «в расчете σzγ используются размеры в плане не фундамента, а котлована» (5.6.33)
  «при котлованах глубиной менее 5 м допускается ... не учитывать второе слагаемое» (5.6.34)
  «если p < σzg,0, осадку вычисляют по формуле (5.19)» (5.6.35)
"""
import pytest

from calc.d1_foundation import D1Params, Layer, settlement, sigma_zg0


def deep_params(**kw) -> D1Params:
    base = dict(
        b=2.0, l=2.4, d=6.0, N=1200.0, phi_deg=16.0, c_kpa=18.0,
        water_line=-3.2, data_bottom=-20.0,
        layers=[
            Layer(top=0.0, bottom=-6.0, gamma=17.5, E_kpa=9000.0),
            Layer(top=-6.0, bottom=-20.0, gamma=18.5, E_kpa=9000.0),
        ],
    )
    base.update(kw)
    return D1Params(**base)


def test_deep_pit_now_computes_instead_of_refusing():
    res = settlement(deep_params())
    assert res["status"] in ("выполняется", "не выполняется")
    assert res["s_cm"] is not None and res["s_cm"] > 0
    assert res["unloading_included"] is True


def test_shallow_pit_keeps_omitting_second_term():
    """п.5.6.34: for d < 5 m the term is omitted — D1 baseline must not move."""
    res = settlement(D1Params())
    assert res["unloading_included"] is False
    assert res["s_cm"] == pytest.approx(4.232, abs=0.002)


def test_omitting_second_term_for_deep_pit_is_refused():
    res = settlement(deep_params(), include_unloading=False)
    assert res["s_cm"] is None
    assert "п.5.6.34" in res["status"]


def test_larger_pit_gives_more_unloading_and_smaller_settlement():
    """σzγ uses pit dimensions (5.6.33): a wider pit unloads deeper."""
    small = settlement(deep_params(pit_b=4.0, pit_l=5.0))
    large = settlement(deep_params(pit_b=12.0, pit_l=15.0))
    assert large["s_cm"] < small["s_cm"]


def test_secondary_modulus_credit_is_conservative_by_default():
    """Note 1 to 5.6.31 allows E_e ≈ 5E; a higher E_e gives less unloading credit.

    With E_e = E (no reload stiffening) the credit is larger and the settlement
    smaller, so the default E_e = 5E is the conservative choice.
    """
    soft_reload = deep_params()
    soft_reload.layers[1].E_unload_kpa = 9000.0  # no stiffening on reload
    assert settlement(soft_reload)["s_cm"] < settlement(deep_params())["s_cm"]


def test_pressure_below_own_weight_requires_formula_519():
    res = settlement(deep_params(N=10.0, gamma_f=1.0))
    assert res["s_cm"] is None
    assert "5.19" in res["status"]


def test_sigma_zg0_uses_submerged_weight_below_water_table():
    """5.6.33: σzg,0 = γ'·d; below the water table the submerged weight applies."""
    params = deep_params(d=6.0)  # water_line = -3.2 m
    expected = (17.5 * 3.2 + (17.5 - 9.81) * 2.8) / 6.0 * 6.0
    assert sigma_zg0(params) == pytest.approx(expected, rel=1e-9)
    dry = deep_params(d=6.0, water_line=-50.0)
    assert sigma_zg0(dry) == pytest.approx(17.5 * 6.0, rel=1e-9)
