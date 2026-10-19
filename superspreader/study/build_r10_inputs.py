#!/usr/bin/env python3
"""Copy of locations1.json with the infectiousness of the home type (2) set to 0, for R10-3. The original is not touched."""
import json
from pathlib import Path

import run_round6 as r6

OUT = Path(__file__).resolve().parent / "inputs"


def build():
    data = json.load(open(r6.LOCS1))
    n = 0
    for place in data["places"]:
        if place["type"] == 2:
            place["infectious"] = 0
            n += 1
    path = OUT / "r10_locs_nohome.json"
    with open(path, "w") as handle:
        json.dump(data, handle)
    return path, n


if __name__ == "__main__":
    print(*build())
