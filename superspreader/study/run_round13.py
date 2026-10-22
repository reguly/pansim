#!/usr/bin/env python3
"""Note 65 round 13: noise, replication and sensitivity of the four matched worlds.

Worlds, flags, locations and dump options are those of round 12 (notes 58, 61); only the seed set,
the background coefficient (recalibrated, frozen or scaled) and, for N3, one tuned parameter change.

  PANSIM_JOBS=4 python3 superspreader/study/run_round13.py cal   <world> <setname>   # N1 items 1, 3
  PANSIM_JOBS=4 python3 superspreader/study/run_round13.py frozen <world> <setname>  # N1 item 2
  PANSIM_JOBS=4 python3 superspreader/study/run_round13.py sens  <world> <mult>      # N2 (seeds 77001..77012)

world in w1 w2a w2b w3b; setname in s78 s79 (seeds 78001..78012, 79001..79012).
"""
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ.setdefault("PANSIM_BIN", str(HERE.parent.parent / "build_r10" / "panSim"))
sys.path.insert(0, str(HERE))

import run_round6 as r6  # noqa: E402
import run_round8 as r8  # noqa: E402
import run_x21  # noqa: E402

RESULTS = HERE / "results" / "round13"
STATE = RESULTS / "state"
run_x21.RESULTS = RESULTS
r6.RESULTS = RESULTS
r6.STATE = STATE
TARGET = 6211.25
R12 = {  # round-12 coefficient and the state file it came from
    "w1": HERE / "results/round10/state/r10_w1_sh0.32.json",
    "w2a": HERE / "results/round11/state/r11_w2_L30_sh0.70.json",
    "w2b": HERE / "results/round11/state/r11_w2_L10_sh0.58.json",
    "w3b": HERE / "results/round12/state/r12_w3b_M30_rate0.1456.json",
}
SETS = {"s77": 77001, "s78": 78001, "s79": 79001, "s76": 76001}


def seeds_of(setname, n=12):
    return list(range(SETS[setname], SETS[setname] + n))


def round12_k(world):
    return json.loads(R12[world].read_text())["k"]


def world_flags(world, param=None):
    """Extra command-line flags and locations file of a world, as in rounds 10 to 12."""
    if world == "w1":
        return ["--sheddingShape", str(param if param is not None else "0.32")], r6.LOCS1, False
    if world == "w2a":
        return r8.ARMS["s8_2_t1_L30"]["flags"] + ["--sheddingShape", "0.70"], r8.locs_for(30), True
    if world == "w2b":
        return r8.ARMS["s8_2_t1_L10"]["flags"] + ["--sheddingShape", str(param if param is not None else "0.58")], r8.locs_for(10), True
    if world == "w3b":
        return ["--eventRate", str(param if param is not None else "0.1456"), "--eventFactor", "3000", "--eventTypes", "5,8",
                "--eventGroupSize", "30", "--eventDurationHours", "2"], r6.LOCS1, True
    raise KeyError(world)


def make_for(world, param=None):
    flags, _locs, dump = world_flags(world, param)

    def make(k, seed, w, run_dir):
        extra = list(flags)
        if world == "w3b":
            extra += ["--eventGroupLog", str(Path(run_dir) / "events.tsv")]
        if dump:
            extra += ["--hviDump", str(Path(run_dir) / "hvi.csv")]
        return r6.base_args(k, seed, w, extra)
    return make


REDRAWN = HERE / "inputs" / "r13_agents_venues_redrawn.json"


def job_for(world, agents=None):
    _flags, locs, _dump = world_flags(world)
    return {"agents": agents or r6.AGENTS2, "locations": locs}


def cal(world, setname):
    stored = r6.match(f"r13_{setname}_{world}", make_for(world), round12_k(world), seeds_of(setname), 4, TARGET,
                      job_for(world), pilot=4)
    print(f"R13 cal {setname} {world} k={stored['k']:.6g} day28={stored['day28']:.1f} matched={stored['matched']}", flush=True)


def fixed_k(tag, world, k, seeds, weeks=4):
    """Runs at a fixed coefficient (no calibration). Output: <tag>/<world>/repNN."""
    make = make_for(world)
    batch = []
    for index, seed in enumerate(seeds, start=1):
        name = f"{tag}/{world}/rep{index:02d}"
        batch.append((name, make(k, seed, weeks, RESULTS / name)))
    r6.run_many(batch, job_for(world))
    means = [r6.day28(RESULTS / n) for n, _ in batch]
    day28 = sum(means) / len(means)
    r6.save_json(STATE / f"r13_{tag}_{world}.json", {"k": k, "day28": day28, "matched": None, "target": TARGET,
                                                       "prefix": f"{tag}/{world}", "seeds": seeds, "values": means})
    print(f"R13 {tag} {world} k={k:.6g} day28={day28:.1f} ({day28 / TARGET - 1:+.1%})", flush=True)


def frozen(world, setname):
    fixed_k(f"frozen_{setname}", world, round12_k(world), seeds_of(setname))


def sens(world, mult):
    m = float(mult)
    fixed_k(f"sens_{m:g}", world, round12_k(world) * m, seeds_of("s77"))


# ---------------------------------------------------------------- N3: target band

# anchors from earlier rounds: (parameter, likelihood k, background coefficient) used only to start the secant
N3_ANCHORS = {
    "w1": [(0.32, 0.357, 0.000499), (0.5, 0.5255, 0.00047), (1.0, 0.919, 0.00044)],
    "w2b": [(0.58, 0.365, 0.000117), (1.0, 0.5096, 0.000094)],
    "w3b": [(0.1456, 0.306, 0.000130), (0.08, 0.5678, 0.000231), (0.05, 0.8887, 0.000304)],
}
N3_SEEDS_CAL = list(range(76001, 76007))


