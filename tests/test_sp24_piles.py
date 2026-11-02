# -*- coding: utf-8 -*-
"""СП 24.13330.2021 — единичные проверки против официального текста.

Источники значений: PDF официального издания (82 с., получен из публичного зеркала,
web.archive) и OCR-контроль страниц 17–21. Табл. 7.3 глинистая часть сверена
с классическим СНиП 2.02.03-85 табл. 2 (совпадает полностью).
"""
import pytest

from calc.d1_foundation import UnverifiedNormValue
from calc.sp24_piles import (
    PileLayer, Sp24Limitation, bored_pile, driven_friction_pile,
    end_bearing_rock, f_lateral_cohesive, gamma_rf_bored, ks_for_rock,
    pulled_out_pile,
)


# ---------- табл. 7.1: Ks ----------

def test_ks_endpoints():
    assert ks_for_rock(95) == 1.0
    assert ks_for_rock(10) == pytest.approx(0.22)
    assert ks_for_rock(50) == pytest.approx(0.32)


def test_ks_interpolates_within_band():
    assert ks_for_rock(80) == pytest.approx(0.60 + (1.0 - 0.60) * (80 - 75) / (90 - 75))


# ---------- табл. 7.3: fi глинистые ----------

@pytest.mark.parametrize("depth, IL, expected", [
    (1.0, 0.2, 35), (1.0, 1.0, 2), (2.0, 0.2, 42), (40.0, 0.2, 107),
    (3.0, 0.5, 20), (20.0, 0.3, 56), (35.0, 1.0, 7),
])
def test_f_lateral_nodes(depth, IL, expected):
    assert f_lateral_cohesive(depth, IL) == pytest.approx(expected)


def test_f_lateral_interpolates_both_axes():
    # глубина 1.5 (между 1 и 2), IL=0.25 (между 0.2 и 0.3): (35+42)/2=38.5 и (23+30)/2=26.5 → 32.5
    assert f_lateral_cohesive(1.5, 0.25) == pytest.approx(32.5)


def test_f_lateral_out_of_range_refuses():
    with pytest.raises(UnverifiedNormValue):
        f_lateral_cohesive(5.0, 0.15)
    with pytest.raises(Sp24Limitation):
        f_lateral_cohesive(0.5, 0.4)
    with pytest.raises(Sp24Limitation):
        f_lateral_cohesive(45.0, 0.4)


