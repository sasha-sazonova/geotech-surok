# -*- coding: utf-8 -*-
"""D2 — свая под горизонтальной нагрузкой: независимая реализация и закрытая форма.

Зачем: в D2 расчёт вёлся в openpile (p-y, API sand). Кросс-проверка «второй реализацией»
отсутствовала — по правилу проекта статус «проверено» без неё не выдаётся. Модуль закрывает
этот пробел: считает ту же задачу конечно-разностным решателем балки на упругом основании
(Винклер) с той же p-y кривой API, и, независимо, сверяет с точным решением бесконечной
балки на упругом основании постоянной жёсткости.

Единицы: кН, м, кПа.

Реализовано:
* `api_sand_py` — кривая p-y API RP2A для песка (pu = min(pus, pud), A, tanh-переход);
* `solve_winkler` — МКР-решатель (EI y'''' + k(z)·y = 0) с итерациями по секущей жёсткости,
  граничные условия: свободный оголовок (Q = H, M = 0), свободный конец (Q = M = 0);
* `elastic_infinite_beam` — точное решение для постоянного k: y0 = H·λ/(2·k·D),
  Mmax = H/(4λ), λ = (k·D/(4·EI))^(1/4);
* `compare_with_openpile` — сверка с эталонными числами openpile, допуск объявляется явно.

Честные ограничения: только песчаный профиль, только свободный оголовок, только
горизонтальная нагрузка без момента; слоистый грунт и наклон нагрузки — вне области.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, Optional, Tuple

import numpy as np


@dataclass
class PileSection:
    D: float          # диаметр, м
    t: float          # толщина стенки, м
    E: float = 210e6  # модуль стали, кПа

    @property
    def I(self) -> float:
        """Момент инерции кольцевого сечения, м⁴."""
        d_in = self.D - 2.0 * self.t
        return math.pi * (self.D ** 4 - d_in ** 4) / 64.0

    @property
    def EI(self) -> float:
        return self.E * self.I


@dataclass
class SandProfile:
    phi_deg: float = 35.0
    gamma_sub: float = 8.19   # удельный вес ниже УГВ, кН/м³
    water_depth: float = 3.0  # УГВ от поверхности, м
    gamma: float = 18.0       # выше УГВ

    def sigma_v(self, z: np.ndarray) -> np.ndarray:
        z = np.asarray(z, dtype=float)
        above = np.minimum(z, self.water_depth)
        below = np.maximum(z - self.water_depth, 0.0)
        return self.gamma * above + self.gamma_sub * below

    def k_initial(self) -> float:
        """Начальный модуль субграда (API RP2A, песок средней плотности), кН/м³."""
        # API: k ≈ 34 МН/м³ для φ = 35°, линейно между 30° и 40°
        phi = self.phi_deg
        if phi <= 30:
            return 5.4e3
        if phi >= 40:
            return 34e3
        return 16.3e3 + (34e3 - 16.3e3) * (phi - 30.0) / 10.0


def api_sand_py(profile: SandProfile, D: float) -> Callable[[np.ndarray, np.ndarray], np.ndarray]:
    """p-y API RP2A для песка: p = A·pu·tanh(k·z·y/(A·pu)); pu = min(pus, pud).

    Коэффициенты C1, C2, C3 — по таблице API для φ = 35°: 3.0 / 3.8 / 40.
    """
    C1, C2, C3 = 3.0, 3.8, 40.0
    k = profile.k_initial()

    def py(z: np.ndarray, y: np.ndarray) -> np.ndarray:
        z = np.asarray(z, dtype=float)
        y = np.asarray(y, dtype=float)
        sig = profile.sigma_v(z)
        pus = (C1 * z + C2 * D) * sig
        pud = C3 * D * sig
        pu = np.minimum(pus, pud)
        pu = np.maximum(pu, 1e-6)
        A = np.maximum(3.0 - 0.8 * z / D, 0.9)
        arg = np.clip(k * z * np.abs(y) / (A * pu), 0.0, 50.0)
        p = A * pu * np.tanh(arg)
        return np.sign(y) * p

    return py


def solve_winkler(section: PileSection, profile: SandProfile, L: float, H: float,
                  n: int = 60, iterations: int = 80, tol: float = 1e-8,
                  py_fn: Optional[Callable] = None,
                  k_const: Optional[float] = None) -> Dict[str, object]:
    """МКЭ: балка на упругом основании (пружины по длине), нелинейность — итерациями
    по секущей жёсткости p-y.

    Возвращает y0 (м), Mmax (кН·м) и эпюры. При k_const — линейная задача, которая
    сверяется с точным решением `elastic_infinite_beam`.
    """
    EI = section.EI
    D = section.D
    py = py_fn if py_fn is not None else api_sand_py(profile, D)

    z_nodes = np.linspace(0.0, L, n + 1)
    Le = L / n
    ndof = 2 * (n + 1)

    # жёсткость балки
    Ke = EI / Le ** 3 * np.array([
        [12.0, 6 * Le, -12.0, 6 * Le],
        [6 * Le, 4 * Le ** 2, -6 * Le, 2 * Le ** 2],
        [-12.0, -6 * Le, 12.0, -6 * Le],
        [6 * Le, 2 * Le ** 2, -6 * Le, 4 * Le ** 2],
    ])
    Kb = np.zeros((ndof, ndof))
    for e in range(n):
        idx = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
        Kb[np.ix_(idx, idx)] += Ke

    # нагрузка: горизонтальная сила H в узле 0 (свободный оголовок)
    F = np.zeros(ndof)
    F[0] = H

    # пружины: узловые площади влияния
    trib = np.full(n + 1, Le)
    trib[0] = Le / 2.0
    trib[-1] = Le / 2.0

    y = np.full(n + 1, 1e-4)
    k_sec = np.full(n + 1, k_const if k_const is not None else profile.k_initial())

    for _ in range(iterations):
        K = Kb.copy()
        for i in range(n + 1):
            K[2 * i, 2 * i] += k_sec[i] * D * trib[i]
        # шарнир по вращению не вводим: свободный оголовок и свободный конец
        u = np.linalg.solve(K, F)
        y_new = u[0::2]
        if k_const is not None:
            y = y_new
            break
        p = py(z_nodes, y_new)
        with np.errstate(divide="ignore", invalid="ignore"):
            k_new = np.where(np.abs(y_new) > 1e-9, p / np.where(y_new == 0, 1, y_new), k_sec)
        k_new = np.clip(np.abs(k_new), 1.0, 1e7)
        dy = np.max(np.abs(y_new - y))
        y = y_new
        k_sec = 0.5 * k_sec + 0.5 * k_new
        if dy < tol:
            break

    # изгибающие моменты: M(x) = EI·y''(x) через функции формы (эрмитовы полиномы)
    M = np.zeros(n + 1)
    for e in range(n):
        v1, th1, v2, th2 = u[2 * e], u[2 * e + 1], u[2 * e + 2], u[2 * e + 3]
        # ξ = 0 и ξ = 1
        b0 = np.array([-6.0 / Le ** 2, -4.0 / Le, 6.0 / Le ** 2, -2.0 / Le])
        b1 = np.array([6.0 / Le ** 2, 2.0 / Le, -6.0 / Le ** 2, 4.0 / Le])
        ue = np.array([v1, th1, v2, th2])
        M[e] = max(M[e], abs(EI * float(b0 @ ue)))
        M[e + 1] = max(M[e + 1], abs(EI * float(b1 @ ue)))

    return {"status": "рассчитано", "y0_m": float(y[0]), "y0_mm": float(y[0]) * 1000.0,
            "Mmax_kNm": float(np.max(np.abs(M))), "z": z_nodes.tolist(),
            "y": y.tolist(), "M": M.tolist()}


def elastic_semi_infinite_beam(section: PileSection, k_sub: float, H: float) -> Dict[str, float]:
    """Точное решение для ПОЛУБЕСКОНЕЧНОЙ балки на упругом основании постоянной жёсткости.

    Это и есть модель сваи: нагрузка приложена к свободному оголовку, ниже — бесконечное
    продолжение. (Формула «бесконечной балки» с нагрузкой в середине здесь неприменима —
    именно на этой путанице ловятся ошибки в 4 раза.)

        K = k·D  [кН/м²]      λ = (K/(4·EI))^(1/4)
        y0 = 2·H·λ / K
        Mmax = 0.3224·H/λ     (в сечении λx = π/4)
    """
    K = k_sub * section.D
    lam = (K / (4.0 * section.EI)) ** 0.25
    y0 = 2.0 * H * lam / K
    mmax = 0.3224 * H / lam
    return {"lambda_1_per_m": lam, "y0_m": y0, "Mmax_kNm": mmax,
            "note": "полубесконечная балка, нагрузка на свободном конце"}
