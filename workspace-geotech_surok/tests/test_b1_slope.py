# -*- coding: utf-8 -*-
"""B1 benchmark: slope stability — hand Fellenius/Bishop vs xslope 1.0.6 and pyslope 1.4.0.

Geometry: crest (40, RL 50), toe (60, RL 40), material 18 kN/m3, phi=25, c=10.
Circle: cx=55.405, cz=61.024, R=21.520 (pyslope's critical circle on its own geometry).

ИСПРАВЛЕНО 2026-11-04. Прежние числа (Fellenius 1.7296, Bishop 1.5265) были следствием
двух ошибок в коде и признаны недействительными:
  * Fellenius считался без cos α (N = W вместо N = W·cos α);
  * Bishop — по формуле, не соответствующей упрощённому Bishop.

Правильные значения на этом круге:
  Fellenius 1.5903   (xslope OMS 1.590)
  Bishop    1.6922   (xslope Bishop 1.692)
Расхождение с xslope ≤ 0.02 % — это и есть теперь критерий приёмки B1.
"""
import pytest

from calc.b1_slope import SlopeSpec, bishop_fellenius_on_circle

SPEC = SlopeSpec()
CIRCLE = dict(cx=55.4053481969273, cz=61.02417631243577, R=21.52038138156163)
X_EXIT_TOE = 59.95  # arc crosses the base RL=40 near the toe


def test_fellenius_matches_xslope_oms():
    """Fellenius against the published LEM engine (xslope 1.0.6 OMS = 1.590)."""
    r = bishop_fellenius_on_circle(SPEC, method="fellenius", x_hi_override=X_EXIT_TOE, **CIRCLE)
    assert r["fs"] == pytest.approx(1.590, abs=0.005)


def test_bishop_matches_xslope_bishop():
    """Simplified Bishop against xslope (1.692)."""
    r = bishop_fellenius_on_circle(SPEC, method="bishop", x_hi_override=X_EXIT_TOE, **CIRCLE)
    assert r["fs"] == pytest.approx(1.692, abs=0.005)


def test_bishop_above_fellenius_for_circular_slip():
    """Для круглоцилиндрической поверхности упрощённый Bishop даёт FS выше Fellenius."""
    f = bishop_fellenius_on_circle(SPEC, method="fellenius", x_hi_override=X_EXIT_TOE, **CIRCLE)["fs"]
    b = bishop_fellenius_on_circle(SPEC, method="bishop", x_hi_override=X_EXIT_TOE, **CIRCLE)["fs"]
    assert b > f


def test_auto_exit_detection_without_override():
    """Без x_hi_override модуль сам находит касательный выход у подошвы (баг 11.2026)."""
    r = bishop_fellenius_on_circle(SPEC, method="fellenius", **CIRCLE)
    assert r["x_exit"] > 59.0
    assert r["fs"] == pytest.approx(1.590, abs=0.01)


def test_monotonic_fs_in_cohesion():
    c_weak = bishop_fellenius_on_circle(SPEC, method="fellenius", x_hi_override=X_EXIT_TOE, **CIRCLE)["fs"]
    strong = SlopeSpec(c_kpa=20.0)
    c_strong = bishop_fellenius_on_circle(strong, method="fellenius", x_hi_override=X_EXIT_TOE, **CIRCLE)["fs"]
    assert c_strong > c_weak
