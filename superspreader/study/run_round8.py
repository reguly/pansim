#!/usr/bin/env python3
"""Note 49 round 8: high-L venues, tilted class, exclusive scene, isolation breaking. Uses the build_r8 binary (PANSIM_BIN).

  PANSIM_BIN=build_r8/panSim python3 superspreader/study/run_round8.py mob8 ...
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_round6 as r6  # noqa: E402
import run_x21  # noqa: E402

RESULTS = HERE / "results" / "round8"
STATE = RESULTS / "state"
R7_STATE = HERE / "results" / "round7" / "state"
run_x21.RESULTS = RESULTS
r6.RESULTS = RESULTS
r6.STATE = STATE
fmt = r6.fmt
ELIGIBLE_TYPES = (4, 5, 6, 7, 8)
CAL_SEED = 73001
TARGET = 6211.25
K0 = 0.00041
SEED_BASE = 77000          # one seed set for every S8 arm
HIGH_TYPES = (5, 6, 9, 10)
LAMBDAS = (3, 10, 30)
INPUTS = HERE / "inputs"


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, indent=1) + "\n")


def seeds8(n=12):
    return list(range(SEED_BASE + 1, SEED_BASE + n + 1))


def s2_scale_flags():
    """Per-type scales of the round-7 S2 cell f = 5%, F = 3 (hours of class and others preserved there)."""
    stored = json.loads((R7_STATE / "scale_s2_f0.05_F3.json").read_text())
    def string(d):
        return ",".join(f"{t}:{d[str(t)]:.5f}" for t in ELIGIBLE_TYPES)
    return ["--hviScaleByType", string(stored["scale"]["wd"]), "--hviScaleByTypeWeekend", string(stored["scale"]["we"])]


def class_flags(f, F):
    return ["--hviMode", "class", "--hviClassFraction", f"{f:g}", "--hviClassFactor", f"{F:g}"]


def locs_for(lam):
    return r6.LOCS1 if lam == 1 else INPUTS / f"r8_locs_L{lam}.json"


# arm registry: label -> dict(flags, lam)
ARMS = {}
for lam in LAMBDAS:
    ARMS[f"s8_1_L{lam}"] = {"flags": [], "lam": lam}
for tau in (0.5, 1.0):
    for lam in LAMBDAS:
        ARMS[f"s8_2_t{tau:g}_L{lam}"] = {"flags": class_flags(0.05, 3) + s2_scale_flags() + ["--hviTilt", f"{tau:g}"], "lam": lam}
for lam in LAMBDAS:
    ARMS[f"s8_3_L{lam}"] = {"flags": class_flags(0.05, 3) + s2_scale_flags() + ["--hviTilt", "1", "--hviOthersHighScale", "0.2"], "lam": lam}
for f in (0.05, 0.20):
    for lam in (1, 10):
        ARMS[f"s8_4_f{int(round(f * 100))}_L{lam}"] = {"flags": class_flags(f, 1) + ["--hviIsolationBreak", "1"], "lam": lam}

# movement-only variants used for R8-0 (tables and predictions); name -> flags
MOVEMENT = {
    "base": [],
    "f3_t0": class_flags(0.05, 3) + s2_scale_flags(),
    "f3_t0.5": class_flags(0.05, 3) + s2_scale_flags() + ["--hviTilt", "0.5"],
    "f3_t1": class_flags(0.05, 3) + s2_scale_flags() + ["--hviTilt", "1"],
    "f3_t1_o0.2": class_flags(0.05, 3) + s2_scale_flags() + ["--hviTilt", "1", "--hviOthersHighScale", "0.2"],
    "c5_F1": class_flags(0.05, 1),
    "c20_F1": class_flags(0.20, 1),
}


def mob_run8(name, flags, seed=CAL_SEED, weeks=2):
    log = RESULTS / "mob8" / name / "mobility.csv"
    dump = RESULTS / "mob8" / name / "hvi.csv"
    args = r6.base_args(0.0, seed, weeks, list(flags) + ["--mobilityLog", str(log), "--hviDump", str(dump)])
    code = run_x21.run_job(f"mob8/{name}", args, agents=r6.AGENTS2, locations=r6.LOCS1)
    if code:
        raise SystemExit(code)
    return log


def mob8():
    for name, flags in MOVEMENT.items():
        if (RESULTS / "mob8" / name / "mobility.csv").exists() and (RESULTS / "mob8" / name / "hvi.csv").exists():
            continue
        mob_run8(name, flags)


def k0_of(label):
    path = STATE / "k0.json"
    if path.exists():
        table = json.loads(path.read_text())
        if label in table:
            return table[label]
    return K0


def epidemic_make(label):
    flags = ARMS[label]["flags"]

    def make(k, seed, weeks, run_dir):
        return r6.base_args(k, seed, weeks, flags + ["--hviDump", str(Path(run_dir) / "hvi.csv")])
    return make


def job_of(label):
    return {"agents": r6.AGENTS2, "locations": locs_for(ARMS[label]["lam"])}


def run_arm8(label, reps=12, pilot=4):
    seeds = seeds8(reps)
    return r6.match(f"r8_{label}", epidemic_make(label), k0_of(label), seeds, 4, TARGET, job_of(label), pilot=pilot)


def run_arms(labels):
    for label in labels:
        stored = run_arm8(label)
        print(f"S8 {label} k={stored['k']:.6g} day28={stored['day28']:.1f} matched={stored['matched']}", flush=True)


def gate():
    """Order of note 49: S8-1 and S8-2 at lambda 10 only."""
    run_arms(["s8_1_L10", "s8_2_t1_L10"])


def gate2():
    run_arms(["s8_2_t0.5_L10"])


def s83():
    run_arms([f"s8_3_L{lam}" for lam in (10,)])


def s84():
    run_arms([k for k in ARMS if k.startswith("s8_4_")])


def s81():
    run_arms([f"s8_1_L{lam}" for lam in (3, 30)])


def s82():
    run_arms([f"s8_2_t{t:g}_L{lam}" for t in (1.0, 0.5) for lam in (3, 30)])


def s83all():
    run_arms([f"s8_3_L{lam}" for lam in (3, 30)])


# ---------------------------------------------------------------- S8-5, policy contrast on one cell

def write_close(types, path):
    rule = {"name": "r8_close", "conditionType": "afterDays", "threshold": 21, "threshold2": 21, "openAfter": 400, "closeAfter": -1,
            "parameter": "0", "locationTypesToClose": list(types)}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"rules": [rule]}, indent=2) + "\n")


def hours_of(log):
    """Total role-discretionary hours and total hours at the high-L types (all roles) over all agents of a mobility log."""
    disc = high = 0.0
    with open(log) as handle:
        for r in csv.DictReader(handle):
            disc += float(r["h_wd_role_disc"]) + float(r["h_we_role_disc"])
            high += sum(float(r[f"hpt_{t}"]) for t in HIGH_TYPES)
    return disc, high


def ctrl_run8(name, flags, weeks=5, closures=None):
    log = RESULTS / name / "mobility.csv"
    args = r6.base_args(0.0, CAL_SEED, weeks, list(flags) + ["--mobilityLog", str(log)])
    if closures is not None:
        args[args.index("--closures") + 1] = str(closures)
    code = run_x21.run_job(name, args, agents=r6.AGENTS2, locations=r6.LOCS1)
    if code:
        raise SystemExit(code)
    return hours_of(log)


def s85_prep(base):
    path = STATE / f"s85_prep_{base}.json"
    if path.exists():
        return json.loads(path.read_text())
    flags = ARMS[base]["flags"]
    tag = f"mob8/s85/{base}"
    h3 = ctrl_run8(f"{tag}_h3", flags, 3)
    h5 = ctrl_run8(f"{tag}_h5", flags, 5)
    post = (h5[0] - h3[0], h5[1] - h3[1])
    hc = ctrl_run8(f"{tag}_cap", flags + ["--hviControlDay", "21", "--hviControlMode", "capTop", "--hviControlParam", "0.05"], 5)
    cap = ((h5[0] - hc[0]) / post[0], (h5[1] - hc[1]) / post[1])
    print(f"S8-5 {base}: capTop removes {cap[0]:.3%} of discretionary and {cap[1]:.3%} of high-L hours", flush=True)
    trials = []
    s_val = 1.0 - cap[0]
    for it in range(6):
        hs = ctrl_run8(f"{tag}_scale{it}", flags + ["--hviControlDay", "21", "--hviControlMode", "scaleAll", "--hviControlParam", f"{s_val:.4f}"], 5)
        rho = ((h5[0] - hs[0]) / post[0], (h5[1] - hs[1]) / post[1])
        trials.append((s_val, rho[0], rho[1]))
        print(f"S8-5 {base}: scaleAll {s_val:.4f} removes {rho[0]:.3%} of discretionary and {rho[1]:.3%} of high-L hours", flush=True)
        if abs(rho[0] - cap[0]) < 0.03 * cap[0]:
            break
        if len(trials) >= 2 and trials[-1][1] != trials[-2][1]:
            (s1, r1, _), (s2, r2, _) = trials[-2], trials[-1]
            s_val = s2 + (cap[0] - r2) * (s2 - s1) / (r2 - r1)
        else:
            s_val = s_val * (1 - cap[0]) / (1 - rho[0]) if rho[0] < 1 else s_val
        s_val = min(max(s_val, 0.0), 1.0)
    cf = RESULTS / "inputs" / f"close_{base}.json"
    write_close(HIGH_TYPES, cf)
    hcl = ctrl_run8(f"{tag}_close", flags, 5, closures=cf)
    close = ((h5[0] - hcl[0]) / post[0], (h5[1] - hcl[1]) / post[1])
    print(f"S8-5 {base}: closing {HIGH_TYPES} removes {close[0]:.3%} of discretionary and {close[1]:.3%} of high-L hours", flush=True)
    payload = {"base": base, "post_hours_disc": post[0], "post_hours_high": post[1], "cap": cap, "scale_param": trials[-1][0], "scale": trials[-1][1:],
               "scale_trials": trials, "close": close, "close_file": str(cf)}
    save_json(path, payload)
    return payload


def s85(base=None):
    base = base or sys.argv[-1]
    prep = s85_prep(base)
    k = json.loads((STATE / f"r8_{base}.json").read_text())["k"]
    seeds = seeds8(12)
    flags0 = ARMS[base]["flags"]
    job = job_of(base)
    for mode in ("none", "capTop", "scaleAll", "close"):
        label = f"s85_{base}_{mode}"
        extra, closures = [], None
        if mode == "capTop":
            extra = ["--hviControlDay", "21", "--hviControlMode", "capTop", "--hviControlParam", "0.05"]
        elif mode == "scaleAll":
            extra = ["--hviControlDay", "21", "--hviControlMode", "scaleAll", "--hviControlParam", f"{prep['scale_param']:.4f}"]
        elif mode == "close":
            closures = Path(prep["close_file"])
        batch = []
        for rep, seed in enumerate(seeds, start=1):
            nm = f"r8/{label}/rep{rep:02d}"
            args = r6.base_args(k, seed, 12, flags0 + extra + ["--hviDump", str(RESULTS / nm / "hvi.csv")])
            if closures is not None:
                args[args.index("--closures") + 1] = str(closures)
            batch.append((nm, args))
        r6.run_many(batch, job)
        print(f"S8-5 {label} done", flush=True)


def grid():
    """After the gate (note 49 stop rule: S8-2 gave k below 2): S8-3, S8-4, then the lambda and tau grids, 12 replicates everywhere."""
    run_arms(["s8_3_L10"])
    run_arms([k for k in ARMS if k.startswith("s8_4_")])
    run_arms([f"s8_2_t{t:g}_L{lam}" for t in (1.0, 0.5) for lam in (3, 30)])
    run_arms([f"s8_3_L{lam}" for lam in (3, 30)])
    run_arms([f"s8_1_L{lam}" for lam in (3, 30)])


TASKS = {k: v for k, v in globals().items() if k in ("mob8", "gate", "gate2", "s83", "s84", "s81", "s82", "s83all", "grid", "s85")}

if __name__ == "__main__":
    for name in sys.argv[1:]:
        TASKS[name]()
