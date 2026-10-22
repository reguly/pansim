#!/usr/bin/env python3
"""Note 68 round 14: run A (second seed set for the N3 cells), B1 (likelihood k 0.27 at the usual matching) and
B2 (likelihood k 0.27 at mean offspring 0.88, day 28 not matched). World definitions, flags and file locations are
those of round 13 (run_round13.py); only seeds, coefficient and the tuned parameter differ.

  PANSIM_JOBS=2 python3 superspreader/study/run_round14.py runA <world> <target>   # target 0.2 or 0.5
  PANSIM_JOBS=2 python3 superspreader/study/run_round14.py b1 <world>
  PANSIM_JOBS=2 python3 superspreader/study/run_round14.py b2 <world>
"""
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
os.environ.setdefault("PANSIM_BIN", str(HERE.parent.parent / "build_r10" / "panSim"))
sys.path.insert(0, str(HERE))

import run_round6 as r6  # noqa: E402
import run_x21  # noqa: E402
import run_round13 as r13  # noqa: E402
import analyze_round13 as a13  # noqa: E402
from r6stats import ml_k, mom_k  # noqa: E402

RESULTS = HERE / "results" / "round14"
STATE = RESULTS / "state"
run_x21.RESULTS = RESULTS
r6.RESULTS = RESULTS
r6.STATE = STATE
R13STATE = HERE / "results" / "round13" / "state"
TARGET = 6211.25
CAL_SEEDS = list(range(76001, 76007))


def seeds(first, n=12):
    return list(range(first, first + n))


def measure(dirs):
    cores = [a13.replicate_core(d) for d in dirs]
    total = np.concatenate([c[2] for c in cores])
    return {"R": float(total.mean()), "k_ml": float(ml_k(total)), "k_mom": float(mom_k(total)), "index_cases": int(total.size),
            "replicates": len(dirs), "day28": float(np.mean([c[0]["day28_cumulative_infections"] for c in cores]))}


def pfmt(p):
    return f"{p:.4g}"


def log_json(path, obj):
    r6.save_json(path, obj)


def run_cell(label, world, coeff, param, seed_list, weeks=4):
    """Fixed coefficient and parameter, no day-28 matching. Runs into RESULTS/label/repNN (existing runs are kept)."""
    make = r13.make_for(world, pfmt(param))
    batch = []
    for i, sd in enumerate(seed_list, start=1):
        name = f"{label}/rep{i:02d}"
        batch.append((name, make(coeff, sd, weeks, RESULTS / name)))
    r6.run_many(batch, r13.job_for(world))
    return [RESULTS / n for n, _ in batch]


# ---------------------------------------------------------------- run A

def run_a(world, target):
    d = json.loads((R13STATE / f"n3_final_{world}_{float(target):g}.json").read_text())
    param, coeff = d["param"], d["coefficient"]
    label = f"r14_a-t{float(target):g}_{world}"
    st = r6.match(label, r13.make_for(world, pfmt(param)), coeff, seeds(78001), 4, TARGET, r13.job_for(world), pilot=4)
    log_json(STATE / f"a_param_{world}_{float(target):g}.json", {"param": param, "start_coefficient": coeff, "coefficient": st["k"],
                                                                   "day28": st["day28"], "matched": st["matched"]})
    print(f"R14 A {world} target {target}: param={param} k={st['k']:.6g} day28={st['day28']:.0f} matched={st['matched']}", flush=True)


# ---------------------------------------------------------------- B1

B1_START = {"w1": (0.24, 0.000535, 1.06), "w2b": (0.40, 0.000117, 1.42), "w3b": (0.17, 0.000108, -0.90)}
B_TARGET = 0.27


def next_param(trials, slope0, target=B_TARGET):
    """Log-log secant on the last two trials (falls back to the starting slope)."""
    last = trials[-1]
    slope = slope0
    if len(trials) >= 2:
        a, b = trials[-2], trials[-1]
        if a["param"] != b["param"] and a["k_ml"] != b["k_ml"] and a["k_ml"] > 0 and b["k_ml"] > 0:
            sl = (math.log(b["param"]) - math.log(a["param"])) / (math.log(b["k_ml"]) - math.log(a["k_ml"]))
            if sl * slope0 > 0 and 0.4 * abs(slope0) <= abs(sl) <= 3 * abs(slope0):
                slope = sl
    return last["param"] * math.exp(slope * (math.log(target) - math.log(last["k_ml"]))), slope


