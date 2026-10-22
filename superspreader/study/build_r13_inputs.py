#!/usr/bin/env python3
"""Round 13 N5: one more realisation of the per-agent venue lists (restaurants 5, long shops 8, churches 9, parks 10).

A copy of agents2.json (the original is not touched) in which, separately for each of the four types, the venue ids of
the slots are shuffled among agents whose homes lie in the same 2 km grid cell (EOV coordinates read from the home id;
agents whose home id carries no coordinates form one extra cell). Every venue keeps its count in every cell, hence also
its total quota; agents keep their number of slots per type; a second pass swaps away repeated venues within an agent.

  python3 superspreader/study/build_r13_inputs.py
"""
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / "inputRealExample" / "agents2.json"
OUT = HERE / "inputs" / "r13_agents_venues_redrawn.json"
SEED = 20261022
TYPES = (5, 8, 9, 10)
CELL = 2000


def cell_of(person):
    for slot in person["locations"]:
        if slot["typeID"] == 2:
            m = re.match(r".*_(\d+)_(\d+)$", slot["locID"])
            if m:
                return (int(m[1]) // CELL, int(m[2]) // CELL)
    return (-1, -1)


def main():
    data = json.loads(SRC.read_text())
    people = data["people"]
    cells = [cell_of(p) for p in people]
    rng = random.Random(SEED)
    report = {"seed": SEED, "cell_size_m": CELL, "types": {}}
    for t in TYPES:
        slots = defaultdict(list)  # cell -> [(person, slot)]
        for i, p in enumerate(people):
            for j, s in enumerate(p["locations"]):
                if s["typeID"] == t:
                    slots[cells[i]].append((i, j))
        before = Counter(s["locID"] for p in people for s in p["locations"] if s["typeID"] == t)
        moved = swaps = 0
        for cell, pos in slots.items():
            ids = [people[i]["locations"][j]["locID"] for i, j in pos]
            old = list(ids)
            rng.shuffle(ids)
            owner = defaultdict(list)
            for k, (i, _j) in enumerate(pos):
                owner[i].append(k)
            for _pass in range(12):
                dirty = []
                for i, ks in owner.items():
                    seen = set()
                    for k in ks:
                        if ids[k] in seen:
                            dirty.append(k)
                        seen.add(ids[k])
                if not dirty:
                    break
                for k in dirty:
                    i = pos[k][0]
                    own = {ids[x] for x in owner[i]}
                    for _ in range(2000):
                        o = rng.randrange(len(ids))
                        oi = pos[o][0]
                        if oi == i or ids[o] in own or ids[k] in {ids[x] for x in owner[oi]}:
                            continue
                        ids[k], ids[o] = ids[o], ids[k]
                        swaps += 1
                        break
            for k, (i, j) in enumerate(pos):
                people[i]["locations"][j]["locID"] = ids[k]
            moved += sum(1 for a, b in zip(old, ids) if a != b)
        after = Counter(s["locID"] for p in people for s in p["locations"] if s["typeID"] == t)
        dup = sum(1 for p in people if len([s["locID"] for s in p["locations"] if s["typeID"] == t])
                  != len({s["locID"] for s in p["locations"] if s["typeID"] == t}))
        report["types"][str(t)] = {"slots": sum(len(v) for v in slots.values()), "slots_changed": moved, "repair_swaps": swaps,
                                    "counts_equal": before == after, "agents_with_repeated_venue_after": dup,
                                    "agents_with_repeated_venue_before": 0}
        print(t, report["types"][str(t)], flush=True)
        if before != after:
            raise SystemExit("venue counts changed")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, separators=(",", ":")))
    (HERE / "inputs" / "r13_agents_venues_redrawn.json.report.json").write_text(json.dumps(report, indent=1) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
