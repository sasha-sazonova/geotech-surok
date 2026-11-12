# -*- coding: utf-8 -*-
"""Сценарии YAML обязаны быть согласованы с проверенной редакцией нормы.

Причина появления этих тестов: сценарии — единственный способ посчитать «без
программирования», но ни один тест их не читал. За пару ревизий они разъехались
с кодом (γc1 = 1.1 вместо 1.2, γc2 = 1.1 вместо 1.0, граница толщи 0.2 вместо 0.5)
и никто этого не замечал, пока не появился раннер.
"""
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import run_scenario  # noqa: E402

SCENARIOS = sorted((ROOT / "scenarios").glob("d1-*.yaml"))


def test_scenarios_exist():
    assert SCENARIOS, "в scenarios/ нет ни одного сценария D1"


@pytest.mark.parametrize("path", SCENARIOS, ids=lambda p: p.stem)
def test_scenario_has_no_stale_warnings(path):
    params, warnings = run_scenario.load(path)
    assert warnings == [], f"{path.name}: сценарий разошёлся с нормой — {warnings}"


@pytest.mark.parametrize("path", SCENARIOS, ids=lambda p: p.stem)
def test_scenario_computes(path):
    from calc.d1_foundation import analyze

    params, _ = run_scenario.load(path)
    result = analyze(params)
    assert result["R_kPa"] > 0
    assert result["settlement"]["s_cm"] is not None
