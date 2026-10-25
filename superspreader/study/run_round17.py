#!/usr/bin/env python3
"""Note 85 round 17.

  PANSIM_BIN=/tmp/r17p/build_study/panSim PANSIM_JOBS=2 \\
      python3 superspreader/study/run_round17.py E
"""
import csv
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ.setdefault("PANSIM_BIN", "/tmp/r17p/build_study/panSim")
os.environ.setdefault("PANSIM_JOBS", "2")
sys.path.insert(0, str(HERE))

import run_round15 as r15  # noqa: E402
import run_round16 as r16  # noqa: E402
import run_round6 as r6  # noqa: E402
import run_x21  # noqa: E402

RESULTS = HERE / "results" / "round17"
STATE = RESULTS / "state"
for mod in (r16, r6, run_x21):
    mod.RESULTS = RESULTS
r6.STATE = STATE
r16.RESULTS = RESULTS
r16.STATE = STATE


def run_e(only=None):
    """Five cells. Histogram differences are recorded and do not stop the cell."""
    STATE.mkdir(parents=True, exist_ok=True)
    summary = []
    for cell in r16.e_cells():
        if only and cell["name"] != only and cell["world"] != only:
            continue
        name = cell["name"]
        prefix = f"E/{name}"
        make = r16.make_e(cell["world"], cell["alpha"])
        job = r15.job_for(cell["world"])
        batch = []
        for i, seed in enumerate(r16.SEEDS_77, start=1):
            run_name = f"{prefix}/rep{i:02d}"
            batch.append((run_name, make(cell["k"], seed, 4, RESULTS / run_name)))
        print(f"R17 E {name} k={cell['k']:.8g} seeds 77001-77012", flush=True)
        r6.run_many(batch, job)
        reference = r16.ref_hists(cell["ref_arm"])
        diffs = {}
        for i in range(1, 13):
            got = r16.offspring_hist(RESULTS / prefix / f"rep{i:02d}" / "trace.tsv")
            diff = r16.hist_diff(got, reference.get(i, {}))
            if diff:
                diffs[str(i)] = {str(k): {"got": a, "ref": b} for k, (a, b) in diff.items()}
        state = {
            "cell": name,
            "world": cell["world"],
            "alpha": cell["alpha"],
            "k": cell["k"],
            "ref_arm": cell["ref_arm"],
            "seeds": r16.SEEDS_77,
            "weeks": 4,
            "prefix": prefix,
            "histogram_equal": not diffs,
            "reps_differing": len(diffs),
            "stopped": False,
        }
        r16.save(STATE / f"e_{name}.json", state)
        summary.append({"cell": name, "histogram_equal": not diffs, "reps_differing": len(diffs)})
        print(f"R17 E {name}: histogram_equal={not diffs} reps_differing={len(diffs)}", flush=True)
    r16.save(STATE / "e_summary.json", summary)
    return summary


B2_RATE0 = 0.08435
B2_COEFF0 = 9.046322228651145e-05
B2_MEAN = 0.88
B2_K = 0.27
PROBE = 0.12


def make_w3b(rate):
    def make(k, seed, weeks, run_dir):
        extra = [
            "--eventRate", f"{rate:.8g}",
            "--eventFactor", "3000",
            "--eventTypes", "5,8",
            "--eventGroupSize", "30",
            "--eventDurationHours", "2",
            "--eventGroupLog", str(Path(run_dir) / "events.tsv"),
            "--hviDump", str(Path(run_dir) / "hvi.csv"),
        ]
        return r6.base_args(k, seed, weeks, extra, alpha=1.0)
    return make


def both_ok(row):
    return abs(row["R"] / B2_MEAN - 1.0) <= 0.03 and abs(row["k_ml"] - B2_K) <= 0.03


def rank_key(row):
    return (abs(row["R"] / B2_MEAN - 1.0), abs(row["k_ml"] - B2_K))


def clamp_step(dx):
    return tuple(max(-0.35, min(0.35, v)) for v in dx)


def newton_step(jacobian, residual):
    a, b = jacobian[0]
    c, d = jacobian[1]
    det = a * d - b * c
    if abs(det) < 1e-8:
        return None
    y0, y1 = residual
    return clamp_step(((-y0 * d + y1 * b) / det, (a * -y1 + c * y0) / det))


