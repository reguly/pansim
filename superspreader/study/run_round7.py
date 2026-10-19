#!/usr/bin/env python3
"""Note 46 round 7: high-velocity individuals. Uses the build_r7 binary (PANSIM_BIN).

  PANSIM_BIN=build_r7/panSim python3 superspreader/study/run_round7.py cal_s1 ...
"""
import csv
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_round6 as r6  # noqa: E402
import run_x21  # noqa: E402

RESULTS = HERE / "results" / "round7"
STATE = RESULTS / "state"
run_x21.RESULTS = RESULTS
r6.RESULTS = RESULTS
r6.STATE = STATE
fmt = r6.fmt
JOB_A = r6.JOB_A
ELIGIBLE_TYPES = (4, 5, 6, 7, 8)
CAL_SEED = 73001
CAL_WEEKS = 2

# arm registry: label -> HVI flags (without the per-type scale)
ARMS = {}
for a in ("3", "1", "0.5", "0.3", "0.15"):
    ARMS[f"s1_a{a}"] = ["--hviMode", "gamma", "--hviShape", a]
for f in (0.01, 0.05, 0.10, 0.20):
    for F in (2, 3, 4.5):
        ARMS[f"s2_f{f:g}_F{F:g}"] = ["--hviMode", "class", "--hviClassFraction", f"{f:g}", "--hviClassFactor", f"{F:g}"]
ARMS["s2_rotate1"] = ["--hviRotateFraction", "0.01"]

SCALE_FROM = {}        # label -> label whose per-type scale it reuses
JOB_FILES = {}         # label -> (agents, locations) override
FIXED_HVI_SEED = 424242
S2_CELL = "s2_f0.05_F3"
# S3 repertoire (fixed HVI assignment so that one agents file serves every replicate), S4 visits, S5 uncoupled, S6 control
for rep in (1, 3, 10):
    lab = f"s3_rep{rep}"
    ARMS[lab] = ARMS[S2_CELL] + ["--hviSeed", str(FIXED_HVI_SEED)]
    SCALE_FROM[lab] = S2_CELL
    if rep > 1:
        JOB_FILES[lab] = (HERE / "inputs" / f"r7_agents_rep{rep}.json", r6.LOCS1)
for v in (1, 2, 4):
    lab = f"s4_v{v}"
    ARMS[lab] = ARMS[S2_CELL] + ["--hviVisitsFactor", str(v)]
    SCALE_FROM[lab] = S2_CELL
for a in ("0.5", "0.3"):
    lab = f"s5_unc_a{a}"
    ARMS[lab] = ARMS[f"s1_a{a}"] + ["--hviWhen", "infectious"]
    SCALE_FROM[lab] = f"s1_a{a}"
for base in (S2_CELL, "s1_a0.3"):
    tag = base.split("_")[0] + ("c" if base == S2_CELL else "s")
    for mode, param in (("capTop", "0.05"), ("scaleAll", "SCALE")):
        lab = f"s6_{tag}_{mode}"
        ARMS[lab] = ARMS[base] + ["--hviControlDay", "21", "--hviControlMode", mode, "--hviControlParam", param]
        SCALE_FROM[lab] = base
    lab = f"s6_{tag}_none"
    ARMS[lab] = list(ARMS[base])
    SCALE_FROM[lab] = base
    lab = f"s6_{tag}_close"
    ARMS[lab] = list(ARMS[base])
    SCALE_FROM[lab] = base


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, indent=1) + "\n")


def mob_args(flags, seed, weeks, log):
    return r6.base_args(0.0, seed, weeks, list(flags) + ["--mobilityLog", str(log)])


def mob_run(name, flags, seed=CAL_SEED, weeks=CAL_WEEKS, job=None):
    log = RESULTS / name / "mobility.csv"
    code = run_x21.run_job(name, mob_args(flags, seed, weeks, log), **(job or JOB_A))
    if code:
        raise SystemExit(code)
    return log


