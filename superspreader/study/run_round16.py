#!/usr/bin/env python3
"""Note 82 round 16.

  PANSIM_JOBS=2 python3 superspreader/study/run_round16.py E
  python3 superspreader/study/run_round16.py A
  python3 superspreader/study/run_round16.py B
  python3 superspreader/study/run_round16.py G

Run E re-runs the five round-15 cells with --infectiousEpisodeLog and checks
offspring histograms against 74_d_replicate_histograms.csv. A mismatched cell
is reported and not treated as a matched re-run. Runs A and B stop at the
trial limits in note 82.
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ.setdefault("PANSIM_BIN", str(HERE.parent.parent / "build_r10" / "panSim"))
os.environ.setdefault("PANSIM_JOBS", "2")
sys.path.insert(0, str(HERE))

import run_round6 as r6  # noqa: E402
import run_round13 as r13  # noqa: E402
import run_round14 as r14  # noqa: E402
import run_round15 as r15  # noqa: E402
import run_round8 as r8  # noqa: E402
import run_x21  # noqa: E402

RESULTS = HERE / "results" / "round16"
STATE = RESULTS / "state"
run_x21.RESULTS = RESULTS
r6.RESULTS = RESULTS
r6.STATE = STATE

TARGET = 6211.25
TOL = 0.03
UNKNOWN = 4294967295
STEPS = 144
SEEDS_77 = list(range(77001, 77013))
R15_STATE = HERE / "results" / "round15" / "state"
R14_STATE = HERE / "results" / "round14" / "state"
HIST_REF = HERE.parent / "74_d_replicate_histograms.csv"
B2_MEAN = 0.88
B2_K = 0.27


def save(path, obj):
    r6.save_json(path, obj)


def seeds(first, n):
    return list(range(first, first + n))


def offspring_hist(trace_path):
    """Same index-case filter as analyze_round15.replicate_core_d (days 1-10, known infector, cd <= day+14)."""
    children = defaultdict(list)
    rows = []
    with open(trace_path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        col = {name: i for i, name in enumerate(header)}
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            agent = int(parts[col["agent"]])
            inf = int(parts[col["infector"]])
            day = int(parts[col["timestamp"]]) // STEPS
            rows.append((agent, inf, day))
            if inf != UNKNOWN:
                children[inf].append(day)
    counts = Counter()
    for agent, inf, day in rows:
        if inf == UNKNOWN or not (1 <= day <= 10):
            continue
        n = sum(1 for cd in children.get(agent, ()) if cd <= day + 14)
        counts[n] += 1
    return counts


def ref_hists(arm):
    out = defaultdict(Counter)
    with open(HIST_REF) as handle:
        header = handle.readline().rstrip("\n").split(",")
        for line in handle:
            parts = line.rstrip("\n").split(",")
            row = dict(zip(header, parts))
            if row["arm"] != arm:
                continue
            out[int(row["replicate"])][int(row["offspring_total"])] += int(row["index_cases"])
    return out


def hist_diff(got, ref):
    keys = set(got) | set(ref)
    return {k: (got.get(k, 0), ref.get(k, 0)) for k in sorted(keys) if got.get(k, 0) != ref.get(k, 0)}


def make_e(world, alpha):
    base = r15.make_for(world, alpha=alpha, episode_trace=False)

    def make(k, seed, weeks, run_dir):
        args = base(k, seed, weeks, run_dir)
        args += ["--infectiousEpisodeLog", str(Path(run_dir) / "episodes_inf.tsv")]
        return args

    return make


def e_cells():
    cells = []
    for world in ("w1", "w2b", "w3b"):
        cells.append({
            "name": f"{world}_a1",
            "world": world,
            "alpha": 1.0,
            "k": r15.B1_CELLS[world]["k"],
            "ref_arm": f"{world}:B1_alpha1",
        })
    for alpha in (0.5, 0.0):
        stored = json.loads((R15_STATE / f"r15_d_a{alpha:g}_w1.json").read_text())
        cells.append({
            "name": f"w1_a{alpha:g}",
            "world": "w1",
            "alpha": float(alpha),
            "k": stored["k"],
            "ref_arm": f"w1:D_alpha{alpha:g}",
        })
    return cells


def run_e(only=None):
    STATE.mkdir(parents=True, exist_ok=True)
    summary = []
    for cell in e_cells():
        if only and cell["name"] != only and cell["world"] != only:
            continue
        name = cell["name"]
        prefix = f"E/{name}"
        make = make_e(cell["world"], cell["alpha"])
        job = r15.job_for(cell["world"])
        batch = []
        for i, seed in enumerate(SEEDS_77, start=1):
            run_name = f"{prefix}/rep{i:02d}"
            batch.append((run_name, make(cell["k"], seed, 4, RESULTS / run_name)))
        r6.run_many(batch, job)
        reference = ref_hists(cell["ref_arm"])
        diffs = {}
        for i in range(1, 13):
            got = offspring_hist(RESULTS / prefix / f"rep{i:02d}" / "trace.tsv")
            diff = hist_diff(got, reference.get(i, Counter()))
            if diff:
                diffs[str(i)] = {str(k): {"got": a, "ref": b} for k, (a, b) in diff.items()}
        state = {
            "cell": name,
            "world": cell["world"],
            "alpha": cell["alpha"],
            "k": cell["k"],
            "ref_arm": cell["ref_arm"],
            "seeds": SEEDS_77,
            "weeks": 4,
            "prefix": prefix,
            "histogram_equal": not diffs,
            "stopped": bool(diffs),
            "hist_diff": diffs,
        }
        save(STATE / f"e_{name}.json", state)
        summary.append({"cell": name, "histogram_equal": state["histogram_equal"], "reps_differing": len(diffs)})
        print(f"R16 E {name}: histogram_equal={state['histogram_equal']} reps_differing={len(diffs)}", flush=True)
        if diffs:
            print(f"R16 E {name}: STOP on this cell; histogram differs from round 15", flush=True)
    save(STATE / "e_summary.json", summary)
    return summary


def run_fixed(label, make, job, coeff, seed_list, weeks=4):
    batch = []
    for i, seed in enumerate(seed_list, start=1):
        name = f"{label}/rep{i:02d}"
        batch.append((name, make(coeff, seed, weeks, RESULTS / name)))
    r6.run_many(batch, job)
    return [RESULTS / n for n, _ in batch]


def run_a():
    """World 3b B1 (event rate 0.17, group 30, factor 3000). Four secant calibrations, trial limit 5, no pilot."""
    make = r15.make_for("w3b", alpha=1.0, episode_trace=False)
    job = r15.job_for("w3b")
    k0 = r15.B1_CELLS["w3b"]["k"]
    sets = [
        ("a12_88001", seeds(88001, 12)),
        ("a12_88013", seeds(88013, 12)),
        ("a12_88025", seeds(88025, 12)),
        ("a36_88001", seeds(88001, 36)),
    ]
    done = []
    for label, seed_list in sets:
        stored = r6.match(label, make, k0, seed_list, 4, TARGET, job, tol=TOL, max_rounds=5, pilot=0)
        stored = dict(stored)
        stored["seeds"] = seed_list
        stored["n_trials"] = len([p for p in stored["points"] if not p.get("pilot")])
        stored["trial_limit"] = 5
        save(STATE / f"{label}.json", stored)
        print(f"R16 A {label}: k={stored['k']:.6g} day28={stored['day28']:.1f} matched={stored['matched']} trials={stored['n_trials']}", flush=True)
        done.append(stored)
    # Evaluate each of the four coefficients on all 36 seeds. Reuse a run when the seed was already
    # simulated at that coefficient in its own calibration directory.
    eval_rows = []
    all_seeds = seeds(88001, 36)
    for stored, (label, seed_list) in zip(done, sets):
        k = stored["k"]
        own = {seed: RESULTS / stored["prefix"] / f"rep{i:02d}" for i, seed in enumerate(seed_list, start=1)}
        dirs = []
        missing = []
        for seed in all_seeds:
            if seed in own and (own[seed] / "trace.tsv").exists():
                dirs.append(own[seed])
            else:
                missing.append(seed)
        if missing:
            dest = f"A/eval_{label}_k{k:.6g}"
            made = run_fixed(dest, make, job, k, missing, 4)
            by_seed = {}
            for run_dir in made:
                cmd = json.loads((run_dir / "command.json").read_text())
                by_seed[int(cmd[cmd.index("--seed") + 1])] = run_dir
            dirs = [own[s] if s in own and (own[s] / "trace.tsv").exists() else by_seed[s] for s in all_seeds]
        row = {"label": label, "k": k, "matched_on_own_set": stored["matched"], "own_day28": stored["day28"],
               "n_trials": stored["n_trials"], "eval_dirs": [str(p) for p in dirs]}
        save(STATE / f"a_eval_{label}.json", row)
        eval_rows.append(row)
        print(f"R16 A eval {label}: {len(dirs)} replicates at k={k:.6g}", flush=True)
    save(STATE / "a_manifest.json", eval_rows)


def b2_update(trials, slope0, coeff, param):
    last = trials[-1]
    beta = 0.9
    if len(trials) >= 2 and trials[-2]["coefficient"] != last["coefficient"] and trials[-2]["early_R"] > 0 and last["early_R"] > 0:
        b = math.log(last["early_R"] / trials[-2]["early_R"]) / math.log(last["coefficient"] / trials[-2]["coefficient"])
        if 0.3 <= b <= 2.0:
            beta = b
    floor = 0.03 * json.loads((R14_STATE / "b1_final_w1.json").read_text())["final"]["coefficient"]
    # floor is world-specific; caller passes it via slope path. Recompute below.
    del floor
    new_c = last["coefficient"] * (B2_MEAN / last["early_R"]) ** (1.0 / beta)
    new_p, _ = r14.next_param(trials, slope0, target=B2_K)
    return new_c, new_p


def measure_b(dirs):
    import analyze_round13 as a13
    from r6stats import ml_k, mom_k
    import numpy as np
    cores = [a13.replicate_core(d) for d in dirs]
    total = np.concatenate([c[2] for c in cores])
    return {
        "R": float(total.mean()) if total.size else float("nan"),
        "k_ml": float(ml_k(total)) if total.size > 1 else float("nan"),
        "k_mom": float(mom_k(total)) if total.size > 1 else float("nan"),
        "index_cases": int(total.size),
        "replicates": len(dirs),
        "day28": float(np.mean([c[0]["day28_cumulative_infections"] for c in cores])),
    }


def run_b(only=None):
    """B2 redo. Five trials on seeds 89001-89012, then up to four more if the mean is outside 3%, then one 36-seed run."""
    for world in ("w1", "w2b", "w3b"):
        if only and world != only:
            continue
        final14 = json.loads((R14_STATE / f"b2_final_{world}.json").read_text())["final"]
        param = float(final14["param"])
        coeff = float(final14["coefficient"])
        slope0 = r14.B1_START[world][2]
        b1_coeff = json.loads((R14_STATE / f"b1_final_{world}.json").read_text())["final"]["coefficient"]
        floor = 0.03 * b1_coeff
        log_path = STATE / f"b2_trials_{world}.json"
        trials = json.loads(log_path.read_text()) if log_path.exists() else []
        phase_limits = (("first12", 5), ("further12", 4))
        for phase, limit in phase_limits:
            have = [t for t in trials if t["phase"] == phase]
            if phase == "further12":
                if not trials:
                    break
                if abs(trials[-1]["early_R"] / B2_MEAN - 1) <= TOL:
                    print(f"R16 B {world}: mean inside 3% after {len(trials)} trials; no further trials", flush=True)
                    break
            for it in range(len(have), limit):
                if trials:
                    coeff, param = b2_update(trials, slope0, coeff, param)
                    coeff = max(floor, coeff)
                label = f"B/trial_{world}_{phase}_i{it + 1}"
                dirs = run_fixed(label, r13.make_for(world, r14.pfmt(param)), r13.job_for(world), coeff, seeds(89001, 12), 4)
                measured = measure_b(dirs)
                row = {
                    "phase": phase, "iteration": it + 1, "param": float(r14.pfmt(param)), "coefficient": coeff,
                    "early_R": measured["R"], "k_ml": measured["k_ml"], "k_mom": measured["k_mom"],
                    "day28": measured["day28"], "index_cases": measured["index_cases"], "prefix": label,
                    "mean_within_3pct": abs(measured["R"] / B2_MEAN - 1) <= TOL,
                    "k_within_0.03": abs(measured["k_ml"] - B2_K) <= 0.03,
                }
                trials.append(row)
                save(log_path, trials)
                print(f"R16 B {world} {phase} {it + 1}: param={row['param']:.4g} coeff={coeff:.5g} R={measured['R']:.3f} k_ml={measured['k_ml']:.3f}", flush=True)
                if row["mean_within_3pct"] and row["k_within_0.03"]:
                    break
            if trials and trials[-1]["mean_within_3pct"] and trials[-1]["k_within_0.03"]:
                break
        best = min(trials, key=lambda t: (abs(t["early_R"] / B2_MEAN - 1), abs(t["k_ml"] - B2_K)))
        label = f"B/final36_{world}"
        dirs = run_fixed(label, r13.make_for(world, r14.pfmt(best["param"])), r13.job_for(world), best["coefficient"], seeds(89001, 36), 4)
        measured = measure_b(dirs)
        out = {
            "world": world, "trials": trials, "chosen": best, "final36": measured, "prefix": label,
            "mean_within_3pct": abs(measured["R"] / B2_MEAN - 1) <= TOL,
            "n_trials": len(trials),
        }
        save(STATE / f"b2_final_{world}.json", out)
        print(f"R16 B {world} final36: R={measured['R']:.3f} k_ml={measured['k_ml']:.3f} trials={len(trials)} within3={out['mean_within_3pct']}", flush=True)


def run_g():
    """Movement-only, two weeks, seeds 77001-77012, tilt 0, 0.5 and 1. No infection kernel."""
    flags = {
        "t0": r8.MOVEMENT["f3_t0"],
        "t0.5": r8.MOVEMENT["f3_t0.5"],
        "t1": r8.MOVEMENT["f3_t1"],
    }
    # Also the single seed that produced 50_r80_hours_by_type.csv.
    for tilt, extra in flags.items():
        batch = []
        for i, seed in enumerate(SEEDS_77, start=1):
            name = f"G/{tilt}/rep{i:02d}"
            log = RESULTS / name / "mobility.csv"
            args = r6.base_args(0.0, seed, 2, list(extra) + ["--mobilityLog", str(log), "--hviDump", str(RESULTS / name / "hvi.csv")])
            batch.append((name, args))
        r6.run_many(batch, {"agents": r6.AGENTS2, "locations": r6.LOCS1})
        print(f"R16 G tilt {tilt} done", flush=True)
    name = "G/t0_seed73001"
    log = RESULTS / name / "mobility.csv"
    args = r6.base_args(0.0, 73001, 2, list(flags["t0"]) + ["--mobilityLog", str(log), "--hviDump", str(RESULTS / name / "hvi.csv")])
    r6.run_many([(name, args)], {"agents": r6.AGENTS2, "locations": r6.LOCS1})
    for tilt in ("t0.5", "t1"):
        name = f"G/{tilt}_seed73001"
        log = RESULTS / name / "mobility.csv"
        args = r6.base_args(0.0, 73001, 2, list(flags[tilt]) + ["--mobilityLog", str(log), "--hviDump", str(RESULTS / name / "hvi.csv")])
        r6.run_many([(name, args)], {"agents": r6.AGENTS2, "locations": r6.LOCS1})
    print("R16 G seed 73001 done", flush=True)


COMMANDS = {"E": run_e, "A": run_a, "B": run_b, "G": run_g}


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "E" and len(sys.argv) > 2:
        run_e(sys.argv[2])
    elif cmd == "B" and len(sys.argv) > 2:
        run_b(sys.argv[2])
    else:
        COMMANDS[cmd]()
