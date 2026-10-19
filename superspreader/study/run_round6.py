#!/usr/bin/env python3
"""Note 42 round 6. Resumes finished jobs.

  python3 superspreader/study/run_round6.py r61 r64 r65 r66
  PANSIM_JOBS=3 sets the number of concurrent simulator processes (default 1).

Every run goes to results/round6/<name>. Calibration state is kept in results/round6/state.
"""

import json
import math
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_x21  # noqa: E402
from analyze import load_daily  # noqa: E402
from run_phase2 import fmt  # noqa: E402
from run_study import CLOSURE_NONE, ROOT  # noqa: E402

RESULTS = HERE / "results" / "round6"
run_x21.RESULTS = RESULTS
STATE = RESULTS / "state"
AGENTS2 = ROOT / "inputRealExample" / "agents2.json"
LOCS1 = ROOT / "inputRealExample" / "locations1.json"
JOB_A = {"agents": AGENTS2, "locations": LOCS1}
JOBS = int(os.environ.get("PANSIM_JOBS", "1"))
TARGET_61 = 6211.25
TARGET_64 = 6000.0
TOL = 0.03
EVENT_TYPES = "5,8"
EVENT_RATE = 0.003
EVENT_CAP = 100


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(payload, indent=1) + "\n")


def day28(run_dir):
    rows = load_daily(Path(run_dir) / "stdout.txt")
    if len(rows) < 28:
        raise RuntimeError(f"{run_dir} has {len(rows)} days")
    return int(rows[27]["INF"])


def base_args(k, seed, weeks, extra=(), alpha=1):
    return [
        "-r", "--quarantinePolicy", "0", "--closures", str(CLOSURE_NONE),
        "-k", fmt(k), "-w", str(weeks), "--seed", str(seed),
        "--densityExponent", fmt(alpha), "--venueProfile", "off", *extra,
    ]


def run_many(names_args, job):
    """Run (name, args) pairs, JOBS at a time. Raises if any job fails."""
    def one(item):
        name, args = item
        return run_x21.run_job(name, args, **job)
    if JOBS <= 1:
        codes = [one(item) for item in names_args]
    else:
        with ThreadPoolExecutor(max_workers=JOBS) as pool:
            codes = list(pool.map(one, names_args))
    if any(codes):
        raise SystemExit(f"a job failed: {codes}")


def all_node_mean(run_dir):
    """Mean offspring of a chain run: infected agents that have an infector, over all infected agents."""
    nodes = seeds = 0
    with open(Path(run_dir) / "trace.tsv") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        col = header.index("infector")
        for line in handle:
            nodes += 1
            if int(line.split("\t", col + 1)[col]) == 4294967295:
                seeds += 1
    return (nodes - seeds) / nodes if nodes else float("nan")


def pooled_mean(prefix, reps=40):
    """Mean offspring of a set of chain runs pooled over replicates: (nodes - seeds) / nodes."""
    nodes = seeds = 0
    for rep in range(1, reps + 1):
        with open(RESULTS / f"{prefix}/rep{rep:02d}/trace.tsv") as handle:
            header = handle.readline().rstrip("\n").split("\t")
            col = header.index("infector")
            for line in handle:
                nodes += 1
                if int(line.split("\t", col + 1)[col]) == 4294967295:
                    seeds += 1
    return (nodes - seeds) / nodes