def disc_means(log):
    """Mean discretionary role hours per day among eligible agents, by agent type, weekday and weekend."""
    acc = {t: [0, 0.0, 0.0, 0.0, 0.0] for t in ELIGIBLE_TYPES}
    with open(log) as handle:
        for r in csv.DictReader(handle):
            t = int(r["type"])
            if t not in acc or int(r["age"]) < 15:
                continue
            dwd, dwe = float(r["days_weekday"]), float(r["days_weekend"])
            a = acc[t]
            a[0] += 1
            a[1] += float(r["h_wd_role_disc"]) / dwd
            a[2] += float(r["h_we_role_disc"]) / dwe
            a[3] += float(r["visits_wd"]) / dwd
            a[4] += float(r["visits_we"]) / dwe
    return {t: {"n": a[0], "wd": a[1] / a[0], "we": a[2] / a[0], "visits_wd": a[3] / a[0], "visits_we": a[4] / a[0]} for t, a in acc.items()}


def baseline_means():
    path = STATE / "baseline_means.json"
    if path.exists():
        return {int(k): v for k, v in json.loads(path.read_text()).items()}
    log = mob_run("mob/baseline", [])
    means = disc_means(log)
    save_json(path, means)
    return means


def scale_string(scale):
    return ",".join(f"{t}:{scale[t]:.5f}" for t in ELIGIBLE_TYPES)


def scale_flags(scales):
    return ["--hviScaleByType", scale_string(scales["wd"]), "--hviScaleByTypeWeekend", scale_string(scales["we"])]


def calibrate_scale(label, flags, tol=0.02, max_iter=8, slope=0.6):
    """Per-agent-type scales on the multiplier, separately for weekdays and weekends, so that mean discretionary
    hours return to baseline within tol for every eligible agent type and day type."""
    if label in SCALE_FROM:
        return calibrate_scale(SCALE_FROM[label], ARMS[SCALE_FROM[label]], tol, max_iter, slope)
    state_path = STATE / f"scale_{label}.json"
    if state_path.exists():
        stored = json.loads(state_path.read_text())
        if stored.get("done"):
            return {d: {int(k): v for k, v in stored["scale"][d].items()} for d in ("wd", "we")}, stored
    base = baseline_means()
    scales = {"wd": {t: 1.0 for t in ELIGIBLE_TYPES}, "we": {t: 1.0 for t in ELIGIBLE_TYPES}}
    history = []
    for it in range(max_iter):
        name = f"mob/{label}/it{it}"
        log = mob_run(name, flags + scale_flags(scales))
        got = disc_means(log)
        dev = {t: {"wd": got[t]["wd"] / base[t]["wd"] - 1, "we": got[t]["we"] / base[t]["we"] - 1} for t in ELIGIBLE_TYPES}
        history.append({"iteration": it, "scale": {d: dict(scales[d]) for d in scales}, "deviation": dev})
        worst = max(abs(dev[t][d]) for t in ELIGIBLE_TYPES for d in ("wd", "we"))
        print(f"scale {label} it{it} worst deviation {worst:+.3%} " + " ".join(f"{t}:{dev[t]['wd']:+.3f}/{dev[t]['we']:+.3f}" for t in ELIGIBLE_TYPES), flush=True)
        if worst <= tol:
            stored = {"done": True, "scale": scales, "history": history, "deviation": dev, "accepted_iteration": it}
            save_json(state_path, stored)
            return scales, stored
        for t in ELIGIBLE_TYPES:
            for d in ("wd", "we"):
                scales[d][t] = scales[d][t] * (1.0 / (1.0 + dev[t][d])) ** (1.0 / slope)
    stored = {"done": True, "scale": scales, "history": history, "deviation": dev, "accepted_iteration": None}
    save_json(state_path, stored)
    return scales, stored


def cal_s1():
    for label in [k for k in ARMS if k.startswith("s1_")]:
        calibrate_scale(label, ARMS[label])


def cal_s2():
    for label in [k for k in ARMS if k.startswith("s2_")]:
        calibrate_scale(label, ARMS[label])


# ---------------------------------------------------------------- epidemic arms

TARGET = 6211.25
K0 = 0.00041


def arm_flags(label):
    scale, _ = calibrate_scale(label, ARMS[label])
    return ARMS[label] + scale_flags(scale)