def broyden(jacobian, dx, dy):
    denom = dx[0] * dx[0] + dx[1] * dx[1]
    if denom < 1e-12:
        return jacobian
    err0 = dy[0] - (jacobian[0][0] * dx[0] + jacobian[0][1] * dx[1])
    err1 = dy[1] - (jacobian[1][0] * dx[0] + jacobian[1][1] * dx[1])
    return [
        [jacobian[0][0] + err0 * dx[0] / denom, jacobian[0][1] + err0 * dx[1] / denom],
        [jacobian[1][0] + err1 * dx[0] / denom, jacobian[1][1] + err1 * dx[1] / denom],
    ]


def run_b2():
    """Joint secant of world 3b event rate and coefficient. At most nine 12-seed trials, then one 36-seed run."""
    import math
    STATE.mkdir(parents=True, exist_ok=True)
    job = r15.job_for("w3b")
    seeds12 = list(range(89001, 89013))
    log_path = STATE / "b2_trials.json"
    trials = json.loads(log_path.read_text()) if log_path.exists() else []

    def one_trial(rate, coeff, phase, iteration):
        label = f"B2/{phase}_i{iteration}"
        dirs = []
        batch = []
        for i, seed in enumerate(seeds12, start=1):
            name = f"{label}/rep{i:02d}"
            batch.append((name, make_w3b(rate)(coeff, seed, 4, RESULTS / name)))
        r6.run_many(batch, job)
        dirs = [RESULTS / n for n, _ in batch]
        measured = r16.measure_b(dirs)
        row = {
            "phase": phase,
            "iteration": iteration,
            "rate": rate,
            "coefficient": coeff,
            **measured,
        }
        trials.append(row)
        r16.save(log_path, trials)
        print(
            f"R17 B2 {phase} {iteration}: rate={rate:.6g} c={coeff:.6g} R={measured['R']:.4f} k={measured['k_ml']:.4f}",
            flush=True,
        )
        return row

    if not trials:
        one_trial(B2_RATE0, B2_COEFF0, "probe", 1)
    if len(trials) < 2 and not both_ok(trials[-1]):
        one_trial(B2_RATE0 * math.exp(PROBE), B2_COEFF0, "probe", 2)
    if len(trials) < 3 and not both_ok(trials[-1]):
        one_trial(B2_RATE0, B2_COEFF0 * math.exp(PROBE), "probe", 3)

    jacobian = None
    if len(trials) >= 3:
        y1 = (trials[0]["R"], trials[0]["k_ml"])
        y2 = (trials[1]["R"], trials[1]["k_ml"])
        y3 = (trials[2]["R"], trials[2]["k_ml"])
        jacobian = [
            [(y2[0] - y1[0]) / PROBE, (y3[0] - y1[0]) / PROBE],
            [(y2[1] - y1[1]) / PROBE, (y3[1] - y1[1]) / PROBE],
        ]

    while len(trials) < 9 and not both_ok(trials[-1]) and jacobian is not None:
        best = min(trials, key=rank_key)
        step = newton_step(jacobian, (best["R"] - B2_MEAN, best["k_ml"] - B2_K))
        if step is None:
            print("R17 B2: Jacobian is singular; stopping the 12-seed loop", flush=True)
            break
        rate = max(0.01, min(0.5, best["rate"] * math.exp(step[0])))
        coeff = max(1e-5, min(5e-4, best["coefficient"] * math.exp(step[1])))
        before = (best["R"], best["k_ml"])
        row = one_trial(rate, coeff, "secant", len(trials) - 2)
        dx = (math.log(row["rate"] / best["rate"]), math.log(row["coefficient"] / best["coefficient"]))
        dy = (row["R"] - before[0], row["k_ml"] - before[1])
        jacobian = broyden(jacobian, dx, dy)

    best = min(trials, key=rank_key)
    final_label = "B2/final36"
    seeds36 = list(range(89001, 89037))
    batch = []
    for i, seed in enumerate(seeds36, start=1):
        name = f"{final_label}/rep{i:02d}"
        if i <= 12 and abs(best["rate"] - trials[0]["rate"]) < 1e-15:
            pass
        batch.append((name, make_w3b(best["rate"])(best["coefficient"], seed, 4, RESULTS / name)))
    # Reuse a 12-seed trial only when its rate and coefficient are the chosen ones.
    reuse = None
    for row in trials:
        if abs(row["rate"] - best["rate"]) / best["rate"] < 1e-8 and abs(row["coefficient"] - best["coefficient"]) / best["coefficient"] < 1e-8:
            reuse = row
    if reuse is not None:
        batch = batch[12:]
        print(f"R17 B2 reusing 12-seed trial {reuse['phase']} {reuse['iteration']} for the first 12 of 36", flush=True)
    if batch:
        r6.run_many(batch, job)
    final_dirs = []
    for i in range(1, 37):
        if i <= 12 and reuse is not None:
            final_dirs.append(RESULTS / f"B2/{reuse['phase']}_i{reuse['iteration']}/rep{i:02d}")
        else:
            final_dirs.append(RESULTS / f"{final_label}/rep{i:02d}")
    final = r16.measure_b(final_dirs)
    payload = {"best_trial": best, "final36": final, "n_trials": len(trials), "dirs": [str(p) for p in final_dirs]}
    r16.save(STATE / "b2_final.json", payload)
    print(f"R17 B2 final36 R={final['R']:.4f} k={final['k_ml']:.4f} trials={len(trials)}", flush=True)


