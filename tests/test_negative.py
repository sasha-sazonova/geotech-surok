from calc.d1_foundation import D1Params, analyze


def test_missing_soil_data_refused():
    r = analyze(D1Params(data_bottom=-1.0))
    assert any("нет данных" in x for x in r["refusals"])
    assert r["settlement"]["status"].startswith("не определено")


def test_moment_refused():
    r = analyze(D1Params(moment_kNm=120.0))
    assert any("крен" in x for x in r["refusals"])


def test_deep_base_without_soil_data_refused():
    """d ≥ 5 м now computes the σzγ term, so the refusal must come from missing data."""
    r = analyze(D1Params(d=5.5))  # данные до -5.8 м, подошва -5.5 м → 0.3 м
    assert "вне данных" in r["settlement"]["status"]
    deep = analyze(D1Params(d=6.0))  # подошва ниже всех данных
    assert deep["settlement"]["s_cm"] is None
    assert "нет данных" in deep["settlement"]["status"]


def test_failed_check_is_a_number_not_a_refusal():
    r = analyze(D1Params())
    assert r["checks"][0]["status"] == "не выполняется"
    assert r["R_kPa"] > 0 and r["p_kPa"] > 0
