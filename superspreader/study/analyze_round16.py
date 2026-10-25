#!/usr/bin/env python3
"""Note 82 runs F and H, from stored traces and delivered tables. No new simulations.

  python3 superspreader/study/analyze_round16.py F
  python3 superspreader/study/analyze_round16.py H
"""
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
RES = HERE / "results"
sys.path.insert(0, str(HERE))

from r6stats import write_csv  # noqa: E402

UNKNOWN = 4294967295
STEPS = 144
HOME_CACHE = RES / "round10" / "state" / "agents.npz"


def home_ids():
    return np.load(HOME_CACHE)["home"]


def read_infections(trace_path):
    rows = []
    with open(trace_path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        col = {name: i for i, name in enumerate(header)}
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            rows.append((
                int(parts[col["agent"]]),
                int(parts[col["infector"]]),
                int(parts[col["location"]]),
                int(parts[col["timestamp"]]) // STEPS,
            ))
    return rows


def canonical_top10(rows, home):
    """Ten largest clusters. Offspring descending, then infector id ascending.
    Offspring and composition both use children with 0 <= child_day - index_day <= 14.
    Index cases: infected on days 1-10 with a known infector.
    """
    day_of = {}
    for agent, inf, _loc, day in rows:
        if inf != UNKNOWN and 1 <= day <= 10 and agent not in day_of:
            day_of[agent] = day
    kids = defaultdict(list)
    for agent, inf, loc, day in rows:
        iday = day_of.get(inf)
        if iday is None:
            continue
        if 0 <= day - iday <= 14:
            kids[inf].append((loc, day, agent))
    ranked = sorted(day_of, key=lambda agent: (-len(kids[agent]), agent))[:10]
    offspring, hh, venue, distinct = [], [], [], []
    for agent in ranked:
        group = kids[agent]
        n = len(group)
        offspring.append(n)
        if n == 0:
            continue
        by_vd = Counter((loc, day) for loc, day, _a in group)
        venues = {loc for loc, _day, _a in group}
        if home[agent] >= 0:
            same = sum(1 for _loc, _day, child in group if home[child] == home[agent]) / n
            hh.append(same)
        venue.append(max(by_vd.values()) / n)
        distinct.append(len(venues))
    def mean(xs):
        return float(np.mean(xs)) if xs else float("nan")
    return {
        "top10_mean_offspring": mean(offspring),
        "top10_mean_same_household_share": mean(hh),
        "top10_mean_largest_venue_day_share": mean(venue),
        "top10_mean_distinct_venues": mean(distinct),
        "n_ranked": len(ranked),
    }


def dirs_of(round_name, state_file):
    state = json.loads((RES / round_name / "state" / state_file).read_text())
    found = sorted(p.parent for p in (RES / round_name / state["prefix"]).glob("rep*/trace.tsv"))
    if not found:
        raise RuntimeError(f"no traces for {round_name} {state_file} prefix {state['prefix']}")
    return found


def mean_rows(rows, key):
    vals = [r[key] for r in rows if r.get(key) == r.get(key)]
    return float(np.mean(vals)) if vals else float("nan")


def old_from_replicate_csv(path, arm):
    rows = []
    with open(path) as handle:
        for row in csv.DictReader(handle):
            if row["arm"] == arm:
                rows.append({
                    "top10_mean_offspring": float(row["top10_mean_offspring"]) if row["top10_mean_offspring"] else float("nan"),
                    "top10_mean_same_household_share": float(row["top10_mean_same_household_share"]) if row["top10_mean_same_household_share"] else float("nan"),
                    "top10_mean_largest_venue_day_share": float(row["top10_mean_largest_venue_day_share"]) if row["top10_mean_largest_venue_day_share"] else float("nan"),
                    "top10_mean_distinct_venues": float(row["top10_mean_distinct_venues"]) if row["top10_mean_distinct_venues"] else float("nan"),
                })
    if not rows:
        raise RuntimeError(f"{arm} not in {path}")
    return {key: mean_rows(rows, key) for key in rows[0]}


def cell_record(table, cell, script, runs, old, home):
    new_reps = [canonical_top10(read_infections(run / "trace.tsv"), home) for run in runs]
    new = {key: mean_rows(new_reps, key) for key in (
        "top10_mean_offspring", "top10_mean_same_household_share",
        "top10_mean_largest_venue_day_share", "top10_mean_distinct_venues")}
    row = {
        "table": table,
        "cell": cell,
        "previous_script": script,
        "replicates": len(runs),
        "new_offspring": new["top10_mean_offspring"],
        "old_offspring": old["top10_mean_offspring"],
        "diff_offspring": new["top10_mean_offspring"] - old["top10_mean_offspring"],
        "new_same_household_share": new["top10_mean_same_household_share"],
        "old_same_household_share": old["top10_mean_same_household_share"],
        "diff_same_household_pp": 100 * (new["top10_mean_same_household_share"] - old["top10_mean_same_household_share"]),
        "new_venue_day_share": new["top10_mean_largest_venue_day_share"],
        "old_venue_day_share": old["top10_mean_largest_venue_day_share"],
        "diff_venue_day_pp": 100 * (new["top10_mean_largest_venue_day_share"] - old["top10_mean_largest_venue_day_share"]),
        "new_distinct_venues": new["top10_mean_distinct_venues"],
        "old_distinct_venues": old["top10_mean_distinct_venues"],
        "diff_distinct_venues": new["top10_mean_distinct_venues"] - old["top10_mean_distinct_venues"],
    }
    print(
        f"F {table} {cell}: hh {row['diff_same_household_pp']:+.3f} pp, "
        f"venue-day {row['diff_venue_day_pp']:+.3f} pp, venues {row['diff_distinct_venues']:+.3f}",
        flush=True,
    )
    return row


def run_f():
    home = home_ids()
    rows = []
    # Table 5.16b: round-11 matched worlds. Previous numbers are the round-13 reanalysis
    # (analyze_round13.replicate_core: unstable argsort, composition not limited to 14 days),
    # which is the per-replicate file note 82 names. The round-11 script was the same on both points.
    table_b = [
        ("world1_sh0.32", "round10", "r10_w1_sh0.32.json", "round10:r10_w1_sh0.32"),
        ("world2a_L30_sh0.70", "round11", "r11_w2_L30_sh0.70.json", "round11:r11_w2_L30_sh0.70"),
        ("world2b_L10_sh0.58", "round11", "r11_w2_L10_sh0.58.json", "round11:r11_w2_L10_sh0.58"),
        ("world3b_r6_M30", "round6", "r67_M30.json", "round6:r67_M30"),
        ("world3b_paired", "round12", "r12_w3b_M30_rate0.1456.json", "round12:r12_w3b_M30_rate0.1456"),
        ("world3_rate0.034", "round10", "r10_w3_rate0.034.json", "round10:r10_w3_rate0.034"),
    ]
    for cell, rnd, state, arm in table_b:
        runs = dirs_of(rnd, state)
        old = old_from_replicate_csv(OUT / "66_n0_replicate_summary.csv", arm)
        rows.append(cell_record("5.16b", cell, "analyze_round11.py / analyze_round13.py replicate_core", runs, old, home))

    # Table 5.16f: round-13 seed-set cells (66_n1), same script as analyze_round13.
    n1_arms = []
    with open(OUT / "66_n1_replicate_summary.csv") as handle:
        for row in csv.DictReader(handle):
            if row["arm"] not in n1_arms:
                n1_arms.append(row["arm"])
    import analyze_round13 as a13
    registry = {c["cell"]: c["dirs"] for c in a13.cell_registry(include_sens=False)}
    for arm in n1_arms:
        if arm not in registry:
            print(f"F skip {arm}: no trace registry", flush=True)
            continue
        old = old_from_replicate_csv(OUT / "66_n1_replicate_summary.csv", arm)
        rows.append(cell_record("5.16f", arm, "analyze_round13.py replicate_core", registry[arm], old, home))

    # Table 5.17a all-detected arms: detection rate 1 in 62_r122_thinning.csv.
    # Those rows were produced by analyze_round12.py's thinning function, which already
    # kept only 14-day offspring. The trace set is the paired worlds.
    thin_worlds = {
        "world1_multiplier_only": ("round10", "r10_w1_sh0.32.json"),
        "world2a_scene_L30": ("round11", "r11_w2_L30_sh0.70.json"),
        "world2b_scene_L10": ("round11", "r11_w2_L10_sh0.58.json"),
        "world3b_paired": ("round12", "r12_w3b_M30_rate0.1456.json"),
    }
    # Discover the actual world labels in the thinning file.
    thin_rows = list(csv.DictReader(open(OUT / "62_r122_thinning.csv")))
    worlds_in_file = sorted({r["world"] for r in thin_rows})
    print("thinning worlds:", worlds_in_file, flush=True)
    label_map = {}
    for label in worlds_in_file:
        for key, spec in thin_worlds.items():
            if label.startswith(key) or key.startswith(label) or label.replace("_", "") in key.replace("_", ""):
                label_map[label] = spec
        if "world1" in label or label.startswith("world1"):
            label_map[label] = thin_worlds["world1_multiplier_only"]
        elif "2a" in label or "L30" in label:
            label_map[label] = thin_worlds["world2a_scene_L30"]
        elif "2b" in label or "L10" in label:
            label_map[label] = thin_worlds["world2b_scene_L10"]
        elif "3b" in label:
            label_map[label] = thin_worlds["world3b_paired"]
    seen = set()
    for row in thin_rows:
        if float(row["detection_rate"]) != 1.0:
            continue
        key = (row["world"], row["scheme"], row["detection_rate"])
        if key in seen:
            continue
        seen.add(key)
        spec = label_map.get(row["world"])
        if spec is None:
            print(f"F skip thinning {row['world']}: no traces", flush=True)
            continue
        runs = dirs_of(*spec)
        old = {
            "top10_mean_offspring": float(row["top10_clusters_mean_offspring"]),
            "top10_mean_same_household_share": float(row["top10_clusters_mean_same_household_share"]),
            "top10_mean_largest_venue_day_share": float(row["top10_clusters_mean_largest_venue_day_share"]),
            "top10_mean_distinct_venues": float(row["top10_clusters_mean_distinct_venues"]),
        }
        rows.append(cell_record(
            "5.17a", f"{row['world']}|{row['scheme']}|p{row['detection_rate']}",
            "analyze_round12.py thinning (14-day filter)", runs, old, home))

    # Table 5.19b: round-14 B1 cells. Previous script: analyze_round14.py -> analyze_round13.replicate_core.
    for world in ("w1", "w2b", "w3b"):
        state = json.loads((RES / "round14" / "state" / f"r14_b1final_{world}.json").read_text())
        runs = sorted(p.parent for p in (RES / "round14" / state["prefix"]).glob("rep*/trace.tsv"))
        old = old_from_replicate_csv(OUT / "69_b_replicate_summary.csv", f"{world}:B1")
        rows.append(cell_record("5.19b", f"{world}:B1", "analyze_round14.py via analyze_round13.replicate_core", runs, old, home))

    # Table 5.22a: round-15 density cells, including alpha=1 B1 references.
    # analyze_round15.replicate_core_d ranks with a stable sort on offspring only (ties keep trace order)
    # and composes over every child in the trace, not only the 14-day window.
    with open(OUT / "74_d_replicate_summary.csv") as handle:
        arms = []
        for row in csv.DictReader(handle):
            if row["arm"] not in arms:
                arms.append(row["arm"])
    import analyze_round15 as a15
    for arm in arms:
        # Reconstruct directories the same way analyze_round15.run_d_analysis does.
        world, rest = arm.split(":", 1)
        if rest.startswith("B1"):
            state = json.loads((RES / "round14" / "state" / f"r14_b1final_{world}.json").read_text())
            runs = sorted(p.parent for p in (RES / "round14" / state["prefix"]).glob("rep*/trace.tsv"))
        else:
            alpha = rest.split("alpha")[1]
            state = json.loads((RES / "round15" / "state" / f"r15_d_a{alpha}_{world}.json").read_text())
            runs = sorted(p.parent for p in (RES / "round15" / state["prefix"]).glob("rep*/trace.tsv"))
        old = old_from_replicate_csv(OUT / "74_d_replicate_summary.csv", arm)
        rows.append(cell_record("5.22a", arm, "analyze_round15.py replicate_core_d", runs, old, home))

    write_csv(OUT / "83_f_diff.csv", rows)
    worst_pp = max(max(abs(r["diff_same_household_pp"]), abs(r["diff_venue_day_pp"])) for r in rows)
    worst_v = max(abs(r["diff_distinct_venues"]) for r in rows)
    print(f"F done: {len(rows)} cells, max |share diff| {worst_pp:.3f} pp, max |venues| {worst_v:.3f}", flush=True)


def fill_hist(counts):
    if not counts:
        return []
    hi = max(counts)
    return [(j, counts.get(j, 0)) for j in range(hi + 1)]


def load_hist_csv(path, arm_col="arm"):
    """arm -> replicate -> offspring -> count. Sums duplicate keys."""
    out = defaultdict(lambda: defaultdict(Counter))
    seeds = defaultdict(dict)
    n_index = defaultdict(lambda: defaultdict(int))
    with open(path) as handle:
        for row in csv.DictReader(handle):
            arm = row[arm_col]
            rep = int(row["replicate"])
            off = int(row["offspring_total"])
            n = int(row["index_cases"])
            out[arm][rep][off] += n
            n_index[arm][rep] += n
            if "seed" in row and row["seed"] != "":
                seeds[arm][rep] = int(float(row["seed"]))
    return out, seeds, n_index


def run_h():
    pieces = []
    for path in (
        OUT / "69_a_replicate_histograms.csv",
        OUT / "66_n3_replicate_histograms.csv",
        OUT / "69_b_replicate_histograms.csv",
        OUT / "74_d_replicate_histograms.csv",
    ):
        hist, seeds, _n = load_hist_csv(path)
        pieces.append((path.name, hist, seeds))

    def find(arm):
        for source, hist, seeds in pieces:
            if arm in hist:
                return source, hist[arm], seeds[arm]
        return None, None, None

    wanted = []
    for table, path in (("5.20a", OUT / "70_delaporte_fits_A.csv"), ("5.20b", OUT / "70_delaporte_fits_B.csv")):
        for row in csv.DictReader(open(path)):
            wanted.append((table, row["arm"]))
    for row in csv.DictReader(open(OUT / "74_d_cells_summary.csv")):
        wanted.append(("5.22a", row["cell"]))

    out_rows = []
    missing = []
    for table, arm in wanted:
        source, reps, seeds = find(arm)
        if reps is None:
            missing.append((table, arm))
            continue
        for rep in sorted(reps):
            counts = reps[rep]
            n_index = sum(counts.values())
            for offspring, n in fill_hist(counts):
                out_rows.append({
                    "table": table,
                    "cell": arm,
                    "source_file": source,
                    "replicate": rep,
                    "seed": seeds.get(rep, ""),
                    "n_index_cases": n_index,
                    "offspring": offspring,
                    "index_cases": n,
                })
        print(f"H {table} {arm}: {len(reps)} replicates from {source}", flush=True)
    if missing:
        print("H missing arms:", missing, flush=True)
    write_csv(OUT / "83_h_replicate_histograms.csv", out_rows)
    print(f"H wrote {len(out_rows)} rows, missing {len(missing)}", flush=True)


def t_crit_90(df):
    """Upper 5% point of Student's t, the half-width factor of a 90% interval."""
    z = 1.6448536269514722
    n = float(df)
    return (z + (z ** 3 + z) / (4 * n) + (5 * z ** 5 + 16 * z ** 3 + 3 * z) / (96 * n ** 2)
            + (3 * z ** 7 + 19 * z ** 5 + 17 * z ** 3 - 15 * z) / (384 * n ** 3))


def _log_pois(j, lam):
    if lam <= 0:
        return 0.0 if j == 0 else -1e300
    return -lam + j * math.log(lam) - math.lgamma(j + 1)


def _log_nb(j, mu, k):
    p = k / (k + mu)
    return math.lgamma(j + k) - math.lgamma(k) - math.lgamma(j + 1) + k * math.log(p) + j * math.log(1 - p)


def delaporte_baseline(values):
    """Delaporte = Poisson(l0) + NB(mu, k), mean fixed. Returns the baseline share l0/mean."""
    values = np.asarray(values, dtype=np.int64)
    mean = float(values.mean())
    if not mean > 0:
        return float("nan")
    counts = Counter(values.tolist())
    hi = min(max(counts), 400)

    def nll(th):
        l0 = mean / (1.0 + math.exp(-th[0]))
        mu = max(mean - l0, 1e-9)
        k = math.exp(th[1])
        total = 0.0
        for j, c in counts.items():
            if j > hi:
                continue
            terms = []
            for i in range(j + 1):
                terms.append(_log_pois(i, l0) + _log_nb(j - i, mu, k))
            m = max(terms)
            total += c * (m + math.log(sum(math.exp(t - m) for t in terms)))
        return -total

    best = None
    for t0 in (-3.0, -1.0, 1.0):
        for t1 in (-3.0, -1.0, 0.0):
            x = [t0, t1]
            # Nelder-Mead, two parameters.
            simplex = [x, [x[0] + 0.4, x[1]], [x[0], x[1] + 0.4]]
            vals = [nll(p) for p in simplex]
            for _ in range(80):
                order = sorted(range(3), key=lambda i: vals[i])
                simplex = [simplex[i] for i in order]
                vals = [vals[i] for i in order]
                centroid = [(simplex[0][d] + simplex[1][d]) / 2 for d in range(2)]
                reflected = [centroid[d] + (centroid[d] - simplex[2][d]) for d in range(2)]
                fr = nll(reflected)
                if vals[0] <= fr < vals[1]:
                    simplex[2], vals[2] = reflected, fr
                elif fr < vals[0]:
                    expanded = [centroid[d] + 2 * (reflected[d] - centroid[d]) for d in range(2)]
                    fe = nll(expanded)
                    simplex[2], vals[2] = (expanded, fe) if fe < fr else (reflected, fr)
                else:
                    contracted = [centroid[d] + 0.5 * (simplex[2][d] - centroid[d]) for d in range(2)]
                    fc = nll(contracted)
                    if fc < vals[2]:
                        simplex[2], vals[2] = contracted, fc
                    else:
                        simplex[1] = [(simplex[0][d] + simplex[1][d]) / 2 for d in range(2)]
                        simplex[2] = [(simplex[0][d] + simplex[2][d]) / 2 for d in range(2)]
                        vals[1], vals[2] = nll(simplex[1]), nll(simplex[2])
            if best is None or vals[0] < best[0]:
                best = (vals[0], simplex[0])
    l0 = mean / (1.0 + math.exp(-best[1][0]))
    return l0 / mean


def offspring_by_replicate(dirs):
    from r6stats import index_table
    out = []
    for run in dirs:
        _ids, total, _event = index_table(run / "trace.tsv")
        out.append(np.asarray(total, dtype=np.int64))
    return out


def pooled_fingerprints(groups):
    from r6stats import ml_k, mom_k, nb_pmf
    y = np.concatenate(groups) if groups else np.asarray([], dtype=np.int64)
    n = int(y.size)
    mean = float(y.mean()) if n else float("nan")
    kml = float(ml_k(y)) if n > 1 else float("nan")
    kmom = float(mom_k(y)) if n > 1 else float("nan")
    zero = float(np.mean(y == 0)) if n else float("nan")
    nb_zero = float(nb_pmf(mean, kml, 0)) if n > 1 else float("nan")
    return {
        "n": n,
        "replicates": len(groups),
        "mean": mean,
        "k_ml": kml,
        "k_mom": kmom,
        "zero_share": zero,
        "nb_zero": nb_zero,
        "zero_gap_points": 100 * (zero - nb_zero),
        "delaporte_baseline": delaporte_baseline(y) if n > 1 else float("nan"),
        "max_offspring": int(y.max()) if n else 0,
        "share_0": zero,
        "share_1_to_5": float(np.mean((y >= 1) & (y <= 5))) if n else float("nan"),
        "share_above_5": float(np.mean(y > 5)) if n else float("nan"),
    }


def replicate_intervals(groups, key_fn, seed=20261016, draws=1000):
    """90% replicate-bootstrap percentile interval and jackknife-t interval of a pooled statistic."""
    rng = np.random.default_rng(seed)
    r = len(groups)
    point = key_fn(groups)
    boots = np.empty(draws)
    for i in range(draws):
        pick = rng.integers(0, r, r)
        boots[i] = key_fn([groups[j] for j in pick])
    lo, hi = np.quantile(boots, [0.05, 0.95])
    leave = np.empty(r)
    for i in range(r):
        leave[i] = key_fn(groups[:i] + groups[i + 1:])
    se = math.sqrt((r - 1) / r * float(np.sum((leave - leave.mean()) ** 2)))
    half = t_crit_90(r - 1) * se
    return {
        "point": point,
        "boot_low": float(lo),
        "boot_high": float(hi),
        "jackknife_t_low": point - half,
        "jackknife_t_high": point + half,
        "jackknife_se": se,
    }


def run_g():
    """Hours at tilt 0, 0.5 and 1. Role-discretionary hours and the hdt sum used in Section 5.14."""
    import analyze_round8 as a8
    results = HERE / "results" / "round16" / "G"
    high = (5, 6, 9, 10)
    hdt_types = (1, 5, 6, 7, 8, 9, 10)
    rows = []

    def one(path, tilt, seed_label):
        data = a8.load_log(path)
        # role-discretionary hours are not in load_log; read them directly
        role = []
        with open(path) as handle:
            for rec in csv.DictReader(handle):
                days = float(rec["days_weekday"]) + float(rec["days_weekend"])
                role.append((float(rec["h_wd_role_disc"]) + float(rec["h_we_role_disc"])) / days)
        role = np.asarray(role)
        groups = a8.groups(data)
        for gname, mask in groups.items():
            if gname not in ("class", "others_eligible"):
                continue
            hdt = {t: float(data[f"hdt_{t}"][mask].mean()) for t in hdt_types}
            hpt_high = sum(float(data[f"hpt_{t}"][mask].mean()) for t in high)
            hdt_sum = sum(hdt.values())
            hdt_high = sum(hdt[t] for t in high)
            rows.append({
                "tilt": tilt,
                "seeds": seed_label,
                "group": gname,
                "agents": int(mask.sum()),
                "role_disc_hours_per_day": float(role[mask].mean()),
                "hdt_sum_per_day": hdt_sum,
                "hdt_high_per_day": hdt_high,
                "hdt_high_share": hdt_high / hdt_sum if hdt_sum else float("nan"),
                "all_hours_at_high_types": hpt_high,
                "population": "eligible agents aged 15+ in types 4-8; class is the 5% round-8 class",
            })

    for tilt in ("t0", "t0.5", "t1"):
        # average the 12 seeds by pooling agents across replicates
        paths = sorted((results / tilt).glob("rep*/mobility.csv"))
        # per-seed then mean, so a seed of a different length does not dominate
        acc = []
        for path in paths:
            before = len(rows)
            one(path, tilt, "77001-77012")
            acc.append(rows[before:])
            del rows[before:]
        keys = [k for k in acc[0][0] if k not in ("tilt", "seeds", "group", "population")]
        for g_i, gname in enumerate(("class", "others_eligible")):
            merged = {"tilt": tilt, "seeds": "77001-77012", "group": gname, "population": acc[0][g_i]["population"]}
            for key in keys:
                merged[key] = float(np.mean([block[g_i][key] for block in acc]))
            rows.append(merged)
        one(results / f"{tilt}_seed73001" / "mobility.csv", tilt, "73001")
    write_csv(OUT / "83_g_hours.csv", rows)
    # G(a) on the class role-disc hours and on the hdt sum
    by = {(r["tilt"], r["seeds"], r["group"]): r for r in rows}
    for seeds in ("77001-77012", "73001"):
        role = [by[(t, seeds, "class")]["role_disc_hours_per_day"] for t in ("t0", "t0.5", "t1")]
        hdt = [by[(t, seeds, "class")]["hdt_sum_per_day"] for t in ("t0", "t0.5", "t1")]
        def spread(xs):
            return (max(xs) - min(xs)) / min(xs)
        print(f"G {seeds} class role-disc {role} spread {spread(role):.4%} hdt {hdt} spread {spread(hdt):.4%}", flush=True)


def run_ab_report():
    """Summarise whatever Run A and Run B state files exist."""
    import run_round16 as r16
    state = r16.STATE
    rows = []
    manifest = state / "a_manifest.json"
    if manifest.exists():
        from r6stats import ml_k
        for entry in json.loads(manifest.read_text()):
            dirs = [Path(p) for p in entry["eval_dirs"]]
            groups = offspring_by_replicate(dirs)

            def kml_of(gs, _ml=ml_k):
                y = np.concatenate(gs)
                return float(_ml(y))

            def gap_of(gs):
                from r6stats import nb_pmf
                y = np.concatenate(gs)
                mean = float(y.mean())
                kml = float(ml_k(y))
                zero = float(np.mean(y == 0))
                return 100 * (zero - float(nb_pmf(mean, kml, 0)))

            point = pooled_fingerprints(groups)
            # own-set day 28 is already in the calibration record; all-36 day 28 from the eval runs
            days = []
            for run in dirs:
                from analyze import load_daily
                days.append(int(load_daily(run / "stdout.txt")[27]["INF"]))
            k_iv = replicate_intervals(groups, kml_of)
            g_iv = replicate_intervals(groups, gap_of, seed=20261017)
            rows.append({
                "run": "A",
                "label": entry["label"],
                "coefficient": entry["k"],
                "own_day28": entry["own_day28"],
                "all36_day28": float(np.mean(days)),
                "trials": entry["n_trials"],
                "matched_own": entry["matched_on_own_set"],
                **{f"fp_{k}": v for k, v in point.items()},
                "k_ml_boot_low": k_iv["boot_low"], "k_ml_boot_high": k_iv["boot_high"],
                "k_ml_jt_low": k_iv["jackknife_t_low"], "k_ml_jt_high": k_iv["jackknife_t_high"],
                "gap_boot_low": g_iv["boot_low"], "gap_boot_high": g_iv["boot_high"],
                "gap_jt_low": g_iv["jackknife_t_low"], "gap_jt_high": g_iv["jackknife_t_high"],
            })
            print(f"A {entry['label']}: k={entry['k']:.6g} day28={np.mean(days):.0f} kml={point['k_ml']:.3f} gap={point['zero_gap_points']:.2f}", flush=True)
    for world in ("w1", "w2b", "w3b"):
        path = state / f"b2_final_{world}.json"
        if not path.exists():
            continue
        final = json.loads(path.read_text())
        dirs = sorted(p.parent for p in (r16.RESULTS / final["prefix"]).glob("rep*/trace.tsv"))
        groups = offspring_by_replicate(dirs)
        point = pooled_fingerprints(groups)
        rows.append({"run": "B", "label": world, "trials": final["n_trials"], "coefficient": final["chosen"]["coefficient"],
                     "param": final["chosen"]["param"], "mean_within_3pct": final["mean_within_3pct"], **{f"fp_{k}": v for k, v in point.items()}})
        print(f"B {world}: R={point['mean']:.3f} kml={point['k_ml']:.3f} gap={point['zero_gap_points']:.2f} max={point['max_offspring']}", flush=True)
    if rows:
        write_csv(OUT / "83_ab_summary.csv", rows)
    return rows


if __name__ == "__main__":
    {"F": run_f, "H": run_h, "AB": run_ab_report, "G": run_g}[sys.argv[1]]()