def _interp(world, target):
    """Log-log interpolation of (parameter, coefficient) at the target k from the anchors."""
    import math
    a = sorted(N3_ANCHORS[world], key=lambda t: t[1])
    for (p0, k0, c0), (p1, k1, c1) in zip(a, a[1:]):
        if k0 <= target <= k1:
            f = (math.log(target) - math.log(k0)) / (math.log(k1) - math.log(k0))
            return math.exp(math.log(p0) + f * (math.log(p1) - math.log(p0))), math.exp(math.log(c0) + f * (math.log(c1) - math.log(c0)))
    (p0, k0, c0), (p1, k1, c1) = (a[0], a[1]) if target < a[0][1] else (a[-2], a[-1])
    slope = (math.log(p1) - math.log(p0)) / (math.log(k1) - math.log(k0))
    cslope = (math.log(c1) - math.log(c0)) / (math.log(k1) - math.log(k0))
    return (math.exp(math.log(p1) + slope * (math.log(target) - math.log(k1))),
            math.exp(math.log(c1) + cslope * (math.log(target) - math.log(k1))))


def _measure(run_dirs):
    import analyze_round13 as a13
    cores = [a13.replicate_core(r) for r in run_dirs]
    total = __import__("numpy").concatenate([c[2] for c in cores])
    from r6stats import ml_k, mom_k
    return ml_k(total), mom_k(total), int(total.size)


def n3(world, target):
    """At most three trials of the tuned parameter, each with its coefficient calibrated on 76001..76006, then the
    final cell on 77001..77012 with the coefficient recalibrated."""
    import math
    target = float(target)
    log_path = STATE / f"n3_trials_{world}_{target:g}.json"
    trials = json.loads(log_path.read_text()) if log_path.exists() else []
    param, coeff = _interp(world, target)
    for it in range(3):
        if len(trials) > it:
            continue
        if it >= 1:
            pts = [t for t in trials if t.get("matched")] or trials
            if len(pts) >= 2 and pts[-1]["param"] != pts[-2]["param"] and pts[-1]["k_ml"] != pts[-2]["k_ml"]:
                slope = (math.log(pts[-1]["param"]) - math.log(pts[-2]["param"])) / (math.log(pts[-1]["k_ml"]) - math.log(pts[-2]["k_ml"]))
            else:
                slope = (math.log(param) - math.log(N3_ANCHORS[world][0][0])) / (math.log(target) - math.log(N3_ANCHORS[world][0][1]))
            param = pts[-1]["param"] * math.exp(slope * (math.log(target) - math.log(pts[-1]["k_ml"])))
            coeff = pts[-1]["coefficient"]
        label = f"r13_n3trial-t{target:g}-i{it + 1}_{world}"
        st = r6.match(label, make_for(world, f"{param:.4g}"), coeff, N3_SEEDS_CAL, 4, TARGET, job_for(world))
        dirs = sorted(p.parent for p in (RESULTS / st["prefix"]).glob("rep*/trace.tsv"))
        k_ml, k_mom, n = _measure(dirs)
        trials.append({"iteration": it + 1, "param": float(f"{param:.4g}"), "coefficient": st["k"], "day28": st["day28"],
                       "matched": st["matched"], "k_ml": k_ml, "k_mom": k_mom, "index_cases": n, "replicates": len(dirs)})
        r6.save_json(log_path, trials)
        print(f"R13 n3 {world} target {target:g} trial {it + 1}: param={param:.4g} k={st['k']:.5g} day28={st['day28']:.0f} "
              f"k_ml={k_ml:.3f} k_mom={k_mom:.3f}", flush=True)
        if abs(k_ml - target) <= 0.03:
            break
    best = min(trials, key=lambda t: abs(t["k_ml"] - target))
    label = f"r13_n3final-t{target:g}_{world}"
    st = r6.match(label, make_for(world, f"{best['param']:.4g}"), best["coefficient"], seeds_of("s77"), 4, TARGET,
                  job_for(world), pilot=4)
    r6.save_json(STATE / f"n3_final_{world}_{target:g}.json", {"param": best["param"], "target": target, "trial": best["iteration"],
                                                                "coefficient": st["k"], "matched": st["matched"], "day28": st["day28"]})
    print(f"R13 n3 final {world} target {target:g}: param={best['param']:.4g} k={st['k']:.5g} day28={st['day28']:.0f} matched={st['matched']}", flush=True)


def n5(world):
    """N5: the same world on a redrawn venue assignment (build_r13_inputs.py), seeds 77001..77012, recalibrated."""
    st = r6.match(f"r13_n5_{world}", make_for(world), round12_k(world), seeds_of("s77"), 4, TARGET,
                  job_for(world, REDRAWN), pilot=4)
    print(f"R13 n5 {world} k={st['k']:.6g} day28={st['day28']:.1f} matched={st['matched']}", flush=True)


TASKS = {"n5": lambda: n5(sys.argv[2]), "n3": lambda: n3(sys.argv[2], sys.argv[3]), "cal": lambda: cal(sys.argv[2], sys.argv[3]), "frozen": lambda: frozen(sys.argv[2], sys.argv[3]),
         "sens": lambda: sens(sys.argv[2], sys.argv[3])}

if __name__ == "__main__":
    TASKS[sys.argv[1]]()
