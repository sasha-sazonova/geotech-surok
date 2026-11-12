# -*- coding: utf-8 -*-
"""B3 benchmark: openpile API_sand_axial unit formulas vs hand API RP2A formulas.

Verified on the compute node (jobs b3-axial-003): shaft friction matches hand
f = K·sigma_v'·tan(delta) to 0.0% at z = 1..20 m; at z = 23 m openpile applies
the built-in API fmax limit (−4.87 %) — that is part of the method, not an error.
Tip: openpile qp = 9039.6 kPa = Nq(40)·sigma_v'(24 m) — exact match.

This test file runs WITHOUT openpile (pure formulas) to keep the repo light:
it pins the hand-reference numbers that openpile was checked against on the node.
"""
import math

import pytest

GAMMA, GAMMA_SUB, WL = 18.0, 18.0 - 9.81, -3.0
DELTA, K = 30.0, 0.8


def sigma_v(z: float) -> float:
    if z <= -WL:
        return GAMMA * z
    return GAMMA * (-WL) + GAMMA_SUB * (z + WL)


def f_hand(z: float) -> float:
    return K * sigma_v(z) * math.tan(math.radians(DELTA))


EXPECTED_NODE = {  # openpile values from jobs b3-axial-003
    1.0: 8.31, 3.0: 24.94, 5.0: 32.51, 10.0: 51.42, 15.0: 70.34, 20.0: 89.25, 23.0: 95.70,
}


@pytest.mark.parametrize("z, f_node", sorted(EXPECTED_NODE.items()))
def test_hand_matches_openpile_node_values(z, f_node):
    hand = f_hand(z)
    if z <= 20.0:
        assert hand == pytest.approx(f_node, abs=0.01)
    else:
        # openpile applies the API fmax cap near the tip: node value is BELOW the naive formula
        assert f_node <= hand


def test_tip_pressure_reference():
    """Nq = 40, sigma_v'(24 m) = 226.0 kPa -> qp = 9039.6 kPa (node value)."""
    Nq = 40.0
    qp = Nq * sigma_v(24.0)
    assert qp == pytest.approx(9039.6, abs=0.5)
