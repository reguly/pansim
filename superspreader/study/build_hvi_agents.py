#!/usr/bin/env python3
"""S3 repertoire lever: a new agents file in which the high-velocity class has an enlarged venue list.

  python3 build_hvi_agents.py HVI_DUMP.csv FACTOR OUT.json

HVI_DUMP.csv comes from a run with the fixed --hviSeed (columns agent,type,age,m,class,rotate). For every class
member and each discretionary venue type (5, 6, 7, 8, 9, 10), the list becomes the N nearest venues of that type to
the agent's home (by the coordinates in locations1.json), N = FACTOR times the agent's original count. The original
venues are kept; venues are added, none removed. Home, school, work and other types are unchanged.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
TYPES = (5, 6, 7, 8, 9, 10)


def main(dump, factor, out):
    factor = float(factor)
    locs = json.load(open(ROOT / "inputRealExample" / "locations1.json"))["places"]
    coord = {}
    by_type = {t: [] for t in TYPES}
    for p in locs:
        coord[p["ID"]] = p["coordinates"]
        if p["type"] in by_type:
            by_type[p["type"]].append(p["ID"])
    xy = {t: np.asarray([coord[i] for i in ids], dtype=float) for t, ids in by_type.items()}
    members = set()
    with open(dump) as handle:
        for r in csv.DictReader(handle):
            if int(r["class"]) == 1:
                members.add(int(r["agent"]))
    data = json.load(open(ROOT / "inputRealExample" / "agents2.json"))
    people = data["people"]
    added = {t: 0 for t in TYPES}
    for idx in members:
        person = people[idx]
        home = next((l["locID"] for l in person["locations"] if l["typeID"] == 2), None)
        if home is None or home not in coord:
            continue
        h = np.asarray(coord[home], dtype=float)
        for t in TYPES:
            have = [l["locID"] for l in person["locations"] if l["typeID"] == t]
            if not have:
                continue
            want = int(round(len(have) * factor))
            if want <= len(have):
                continue
            dist = np.hypot(*(xy[t] - h).T)
            order = np.argsort(dist)
            keep = set(have)
            for j in order:
                vid = by_type[t][int(j)]
                if vid in keep:
                    continue
                person["locations"].append({"typeID": t, "locID": vid})
                keep.add(vid)
                added[t] += 1
                if len(keep) >= want:
                    break
    Path(out).write_text(json.dumps(data, separators=(",", ":")))
    print("class members", len(members), "venues added", added)


if __name__ == "__main__":
    main(*sys.argv[1:4])
