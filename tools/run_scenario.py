#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Запуск расчёта D1 из сценария YAML — без правки кода.

    python tools/run_scenario.py scenarios/d1-foundation.yaml
    python tools/run_scenario.py scenarios/d1-foundation.yaml --json

Сценарий описывает геометрию, нагрузку и грунт. Коэффициенты нормы (табл. 5.4/5.5/5.8)
библиотека берёт сама; если сценарий задаёт их вручную и значение расходится с проверенным
по официальному тексту — в выводе будет предупреждение, а не тихая подмена.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from calc.d1_foundation import D1Params, Layer, analyze  # noqa: E402

# Проверенные по официальному тексту значения (docs/norm-sources/sp22-2016.md).
VERIFIED = {
    "gamma_c1": (1.2, "табл. 5.4, глинистые 0.25 < IL < 0.5"),
    "gamma_c2": (1.0, "табл. 5.4, L/H ≥ 4 или гибкая схема"),
}


def load(path: pathlib.Path) -> tuple[D1Params, list[str]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    warnings: list[str] = []

    geom = data.get("geometry") or {}
    loads = data.get("loads") or {}
    soil = data.get("soil") or {}
    iges = {k: v for k, v in soil.items() if isinstance(v, dict) and "gamma_kNm3" in v}

    if not iges:
        raise SystemExit(
            f"{path}: сценарий не содержит слоёв грунта (soil.*.gamma_kNm3).\n"
            "Этот раннер считает только фундаменты мелкого заложения (D1).\n"
            "Свайные сценарии считаются отдельно: см. docs/status.md и reports/d2-pile/.")

    above = float(soil.get("above_base_gamma_kNm3", 17.5))
    ugv = float(soil.get("UGV_m", 0.0))
    water_line = -abs(ugv)  # в сценарии УГВ задан глубиной (положительное число вниз)
    data_bottom = -abs(float(soil.get("data_bottom_m", 5.8)))

    layers: list[Layer] = []
    layers.append(Layer(top=0.0, bottom=-abs(float(geom.get("d", 1.8))),
                        gamma=above, E_kpa=9000.0))
    top = -abs(float(geom.get("d", 1.8)))
    for name, ig in iges.items():
        thickness = float(ig.get("thickness_below_base_m", 0.0))
        if thickness <= 0:
            continue
        layers.append(Layer(top=top, bottom=top - thickness,
                            gamma=float(ig["gamma_kNm3"]),
                            E_kpa=float(ig.get("E_MPa", 9.0)) * 1000.0))
        top -= thickness

    assumptions = {a.get("name"): a.get("value") for a in (data.get("assumptions") or [])
                   if isinstance(a, dict)}
    for name, (expected, note) in VERIFIED.items():
        given = assumptions.get(name)
        if given is not None and abs(float(given) - expected) > 1e-9:
            warnings.append(
                f"{name} в сценарии = {given}, но по официальному тексту ({note}) = {expected}. "
                f"Использовано проверенное значение {expected}; сценарий устарел.")

    policy = data.get("calculation_policy") or {}
    if policy.get("gst_boundary_coef") not in (None, 0.5):
        warnings.append(
            f"calculation_policy.gst_boundary_coef = {policy.get('gst_boundary_coef')} — устарело: "
            "п.5.6.41 использует σzp ≈ 0.5·σzg, код считает по 0.5.")
    if policy.get("settlement_from") not in (None, "p0", "p"):
        warnings.append(f"calculation_policy.settlement_from = {policy.get('settlement_from')} — не распознано")

    params = D1Params(
        b=float(geom.get("b", 2.0)),
        l=float(geom.get("l", 2.4)),
        d=float(geom.get("d", 1.8)),
        N=float(loads.get("N", 0.0)),
        gamma_f=20.0,
        phi_deg=float(iges[list(iges)[0]].get("phi_deg", 16.0)),
        c_kpa=float(iges[list(iges)[0]].get("c_kPa", 18.0)),
        gamma_c1=1.2,
        gamma_c2=1.0,
        water_line=water_line,
        data_bottom=data_bottom,
        layers=layers,
    )
    return params, warnings


def main() -> int:
    ap = argparse.ArgumentParser(description="Расчёт D1 из сценария YAML")
    ap.add_argument("scenario", type=pathlib.Path)
    ap.add_argument("--json", action="store_true", help="вывести результат как JSON")
    args = ap.parse_args()

    params, warnings = load(args.scenario)
    result = analyze(params)
    result["scenario"] = str(args.scenario)
    result["warnings"] = warnings

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"Сценарий: {args.scenario}")
    print(f"b × l = {params.b} × {params.l} м, d = {params.d} м, N = {params.N} кН")
    print()
    def fmt(v, digits=2):
        return "—" if v is None else f"{v:.{digits}f}"
    print("R  (расчётное сопротивление):", fmt(result["R_kPa"]), "кПа")
    print("p  (среднее давление)       :", fmt(result["p_kPa"]), "кПа")
    print("s  (осадка)                 :", fmt(result["settlement"].get("s_cm")), "см")
    print("Hc (сжимаемая толща)        :", fmt(result["settlement"].get("Hc_m")), "м")
    print()
    for check in result["checks"]:
        print(f"  {check['id']}: {fmt(check['value'])} против {fmt(check['criterion'])} → {check['status']}")
    if result["refusals"]:
        print("\nНе посчитано:")
        for item in result["refusals"]:
            print("  -", item)
    if warnings:
        print("\nПредупреждения по сценарию:")
        for item in warnings:
            print("  !", item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
