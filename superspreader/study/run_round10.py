#!/usr/bin/env python3
"""Note 55 round 10: same k in different worlds, plus the correlated multiplier, the household test and the upper bound.

  PANSIM_BIN=build_r10/panSim python3 superspreader/study/run_round10.py w1 r104 r102 r103 w3
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_round6 as r6  # noqa: E402
import run_round8 as r8  # noqa: E402
import run_x21  # noqa: E402

RESULTS = HERE / "results" / "round10"
STATE = RESULTS / "state"
run_x21.RESULTS = RESULTS
r6.RESULTS = RESULTS
r6.STATE = STATE
TARGET = 6211.25
SEEDS = r8.seeds8(12)          # the round-8 and round-9 seed set, for comparability
NOHOME = HERE / "inputs" / "r10_locs_nohome.json"
EVENT_TYPES = "5,8"


def job(locations=None):
    return {"agents": r6.AGENTS2, "locations": locations or r6.LOCS1}


def match_arm(label, flags, k0, locations=None, weeks=4, pilot=4, dump=False):
    def make(k, seed, w, run_dir):
        extra = list(flags)
        if dump:
            extra += ["--hviDump", str(Path(run_dir) / "hvi.csv")]
        return r6.base_args(k, seed, w, extra)
    stored = r6.match(f"r10_{label}", make, k0, SEEDS, weeks, TARGET, job(locations), pilot=pilot)
    print(f"R10 {label} k={stored['k']:.6g} day28={stored['day28']:.1f} matched={stored['matched']}", flush=True)
    return stored


# ---------------------------------------------------------------- R10-1 world 1: the multiplier alone

def w1(shapes=("0.32",)):
    for shape in shapes:
        match_arm(f"w1_sh{shape}", ["--sheddingShape", str(shape)], 0.00046)


def w1_more():
    """Extra shapes, chosen after the first one from the measured relation between shape and k."""
    w1(tuple(sys.argv[2:]) or ("0.32",))


# ---------------------------------------------------------------- R10-1 world 3: closed-group events

def w3(rates=("0.034",)):
    for rate in rates:
        flags = ["--eventRate", str(rate), "--eventFactor", "3000", "--eventTypes", EVENT_TYPES,
                 "--eventGroupSize", "30", "--eventDurationHours", "2"]
        match_arm(f"w3_rate{rate}", flags, 0.00032)


# ---------------------------------------------------------------- R10-2: the correlated multiplier

def r102():
    flags = r8.ARMS["s8_2_t1_L10"]["flags"] + ["--sheddingShape", "2", "--sheddingClassMean", "1.5", "--sheddingOthersMean", "0.974"]
    match_arm("r102_correlated", flags, 0.000117, locations=r8.locs_for(10), dump=True)


# ---------------------------------------------------------------- R10-3: the multiplier without households

def r103():
    match_arm("r103_nohome_sh1", ["--sheddingShape", "1"], 0.0011, locations=NOHOME)


def r103ctl():
    """Control: the same suppression with no multiplier, so the baseline dispersion of this world is known."""
    match_arm("r103_nohome_base", [], 0.0011, locations=NOHOME)


# ---------------------------------------------------------------- R10-4: upper bound

def r104():
    flags = r8.ARMS["s8_2_t1_L30"]["flags"] + ["--sheddingShape", "0.5"]
    match_arm("r104_upper", flags, 4.4e-05, locations=r8.locs_for(30), dump=True)


# ---------------------------------------------------------------- R10-1 item 4: repeat infections

def pairs():
    """Offspring correlation across repeated infections of the same agent: 16 weeks, 8 replicates, vaccination off."""
    import run_round8 as r8b
    worlds = {
        "w1": (json.loads((STATE / "r10_w1_sh0.32.json").read_text())["k"], ["--sheddingShape", "0.32"], None),
        "w2": (json.loads(((HERE / "results" / "round9" / "state") / "r9_s9_t1_L10_sh1.json").read_text())["k"],
               r8b.ARMS["s8_2_t1_L10"]["flags"] + ["--sheddingShape", "1"], r8b.locs_for(10)),
    }
    seeds = list(range(78001, 78009))
    for name, (k, flags, locs) in worlds.items():
        batch = []
        for rep, seed in enumerate(seeds, start=1):
            nm = f"r10/pairs_{name}/rep{rep:02d}"
            args = r6.base_args(k, seed, 16, flags + ["--immunizationStart", "100000",
                                                      "--episodeTrace", str(RESULTS / nm / "episodes.tsv")])
            batch.append((nm, args))
        r6.run_many(batch, job(locs))
        print(f"R10 pairs {name} done", flush=True)


TASKS = {"w1": lambda: w1(tuple(sys.argv[2:]) or ("0.32",)), "w3": lambda: w3(tuple(sys.argv[2:]) or ("0.034",)),
         "r102": r102, "r103": r103, "r103ctl": r103ctl, "r104": r104, "pairs": pairs}

if __name__ == "__main__":
    name = sys.argv[1]
    TASKS[name]()