def match(label, make, k0, seeds, weeks, target, job, tol=TOL, max_rounds=9, measure=day28, pilot=0, pilot_tol=0.12):
    """Log-log secant on k until the mean of measure() is within tol of target.

    make(k, seed, weeks, run_dir) returns the argument list. Each round writes to
    cal/<label>/k<k>/repNN. The matched round is returned and its runs are kept as the replicates.
    With pilot > 0 the first rounds use only the first `pilot` seeds, until within pilot_tol, and
    the full seed list is used from then on (the pilot runs are reused at the same k).
    """
    state_path = STATE / f"{label}.json"
    points = []
    k = k0
    in_pilot = pilot > 0
    if state_path.exists():
        stored = json.loads(state_path.read_text())
        if stored.get("matched"):
            print(f"match {label} cached k={stored['k']:.6g} value={stored['day28']:.4g}", flush=True)
            return stored
        points = stored["points"]
        k = stored["next_k"]
        in_pilot = stored.get("in_pilot", in_pilot)
    for _ in range(max_rounds + (6 if pilot else 0)):
        use = seeds[:pilot] if in_pilot else seeds
        prefix = f"cal/{label}/k{k:.6g}"
        batch = []
        for index, seed in enumerate(use, start=1):
            name = f"{prefix}/rep{index:02d}"
            batch.append((name, make(k, seed, weeks, RESULTS / name)))
        run_many(batch, job)
        values = [measure(RESULTS / f"{prefix}/rep{index:02d}") for index in range(1, len(use) + 1)]
        value = sum(values) / len(values)
        points.append({"k": k, "day28": value, "values": values, "prefix": prefix, "pilot": in_pilot})
        print(f"match {label} k={k:.6g} value={value:.4g} target={target:.4g} ({value / target - 1:+.1%}){' pilot' if in_pilot else ''}", flush=True)
        if abs(value / target - 1.0) <= (pilot_tol if in_pilot else tol):
            if in_pilot:
                in_pilot = False
                points[-1]["pilot_done"] = True
                save_json(state_path, {"matched": False, "points": points, "next_k": k, "target": target, "in_pilot": False})
                continue
            stored = {"k": k, "day28": value, "matched": True, "target": target, "prefix": prefix, "points": points}
            save_json(state_path, stored)
            return stored
        usable = [p for p in points if not p.get("pilot") or in_pilot]
        low = [p for p in usable if p["day28"] < target]
        high = [p for p in usable if p["day28"] > target]
        if low and high:
            lo = max(low, key=lambda p: p["day28"])
            hi = min(high, key=lambda p: p["day28"])
            span = math.log(hi["day28"] / lo["day28"])
            frac = math.log(target / lo["day28"]) / span if span else 0.5
            k = math.exp(math.log(lo["k"]) + frac * (math.log(hi["k"]) - math.log(lo["k"])))
        else:
            slope = 1.5
            if len(usable) >= 2 and usable[-2]["k"] != usable[-1]["k"] and usable[-2]["day28"] > 0 and value > 0:
                slope = math.log(value / usable[-2]["day28"]) / math.log(usable[-1]["k"] / usable[-2]["k"])
                slope = min(8.0, max(0.3, slope))
            k = k * (target / value) ** (1.0 / slope)
        save_json(state_path, {"matched": False, "points": points, "next_k": k, "target": target, "in_pilot": in_pilot})
    full = [p for p in points if not p.get("pilot")]
    best = min(full or points, key=lambda p: abs(p["day28"] / target - 1.0))
    stored = {"k": best["k"], "day28": best["day28"], "matched": False, "target": target, "prefix": best["prefix"], "points": points}
    save_json(state_path, stored)
    print(f"match {label} NOT matched within {tol:.0%}; closest k={best['k']:.6g} value={best['day28']:.4g}", flush=True)
    return stored


# ---------------------------------------------------------------- R6-1

R61_SHAPES = ("none", "1.0", "0.5", "0.3")
R61_FACTORS = (0, 300, 600, 1091)
# Cells that exist from rounds 3 to 5 and are reused: (shape, factor) -> directory below results/round2
R61_REUSED = {
    ("none", 0): "r36/baseline",
    ("none", 600): "r42/cap100_f600",
    ("none", 1091): "r42/cap100_f1091",
    ("0.3", 0): "r3cal/r35_E/round0",
}
# Start guesses for the background coefficient.
R61_K0 = {"none": 0.00041, "1.0": 0.00044, "0.5": 0.00047, "0.3": 0.000498}
R61_EVENT_SCALE = {0: 1.0, 300: 0.95, 600: 0.89, 1091: 0.85}


