# -*- coding: utf-8 -*-
# D1 v3: параметры из scenario.json (фолбэк — базовая D1). Политика: procedures/calculation-status-policy.md
import json, os, math

D = dict(b=2.0, l=2.4, A=4.8, d=1.8, N=1200.0, gamma_f=20.0,
         gamma1=18.5, gamma_above=17.5, gamma_sb=9.0, phi=16.0, c=18.0, E_kPa=9000.0,
         WL=3.2, data_bottom=5.8, su_cm=10.0, params_source="tests", gst_coef=0.2,
         Mg=0.36, Mq=2.43, Mc=4.99, gc1=1.1, gc2=1.1, kz=1.0)
if os.path.exists("scenario.json"):
    D.update(json.load(open("scenario.json", encoding="utf-8")))

b, l, A, d = D["b"], D["l"], D["A"], D["d"]
p = D["N"] / A + D["gamma_f"] * d
sigma_zg0 = D["gamma_above"] * d

def sigma_zg(z):
    return min(z, D["WL"]) * D["gamma_above"] + max(0.0, z - D["WL"]) * D["gamma_sb"]

def avg_gamma(z0, z1):
    wl_rel = D["WL"] - d
    cuts = sorted(set([z0, z1] + ([wl_rel] if z0 < wl_rel < z1 else [])))
    tot = 0.0
    for a, bnd in zip(cuts[:-1], cuts[1:]):
        g = D["gamma1"] if 0.5 * (a + bnd) <= wl_rel else D["gamma_sb"]
        tot += g * (bnd - a)
    return tot / (z1 - z0)

gamma_II = avg_gamma(0.0, b / 2.0)
gamma_IIp = D["gamma_above"]
k = 1.0 if D["params_source"] == "tests" else 1.1

R = (D["gc1"] * D["gc2"] / k) * (D["Mg"] * D["kz"] * b * gamma_II
                                 + D["Mq"] * gamma_IIp * d + D["Mc"] * D["c"])

p0 = p - sigma_zg0
ALPHA_XI = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.6, 4.0, 4.4, 4.8, 5.2, 5.6, 6.0]
ALPHA_Y = [1.000, 0.966, 0.830, 0.664, 0.516, 0.401, 0.316, 0.253, 0.207, 0.171, 0.144, 0.122, 0.105, 0.091, 0.080, 0.071]

def alpha(xi):
    if xi <= ALPHA_XI[0]:
        return ALPHA_Y[0]
    for x0, x1, y0, y1 in zip(ALPHA_XI[:-1], ALPHA_XI[1:], ALPHA_Y[:-1], ALPHA_Y[1:]):
        if xi <= x1:
            return y0 + (y1 - y0) * (xi - x0) / (x1 - x0)
    return ALPHA_Y[-1]

h = 0.4
H_data = D["data_bottom"] - d
s = 0.0
Hc = None
truncated = True
z = 0.0
while z < H_data - 1e-9:
    z_next = min(z + h, H_data)
    hh = z_next - z
    zm = z + hh / 2.0
    sp = alpha(2.0 * zm / b) * p0
    sg = sigma_zg(d + z_next)
    s += 0.8 * sp * hh / D["E_kPa"]
    if sp <= D["gst_coef"] * sg:
        Hc = z_next
        truncated = False
        break
    z = z_next

s_cm = s * 100.0
p_status = "выполняется" if p <= R else "не выполняется"
if s_cm > D["su_cm"]:
    s_status = "не выполняется"
elif truncated:
    s_status = "не определено (толща обрезана на %.1f м)" % H_data
else:
    s_status = "выполняется"

print(json.dumps(dict(
    scenario_id=D.get("scenario_id", "d1-foundation"), b=b, l=l, A=A, d=d,
    Mg=D["Mg"], Mq=D["Mq"], Mc=D["Mc"], gamma_c1=D["gc1"], gamma_c2=D["gc2"], k=k, kz=D["kz"],
    gamma_II=round(gamma_II, 3), gamma_IIp=gamma_IIp, params_source=D["params_source"],
    R_kPa=round(R, 2), p_kPa=round(p, 2), p0_kPa=round(p0, 2), p_le_R=bool(p <= R), p_status=p_status,
    Hc_m=Hc, truncated=truncated, s_cm=round(s_cm, 3), s_lower_bound=bool(truncated),
    su_cm=D["su_cm"], s_le_su=bool(s_cm <= D["su_cm"]), s_status=s_status), ensure_ascii=False, indent=1))
