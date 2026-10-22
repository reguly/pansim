#!/usr/bin/env python3
"""B2, world 3b, beyond the five-trial limit of note 68: a log-linear model of the early R and of the likelihood k in the
background coefficient and the event rate, fitted to every B2 point of that world (rate at most 0.13), solved for R 0.88
and k 0.27, then tried on 6 replicates (seeds 76001 to 76006); at most four extra trials; then 12 replicates on 77001
to 77012 and, if the pooled index cases are below 8,000, 12 more per step (seeds 77013 on) up to 36.
"""
import json
import math
import re
import sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_round14 as r14  # noqa: E402

world = "w3b"
STATE = r14.STATE
base = json.loads((STATE / f"b2_final_{world}.json").read_text())
pts = [(t["coefficient"], t["param"], t["early_R"], t["k_ml"], 6, f"trial{t['iteration']}") for t in base["trials"]]
pts += [(a["coefficient"], a["param"], a["early_R"], a["k_ml"], 12, a["label"]) for a in base["attempts"]]
extra = []
log_path = STATE / "b2ext_trials_w3b.json"
if log_path.exists():
    extra = json.loads(log_path.read_text())
    pts += [(t["coefficient"], t["param"], t["early_R"], t["k_ml"], 6, f"ext{t['iteration']}") for t in extra]


def propose(points):
    sel = [p for p in points if p[1] <= 0.13]
    X = np.array([[1, math.log(p[0]), math.log(p[1])] for p in sel])
    w = np.sqrt(np.array([p[4] for p in sel], float))
    cR = np.linalg.lstsq(X * w[:, None], np.log([p[2] for p in sel]) * w, rcond=None)[0]
    ck = np.linalg.lstsq(X * w[:, None], np.log([p[3] for p in sel]) * w, rcond=None)[0]
    A = np.array([[cR[1], cR[2]], [ck[1], ck[2]]])
    b = np.array([math.log(0.88) - cR[0], math.log(0.27) - ck[0]])
    c, p = np.exp(np.linalg.solve(A, b))
    return float(c), float(p), cR.tolist(), ck.tolist()


for it in range(len(extra), 4):
    c, p, cR, ck = propose(pts)
    dirs = r14.run_cell(f"b2ext-i{it + 1}_{world}", world, c, p, r14.CAL_SEEDS)
    m = r14.measure(dirs)
    rec = {"iteration": it + 1, "param": float(r14.pfmt(p)), "coefficient": c, "early_R": m["R"], "k_ml": m["k_ml"], "k_mom": m["k_mom"],
           "day28": m["day28"], "index_cases": m["index_cases"], "replicates": 6, "model_R": cR, "model_k": ck}
    extra.append(rec)
    r14.log_json(log_path, extra)
    pts.append((c, rec["param"], m["R"], m["k_ml"], 6, f"ext{it + 1}"))
    print(f"R14 B2ext {world} trial {it + 1}: param={p:.4g} coeff={c:.5g} R={m['R']:.3f} k_ml={m['k_ml']:.3f}", flush=True)
    if abs(m["R"] / 0.88 - 1) <= 0.02 and abs(m["k_ml"] - 0.27) <= 0.02:
        break


def dist(t):
    return max(abs(t["early_R"] / 0.88 - 1) / 0.03, abs(t["k_ml"] - 0.27) / 0.03)


best = min(extra, key=dist)
c, p = best["coefficient"], best["param"]
attempts = []
for corr in range(3):
    label = f"b2extfinal{'' if corr == 0 else '-c%d' % corr}_{world}"
    dirs = r14.run_cell(label, world, c, p, r14.seeds(77001))
    m = r14.measure(dirs)
    attempts.append({"label": label, "param": float(r14.pfmt(p)), "coefficient": c, "early_R": m["R"], "k_ml": m["k_ml"], "k_mom": m["k_mom"],
                     "day28": m["day28"], "index_cases": m["index_cases"], "replicates": m["replicates"]})
    print(f"R14 B2ext final {world} {label}: param={p:.4g} coeff={c:.5g} R={m['R']:.3f} k_ml={m['k_ml']:.3f} index={m['index_cases']}", flush=True)
    if abs(m["R"] / 0.88 - 1) <= 0.03 and 0.24 <= m["k_ml"] <= 0.30:
        break
    pts.append((c, p, m["R"], m["k_ml"], 12, label))
    c, p, _, _ = propose(pts)
final = attempts[-1]
nrep = final["replicates"]
while final["index_cases"] < 8000 and nrep < 36:
    label = final["label"]
    make = r14.r13.make_for(world, r14.pfmt(final["param"]))
    batch = []
    for i, sd in enumerate(r14.seeds(77001 + nrep), start=nrep + 1):
        name = f"{label}/rep{i:02d}"
        batch.append((name, make(final["coefficient"], sd, 4, r14.RESULTS / name)))
    r14.r6.run_many(batch, r14.r13.job_for(world))
    dirs = sorted(x.parent for x in (r14.RESULTS / label).glob("rep*/trace.tsv"))
    m = r14.measure(dirs)
    final = {**final, "early_R": m["R"], "k_ml": m["k_ml"], "k_mom": m["k_mom"], "day28": m["day28"], "index_cases": m["index_cases"], "replicates": m["replicates"]}
    nrep = m["replicates"]
    print(f"R14 B2ext {world}: {nrep} replicates, index cases {m['index_cases']}, R={m['R']:.3f}, k_ml={m['k_ml']:.3f}", flush=True)
r14.log_json(STATE / "b2ext_final_w3b.json", {"world": world, "final": final, "attempts": attempts, "trials": extra, "prefix": final["label"]})