def r61_args(shape, factor):
    def make(k, seed, weeks, run_dir):
        extra = []
        if shape != "none":
            extra += ["--sheddingShape", shape]
        if factor > 0:
            extra += [
                "--eventRate", fmt(EVENT_RATE), "--eventFactor", fmt(factor), "--eventTypes", EVENT_TYPES,
                "--eventMaxCapacity", str(EVENT_CAP), "--eventLog", str(Path(run_dir) / "events.tsv"),
            ]
        return base_args(k, seed, weeks, extra)
    return make


def r61():
    order = []
    for factor in R61_FACTORS:
        for shape in R61_SHAPES:
            if (shape, factor) not in R61_REUSED:
                order.append((shape, factor))
    for index, (shape, factor) in enumerate(order):
        label = f"r61_a{shape}_f{factor}"
        seeds = list(range(61000 + 100 * (index + 1) + 1, 61000 + 100 * (index + 1) + 13))
        k0 = R61_K0[shape] * R61_EVENT_SCALE[factor]
        print(f"R6-1 cell shape {shape} factor {factor} k0 {k0:.6g}", flush=True)
        match(label, r61_args(shape, factor), k0, seeds, 4, TARGET_61, JOB_A)


# ---------------------------------------------------------------- R6-4

PS1_FLAGS = {
    "E": ["--sheddingShape", "0.3"],
    "P0": ["--traitShape", "0.3", "--traitPersist", "1", "--traitSusceptibilityExp", "0"],
    "P25": ["--traitShape", "0.3", "--traitPersist", "1", "--traitSusceptibilityExp", "0.25"],
    "P50": ["--traitShape", "0.3", "--traitPersist", "1", "--traitSusceptibilityExp", "0.5"],
    "P100": ["--traitShape", "0.3", "--traitPersist", "1", "--traitSusceptibilityExp", "1"],
    "P25k": ["--traitShape", "0.08", "--traitPersist", "1", "--traitSusceptibilityExp", "0.25"],
    "P100ln": ["--traitDist", "lognormal", "--traitShape", "0.3", "--traitPersist", "1", "--traitSusceptibilityExp", "1"],
}
# PS1 coefficients (old map, early-R matched) are the start guesses.
R64_K0 = {"E": 0.000498, "P0": 0.000497, "P25": 0.000289, "P50": 0.00022, "P100": 0.00019, "P25k": 0.000159, "P100ln": 0.000184}


def r64_args(arm):
    def make(k, seed, weeks, run_dir):
        return base_args(k, seed, weeks, PS1_FLAGS[arm] + ["--traitDump", str(Path(run_dir) / "agents_trait.csv")])
    return make


def r64(arms=None):
    for index, arm in enumerate(arms or PS1_FLAGS):
        label = f"r64_{arm}"
        seeds = list(range(64000 + 100 * (index + 1) + 1, 64000 + 100 * (index + 1) + 13))
        print(f"R6-4 arm {arm}", flush=True)
        stored = match(label, r64_args(arm), R64_K0[arm], seeds, 4, TARGET_64, JOB_A)
        make = r64_args(arm)
        batch = []
        for rep, seed in enumerate(seeds, start=1):
            name = f"r64/{arm}/rep{rep:02d}"
            batch.append((name, make(stored["k"], seed, 16, RESULTS / name)))
        run_many(batch, JOB_A)
        save_json(STATE / f"r64_{arm}_final.json", {"k": stored["k"], "seeds": seeds, "matched": stored["matched"], "day28_calibration": stored["day28"]})


# ---------------------------------------------------------------- R6-5

CLOSURE_SEED1000 = HERE / "closures_seed1000.json"
R65_TARGET = 0.345
R65_ARMS = {
    # label: (agents, locations, starting coefficient)
    "w10": (HERE / "inputs" / "r65_w10" / "agents_wards.json", HERE / "inputs" / "r65_w10" / "locations_wards.json", 0.000138),
    "w100": (HERE / "inputs" / "r65_w100" / "agents_wards.json", HERE / "inputs" / "r65_w100" / "locations_wards.json", 0.000138),
    "w300": (HERE / "inputs" / "r65_w300" / "agents_wards.json", HERE / "inputs" / "r65_w300" / "locations_wards.json", 0.000138),
    "unsplit": (AGENTS2, LOCS1, 0.00011),
}


