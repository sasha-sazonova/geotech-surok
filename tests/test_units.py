import pytest
import pint
from calc.d1_foundation import D1Params, analyze

ureg = pint.UnitRegistry()
Q = ureg.Quantity


def test_R_dimensional_consistency():
    b, d = Q(2.0, "m"), Q(1.8, "m")
    g, c = Q(18.5, "kN/m**3"), Q(18.0, "kPa")
    expr = (Q(1.2, "") * Q(1.0, "") / Q(1.0, "")) * (
        Q(0.36, "") * Q(1.0, "") * b * g
        + Q(2.43, "") * Q(17.5, "kN/m**3") * d
        + Q(4.99, "") * c
    )
    assert expr.check("[pressure]")
    assert float(expr.to("kPa").magnitude) == pytest.approx(analyze(D1Params())["R_kPa"], rel=0.01)


def test_settlement_dimensions():
    term = Q(0.8, "") * Q(0.4, "m") * Q(286.0, "kPa") / Q(9000.0, "kPa")
    assert term.check("[length]")
    assert term.to("cm").magnitude == pytest.approx(1.017, rel=0.01)
