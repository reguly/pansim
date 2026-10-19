#!/usr/bin/env python3
"""T1 of round 8: a 12-week run with every new option off, for the binary named by PANSIM_BIN. Usage: t1_round8.py <name>"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import run_round8 as r8  # noqa: E402
import run_round6 as r6  # noqa: E402
import run_x21  # noqa: E402

name = sys.argv[1]
args = r6.base_args(0.00041, 77777, 12, [])
raise SystemExit(run_x21.run_job(f"t1/{name}", args, agents=r6.AGENTS2, locations=r6.LOCS1))
