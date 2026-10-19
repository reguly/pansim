#!/usr/bin/env python3
"""Note 58 round 11: worlds matched on the likelihood k, with the observed shares as the comparison.

  python3 superspreader/study/analyze_round11.py worlds
  python3 superspreader/study/analyze_round11.py composition
  python3 superspreader/study/analyze_round11.py pairs
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from r6stats import BOOT_SEED, interval, write_csv  # noqa: E402
import analyze_round10 as a10  # noqa: E402
from analyze_round9 import nb_shares  # noqa: E402

OUT = HERE.parent
R9 = HERE / "results" / "round9"
R10 = HERE / "results" / "round10"
R11 = HERE / "results" / "round11"
UNKNOWN = a10.UNKNOWN

# report name -> (state base, state label)
WORLDS = [
    ("world1_multiplier_only", R10, "r10_w1_sh0.32"),
    ("world2a_scene_L30_plus_multiplier", R11, None),      # filled in from whatever r11 arm is closest to 0.35
    ("world2b_scene_L10_plus_multiplier", R11, None),
    ("world3_events_only", R10, "r10_w3_rate0.034"),
]


def r11_arms(lam):
    return sorted(p.stem for p in (R11 / "state").glob(f"r11_w2_L{lam}_sh*.json"))


def extras(label, dirs):
    """Statistics note 58 adds on top of the round-10 set, and the R11-3 cluster composition."""
    age, atype, home = a10.agent_table()
    top_n = 0
    rows = []
    for run in dirs:
        trace = a10.read_trace(run)
        ids, total, _event = a10.index_table(run / "trace.tsv")
        if len(total) == 0:
            continue
        top_n += max(1, int(round(0.01 * len(total))))
        children = defaultdict(list)
        for a, inf, loc, lt, d in trace:
            if inf != UNKNOWN:
                children[inf].append((loc, lt, d, a))
        for j in np.argsort(total)[::-1][:10]:
            inf_id = int(ids[j])
            kids = children.get(inf_id, [])
            if not kids:
                continue
            kid_ids = np.asarray([a for _l, _t, _d, a in kids])
            ages = age[kid_ids]
            by_type = Counter(t for _l, t, _d, _a in kids)
            modal_type, modal_n = by_type.most_common(1)[0]
            same_home = int(np.sum((home[kid_ids] >= 0) & (home[kid_ids] == home[inf_id]))) if home[inf_id] >= 0 else 0
            rows.append({"arm": label, "infector": inf_id, "offspring": int(total[j]),
                         "same_household_share": same_home / len(kids),
                         "modal_venue_type": int(modal_type),
                         "modal_venue_type_name": a10.LOCTYPE_NAMES.get(int(modal_type), str(modal_type)),
                         "same_venue_type_share": modal_n / len(kids),
                         "distinct_venue_types": len(by_type),
                         "infectee_age_min": int(ages.min()), "infectee_age_max": int(ages.max()),
                         "infectee_age_mean": float(ages.mean()),
                         "infectee_age_range": int(ages.max() - ages.min()),
                         "infector_age": int(age[inf_id]), "infector_agent_type": int(atype[inf_id])})
    summary = {"top1pct_infectors": top_n}
    if rows:
        for key in ("same_household_share", "same_venue_type_share", "distinct_venue_types",
                    "infectee_age_mean", "infectee_age_range"):
            summary[f"top10_clusters_mean_{key}"] = float(np.mean([r[key] for r in rows]))
        summary["top10_clusters_modal_venue_type_mode"] = Counter(r["modal_venue_type_name"] for r in rows).most_common(1)[0][0]
    return summary, rows


def collect(labels):
    rows, joint, clusters, comp = [], [], [], []
    for i, (name, base, label) in enumerate(labels):
        dirs, state = a10.run_dirs(base, label)
        row, j, c = a10.world_stats(name, dirs, 13 * i)
        extra, comp_rows = extras(name, dirs)
        row.update(extra)
        mean = row["early_R"]
        for est in ("mom", "ml"):
            z, s80 = nb_shares(row[f"k_{est}"], mean)
            row[f"nb_zero_at_k_{est}_own_mean"] = z
            row[f"nb_80pct_at_k_{est}_own_mean"] = s80
            z14, s14 = nb_shares(row[f"k_{est}"], 1.4)
            row[f"zero_at_mean_1.4_{est}"] = z14
            row[f"share_causing_80pct_at_mean_1.4_{est}"] = s14
        row["k_ml_over_k_mom"] = row["k_ml"] / row["k_mom"]
        row["observed_zero_minus_nb_zero_at_k_ml"] = row["share_0"] - row["nb_zero_at_k_ml_own_mean"]
        row.update({"background_coefficient": state["k"], "calibration_matched": state["matched"], "state_label": label})
        rows.append(row)
        joint += j
        clusters += c
        comp += comp_rows
        print(f"{name}: kml {row['k_ml']:.3f} kmom {row['k_mom']:.3f} ratio {row['k_ml_over_k_mom']:.2f} "
              f"mean {mean:.3f} zero {row['share_0']:.3f} (nb {row['nb_zero_at_k_ml_own_mean']:.3f}) "
              f"80% {row['share_of_index_cases_causing_80pct']:.3f} (nb {row['nb_80pct_at_k_ml_own_mean']:.3f}) "
              f"home {row['infections_share_home']:.3f} highL {row['infections_share_high_L_types']:.3f} "
              f"top1%n {row['top1pct_infectors']} day28 {row['day28_vs_6211.25']:+.3f}", flush=True)
    return rows, joint, clusters, comp


def worlds():
    labels = [("world1_multiplier_only", R10, "r10_w1_sh0.32")]
    for lam, nm in ((30, "world2a_scene_L30"), (10, "world2b_scene_L10")):
        for arm in r11_arms(lam):
            labels.append((f"{nm}_{arm.split('_')[-1]}", R11, arm))
    labels.append(("world3_events_only", R10, "r10_w3_rate0.034"))
    labels.append(("world2_round10_gate_L10_sh1", R9, "r9_s9_t1_L10_sh1"))
    rows, joint, clusters, comp = collect(labels)
    write_csv(OUT / "59_r111_worlds.csv", rows)
    write_csv(OUT / "59_r111_worlds_offspring.csv", joint)
    write_csv(OUT / "59_r111_clusters.csv", clusters)
    write_csv(OUT / "59_r113_cluster_composition.csv", comp)


def pairs():
    """Repeat-infection correlation for world 2a (and round-10 world 2), plus the class decomposition for R11-2."""
    from analyze import load_daily
    from analyze_round6 import episode_pairs, pearson, spearman as sp6
    fallback_hvi = R11 / "r11" / "pairs_w2_L30_sh0.70"
    sources = [("world1_multiplier_only", R10 / "r10" / "pairs_w1", None)]
    for d in sorted((R11 / "r11").glob("pairs_*")):
        sources.append((f"world2a_{d.name[len('pairs_'):]}", d, d))
    sources.append(("world2_round10_gate_L10_sh1", R10 / "r10" / "pairs_w2", fallback_hvi))
    rows = []
    for name, folder, hvi_folder in sources:
        runs = sorted(folder.glob("rep*"))
        if not runs:
            continue
        per_rep, per_rep_cls = [], {0: [], 1: []}
        for run in runs:
            last_day = len(load_daily(run / "stdout.txt")) - 1
            prs, _w2, _m, _n = episode_pairs(run, last_day)
            per_rep.append(prs)
            flags = None
            cls = (hvi_folder / run.name / "hvi.csv") if hvi_folder is not None else (run / "hvi.csv")
            if cls.exists():
                with open(cls) as handle:
                    next(handle)
                    flags = np.asarray([line.split(",")[4] == "1" for line in handle])
            for g in (0, 1):
                per_rep_cls[g].append([p for p in prs if flags is not None and bool(flags[p[0]]) == bool(g)])
        def corr(groups):
            allp = [p for rep in groups for p in rep]
            if len(allp) < 20:
                return None
            x = [p[2] for p in allp]
            y = [p[4] for p in allp]
            rp, rs = pearson(x, y), sp6(x, y)
            rng = np.random.default_rng(BOOT_SEED + 97)
            bp = []
            for _ in range(400):
                pick = rng.integers(0, len(groups), size=len(groups))
                pp = [p for i in pick for p in groups[i]]
                if len(pp) < 10:
                    continue
                bp.append(pearson([q[2] for q in pp], [q[4] for q in pp]))
            lo, hi = interval(bp) if bp else (float("nan"), float("nan"))
            return {"pairs": len(allp), "pearson": rp, "pearson_low": lo, "pearson_high": hi, "spearman": rs,
                    "mean_ep1": float(np.mean(x)), "mean_ep2": float(np.mean(y))}
        base_row = {"world": name, "replicates": len(per_rep)}
        allc = corr(per_rep)
        if allc:
            base_row.update({f"all_{k}": v for k, v in allc.items()})
        for g, gname in ((1, "class"), (0, "others")):
            c = corr(per_rep_cls[g])
            if c:
                base_row.update({f"{gname}_{k}": v for k, v in c.items()})
        base_row["reference_persistent_trait_pearson_R6_2"] = 0.5436
        base_row["reference_mobility_pearson_R7_S5"] = 0.0405
        rows.append(base_row)
        print(name, base_row, flush=True)
    write_csv(OUT / "59_r112_repeat_infections.csv", rows)


TASKS = {"worlds": worlds, "pairs": pairs}

if __name__ == "__main__":
    TASKS[sys.argv[1]]()
