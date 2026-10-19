#!/usr/bin/env python3
"""Note 61 round 12: run world 3b (closed-group events M=30, rate=0.1456, factor=3000)
on the common seeds 77001..77012 and log full event details for R12-1 and R12-2.

  PANSIM_BIN=build_r10/panSim python3 superspreader/study/run_round12.py w3b
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ.setdefault("PANSIM_BIN", str(HERE.parent.parent / "build_r10" / "panSim"))
sys.path.insert(0, str(HERE))

import run_round6 as r6  # noqa: E402
import run_round8 as r8  # noqa: E402
import run_x21  # noqa: E402

RESULTS = HERE / "results" / "round12"
STATE = RESULTS / "state"
run_x21.RESULTS = RESULTS
r6.RESULTS = RESULTS
r6.STATE = STATE
TARGET = 6211.25
SEEDS = r8.seeds8(12)

# Starting baseline k from the Round-6 matched r67_M30 arm (0.0001422)
K0_W3B = 0.0001422


def job(locations=None):
    return {"agents": r6.AGENTS2, "locations": locations or r6.LOCS1}


def w3b():
    label = "w3b_M30_rate0.1456"
    flags = [
        "--eventRate", "0.1456",
        "--eventFactor", "3000",
        "--eventTypes", "5,8",
        "--eventGroupSize", "30",
        "--eventDurationHours", "2",
    ]

    def make(k, seed, w, run_dir):
        extra = list(flags) + [
            "--eventGroupLog", str(Path(run_dir) / "events.tsv"),
            "--hviDump", str(Path(run_dir) / "hvi.csv"),
        ]
        return r6.base_args(k, seed, w, extra)

    stored = r6.match(f"r12_{label}", make, K0_W3B, SEEDS, 4, TARGET, job(), pilot=4)
    print(f"R12 {label} k={stored['k']:.6g} day28={stored['day28']:.1f} matched={stored['matched']}", flush=True)
    return stored


TASKS = {"w3b": w3b}

if __name__ == "__main__":
    TASKS[sys.argv[1] if len(sys.argv) > 1 else "w3b"]()
