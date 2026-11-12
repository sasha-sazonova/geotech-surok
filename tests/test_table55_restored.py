# -*- coding: utf-8 -*-
"""Строки 38 и 43 табл. 5.5: значения подтверждены печатным изданием.

История: текстовый слой PDF в этих ячейках повреждён (OCR показывал «А Н .» и «ЗЛ2»),
поэтому значения были помечены как реконструкция, а расчёт с φ = 38°/43° отказывал.
01.11.2026 ячейки прочитаны с изображения печатных страниц 36 и 37:
Mγ(38) = 2,11; Mγ(43) = 3,12. Отказ снят, значения закреплены этими тестами.

Механизм UnverifiedNormValue сохранён как страховка: если в будущем появится неподтверждённая
ячейка, достаточно добавить её в RESTORED_ROWS, и расчёт снова начнёт отказывать.
"""
import pytest

from calc.d1_foundation import (
    M_coefficients, RESTORED_ROWS, TABLE55_PROVENANCE, UnverifiedNormValue,
    bearing_resistance, D1Params,
)


def test_no_unverified_rows_left():
    assert RESTORED_ROWS == {}


def test_provenance_recorded_for_former_gaps():
    assert set(TABLE55_PROVENANCE) == {38, 43}
    assert "2,11" in TABLE55_PROVENANCE[38]
    assert "3,12" in TABLE55_PROVENANCE[43]


@pytest.mark.parametrize("phi, expected", [(38.0, 2.11), (43.0, 3.12)])
def test_former_gap_rows_now_return_verified_values(phi, expected):
    mg, mq, mc = M_coefficients(phi)
    assert mg == pytest.approx(expected)


def test_neighbours_unchanged_by_the_fix():
    assert M_coefficients(37.0)[0] == pytest.approx(1.95)
    assert M_coefficients(39.0)[0] == pytest.approx(2.28)
    assert M_coefficients(42.0)[0] == pytest.approx(2.88)
    assert M_coefficients(44.0)[0] == pytest.approx(3.38)


def test_guard_still_works_when_a_row_is_flagged(monkeypatch):
    """Страховка жива: помеченная ячейка снова даёт отказ."""
    monkeypatch.setitem(RESTORED_ROWS, 38, "тестовая пометка")
    with pytest.raises(UnverifiedNormValue):
        M_coefficients(38.0)
    with pytest.raises(UnverifiedNormValue):
        bearing_resistance(D1Params(phi_deg=37.5))


def test_design_case_unaffected():
    assert bearing_resistance(D1Params())["R_kPa"] == pytest.approx(215.62, abs=0.01)