def r65_args(k, seed, weeks, run_dir=None):
    return [
        "--quarantinePolicy", "0", "--closures", str(CLOSURE_SEED1000), "-k", fmt(k), "-w", str(weeks), "--seed", str(seed),
        "--sheddingShape", "0.03", "--shuffleSchedules", "1", "--venueProfile", "off", "--venueStrength", "1", "--densityExponent", "1",
    ]


def r65(arms=None):
    for index, label in enumerate(arms or R65_ARMS):
        agents, locations, k0 = R65_ARMS[label]
        job = {"agents": agents, "locations": locations}
        pilot_seeds = list(range(65000 + 100 * (index + 1) + 1, 65000 + 100 * (index + 1) + 5))
        stored = match(f"r65_{label}", r65_args, k0, pilot_seeds, 7, R65_TARGET, job, measure=all_node_mean)
        k = stored["k"]
        batch = []
        for rep in range(1, 41):
            name = f"r65/{label}/rep{rep:02d}"
            batch.append((name, r65_args(k, 65500 + 100 * (index + 1) + rep, 7)))
        run_many(batch, job)
        values = [all_node_mean(RESULTS / f"r65/{label}/rep{rep:02d}") for rep in range(1, 41)]
        mean_all = sum(values) / len(values)
        print(f"R6-5 {label} k={k:.6g} pilot {stored['day28']:.4f} 40-rep mean {mean_all:.4f} ({mean_all / R65_TARGET - 1:+.1%})", flush=True)
        save_json(STATE / f"r65_{label}_final.json", {"k": k, "pilot_mean": stored["day28"], "pilot_matched": stored["matched"], "mean_40": mean_all, "values": values})


def r65_refine(arms=None, max_passes=4, slope=1.6):
    """Rescale k and rerun 40 replicates when the pooled 40-replicate mean offspring misses 0.345 by more than 3%.
    Every pass is kept: r65/<label> is the first set, r65/<label>_p2, _p3 and _p4 the later ones. The state
    file r65_<label>_final.json lists all sets; the last one is the arm's primary set. The pooled mean is
    (infected agents with an infector) / (infected agents), the same quantity as the chain mean in the results."""
    for index, label in enumerate(arms or R65_ARMS):
        agents, locations, _k0 = R65_ARMS[label]
        job = {"agents": agents, "locations": locations}
        info = json.loads((STATE / f"r65_{label}_final.json").read_text())
        sets = info.get("sets") or [{"dir": f"r65/{label}", "k": info["k"], "mean_40": info["mean_40"]}]
        for item in sets:
            item["pooled_mean"] = pooled_mean(item["dir"])
        k = sets[-1]["k"]
        mean_all = sets[-1]["pooled_mean"]
        print(f"R6-5 refine {label}: set {len(sets)} pooled mean {mean_all:.4f} ({mean_all / R65_TARGET - 1:+.1%})", flush=True)
        passes = len(sets)
        while abs(mean_all / R65_TARGET - 1.0) > TOL and passes < max_passes:
            passes += 1
            k = k * (R65_TARGET / mean_all) ** (1.0 / slope)
            prefix = f"r65/{label}_p{passes}"
            batch = []
            for rep in range(1, 41):
                name = f"{prefix}/rep{rep:02d}"
                batch.append((name, r65_args(k, 65500 + 100 * (index + 1) + 50 * passes + rep, 7)))
            run_many(batch, job)
            mean_all = pooled_mean(prefix)
            sets.append({"dir": prefix, "k": k, "mean_40": None, "pooled_mean": mean_all})
            print(f"R6-5 refine {label} pass {passes} k={k:.6g} pooled mean {mean_all:.4f} ({mean_all / R65_TARGET - 1:+.1%})", flush=True)
        info.update({"k": k, "mean_40": mean_all, "sets": sets, "final_dir": sets[-1]["dir"]})
        save_json(STATE / f"r65_{label}_final.json", info)


