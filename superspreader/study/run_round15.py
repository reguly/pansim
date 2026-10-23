#!/usr/bin/env python3
"""Note 73 round 15:
- Run C: B1 cells of worlds 1, 2b, 3b run to day 42 (-w 6) on seeds 77001..77012 with infection/episode/event traces.
- Run D: B1 cells of worlds 1, 2b, 3b at density exponent alpha = 0.5 and alpha = 0, calibrated on 76001..76006 (6 reps,
  up to 4 trials) and then run/verified on 77001..77012 (12 reps) within 3% of 6,211.25.

  python3 superspreader/study/run_round15.py runC [w1|w2b|w3b|all]
  python3 superspreader/study/run_round15.py runD <alpha> [w1|w2b|w3b|all]
  python3 superspreader/study/run_round15.py all
"""
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ.setdefault("PANSIM_BIN", str(HERE.parent.parent / "build_r10" / "panSim"))
os.environ.setdefault("PANSIM_JOBS", "4")
sys.path.insert(0, str(HERE))

import run_round6 as r6  # noqa: E402
import run_round8 as r8  # noqa: E402
import run_x21  # noqa: E402

RESULTS = HERE / "results" / "round15"
STATE = RESULTS / "state"
R14_STATE = HERE / "results" / "round14" / "state"
run_x21.RESULTS = RESULTS
r6.RESULTS = RESULTS
r6.STATE = STATE

TARGET = 6211.25
TOL = 0.03
CAL_SEEDS = list(range(76001, 76007))
SEEDS_77 = list(range(77001, 77013))
WORLDS = ("w1", "w2b", "w3b")

# Exact B1 parameters and coefficients from Round 14 (69_tuning_log.csv and results/round14/state/r14_b1final_*.json)
B1_CELLS = {
    "w1": {"param": "0.24", "k": 0.0005151697600710852},
    "w2b": {"param": "0.4", "k": 0.00011688421162113477},
    "w3b": {"param": "0.17", "k": 0.00010587156817289024},
}

ALPHA_SCALE = {0.5: 0.13, 0.0: 0.0077}


def world_spec(world):
    param = B1_CELLS[world]["param"]
    if world == "w1":
        return ["--sheddingShape", param], r6.LOCS1, False
    if world == "w2b":
        return r8.ARMS["s8_2_t1_L10"]["flags"] + ["--sheddingShape", param], r8.locs_for(10), True
    if world == "w3b":
        return [
            "--eventRate", param,
            "--eventFactor", "3000",
            "--eventTypes", "5,8",
            "--eventGroupSize", "30",
            "--eventDurationHours", "2",
        ], r6.LOCS1, True
    raise KeyError(world)


def job_for(world):
    _flags, locs, _dump = world_spec(world)
    return {"agents": r6.AGENTS2, "locations": locs}


def make_for(world, alpha=1.0, episode_trace=False):
    flags, _locs, dump = world_spec(world)

    def make(k, seed, weeks, run_dir):
        extra = list(flags)
        if world == "w3b":
            extra += ["--eventGroupLog", str(Path(run_dir) / "events.tsv")]
        if dump:
            extra += ["--hviDump", str(Path(run_dir) / "hvi.csv")]
        if episode_trace:
            extra += ["--episodeTrace", str(Path(run_dir) / "episodes.tsv")]
        return r6.base_args(k, seed, weeks, extra, alpha=alpha)

    return make


