# -*- coding: utf-8 -*-
"""Rows 38 and 43 of табл. 5.5 are flagged as reconstructed.

The source PDF text layer is damaged exactly in the Mγ column of those two
rows («А Н .» and «ЗЛ2»), while Mq and Mc are readable.  The stored Mγ values
are reconstructions, so any calculation touching them must refuse rather than
return a number that looks normative.
"""
import pytest

from calc.d1_foundation import (
    M_coefficients, RESTORED_ROWS, UnverifiedNormValue, bearing_resistance, D1Params,
)


def test_restored_rows_are_declared():
    assert set(RESTORED_ROWS) == {38, 43}


@pytest.mark.parametrize("phi", [38, 43])
def test_exact_restored_row_refuses(phi):
    with pytest.raises(UnverifiedNormValue):
        M_coefficients(float(phi))


@pytest.mark.parametrize("phi", [37.5, 42.5])
def test_interpolation_touching_restored_row_refuses(phi):
    with pytest.raises(UnverifiedNormValue):
        M_coefficients(phi)


@pytest.mark.parametrize("phi", [0, 16, 25, 35, 37, 39, 45])
def test_verified_rows_still_work(phi):
    mg, mq, mc = M_coefficients(float(phi))
    assert mg >= 0 and mq >= 1 and mc > 3


def test_sensitivity_mode_is_explicit():
    mg, mq, mc = M_coefficients(38, allow_restored=True)
    assert mg == pytest.approx(2.11)
    assert (mq, mc) == pytest.approx((9.44, 10.80))


def test_bearing_resistance_refuses_on_damaged_cell():
    with pytest.raises(UnverifiedNormValue):
        bearing_resistance(D1Params(phi_deg=38.0))


def test_default_design_case_is_unaffected():
    """D1 uses φ = 16°, so the restored rows never enter a delivered number."""
    res = bearing_resistance(D1Params())
    assert res["R_kPa"] == pytest.approx(215.62, abs=0.01)
