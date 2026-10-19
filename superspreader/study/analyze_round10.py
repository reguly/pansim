#!/usr/bin/env python3
"""Note 55 round 10: the three worlds at matched k and their discriminating statistics, plus R10-2, R10-3 and R10-4."""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from r6stats import BOOT_SEED, bootstrap_pack, flatten_row, index_table, interval, pack, write_csv  # noqa: E402

OUT = HERE.parent
ROOT = HERE.parents[1]
R10 = HERE / "results" / "round10"
R9 = HERE / "results" / "round9"
UNKNOWN = 4294967295
STEPS = 144
HIGH = (5, 6, 9, 10)
LOCTYPE_NAMES = {2: "home", 3: "school", 33: "classroom", 4: "work_type4", 13: "work_type13", 1: "public_space", 5: "restaurant",
                 6: "large_venue", 7: "shop_short", 8: "shop_long", 9: "church", 10: "recreation", 12: "hospital",
                 14: "health_centre", 22: "nursing_home", 44: "university"}


def agent_table():
    """Age, agent type and home location id of every agent (cached)."""
    cache = R10 / "state" / "agents.npz"
    if cache.exists():
        d = np.load(cache)
        return d["age"], d["atype"], d["home"]
    people = json.load(open(ROOT / "inputRealExample" / "agents2.json"))["people"]
    age = np.zeros(len(people), dtype=np.int32)
    atype = np.zeros(len(people), dtype=np.int32)
    home = np.full(len(people), -1, dtype=np.int64)
    ids = {}
    for i, p in enumerate(people):
        age[i] = int(p.get("age", -1))
        atype[i] = int(p.get("typeID", p.get("type", -1)))
        for l in p["locations"]:
            if l["typeID"] == 2:
                home[i] = ids.setdefault(l["locID"], len(ids))
                break
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez(cache, age=age, atype=atype, home=home)
    return age, atype, home


def run_dirs(base, label):
    state = json.loads((base / "state" / f"{label}.json").read_text())
    return sorted(p.parent for p in (base / state["prefix"]).glob("rep*/trace.tsv")), state


