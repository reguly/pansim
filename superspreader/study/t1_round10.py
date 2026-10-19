#!/usr/bin/env python3
"""T1 of round 10: rerun round-9 replicates on build_r10 (new options off) and compare byte for byte with the stored round-9 output."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R9 = HERE / "results" / "round9"
OUT = HERE / "results" / "round10" / "t1"


def run(label, extra, tag):
    state = json.loads((R9 / "state" / f"r9_{label}.json").read_text())
    src = R9 / state["prefix"] / "rep01"
    cmd = json.loads((src / "command.json").read_text())
    cmd[0] = str(ROOT / "build_r10" / "panSim")
    out = OUT / f"{label}_{tag}"
    out.mkdir(parents=True, exist_ok=True)
    cmd[cmd.index("--infectionTrace") + 1] = str(out / "trace.tsv")
    if "--hviDump" in cmd:
        cmd[cmd.index("--hviDump") + 1] = str(out / "hvi.csv")
    cmd += extra
    with open(out / "stdout.txt", "w") as handle:
        subprocess.run(cmd, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, check=True)
    return src, out


def same(a, b):
    return a.read_bytes() == b.read_bytes()


def daily(path):
    return [l for l in path.read_text().splitlines() if "seconds" not in l]


for label in ("s9_t1_L10_sh1", "s9_ref_sh1", "s9_s8_1_L10_sh3"):
    src, out = run(label, [], "off")
    print(label, "trace identical", same(src / "trace.tsv", out / "trace.tsv"),
          "| daily identical", daily(src / "stdout.txt") == daily(out / "stdout.txt"), flush=True)
