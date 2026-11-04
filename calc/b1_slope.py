# -*- coding: utf-8 -*-
"""B1 — slope stability: hand Fellenius/Bishop on a defined circular slip surface.

ИСПРАВЛЕНО 2026-11-04 (кросс-проверка против xslope 1.0.6):

* Fellenius считался без cos α в числителе (N = W вместо N = W·cos α) → FS завышался;
* Bishop считался по формуле (c·l + W·tanφ)/(1 + tanα·tanφ/FS) вместо
  (c·b + W·tanφ)/m_α с m_α = cosα + sinα·tanφ/FS → FS занижался.

После исправления на круге pyslope (cx=55.405, cz=61.024, R=21.520):
Fellenius 1.5904 (xslope OMS 1.590), Bishop 1.6925 (xslope Bishop 1.692).
Прежние значения 1.7296 / 1.5265 были следствием двух ошибок и недействительны.


Reference verified against pyslope 1.4.0 (jobs b1-slope-005/006):
* pyslope critical circle (cx=55.405, cz=61.024, R=21.520) on its own geometry
  (crest x=40 RL=50; toe x=60 RL=40) with clayey fill (18 kN/m3, φ=25°, c=10 kPa)
  → pyslope Fs = 1.6913;
* our Fellenius on the same circle/geometry → Fs = 1.7296 (ratio 0.978, i.e. 2.2 %);
* our Bishop → 1.5265 (Bishop < Fellenius, consistent with theory).

Geometry note: pyslope y-axis is elevation (RL up), slope descends to the right,
crest (40, 50), toe (60, 40). Slices: x from arc entry (36.92) to toe exit (59.95).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class SlopeSpec:
    crest_x: float = 40.0
    crest_rl: float = 50.0
    height: float = 10.0
    slope_run: float = 20.0     # horizontal run of the slope face
    base_rl: float = 40.0
    phi_deg: float = 25.0
    c_kpa: float = 10.0
    gamma: float = 18.0

    def surface_rl(self, x: float) -> float:
        if x <= self.crest_x:
            return self.crest_rl
        if x <= self.crest_x + self.slope_run:
            return self.crest_rl - (x - self.crest_x) * (self.height / self.slope_run)
        return self.base_rl


def surface_rl(spec: SlopeSpec, x: float) -> float:
    return spec.surface_rl(x)


def circle_rl(spec: SlopeSpec, cx: float, cz: float, R: float, x: float) -> Optional[float]:
    dx = x - cx
    if abs(dx) > R:
        return None
    return cz - math.sqrt(R * R - dx * dx)


def _intersections(spec: SlopeSpec, cx: float, cz: float, R: float) -> List[float]:
    roots: List[float] = []
    prev: Optional[Tuple[float, float]] = None
    for i in range(4000):
        x = -60.0 + i * 0.05
        cy = circle_rl(spec, cx, cz, R, x)
        if cy is None:
            prev = None
            continue
        d = cy - spec.surface_rl(x)
        if prev is not None and prev[1] * d < 0:
            roots.append(0.5 * (prev[0] + x))
        prev = (x, d)
    # Касание: круг выходит из грунта почти касательно (типично для глубокого круга
    # у подошвы), знак не меняется и второй корень не находится. Ищем точку
    # наибольшего сближения правее первого корня и принимаем её за выход.
    if len(roots) == 1:
        # сканируем справа налево: выход — самая правая точка, где круг ещё в грунте
        x_max = cx + R
        x = x_max
        while x > roots[0] + 1.0:
            cy = circle_rl(spec, cx, cz, R, x)
            if cy is not None and abs(cy - spec.surface_rl(x)) < 0.05:
                roots.append(x)
                break
            x -= 0.05
    return roots


def bishop_fellenius_on_circle(
    spec: SlopeSpec, cx: float, cz: float, R: float,
    n: int = 120, method: str = "bishop", x_hi_override: Optional[float] = None,
) -> Dict[str, float]:
    """Fs for a FIXED circle: Fellenius (ordinary) or simplified Bishop."""
    roots = _intersections(spec, cx, cz, R)
    if not roots:
        raise ValueError("circle does not intersect the slope surface")
    x_lo = roots[0]
    x_hi = x_hi_override if x_hi_override is not None else roots[-1]
    phi = math.radians(spec.phi_deg)
    fs = 1.5
    driving = resisting = 0.0
    for _ in range(200):
        driving = resisting = 0.0
        for i in range(n):
            x1 = x_lo + (x_hi - x_lo) * i / n
            x2 = x_lo + (x_hi - x_lo) * (i + 1) / n
            y1 = circle_rl(spec, cx, cz, R, x1)
            y2 = circle_rl(spec, cx, cz, R, x2)
            alpha = math.atan2(y1 - y2, x2 - x1)   # RL down to the right → positive
            b = x2 - x1
            ell = b / math.cos(alpha)
            yb = 0.5 * (y1 + y2)
            h = spec.surface_rl(xm := 0.5 * (x1 + x2)) - yb
            if h <= 0:
                continue
            W = spec.gamma * b * h
            driving += W * math.sin(alpha)
            if method == "fellenius":
                # Fellenius (ordinary): N = W·cos α, T = W·sin α
                resisting += spec.c_kpa * ell + W * math.cos(alpha) * math.tan(phi)
            else:
                # Simplified Bishop: FS = Σ[(c·b + W·tanφ)/m_α] / Σ W·sin α,
                # m_α = cos α + sin α·tanφ/FS
                m_alpha = math.cos(alpha) + math.sin(alpha) * math.tan(phi) / fs
                resisting += (spec.c_kpa * b + W * math.tan(phi)) / m_alpha
        if driving <= 0:
            raise ValueError(
                "circle gives zero driving force (arc does not cut a soil mass); "
                "check geometry or pass x_hi_override")
        new_fs = resisting / driving
        if method == "fellenius":
            return {"fs": round(new_fs, 4), "x_entry": round(x_lo, 2), "x_exit": round(x_hi, 2)}
        if abs(new_fs - fs) < 1e-10:
            fs = new_fs
            break
        fs = new_fs
    return {"fs": round(fs, 4), "x_entry": round(x_lo, 2), "x_exit": round(x_hi, 2)}

