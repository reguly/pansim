#!/usr/bin/env python3
"""R7-0 static facts: window sums, repertoire sizes per agent type and location type, L by location type."""
import json, sys, collections, statistics
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "superspreader"
import csv
def write(path, rows):
    keys = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n"); w.writeheader(); w.writerows(rows)
    print("wrote", path.name)

rep_rows = []
for label in ("agents2", "agents4"):
    d = json.load(open(ROOT / "inputRealExample" / f"{label}.json"))
    people = d["people"]
    per = collections.defaultdict(lambda: collections.defaultdict(list))   # agent type -> loc type -> counts
    for p in people:
        c = collections.Counter(l["typeID"] for l in p.get("locations", []))
        for t in (1, 5, 6, 7, 8, 9, 10, 2, 3, 4, 13, 33, 44):
            per[p["typeID"]][t].append(c.get(t, 0))
    for at in sorted(per):
        for t, v in sorted(per[at].items()):
            v = sorted(v); n = len(v)
            q = lambda f: v[min(n - 1, int(f * n))]
            rep_rows.append({"file": label, "agent_type": at, "location_type": t, "agents": n,
                             "with_any": sum(1 for x in v if x > 0), "mean": sum(v) / n,
                             "p50": q(0.5), "p90": q(0.9), "p99": q(0.99), "max": v[-1]})
    del d, people
write(OUT / "47_r70_repertoire.csv", rep_rows)

loc_rows = []
for label in ("locations1", "locations3"):
    d = json.load(open(ROOT / "inputRealExample" / f"{label}.json"))
    by = collections.defaultdict(list)
    for p in d["places"]:
        by[p["type"]].append(p)
    for t, ps in sorted(by.items()):
        inf = [float(p.get("infectious", 0)) for p in ps]
        cap = [float(p.get("capacity", 0)) for p in ps]
        loc_rows.append({"file": label, "location_type": t, "places": len(ps),
                         "L_mean": statistics.mean(inf), "L_min": min(inf), "L_max": max(inf),
                         "capacity_mean": statistics.mean(cap), "capacity_max": max(cap)})
write(OUT / "47_r70_location_L.csv", loc_rows)
