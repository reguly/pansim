#!/usr/bin/env python3
"""Copies of locations1.json with `infectious` (L) multiplied by lambda on the high-L types 5, 6, 9, 10. The original is not touched."""
import json
from pathlib import Path

import run_round6 as r6

HIGH = (5, 6, 9, 10)
OUT = Path(__file__).resolve().parent / "inputs"


def build(lam):
    data = json.load(open(r6.LOCS1))
    n = 0
    for place in data["places"]:
        if place["type"] in HIGH:
            place["infectious"] = place["infectious"] * lam
            n += 1
    path = OUT / f"r8_locs_L{lam}.json"
    with open(path, "w") as handle:
        json.dump(data, handle)
    return path, n


if __name__ == "__main__":
    for lam in (3, 10, 30):
        print(*build(lam))
