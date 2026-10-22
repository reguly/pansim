#!/usr/bin/env python3
"""Add replicates (seeds 77025 to 77036) to the final B2 cell of a world whose index cases are below 8,000."""
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_round14 as r14  # noqa: E402

world = sys.argv[1]
path = r14.STATE / f"b2_final_{world}.json"
d = json.loads(path.read_text())
fin = d["final"]
make = r14.r13.make_for(world, r14.pfmt(fin["param"]))
batch = []
for i, sd in enumerate(r14.seeds(77025), start=25):
    name = f"{fin['label']}/rep{i:02d}"
    batch.append((name, make(fin["coefficient"], sd, 4, r14.RESULTS / name)))
r14.r6.run_many(batch, r14.r13.job_for(world))
dirs = sorted(x.parent for x in (r14.RESULTS / fin["label"]).glob("rep*/trace.tsv"))
m = r14.measure(dirs)
d["final"] = {**fin, "early_R": m["R"], "k_ml": m["k_ml"], "k_mom": m["k_mom"], "day28": m["day28"], "index_cases": m["index_cases"], "replicates": m["replicates"]}
d["extended_to_36_replicates"] = True
path.write_text(json.dumps(d, indent=1) + "\n")
print(f"R14 B2 {world}: extended to {m['replicates']} replicates, index cases {m['index_cases']}, R={m['R']:.3f}, k_ml={m['k_ml']:.3f}", flush=True)
