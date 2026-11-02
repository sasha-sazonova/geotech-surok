# -*- coding: utf-8 -*-
"""СП 24.13330.2021 «Свайные фундаменты» — несущая способность одиночной сваи.

Источник: официальный текст (PDF, 82 с.), получен из публичного зеркала 03.11.2026;
текст сверен с изображениями страниц, значения закреплены тестами tests/test_sp24_piles.py.

Реализовано:

* п.7.2.1, ф.(7.5)–(7.7) — сваи-стойки на скальном грунте (Rm = Rc·Ks, Ks — табл. 7.1);
* п.7.2.4, ф.(7.9) — висячие забивные/вдавливаемые сваи;
* п.7.2.7, ф.(7.11) — выдёргивающая нагрузка;
* п.7.2.10, ф.(7.13) — набивные и буровые сваи (γR,f — табл. 7.6);
* табл. 7.3 — fi на боковой поверхности в глинистых грунтах (IL = 0.2…1.0);
* табл. 7.4 — γR,R, γR,f по способу погружения;
* табл. 7.1 — Ks (трещиноватость скального грунта).

Честные ограничения (возврат «не определено», не числа):

* табл. 7.2 (R под нижним концом): надёжно подтверждены только песчаные колонки;
  глинистые (IL = 0…0.6) в текстовом слое повреждены и пока НЕ включены — для глины
  под нижним концом расчёт отказывает;
* табл. 7.3: песчаные колонки (крупные/средней крупности, мелкие, пылеватые) в текстовом
  слое потеряны — для песка на боковой поверхности расчёт отказывает;
* сваи-оболочки, сваи-колонны, пирамидальные/ромбовидные сваи (7.10), камуфлетные
  уширения, наборные случаи 7.2.11б–в — вне области реализации.

Единицы: кН, м, кПа.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from .d1_foundation import UnverifiedNormValue


class Sp24Limitation(ValueError):
    """Случай, не покрытый подтверждённой частью СП 24."""


# ---------------- табл. 7.1: Ks — снижение прочности скального грунта ----------------
# (показатель трещиноватости ВОР, % → Ks)
KS_TABLE: Tuple[Tuple[float, float, float], ...] = (
    # (вор_от, вор_до, ks_от, ks_до)
    (90, 100, 1.00, 1.00),   # очень слаботрещиноватые
    (75, 90, 0.60, 1.00),    # слаботрещиноватые
    (50, 75, 0.32, 0.60),    # среднетрещиноватые
    (25, 50, 0.22, 0.32),    # сильнотрещиноватые
    (0, 25, 0.22, 0.22),     # очень сильнотрещиноватые
)


def ks_for_rock(vop_percent: float) -> float:
    """Ks по табл. 7.1. Для промежуточных ВОР — линейная интерполяция диапазона."""
    if not (0 <= vop_percent <= 100):
        raise ValueError(f"ВОР = {vop_percent}% вне диапазона 0…100")
    for lo, hi, ks_lo, ks_hi in KS_TABLE:
        if lo <= vop_percent <= hi:
            if hi == lo:
                return ks_lo
            frac = (vop_percent - lo) / (hi - lo)
            return ks_lo + (ks_hi - ks_lo) * frac
    raise ValueError("недостижимо")


# ---------------- табл. 7.3: fi на боковой поверхности, глинистые ----------------
T73_IL: Tuple[float, ...] = (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
T73_COHESIVE: Dict[int, Tuple[float, ...]] = {
    1:  (35, 23, 15, 12, 8, 4, 4, 3, 2),
    2:  (42, 30, 21, 17, 12, 7, 5, 4, 4),
    3:  (48, 35, 25, 20, 14, 8, 7, 6, 5),
    4:  (53, 38, 27, 22, 16, 9, 8, 7, 5),
    5:  (56, 40, 29, 24, 17, 10, 8, 7, 6),
    6:  (58, 42, 31, 25, 18, 10, 8, 7, 6),
    8:  (62, 44, 33, 26, 19, 10, 8, 7, 6),
    10: (65, 46, 34, 27, 19, 10, 8, 7, 6),
    15: (72, 51, 38, 28, 20, 11, 8, 7, 6),
    20: (79, 56, 41, 30, 20, 12, 8, 7, 6),
    25: (86, 61, 44, 32, 20, 12, 8, 7, 6),
    30: (93, 66, 47, 34, 21, 12, 9, 8, 7),
    35: (100, 70, 50, 36, 22, 13, 9, 8, 7),
    40: (107, 74, 53, 38, 23, 14, 9, 8, 7),
}


def f_lateral_cohesive(depth_m: float, IL: float) -> float:
    """fi (кПа) на боковой поверхности забивной сваи в глинистом грунте (табл. 7.3).

    Двумерная линейная интерполяция по глубине и по IL. Вне узлов глубины — интерполяция
    между соседними узлами; за пределами 1…40 м — экстраполяция запрещена (отказ).
    """
    if not (0.2 <= IL <= 1.0):
        raise UnverifiedNormValue(
            f"табл. 7.3: IL = {IL} вне диапазона 0.2…1.0")
    if not (1.0 <= depth_m <= 40.0):
        raise Sp24Limitation(
            f"табл. 7.3: глубина {depth_m} м вне диапазона таблицы 1…40 м")
    depths = sorted(T73_COHESIVE)
    d_lo = max(x for x in depths if x <= depth_m)
    d_hi = min(x for x in depths if x >= depth_m)
    il_lo = max(x for x in T73_IL if x <= IL + 1e-12)
    il_hi = min(x for x in T73_IL if x >= IL - 1e-12)
    v00 = T73_COHESIVE[d_lo][T73_IL.index(il_lo)]
    v01 = T73_COHESIVE[d_lo][T73_IL.index(il_hi)]
    v10 = T73_COHESIVE[d_hi][T73_IL.index(il_lo)]
    v11 = T73_COHESIVE[d_hi][T73_IL.index(il_hi)]
    fd = 0.0 if d_hi == d_lo else (depth_m - d_lo) / (d_hi - d_lo)
    fi = 0.0 if il_hi == il_lo else (IL - il_lo) / (il_hi - il_lo)
    top = v00 + (v01 - v00) * fi
    bot = v10 + (v11 - v10) * fi
    return top + (bot - top) * fd


# ---------------- табл. 7.4: γR,R, γR,f (забивные/вдавливаемые) ----------------
DRIVING_METHODS: Dict[str, Tuple[float, float]] = {
    # способ → (γR,R, γR,f)
    "hammer": (1.0, 1.0),                # п.1: молоты, сплошные/закрытый конец
    "leader_equal": (1.0, 0.5),          # п.2а: лидер = стороне/диаметру
    "leader_minus_005": (1.0, 0.6),      # п.2б: лидер на 0.05 м меньше
    "leader_minus_015": (1.0, 1.0),      # п.2в: лидер на 0.15 м меньше
    "jetting_compacted": (1.0, 0.9),     # п.3: подмыв с добивкой
}


def driving_factors(method: str) -> Tuple[float, float]:
    if method not in DRIVING_METHODS:
        raise Sp24Limitation(
            f"способ погружения '{method}' не подтверждён табл. 7.4 "
            f"(есть: {', '.join(sorted(DRIVING_METHODS))})")
    return DRIVING_METHODS[method]


# ---------------- табл. 7.6: γR,f для набивных/буровых ----------------
BORING_METHODS: Dict[str, Tuple[Tuple[float, ...], Tuple[float, ...]]] = {
    # способ → ((пески, супеси, суглинки, глины)) — строка таблицы
    "driven_pipe_tip": ((1.0, 1.0, 1.0, 0.9),),          # п.1: с теряемым наконечником/пробкой
    "vibro_stamped": ((0.9, 0.9, 0.9, 0.9),),            # п.2: виброштампованные
    "bored_dry": ((0.7, 0.7, 0.7, 0.6),),                # п.3а: сухим способом/обсадные/НПШ
    "bored_under_water": ((0.6, 0.6, 0.6, 0.6),),        # п.3б: под водой/раствором
    "bored_stiff_vibrated": ((0.8, 0.8, 0.8, 0.7),),     # п.3в: жёсткие смеси с вибрацией
    "barettes": ((0.6, 0.6, 0.6, 0.6),),                 # п.4: бареты
    "shell_vibrated": ((1.0, 0.9, 0.7, 0.6),),           # п.5: сваи-оболочки с выемкой
    "column_piles": ((0.7, 0.7, 0.7, 0.6),),             # п.6: сваи-столбы
    "injection_press": ((0.9, 0.8, 0.8, 0.8),),          # п.7: буроинъекц. с опрессовкой
    "injection_pulse": ((1.3, 1.3, 1.1, 1.1),),          # п.8: разрядно-импульсные
}
SOIL_COLUMNS = ("пески", "супеси", "суглинки", "глины")


def gamma_rf_bored(method: str, soil: str) -> float:
    """γR,f по табл. 7.6 для способа устройства и вида грунта."""
    if method not in BORING_METHODS:
        raise Sp24Limitation(f"способ '{method}' отсутствует в табл. 7.6")
    if soil not in SOIL_COLUMNS:
        raise Sp24Limitation(f"вид грунта '{soil}' вне колонок табл. 7.6")
    row = BORING_METHODS[method][0]
    return row[SOIL_COLUMNS.index(soil)]


# ---------------- п.7.2.1: сваи-стойки на скальном грунте ----------------

def end_bearing_rock(Rc: float, area: float, vop_percent: float = 100.0,
                     embedment_m: float = 0.0, diameter_m: float = 0.0) -> Dict[str, object]:
    """Fd по ф.(7.5)–(7.7), при заделке — ф.(7.8). Rc — предел прочности массива на
    одноосное сжатие в водонасыщенном состоянии, кПа (Rm = Rc·Ks, Ks — табл. 7.1).

    Ограничение нормы: R ≤ 20000 кПа (п.7.2.1, последний абзац).
    """
    if Rc <= 0 or area <= 0:
        raise ValueError("Rc и area должны быть положительными")
    ks = ks_for_rock(vop_percent)
    R = Rc * ks
    if embedment_m > 0 and diameter_m > 0:
        factor = 1.0 + 0.4 * embedment_m / diameter_m
        if factor > 3.0:
            factor = 3.0  # «фактор заглубления принимается не более 3»
        R = R * factor
    R = min(R, 20000.0)
    gamma_c = 1.0
    Fd = gamma_c * R * area
    return {"Fd_kN": Fd, "R_kPa": R, "Ks": ks, "gamma_c": gamma_c}


# ---------------- ф.(7.9): висячая забивная/вдавливаемая свая ----------------

@dataclass
class PileLayer:
    depth_mid_m: float   # средняя глубина расположения слоя, м (табл. 7.3)
    thickness_m: float   # hi — толщина слоя, м (≤ 2 м по прим. 2 к табл. 7.3)
    IL: float = None     # показатель текучести (для глинистых)


def driven_friction_pile(R_sand_kpa: Optional[float], area: float, perimeter_m: float,
                         layers: List[PileLayer], driving_method: str = "hammer",
                         gamma_c: float = 1.0,
                         dense_sand_CPT: bool = False) -> Dict[str, object]:
    """Fd по ф.(7.9): Fd = γc·(γR,R·R·A + u·Σ γR,f·fi·hi).

    R (табл. 7.2) — только для песчаного основания под нижним концом (глинистая часть
    таблицы не подтверждена → refusal). fi (табл. 7.3) — только глинистые слои (песчаные
    колонки таблицы не подтверждены → refusal).
    Примечание 3 к табл. 7.3: плотные пески +30 % — применяется, когда слои песка
    заданы; здесь не активируется (песчаные fi не читаются).
    """
    refusals: list = []
    gamma_rr, gamma_rf = driving_factors(driving_method)

    end_term = None
    if R_sand_kpa is not None:
        if dense_sand_CPT:
            R_sand_kpa = R_sand_kpa * 2.0  # прим. 4 (зондирование): +100 %, cap 20000
            R_sand_kpa = min(R_sand_kpa, 20000.0)
        end_term = gamma_rr * R_sand_kpa * area

    side_sum = 0.0
    for layer in layers:
        if layer.thickness_m <= 0:
            continue
        if layer.thickness_m > 2.0 + 1e-9:
            refusals.append(
                f"слой на глубине {layer.depth_mid_m} м: толщина {layer.thickness_m} м > 2 м "
                "(прим. 2 к табл. 7.3 требует расчленения на слои ≤ 2 м)")
            continue
        if layer.IL is None:
            refusals.append(
                f"слой на глубине {layer.depth_mid_m} м: песчаные fi табл. 7.3 не подтверждены "
                "(текстовый слой источника повреждён); требуется IL глинистого грунта или ручной ввод fi")
            continue
        try:
            fi = f_lateral_cohesive(layer.depth_mid_m, layer.IL)
        except (UnverifiedNormValue, Sp24Limitation) as exc:
            refusals.append(f"слой на глубине {layer.depth_mid_m} м: {exc}")
            continue
        side_sum += gamma_rf * fi * layer.thickness_m

    if end_term is None:
        refusals.append("R под нижним концом: для глинистого грунта табл. 7.2 не подтверждена; "
                        "задайте R_sand_kpa только при песчаном основании")
    if refusals:
        return {"status": "не определено", "Fd_kN": None, "refusals": refusals}

    Fd = gamma_c * (end_term + perimeter_m * side_sum)
    return {"status": "рассчитано", "Fd_kN": Fd,
            "gamma_R_R": gamma_rr, "gamma_R_f": gamma_rf,
            "end_term_kN": end_term, "side_term_kN": perimeter_m * side_sum,
            "refusals": []}


# ---------------- ф.(7.11): выдёргивающая нагрузка ----------------

def pulled_out_pile(perimeter_m: float, layers: List[PileLayer],
                    driving_method: str = "hammer", gamma_cu: float = 1.0) -> Dict[str, object]:
    """Fdu по ф.(7.11): Fdu = γcu·Σ γR,f·fi·hi — только боковая поверхность."""
    _, gamma_rf = driving_factors(driving_method)
    refusals: list = []
    total = 0.0
    for layer in layers:
        if layer.thickness_m <= 0:
            continue
        if layer.thickness_m > 2.0 + 1e-9:
            refusals.append(f"слой на глубине {layer.depth_mid_m} м: толщина > 2 м (прим. 2)")
            continue
        if layer.IL is None:
            refusals.append(f"слой на глубине {layer.depth_mid_m} м: песчаные fi не подтверждены")
            continue
        try:
            fi = f_lateral_cohesive(layer.depth_mid_m, layer.IL)
        except (UnverifiedNormValue, Sp24Limitation) as exc:
            refusals.append(str(exc))
            continue
        total += gamma_rf * fi * layer.thickness_m
    if refusals:
        return {"status": "не определено", "Fdu_kN": None, "refusals": refusals}
    return {"status": "рассчитано", "Fdu_kN": gamma_cu * perimeter_m * total, "refusals": []}


# ---------------- ф.(7.13): набивные и буровые сваи ----------------

def bored_pile(R_kpa: float, area: float, perimeter_m: float,
               layers: List[Tuple[float, float, Optional[float]]],
               boring_method: str = "bored_dry",
               soil_types: Optional[List[str]] = None,
               Sr_less_085_or_loess: bool = False) -> Dict[str, object]:
    """Fd по ф.(7.13): Fd = γc·(γR,R·R·A + γR,f·u·Σ fi·hi).

    R — по п.7.2.11 (табл. 7.2 для технологии а)–б) — передаётся готовым числом;
    γR,R = 1 (кроме камуфлетных/буроинъекционных — вне области);
    γc = 0.8 только для глинистых Sr < 0.85 и лессовых, иначе 1;
    γR,f — табл. 7.6 по способу и виду грунта каждого слоя.
    fi: передаются готовыми (кПа) через layers[i][2]; если None — refusal.
    """
    refusals: list = []
    gamma_rr = 1.0
    gamma_c = 0.8 if Sr_less_085_or_loess else 1.0
    side_sum = 0.0
    for idx, (depth_mid, hi, fi) in enumerate(layers):
        if fi is None:
            refusals.append(f"слой {idx}: fi не задан (табл. 7.3 пески не подтверждены)")
            continue
        if soil_types is None or idx >= len(soil_types):
            refusals.append(f"слой {idx}: не указан вид грунта для табл. 7.6")
            continue
        try:
            grf = gamma_rf_bored(boring_method, soil_types[idx])
        except Sp24Limitation as exc:
            refusals.append(f"слой {idx}: {exc}")
            continue
        side_sum += grf * fi * hi
    if refusals:
        return {"status": "не определено", "Fd_kN": None, "refusals": refusals}
    Fd = gamma_c * (gamma_rr * R_kpa * area + perimeter_m * side_sum)
    return {"status": "рассчитано", "Fd_kN": Fd, "gamma_c": gamma_c,
            "gamma_R_R": gamma_rr, "refusals": []}
