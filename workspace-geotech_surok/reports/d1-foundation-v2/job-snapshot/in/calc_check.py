# -*- coding: utf-8 -*-
# D1 v2 — независимая реализация (другой шаг, без переиспользования кода main).
import json

b, l, A, d = 2.0, 2.4, 4.8, 1.8
N = 1200.0
p = N / A + 20.0 * d
gz0 = 17.5 * d
p0 = p - gz0

# γII по b/2: 1.8..2.8 м, УГВ на 3.2 м -> весь участок выше УГВ
gII = 18.5

R = (1.1 * 1.1 / 1.0) * (0.36 * 1.0 * b * gII + 2.43 * 17.5 * d + 4.99 * 18.0)

# осадка: шаг 0.2 м, явные коэффициенты α для ξ=2z/b (η=1.2)
tab = {0.0:1.000, 0.2:0.983, 0.4:0.966, 0.6:0.898, 0.8:0.830, 1.0:0.747,
       1.2:0.664, 1.4:0.590, 1.6:0.516, 1.8:0.458, 2.0:0.401, 2.2:0.358,
       2.4:0.316, 2.6:0.285, 2.8:0.253, 3.0:0.230, 3.2:0.207, 3.4:0.189,
       3.6:0.171, 3.8:0.157, 4.0:0.144}
s = 0.0; Hc = None; trunc = True
z = 0.0
while z < 4.0 - 1e-9:
    z2 = min(z + 0.2, 4.0)
    zm = z + (z2 - z) / 2.0
    xi = round(2.0 * zm / b, 1)
    # линейная интерполяция между узлами сетки 0.1 не нужна: xi попадает в узлы 0.1? используем ближайший/линейный
    keys = sorted(tab.keys())
    lo = max([k for k in keys if k <= xi]); hi = min([k for k in keys if k >= xi])
    a = tab[lo] if hi == lo else tab[lo] + (tab[hi] - tab[lo]) * (xi - lo) / (hi - lo)
    sp = a * p0
    s += 0.8 * sp * 0.2 / 9000.0
    sg = 17.5 * min(d + z2, 3.2) + 9.0 * max(0.0, d + z2 - 3.2)
    if sp <= 0.2 * sg:
        Hc = z2; trunc = False; break
    z = z2

print(json.dumps(dict(R_kPa=round(R,2), p_kPa=round(p,2), s_cm=round(s*100,3),
                      truncated=trunc, Hc_m=Hc, p0_kPa=round(p0,2)), ensure_ascii=False, indent=1))
