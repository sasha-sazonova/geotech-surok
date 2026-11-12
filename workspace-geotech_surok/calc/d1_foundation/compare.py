import json, os
base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
m = json.load(open(os.path.join(base, "result_main.json")))
c = json.load(open(os.path.join(base, "result_check.json")))
def dev(a, b): return abs(a - b) / max(abs(a), abs(b), 1e-12) * 100
res = {
 "R_kPa": {"main": m["R_kPa"], "check": c["R_kPa"], "dev_percent": round(dev(m["R_kPa"], c["R_kPa"]), 4), "within_5pct": dev(m["R_kPa"], c["R_kPa"]) <= 5},
 "s_cm": {"main": m["s_cm"], "check": c["s_cm"], "dev_percent": round(dev(m["s_cm"], c["s_cm"]), 4), "within_5pct": dev(m["s_cm"], c["s_cm"]) <= 5},
 "truncated_flag": {"main": m["truncated"], "check": c["truncated"], "match": bool(m["truncated"]) == bool(c["truncated"])},
 "p_kPa": {"main": m["p_kPa"], "check": c["p_kPa"], "match": m["p_kPa"] == c["p_kPa"]},
}
print(json.dumps(res, ensure_ascii=False, indent=1))