BEFORE_BIN = Path("/tmp/r17p/panSim_o3_head")
AFTER_BIN = Path("/tmp/r17p/build_cafter/panSim")
STUDY_BIN = Path("/tmp/r17p/build_study/panSim")
C_ARMS = ("s8_3_L10", "s8_3_L30", "s8_2_t1_L30")
C_K0 = {
    "s8_3_L10": 0.00011523609118850581,
    "s8_3_L30": 4.121534745293414e-05,
    "s8_2_t1_L30": 4.3690747244199036e-05,
}
# Round-8 scaleAll parameters. S8-3 at venue risk 30 had no stored search; it starts from the S8-3 risk-10 value.
C_SCALE0 = {"s8_3_L10": 0.32631776960025943, "s8_3_L30": 0.32631776960025943, "s8_2_t1_L30": 0.9162650560468669}
C_WEEKS = 12
PS1_K = {"A0": 0.00041, "E": 0.000483661, "P0": 0.000483661}
PS1_FLAGS = {
    "A0": [],
    "E": ["--sheddingShape", "0.3"],
    "P0": ["--traitShape", "0.3", "--traitPersist", "1", "--traitSusceptibilityExp", "0"],
}
W1_B1_K = 0.0005151697600710852


def use_binary(path):
    run_x21.BINARY = Path(path)
    print(f"R17 binary {run_x21.BINARY}", flush=True)


def bind_results():
    for mod in (r16, r6, run_x21):
        mod.RESULTS = RESULTS
    r6.STATE = STATE
    r16.STATE = STATE


def control_flags(arm_flags, mode, scale=None):
    flags = list(arm_flags)
    if mode == "capTop":
        flags += ["--hviControlDay", "21", "--hviControlMode", "capTop", "--hviControlParam", "0.05"]
    elif mode == "scaleAll":
        flags += ["--hviControlDay", "21", "--hviControlMode", "scaleAll", "--hviControlParam", f"{scale:.4f}"]
    return flags


def mobility_totals(path):
    disc = high = 0.0
    with open(path) as handle:
        for row in csv.DictReader(handle):
            disc += float(row["h_wd_role_disc"]) + float(row["h_we_role_disc"])
            high += float(row["hpt_5"]) + float(row["hpt_6"]) + float(row["hpt_9"]) + float(row["hpt_10"])
    return disc, high


def run_mixed(items):
    """Run (name, args, job) together. Jobs may use different location files. Two processes at a time."""
    def one(item):
        name, args, job = item
        return run_x21.run_job(name, args, **job)
    if r6.JOBS <= 1:
        codes = [one(item) for item in items]
    else:
        with ThreadPoolExecutor(max_workers=r6.JOBS) as pool:
            codes = list(pool.map(one, items))
    if any(codes):
        raise SystemExit(f"a job failed: {codes}")


def control_item(which, arm, mode, k, arm_flags, job, closures=None, scale=None, reps=12, mobility_reps=(1,)):
    """12-week infection runs. Seed 77001 (rep 01) also writes the mobility log used for hours."""
    import run_round8 as r8
    items = []
    for i, seed in enumerate(r8.seeds8(reps), start=1):
        name = f"C/{which}/{arm}/{mode}/rep{i:02d}"
        flags = control_flags(arm_flags, mode, scale)
        flags += ["--hviDump", str(RESULTS / name / "hvi.csv")]
        if i in mobility_reps:
            flags += ["--mobilityLog", str(RESULTS / name / "mobility.csv")]
        args = r6.base_args(k, seed, C_WEEKS, flags)
        if closures is not None:
            args[args.index("--closures") + 1] = str(closures)
        items.append((name, args, job))
    return items