def b1(world):
    p, c, slope0 = B1_START[world]
    log_path = STATE / f"b1_trials_{world}.json"
    trials = json.loads(log_path.read_text()) if log_path.exists() else []
    for it in range(4):
        if len(trials) > it:
            continue
        if it >= 1:
            p, _ = next_param(trials, slope0)
            c = trials[-1]["coefficient"]
        label = f"r14_b1trial-i{it + 1}_{world}"
        st = r6.match(label, r13.make_for(world, pfmt(p)), c, CAL_SEEDS, 4, TARGET, r13.job_for(world))
        dirs = sorted(x.parent for x in (RESULTS / st["prefix"]).glob("rep*/trace.tsv"))
        m = measure(dirs)
        trials.append({"iteration": it + 1, "param": float(pfmt(p)), "coefficient": st["k"], "day28": st["day28"],
                       "matched": st["matched"], "k_ml": m["k_ml"], "k_mom": m["k_mom"], "early_R": m["R"],
                       "index_cases": m["index_cases"], "replicates": m["replicates"]})
        log_json(log_path, trials)
        print(f"R14 B1 {world} trial {it + 1}: param={p:.4g} coeff={st['k']:.5g} day28={st['day28']:.0f} k_ml={m['k_ml']:.3f} R={m['R']:.3f}", flush=True)
        if abs(m["k_ml"] - B_TARGET) <= 0.02:
            break
    best = min(trials, key=lambda t: abs(t["k_ml"] - B_TARGET))
    p, c = best["param"], best["coefficient"]
    corrections = []
    for corr in range(3):   # the final cell, then at most two corrections if it falls outside 0.24 to 0.30
        label = f"r14_b1final{'' if corr == 0 else '-c%d' % corr}_{world}"
        st = r6.match(label, r13.make_for(world, pfmt(p)), c, seeds(77001), 4, TARGET, r13.job_for(world), pilot=4)
        dirs = sorted(x.parent for x in (RESULTS / st["prefix"]).glob("rep*/trace.tsv"))
        m = measure(dirs)
        corrections.append({"label": label, "param": float(pfmt(p)), "coefficient": st["k"], "k_ml": m["k_ml"], "day28": st["day28"],
                            "matched": st["matched"], "early_R": m["R"]})
        print(f"R14 B1 final {world} {label}: param={p:.4g} coeff={st['k']:.5g} day28={st['day28']:.0f} k_ml={m['k_ml']:.3f}", flush=True)
        if 0.24 <= m["k_ml"] <= 0.30:
            break
        # correct with the log-log slope from the best trial and this final cell
        slope = slope0
        if p != best["param"] and m["k_ml"] != best["k_ml"]:
            sl = (math.log(p) - math.log(best["param"])) / (math.log(m["k_ml"]) - math.log(best["k_ml"]))
            if sl * slope0 > 0 and 0.4 * abs(slope0) <= abs(sl) <= 3 * abs(slope0):
                slope = sl
        p = p * math.exp(slope * (math.log(B_TARGET) - math.log(m["k_ml"])))
        c = st["k"]
    final = corrections[-1]
    log_json(STATE / f"b1_final_{world}.json", {"world": world, "final": final, "attempts": corrections, "trials": trials})


# ---------------------------------------------------------------- B2

B2_TARGET_R = 0.88