# ---------------------------------------------------------------- R6-6

R66_ALPHAS = (0.75, 0.5, 0.25, 0.0)
R66_K0 = {0.75: 0.00033, 0.5: 0.00011, 0.25: 0.00004, 0.0: 0.000015}


def r66():
    for index, alpha in enumerate(R66_ALPHAS):
        label = f"r66_alpha{alpha:g}"
        seeds = list(range(66000 + 100 * (index + 1) + 1, 66000 + 100 * (index + 1) + 13))

        def make(k, seed, weeks, run_dir, alpha=alpha):
            return base_args(k, seed, weeks, alpha=alpha)

        print(f"R6-6 alpha {alpha}", flush=True)
        match(label, make, R66_K0[alpha], seeds, 4, TARGET_61, JOB_A, pilot=3)


# ---------------------------------------------------------------- R6-2

K_A0 = 0.00041
K_E = 0.000497841223604006
K_P0 = 0.0004972587500573815
R62_WEEKS = 16
R62_REPS = 8


def r62():
    """A0, E and P0 for 16 weeks with every infection episode logged. Needs the build with --episodeTrace.
    Vaccination is switched off so that reinfection is governed by infection-acquired protection alone."""
    if "build_r62" not in str(run_x21.BINARY):
        raise SystemExit("set PANSIM_BIN to the build_r62 binary, which has --episodeTrace")
    arms = {"A0": ([], K_A0), "E": (PS1_FLAGS["E"], K_E), "P0": (PS1_FLAGS["P0"], K_P0)}
    batch = []
    for index, (arm, (flags, k)) in enumerate(arms.items()):
        for rep in range(1, R62_REPS + 1):
            seed = 62000 + 100 * (index + 1) + rep
            name = f"r62/{arm}/rep{rep:02d}"
            extra = list(flags) + ["--immunizationStart", "100000", "--episodeTrace", str(RESULTS / name / "episodes.tsv")]
            batch.append((name, base_args(k, seed, R62_WEEKS, extra)))
    run_many(batch, JOB_A)


# ---------------------------------------------------------------- R6-7

R67_GROUPS = (30, 100)
# A factor is saturated when the group attack rate is close to 1 for one infectious attendee:
# exponent = k * (1 / group) * factor * 120 minutes, about 4.6 at these values.
R67_FACTOR = {30: 3000, 100: 10000}
R67_PILOT_RATES = (0.003, 0.01, 0.03, 0.1, 0.3, 1.0)
R67_TARGET_K = 0.3


def r67_args(group, factor, rate):
    def make(k, seed, weeks, run_dir):
        extra = [
            "--eventRate", fmt(rate), "--eventFactor", fmt(factor), "--eventTypes", EVENT_TYPES,
            "--eventGroupSize", str(group), "--eventDurationHours", "2",
            "--eventGroupLog", str(Path(run_dir) / "events.tsv"),
        ]
        return base_args(k, seed, weeks, extra)
    return make


def pooled_moment_k(prefix, count):
    import numpy as np
    from r6stats import index_table, mom_k
    parts = []
    for rep in range(1, count + 1):
        _ids, total, _event = index_table(RESULTS / f"{prefix}/rep{rep:02d}/trace.tsv")
        parts.append(total)
    return mom_k(np.concatenate(parts))