def _scale_step(spec, s_run, removed):
    trials = spec["trials"]
    if len(trials) >= 1 and removed != trials[-1]["disc_removed"]:
        prev = trials[-1]
        span = removed - prev["disc_removed"]
        s = s_run + (spec["target"] - removed) * (s_run - prev["scale"]) / span
    elif removed < spec["target"]:
        s = s_run * 0.7
    else:
        s = s_run + 0.5 * (1.0 - s_run)
    return min(1.0, max(0.0, s))


def _close_scale(which, spec, matched):
    trials = spec["trials"]
    best = min(trials, key=lambda row: abs(row["disc_removed"] - spec["target"]))
    chosen = best["scale"]
    if matched:
        chosen = trials[-1]["scale"]
    stored = {"done": True, "scale": chosen, "matched": matched, "trials": trials, "target_removed": spec["target"]}
    r16.save(STATE / f"c_scale_{which}_{spec['arm']}.json", stored)
    print(f"R17 C scale {which} {spec['arm']} s={chosen:.4f} matched={matched}", flush=True)
    return stored


def fit_scales(which, specs):
    """Up to five 12-week infection trials per arm, on seed 77001, run two arms at a time."""
    import run_round8 as r8
    bind_results()
    results = {}
    active = []
    for spec in specs:
        log_path = STATE / f"c_scale_{which}_{spec['arm']}.json"
        if log_path.exists():
            stored = json.loads(log_path.read_text())
            if stored.get("done"):
                print(f"R17 C scale {which} {spec['arm']} cached s={stored['scale']:.4f}", flush=True)
                results[spec["arm"]] = stored
                continue
            spec["trials"] = stored.get("trials", [])
            spec["s"] = spec["trials"][-1]["next_s"] if spec["trials"] else C_SCALE0[spec["arm"]]
        else:
            spec["trials"] = []
            spec["s"] = C_SCALE0[spec["arm"]]
        active.append(spec)
    seed = r8.seeds8(1)[0]
    while active:
        items = []
        planned = []
        finished = []
        for spec in active:
            if len(spec["trials"]) >= 5:
                finished.append(spec)
                continue
            s_run = min(1.0, max(0.0, float(f"{spec['s']:.4f}")))
            name = f"C/{which}/{spec['arm']}/scale_search/i{len(spec['trials']) + 1:02d}"
            flags = control_flags(spec["flags"], "scaleAll", s_run)
            flags += ["--hviDump", str(RESULTS / name / "hvi.csv"), "--mobilityLog", str(RESULTS / name / "mobility.csv")]
            items.append((name, r6.base_args(spec["k"], seed, C_WEEKS, flags), spec["job"]))
            planned.append((spec, s_run, name))
        for spec in finished:
            results[spec["arm"]] = _close_scale(which, spec, False)
        active = [spec for spec in active if spec not in finished]
        if not items:
            break
        run_mixed(items)
        still = []
        for spec, s_run, name in planned:
            disc, high = mobility_totals(RESULTS / name / "mobility.csv")
            removed = spec["base_disc"] - disc
            row = {"iteration": len(spec["trials"]) + 1, "scale": s_run, "disc_hours": disc, "high_hours": high, "disc_removed": removed}
            hit = spec["target"] > 0 and abs(removed - spec["target"]) <= 0.03 * spec["target"]
            if hit:
                row["accepted"] = True
                spec["trials"].append(row)
                results[spec["arm"]] = _close_scale(which, spec, True)
                continue
            nxt = _scale_step(spec, s_run, removed)
            row["next_s"] = nxt
            row["accepted"] = False
            spec["trials"].append(row)
            spec["s"] = nxt
            r16.save(STATE / f"c_scale_{which}_{spec['arm']}.json", {"done": False, "trials": spec["trials"], "target_removed": spec["target"]})
            print(f"R17 C scale {which} {spec['arm']} trial {row['iteration']} s={s_run:.4f} removed={removed:.4g} next={nxt:.4f}", flush=True)
            if abs(nxt - s_run) < 5e-5 or len(spec["trials"]) >= 5:
                results[spec["arm"]] = _close_scale(which, spec, False)
            else:
                still.append(spec)
        active = still
    return results


