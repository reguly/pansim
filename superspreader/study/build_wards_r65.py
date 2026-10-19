#!/usr/bin/env python3
"""R6-5: ward files at several target sizes. Same rule as build_wards.py (hospitals, health centres and
nursing homes, types 12, 14 and 22): a location is left whole at or below 4/3 of the target and split
into round(n / target) wards otherwise. Target 30 reproduces inputs/v25_wards."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_wards

ROOT = HERE.parents[1]
LOCS = ROOT / "inputRealExample" / "locations1.json"
AGENTS = ROOT / "inputRealExample" / "agents2.json"

for target in [int(v) for v in sys.argv[1:]]:
    out = HERE / "inputs" / f"r65_w{target}"
    if (out / "locations_wards.json").exists():
        print("exists", out)
        continue
    build_wards.TARGET = target
    build_wards.MAX_WHOLE = int(round(target * 4 / 3))
    build_wards.main(LOCS, AGENTS, out)
