#!/usr/bin/env python3
"""Round 14 analysis (note 68): run A cells with the two-set comparison to the round-13 N3 cells, B1 and B2 cells.

  python3 superspreader/study/analyze_round14.py a      # 69_a_*.csv, 69_runA_two_set.csv
  python3 superspreader/study/analyze_round14.py b      # 69_b_*.csv (B1, B2 and the round-12 reference cells)
"""
import csv
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import analyze_round13 as a13  # noqa: E402
from r6stats import write_csv  # noqa: E402

OUT = HERE.parent
R14 = HERE / "results" / "round14"
R13 = HERE / "results" / "round13"
WORLDS = ("w1", "w2b", "w3b")


def dirs_of(base, prefix):
    return sorted(p.parent for p in (base / prefix).glob("rep*/trace.tsv"))


def a_cells():
    cells = []
    for w in WORLDS:
        for t in ("0.2", "0.5"):
            st = json.loads((R14 / "state" / f"r14_a-t{t}_{w}.json").read_text())
            cells.append({"cell": f"{w}:A_t{t}_s78", "world": w, "set": "s78", "kind": f"runA_t{t}", "dirs": dirs_of(R14, st["prefix"]),
                          "k": st["k"], "state": st})
            st13 = json.loads((R13 / "state" / f"r13_n3final-t{t}_{w}.json").read_text())
            cells.append({"cell": f"{w}:N3_t{t}_s77", "world": w, "set": "s77", "kind": f"n3_t{t}", "dirs": dirs_of(R13, st13["prefix"]),
                          "k": st13["k"], "state": st13})
    return cells


def b_cells():
    cells = []
    for w in WORLDS:
        rnd, label = a13.R12_STATES[w]
        st = json.loads((a13.RES / rnd / "state" / f"{label}.json").read_text())
        cells.append({"cell": f"{w}:ref_round12", "world": w, "set": "s77", "kind": "ref", "dirs": a13.cell_dirs(rnd, st["prefix"]),
                      "k": st["k"], "state": st})
        f1 = json.loads((R14 / "state" / f"b1_final_{w}.json").read_text())["final"]
        st = json.loads((R14 / "state" / f"r14_{f1['label']}_{w}.json").read_text()) if False else json.loads((R14 / "state" / f"{f1['label']}.json").read_text())
        cells.append({"cell": f"{w}:B1", "world": w, "set": "s77", "kind": "B1", "dirs": dirs_of(R14, st["prefix"]), "k": st["k"], "state": st,
                      "param": f1["param"]})
        b2p = R14 / "state" / f"b2_final_{w}.json"
        if b2p.exists():
            f2 = json.loads(b2p.read_text())
            fin = f2["final"]
            cells.append({"cell": f"{w}:B2", "world": w, "set": "s77", "kind": "B2", "dirs": dirs_of(R14, fin["label"]), "k": fin["coefficient"],
                          "state": {"points": []}, "param": fin["param"]})
    ext = R14 / "state" / "b2ext_final_w3b.json"
    if ext.exists():
        fe = json.loads(ext.read_text())["final"]
        cells.append({"cell": "w3b:B2_extended_search", "world": "w3b", "set": "s77", "kind": "B2ext", "dirs": dirs_of(R14, fe["label"]),
                      "k": fe["coefficient"], "state": {"points": []}, "param": fe["param"]})
    return cells


def tuning_logs():
    rows = []
    for w in WORLDS:
        for kind, name in (("B1", f"b1_trials_{w}.json"), ("B2", f"b2_trials_{w}.json"), ("B2ext", f"b2ext_trials_{w}.json")):
            path = R14 / "state" / name
            if path.exists():
                for t in json.loads(path.read_text()):
                    rows.append({"world": w, "stage": kind, "trial": t["iteration"], "tuned_parameter": t["param"], "coefficient": t["coefficient"],
                                 "day28_mean": t.get("day28", ""), "early_R": t.get("early_R", ""), "k_ml": t["k_ml"], "k_mom": t["k_mom"],
                                 "index_cases": t.get("index_cases", ""), "replicates": t.get("replicates", "")})
        for kind, name in (("B1_final", f"b1_final_{w}.json"), ("B2_final", f"b2_final_{w}.json"), ("B2ext_final", f"b2ext_final_{w}.json")):
            path = R14 / "state" / name
            if path.exists():
                for a in json.loads(path.read_text())["attempts"]:
                    rows.append({"world": w, "stage": kind, "trial": a["label"], "tuned_parameter": a["param"], "coefficient": a["coefficient"],
                                 "day28_mean": a.get("day28", ""), "early_R": a.get("early_R", ""), "k_ml": a["k_ml"], "k_mom": a.get("k_mom", ""),
                                 "index_cases": a.get("index_cases", ""), "replicates": a.get("replicates", "")})
    write_csv(OUT / "69_tuning_log.csv", rows)


def two_set():
    S = {r["cell"]: r for r in csv.DictReader(open(OUT / "69_a_cells_summary.csv"))}
    stats = [("k_ml", "likelihood k", 1), ("k_mom", "moment k", 1), ("k_ml_over_k_mom", "ratio", 1), ("share_0", "zero share (points)", 100),
             ("observed_minus_nb_zero", "observed minus NB zero (points)", 100), ("share_causing_80pct", "share causing 80% (points)", 100),
             ("infections_share_home", "home share (points)", 100), ("household_secondary_attack_rate", "household SAR", 1),
             ("top10_mean_offspring", "top-10 offspring", 1), ("top10_mean_same_household_share", "top-10 same-household share (points)", 100),
             ("top10_mean_largest_venue_day_share", "top-10 venue-day share (points)", 100), ("top10_mean_distinct_venues", "top-10 distinct venues", 1),
             ("early_R", "early R", 1), ("share_above_5", "share above five (points)", 100)]
    rows = []
    for w in WORLDS:
        for t in ("0.2", "0.5"):
            a, b = S[f"{w}:N3_t{t}_s77"], S[f"{w}:A_t{t}_s78"]
            for key, name, sc in stats:
                x, y = float(a[key]) * sc, float(b[key]) * sc
                sa, sb = a.get(key + "_boot_sd", ""), b.get(key + "_boot_sd", "")
                se = math.hypot(float(sa) * sc, float(sb) * sc) if sa not in ("", None) and sb not in ("", None) else float("nan")
                rows.append({"world": w, "target": t, "statistic": name, "round13_cell_s77": x, "runA_cell_s78": y, "difference": y - x,
                             "combined_se": se, "z": (y - x) / se if se and se == se else float("nan")})
    write_csv(OUT / "69_runA_two_set.csv", rows)
    return rows


def main():
    which = sys.argv[1]
    if which == "a":
        a13.cells_export("69_a", cells=a_cells())
        two_set()
    elif which == "b":
        a13.cells_export("69_b", cells=b_cells())
        tuning_logs()


if __name__ == "__main__":
    main()
