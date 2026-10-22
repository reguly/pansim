#!/usr/bin/env python3
"""Note 65 round 13 analysis: replicate-level exports (N0), cells of N1/N2/N3, and thinning draws (N4).

  python3 superspreader/study/analyze_round13.py n0            # 66_n0_*.csv for every arm of rounds 6 to 12
  python3 superspreader/study/analyze_round13.py cells         # 66_n1_* / 66_n2_* from results/round13
  python3 superspreader/study/analyze_round13.py n4            # 66_n4_thinning_draws.csv

Definitions are those of round 12 (analyze_round12.world_stats_with_events): index cases are agents infected on
days 1 to 10 with a known infector, offspring are infections they cause up to day + 14, event offspring are
infectees listed in <eventGroupLog>.infections. Per-replicate statistics are computed on that replicate's index
cases alone.
"""
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from r6stats import load_event_agents, load_events, ml_k, mom_k, write_csv  # noqa: E402
import analyze_round10 as a10  # noqa: E402
from analyze import load_daily  # noqa: E402
from analyze_round7 import lorenz_shares  # noqa: E402
from analyze_round9 import nb_shares  # noqa: E402

OUT = HERE.parent
RES = HERE / "results"
UNKNOWN = a10.UNKNOWN
SCHOOL_WORK = (3, 33, 4, 13, 44)
HIGH = a10.HIGH
HOSPITAL = (12,)
_CTX = {}


def ctx():
    if not _CTX:
        age, atype, home = a10.agent_table()
        _CTX.update(age=age, atype=atype, home=home, hh_size=Counter(home[home >= 0].tolist()))
    return _CTX


def run_info(run):
    cmd = json.loads((run / "command.json").read_text())
    return {"seed": int(cmd[cmd.index("--seed") + 1]), "k": float(cmd[cmd.index("-k") + 1]),
            "weeks": int(cmd[cmd.index("-w") + 1]), "agents": Path(cmd[cmd.index("-a") + 1]).name}