def b2(world):
    f1 = json.loads((STATE / f"b1_final_{world}.json").read_text())["final"]
    p, slope0 = f1["param"], B1_START[world][2]
    floor = 0.03 * f1["coefficient"]
    c = f1["coefficient"] * (0.5 if world == "w3b" else 0.65)
    log_path = STATE / f"b2_trials_{world}.json"
    trials = json.loads(log_path.read_text()) if log_path.exists() else []
    for it in range(5):
        if len(trials) > it:
            continue
        if it >= 1:
            last = trials[-1]
            beta = 0.9
            if len(trials) >= 2 and trials[-2]["coefficient"] != last["coefficient"] and trials[-2]["early_R"] > 0:
                b = math.log(last["early_R"] / trials[-2]["early_R"]) / math.log(last["coefficient"] / trials[-2]["coefficient"])
                if 0.3 <= b <= 2.0:
                    beta = b
            c = max(floor, last["coefficient"] * (B2_TARGET_R / last["early_R"]) ** (1.0 / beta))
            p, _ = next_param(trials, slope0)
        dirs = run_cell(f"b2trial-i{it + 1}_{world}", world, c, p, CAL_SEEDS)
        m = measure(dirs)
        trials.append({"iteration": it + 1, "param": float(pfmt(p)), "coefficient": c, "day28": m["day28"], "k_ml": m["k_ml"],
                       "k_mom": m["k_mom"], "early_R": m["R"], "index_cases": m["index_cases"], "replicates": m["replicates"]})
        log_json(log_path, trials)
        print(f"R14 B2 {world} trial {it + 1}: param={p:.4g} coeff={c:.5g} R={m['R']:.3f} k_ml={m['k_ml']:.3f} day28={m['day28']:.0f}", flush=True)
        if abs(m["R"] / B2_TARGET_R - 1) <= 0.02 and abs(m["k_ml"] - B_TARGET) <= 0.02:
            break
        if c <= floor * 1.0001 and m["R"] > B2_TARGET_R * 1.03 and it >= 2:
            print(f"R14 B2 {world}: coefficient at its floor, mean offspring cannot be lowered further by the coefficient", flush=True)
            break

    def distance(t):
        return max(abs(t["early_R"] / B2_TARGET_R - 1) / 0.03, abs(t["k_ml"] - B_TARGET) / 0.03)
    best = min(trials, key=distance)
    p, c = best["param"], best["coefficient"]
    attempts = []
    for corr in range(3):
        label = f"b2final{'' if corr == 0 else '-c%d' % corr}_{world}"
        dirs = run_cell(label, world, c, p, seeds(77001))
        m = measure(dirs)
        attempts.append({"label": label, "param": float(pfmt(p)), "coefficient": c, "early_R": m["R"], "k_ml": m["k_ml"], "k_mom": m["k_mom"],
                         "day28": m["day28"], "index_cases": m["index_cases"], "replicates": m["replicates"]})
        print(f"R14 B2 final {world} {label}: param={p:.4g} coeff={c:.5g} R={m['R']:.3f} k_ml={m['k_ml']:.3f} index={m['index_cases']}", flush=True)
        ok = abs(m["R"] / B2_TARGET_R - 1) <= 0.03 and 0.24 <= m["k_ml"] <= 0.30
        if ok or corr == 2 or (c <= floor * 1.0001 and m["R"] > B2_TARGET_R):
            break
        beta = 0.9
        c = max(floor, c * (B2_TARGET_R / m["R"]) ** (1.0 / beta))
        sl = slope0
        p = p * math.exp(sl * (math.log(B_TARGET) - math.log(m["k_ml"])))
    final = attempts[-1]
    # at least 8,000 index cases: add 12 replicates (seeds 77013 to 77024) to the same cell
    extended = False
    if final["index_cases"] < 8000:
        label = final["label"]
        make = r13.make_for(world, pfmt(final["param"]))
        batch = []
        for i, sd in enumerate(seeds(77013), start=13):
            name = f"{label}/rep{i:02d}"
            batch.append((name, make(final["coefficient"], sd, 4, RESULTS / name)))
        r6.run_many(batch, r13.job_for(world))
        dirs = sorted(x.parent for x in (RESULTS / label).glob("rep*/trace.tsv"))
        m = measure(dirs)
        final = {**final, "early_R": m["R"], "k_ml": m["k_ml"], "k_mom": m["k_mom"], "day28": m["day28"], "index_cases": m["index_cases"], "replicates": m["replicates"]}
        extended = True
        print(f"R14 B2 {world}: extended to 24 replicates, index cases {m['index_cases']}", flush=True)
    log_json(STATE / f"b2_final_{world}.json", {"world": world, "final": final, "attempts": attempts, "trials": trials,
                                                  "extended_to_24_replicates": extended, "prefix": final["label"]})


TASKS = {"runA": lambda: run_a(sys.argv[2], sys.argv[3]), "b1": lambda: b1(sys.argv[2]), "b2": lambda: b2(sys.argv[2])}

if __name__ == "__main__":
    TASKS[sys.argv[1]]()
