from calc.d1_foundation import D1Params, analyze


def test_d1_base_golden(data_regression):
    data_regression.check(analyze(D1Params()))


def test_d1_resized_golden(data_regression):
    data_regression.check(analyze(D1Params(b=2.4, l=2.8)))