def epidemic_make(label, extra=()):
    flags = arm_flags(label) + list(extra)

    def make(k, seed, weeks, run_dir):
        return r6.base_args(k, seed, weeks, flags + ["--hviDump", str(Path(run_dir) / "hvi.csv")])
    return make


def run_arm(label, index, extra=(), weeks=4, name=None, target=TARGET, k0=K0):
    """Match the infection coefficient to day 28 on 12 seeds; the matched round is the replicate set."""
    seeds = list(range(74000 + 100 * (index + 1) + 1, 74000 + 100 * (index + 1) + 13))
    return r6.match(f"r7_{name or label}", epidemic_make(label, extra), k0, seeds, weeks, target, JOB_A)


def s1():
    for index, label in enumerate([k for k in ARMS if k.startswith("s1_")]):
        stored = run_arm(label, index)
        print(f"S1 {label} k={stored['k']:.6g} day28={stored['day28']:.1f} matched={stored['matched']}", flush=True)


def wk1_runs(prefix):
    """1-week movement-only runs at the accepted scale, for the weekly persistence test (T3)."""
    for label in [k for k in ARMS if k.startswith(prefix)]:
        scale, _ = calibrate_scale(label, ARMS[label])
        mob_run(f"mob/{label}/wk1", ARMS[label] + scale_flags(scale), weeks=1)


def wk1_s1():
    wk1_runs("s1_")


def wk1_s2():
    wk1_runs("s2_")


def job_of(label):
    agents, locations = JOB_FILES.get(label, (r6.AGENTS2, r6.LOCS1))
    return {"agents": agents, "locations": locations}


def matched_k(label):
    return json.loads((STATE / f"r7_{label}.json").read_text())["k"]


def fixed_k_runs(label, k, seeds, weeks=4, extra=(), job=None, name=None, closures=None):
    """12 runs at a given coefficient (no calibration), results in r7/<name or label>/repNN with the HVI dump."""
    flags = arm_flags(label) + list(extra)
    batch = []
    for rep, seed in enumerate(seeds, start=1):
        nm = f"r7/{name or label}/rep{rep:02d}"
        args = r6.base_args(k, seed, weeks, flags + ["--hviDump", str(RESULTS / nm / "hvi.csv")])
        if closures is not None:
            args[args.index("--closures") + 1] = str(closures)
        batch.append((nm, args))
    r6.run_many(batch, job or job_of(label))


def seeds_for(tag, n=12):
    base = {"s2cell": 74900, "s3": 76100, "s4": 76200, "s6": 76300, "s5pairs": 76400}[tag]
    return list(range(base + 1, base + n + 1))


def s2():
    for index, label in enumerate([k for k in ARMS if k.startswith("s2_")]):
        stored = run_arm(label, 20 + index)
        print(f"S2 {label} k={stored['k']:.6g} day28={stored['day28']:.1f} matched={stored['matched']}", flush=True)


def s3():
    k = matched_k(S2_CELL)
    for rep in (1, 3, 10):
        fixed_k_runs(f"s3_rep{rep}", k, seeds_for("s3"))
        print(f"S3 rep {rep} done at k={k:.6g}", flush=True)


def s4():
    use_v2_binary()
    k = matched_k(S2_CELL)
    state = json.loads((STATE / f"r7_{S2_CELL}.json").read_text())
    seeds = [74000 + 100 * (20 + [x for x in ARMS if x.startswith("s2_")].index(S2_CELL) + 1) + i for i in range(1, 13)]
    for v in (2, 4):
        fixed_k_runs(f"s4_v{v}", k, seeds)
        print(f"S4 V {v} done at k={k:.6g}", flush=True)


def s5():
    for index, a in enumerate(("0.5", "0.3")):
        label = f"s5_unc_a{a}"
        stored = run_arm(label, 60 + index)
        print(f"S5 {label} k={stored['k']:.6g} day28={stored['day28']:.1f} matched={stored['matched']}", flush=True)


