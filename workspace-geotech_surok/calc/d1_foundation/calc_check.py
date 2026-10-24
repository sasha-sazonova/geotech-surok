# -*- coding: utf-8 -*-
# Независимая реализация: шаг 0.2 м, отдельный код, те же формулы.
import json, os
D = dict(b=2.0, l=2.4, A=4.8, d=1.8, N=1200.0, gamma_f=20.0, gamma1=18.5, gamma_above=17.5,
         gamma_sb=9.0, phi=16.0, c=18.0, E_kPa=9000.0, WL=3.2, data_bottom=5.8, su_cm=10.0,
         params_source="tests", gst_coef=0.2)
if os.path.exists("scenario.json"):
    D.update(json.load(open("scenario.json", encoding="utf-8")))
b, A, d = D["b"], D["A"], D["d"]
p = D["N"] / A + D["gamma_f"] * d
gz0 = D["gamma_above"] * d
p0 = p - gz0
gII = D["gamma1"] if (D["WL"] - d) >= b / 2.0 else ((D["WL"] - d) * D["gamma1"] + (b / 2.0 - (D["WL"] - d)) * D["gamma_sb"]) / (b / 2.0)
k = 1.0 if D["params_source"] == "tests" else 1.1
R = (1.1 * 1.1 / k) * (0.36 * 1.0 * b * gII + 2.43 * 17.5 * d + 4.99 * 18.0)
tab = {0.0:1.000,0.2:0.983,0.4:0.966,0.6:0.898,0.8:0.830,1.0:0.747,1.2:0.664,1.4:0.590,
       1.6:0.516,1.8:0.458,2.0:0.401,2.2:0.358,2.4:0.316,2.6:0.285,2.8:0.253,3.0:0.230,
       3.2:0.207,3.4:0.189,3.6:0.171,3.8:0.157,4.0:0.144}
s = 0.0; Hc = None; trunc = True; z = 0.0
while z < 4.0 - 1e-9:
    z2 = min(z + 0.2, 4.0); zm = z + (z2 - z) / 2.0
    xi = 2.0 * zm / b
    keys = sorted(tab); lo = max(kk for kk in keys if kk <= xi); hi = min(kk for kk in keys if kk >= xi)
    a = tab[lo] if hi == lo else tab[lo] + (tab[hi] - tab[lo]) * (xi - lo) / (hi - lo)
    sp = a * p0
    s += 0.8 * sp * (z2 - z) / D["E_kPa"]
    sg = D["gamma_above"] * min(d + z2, D["WL"]) + D["gamma_sb"] * max(0.0, d + z2 - D["WL"])
    if sp <= D["gst_coef"] * sg:
        Hc = z2; trunc = False; break
    z = z2
print(json.dumps(dict(R_kPa=round(R,2), p_kPa=round(p,2), s_cm=round(s*100,3),
                      truncated=trunc, Hc_m=Hc, p0_kPa=round(p0,2), gamma_II=round(gII,3)), ensure_ascii=False, indent=1))