def replicate_core(run):
    """One replicate: everything computed on its own index cases. Returns (row, ids, total, event)."""
    c = ctx()
    home, atype = c["home"], c["atype"]
    run = Path(run)
    info = run_info(run)
    household_ok = info["agents"] in ("agents2.json", "r13_agents_venues_redrawn.json")  # homes and types unchanged in the redrawn file
    rows = a10.read_trace(run)
    ev_path = run / "events.tsv.infections"
    ev_agents = load_event_agents(ev_path) if ev_path.exists() else None
    ev_log = run / "events.tsv"
    ev_header = ev_log.open().readline().rstrip("\n").split("\t") if ev_log.exists() else []
    # two formats: closed-group log (infectious_in_group, with .infections) and the venue-day boost log (max_present)
    ev_venue_days = load_events(ev_log) if "max_present" in ev_header else None

    day, children = {}, defaultdict(list)
    loc_counts = Counter()
    hh_trans = 0
    for a, inf, loc, lt, d in rows:
        day[a] = d
        if inf != UNKNOWN:
            children[inf].append((loc, lt, d, a))
        if 1 <= d <= 28:
            loc_counts[lt] += 1
            if household_ok and inf != UNKNOWN and home[a] >= 0 and home[a] == home[inf]:
                hh_trans += 1
    known = {a for kids in children.values() for _l, _t, _d, a in kids}
    ids, total, event = [], [], []
    for a, d in day.items():
        if a not in known or not (1 <= d <= 10):
            continue
        n = e = 0
        for _loc, _lt, cd, ca in children.get(a, ()):
            if cd <= d + 14:
                n += 1
                if ev_agents is not None and ca in ev_agents:
                    e += 1
                elif ev_venue_days is not None and (_loc, cd) in ev_venue_days:
                    e += 1
        ids.append(a)
        total.append(n)
        event.append(e)
    ids, total, event = np.asarray(ids, dtype=np.int64), np.asarray(total, dtype=np.int64), np.asarray(event, dtype=np.int64)

    daily = load_daily(run / "stdout.txt")
    row = {"seed": info["seed"], "background_coefficient": info["k"], "weeks": info["weeks"]}
    for dd in (28, 56, 84, 112):
        row[f"day{dd}_cumulative_infections"] = int(daily[dd - 1]["INF"]) if len(daily) >= dd else ""
    n = len(total)
    row["index_cases"] = n
    row["early_R"] = float(total.mean()) if n else float("nan")
    nodes, seeds_ = len(rows), sum(1 for r in rows if r[1] == UNKNOWN)
    row["mean_offspring_all_nodes"] = (nodes - seeds_) / nodes if nodes else float("nan")
    row["k_mom"] = mom_k(total) if n > 1 else ""
    row["k_ml"] = ml_k(total) if n > 1 else ""
    row["share_0"] = float(np.mean(total == 0)) if n else float("nan")
    ls = lorenz_shares(total) if n else {}
    row["share_causing_80pct"] = ls.get("share_of_index_cases_causing_80pct", "")
    row["largest_offspring"] = int(total.max()) if n else 0
    tot_loc = sum(loc_counts.values())
    if tot_loc:
        row["infections_share_home"] = loc_counts.get(2, 0) / tot_loc
        row["infections_share_school_and_work"] = sum(loc_counts.get(t, 0) for t in SCHOOL_WORK) / tot_loc
        row["infections_share_high_L_types"] = sum(loc_counts.get(t, 0) for t in HIGH) / tot_loc
        row["infections_share_hospital"] = sum(loc_counts.get(t, 0) for t in HOSPITAL) / tot_loc
    row["infections_d1_28"] = tot_loc
    if household_ok:
        den = sum(max(c["hh_size"][int(home[a])] - 1, 0) for a in ids.tolist() if home[a] >= 0)
        row["household_secondary_attack_numerator"] = hh_trans
        row["household_secondary_attack_denominator"] = den
    # ten largest clusters
    comp = []
    for j in (np.argsort(total)[::-1][:10] if n else []):
        inf_id = int(ids[j])
        kids = children.get(inf_id, [])
        if not kids:
            continue
        bvd = Counter((loc, d) for loc, _lt, d, _a in kids)
        same = (sum(1 for _l, _t, _d, a in kids if home[a] == home[inf_id]) / len(kids)
                if household_ok and home[inf_id] >= 0 else float("nan"))
        comp.append((int(total[j]), same, max(bvd.values()) / len(kids), len({loc for loc, _lt, _d, _a in kids})))
    if comp:
        arr = np.asarray(comp, dtype=float)
        row["top10_mean_offspring"] = float(arr[:, 0].mean())
        row["top10_mean_same_household_share"] = float(np.nanmean(arr[:, 1])) if household_ok else ""
        row["top10_mean_largest_venue_day_share"] = float(arr[:, 2].mean())
        row["top10_mean_distinct_venues"] = float(arr[:, 3].mean())
    # events
    if "infectious_in_group" in ev_header:
        et = ei = einf = 0
        with open(ev_log) as handle:
            for r in csv.DictReader(handle, delimiter="\t"):
                et += 1
                if float(r["infectious_in_group"]) > 0:
                    einf += 1
                ei += int(r["infected"])
        row["events_total"] = et
        row["events_with_infectious"] = einf
        row["event_infections"] = ei
        row["event_offspring_share"] = float(event.sum() / total.sum()) if total.sum() else ""
    elif ev_venue_days is not None:
        row["events_total"] = len(ev_venue_days)
        row["event_offspring_share"] = float(event.sum() / total.sum()) if total.sum() else ""
    return row, ids, total, event


def _core_task(args):
    arm, rep, run = args
    row, ids, total, event = replicate_core(run)
    return arm, rep, row, ids, total, event


def add_top1(rows_cores):
    """Pooled top 1% of the arm: the round(1% x pooled index cases) largest offspring counts, ties broken by a fixed
    random order. Counts of those infectors by agent type are written per replicate (threshold = smallest included count)."""
    c = ctx()
    sizes = [t.size for _r, _i, t, _e in rows_cores]
    pooled = np.concatenate([t for _r, _i, t, _e in rows_cores])
    if not pooled.size:
        return None
    cut = max(1, int(round(0.01 * pooled.size)))
    owner = np.repeat(np.arange(len(sizes)), sizes)
    pos = np.concatenate([np.arange(n) for n in sizes])
    tie = np.random.default_rng(20261022).random(pooled.size)
    order = np.lexsort((tie, -pooled))[:cut]
    threshold = int(pooled[order].min())
    types = sorted(set(c["atype"].tolist()))
    for r_idx, (row, ids, total, _e) in enumerate(rows_cores):
        sel = ids[pos[order[owner[order] == r_idx]]]
        row["top1pct_threshold_pooled"] = threshold
        row["top1pct_infectors"] = int(sel.size)
        for t in types:
            if t >= 0:
                row[f"top1pct_type{t}"] = int(np.sum(c["atype"][sel] == t))
    return threshold