def run_c():
    """S8-3 at venue risk 10 and 30, and S8-2 tilt 1 at venue risk 30, before and after the scene repair."""
    import run_round8 as r8
    bind_results()
    if not BEFORE_BIN.exists() or not AFTER_BIN.exists():
        raise SystemExit(f"missing C binary: before={BEFORE_BIN.exists()} after={AFTER_BIN.exists()}")
    STATE.mkdir(parents=True, exist_ok=True)
    close_dir = RESULTS / "inputs"
    close_dir.mkdir(parents=True, exist_ok=True)
    for which, binary in (("before", BEFORE_BIN), ("after", AFTER_BIN)):
        use_binary(binary)
        calibrated = {}
        for arm in C_ARMS:
            label = f"c_{which}_{arm}"
            make_flags = r8.ARMS[arm]["flags"]

            def make(k, seed, weeks, run_dir, make_flags=make_flags):
                return r6.base_args(k, seed, weeks, list(make_flags) + ["--hviDump", str(Path(run_dir) / "hvi.csv")])

            stored = r6.match(label, make, C_K0[arm], r8.seeds8(12), 4, 6211.25, r8.job_of(arm), max_rounds=5)
            calibrated[arm] = stored
            print(f"R17 C {which} {arm} k={stored['k']:.6g} day28={stored['day28']:.1f} matched={stored['matched']}", flush=True)
        items = []
        specs = []
        for arm in C_ARMS:
            k = calibrated[arm]["k"]
            flags = r8.ARMS[arm]["flags"]
            job = r8.job_of(arm)
            close = close_dir / f"close_{arm}.json"
            r8.write_close((5, 6, 9, 10), close)
            items += control_item(which, arm, "none", k, flags, job)
            items += control_item(which, arm, "capTop", k, flags, job)
            items += control_item(which, arm, "close", k, flags, job, closures=close)
            specs.append({"arm": arm, "k": k, "flags": flags, "job": job, "matched": calibrated[arm]["matched"], "day28": calibrated[arm]["day28"]})
        run_mixed(items)
        for spec in specs:
            base_disc, _ = mobility_totals(RESULTS / f"C/{which}/{spec['arm']}/none/rep01/mobility.csv")
            cap_disc, _ = mobility_totals(RESULTS / f"C/{which}/{spec['arm']}/capTop/rep01/mobility.csv")
            spec["base_disc"] = base_disc
            spec["target"] = base_disc - cap_disc
        fits = fit_scales(which, specs)
        scale_items = []
        for spec in specs:
            scale_items += control_item(which, spec["arm"], "scaleAll", spec["k"], spec["flags"], spec["job"], scale=fits[spec["arm"]]["scale"])
        run_mixed(scale_items)
        for spec in specs:
            r16.save(STATE / f"c_{which}_{spec['arm']}_runs.json", {
                "k": spec["k"], "matched": spec["matched"], "day28": spec["day28"],
                "scale": fits[spec["arm"]]["scale"], "binary": str(binary),
            })


def run_d():
    """16-week PS1 arms on the original map, and world-1 B1 on the enlarged map, with the episode trace."""
    from run_study import ROOT
    bind_results()
    if not STUDY_BIN.exists():
        raise SystemExit(f"missing study binary {STUDY_BIN}")
    use_binary(STUDY_BIN)
    original = {"agents": ROOT / "inputRealExample" / "agents1.json", "locations": ROOT / "inputRealExample" / "locations0.json"}
    enlarged = {"agents": r6.AGENTS2, "locations": r6.LOCS1}
    batch = []
    for arm, k in PS1_K.items():
        for i, seed in enumerate(range(1101, 1113), start=1):
            name = f"D/ps1_{arm}/rep{i:02d}"
            extra = list(PS1_FLAGS[arm]) + ["--episodeTrace", str(RESULTS / name / "episodes.tsv")]
            batch.append((name, r6.base_args(k, seed, 16, extra)))
    print("R17 D original-map PS1 A0 E P0, 16 weeks, seeds 1101-1112", flush=True)
    r6.run_many(batch, original)
    batch = []
    for i, seed in enumerate(range(77001, 77013), start=1):
        name = f"D/w1_b1/rep{i:02d}"
        extra = ["--episodeTrace", str(RESULTS / name / "episodes.tsv")]
        batch.append((name, r6.base_args(W1_B1_K, seed, 16, extra)))
    print("R17 D enlarged world-1 B1, 16 weeks, seeds 77001-77012", flush=True)
    r6.run_many(batch, enlarged)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "E"
    only = sys.argv[2] if len(sys.argv) > 2 else None
    if cmd == "E":
        run_e(only)
    elif cmd == "B2":
        run_b2()
    elif cmd == "C":
        run_c()
    elif cmd == "D":
        run_d()
    else:
        raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
