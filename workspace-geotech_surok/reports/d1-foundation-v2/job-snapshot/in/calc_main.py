# -*- coding: utf-8 -*-
# D1 v2: СП 22.13330.2016 — R (п.5.6.7, ф.5.7), осадка (прил. Г), su (прил. Д).
# Политика: см. procedures/calculation-status-policy.md. Эталон D1, вводные не менять.
import json, math

b, l, A, d = 2.0, 2.4, 4.8, 1.8
N = 1200.0
GAMMA_F = 20.0          # кН/м³ вес фундамента и грунта на уступах (условие сценария)
gamma1 = 18.5           # ИГЭ-1
gamma_above = 17.5
gamma_sb = 9.0
phi, c = 16.0, 18.0     # из ИГЭ (испытания) -> k=1.0
E = 9000.0              # кПа
WL = 3.2                # м от поверхности
DATA_BOTTOM = 5.8       # м от поверхности: ниже данных нет
SU_CM = 10.0
PARAMS_SOURCE = "tests" # tests -> k=1.0; tables -> k=1.1
GST_COEF = 0.2          # нижняя граница сжимаемой толщи: σzp <= 0.2·σzg (прил. Г; сверка примечания — в чек-листе)

p = N / A + GAMMA_F * d
sigma_zg0 = gamma_above * d

def sigma_zg(z):
    """Природное давление от поверхности, z — от поверхности."""
    return min(z, WL) * gamma_above + max(0.0, z - WL) * gamma_sb

def avg_gamma(z0, z1):
    """Осреднённый удельный вес в зоне [z0,z1] ниже подошвы (учёт УГВ)."""
    wl_rel = WL - d
    cuts = sorted(set([z0, z1] + ([wl_rel] if z0 < wl_rel < z1 else [])))
    tot = 0.0
    for a, bnd in zip(cuts[:-1], cuts[1:]):
        seg_mid = 0.5 * (a + bnd)
        g = gamma1 if seg_mid <= wl_rel else gamma_sb
        tot += g * (bnd - a)
    return tot / (z1 - z0)

gamma_II = avg_gamma(0.0, b / 2.0)   # зона b/2 ниже подошвы
gamma_IIp = gamma_above

Mg, Mq, Mc = 0.36, 2.43, 4.99        # табл. 5.5, φ=16°
gc1, gc2 = 1.1, 1.1                  # табл. 5.4; gc2 — допущение (геометрия здания не задана)
k = 1.0 if PARAMS_SOURCE == "tests" else 1.1
kz = 1.0

R = (gc1 * gc2 / k) * (Mg * kz * b * gamma_II + Mq * gamma_IIp * d + Mc * c)

# Осадка: σzp = α·p0, p0 = p − σzg0
p0 = p - sigma_zg0
BETA = 0.8
ALPHA_XI = [0.0, 0.4, 0.8, 1.2, 1.6, 2.0, 2.4, 2.8, 3.2, 3.6, 4.0, 4.4, 4.8, 5.2, 5.6, 6.0]
ALPHA_Y = [1.000, 0.966, 0.830, 0.664, 0.516, 0.401, 0.316, 0.253, 0.207, 0.171, 0.144, 0.122, 0.105, 0.091, 0.080, 0.071]

def alpha(xi):
    if xi <= ALPHA_XI[0]: return ALPHA_Y[0]
    for x0, x1, y0, y1 in zip(ALPHA_XI[:-1], ALPHA_XI[1:], ALPHA_Y[:-1], ALPHA_Y[1:]):
        if xi <= x1:
            return y0 + (y1 - y0) * (xi - x0) / (x1 - x0)
    return ALPHA_Y[-1]

h = 0.4
H_data = DATA_BOTTOM - d            # 4.0 м доступной толщи ниже подошвы
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
    s += BETA * sp * hh / E
    if sp <= GST_COEF * sg:
        Hc = z_next
        truncated = False
        break
    z = z_next

s_cm = s * 100.0
p_status = "выполняется" if p <= R else "не выполняется"
if s_cm > SU_CM:
    s_status = "не выполняется"
elif truncated:
    s_status = "не определено (толща обрезана на %.1f м)" % H_data
else:
    s_status = "выполняется"

out = dict(
    Mg=Mg, Mq=Mq, Mc=Mc, gamma_c1=gc1, gamma_c2=gc2, k=k, kz=kz,
    gamma_II=round(gamma_II, 3), gamma_IIp=gamma_IIp, params_source=PARAMS_SOURCE,
    R_kPa=round(R, 2), p_kPa=round(p, 2), p0_kPa=round(p0, 2),
    p_le_R=bool(p <= R), p_status=p_status,
    Hc_m=Hc, truncated=truncated, s_cm=round(s_cm, 3),
    s_lower_bound=bool(truncated), su_cm=SU_CM, s_le_su=bool(s_cm <= SU_CM), s_status=s_status,
)
print(json.dumps(out, ensure_ascii=False, indent=1))
