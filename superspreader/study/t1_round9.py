#!/usr/bin/env python3
"""T1 of round 9: rerun round-8 replicates on build_r9 (shedding off) and compare byte for byte; with shedding on compare the HVI dump."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
R8 = HERE / "results" / "round8"
OUT = HERE / "results" / "round9" / "t1"


def run(label, extra, tag):
    state = json.loads((R8 / "state" / f"r8_{label}.json").read_text())
    src = R8 / state["prefix"] / "rep01"
    cmd = json.loads((src / "command.json").read_text())
    cmd[0] = str(ROOT / "build_r9" / "panSim")
    out = OUT / f"{label}_{tag}"
    out.mkdir(parents=True, exist_ok=True)
    cmd[cmd.index("--infectionTrace") + 1] = str(out / "trace.tsv")
    cmd[cmd.index("--hviDump") + 1] = str(out / "hvi.csv")
    cmd += extra
    with open(out / "stdout.txt", "w") as handle:
        subprocess.run(cmd, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, check=True)
    return src, out


def same(a, b):
    return a.read_bytes() == b.read_bytes()


def daily(path):
    return [l for l in path.read_text().splitlines() if "seconds" not in l]


for label in ("s8_1_L10", "s8_2_t1_L10", "s8_3_L10"):
    src, out = run(label, [], "off")
    print(label, "shedding off: trace identical", same(src / "trace.tsv", out / "trace.tsv"), "hvi identical", same(src / "hvi.csv", out / "hvi.csv"),
          "stdout (without timing) identical", daily(src / "stdout.txt") == daily(out / "stdout.txt"), flush=True)
    src, out2 = run(label, ["--sheddingShape", "2"], "shed2")
    print(label, "shedding 2: hvi identical to round 8", same(src / "hvi.csv", out2 / "hvi.csv"), "trace identical", same(src / "trace.tsv", out2 / "trace.tsv"), flush=True)
