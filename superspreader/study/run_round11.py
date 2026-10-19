#!/usr/bin/env python3
"""Note 58 round 11: the worlds matched on the likelihood k (about 0.35), not on the moment k.

  PANSIM_BIN=build_r10/panSim python3 superspreader/study/run_round11.py w2a 0.70
  PANSIM_BIN=build_r10/panSim python3 superspreader/study/run_round11.py w2b 0.58
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_round6 as r6  # noqa: E402
import run_round8 as r8  # noqa: E402
import run_x21  # noqa: E402

RESULTS = HERE / "results" / "round11"
STATE = RESULTS / "state"
run_x21.RESULTS = RESULTS
r6.RESULTS = RESULTS
r6.STATE = STATE
TARGET = 6211.25
SEEDS = r8.seeds8(12)

# starting background coefficients, from the matched round-9 and round-10 arms of the same scene
K0 = {30: 4.35e-05, 10: 1.185e-04}


def job(locations=None):
    return {"agents": r6.AGENTS2, "locations": locations or r6.LOCS1}


def match_arm(label, flags, k0, locations=None, weeks=4, pilot=4, dump=True):
    def make(k, seed, w, run_dir):
        extra = list(flags)
        if dump:
            extra += ["--hviDump", str(Path(run_dir) / "hvi.csv")]
        return r6.base_args(k, seed, w, extra)
    stored = r6.match(f"r11_{label}", make, k0, SEEDS, weeks, TARGET, job(locations), pilot=pilot)
    print(f"R11 {label} k={stored['k']:.6g} day28={stored['day28']:.1f} matched={stored['matched']}", flush=True)
    return stored


def scene(lam, shape, tag=None):
    """S8-2 tau 1 at the given lambda, with the per-episode multiplier shape tuned."""
    flags = r8.ARMS[f"s8_2_t1_L{lam}"]["flags"] + ["--sheddingShape", str(shape)]
    return match_arm(tag or f"w2_L{lam}_sh{shape}", flags, K0[lam], locations=r8.locs_for(lam))


def w2a(shapes):
    for shape in shapes:
        scene(30, shape)


def w2b(shapes):
    for shape in shapes:
        scene(10, shape)


def pairs():
    """Repeat-infection correlation in world 2a: 16 weeks, 8 replicates, vaccination off."""
    label = sys.argv[2]
    k = json.loads((STATE / f"r11_{label}.json").read_text())["k"]
    flags = r8.ARMS["s8_2_t1_L30"]["flags"] + ["--sheddingShape", label.split("_sh")[1]]
    batch = []
    for rep, seed in enumerate(range(78001, 78009), start=1):
        nm = f"r11/pairs_{label}/rep{rep:02d}"
        args = r6.base_args(k, seed, 16, flags + ["--immunizationStart", "100000",
                                                  "--episodeTrace", str(RESULTS / nm / "episodes.tsv"),
                                                  "--hviDump", str(RESULTS / nm / "hvi.csv")])
        batch.append((nm, args))
    r6.run_many(batch, job(r8.locs_for(30)))
    print(f"R11 pairs {label} done", flush=True)


TASKS = {"w2a": lambda: w2a(sys.argv[2:] or ["0.70"]), "w2b": lambda: w2b(sys.argv[2:] or ["0.58"]), "pairs": pairs}

if __name__ == "__main__":
    TASKS[sys.argv[1]]()
