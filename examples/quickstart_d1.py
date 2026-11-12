# -*- coding: utf-8 -*-
"""Быстрый старт: расчёт фундамента мелкого заложения по СП 22.13330.2016.

Запуск из корня репозитория:

    python examples/quickstart_d1.py

Поменяйте числа в блоке «ВАШИ ДАННЫЕ» — остальное считает библиотека.
Скрипт печатает R (расчётное сопротивление), p (среднее давление), осадку s,
границу сжимаемой толщи Hc и статусы проверок. Если данных не хватает,
вместо числа будет «не определено» — это штатный результат, а не ошибка.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from calc.d1_foundation import D1Params, Layer, analyze  # noqa: E402

# ------------------------- ВАШИ ДАННЫЕ -------------------------
params = D1Params(
    b=2.0,            # ширина подошвы, м
    l=2.4,            # длина подошвы, м
    d=1.8,            # глубина заложения, м
    N=1200.0,         # вертикальная нагрузка на фундамент, кН
    gamma_f=20.0,     # осреднённый удельный вес фундамента и грунта на уступах, кН/м³
    phi_deg=16.0,     # угол внутреннего трения φII, град
    c_kpa=18.0,       # удельное сцепление cII, кПа
    gamma_c1=1.2,     # табл. 5.4 (глинистые, 0.25 < IL < 0.5)
    gamma_c2=1.0,     # табл. 5.4 (L/H ≥ 4 или гибкая схема)
    water_line=-3.2,  # отметка уровня подземных вод, м (отрицательная вниз)
    data_bottom=-5.8, # самая низкая известная отметка грунта, м
    layers=[
        Layer(top=0.0, bottom=-1.8, gamma=17.5, E_kpa=9000.0),    # насыпь выше подошвы
        Layer(top=-1.8, bottom=-5.8, gamma=18.5, E_kpa=9000.0),   # ИГЭ-1
    ],
)
# ---------------------------------------------------------------

result = analyze(params)

print("R  (расчётное сопротивление) :", result["R_kPa"], "кПа")
print("p  (среднее давление)        :", result["p_kPa"], "кПа")
print("s  (осадка)                  :", result["settlement"]["s_cm"], "см")
print("Hc (сжимаемая толща)         :", result["settlement"]["Hc_m"], "м")
print()
def fmt(value, digits=2):
    return "—" if value is None else f"{value:.{digits}f}"


print("Проверки:")
for check in result["checks"]:
    print(f"  {check['id']:<10} {check['clause']}")
    print(f"             {fmt(check['value'])} против {fmt(check['criterion'])} → {check['status']}")
if result["refusals"]:
    print("\nЧто не посчитано и почему:")
    for item in result["refusals"]:
        print("  -", item)
