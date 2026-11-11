# -*- coding: utf-8 -*-
import json
from openpile.construct import Pile, CircularPileSection, SoilProfile, Layer, Model, BoundaryFixation
from openpile.soilmodels import Dunkirk_sand

def run(tag, lat, H):
    try:
        pile = Pile(name=tag, sections=[CircularPileSection(top=0.0, bottom=-24.0, diameter=1.2, thickness=0.022)], material="Steel")
        soil = SoilProfile(name="sand", top_elevation=0.0, water_line=-3.0,
                           layers=[Layer(name="sand", top=0.0, bottom=-30.0, weight=18.0, lateral_model=lat)])
        m = Model(name=tag, pile=pile, soil=soil, boundary_conditions=[BoundaryFixation(elevation=0.0, z=True)])
        m.set_pointload(elevation=0.0, Py=H)
        res = m.solve()
        d, f = res.displacements, res.forces
        y = float(d[d["Elevation [m]"] == 0.0].iloc[0]["Deflection [m]"]) * 1000.0
        imax = f["M [kNm]"].abs().idxmax()
        return {"tag": tag, "H_kN": H, "y_head_mm": round(y, 3),
                "Mmax_kNm": round(float(f.loc[imax, "M [kNm]"]), 1),
                "z_Mmax_m": round(float(f.loc[imax, "Elevation [m]"]), 2), "ok": True}
    except Exception as e:
        return {"tag": tag, "H_kN": H, "ok": False, "error": f"{type(e).__name__}: {str(e)[:180]}"}

out = []
for H in (100.0, 500.0):
    out.append(run("dunkirk", Dunkirk_sand(Dr=0.75, G0=80e3), H))
    print(json.dumps(out[-1], ensure_ascii=False))
json.dump(out, open("../out/d2_dunkirk.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
