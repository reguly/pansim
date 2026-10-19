#!/usr/bin/env python3
"""Note 52 round 9: a venue scene combined with a per-episode shedding multiplier. Uses the build_r9 binary (PANSIM_BIN).

  PANSIM_BIN=build_r9/panSim python3 superspreader/study/run_round9.py column refs ...
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_round8 as r8  # noqa: E402
import run_round6 as r6  # noqa: E402
import run_x21  # noqa: E402

RESULTS = HERE / "results" / "round9"
STATE = RESULTS / "state"
run_x21.RESULTS = RESULTS
r6.RESULTS = RESULTS
r6.STATE = STATE
SCENES = {"s8_1_L10": "s8_1_L10", "t0.5_L10": "s8_2_t0.5_L10", "t1_L10": "s8_2_t1_L10", "t1_L30": "s8_2_t1_L30"}
SHAPES = (3, 2, 1)
ARMS = {}
for sname, base in SCENES.items():
    for shape in SHAPES:
        ARMS[f"s9_{sname}_sh{shape}"] = {"flags": r8.ARMS[base]["flags"] + ["--sheddingShape", str(shape)], "lam": r8.ARMS[base]["lam"], "scene": base}
for shape in SHAPES:
    ARMS[f"s9_ref_sh{shape}"] = {"flags": ["--sheddingShape", str(shape)], "lam": 1, "scene": None}


def k0_of(label):
    scene = ARMS[label]["scene"]
    if scene is None:
        return 0.00041
    return json.loads((r8.STATE / f"r8_{scene}.json").read_text())["k"]


def run_arm9(label, reps=12, pilot=4):
    seeds = r8.seeds8(reps)
    spec = ARMS[label]
    job = {"agents": r6.AGENTS2, "locations": r8.locs_for(spec["lam"])}
    flags = spec["flags"]

    def make(k, seed, weeks, run_dir):
        return r6.base_args(k, seed, weeks, flags + ["--hviDump", str(Path(run_dir) / "hvi.csv")])
    return r6.match(f"r9_{label}", make, k0_of(label), seeds, 4, r8.TARGET, job, pilot=pilot)


def run_arms(labels):
    for label in labels:
        stored = run_arm9(label)
        print(f"S9 {label} k={stored['k']:.6g} day28={stored['day28']:.1f} matched={stored['matched']}", flush=True)


def column():
    run_arms([f"s9_t1_L10_sh{s}" for s in SHAPES])


def refs():
    run_arms([f"s9_ref_sh{s}" for s in SHAPES])


def rest():
    run_arms([f"s9_{n}_sh{s}" for n in ("s8_1_L10", "t0.5_L10", "t1_L30") for s in SHAPES])


TASKS = {"column": column, "refs": refs, "rest": rest}

if __name__ == "__main__":
    for name in sys.argv[1:]:
        TASKS[name]()