def read_trace(run):
    """agent, infector, location, locType, day of every infection."""
    rows = []
    with open(run / "trace.tsv") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        col = {name: i for i, name in enumerate(header)}
        for line in handle:
            p = line.split("\t")
            rows.append((int(p[col["agent"]]), int(p[col["infector"]]), int(p[col["location"]]),
                         int(p[col["locType"]]), int(p[col["timestamp"]]) // STEPS))
    return rows


def world_stats(label, dirs, seed_offset=0, class_flags_name="hvi.csv"):
    """Shape measures plus the discriminating statistics of note 55."""
    age, atype, home = agent_table()
    reps, days = [], []
    loc_counts = Counter()
    cluster_rows = []
    top_age, top_type, top_class = [], [], []
    pop_age, pop_type = [], []
    hh_trans = hh_denom = 0
    maxima, p99, p999 = [], [], []
    for run in dirs:
        rows = read_trace(run)
        ids, total, event = index_table(run / "trace.tsv")
        reps.append((total, event))
        from analyze import load_daily
        days.append(int(load_daily(run / "stdout.txt")[27]["INF"]))
        children = defaultdict(list)
        for a, inf, loc, lt, d in rows:
            if 1 <= d <= 28:
                loc_counts[lt] += 1
                if inf != UNKNOWN and home[a] >= 0 and home[a] == home[inf]:
                    hh_trans += 1
            if inf != UNKNOWN:
                children[inf].append((loc, d, a))
        # offspring quantiles and the ten largest clusters of this replicate
        if len(total):
            maxima.append(int(total.max()))
            p99.append(float(np.quantile(total, 0.99)))
            p999.append(float(np.quantile(total, 0.999)))
        order = np.argsort(total)[::-1][:10]
        for j in order:
            inf_id = int(ids[j])
            kids = children.get(inf_id, [])
            if not kids:
                continue
            venues = {loc for loc, _d, _a in kids}
            by_venue_day = Counter((loc, d) for loc, d, _a in kids)
            cluster_rows.append({"arm": label, "offspring": int(total[j]), "distinct_venues": len(venues),
                                 "largest_venue_day_share": max(by_venue_day.values()) / len(kids)})
        # household denominator: other members of every index case's household
        hh_size = Counter(home[home >= 0].tolist())
        for a in ids.tolist():
            if home[a] >= 0:
                hh_denom += max(hh_size[int(home[a])] - 1, 0)
        # the top 1% of infectors
        if len(total):
            cut = max(1, int(round(0.01 * len(total))))
            top = ids[np.argsort(total)[::-1][:cut]]
            top_age += age[top].tolist()
            top_type += atype[top].tolist()
            cls = run / class_flags_name
            if cls.exists():
                flags = []
                with open(cls) as handle:
                    next(handle)
                    for line in handle:
                        flags.append(line.split(",")[4] == "1")
                flags = np.asarray(flags)
                top_class.append(float(flags[top].mean()))
            pop_age += age[ids].tolist()
            pop_type += atype[ids].tolist()
    total_all = np.concatenate([r[0] for r in reps])
    event_all = np.concatenate([r[1] for r in reps])
    row = flatten_row(label, pack(total_all, event_all), bootstrap_pack(reps, seed=BOOT_SEED + seed_offset))
    from analyze_round7 import lorenz_shares
    row.update(lorenz_shares(total_all))
    tot_loc = sum(loc_counts.values())
    for t, name in LOCTYPE_NAMES.items():
        row[f"infections_share_{name}"] = loc_counts.get(t, 0) / tot_loc
    row["infections_share_high_L_types"] = sum(loc_counts.get(t, 0) for t in HIGH) / tot_loc
    row["infections_share_school_and_work"] = sum(loc_counts.get(t, 0) for t in (3, 33, 4, 13, 44)) / tot_loc
    row.update({"replicates": len(dirs), "day28_mean": float(np.mean(days)), "day28_vs_6211.25": float(np.mean(days)) / 6211.25 - 1,
                "largest_offspring_mean_over_replicates": float(np.mean(maxima)), "largest_offspring_max": int(max(maxima)),
                "offspring_p99": float(np.mean(p99)), "offspring_p999": float(np.mean(p999)),
                "household_secondary_attack_rate": hh_trans / hh_denom if hh_denom else float("nan"),
                "household_transmissions": hh_trans, "household_susceptible_contacts": hh_denom})
    if cluster_rows:
        c = [r for r in cluster_rows if r["arm"] == label]
        row["top10_clusters_mean_distinct_venues"] = float(np.mean([r["distinct_venues"] for r in c]))
        row["top10_clusters_mean_largest_venue_day_share"] = float(np.mean([r["largest_venue_day_share"] for r in c]))
        row["top10_clusters_mean_offspring"] = float(np.mean([r["offspring"] for r in c]))
    if top_age:
        row["top1pct_mean_age"] = float(np.mean(top_age))
        row["all_infectors_mean_age"] = float(np.mean(pop_age))
        for t in sorted(set(pop_type)):
            if t < 0:
                continue
            row[f"top1pct_share_agent_type{t}"] = float(np.mean(np.asarray(top_type) == t))
            row[f"all_infectors_share_agent_type{t}"] = float(np.mean(np.asarray(pop_type) == t))
    if top_class:
        row["top1pct_share_in_class"] = float(np.mean(top_class))
    joint = [{"cell": label, "offspring_total": a, "offspring_at_events": e, "index_cases": n}
             for (a, e), n in sorted(Counter(zip(total_all.tolist(), event_all.tolist())).items())]
    return row, joint, cluster_rows


def nb_shares(k, mean=1.4):
    from analyze_round9 import nb_shares as f
    return f(k, mean)


WORLDS = {"world1_multiplier_only": (R10, None), "world2_scene_plus_multiplier": (R9, "r9_s9_t1_L10_sh1"),
          "world3_events_only": (R10, None)}


def arms_of(prefix, base=R10):
    return sorted(p.stem for p in (base / "state").glob(f"{prefix}*.json"))


def collect(labels):
    """labels: list of (report name, state base, state label)."""
    rows, joint, clusters = [], [], []
    for i, (name, base, label) in enumerate(labels):
        try:
            dirs, state = run_dirs(base, label)
        except FileNotFoundError:
            print("missing", label, flush=True)
            continue
        row, j, c = world_stats(name, dirs, 13 * i)
        for est in ("mom", "ml"):
            z, s80 = nb_shares(row[f"k_{est}"])
            row[f"zero_at_mean_1.4_{est}"] = z
            row[f"share_causing_80pct_at_mean_1.4_{est}"] = s80
        row.update({"background_coefficient": state["k"], "calibration_matched": state["matched"], "state_label": label})
        rows.append(row)
        joint += j
        clusters += c
        print(name, "kmom", round(row["k_mom"], 3), "kml", round(row["k_ml"], 3), "zero", round(row["share_0"], 3),
              "home", round(row["infections_share_home"], 3), "highL", round(row["infections_share_high_L_types"], 3),
              "maxoff", row["largest_offspring_max"], "hhSAR", round(row["household_secondary_attack_rate"], 4),
              "day28", round(row["day28_vs_6211.25"], 3), flush=True)
    return rows, joint, clusters


def pairs():
    """R10-1 item 4: offspring correlation across repeated infections of the same agent, for worlds 1 and 2."""
    from analyze import load_daily
    from analyze_round6 import episode_pairs, pearson, spearman as sp6
    rows = []
    for name, folder in (("world1_multiplier_only", "pairs_w1"), ("world2_scene_plus_multiplier", "pairs_w2")):
        runs = sorted((R10 / "r10" / folder).glob("rep*"))
        if not runs:
            continue
        per_rep = []
        for run in runs:
            last_day = len(load_daily(run / "stdout.txt")) - 1
            prs, _with_two, _multi, _n = episode_pairs(run, last_day)
            per_rep.append(prs)
        allp = [p for rep in per_rep for p in rep]
        x = [p[2] for p in allp]
        y = [p[4] for p in allp]
        rp, rs = pearson(x, y), sp6(x, y)
        rng = np.random.default_rng(BOOT_SEED + 97)
        bp, bs = [], []
        for _ in range(400):
            pick = rng.integers(0, len(per_rep), size=len(per_rep))
            pp = [p for i in pick for p in per_rep[i]]
            bp.append(pearson([q[2] for q in pp], [q[4] for q in pp]))
            bs.append(sp6([q[2] for q in pp], [q[4] for q in pp]))
        lo, hi = interval(bp)
        slo, shi = interval(bs)
        rows.append({"world": name, "replicates": len(per_rep), "pairs": len(allp), "pearson": rp, "pearson_low": lo, "pearson_high": hi,
                     "spearman": rs, "spearman_low": slo, "spearman_high": shi,
                     "reference_persistent_trait_pearson_R6_2": 0.5436, "reference_mobility_pearson_R7_S5": 0.0405})
        print(name, "pairs", len(allp), "pearson", round(rp, 4), (round(lo, 4), round(hi, 4)), "spearman", round(rs, 4), flush=True)
    write_csv(OUT / "56_r101_repeat_infections.csv", rows)


def main():
    cmd = sys.argv[1]
    labels = []
    if cmd == "worlds":
        for lab in arms_of("r10_w1_"):
            labels.append((f"world1_{lab[len('r10_'):]}", R10, lab))
        labels.append(("world2_scene_plus_multiplier", R9, "r9_s9_t1_L10_sh1"))
        for lab in arms_of("r10_w3_"):
            labels.append((f"world3_{lab[len('r10_'):]}", R10, lab))
        rows, joint, clusters = collect(labels)
        write_csv(OUT / "56_r101_worlds.csv", rows)
        write_csv(OUT / "56_r101_worlds_offspring.csv", joint)
        write_csv(OUT / "56_r101_clusters.csv", clusters)
    elif cmd == "pairs":
        pairs()
    elif cmd == "others":
        for lab in ("r10_r102_correlated", "r10_r103_nohome_sh1", "r10_r103_nohome_base", "r10_r104_upper"):
            if (R10 / "state" / f"{lab}.json").exists():
                labels.append((lab[len("r10_"):], R10, lab))
        labels.append(("round9_reference_sh1", R9, "r9_s9_ref_sh1"))
        labels.append(("round9_gate_sh2", R9, "r9_s9_t1_L10_sh2"))
        rows, joint, _c = collect(labels)
        write_csv(OUT / "56_r102_r104_summary.csv", rows)
        write_csv(OUT / "56_r102_r104_offspring.csv", joint)


if __name__ == "__main__":
    main()
