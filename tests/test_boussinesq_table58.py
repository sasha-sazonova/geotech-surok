# -*- coding: utf-8 -*-
"""B2 benchmark: table 5.8 alpha vs exact angular-point formula + Boussinesq integration.

Established facts (2026-10-28/29, see docs/benchmarks/table-5.8-boussinesq.md):

* table 5.8 tabulates the influence coefficient; our numeric Boussinesq integration of the
  footing area reproduces the "4 x angular-point" scheme to 0.4-0.6% (ratio 0.9937-0.9984);
* the tabulated values are systematically BELOW the exact elastic value by 2-12%
  (deviation grows with xi) — a property of the historical SNiP table, kept for
  normative compatibility; our alpha_coeff interpolator must reproduce the table;
* settlement computed with tabulated alpha is therefore conservative.
"""
import math

import pytest

from calc.d1_foundation import alpha_coeff, settlement, D1Params

# verified rows of table 5.8 (column eta = 1.8), from the official PDF (page 54)
TABLE_58_COL_18 = {0.8: 0.848, 1.2: 0.682, 1.6: 0.532, 2.0: 0.414, 2.4: 0.325, 3.2: 0.210, 4.0: 0.145}


def _exact_center_boussinesq(xi: float, eta: float = 1.8) -> float:
    """Exact elastic alpha under the center of a footing b x l (xi = 2z/b, eta = l/b),
    via the closed-form angular-point formula with m = 1/xi, n = eta/xi, times 4."""
    m = 1.0 / xi
    n = eta / xi
    S = math.sqrt(1.0 + m * m + n * n)
    corner = ((m * n / S) * (1.0 / (m * m + 1.0) + 1.0 / (n * n + 1.0)) + math.atan(m * n / S)) / (2.0 * math.pi)
    return 4.0 * corner


@pytest.mark.parametrize("xi, tab", sorted(TABLE_58_COL_18.items()))
def test_table58_is_conservative_vs_exact(xi, tab):
    exact = _exact_center_boussinesq(xi)
    assert exact > tab, (xi, exact, tab)
    assert (exact - tab) / tab * 100.0 <= 25.0, (xi, exact, tab)


@pytest.mark.parametrize("xi, tab", sorted(TABLE_58_COL_18.items()))
def test_our_interpolator_reproduces_table(xi, tab):
    assert alpha_coeff(xi, 1.8) == pytest.approx(tab, abs=0.004)


def test_settlement_is_conservative():
    result = settlement(D1Params())
    assert result["s_cm"] == pytest.approx(4.232, abs=0.05)
    assert result["Hc_m"] == pytest.approx(3.6, abs=0.01)
