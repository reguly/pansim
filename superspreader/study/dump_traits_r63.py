#!/usr/bin/env python3
"""R6-3: write the trait of every agent for each PS1 replicate. Traits depend on the seed and the
trait flags only, so a one-week run with the stored command reproduces them. The stored
rep1101 dump is compared with the re-dump as a check."""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = HERE / "results" / "ps" / "ps1"
OUT = HERE / "results" / "round6" / "r63"
for arm in ("P0", "P25", "P50", "P100", "P25k", "P100ln"):
    for rep in sorted((BASE / arm).glob("rep*")):
        dest = OUT / arm / rep.name
        dump = dest / "agents_trait.csv"
        if dump.exists():
            continue
        dest.mkdir(parents=True, exist_ok=True)
        cmd = json.loads((rep / "command.json").read_text())
        i = cmd.index("-w"); cmd[i + 1] = "1"
        i = cmd.index("--infectionTrace"); cmd[i + 1] = str(dest / "trace1w.tsv")
        if "--traitDump" in cmd:
            i = cmd.index("--traitDump"); cmd[i + 1] = str(dump)
        else:
            cmd += ["--traitDump", str(dump)]
        r = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        print(arm, rep.name, r.returncode, flush=True)
        (dest / "trace1w.tsv").unlink(missing_ok=True)
