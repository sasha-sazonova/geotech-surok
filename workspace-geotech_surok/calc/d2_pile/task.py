# -*- coding: utf-8 -*-
import json, math
from openpile.construct import Pile, CircularPileSection, SoilProfile, Layer, Model, BoundaryFixation
from openpile.soilmodels import API_sand

def model_for(lat, tag):
    pile = Pile(name=tag, sections=[CircularPileSection(top=0.0, bottom=-24.0, diameter=1.2, thickness=0.022)], material="Steel")
    soil = SoilProfile(name="sand", top_elevation=0.0, water_line=-3.0,
                       layers=[Layer(name="sand", top=0.0, bottom=-30.0, weight=18.0, lateral_model=lat)])
    return Model(name=tag, pile=pile, soil=soil, boundary_conditions=[BoundaryFixation(elevation=0.0, z=True)])

def run(tag, lat, H):
    try:
        m = model_for(lat, tag)
        m.set_pointload(elevation=0.0, Py=H)
        res = m.solve()
        d, f = res.displacements, res.forces
        head = d[d["Elevation [m]"] == 0.0].iloc[0]
        y = float(head["Deflection [m]"]) * 1000.0
        imax = f["M [kNm]"].abs().idxmax()
        M = float(f.loc[imax, "M [kNm]"]); zM = float(f.loc[imax, "Elevation [m]"])
        d.to_csv(f"../out/{tag}_H{int(H)}_disp.csv", index=False)
        f.to_csv(f"../out/{tag}_H{int(H)}_forces.csv", index=False)
        r = {"tag": tag, "H_kN": H, "y_head_mm": round(y, 3), "Mmax_kNm": round(M, 1), "z_Mmax_m": round(zM, 2), "ok": True}
    except Exception as e:
        r = {"tag": tag, "H_kN": H, "ok": False, "error": f"{type(e).__name__}: {str(e)[:200]}"}
    print(json.dumps(r, ensure_ascii=False))
    return r

out = {"runs": [], "meta": {}}
for H in (100.0, 500.0):
    out["runs"].append(run("api_k5000", API_sand(phi=35, initial_subgrade_modulus=5000.0), H))
for H in (100.0, 500.0):
    out["runs"].append(run("api_default", API_sand(phi=35), H))
try:
    from openpile.soilmodels import Dunkirk_sand
    out["meta"]["dunkirk_fields"] = list(Dunkirk_sand.model_fields.keys())
    for H in (100.0, 500.0):
        try:
            lat = Dunkirk_sand(Dr=0.75, phi=35)
        except Exception:
            lat = Dunkirk_sand(Dr=0.75)
        out["runs"].append(run("dunkirk", lat, H))
except Exception as e:
    out["meta"]["dunkirk_error"] = f"{type(e).__name__}: {str(e)[:150]}"

# линейность: y(500)/y(100)
def y_of(tag, H):
    for r in out["runs"]:
        if r.get("tag") == tag and r.get("H_kN") == H and r.get("ok"):
            return r["y_head_mm"]
    return None
out["meta"]["linearity_api_k5000"] = round(y_of("api_k5000", 500.0) / y_of("api_k5000", 100.0), 3) if y_of("api_k5000", 500.0) and y_of("api_k5000", 100.0) else None
out["meta"]["linearity_api_default"] = round(y_of("api_default", 500.0) / y_of("api_default", 100.0), 3) if y_of("api_default", 500.0) and y_of("api_default", 100.0) else None

# верхняя оценка Broms (песок, свободная голова, e=0): Hu ~ 0.5*gamma_avg*D*L^3*Kp/L
D, L = 1.2, 24.0
gamma_avg = (3 * 18.0 + (L - 3) * (18.0 - 9.81)) / L
Kp = math.tan(math.radians(45 + 35 / 2.0)) ** 2
out["meta"]["broms_Hu_kN"] = round(0.5 * gamma_avg * D * L ** 3 * Kp / L, 0)
json.dump(out, open("../out/d2_results.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