def s5_pairs():
    """Persistent main arm, shape 0.3, 16 weeks, 8 replicates, every infection episode logged, vaccination off."""
    label = "s1_a0.3"
    k = matched_k(label)
    flags = arm_flags(label) + ["--immunizationStart", "100000"]
    batch = []
    for rep, seed in enumerate(seeds_for("s5pairs", 8), start=1):
        nm = f"r7/s5_pairs/rep{rep:02d}"
        args = r6.base_args(k, seed, 16, flags + ["--episodeTrace", str(RESULTS / nm / "episodes.tsv"), "--hviDump", str(RESULTS / nm / "hvi.csv")])
        batch.append((nm, args))
    r6.run_many(batch, JOB_A)


def use_v2_binary():
    run_x21.BINARY = r6.ROOT / "build_r7b" / "panSim"


def t6():
    """T6: visits and repertoire levers on the S2 cell (f = 5%, F = 3), movement only, 2 weeks, one seed."""
    use_v2_binary()
    scale, _ = calibrate_scale(S2_CELL, ARMS[S2_CELL])
    base = ARMS[S2_CELL] + scale_flags(scale)
    for v in (2, 4):
        mob_run(f"mob/t6b/v{v}", base + ["--hviVisitsFactor", str(v)])


# ---------------------------------------------------------------- S6 control

S6_BASES = {"cell": S2_CELL, "shape": "s1_a0.3"}


ELIGIBLE = (4, 5, 6, 7, 8)


def total_disc_hours(log):
    total = 0.0
    with open(log) as handle:
        for r in csv.DictReader(handle):
            total += float(r["h_wd_role_disc"]) + float(r["h_we_role_disc"])
    return total


def class_hours_by_type(log, top_fraction=0.05):
    """Discretionary hours by physical venue type among the most active agents (the class, or the top fraction by m)."""
    rows = list(csv.DictReader(open(log)))
    elig = [r for r in rows if int(r["type"]) in ELIGIBLE and int(r["age"]) >= 15]
    ms = sorted(float(r["m"]) for r in elig)
    thr = ms[int((1 - top_fraction) * len(ms))]
    sums = {t: 0.0 for t in (1, 5, 6, 7, 8, 9, 10)}
    for r in elig:
        if float(r["m"]) >= thr:
            for t in sums:
                sums[t] += float(r[f"hdt_{t}"])
    return sums


def write_close(types, path):
    rule = {"name": "r7_close", "conditionType": "afterDays", "threshold": 21, "threshold2": 21, "openAfter": 400, "closeAfter": -1,
            "parameter": "0", "locationTypesToClose": list(types)}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"rules": [rule]}, indent=2) + "\n")


def ctrl_run(name, flags, weeks=5, closures=None):
    log = RESULTS / name / "mobility.csv"
    args = mob_args(flags, CAL_SEED, weeks, log)
    if closures is not None:
        args[args.index("--closures") + 1] = str(closures)
    code = run_x21.run_job(name, args, **JOB_A)
    if code:
        raise SystemExit(code)
    return total_disc_hours(log)