def r67():
    """Closed-group events. Needs the build with --eventGroupSize (build_r67).

    The factor alone cannot reach moment k 0.3 at an event rate of 0.3% (the group attack rate saturates and few
    events have an infectious attendee), so the factor is fixed at a saturated value and the event rate is tuned."""
    if "build_r67" not in str(run_x21.BINARY):
        raise SystemExit("set PANSIM_BIN to the build_r67 binary, which has --eventGroupSize")
    for index, group in enumerate(R67_GROUPS):
        factor = R67_FACTOR[group]
        pilot_seeds = list(range(67000 + 1000 * (index + 1) + 1, 67000 + 1000 * (index + 1) + 7))
        full_seeds = list(range(67000 + 1000 * (index + 1) + 101, 67000 + 1000 * (index + 1) + 113))
        k_pilot = 0.00038
        state_path = STATE / f"r67_M{group}_params.json"
        if state_path.exists():
            params = json.loads(state_path.read_text())
        else:
            points = []
            for rate in R67_PILOT_RATES:
                batch = []
                for rep, seed in enumerate(pilot_seeds, start=1):
                    name = f"r67/pilot_M{group}_r{rate:g}/rep{rep:02d}"
                    batch.append((name, r67_args(group, factor, rate)(k_pilot, seed, 4, RESULTS / name)))
                run_many(batch, JOB_A)
                kk = pooled_moment_k(f"r67/pilot_M{group}_r{rate:g}", len(pilot_seeds))
                d28 = sum(day28(RESULTS / f"r67/pilot_M{group}_r{rate:g}/rep{r:02d}") for r in range(1, len(pilot_seeds) + 1)) / len(pilot_seeds)
                points.append({"rate": rate, "k_mom": kk, "day28": d28})
                print(f"R6-7 M {group} factor {factor} pilot rate {rate:g}: moment k {kk:.3f} day28 {d28:.0f}", flush=True)
                if kk < 0.2:
                    break
            lows = [p for p in points if p["k_mom"] > R67_TARGET_K]
            highs = [p for p in points if p["k_mom"] <= R67_TARGET_K]
            if lows and highs:
                lo, hi = lows[-1], highs[0]
                frac = math.log(lo["k_mom"] / R67_TARGET_K) / math.log(lo["k_mom"] / hi["k_mom"])
                rate = math.exp(math.log(lo["rate"]) + frac * (math.log(hi["rate"]) - math.log(lo["rate"])))
            else:
                rate = points[-1]["rate"]
                print(f"R6-7 M {group}: pilot did not bracket moment k 0.3; using rate {rate}", flush=True)
            params = {"group": group, "factor": factor, "rate": rate, "pilot": points}
            save_json(state_path, params)
        rate = params["rate"]
        label = f"r67_M{group}"
        print(f"R6-7 M {group} factor {factor} rate {rate:.4g}", flush=True)
        stored = match(label, r67_args(group, factor, rate), k_pilot, full_seeds, 4, TARGET_61, JOB_A)
        kk = pooled_moment_k(stored["prefix"], len(full_seeds))
        print(f"R6-7 M {group} matched day28 {stored['day28']:.0f} moment k {kk:.3f} at rate {rate:.4g}", flush=True)


R67_REFINE = {30: (0.05, 0.08), 100: (0.005, 0.0065)}


def r67_refine(rates=None, groups=None):
    """Extra rates for R6-7 after the first matched cells missed moment k 0.3. Each is matched on day 28."""
    if "build_r67" not in str(run_x21.BINARY):
        raise SystemExit("set PANSIM_BIN to the build_r67 binary")
    for index, group in enumerate(R67_GROUPS):
        if groups and group not in groups:
            continue
        factor = R67_FACTOR[group]
        full_seeds = list(range(67000 + 1000 * (index + 1) + 101, 67000 + 1000 * (index + 1) + 113))
        for rate in (rates or R67_REFINE[group]):
            label = f"r67_M{group}_rate{rate:g}"
            stored = match(label, r67_args(group, factor, rate), 0.00014, full_seeds, 4, TARGET_61, JOB_A)
            kk = pooled_moment_k(stored["prefix"], len(full_seeds))
            print(f"R6-7 refine M {group} rate {rate:g}: matched day28 {stored['day28']:.0f} k {stored['k']:.5g} moment k {kk:.3f}", flush=True)


def r67_extra():
    r67_refine(rates=(0.0075,), groups=(100,))


TASKS = {"r61": r61, "r62": r62, "r64": r64, "r65": r65, "r65_refine": r65_refine, "r66": r66, "r67": r67, "r67_refine": r67_refine, "r67_extra": r67_extra}

if __name__ == "__main__":
    for name in sys.argv[1:]:
        TASKS[name]()