def run_c_world(world):
    """Run B1 cell to day 42 (-w 6) on seeds 77001..77012 and verify day-28 parity with Round 14."""
    k = B1_CELLS[world]["k"]
    make = make_for(world, alpha=1.0, episode_trace=True)
    prefix = f"runC/{world}"
    batch = []
    for idx, seed in enumerate(SEEDS_77, start=1):
        name = f"{prefix}/rep{idx:02d}"
        batch.append((name, make(k, seed, 6, RESULTS / name)))
    r6.run_many(batch, job_for(world))

    d28_vals = [r6.day28(RESULTS / n) for n, _ in batch]
    d42_vals = [int(r6.load_daily(RESULTS / n / "stdout.txt")[41]["INF"]) for n, _ in batch]
    r14_st = json.loads((R14_STATE / f"r14_b1final_{world}.json").read_text())
    r14_d28 = r14_st["points"][-1]["values"]
    exact_d28 = (d28_vals == r14_d28)

    state = {
        "world": world,
        "param": B1_CELLS[world]["param"],
        "k": k,
        "weeks": 6,
        "seeds": SEEDS_77,
        "prefix": prefix,
        "day28": sum(d28_vals) / len(d28_vals),
        "day42": sum(d42_vals) / len(d42_vals),
        "values_day28": d28_vals,
        "values_day42": d42_vals,
        "r14_values_day28": r14_d28,
        "day28_exact_match_r14": exact_d28,
    }
    r6.save_json(STATE / f"r15_c_{world}.json", state)
    print(
        f"R15 RunC {world}: k={k:.6g} day28={state['day28']:.1f} day42={state['day42']:.1f} "
        f"exact_d28_match_r14={exact_d28}",
        flush=True,
    )
    return state


