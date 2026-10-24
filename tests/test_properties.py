from hypothesis import given, settings, strategies as st
from calc.d1_foundation import D1Params, analyze, bearing_resistance, settlement

SET = settings(max_examples=40, deadline=None)


def R_of(**kw):
    return bearing_resistance(D1Params(**kw))["R_kPa"]


@SET
@given(st.floats(min_value=15, max_value=40), st.floats(min_value=15, max_value=40))
def test_R_monotonic_in_phi(phi1, phi2):
    lo, hi = sorted((phi1, phi2))
    assert R_of(phi_deg=lo) <= R_of(phi_deg=hi) + 1e-9


@SET
@given(st.floats(min_value=0, max_value=60), st.floats(min_value=0, max_value=60))
def test_R_monotonic_in_c(c1, c2):
    lo, hi = sorted((c1, c2))
    assert R_of(c_kpa=lo) <= R_of(c_kpa=hi) + 1e-9


@SET
@given(st.floats(min_value=1.0, max_value=6.0), st.floats(min_value=1.0, max_value=6.0))
def test_R_monotonic_in_b_dry(b1, b2):
    lo, hi = sorted((b1, b2))
    kw = dict(water_line=-50.0, gamma_above=18.5)
    assert R_of(b=lo, **kw) <= R_of(b=hi, **kw) + 1e-9


@SET
@given(st.floats(min_value=15.0, max_value=26.0), st.floats(min_value=15.0, max_value=26.0))
def test_R_monotonic_in_gamma(g1, g2):
    lo, hi = sorted((g1, g2))
    assert R_of(gamma_above=lo, water_line=-50.0) <= R_of(gamma_above=hi, water_line=-50.0) + 1e-9


def _s(params):
    return settlement(params)["s_cm"]


@SET
@given(st.floats(min_value=800.0, max_value=2400.0), st.floats(min_value=800.0, max_value=2400.0))
def test_settlement_monotonic_in_load(n1, n2):
    lo, hi = sorted((n1, n2))
    kw = dict(data_bottom=-40.0, layers=[__import__("calc.d1_foundation", fromlist=["Layer"]).Layer(top=0, bottom=-40, gamma=18.5, E_kpa=9000.0)])
    assert _s(D1Params(N=lo, **kw)) <= _s(D1Params(N=hi, **kw)) + 1e-9


@SET
@given(st.floats(min_value=3000.0, max_value=30000.0), st.floats(min_value=3000.0, max_value=30000.0))
def test_settlement_monotonic_in_E(e1, e2):
    from calc.d1_foundation import Layer
    lo, hi = sorted((e1, e2))
    def s_for(E):
        return _s(D1Params(data_bottom=-40.0, layers=[Layer(top=0, bottom=-40, gamma=18.5, E_kpa=E)]))
    assert s_for(lo) >= s_for(hi) - 1e-9
