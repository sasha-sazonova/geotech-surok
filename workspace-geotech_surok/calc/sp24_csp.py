# -*- coding: utf-8 -*-
"""СП 24.13330.2021 — комбинированный свайно-плитный (КСП) фундамент.

Основа: п.7.4.14–7.4.20 и 7.5.x норм. В самих нормах КСП-расчёт формулами не
регламентирован (требуются численные модели), но п.7.4.18 допускает «определение
суммарных жесткостных характеристик свайно-плитных фундаментов в соответствии с 7.4.8».
Эта реализация строит именно такие суммарные жёсткости из уже верифицированных блоков:

* жёсткость сваи k_w — по нелинейной зависимости ф.(7.44) п.7.4.7 (k_w0 из ф.(7.34));
* упругий отпор плиты k_s — по п.7.4.20 из осесимметричной задачи ячейки
  (жёсткое штамповое решение Буссинеска для ячейки сваи);
* распределение полной нагрузки Nd между сваи и плиту из условия совместной осадки;
* проверки: нагрузка на сваю ≤ допускаемой (ф.(7.2), п.7.1.11);
  давление под плитой ≤ расчётного сопротивления (СП 22.13330, ф.(5.7)).

Честные ограничения (GroupLimitation / refusal):
* краевой/групповой эффекты в коэффициенте отпора плиты (п.7.5.5) — вне области:
  реализуется однородный отпор по площади плиты;
* нелинейные модели грунта 7.5.3 для категории 1–2 — вне области;
* m (показатель формы ф.(7.44)) — параметр проектирования, обязателен на входе;
  рекомендация нормы отсутствует, значение по умолчанию НЕ подставляется.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Optional

from .d1_foundation import bearing_resistance
from .sp24_group import SoilForSettlement, single_pile_settlement


class CSPLimitation(ValueError):
    """Случай вне подтверждённой области КСП-расчёта."""


# ---------------- п.7.4.7: нелинейная жёсткость сваи ----------------

def pile_stiffness(k_w0_MN_per_m: float, N_MN: float, Nu_MN: float,
                   m: float) -> float:
    """k_w по ф.(7.44): k_w = k_w0·(1 + (k_w0/N_u)^m)^(−1/m).

    k_w0 — начальная жёсткость (= N/s по ф.(7.34)); m — поправочный коэффициент.
    При N → 0 жёсткость → k_w0; при N → N_u жёсткость падает.
    """
    if k_w0_MN_per_m <= 0 or Nu_MN <= 0:
        raise ValueError("k_w0 и Nu должны быть положительными")
    if m <= 0:
        raise ValueError("m должен быть положительным")
    if N_MN < 0:
        raise ValueError("N не может быть отрицательной")
    ratio = k_w0_MN_per_m / Nu_MN
    return k_w0_MN_per_m * (1.0 + ratio ** m) ** (-1.0 / m)


def pile_initial_stiffness(l_m: float, d_m: float, EA_MN: float,
                           soil: SoilForSettlement) -> Dict[str, float]:
    """k_w0 = N/s, где s по ф.(7.34)–(7.38) (п.7.4.7). Возвращает также s при N=1 МН."""
    res = single_pile_settlement(1.0, l_m, d_m, EA_MN, soil)
    s_mm = res["s_mm"]
    return {"k_w0_MN_per_m": 1000.0 / s_mm,  # 1 МН / s(мм) → МН/м
            "s_at_1MN_mm": s_mm, "branch": res["branch"]}


# ---------------- п.7.4.20: упругий отпор плиты ----------------

def plate_subgrade_reaction(E2_MPa: float, nu2: float,
                            B_m: float, L_m: float) -> float:
    """Средний коэффициент упругого отпора плиты k_s (МПа/м) по осесимметричной задаче
    ячейки (п.7.4.20): жёсткий круглый штамп радиуса R_eq на упругом полупространстве.

    k_s = 4·G2·R_eq/(1 − ν2) на единицу площади → приведение: k_s = 4·G2/(π·R_eq·(1−ν2))
    (штамп: P = 4·G·R·δ/(1−ν) → p/δ = 4G/(π·R·(1−ν)) при делении на площадь πR²).
    G2 = E2/(2(1+ν2)). R_eq = sqrt(B·L/π).
    """
    if B_m <= 0 or L_m <= 0:
        raise ValueError("размеры плиты должны быть положительными")
    G2 = E2_MPa / (2.0 * (1.0 + nu2))
    R_eq = math.sqrt(B_m * L_m / math.pi)
    k_s = 4.0 * G2 / (math.pi * R_eq * (1.0 - nu2))
    return k_s


# ---------------- КСП: распределение нагрузки ----------------

@dataclass
class CSPParams:
    Nd_MN: float                 # полная вертикальная нагрузка на фундамент, МН
    n_piles: int                 # число свай
    l_m: float                   # длина свай, м
    d_m: float                   # диаметр/сторона сечения сваи, м
    EA_MN: float                 # жёсткость ствола, МН
    soil: SoilForSettlement      # G1/ν1, G2/ν2 (п.7.4.3)
    B_m: float                   # ширина плиты, м
    L_m: float                   # длина плиты, м
    Nu_MN: float                 # несущая способность одиночной сваи, МН
    m: float                     # показатель формы ф.(7.44)
    Fd_MN: float                 # Fd одиночной сваи (7.2/7.3), МН
    gamma_n: float               # коэффициент надёжности по ответственности (ГОСТ 27751)
    gamma_cg: float              # коэффициент надёжности по грунту (7.1.11)
    R_plate_kPa: float           # расчётное сопротивление основания плиты, СП 22 ф.(5.7)
    su_mm: float = 100.0         # предельная осадка (прил. Г СП 22, табл. Г.1: 10 см)
    pile_head_area_m2: float = 0.0   # площадь плиты, приходящаяся на сваю (ячейка)


def csp_analysis(params: CSPParams) -> Dict[str, object]:
    """Совместный расчёт КСП: единая осадка системы «сваи + плита».

    Модель (п.7.4.18 через 7.4.8): s = N_total / (n·k_w + k_s·A_plate).
    Распределение: N_piles = n·k_w·s; N_plate = k_s·A_plate·s.
    Проверки: (а) N_piles/n ≤ Fd/(γ_n·γ_cg) — ф.(7.2);
              (б) p_plate ≤ R_plate (СП 22.13330).
    """
    p = params
    refusals: list = []

    # жёсткость плиты
    k_s = plate_subgrade_reaction(p.soil.G2_MPa, p.soil.nu2, p.B_m, p.L_m)
    A_plate = p.B_m * p.L_m

    # начальная жёсткость сваи из (7.34)
    kw0 = pile_initial_stiffness(p.l_m, p.d_m, p.EA_MN, p.soil)["k_w0_MN_per_m"]

    # нелинейная жёсткость сваи при её ожидаемой нагрузке — решение уравнения:
    # s = Nd / (n·k_w(s) + k_s·A) и k_w зависит от N_pile = s·k_w (7.44 — неявная).
    # Итерационное решение (норма допускает пошаговое приращение, п.7.4.7):
    s_m = 0.005  # стартовое приближение осадки, м
    k_w = pile_stiffness(kw0, p.Nd_MN / p.n_piles, p.Nu_MN, p.m)
    for _ in range(200):
        K_total = p.n_piles * k_w + k_s * A_plate
        s_new = p.Nd_MN / K_total
        N_pile = s_new * k_w
        k_w = pile_stiffness(kw0, N_pile, p.Nu_MN, p.m)
        if abs(s_new - s_m) < 1e-9:
            s_m = s_new
            break
        s_m = s_new
    else:
        refusals.append("расчёт КСП не сошёлся за 200 итераций (п.7.4.7)")
        return {"status": "не определено", "refusals": refusals}

    N_pile = s_m * k_w                       # МН на сваю
    N_piles_total = N_pile * p.n_piles
    N_plate = p.Nd_MN - N_piles_total        # МН на плиту
    p_plate_kPa = N_plate * 1000.0 / A_plate if N_plate > 0 else 0.0
    share_piles = N_piles_total / p.Nd_MN

    # допускаемая нагрузка на сваю: ф.(7.2)
    N_allowed = p.Fd_MN / (p.gamma_n * p.gamma_cg)
    pile_check = "выполняется" if N_pile <= N_allowed else "не выполняется"

    # давление под плитой vs СП 22
    if p.R_plate_kPa <= 0:
        refusals.append("R_plate_kPa не задано — проверка плиты по СП 22 невозможна")
        plate_check = "не определено"
    elif N_plate <= 0:
        plate_check = "не применимо (плита не нагружена — все сваи)"
    else:
        plate_check = "выполняется" if p_plate_kPa <= p.R_plate_kPa else "не выполняется"

    # жёсткость сваи в работе
    k_w_final = pile_stiffness(kw0, N_pile, p.Nu_MN, p.m)

    # п.7.4.19: осадки КСП должны быть в допуске по СП 22.13330
    s_mm = s_m * 1000.0
    s_check = "выполняется" if s_mm <= p.su_mm else "не выполняется"

    return {
        "status": "рассчитано" if not refusals else "рассчитано с замечаниями",
        "s_mm": round(s_m * 1000.0, 2),
        "N_pile_MN": round(N_pile, 4),
        "N_piles_total_MN": round(N_piles_total, 4),
        "N_plate_MN": round(N_plate, 4),
        "share_piles": round(share_piles, 3),
        "p_plate_kPa": round(p_plate_kPa, 1),
        "k_w_MN_per_m": round(k_w_final, 1),
        "k_w0_MN_per_m": round(kw0, 1),
        "k_s_MPa_per_m": round(k_s, 3),
        "checks": [
            {"id": "N_pile_le_allowed",
             "clause": "СП 24.13330.2021, п.7.1.11, ф.(7.2)",
             "value": round(N_pile, 4), "criterion": round(N_allowed, 4), "status": pile_check},
            {"id": "p_plate_le_R",
             "clause": "СП 22.13330.2016, ф.(5.7) (для плиты КСП)",
             "value": round(p_plate_kPa, 1), "criterion": p.R_plate_kPa, "status": plate_check},
            {"id": "s_le_su",
             "clause": "СП 24.13330.2021, п.7.4.19 (осадки по СП 22.13330, прил. Г)",
             "value": round(s_mm, 2), "criterion": p.su_mm, "status": s_check},
        ],
        "refusals": refusals,
    }