def run_d_world(world, alpha):
    """Calibrate background coefficient at density exponent alpha on 76001..76006 (up to 4 trials of 6 reps),
    then run 12 replicates on 77001..77012 (recalibrating if outside 3% of 6,211.25)."""
    alpha = float(alpha)
    tag = f"a{alpha:g}_{world}"
    state_path = STATE / f"r15_d_{tag}.json"
    if state_path.exists():
        stored = json.loads(state_path.read_text())
        if stored.get("matched"):
            print(f"R15 RunD {tag} already matched: k={stored['k']:.6g} day28={stored['day28']:.1f}", flush=True)
            return stored

    make = make_for(world, alpha=alpha, episode_trace=False)
    job = job_for(world)
    k = B1_CELLS[world]["k"] * ALPHA_SCALE[alpha]

    cal_trials = []
    # Phase 1: up to 4 trials of 6 replicates on calibration seeds 76001..76006
    for trial in range(1, 5):
        k_str = r6.fmt(k)
        pref = f"calD/{tag}/cal6_k{k_str}"
        batch = [(f"{pref}/rep{i:02d}", make(k, sd, 4, RESULTS / f"{pref}/rep{i:02d}"))
                 for i, sd in enumerate(CAL_SEEDS, start=1)]
        r6.run_many(batch, job)
        vals = [r6.day28(RESULTS / n) for n, _ in batch]
        mean_val = sum(vals) / len(vals)
        cal_trials.append({
            "phase": "cal6_76001_76006",
            "trial": trial,
            "k": k,
            "day28": mean_val,
            "values": vals,
            "prefix": pref,
            "within_3pct": abs(mean_val - TARGET) / TARGET <= TOL,
        })
        print(
            f"R15 RunD {tag} cal6 trial {trial}: k={k_str} day28={mean_val:.1f} "
            f"({(mean_val - TARGET) / TARGET:+.1%})",
            flush=True,
        )
        if abs(mean_val - TARGET) / TARGET <= TOL:
            break
        # Secant / power-law update on k
        if len(cal_trials) >= 2:
            x0, y0 = cal_trials[-2]["k"], max(cal_trials[-2]["day28"], 1.0)
            x1, y1 = cal_trials[-1]["k"], max(cal_trials[-1]["day28"], 1.0)
            if y1 != y0 and x1 != x0:
                slope = (math.log(y1) - math.log(y0)) / (math.log(x1) - math.log(x0))
                slope = min(max(slope, 0.25), 5.0)
                step = (math.log(TARGET) - math.log(y1)) / slope
                step = max(min(step, math.log(5.0)), -math.log(5.0))
                k = x1 * math.exp(step)
            else:
                k = x1 * (TARGET / y1) ** 0.7
        else:
            k = k * (TARGET / max(mean_val, 1.0)) ** 0.7

    # Pick the cal6 trial closest to TARGET as the starting point for 77001..77012
    best_cal = min(cal_trials, key=lambda t: abs(t["day28"] - TARGET))
    k = best_cal["k"]
    # If the best cal6 trial was still outside 3%, take one secant step before running 77001..77012
    if not best_cal["within_3pct"] and len(cal_trials) >= 2:
        s_pts = sorted(cal_trials, key=lambda t: abs(t["day28"] - TARGET))[:2]
        x0, y0 = s_pts[0]["k"], max(s_pts[0]["day28"], 1.0)
        x1, y1 = s_pts[1]["k"], max(s_pts[1]["day28"], 1.0)
        if y1 != y0 and x1 != x0:
            slope = min(max((math.log(y1) - math.log(y0)) / (math.log(x1) - math.log(x0)), 0.25), 5.0)
            step = max(min((math.log(TARGET) - math.log(y0)) / slope, math.log(3.0)), -math.log(3.0))
            k = x0 * math.exp(step)

    # Phase 2: 12 replicates on seeds 77001..77012 (with up to 3 adjustments if 77001..77012 differs from 76001..76006)
    final_trials = []
    for attempt in range(1, 4):
        k_str = r6.fmt(k)
        pref = f"runD/{tag}/k{k_str}"
        batch = [(f"{pref}/rep{i:02d}", make(k, sd, 4, RESULTS / f"{pref}/rep{i:02d}"))
                 for i, sd in enumerate(SEEDS_77, start=1)]
        r6.run_many(batch, job)
        vals = [r6.day28(RESULTS / n) for n, _ in batch]
        mean_val = sum(vals) / len(vals)
        matched = abs(mean_val - TARGET) / TARGET <= TOL
        final_trials.append({
            "phase": "final12_77001_77012",
            "trial": attempt,
            "k": k,
            "day28": mean_val,
            "values": vals,
            "prefix": pref,
            "within_3pct": matched,
        })
        print(
            f"R15 RunD {tag} final12 attempt {attempt}: k={k_str} day28={mean_val:.1f} "
            f"({(mean_val - TARGET) / TARGET:+.1%}) matched={matched}",
            flush=True,
        )
        if matched:
            break
        # Estimate log-log slope from final_trials (or from cal_trials)
        slope = 1.4
        if len(final_trials) >= 2:
            x0, y0 = final_trials[-2]["k"], max(final_trials[-2]["day28"], 1.0)
            x1, y1 = final_trials[-1]["k"], max(final_trials[-1]["day28"], 1.0)
            if y1 != y0 and x1 != x0:
                slope = min(max((math.log(y1) - math.log(y0)) / (math.log(x1) - math.log(x0)), 0.25), 5.0)
        elif len(cal_trials) >= 2:
            x0, y0 = cal_trials[-2]["k"], max(cal_trials[-2]["day28"], 1.0)
            x1, y1 = cal_trials[-1]["k"], max(cal_trials[-1]["day28"], 1.0)
            if y1 != y0 and x1 != x0:
                slope = min(max((math.log(y1) - math.log(y0)) / (math.log(x1) - math.log(x0)), 0.25), 5.0)
        step = max(min((math.log(TARGET) - math.log(max(mean_val, 1.0))) / slope, math.log(3.0)), -math.log(3.0))
        k = k * math.exp(step)

    chosen = min(final_trials, key=lambda t: abs(t["day28"] - TARGET))
    state = {
        "world": world,
        "alpha": alpha,
        "param": B1_CELLS[world]["param"],
        "k": chosen["k"],
        "day28": chosen["day28"],
        "matched": chosen["within_3pct"],
        "target": TARGET,
        "prefix": chosen["prefix"],
        "seeds": SEEDS_77,
        "values": chosen["values"],
        "cal_trials": cal_trials,
        "final_trials": final_trials,
    }
    r6.save_json(state_path, state)
    return state


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "runC":
        which = sys.argv[2] if len(sys.argv) > 2 else "all"
        worlds = WORLDS if which == "all" else (which,)
        for w in worlds:
            run_c_world(w)
    elif cmd == "runD":
        alpha = float(sys.argv[2])
        which = sys.argv[3] if len(sys.argv) > 3 else "all"
        worlds = WORLDS if which == "all" else (which,)
        for w in worlds:
            run_d_world(w, alpha)
    elif cmd == "all":
        for w in WORLDS:
            run_c_world(w)
        for alpha in (0.5, 0.0):
            for w in WORLDS:
                run_d_world(w, alpha)
    else:
        raise SystemExit(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
