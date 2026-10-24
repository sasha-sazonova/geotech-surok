from calc.d1_foundation import D1Params, settlement


def test_step_independence():
    s = {h: settlement(D1Params(), h=h)["s_cm"] for h in (0.4, 0.2, 0.1)}
    base = s[0.4]
    for h, value in s.items():
        assert abs(value - base) / base <= 0.01, (h, value, base)