def s6_prep():
    out = {}
    for tag, base in S6_BASES.items():
        path = STATE / f"s6_prep_{tag}.json"
        if path.exists():
            continue
        scale, _ = calibrate_scale(base, ARMS[base])
        flags = ARMS[base] + scale_flags(scale)
        h3 = ctrl_run(f"mob/s6/{tag}_h3", flags, 3)
        h5 = ctrl_run(f"mob/s6/{tag}_h5", flags, 5)
        post = h5 - h3
        hc = ctrl_run(f"mob/s6/{tag}_cap", flags + ["--hviControlDay", "21", "--hviControlMode", "capTop", "--hviControlParam", "0.05"], 5)
        rho = (h5 - hc) / post
        print(f"S6 {tag}: baseline post-day-21 hours {post:.0f}, capTop removes {rho:.3%}", flush=True)
        # scaleAll: secant on the scale to remove the same fraction
        lo, hi = 0.0, 1.0
        s_val, rho_s = 1.0 - rho, None
        trials = []
        for it in range(5):
            hs = ctrl_run(f"mob/s6/{tag}_scale{it}", flags + ["--hviControlDay", "21", "--hviControlMode", "scaleAll", "--hviControlParam", f"{s_val:.4f}"], 5)
            rho_s = (h5 - hs) / post
            trials.append((s_val, rho_s))
            print(f"S6 {tag}: scaleAll {s_val:.4f} removes {rho_s:.3%}", flush=True)
            if abs(rho_s - rho) < 0.03 * rho:
                break
            if len(trials) >= 2 and trials[-1][1] != trials[-2][1]:
                (s1, r1), (s2, r2) = trials[-2], trials[-1]
                s_val = s2 + (rho - r2) * (s2 - s1) / (r2 - r1)
            else:
                s_val = s_val * (1 - rho) / (1 - rho_s) if rho_s < 1 else s_val
            s_val = min(max(s_val, 0.0), 1.0)
        # closure of the venue types that hold most of the most active agents' hours
        ref_log = RESULTS / "mob" / ("t6/v1" if tag == "cell" else f"{base}/it{json.loads((STATE / f'scale_{base}.json').read_text())['accepted_iteration']}") / "mobility.csv"
        by_type = class_hours_by_type(ref_log)
        order = [t for t, _ in sorted(by_type.items(), key=lambda kv: -kv[1]) if t != 1]
        close = []
        for k in (1, 2, 3):
            types = order[:k]
            cf = RESULTS / "inputs" / f"close_{tag}_{k}.json"
            write_close(types, cf)
            hcl = ctrl_run(f"mob/s6/{tag}_close{k}", flags, 5, closures=cf)
            close.append({"types": types, "removes": (h5 - hcl) / post})
            print(f"S6 {tag}: close {types} removes {(h5 - hcl) / post:.3%}", flush=True)
        best = min(range(3), key=lambda i: abs(close[i]["removes"] - rho))
        save_json(path, {"base": base, "baseline_post_hours": post, "cap_removes": rho, "scale_param": trials[-1][0], "scale_removes": trials[-1][1],
                         "scale_trials": trials, "hours_by_type_top_agents": by_type, "close_options": close, "close_choice": best + 1,
                         "close_types": close[best]["types"], "close_file": str(RESULTS / "inputs" / f"close_{tag}_{best + 1}.json")})


def s6():
    for tag, base in S6_BASES.items():
        prep = json.loads((STATE / f"s6_prep_{tag}.json").read_text())
        k = matched_k(base)
        seeds = seeds_for("s6")
        for mode in ("none", "capTop", "scaleAll", "close"):
            label = f"s6_{'cell' if tag == 'cell' else 'shape'}_{mode}"
            if mode == "none":
                extra, closures = [], None
            elif mode == "capTop":
                extra, closures = ["--hviControlDay", "21", "--hviControlMode", "capTop", "--hviControlParam", "0.05"], None
            elif mode == "scaleAll":
                extra, closures = ["--hviControlDay", "21", "--hviControlMode", "scaleAll", "--hviControlParam", f"{prep['scale_param']:.4f}"], None
            else:
                extra, closures = [], Path(prep["close_file"])
            # the arm's own flags without the placeholder control flags, scale taken from the base arm
            scale, _ = calibrate_scale(base, ARMS[base])
            flags = ARMS[base] + scale_flags(scale) + extra
            batch = []
            for rep, seed in enumerate(seeds, start=1):
                nm = f"r7/{label}/rep{rep:02d}"
                args = r6.base_args(k, seed, 12, flags + ["--hviDump", str(RESULTS / nm / "hvi.csv")])
                if closures is not None:
                    args[args.index("--closures") + 1] = str(closures)
                batch.append((nm, args))
            r6.run_many(batch, JOB_A)
            print(f"S6 {label} done", flush=True)


TASKS = {"s6_prep": s6_prep, "s6": s6, "t6": t6, "s2": s2, "s3": s3, "s4": s4, "s5": s5, "s5_pairs": s5_pairs, "wk1_s1": wk1_s1, "wk1_s2": wk1_s2, "cal_s1": cal_s1, "cal_s2": cal_s2, "s1": s1}

if __name__ == "__main__":
    for name in sys.argv[1:]:
        TASKS[name]()
