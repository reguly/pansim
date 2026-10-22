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


def world_flags(world, run_dir=None):
    """Extra command-line flags and locations file of a world, as in rounds 10 to 12."""
    dump = [] if run_dir is None else ["--hviDump", str(Path(run_dir) / "hvi.csv")]
    if world == "w1":
        return ["--sheddingShape", "0.32"], r6.LOCS1, False
    if world == "w2a":
        return r8.ARMS["s8_2_t1_L30"]["flags"] + ["--sheddingShape", "0.70"], r8.locs_for(30), True
    if world == "w2b":
        return r8.ARMS["s8_2_t1_L10"]["flags"] + ["--sheddingShape", "0.58"], r8.locs_for(10), True
    if world == "w3b":
        return ["--eventRate", "0.1456", "--eventFactor", "3000", "--eventTypes", "5,8",
                "--eventGroupSize", "30", "--eventDurationHours", "2"], r6.LOCS1, True
    raise KeyError(world)


def make_for(world):
    flags, _locs, dump = world_flags(world)

    def make(k, seed, w, run_dir):
        extra = list(flags)
        if world == "w3b":
            extra += ["--eventGroupLog", str(Path(run_dir) / "events.tsv")]
        if dump:
            extra += ["--hviDump", str(Path(run_dir) / "hvi.csv")]
        return r6.base_args(k, seed, w, extra)
    return make


def job_for(world):
    _flags, locs, _dump = world_flags(world)
    return {"agents": r6.AGENTS2, "locations": locs}


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


TASKS = {"cal": lambda: cal(sys.argv[2], sys.argv[3]), "frozen": lambda: frozen(sys.argv[2], sys.argv[3]),
         "sens": lambda: sens(sys.argv[2], sys.argv[3])}

if __name__ == "__main__":
    TASKS[sys.argv[1]]()
