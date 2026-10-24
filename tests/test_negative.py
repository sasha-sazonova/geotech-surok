from calc.d1_foundation import D1Params, analyze


def test_missing_soil_data_refused():
    r = analyze(D1Params(data_bottom=-1.0))
    assert any("нет данных" in x for x in r["refusals"])
    assert r["settlement"]["status"].startswith("не определено")


def test_moment_refused():
    r = analyze(D1Params(moment_kNm=120.0))
    assert any("крен" in x for x in r["refusals"])


def test_deep_base_settlement_refused():
    r = analyze(D1Params(d=5.5))
    assert "σzγ" in r["settlement"]["status"]


def test_failed_check_is_a_number_not_a_refusal():
    r = analyze(D1Params())
    assert r["checks"][0]["status"] == "не выполняется"
    assert r["R_kPa"] > 0 and r["p_kPa"] > 0