def test_f_lateral_matches_snip_2020_baseline():
    """Полная сверка строки d=1 и d=20 с табл. 2 СНиП 2.02.03-85 (историческая сверка)."""
    for IL, v in zip((0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
                     (35, 23, 15, 12, 8, 4, 4, 3, 2)):
        assert f_lateral_cohesive(1.0, IL) == v
    for IL, v in zip((0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
                     (79, 56, 41, 30, 20, 12, 8, 7, 6)):
        assert f_lateral_cohesive(20.0, IL) == v


# ---------- табл. 7.4: способы погружения ----------

def test_driving_factors_hammer():
    assert gamma_rf_bored("bored_dry", "глины") == 0.6
    assert gamma_rf_bored("injection_pulse", "пески") == 1.3
    assert gamma_rf_bored("bored_under_water", "супеси") == 0.6


def test_unknown_driving_method_refuses():
    with pytest.raises(Sp24Limitation):
        gamma_rf_bored("magic_method", "глины")


# ---------- ф.(7.5)–(7.7): сваи-стойки ----------

def test_end_bearing_rock_basic():
    res = end_bearing_rock(Rc=20000.0, area=0.5, vop_percent=95)
    assert res["R_kPa"] == pytest.approx(20000.0)  # 20000·1.0 = cap
    assert res["Fd_kN"] == pytest.approx(10000.0)


def test_end_bearing_rock_cracked_rock():
    res = end_bearing_rock(Rc=20000.0, area=1.0, vop_percent=50)
    assert res["Ks"] == pytest.approx(0.32)
    assert res["Fd_kN"] == pytest.approx(0.32 * 20000.0)


def test_end_bearing_cap_20000():
    res = end_bearing_rock(Rc=50000.0, area=1.0, vop_percent=100)
    assert res["R_kPa"] <= 20000.0


# ---------- ф.(7.9): висячая забивная свая ----------

def test_driven_pile_full_example():
    """Ручной расчёт: R=5000 (песок ср.кр.), A=0.16 (0.4×0.4), u=1.6, молоты.
    Слои: d=3 м, IL=0.4 → fi=25 (узел таблицы); d=7 м, IL=0.3 → интерполяция
    между d=6 (42) и d=8 (44) → 43. side = (25+43)·2 = 136 кПа·м; end = 5000·0.16 = 800.
    Fd = 1.0·(800 + 1.6·136) = 1017.6 кН."""
    layers = [PileLayer(depth_mid_m=3.0, thickness_m=2.0, IL=0.4),
              PileLayer(depth_mid_m=7.0, thickness_m=2.0, IL=0.3)]
    res = driven_friction_pile(5000.0, 0.16, 1.6, layers, "hammer")
    assert res["status"] == "рассчитано"
    assert res["Fd_kN"] == pytest.approx(800 + 1.6 * 136.0)


def test_driven_pile_refuses_sand_side_friction():
    """Песчаные колонки табл. 7.3 не подтверждены → отказ, не число."""
    layers = [PileLayer(depth_mid_m=3.0, thickness_m=2.0, IL=None)]
    res = driven_friction_pile(5000.0, 0.16, 1.6, layers, "hammer")
    assert res["status"] == "не определено"
    assert "не подтверждены" in res["refusals"][0]


def test_driven_pile_refuses_clay_end_bearing():
    """Глинистая часть табл. 7.2 не подтверждена → отказ при R=None."""
    res = driven_friction_pile(None, 0.16, 1.6, [], "hammer")
    assert res["status"] == "не определено"


def test_driven_pile_layer_thicker_than_2m_refuses():
    layers = [PileLayer(depth_mid_m=3.0, thickness_m=4.0, IL=0.4)]
    res = driven_friction_pile(5000.0, 0.16, 1.6, layers, "hammer")
    assert res["status"] == "не определено"
    assert "2 м" in res["refusals"][0]


# ---------- ф.(7.11): выдёргивание ----------

def test_pulled_out_uses_side_only():
    layers = [PileLayer(depth_mid_m=3.0, thickness_m=2.0, IL=0.4)]
    res = pulled_out_pile(1.6, layers, "hammer")
    # Fdu = γcu·Σ γR,f·fi·hi = 1.0·(1.0·25·2)·1.6 = 80 кН
    assert res["Fdu_kN"] == pytest.approx(80.0)


# ---------- ф.(7.13): буровые сваи ----------

def test_bored_pile_with_explicit_fi():
    layers = [(3.0, 2.0, 25.0), (7.0, 2.0, 37.0)]
    soils = ["суглинки", "суглинки"]
    res = bored_pile(3000.0, 0.5, 2.51, layers, "bored_dry", soils)
    # side = 0.7·(25·2 + 37·2) = 86.8; end = 3000·0.5 = 1500; γc = 1
    assert res["Fd_kN"] == pytest.approx(1500 + 2.51 * 86.8)


def test_bored_pile_gamma_c_wet_clay():
    layers = [(3.0, 2.0, 25.0)]
    res = bored_pile(3000.0, 0.5, 2.51, layers, "bored_dry", ["суглинки"],
                     Sr_less_085_or_loess=True)
    assert res["gamma_c"] == 0.8


def test_bored_pile_missing_fi_refuses():
    res = bored_pile(3000.0, 0.5, 2.51, [(3.0, 2.0, None)], "bored_dry", ["суглинки"])
    assert res["status"] == "не определено"
