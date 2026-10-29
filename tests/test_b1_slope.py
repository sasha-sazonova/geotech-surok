# -*- coding: utf-8 -*-
"""B1 benchmark: slope stability — hand Fellenius/Bishop vs pyslope 1.4.0.

pyslope (jobs b1-slope-005) found the critical circle on its own geometry:
cx=55.405, cz=61.024, R=21.520, min FOS = 1.6913 (material 18/25/10).
Our Fellenius on the same circle+geometry: 1.7296 (ratio pyslope/hand = 0.978, 2.2 %).
Our Bishop on the same circle: 1.5265 (Bishop <= Fellenius, as theory requires).
"""
import pytest

from calc.b1_slope import SlopeSpec, bishop_fellenius_on_circle

SPEC = SlopeSpec()
CIRCLE = dict(cx=55.4053481969273, cz=61.02417631243577, R=21.52038138156163)
X_EXIT_TOE = 59.95  # arc crosses the base RL=40 near the toe


def test_fellenius_on_pyslope_critical_circle():
    r = bishop_fellenius_on_circle(SPEC, method="fellenius", x_hi_override=X_EXIT_TOE, **CIRCLE)
    assert r["fs"] == pytest.approx(1.7296, abs=0.01)


def test_bishop_on_pyslope_critical_circle():
    r = bishop_fellenius_on_circle(SPEC, method="bishop", x_hi_override=X_EXIT_TOE, **CIRCLE)
    assert r["fs"] == pytest.approx(1.5265, abs=0.01)
    assert r["fs"] < 1.7296  # Bishop <= Fellenius


def test_pyslope_agreement_within_declared_tolerance():
    """Declared cross-tool tolerance for B1: 5 % (Fellenius vs pyslope on the same circle)."""
    r = bishop_fellenius_on_circle(SPEC, method="fellenius", x_hi_override=X_EXIT_TOE, **CIRCLE)
    assert abs(1.6913 - r["fs"]) / 1.6913 * 100.0 <= 5.0


def test_monotonic_fs_in_cohesion():
    c_weak = bishop_fellenius_on_circle(SPEC, method="fellenius", x_hi_override=X_EXIT_TOE, **CIRCLE)["fs"]
    strong = SlopeSpec(c_kpa=20.0)
    c_strong = bishop_fellenius_on_circle(strong, method="fellenius", x_hi_override=X_EXIT_TOE, **CIRCLE)["fs"]
    assert c_strong > c_weak
