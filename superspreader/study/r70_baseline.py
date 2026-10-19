#!/usr/bin/env python3
"""R7-0: realised baseline mobility by agent type, day type and well-being state from a --mobilityLog file."""
import csv, collections, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "superspreader" / "study" / "results" / "round7" / "r70" / "mob_baseline.csv"
names = {1: "Infant", 2: "Kindergarden student", 3: "Elementary school student", 4: "High school student", 5: "university student",
         6: "Full time worker", 7: "afternoon shift worker", 8: "stay-at-home", 9: "tourist"}
rows = list(csv.DictReader(open(src)))
groups = ["home", "school", "work", "disc", "inst", "other"]
acc = collections.defaultdict(lambda: collections.defaultdict(float)); n = collections.Counter()
for r in rows:
    t = int(r["type"]); n[t] += 1; a = acc[t]
    for k, v in r.items():
        if k in ("agent", "type", "age"): continue
        a[k] += float(v)
out = []
for t in sorted(n):
    a = acc[t]; c = n[t]
    dwd = a["days_weekday"] / c; dwe = a["days_weekend"] / c
    for dt, days, suffix in (("WEEKDAY", dwd, "wd"), ("WEEKEND", dwe, "we")):
        if days == 0: continue
        row = {"agent_type": t, "name": names.get(t, ""), "day_type": dt, "agents": c, "days_observed": days,
               "disc_visits_per_day": a["visits_" + suffix] / c / days,
               "moves_per_day": a["moves_" + ("weekday" if suffix == "wd" else "weekend")] / c / days,
               "distinct_disc_venues_per_day": a["distinct_day_" + suffix] / c}
        hd = a[f"h_{suffix}_role_disc"] / c / days
        row["disc_hours_per_day_role"] = hd
        row["mean_disc_visit_hours"] = hd / row["disc_visits_per_day"] if row["disc_visits_per_day"] else None
        for g in groups: row[f"hours_role_{g}"] = a[f"h_{suffix}_role_{g}"] / c / days
        for g in groups: row[f"hours_phys_{g}"] = a[f"h_{suffix}_phys_{g}"] / c / days
        row["distinct_disc_venues_per_week"] = a["distinct_week"] / c
        out.append(row)
keys = list(out[0].keys())
with open(ROOT / "superspreader" / "47_r70_baseline_mobility.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
    w.writeheader()
    for r in out: w.writerow({k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in r.items()})
# by state (all days): discretionary hours by state and infectious hours by state, per agent type
st = []
for t in sorted(n):
    a = acc[t]; c = n[t]
    tot_days = (a["days_weekday"] + a["days_weekend"]) / c
    st.append({"agent_type": t, "name": names.get(t, ""), "agents": c,
               **{f"disc_hours_per_agent_day_{s}": a[f"hdisc_{s}"] / c / tot_days for s in "WNMS"},
               **{f"infectious_hours_{s}": a[f"hinf_{s}"] for s in "WNMS"}})
with open(ROOT / "superspreader" / "47_r70_state_hours.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(st[0].keys()), lineterminator="\n"); w.writeheader()
    for r in st: w.writerow({k: (f"{v:.4g}" if isinstance(v, float) else v) for k, v in r.items()})
tot = {s: sum(r[f"infectious_hours_{s}"] for r in st) for s in "WNMS"}
print("infectious hours by state", tot, {s: round(tot[s] / sum(tot.values()), 3) for s in tot})
for r in out: print(r["agent_type"], r["day_type"][:2], round(r["disc_visits_per_day"], 2), round(r["disc_hours_per_day_role"], 2), r["mean_disc_visit_hours"] and round(r["mean_disc_visit_hours"], 2), round(r["moves_per_day"], 1), round(r["distinct_disc_venues_per_day"], 2), round(r["distinct_disc_venues_per_week"], 1))
