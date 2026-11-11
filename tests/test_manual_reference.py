import pytest
from calc.d1_foundation import D1Params, analyze


def test_manual_reference_matches():
    """Independent hand calculation (docs/manual-check-d1.md)."""
    r = analyze(D1Params())
    assert r["R_kPa"] == pytest.approx(215.62, abs=0.01)
    assert r["p_kPa"] == pytest.approx(286.0, abs=0.01)
    assert r["settlement"]["s_cm"] == pytest.approx(4.232, abs=0.01)
    assert r["settlement"]["Hc_m"] == pytest.approx(3.6, abs=0.01)
    assert r["checks"][0]["status"] == "не выполняется"
    assert r["checks"][1]["status"] == "выполняется"