def export_arms(arms, hist_path, summary_path, procs=4):
    """arms: list of (arm_name, [run dirs]). Writes the histogram and summary files."""
    tasks = [(arm, rep, run) for arm, runs in arms for rep, run in enumerate(runs, start=1)]
    with Pool(procs) as pool:
        done = pool.map(_core_task, tasks, chunksize=2)
    by_arm = defaultdict(list)
    for arm, rep, row, ids, total, event in done:
        row = {"arm": arm, "replicate": rep, **row}
        by_arm[arm].append((row, ids, total, event))
    hist_rows, sum_rows = [], []
    for arm, _runs in arms:
        cores = by_arm[arm]
        add_top1([(r, i, t, e) for r, i, t, e in cores])
        for row, _ids, total, event in cores:
            sum_rows.append(row)
            for (a, e), n in sorted(Counter(zip(total.tolist(), event.tolist())).items()):
                hist_rows.append({"arm": arm, "seed": row["seed"], "replicate": row["replicate"], "offspring_total": a,
                                  "offspring_at_events": e if "event_offspring_share" in row else "", "index_cases": n})
    write_csv(hist_path, hist_rows)
    # one column order for the whole file
    cols = []
    for r in sum_rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(summary_path, "w", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in sum_rows:
            w.writerow({k: r.get(k, "") for k in cols})
    return sum_rows


def n0_arms():
    arms = []
    for r in range(6, 13):
        for f in sorted((RES / f"round{r}" / "state").glob("*.json")):
            d = json.loads(f.read_text())
            if not isinstance(d, dict) or "prefix" not in d:
                continue
            runs = sorted(p.parent for p in (RES / f"round{r}" / d["prefix"]).glob("rep*/trace.tsv"))
            if runs:
                arms.append((f"round{r}:{f.stem}", runs))
    return arms


def pair_dirs():
    out = []
    for name, base in (("round6:r62_A0", RES / "round6/r62/A0"), ("round6:r62_E", RES / "round6/r62/E"),
                       ("round6:r62_P0", RES / "round6/r62/P0"), ("round7:s5_pairs", RES / "round7/r7/s5_pairs"),
                       ("round10:pairs_w1", RES / "round10/r10/pairs_w1"), ("round10:pairs_w2_gate", RES / "round10/r10/pairs_w2")):
        out.append((name, base))
    for d in sorted((RES / "round11/r11").glob("pairs_*")):
        out.append((f"round11:{d.name}", d))
    runs = [(n, sorted(p.parent for p in b.glob("rep*/trace.tsv"))) for n, b in out]
    return [(n, r) for n, r in runs if r]


def repeat_pairs(path, arms):
    from analyze import load_daily as ld
    from analyze_round6 import episode_pairs
    rows = []
    for arm, runs in arms:
        for rep, run in enumerate(runs, start=1):
            if not (run / "episodes.tsv").exists():
                continue
            last_day = len(ld(run / "stdout.txt")) - 1
            prs, _w2, _m, _n = episode_pairs(run, last_day)
            for agent, d1, o1, d2, o2 in prs:
                rows.append({"arm": arm, "seed": run_info(run)["seed"], "replicate": rep, "agent": agent, "first_day": d1,
                             "first_infection_offspring": o1, "second_day": d2, "second_infection_offspring": o2})
    write_csv(path, rows)


def n0():
    arms = n0_arms()
    pairs = pair_dirs()
    arms += pairs
    print(f"N0: {len(arms)} arms, {sum(len(r) for _a, r in arms)} replicates", flush=True)
    export_arms(arms, OUT / "66_n0_replicate_histograms.csv", OUT / "66_n0_replicate_summary.csv")
    repeat_pairs(OUT / "66_n0_repeat_pairs_by_replicate.csv", pairs)


# ---------------------------------------------------------------- N4: thinning draws

N4_WORLDS = [
    ("world1_multiplier_only", "round10", "r10_w1_sh0.32"),
    ("world2b_scene_L10_sh0.58", "round11", "r11_w2_L10_sh0.58"),
    ("world3b_events_M30_rate0.146_paired", "round12", "r12_w3b_M30_rate0.1456"),
    ("world2a_scene_L30_sh0.70", "round11", "r11_w2_L30_sh0.70"),
]
N4_SCHEMES = ("random", "household_infectee", "household_coupled")
N4_RATES = (0.6, 0.3)
N4_DRAWS = 20
SCHEME_CODE = {"random": 1, "household_infectee": 2, "household_coupled": 3}


class Prepared:
    """One replicate parsed once: index cases, their children within 14 days, infected agents."""

    def __init__(self, run):
        rows = a10.read_trace(run)
        self.agents = np.asarray(sorted({a for a, *_ in rows}), dtype=np.int64)
        index, self.day, self.children = [], {}, defaultdict(list)
        for a, inf, loc, lt, d in rows:
            self.day[a] = d
            if inf != UNKNOWN:
                if 1 <= d <= 10:
                    index.append(a)
                self.children[inf].append((loc, lt, d, a))
        self.index_ids = np.asarray(index, dtype=np.int64)
        self.kids = {}
        for a in index:
            lim = self.day[a] + 14
            self.kids[a] = [k for k in self.children.get(a, []) if k[2] <= lim]


def thin_prepared(prep, scheme, rate, rng, home, unique_homes):
    """Same schemes as analyze_round12.thin_replicate, on a prepared replicate."""
    ids = prep.index_ids
    if scheme == "random":
        det = dict(zip(prep.agents.tolist(), (rng.random(prep.agents.size) < rate).tolist()))
        keep = np.asarray([det[int(i)] for i in ids], dtype=bool)
        child_ok = lambda a: det[a]
    elif scheme == "household_coupled":
        hh = dict(zip(unique_homes.tolist(), (rng.random(unique_homes.size) < rate).tolist()))
        keep = np.asarray([hh.get(int(home[i]), False) for i in ids], dtype=bool)
        child_ok = lambda a: hh.get(int(home[a]), False)
    elif scheme == "household_infectee":
        keep = rng.random(ids.size) < rate
        hh = dict(zip(unique_homes.tolist(), (rng.random(unique_homes.size) < rate).tolist()))
        child_ok = lambda a: hh.get(int(home[a]), False)
    else:
        raise ValueError(scheme)
    kept = ids[keep]
    totals = np.zeros(kept.size, dtype=np.int64)
    ck, hh_num, hh_den = {}, 0, 0
    for j, inf in enumerate(kept.tolist()):
        kids = [k for k in prep.kids[inf] if child_ok(k[3])]
        ck[inf] = kids
        totals[j] = len(kids)
        hh_den += len(kids)
        if home[inf] >= 0 and kids:
            hh_num += sum(1 for *_x, a in kids if home[a] == home[inf])
    clusters = []
    for j in np.argsort(totals)[::-1][:10]:
        inf = int(kept[j])
        kids = ck.get(inf, [])
        if not kids:
            continue
        bvd = Counter((loc, d) for loc, _lt, d, _a in kids)
        same = sum(1 for *_x, a in kids if home[inf] >= 0 and home[a] == home[inf]) / len(kids)
        clusters.append((same, max(bvd.values()) / len(kids)))
    return totals, clusters, hh_num, hh_den


def thin_stats(totals, clusters, hh_num, hh_den):
    n = totals.size
    out = {"detected_index_cases": n}
    if n < 2 or totals.sum() == 0:
        return out
    mean = float(totals.mean())
    kmom, kml = mom_k(totals), ml_k(totals)
    z, _s80 = nb_shares(kml, mean)
    out.update({"thinned_R": mean, "k_mom": kmom, "k_ml": kml, "k_ratio": kml / kmom if kmom else "",
                "share_0": float(np.mean(totals == 0)), "nb_zero_at_k_ml": z,
                "observed_minus_nb_zero": float(np.mean(totals == 0)) - z,
                "all_offspring_same_household_share": hh_num / hh_den if hh_den else "",
                "top10_same_household_share": float(np.mean([c[0] for c in clusters])) if clusters else "",
                "top10_largest_venue_day_share": float(np.mean([c[1] for c in clusters])) if clusters else ""})
    return out


def _n4_world(args):
    w_name, rnd, label = args
    _age, _atype, home = a10.agent_table()
    unique_homes = np.unique(home[home >= 0])
    runs, _st = a10.run_dirs(RES / rnd, label)
    preps = [Prepared(r) for r in runs]
    per_rep, pooled = [], []
    for scheme in N4_SCHEMES:
        for rate in N4_RATES:
            for draw in range(1, N4_DRAWS + 1):
                tots, cls, hn, hd = [], [], 0, 0
                for r_idx, prep in enumerate(preps):
                    rng = np.random.default_rng([13, r_idx, SCHEME_CODE[scheme], int(round(rate * 100)), draw])
                    t, c, a, b = thin_prepared(prep, scheme, rate, rng, home, unique_homes)
                    st = thin_stats(t, c, a, b)
                    per_rep.append({"arm": w_name, "scheme": scheme, "rate": rate, "replicate": r_idx + 1, "draw": draw, **st})
                    tots.append(t)
                    cls += c
                    hn += a
                    hd += b
                st = thin_stats(np.concatenate(tots), cls, hn, hd)
                pooled.append({"arm": w_name, "scheme": scheme, "rate": rate, "draw": draw, **st})
        print(f"N4 {w_name} {scheme} done", flush=True)
    return per_rep, pooled


def n4(procs=4):
    with Pool(min(procs, len(N4_WORLDS))) as pool:
        res = pool.map(_n4_world, N4_WORLDS)
    per = [r for p, _q in res for r in p]
    pooled = [r for _p, q in res for r in q]
    for path, rows in ((OUT / "66_n4_thinning_draws.csv", per), (OUT / "66_n4_thinning_draws_pooled.csv", pooled)):
        cols = []
        for r in rows:
            for k in r:
                if k not in cols:
                    cols.append(k)
        with open(path, "w", newline="") as handle:
            w = csv.DictWriter(handle, fieldnames=cols, lineterminator="\n")
            w.writeheader()
            for r in rows:
                w.writerow({k: r.get(k, "") for k in cols})
        print(f"wrote {path.name} ({len(rows)} rows)")


# ---------------------------------------------------------------- cells (N1, N2, N3): pooled statistics with replicate bootstrap

BOOT = 1000
WORLDS = ("w1", "w2b", "w2a", "w3b")
WORLD_NAMES = {"w1": "world1_multiplier_only", "w2b": "world2b_scene_L10_sh0.58", "w2a": "world2a_scene_L30_sh0.70",
               "w3b": "world3b_events_M30_rate0.146"}
R12_STATES = {"w1": ("round10", "r10_w1_sh0.32"), "w2a": ("round11", "r11_w2_L30_sh0.70"),
              "w2b": ("round11", "r11_w2_L10_sh0.58"), "w3b": ("round12", "r12_w3b_M30_rate0.1456")}


def nb_shares_full(mean, k):
    from r6stats import nb_shares as _nb
    return _nb(mean, k)


def pooled_stats(cores):
    """cores: list of (row, ids, total, event) of one cell. Point statistics on the pooled index cases."""
    total = np.concatenate([c[2] for c in cores])
    event = np.concatenate([c[3] for c in cores])
    out = {}
    mean = float(total.mean())
    kmom, kml = mom_k(total), ml_k(total)
    z, nb80 = nb_shares(kml, mean)
    s0 = float(np.mean(total == 0))
    nb_pub = nb_shares_full(0.88, 0.27)
    nb_own = nb_shares_full(mean, kml)
    out.update({"share_1_to_5": float(np.mean((total >= 1) & (total <= 5))), "share_above_5": float(np.mean(total > 5)),
                "share_at_least_20": float(np.mean(total >= 20)), "share_at_least_50": float(np.mean(total >= 50)),
                "maximum_offspring": int(total.max()), "p99_offspring": float(np.quantile(total, 0.99)),
                "nb_own_share_above_5": nb_own["share_above_5"], "nb_published_zero": nb_pub["share_0"],
                "nb_published_above_5": nb_pub["share_above_5"],
                "share_above_5_over_nb_own": float(np.mean(total > 5)) / nb_own["share_above_5"] if nb_own["share_above_5"] else "",
                "index_cases": int(total.size), "early_R": mean, "k_mom": kmom, "k_ml": kml, "k_ml_over_k_mom": kml / kmom,
                "share_0": s0, "nb_zero_at_k_ml": z, "observed_minus_nb_zero": s0 - z,
                "share_causing_80pct": lorenz_shares(total).get("share_of_index_cases_causing_80pct"),
                "nb_80pct_at_k_ml": nb80})
    rows = [c[0] for c in cores]
    inf = np.asarray([r["infections_d1_28"] for r in rows], dtype=float)
    for key in ("infections_share_home", "infections_share_school_and_work", "infections_share_high_L_types", "infections_share_hospital"):
        out[key] = float(np.sum([r[key] * n for r, n in zip(rows, inf)]) / inf.sum())
    num = sum(r["household_secondary_attack_numerator"] for r in rows)
    den = sum(r["household_secondary_attack_denominator"] for r in rows)
    out["household_secondary_attack_rate"] = num / den
    for key in ("top10_mean_offspring", "top10_mean_same_household_share", "top10_mean_largest_venue_day_share", "top10_mean_distinct_venues"):
        out[key] = float(np.mean([r[key] for r in rows]))
    out["largest_offspring_mean_over_replicates"] = float(np.mean([r["largest_offspring"] for r in rows]))
    out["day28_mean"] = float(np.mean([r["day28_cumulative_infections"] for r in rows]))
    out["day28_vs_6211.25"] = out["day28_mean"] / 6211.25 - 1
    if "event_offspring_share" in rows[0] and rows[0]["event_offspring_share"] != "":
        out["event_offspring_share"] = float(event.sum() / total.sum())
    return out


def bootstrap_cell(cores, draws=BOOT, seed=20261022):
    """Replicate bootstrap (5th and 95th percentile) of the pooled statistics."""
    rng = np.random.default_rng(seed)
    n = len(cores)
    cols = defaultdict(list)
    for _ in range(draws):
        pick = rng.integers(0, n, size=n)
        total = np.concatenate([cores[i][2] for i in pick])
        rows = [cores[i][0] for i in pick]
        mean = float(total.mean())
        kmom, kml = mom_k(total), ml_k(total)
        z, _ = nb_shares(kml, mean)
        s0 = float(np.mean(total == 0))
        cols["early_R"].append(mean)
        cols["k_mom"].append(kmom)
        cols["k_ml"].append(kml)
        cols["k_ml_over_k_mom"].append(kml / kmom)
        cols["share_0"].append(s0)
        cols["share_above_5"].append(float(np.mean(total > 5)))
        cols["share_1_to_5"].append(float(np.mean((total >= 1) & (total <= 5))))
        cols["observed_minus_nb_zero"].append(s0 - z)
        cols["share_causing_80pct"].append(lorenz_shares(total).get("share_of_index_cases_causing_80pct"))
        inf = np.asarray([r["infections_d1_28"] for r in rows], dtype=float)
        cols["infections_share_home"].append(float(np.sum([r["infections_share_home"] * m for r, m in zip(rows, inf)]) / inf.sum()))
        cols["household_secondary_attack_rate"].append(sum(r["household_secondary_attack_numerator"] for r in rows)
                                                       / sum(r["household_secondary_attack_denominator"] for r in rows))
        for key in ("top10_mean_same_household_share", "top10_mean_largest_venue_day_share"):
            cols[key].append(float(np.mean([r[key] for r in rows])))
    out = {}
    for key, vals in cols.items():
        v = np.asarray([x for x in vals if x is not None and np.isfinite(x)], dtype=float)
        out[f"{key}_low"], out[f"{key}_high"] = float(np.quantile(v, 0.05)), float(np.quantile(v, 0.95))
        out[f"{key}_boot_sd"] = float(v.std(ddof=1))
    return out


def cell_dirs(base, prefix):
    return sorted(p.parent for p in (RES / base / prefix).glob("rep*/trace.tsv"))


def cell_registry(include_sens=True):
    """All cells with a state file: (cell name, world, set, kind, run dirs, coefficient, calibration state)."""
    cells = []
    for w in WORLDS:
        rnd, label = R12_STATES[w]
        st = json.loads((RES / rnd / "state" / f"{label}.json").read_text())
        cells.append({"cell": f"{w}:s77_cal", "world": w, "set": "s77", "kind": "round12_calibrated", "dirs": cell_dirs(rnd, st["prefix"]),
                      "k": st["k"], "state": st})
    r6 = json.loads((RES / "round6/state/r67_M30.json").read_text())
    cells.append({"cell": "w3b:s68_cal", "world": "w3b", "set": "s68", "kind": "round6_calibrated", "dirs": cell_dirs("round6", r6["prefix"]),
                  "k": r6["k"], "state": r6})
    st_dir = RES / "round13" / "state"
    for f in sorted(st_dir.glob("r13_*.json")):
        d = json.loads(f.read_text())
        if "prefix" not in d:
            continue
        stem = f.stem[len("r13_"):]
        for w in WORLDS:
            if not stem.endswith("_" + w):
                continue
            tag = stem[: -len(w) - 1]
            if tag.startswith("frozen_"):
                kind, setname = "frozen", tag[len("frozen_"):]
            elif tag.startswith("sens_"):
                kind, setname = f"sens_x{tag[len('sens_'):]}", "s77"
            else:
                kind, setname = "calibrated", tag
            if kind.startswith("sens") and not include_sens:
                continue
            dirs = cell_dirs("round13", d["prefix"])
            if dirs and (d.get("matched") is not False or kind != "calibrated"):
                cells.append({"cell": f"{w}:{setname}_{kind}" if kind != "calibrated" else f"{w}:{setname}_cal", "world": w, "set": setname,
                              "kind": kind, "dirs": dirs, "k": d["k"], "state": d})
    return cells


def cells_export(tag="n1", select=None, cells=None, outdir=None):
    outdir = outdir or OUT
    cells = cells if cells is not None else [c for c in cell_registry() if (select is None or select(c))]
    arms = [(c["cell"], c["dirs"]) for c in cells]
    sum_rows = export_arms(arms, outdir / f"{tag}_replicate_histograms.csv", outdir / f"{tag}_replicate_summary.csv")
    by = defaultdict(list)
    # recompute cores for pooled statistics (cheap)
    out, cal_rows = [], []
    for c in cells:
        cores = [replicate_core(r) for r in c["dirs"]]
        st = pooled_stats(cores)
        bt = bootstrap_cell(cores)
        row = {"cell": c["cell"], "world": c["world"], "seed_set": c["set"], "kind": c["kind"], "replicates": len(c["dirs"]),
               "background_coefficient": c["k"], "first_seed": run_info(c["dirs"][0])["seed"], **st, **bt}
        out.append(row)
        for i, pt in enumerate(c["state"].get("points", []), start=1):
            cal_rows.append({"cell": c["cell"], "iteration": i, "coefficient": pt["k"], "day28_mean": pt["day28"],
                             "replicates_used": len(pt.get("values", [])), "pilot": bool(pt.get("pilot")),
                             "chosen": abs(pt["k"] - c["k"]) < 1e-12 * max(1, abs(c["k"])) and not pt.get("pilot")})
    cols = []
    for r in out:
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(outdir / f"{tag}_cells_summary.csv", "w", newline="") as handle:
        w = csv.DictWriter(handle, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in out:
            w.writerow({k: r.get(k, "") for k in cols})
    write_csv(outdir / f"{tag}_calibration_log.csv", cal_rows)
    for r in out:
        print(f"{r['cell']:22s} k={r['background_coefficient']:.6g} day28={r['day28_mean']:.0f} ({r['day28_vs_6211.25']:+.1%}) "
              f"R={r['early_R']:.3f} k_ml={r['k_ml']:.3f} ({r['k_ml_low']:.3f},{r['k_ml_high']:.3f}) k_mom={r['k_mom']:.3f} "
              f"ratio={r['k_ml_over_k_mom']:.2f} zero={r['share_0']:.3f} gap={r['observed_minus_nb_zero']*100:+.2f} "
              f"s80={r['share_causing_80pct']*100:.1f} home={r['infections_share_home']*100:.1f}", flush=True)
    return out


if __name__ == "__main__":
    {"n0": n0, "n4": n4, "n1": lambda: cells_export("66_n1", lambda c: c["kind"] in ("round12_calibrated", "round6_calibrated", "calibrated", "frozen") and c["set"] in ("s77", "s78", "s79", "s68")),
     "n2": lambda: cells_export("66_n2", lambda c: c["kind"].startswith("sens") or c["kind"] == "round12_calibrated"),
     "n5": lambda: cells_export("66_n5", lambda c: c["set"] == "n5" or c["kind"] == "round12_calibrated"),
     "n3": lambda: cells_export("66_n3", lambda c: c["set"].startswith("n3final") or c["kind"] == "round12_calibrated")}[sys.argv[1]]()
