#!/usr/bin/env python3
"""Note 73 round 15 analysis (pure Python standard library so it runs inside the standard sandbox):
- Run C: infection-level exports (74_c_infections_<world>_reps01_04.csv, reps05_08.csv, reps09_12.csv, each < 2 MB),
  74_c_replicate_summary.csv, 74_c_cells_summary.csv, 74_c_parent_classes.csv, and 74_c_subgroups.csv.
- Run D: density-exponent cells (alpha = 1.0 B1 reference, alpha = 0.5, alpha = 0.0) across worlds 1, 2b, 3b:
  74_d_cells_summary.csv, 74_d_replicate_summary.csv, 74_d_replicate_histograms.csv, and 74_d_calibration_log.csv.

  python3 superspreader/study/analyze_round15.py all
"""
import csv
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = HERE.parents[1]
RES = HERE / "results"
R14 = RES / "round14"
R15 = RES / "round15"

UNKNOWN = 4294967295
STEPS = 144
SCHOOL_WORK = {3, 33, 4, 13, 44}
HIGH = {5, 6, 9, 10}
HOSPITAL = {12}
WORLDS = ("w1", "w2b", "w3b")
BOOT_DRAWS = 1000
BOOT_SEED = 20261023

_AGENTS_CACHE = None


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    keys, seen = [], set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                keys.append(key)

    def clean(value):
        if isinstance(value, float):
            return "" if math.isnan(value) else f"{value:.6g}"
        return "" if value is None else value

    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows([{key: clean(row.get(key, "")) for key in keys} for row in rows])
    print(f"wrote {path.name} ({path.stat().st_size} bytes)", flush=True)


def agent_context():
    """Return (age, atype, home, hh_size) lists/Counters for all 178,746 agents from agents2.json."""
    global _AGENTS_CACHE
    if _AGENTS_CACHE is not None:
        return _AGENTS_CACHE
    cache_path = R15 / "state" / "agents_meta.json"
    if cache_path.exists():
        d = json.loads(cache_path.read_text())
        hh_size = Counter(h for h in d["home"] if h >= 0)
        _AGENTS_CACHE = (d["age"], d["atype"], d["home"], hh_size)
        return _AGENTS_CACHE
    people = json.loads((ROOT / "inputRealExample" / "agents2.json").read_text())["people"]
    age = [0] * len(people)
    atype = [0] * len(people)
    home = [-1] * len(people)
    ids = {}
    for i, p in enumerate(people):
        age[i] = int(p.get("age", -1))
        atype[i] = int(p.get("typeID", p.get("type", -1)))
        for l in p["locations"]:
            if l["typeID"] == 2:
                loc_id = l["locID"]
                if loc_id not in ids:
                    ids[loc_id] = len(ids)
                home[i] = ids[loc_id]
                break
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps({"age": age, "atype": atype, "home": home}))
    hh_size = Counter(h for h in home if h >= 0)
    _AGENTS_CACHE = (age, atype, home, hh_size)
    return _AGENTS_CACHE


# ---------------------------------------------------------------- Pure-Python NB & correlation helpers

def log_nbinom_pmf(j, k, p):
    return math.lgamma(j + k) - math.lgamma(k) - math.lgamma(j + 1) + k * math.log(p) + j * math.log(1.0 - p)


def nb_pmf(mu, k, j):
    p = k / (k + mu)
    return math.exp(log_nbinom_pmf(j, k, p))


def nb_zero(mu, k):
    if k is None or not math.isfinite(k):
        return math.exp(-mu)
    return (k / (k + mu)) ** k


def nb_sf_at_least(mu, k, threshold):
    if threshold <= 0:
        return 1.0
    p = k / (k + mu)
    log_q = math.log(1.0 - p)
    logpmf = log_nbinom_pmf(threshold, k, p)
    logs = [logpmf]
    j = threshold
    while j < threshold + 200000:
        j += 1
        logpmf += math.log(j - 1 + k) - math.log(j) + log_q
        logs.append(logpmf)
        if logpmf < logs[0] - 45 and logpmf < max(logs) - 45:
            break
    peak = max(logs)
    return math.exp(peak) * sum(math.exp(item - peak) for item in logs)


def nb_80pct_share(k, mean):
    """Negative-binomial expected share of index cases causing 80% of offspring."""
    if k is None or not math.isfinite(k) or mean <= 0:
        return float("nan")
    p = k / (k + mean)
    probs, j, cum = [], 0, 0.0
    while j < 50000:
        pr = math.exp(log_nbinom_pmf(j, k, p))
        probs.append((j, pr))
        cum += pr
        if j > mean + 50 and (1.0 - cum) < 1e-10:
            break
        j += 1
    # Accumulate from largest j downward until 80% of mean is reached
    target_off = 0.80 * mean
    acc_off = 0.0
    acc_pop = 0.0
    for val, pr in reversed(probs):
        if val <= 0:
            break
        contrib = val * pr
        if acc_off + contrib >= target_off:
            frac = (target_off - acc_off) / contrib if contrib > 0 else 0.0
            acc_pop += frac * pr
            break
        acc_off += contrib
        acc_pop += pr
    return acc_pop


def mom_k_from_counter(counts, n_total=None, sum_total=None):
    n = n_total if n_total is not None else sum(counts.values())
    if n < 2:
        return float("nan")
    s1 = sum_total if sum_total is not None else sum(j * c for j, c in counts.items())
    mean = s1 / n
    if mean <= 0:
        return float("nan")
    s2 = sum(j * j * c for j, c in counts.items())
    var = (s2 - n * mean * mean) / (n - 1)
    if var <= mean:
        return math.inf
    return (mean * mean) / (var - mean)


def nb_loglik_arrays(offspring, number, mu, k):
    p = k / (k + mu)
    log_p = math.log(p)
    log_q = math.log(1.0 - p)
    log_k = math.lgamma(k)
    total = 0.0
    for j, c in zip(offspring, number):
        total += c * (math.lgamma(j + k) - log_k - math.lgamma(j + 1) + k * log_p + j * log_q)
    return total


def ml_k_from_counter(counts, n_total=None, sum_total=None):
    n = n_total if n_total is not None else sum(counts.values())
    if n < 2:
        return float("nan")
    s1 = sum_total if sum_total is not None else sum(j * c for j, c in counts.items())
    mu = s1 / n
    if mu <= 0:
        return float("nan")
    offspring = list(counts.keys())
    number = [counts[j] for j in offspring]
    ratio = 200.0 / 1e-3
    grid = [1e-3 * (ratio ** (i / 59.0)) for i in range(60)]
    scores = [nb_loglik_arrays(offspring, number, mu, k) for k in grid]
    best = max(range(len(scores)), key=scores.__getitem__)
    if best == len(grid) - 1:
        return math.inf
    lo = grid[max(best - 1, 0)]
    hi = grid[min(best + 1, len(grid) - 1)]
    for _ in range(45):
        a = math.exp((2.0 * math.log(lo) + math.log(hi)) / 3.0)
        b = math.exp((math.log(lo) + 2.0 * math.log(hi)) / 3.0)
        if nb_loglik_arrays(offspring, number, mu, a) < nb_loglik_arrays(offspring, number, mu, b):
            lo = a
        else:
            hi = b
    return math.exp(0.5 * (math.log(lo) + math.log(hi)))


def lorenz_from_list(values):
    n = len(values)
    if n == 0:
        return {}
    s = sorted(values, reverse=True)
    tot = sum(s)
    if tot <= 0:
        return {"share_of_index_cases_causing_80pct": float("nan"),
                "share_of_index_cases_causing_50pct": float("nan"),
                "top_1pct_share_of_offspring": 0.0,
                "top_5pct_share_of_offspring": 0.0}
    target80 = 0.80 * tot
    target50 = 0.50 * tot
    acc = 0.0
    i80 = i50 = None
    for idx, v in enumerate(s, start=1):
        acc_next = acc + v
        if i50 is None and acc_next >= target50:
            i50 = (idx - 1 + (target50 - acc) / v) / n if v > 0 else idx / n
        if i80 is None and acc_next >= target80:
            i80 = (idx - 1 + (target80 - acc) / v) / n if v > 0 else idx / n
            break
        acc = acc_next
    k1 = max(1, int(round(0.01 * n)))
    k5 = max(1, int(round(0.05 * n)))
    return {
        "share_of_index_cases_causing_80pct": i80 if i80 is not None else 1.0,
        "share_of_index_cases_causing_50pct": i50 if i50 is not None else 1.0,
        "top_1pct_share_of_offspring": sum(s[:k1]) / tot,
        "top_5pct_share_of_offspring": sum(s[:k5]) / tot,
    }


def quantile_linear(sorted_vals, q):
    """Match numpy's default linear quantile on a sorted list."""
    n = len(sorted_vals)
    if n == 0:
        return float("nan")
    if n == 1:
        return float(sorted_vals[0])
    pos = q * (n - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return float(sorted_vals[lo])
    frac = pos - lo
    return float(sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac)


def pearson(x, y):
    n = len(x)
    if n < 2:
        return float("nan")
    mx = sum(x) / n
    my = sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx <= 0 or syy <= 0:
        return float("nan")
    return sxy / math.sqrt(sxx * syy)


def _ranks(vals):
    n = len(vals)
    order = sorted(range(n), key=vals.__getitem__)
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        v = vals[order[i]]
        while j + 1 < n and vals[order[j + 1]] == v:
            j += 1
        avg_rank = 0.5 * (i + j) + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg_rank
        i = j + 1
    return ranks


def spearman(x, y):
    if len(x) < 2:
        return float("nan")
    return pearson(_ranks(x), _ranks(y))


def poisson_q99(lam):
    """Smallest integer k such that Poisson(lam) CDF >= 0.99."""
    if lam <= 0:
        return 0
    p = math.exp(-lam)
    cdf = p
    k = 0
    while cdf < 0.99 and k < 1000:
        k += 1
        p *= lam / k
        cdf += p
    return k


def sibling_icc(families):
    """Given a list of child-offspring lists for parents with >= 2 children, return
    (pairwise_pearson, anova_icc, n_families, n_children)."""
    valid = [f for f in families if len(f) >= 2]
    if not valid:
        return float("nan"), float("nan"), 0, 0
    # 1. Pairwise correlation over all ordered pairs (c1, c2) in the same family (weighted equally per pair or per family)
    # Using sufficient statistics per family: sum_i != j x_i x_j = (sum x)^2 - sum(x^2)
    n_pairs = 0
    sum_x = 0.0
    sum_x2 = 0.0
    sum_xy = 0.0
    for fam in valid:
        k = len(fam)
        s1 = sum(fam)
        s2 = sum(v * v for v in fam)
        n_pairs += k * (k - 1)
        sum_x += (k - 1) * s1
        sum_x2 += (k - 1) * s2
        sum_xy += s1 * s1 - s2
    if n_pairs > 0:
        mean_p = sum_x / n_pairs
        var_p = (sum_x2 / n_pairs) - mean_p * mean_p
        cov_p = (sum_xy / n_pairs) - mean_p * mean_p
        pair_r = cov_p / var_p if var_p > 0 else float("nan")
    else:
        pair_r = float("nan")

    # 2. One-way random-effects ANOVA ICC
    K = len(valid)
    N = sum(len(f) for f in valid)
    grand_mean = sum(sum(f) for f in valid) / N
    ss_between = sum(len(f) * ((sum(f) / len(f)) - grand_mean) ** 2 for f in valid)
    ss_within = sum(sum((v - (sum(f) / len(f))) ** 2 for v in f) for f in valid)
    ms_b = ss_between / (K - 1) if K > 1 else 0.0
    ms_w = ss_within / (N - K) if N > K else 0.0
    k0 = (N - sum(len(f) ** 2 for f in valid) / N) / (K - 1) if K > 1 else 1.0
    denom = ms_b + (k0 - 1.0) * ms_w
    anova_r = (ms_b - ms_w) / denom if denom > 0 else float("nan")
    return pair_r, anova_r, K, N


# ---------------------------------------------------------------- Run C analysis

def read_trace_rows(trace_path):
    """Return list of dicts for each row in trace.tsv."""
    out = []
    with open(trace_path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        col = {name: i for i, name in enumerate(header)}
        for line in handle:
            p = line.rstrip("\n").split("\t")
            ts = int(p[col["timestamp"]])
            out.append({
                "agent": int(p[col["agent"]]),
                "infector": int(p[col["infector"]]),
                "location": int(p[col["location"]]),
                "locType": int(p[col["locType"]]),
                "timestamp": ts,
                "day": ts // STEPS,
                "infectedCount": int(p[col["infectedCount"]]),
                "occupancy": int(p[col["occupancy"]]),
            })
    return out


def load_event_pairs(path):
    """Return set of (agent, day) and set of agent from events.tsv.infections."""
    pairs = set()
    agents = set()
    if not path.exists():
        return pairs, agents
    with open(path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        c_day = header.index("day")
        c_ag = header.index("agent")
        for line in handle:
            p = line.rstrip("\n").split("\t")
            if len(p) > max(c_day, c_ag):
                d, a = int(p[c_day]), int(p[c_ag])
                pairs.add((a, d))
                agents.add(a)
    return pairs, agents


def load_hvi_flags(path):
    if not path.exists():
        return None
    flags = []
    with open(path) as handle:
        next(handle)
        for line in handle:
            flags.append(1 if line.rstrip("\n").split(",")[4] == "1" else 0)
    return flags


def build_runc_replicate(world, rep_idx, run4_dir, run6_dir, age, atype, home):
    """Build the infection records up to day 28 and offspring counts up to day 42 for one replicate."""
    cmd = json.loads((run6_dir / "command.json").read_text())
    seed = int(cmd[cmd.index("--seed") + 1])

    rows4 = read_trace_rows(run4_dir / "trace.tsv")
    rows6 = read_trace_rows(run6_dir / "trace.tsv")
    ev4_pairs, ev4_agents = load_event_pairs(run4_dir / "events.tsv.infections")
    ev6_pairs, ev6_agents = load_event_pairs(run6_dir / "events.tsv.infections")
    hvi = load_hvi_flags(run6_dir / "hvi.csv") if world == "w2b" else None

    # Check raw 6-week trace index histogram vs 4-week trace index histogram (to document exact difference from reinfection overwrites)
    def trace_only_hist(t_rows, ev_ag):
        day_m = {}
        children_m = defaultdict(list)
        for r in t_rows:
            a, inf, d = r["agent"], r["infector"], r["day"]
            day_m[a] = d
            if inf != UNKNOWN:
                children_m[inf].append((d, a))
        known_m = {a for kids in children_m.values() for _d, a in kids}
        cnt = Counter()
        for a, d in day_m.items():
            if a not in known_m or not (1 <= d <= 10):
                continue
            n = e = 0
            for cd, ca in children_m.get(a, ()):
                if cd <= d + 14:
                    n += 1
                    if ca in ev_ag:
                        e += 1
            cnt[(n, e if world == "w3b" else 0)] += 1
        return cnt

    hist4_raw = trace_only_hist(rows4, ev4_agents)
    hist6_raw = trace_only_hist(rows6, ev6_agents)
    raw6_hist_diff_cases = sum(abs(hist4_raw[k] - hist6_raw[k]) for k in set(hist4_raw) | set(hist6_raw)) // 2

    # Construct the complete infection timeline (days 0..41):
    # - Days 0..27: locked to rows4 (the exact end-of-day-27 state used in Round 14's 69_b_replicate_histograms.csv).
    # - Days 28..41: all new infection events occurring on days 28..41 from episodes.tsv, events.tsv.infections, and rows6.
    by_agent_d27 = {r["agent"]: r for r in rows4}

    # Collect post-day-27 infection events (day >= 28)
    post27_events = {}  # (agent, day) -> (infector, location, locType, is_event)
    ep_path = run6_dir / "episodes.tsv"
    if ep_path.exists():
        with open(ep_path) as handle:
            header = handle.readline().rstrip("\n").split("\t")
            col = {name: i for i, name in enumerate(header)}
            for line in handle:
                p = line.rstrip("\n").split("\t")
                ts = int(p[col["timestamp"]])
                d = ts // STEPS
                if d >= 28:
                    ag = int(p[col["agent"]])
                    inf = int(p[col["infector"]])
                    loc = int(p[col["location"]])
                    lt = int(p[col["locType"]])
                    post27_events[(ag, d)] = (inf, loc, lt, (ag, d) in ev6_pairs)
    # Also add closed-group event infections on days >= 28 (since writeEpisodes() runs before runGroupEvents())
    if (run6_dir / "events.tsv.infections").exists():
        with open(run6_dir / "events.tsv.infections") as handle:
            header = handle.readline().rstrip("\n").split("\t")
            c_d, c_a, c_l, c_i = header.index("day"), header.index("agent"), header.index("location_index"), header.index("infector")
            for line in handle:
                p = line.rstrip("\n").split("\t")
                d = int(p[c_d])
                if d >= 28:
                    ag, loc, inf = int(p[c_a]), int(p[c_l]), int(p[c_i])
                    post27_events[(ag, d)] = (inf, loc, 8, True)
    # Also ensure any row in rows6 with day >= 28 is included
    for r in rows6:
        d = r["day"]
        if d >= 28:
            ag = r["agent"]
            if (ag, d) not in post27_events:
                post27_events[(ag, d)] = (r["infector"], r["location"], r["locType"], (ag, d) in ev6_pairs)

    # Children map across all 42 days (days 0..27 from rows4 + days 28..41 from post27_events)
    children_all = defaultdict(list)  # infector -> list of (child_day, child_agent, is_event)
    for r in rows4:
        if r["infector"] != UNKNOWN:
            children_all[r["infector"]].append((r["day"], r["agent"], r["agent"] in ev4_agents))
    for (ag, d), (inf, _loc, _lt, is_ev) in sorted(post27_events.items()):
        if inf != UNKNOWN:
            children_all[inf].append((d, ag, is_ev))

    # Build the exported rows for infections up to day 28:
    # All rows from rows4 (days 0..27) plus first-time infections on day 28 (so agent_id is unique in the export)
    export_records = []
    for r in rows4:
        export_records.append({
            "agent": r["agent"],
            "infector": r["infector"],
            "day": r["day"],
            "location": r["location"],
            "locType": r["locType"],
            "event_flag": 1 if (world == "w3b" and r["agent"] in ev4_agents) else 0,
        })
    for r in rows6:
        if r["day"] == 28 and r["agent"] not in by_agent_d27:
            export_records.append({
                "agent": r["agent"],
                "infector": r["infector"],
                "day": 28,
                "location": r["location"],
                "locType": r["locType"],
                "event_flag": 1 if (world == "w3b" and (r["agent"], 28) in ev6_pairs) else 0,
            })
    export_records.sort(key=lambda x: x["agent"])

    arm_name = f"{world}:B1"
    inf_rows = []
    by_agent_export = {}
    for rec in export_records:
        ag = rec["agent"]
        inf = rec["infector"]
        d = rec["day"]
        loc = rec["location"]
        lt = rec["locType"]
        kids = children_all.get(ag, ())
        off_14d = sum(1 for cd, _ca, _ev in kids if cd <= d + 14)
        off_tot = len(kids)
        same_hh = 1 if (inf != UNKNOWN and home[ag] >= 0 and home[ag] == home[inf]) else 0
        row = {
            "arm": arm_name,
            "seed": seed,
            "replicate": rep_idx,
            "agent_id": ag,
            "infector_id": "" if inf == UNKNOWN else inf,
            "infection_day": d,
            "place_type": lt,
            "location_id": loc,
            "venue_day_id": "" if inf == UNKNOWN else f"{loc}_{d}",
            "same_household_as_infector": same_hh,
            "event_flag": rec["event_flag"],
            "offspring_14d": off_14d,
            "offspring_total": off_tot,
            "agent_type": atype[ag],
            "agent_class_flag": hvi[ag] if hvi is not None else "",
        }
        inf_rows.append(row)
        by_agent_export[ag] = row

    return inf_rows, by_agent_export, hist4_raw, raw6_hist_diff_cases


def compute_runc_stats_for_subset(pairs):
    """Given a list of (parent_row, child_row, parent_poisson_q99) tuples, compute correlation & superspreader-pair stats."""
    n = len(pairs)
    if n == 0:
        return {
            "pairs": 0, "pearson": float("nan"), "spearman": float("nan"),
            "ss_parent_pairs": 0, "ss_child_pairs": 0, "ss_child_share": float("nan"),
            "ss_both_observed": 0, "ss_both_expected": float("nan"), "ss_ratio_obs_over_exp": float("nan"),
        }
    px = [p["offspring_14d"] for p, _c, _q in pairs]
    cy = [c["offspring_14d"] for _p, c, _q in pairs]
    q99 = pairs[0][2]
    ss_p = sum(1 for x in px if x > q99)
    ss_c = sum(1 for y in cy if y > q99)
    ss_both = sum(1 for x, y in zip(px, cy) if x > q99 and y > q99)
    p_child = ss_c / n
    exp_both = ss_p * p_child
    ratio = (ss_both / exp_both) if exp_both > 0 else float("nan")
    return {
        "pairs": n,
        "pearson": pearson(px, cy),
        "spearman": spearman(px, cy),
        "ss_parent_pairs": ss_p,
        "ss_child_pairs": ss_c,
        "ss_child_share": p_child,
        "ss_both_observed": ss_both,
        "ss_both_expected": exp_both,
        "ss_ratio_obs_over_exp": ratio,
    }


def run_c_analysis():
    age, atype, home, _hh_size = agent_context()

    # Load 69_b_replicate_histograms.csv to verify 100% exact reproduction
    ref_hist = defaultdict(Counter)
    with open(OUT / "69_b_replicate_histograms.csv") as handle:
        for r in csv.DictReader(handle):
            if r["arm"].endswith(":B1"):
                ev_c = int(r["offspring_at_events"]) if r["offspring_at_events"] != "" else 0
                ref_hist[(r["arm"], int(r["replicate"]))][(int(r["offspring_total"]), ev_c)] = int(r["index_cases"])

    rep_summary_rows = []
    cell_summary_rows = []
    parent_class_rows = []
    subgroup_rows = []

    for world in WORLDS:
        arm_name = f"{world}:B1"
        r14_st = json.loads((R14 / "state" / f"r14_b1final_{world}.json").read_text())
        r15_st = json.loads((R15 / "state" / f"r15_c_{world}.json").read_text())
        dirs4 = sorted(p.parent for p in (R14 / r14_st["prefix"]).glob("rep*/trace.tsv"))
        dirs6 = sorted(p.parent for p in (R15 / r15_st["prefix"]).glob("rep*/trace.tsv"))

        world_inf_rows_by_rep = []
        rep_data = []

        for rep_idx, (d4, d6) in enumerate(zip(dirs4, dirs6), start=1):
            inf_rows, by_agent, hist4, raw6_diff = build_runc_replicate(world, rep_idx, d4, d6, age, atype, home)
            world_inf_rows_by_rep.append((rep_idx, inf_rows))

            # Verify exact match with 69_b_replicate_histograms.csv
            parents = [r for r in inf_rows if r["infector_id"] != "" and 1 <= r["infection_day"] <= 10]
            # Check histogram from exported parent offspring_14d
            exp_hist = Counter(r["offspring_14d"] for r in parents)
            ref_tot_hist = Counter()
            for (tot_k, _ev_k), cnt in ref_hist[(arm_name, rep_idx)].items():
                ref_tot_hist[tot_k] += cnt
            exact_hist_match = (exp_hist == ref_tot_hist)

            # Children of parents:
            # Primary: 14-day children (child_day <= parent_day + 14)
            # Secondary check: all children in export (child_day <= 28)
            parent_map = {r["agent_id"]: r for r in parents}
            pairs_14d = []
            pairs_all28 = []
            children_by_parent = defaultdict(list)
            for r in inf_rows:
                inf_id = r["infector_id"]
                if inf_id != "" and inf_id in parent_map:
                    par = parent_map[inf_id]
                    pairs_all28.append((par, r))
                    if r["infection_day"] <= par["infection_day"] + 14:
                        pairs_14d.append((par, r))
                        children_by_parent[par["agent_id"]].append(r)

            # Day-matched mean offspring_14d of all infections occurring on day d in this replicate
            by_day_off = defaultdict(list)
            for r in inf_rows:
                if r["infector_id"] != "":
                    by_day_off[r["infection_day"]].append(r["offspring_14d"])
            day_mean = {d: sum(vals) / len(vals) for d, vals in by_day_off.items() if vals}

            # Sibling counts:
            # (a) For each child of an index case: siblings = parent["offspring_14d"] - 1
            child_sibs = [par["offspring_14d"] - 1 for par, _c in pairs_14d]
            # (b) For each index case itself: other offspring of its infector (in inf_rows)
            all_children_of_infector = defaultdict(list)
            for r in inf_rows:
                if r["infector_id"] != "":
                    all_children_of_infector[r["infector_id"]].append(r)
            idx_sibs_14d = []
            idx_sibs_all = []
            for par in parents:
                inf_id = par["infector_id"]
                inf_row = by_agent.get(inf_id)
                inf_day = inf_row["infection_day"] if inf_row is not None else 0
                kids_all = all_children_of_infector.get(inf_id, [])
                kids_14 = [k for k in kids_all if k["infection_day"] <= inf_day + 14]
                idx_sibs_all.append(max(len(kids_all) - 1, 0))
                idx_sibs_14d.append(max(len(kids_14) - 1, 0))

            rep_data.append({
                "rep_idx": rep_idx,
                "seed": inf_rows[0]["seed"],
                "day28": r15_st["values_day28"][rep_idx - 1],
                "day42": r15_st["values_day42"][rep_idx - 1],
                "exact_hist_match": exact_hist_match,
                "raw6_hist_diff_cases": raw6_diff,
                "inf_rows": inf_rows,
                "parents": parents,
                "pairs_14d": pairs_14d,
                "pairs_all28": pairs_all28,
                "children_by_parent": children_by_parent,
                "day_mean": day_mean,
                "child_sibs": child_sibs,
                "idx_sibs_14d": idx_sibs_14d,
                "idx_sibs_all": idx_sibs_all,
            })

        # Write the 3 blocks of 4 replicates (each < 2 MB)
        for b_start, b_end in ((1, 4), (5, 8), (9, 12)):
            block_rows = [r for rep_i, rows_i in world_inf_rows_by_rep if b_start <= rep_i <= b_end for r in rows_i]
            b_path = OUT / f"74_c_infections_{world}_reps{b_start:02d}_{b_end:02d}.csv"
            write_csv(b_path, block_rows)

        # Compute pooled parent mean R and Poisson 99th percentile threshold
        all_parent_off = [p["offspring_14d"] for rd in rep_data for p in rd["parents"]]
        pooled_R = sum(all_parent_off) / len(all_parent_off)
        q99 = poisson_q99(pooled_R)  # 5 in all three B1 worlds

        # Per-replicate summary rows
        for rd in rep_data:
            p_off = [p["offspring_14d"] for p in rd["parents"]]
            p_cnt = Counter(p_off)
            r_rep = sum(p_off) / len(p_off)
            kmom_rep = mom_k_from_counter(p_cnt)
            kml_rep = ml_k_from_counter(p_cnt)
            ez_z1_rep = sum(z * (z - 1) for z in p_off) / len(p_off)
            mom_yield_ratio_rep = (1.0 + ez_z1_rep / r_rep) / r_rep

            tagged_14d = [(p, c, q99) for p, c in rd["pairs_14d"]]
            tagged_all28 = [(p, c, q99) for p, c in rd["pairs_all28"]]
            st14 = compute_runc_stats_for_subset(tagged_14d)
            stall = compute_runc_stats_for_subset(tagged_all28)

            c_off = [c["offspring_14d"] for _p, c in rd["pairs_14d"]]
            c_mean = sum(c_off) / len(c_off) if c_off else float("nan")

            # Parent class 1 (parent offspring_14d == 1) day-matched ratio
            c1_kids = [c for p, c in rd["pairs_14d"] if p["offspring_14d"] == 1]
            c1_mean = sum(c["offspring_14d"] for c in c1_kids) / len(c1_kids) if c1_kids else float("nan")
            c1_exp = sum(rd["day_mean"][c["infection_day"]] for c in c1_kids) / len(c1_kids) if c1_kids else float("nan")

            # Sibling ICC and >=6 venue-day share
            fams = [[c["offspring_14d"] for c in kids] for kids in rd["children_by_parent"].values() if len(kids) >= 2]
            pair_icc, anova_icc, n_fams, _n_ch = sibling_icc(fams)
            ge6_vday = []
            for p in rd["parents"]:
                if p["offspring_14d"] >= 6:
                    kids = rd["children_by_parent"].get(p["agent_id"], [])
                    if kids:
                        vc = Counter(c["venue_day_id"] for c in kids)
                        ge6_vday.append(max(vc.values()) / len(kids))

            mean_child_sib = sum(rd["child_sibs"]) / len(rd["child_sibs"])
            mean_idx_sib14 = sum(rd["idx_sibs_14d"]) / len(rd["idx_sibs_14d"])
            mean_idx_siball = sum(rd["idx_sibs_all"]) / len(rd["idx_sibs_all"])

            rep_row = {
                "arm": arm_name,
                "world": world,
                "seed": rd["seed"],
                "replicate": rd["rep_idx"],
                "day28_cumulative_infections": rd["day28"],
                "day42_cumulative_infections": rd["day42"],
                "hist_matches_69_b_exactly": rd["exact_hist_match"],
                "raw_week6_trace_reinfection_overwrites_d1_10": rd["raw6_hist_diff_cases"],
                "index_cases": len(rd["parents"]),
                "parent_mean_offspring_14d": r_rep,
                "k_ml": kml_rep,
                "k_mom": kmom_rep,
                "child_infections_14d": len(rd["pairs_14d"]),
                "child_infections_all_d28": len(rd["pairs_all28"]),
                "child_mean_offspring_14d": c_mean,
                "poisson_q99_threshold": q99,
                "parent_child_pearson_14d": st14["pearson"],
                "parent_child_spearman_14d": st14["spearman"],
                "parent_child_pearson_all_d28": stall["pearson"],
                "parent_child_spearman_all_d28": stall["spearman"],
                "ss_parent_pairs": st14["ss_parent_pairs"],
                "ss_child_pairs": st14["ss_child_pairs"],
                "ss_child_share": st14["ss_child_share"],
                "ss_both_observed": st14["ss_both_observed"],
                "ss_both_expected": st14["ss_both_expected"],
                "ss_ratio_obs_over_exp": st14["ss_ratio_obs_over_exp"],
                "parent_class1_child_mean": c1_mean,
                "parent_class1_day_matched_exp": c1_exp,
                "parent_class1_day_matched_ratio": c1_mean / c1_exp if c1_exp else float("nan"),
                "sibling_pairwise_corr": pair_icc,
                "sibling_anova_icc": anova_icc,
                "parents_with_ge2_children": n_fams,
                "parents_ge6_mean_largest_venue_day_share": sum(ge6_vday) / len(ge6_vday) if ge6_vday else float("nan"),
                "moment_based_yield_ratio": mom_yield_ratio_rep,
                "child_of_index_mean_siblings": mean_child_sib,
                "child_of_index_yield_ratio_over_parent_R": (1.0 + mean_child_sib) / r_rep,
                "child_of_index_yield_ratio_over_child_R": (1.0 + mean_child_sib) / c_mean if c_mean else float("nan"),
                "index_case_mean_siblings_14d": mean_idx_sib14,
                "index_case_yield_ratio_14d": (1.0 + mean_idx_sib14) / r_rep,
                "index_case_mean_siblings_all": mean_idx_siball,
                "index_case_yield_ratio_all": (1.0 + mean_idx_siball) / r_rep,
            }
            rep_summary_rows.append(rep_row)

        # Pooled statistics for this world
        pooled_pairs_14d = [(p, c, q99) for rd in rep_data for p, c in rd["pairs_14d"]]
        pooled_pairs_all28 = [(p, c, q99) for rd in rep_data for p, c in rd["pairs_all28"]]
        st_pool_14 = compute_runc_stats_for_subset(pooled_pairs_14d)
        st_pool_all = compute_runc_stats_for_subset(pooled_pairs_all28)

        # Also check threshold >= 5 (in addition to > 5)
        pooled_pairs_ge5 = [(p, c, q99 - 1) for rd in rep_data for p, c in rd["pairs_14d"]]
        st_pool_ge5 = compute_runc_stats_for_subset(pooled_pairs_ge5)

        # Replicate bootstrap (1,000 draws) for parent-child Pearson, Spearman, and SS ratio
        rng = random.Random(BOOT_SEED + WORLDS.index(world) * 31)
        boot_pearson, boot_spearman, boot_ss_ratio = [], [], []
        n_reps = len(rep_data)
        for _ in range(BOOT_DRAWS):
            picks = [rng.randrange(n_reps) for _ in range(n_reps)]
            bpairs = [(p, c, q99) for i in picks for p, c in rep_data[i]["pairs_14d"]]
            px = [p["offspring_14d"] for p, _c, _q in bpairs]
            cy = [c["offspring_14d"] for _p, c, _q in bpairs]
            boot_pearson.append(pearson(px, cy))
            boot_spearman.append(spearman(px, cy))
            ss_p = sum(1 for x in px if x > q99)
            ss_c = sum(1 for y in cy if y > q99)
            ss_b = sum(1 for x, y in zip(px, cy) if x > q99 and y > q99)
            exp_b = ss_p * (ss_c / len(bpairs)) if bpairs else 0.0
            if exp_b > 0:
                boot_ss_ratio.append(ss_b / exp_b)
        boot_pearson.sort()
        boot_spearman.sort()
        boot_ss_ratio.sort()

        # Parent offspring classes: 1, 2 to 5, 6 to 9, 10 or more (and all >= 1)
        class_defs = [
            ("1 (at most 1)", lambda z: z == 1),
            ("2_to_5", lambda z: 2 <= z <= 5),
            ("6_to_9", lambda z: 6 <= z <= 9),
            ("10_or_more", lambda z: z >= 10),
            ("all_children", lambda z: z >= 1),
        ]
        c_by_class = {}
        for cname, pred in class_defs:
            c_vals = []
            e_vals = []
            n_parents_in_cls = sum(1 for rd in rep_data for p in rd["parents"] if pred(p["offspring_14d"]))
            for rd in rep_data:
                for p, c in rd["pairs_14d"]:
                    if pred(p["offspring_14d"]):
                        c_vals.append(c["offspring_14d"])
                        e_vals.append(rd["day_mean"][c["infection_day"]])
            cm = sum(c_vals) / len(c_vals) if c_vals else float("nan")
            em = sum(e_vals) / len(e_vals) if e_vals else float("nan")
            rat = cm / em if em else float("nan")
            c_by_class[cname] = (n_parents_in_cls, len(c_vals), cm, em, rat)
            parent_class_rows.append({
                "arm": arm_name,
                "world": world,
                "parent_offspring_class": cname,
                "parents_in_class": n_parents_in_cls,
                "child_infections": len(c_vals),
                "child_mean_offspring_14d": cm,
                "day_matched_expectation": em,
                "ratio_to_day_matched": rat,
            })

        # Subgroups (where the child was infected): household vs elsewhere, and inside vs outside events for w3b
        sub_defs = [
            ("all_children", lambda p, c: True),
            ("same_household", lambda p, c: c["same_household_as_infector"] == 1),
            ("outside_household", lambda p, c: c["same_household_as_infector"] == 0),
        ]
        if world == "w3b":
            sub_defs += [
                ("inside_event", lambda p, c: c["event_flag"] == 1),
                ("outside_event", lambda p, c: c["event_flag"] == 0),
            ]
        for sname, spred in sub_defs:
            spairs = [(p, c, q99) for rd in rep_data for p, c in rd["pairs_14d"] if spred(p, c)]
            sst = compute_runc_stats_for_subset(spairs)
            c_m = sum(c["offspring_14d"] for _p, c, _q in spairs) / len(spairs) if spairs else float("nan")
            p_m = sum(p["offspring_14d"] for p, _c, _q in spairs) / len(spairs) if spairs else float("nan")
            subgroup_rows.append({
                "arm": arm_name,
                "world": world,
                "subgroup": sname,
                "pairs": sst["pairs"],
                "share_of_all_pairs": sst["pairs"] / len(pooled_pairs_14d) if pooled_pairs_14d else float("nan"),
                "parent_mean_offspring_14d": p_m,
                "child_mean_offspring_14d": c_m,
                "pearson": sst["pearson"],
                "spearman": sst["spearman"],
                "ss_parent_pairs": sst["ss_parent_pairs"],
                "ss_child_pairs": sst["ss_child_pairs"],
                "ss_child_share": sst["ss_child_share"],
                "ss_both_observed": sst["ss_both_observed"],
                "ss_both_expected": sst["ss_both_expected"],
                "ss_ratio_obs_over_exp": sst["ss_ratio_obs_over_exp"],
            })

        # Pooled sibling ICC & >=6 venue-day share
        all_fams = [[c["offspring_14d"] for c in kids] for rd in rep_data for kids in rd["children_by_parent"].values() if len(kids) >= 2]
        pool_pair_icc, pool_anova_icc, pool_nfams, pool_nch = sibling_icc(all_fams)
        all_ge6_vday = []
        for rd in rep_data:
            for p in rd["parents"]:
                if p["offspring_14d"] >= 6:
                    kids = rd["children_by_parent"].get(p["agent_id"], [])
                    if kids:
                        vc = Counter(c["venue_day_id"] for c in kids)
                        all_ge6_vday.append(max(vc.values()) / len(kids))

        # Tracing yield from traces (pooled)
        p_cnt_all = Counter(all_parent_off)
        kmom_pool = mom_k_from_counter(p_cnt_all)
        kml_pool = ml_k_from_counter(p_cnt_all)
        ez_z1_pool = sum(z * (z - 1) for z in all_parent_off) / len(all_parent_off)
        mom_yield_pool = (1.0 + ez_z1_pool / pooled_R) / pooled_R

        all_child_sibs = [s for rd in rep_data for s in rd["child_sibs"]]
        all_idx_sibs14 = [s for rd in rep_data for s in rd["idx_sibs_14d"]]
        all_idx_sibsall = [s for rd in rep_data for s in rd["idx_sibs_all"]]
        all_child_off = [c["offspring_14d"] for _p, c, _q in pooled_pairs_14d]
        pooled_child_R = sum(all_child_off) / len(all_child_off)

        mean_csib = sum(all_child_sibs) / len(all_child_sibs)
        mean_isib14 = sum(all_idx_sibs14) / len(all_idx_sibs14)
        mean_isiball = sum(all_idx_sibsall) / len(all_idx_sibsall)

        # Class membership stats for World 2b
        cls_stats = {}
        if world == "w2b":
            # Population class share from rep01 hvi.csv
            hvi0 = load_hvi_flags(dirs6[0] / "hvi.csv")
            pop_cls_share = sum(hvi0) / len(hvi0)
            par_cls = [int(p["agent_class_flag"]) for rd in rep_data for p in rd["parents"]]
            c_given_p1 = [int(c["agent_class_flag"]) for _p, c, _q in pooled_pairs_14d if int(_p["agent_class_flag"]) == 1]
            c_given_p0 = [int(c["agent_class_flag"]) for _p, c, _q in pooled_pairs_14d if int(_p["agent_class_flag"]) == 0]
            c_all_cls = [int(c["agent_class_flag"]) for _p, c, _q in pooled_pairs_14d]
            # Share of all non-seed infections (d <= 28) whose infector is a class member
            inf_from_cls = 0
            inf_nonseed = 0
            for rd in rep_data:
                by_ag = {r["agent_id"]: r for r in rd["inf_rows"]}
                hvi_r = load_hvi_flags(dirs6[rd["rep_idx"] - 1] / "hvi.csv")
                for r in rd["inf_rows"]:
                    if r["infector_id"] != "":
                        inf_nonseed += 1
                        if hvi_r[int(r["infector_id"])] == 1:
                            inf_from_cls += 1
            cls_stats = {
                "w2b_pop_class_share": pop_cls_share,
                "w2b_parent_class_share": sum(par_cls) / len(par_cls),
                "w2b_child_class_share_all": sum(c_all_cls) / len(c_all_cls),
                "w2b_child_class_share_given_parent_class1": sum(c_given_p1) / len(c_given_p1),
                "w2b_child_class_share_given_parent_class0": sum(c_given_p0) / len(c_given_p0),
                "w2b_share_index_offspring_from_class_parents": len(c_given_p1) / len(pooled_pairs_14d),
                "w2b_share_all_d28_infections_from_class_infectors": inf_from_cls / inf_nonseed,
            }

        cell_row = {
            "arm": arm_name,
            "world": world,
            "replicates": len(rep_data),
            "all_replicates_match_69_b_hist_exactly": all(rd["exact_hist_match"] for rd in rep_data),
            "raw_week6_trace_reinfection_overwrites_d1_10_total": sum(rd["raw6_hist_diff_cases"] for rd in rep_data),
            "index_cases": len(all_parent_off),
            "parent_mean_offspring_14d": pooled_R,
            "k_ml": kml_pool,
            "k_mom": kmom_pool,
            "child_infections_14d": st_pool_14["pairs"],
            "child_infections_all_d28": st_pool_all["pairs"],
            "child_mean_offspring_14d": pooled_child_R,
            "poisson_q99_threshold": q99,
            "parent_child_pearson_14d": st_pool_14["pearson"],
            "parent_child_pearson_14d_low": quantile_linear(boot_pearson, 0.05),
            "parent_child_pearson_14d_high": quantile_linear(boot_pearson, 0.95),
            "parent_child_spearman_14d": st_pool_14["spearman"],
            "parent_child_spearman_14d_low": quantile_linear(boot_spearman, 0.05),
            "parent_child_spearman_14d_high": quantile_linear(boot_spearman, 0.95),
            "parent_child_pearson_all_d28": st_pool_all["pearson"],
            "parent_child_spearman_all_d28": st_pool_all["spearman"],
            "ss_parent_pairs": st_pool_14["ss_parent_pairs"],
            "ss_child_pairs": st_pool_14["ss_child_pairs"],
            "ss_child_share": st_pool_14["ss_child_share"],
            "ss_both_observed": st_pool_14["ss_both_observed"],
            "ss_both_expected": st_pool_14["ss_both_expected"],
            "ss_ratio_obs_over_exp": st_pool_14["ss_ratio_obs_over_exp"],
            "ss_ratio_obs_over_exp_low": quantile_linear(boot_ss_ratio, 0.05),
            "ss_ratio_obs_over_exp_high": quantile_linear(boot_ss_ratio, 0.95),
            "ss_ratio_at_ge5": st_pool_ge5["ss_ratio_obs_over_exp"],
            "class1_child_mean": c_by_class["1 (at most 1)"][2],
            "class1_day_matched_exp": c_by_class["1 (at most 1)"][3],
            "class1_day_matched_ratio": c_by_class["1 (at most 1)"][4],
            "class2_5_child_mean": c_by_class["2_to_5"][2],
            "class2_5_day_matched_exp": c_by_class["2_to_5"][3],
            "class2_5_day_matched_ratio": c_by_class["2_to_5"][4],
            "class6_9_child_mean": c_by_class["6_to_9"][2],
            "class6_9_day_matched_exp": c_by_class["6_to_9"][3],
            "class6_9_day_matched_ratio": c_by_class["6_to_9"][4],
            "class10p_child_mean": c_by_class["10_or_more"][2],
            "class10p_day_matched_exp": c_by_class["10_or_more"][3],
            "class10p_day_matched_ratio": c_by_class["10_or_more"][4],
            "sibling_pairwise_corr": pool_pair_icc,
            "sibling_anova_icc": pool_anova_icc,
            "parents_with_ge2_children": pool_nfams,
            "children_in_ge2_families": pool_nch,
            "parents_ge6_count": len(all_ge6_vday),
            "parents_ge6_mean_largest_venue_day_share": sum(all_ge6_vday) / len(all_ge6_vday) if all_ge6_vday else float("nan"),
            "moment_based_yield_ratio": mom_yield_pool,
            "child_of_index_mean_siblings": mean_csib,
            "child_of_index_yield_ratio_over_parent_R": (1.0 + mean_csib) / pooled_R,
            "child_of_index_yield_ratio_rel_diff_vs_moment": ((1.0 + mean_csib) / pooled_R) / mom_yield_pool - 1.0,
            "child_of_index_yield_ratio_over_child_R": (1.0 + mean_csib) / pooled_child_R,
            "index_case_mean_siblings_14d": mean_isib14,
            "index_case_yield_ratio_14d": (1.0 + mean_isib14) / pooled_R,
            "index_case_yield_ratio_14d_rel_diff_vs_moment": ((1.0 + mean_isib14) / pooled_R) / mom_yield_pool - 1.0,
            "index_case_mean_siblings_all": mean_isiball,
            "index_case_yield_ratio_all": (1.0 + mean_isiball) / pooled_R,
            "index_case_yield_ratio_all_rel_diff_vs_moment": ((1.0 + mean_isiball) / pooled_R) / mom_yield_pool - 1.0,
            **cls_stats,
        }
        cell_summary_rows.append(cell_row)
        print(
            f"[Run C] {arm_name}: exact_hist={cell_row['all_replicates_match_69_b_hist_exactly']} "
            f"pairs={cell_row['child_infections_14d']} r={cell_row['parent_child_pearson_14d']:+.4f} "
            f"[{cell_row['parent_child_pearson_14d_low']:+.4f},{cell_row['parent_child_pearson_14d_high']:+.4f}] "
            f"rho={cell_row['parent_child_spearman_14d']:+.4f} "
            f"SS_ratio={cell_row['ss_ratio_obs_over_exp']:.3f} [{cell_row['ss_ratio_obs_over_exp_low']:.3f},{cell_row['ss_ratio_obs_over_exp_high']:.3f}] "
            f"c1_ratio={cell_row['class1_day_matched_ratio']:.3f} "
            f"sib_icc={cell_row['sibling_pairwise_corr']:+.4f} "
            f"yield_mom={mom_yield_pool:.3f} yield_child={cell_row['child_of_index_yield_ratio_over_parent_R']:.3f} "
            f"yield_idx14={cell_row['index_case_yield_ratio_14d']:.3f}",
            flush=True,
        )

    write_csv(OUT / "74_c_replicate_summary.csv", rep_summary_rows)
    write_csv(OUT / "74_c_cells_summary.csv", cell_summary_rows)
    write_csv(OUT / "74_c_parent_classes.csv", parent_class_rows)
    write_csv(OUT / "74_c_subgroups.csv", subgroup_rows)
    return cell_summary_rows


# ---------------------------------------------------------------- Run D analysis

def load_daily_inf28(stdout_path):
    with open(stdout_path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        c_inf = header.index("INF")
        lines = [line.rstrip("\n").split("\t") for line in handle if line.strip()]
        return int(lines[27][c_inf])


def replicate_core_d(run_dir, age, atype, home, hh_size):
    run_dir = Path(run_dir)
    cmd = json.loads((run_dir / "command.json").read_text())
    seed = int(cmd[cmd.index("--seed") + 1])
    k_coeff = float(cmd[cmd.index("-k") + 1])
    alpha = float(cmd[cmd.index("--densityExponent") + 1]) if "--densityExponent" in cmd else 1.0

    rows = read_trace_rows(run_dir / "trace.tsv")
    ev_pairs, ev_agents = load_event_pairs(run_dir / "events.tsv.infections")
    ev_log = run_dir / "events.tsv"

    day_map = {}
    children = defaultdict(list)
    loc_counts = Counter()
    venue_inf_all = Counter()
    venue_inf_nonhome = Counter()
    occ_d1_28 = []
    hh_trans = 0

    for r in rows:
        a, inf, loc, lt, d, occ = r["agent"], r["infector"], r["location"], r["locType"], r["day"], r["occupancy"]
        day_map[a] = d
        if inf != UNKNOWN:
            children[inf].append((loc, lt, d, a))
        if 1 <= d <= 28:
            loc_counts[lt] += 1
            if inf != UNKNOWN:
                occ_d1_28.append(occ)
                venue_inf_all[loc] += 1
                if lt != 2:
                    venue_inf_nonhome[loc] += 1
                if home[a] >= 0 and home[a] == home[inf]:
                    hh_trans += 1

    known = {a for kids in children.values() for _l, _lt, _d, a in kids}
    ids, total, event = [], [], []
    for a, d in day_map.items():
        if a not in known or not (1 <= d <= 10):
            continue
        n = e = 0
        for _loc, _lt, cd, ca in children.get(a, ()):
            if cd <= d + 14:
                n += 1
                if ca in ev_agents:
                    e += 1
        ids.append(a)
        total.append(n)
        event.append(e)

    n = len(total)
    cnt = Counter(total)
    mean_r = sum(total) / n if n else float("nan")
    kmom = mom_k_from_counter(cnt, n, sum(total)) if n > 1 else float("nan")
    kml = ml_k_from_counter(cnt, n, sum(total)) if n > 1 else float("nan")
    ls = lorenz_from_list(total)

    tot_loc = sum(loc_counts.values())
    den_hh = sum(max(hh_size[home[a]] - 1, 0) for a in ids if home[a] >= 0)

    # Top 10 largest clusters of this replicate
    order = sorted(range(n), key=total.__getitem__, reverse=True)[:10]
    comp = []
    for j in order:
        inf_id = ids[j]
        kids = children.get(inf_id, [])
        if not kids:
            continue
        bvd = Counter((loc, d) for loc, _lt, d, _a in kids)
        same = (sum(1 for _l, _t, _d, a in kids if home[a] == home[inf_id]) / len(kids)) if home[inf_id] >= 0 else 0.0
        comp.append((total[j], same, max(bvd.values()) / len(kids), len({loc for loc, _lt, _d, _a in kids})))

    # Occupancy quantiles and busiest 10% of active venues in this replicate
    occ_sorted = sorted(occ_d1_28)
    occ_med = quantile_linear(occ_sorted, 0.50)
    occ_p90 = quantile_linear(occ_sorted, 0.90)

    v_vals = sorted(venue_inf_all.values(), reverse=True)
    k10_all = max(1, int(round(0.10 * len(v_vals)))) if v_vals else 0
    top10_active_share = sum(v_vals[:k10_all]) / sum(v_vals) if v_vals else float("nan")

    v_nh = sorted(venue_inf_nonhome.values(), reverse=True)
    k10_nh = max(1, int(round(0.10 * len(v_nh)))) if v_nh else 0
    top10_nh_share = sum(v_nh[:k10_nh]) / sum(v_nh) if v_nh else float("nan")

    row = {
        "seed": seed,
        "background_coefficient": k_coeff,
        "alpha": alpha,
        "day28_cumulative_infections": load_daily_inf28(run_dir / "stdout.txt"),
        "index_cases": n,
        "early_R": mean_r,
        "k_mom": kmom,
        "k_ml": kml,
        "share_0": cnt[0] / n if n else float("nan"),
        "share_1_to_5": sum(cnt[j] for j in range(1, 6)) / n if n else float("nan"),
        "share_above_5": sum(c for j, c in cnt.items() if j > 5) / n if n else float("nan"),
        "share_causing_80pct": ls.get("share_of_index_cases_causing_80pct", float("nan")),
        "largest_offspring": max(total) if n else 0,
        "infections_d1_28": tot_loc,
        "infections_share_home": loc_counts[2] / tot_loc if tot_loc else float("nan"),
        "infections_share_school_and_work": sum(loc_counts[t] for t in SCHOOL_WORK) / tot_loc if tot_loc else float("nan"),
        "infections_share_high_L_types": sum(loc_counts[t] for t in HIGH) / tot_loc if tot_loc else float("nan"),
        "infections_share_hospital": sum(loc_counts[t] for t in HOSPITAL) / tot_loc if tot_loc else float("nan"),
        "household_secondary_attack_numerator": hh_trans,
        "household_secondary_attack_denominator": den_hh,
        "top10_mean_offspring": sum(x[0] for x in comp) / len(comp) if comp else float("nan"),
        "top10_mean_same_household_share": sum(x[1] for x in comp) / len(comp) if comp else float("nan"),
        "top10_mean_largest_venue_day_share": sum(x[2] for x in comp) / len(comp) if comp else float("nan"),
        "top10_mean_distinct_venues": sum(x[3] for x in comp) / len(comp) if comp else float("nan"),
        "infection_occupancy_median": occ_med,
        "infection_occupancy_p90": occ_p90,
        "active_venues_count": len(v_vals),
        "top10pct_active_venues_share": top10_active_share,
        "top10pct_nonhome_active_venues_share": top10_nh_share,
    }

    if ev_log.exists():
        et = einf = ei = 0
        with open(ev_log) as handle:
            for r in csv.DictReader(handle, delimiter="\t"):
                et += 1
                if float(r["infectious_in_group"]) > 0:
                    einf += 1
                ei += int(r["infected"])
        row["events_total"] = et
        row["events_with_infectious"] = einf
        row["event_infections"] = ei
        row["event_offspring_share"] = sum(event) / sum(total) if sum(total) else 0.0

    return row, ids, total, event, cnt, occ_d1_28, venue_inf_all


def run_d_analysis():
    age, atype, home, hh_size = agent_context()

    cells = []
    for world in WORLDS:
        # alpha = 1.0 B1 reference from Round 14
        st14 = json.loads((R14 / "state" / f"r14_b1final_{world}.json").read_text())
        dirs14 = sorted(p.parent for p in (R14 / st14["prefix"]).glob("rep*/trace.tsv"))
        cells.append({
            "cell": f"{world}:B1_alpha1",
            "world": world,
            "alpha": 1.0,
            "dirs": dirs14,
            "k": st14["k"],
            "state": st14,
        })
        for alpha in (0.5, 0.0):
            tag = f"a{alpha:g}_{world}"
            st15 = json.loads((R15 / "state" / f"r15_d_{tag}.json").read_text())
            dirs15 = sorted(p.parent for p in (R15 / st15["prefix"]).glob("rep*/trace.tsv"))
            cells.append({
                "cell": f"{world}:D_alpha{alpha:g}",
                "world": world,
                "alpha": alpha,
                "dirs": dirs15,
                "k": st15["k"],
                "state": st15,
            })

    hist_rows = []
    rep_rows = []
    cell_rows = []
    cal_rows = []

    for c_idx, c in enumerate(cells):
        cores = [replicate_core_d(d, age, atype, home, hh_size) for d in c["dirs"]]
        for rep_i, (r_row, _ids, tot, ev, _cnt, _occ, _vinf) in enumerate(cores, start=1):
            full_rep = {"arm": c["cell"], "world": c["world"], "replicate": rep_i, **r_row}
            rep_rows.append(full_rep)
            has_ev = "event_offspring_share" in r_row
            for (a, e), n_c in sorted(Counter(zip(tot, ev)).items()):
                hist_rows.append({
                    "arm": c["cell"],
                    "seed": r_row["seed"],
                    "replicate": rep_i,
                    "offspring_total": a,
                    "offspring_at_events": e if has_ev else "",
                    "index_cases": n_c,
                })

        # Pooled statistics
        tot_all = [x for _r, _i, tot, _ev, _cnt, _occ, _vinf in cores for x in tot]
        ev_all = [x for _r, _i, _tot, ev, _cnt, _occ, _vinf in cores for x in ev]
        cnt_all = Counter(tot_all)
        n_idx = len(tot_all)
        mean_r = sum(tot_all) / n_idx
        kmom = mom_k_from_counter(cnt_all, n_idx, sum(tot_all))
        kml = ml_k_from_counter(cnt_all, n_idx, sum(tot_all))
        z_nb = nb_zero(mean_r, kml)
        s80_nb = nb_80pct_share(kml, mean_r)
        nb_own_ab5 = nb_sf_at_least(mean_r, kml, 6)
        s0 = cnt_all[0] / n_idx
        s1_5 = sum(cnt_all[j] for j in range(1, 6)) / n_idx
        sab5 = sum(v for j, v in cnt_all.items() if j > 5) / n_idx
        sat20 = sum(v for j, v in cnt_all.items() if j >= 20) / n_idx
        sat50 = sum(v for j, v in cnt_all.items() if j >= 50) / n_idx
        ls = lorenz_from_list(tot_all)
        tot_sorted = sorted(tot_all)

        r_list = [x[0] for x in cores]
        inf_d1_28_tot = sum(r["infections_d1_28"] for r in r_list)
        hh_num = sum(r["household_secondary_attack_numerator"] for r in r_list)
        hh_den = sum(r["household_secondary_attack_denominator"] for r in r_list)

        # Pooled occupancy and pooled busiest 10% of active venues
        occ_pooled = sorted(x for _r, _i, _tot, _ev, _cnt, occ, _vinf in cores for x in occ)
        occ_med_pooled = quantile_linear(occ_pooled, 0.50)
        occ_p90_pooled = quantile_linear(occ_pooled, 0.90)

        v_pooled = Counter()
        for _r, _i, _tot, _ev, _cnt, _occ, vinf in cores:
            v_pooled.update(vinf)
        vp_vals = sorted(v_pooled.values(), reverse=True)
        kp10 = max(1, int(round(0.10 * len(vp_vals))))
        top10_active_pooled = sum(vp_vals[:kp10]) / sum(vp_vals)

        # Replicate bootstrap (1,000 draws)
        rng = random.Random(BOOT_SEED + 500 + c_idx * 37)
        n_reps = len(cores)
        b_cols = defaultdict(list)
        for _ in range(BOOT_DRAWS):
            picks = [rng.randrange(n_reps) for _ in range(n_reps)]
            b_cnt = Counter()
            b_n = 0
            b_sum = 0
            for i in picks:
                ci = cores[i][4]
                b_cnt.update(ci)
                ni = len(cores[i][2])
                b_n += ni
                b_sum += sum(cores[i][2])
            b_mean = b_sum / b_n
            b_kmom = mom_k_from_counter(b_cnt, b_n, b_sum)
            b_kml = ml_k_from_counter(b_cnt, b_n, b_sum)
            b_z = nb_zero(b_mean, b_kml)
            b_s0 = b_cnt[0] / b_n
            b_cols["early_R"].append(b_mean)
            b_cols["k_mom"].append(b_kmom)
            b_cols["k_ml"].append(b_kml)
            b_cols["k_ml_over_k_mom"].append(b_kml / b_kmom)
            b_cols["share_0"].append(b_s0)
            b_cols["share_1_to_5"].append(sum(b_cnt[j] for j in range(1, 6)) / b_n)
            b_cols["share_above_5"].append(sum(v for j, v in b_cnt.items() if j > 5) / b_n)
            b_cols["observed_minus_nb_zero"].append(b_s0 - b_z)
            b_tot_list = [x for i in picks for x in cores[i][2]]
            b_cols["share_causing_80pct"].append(lorenz_from_list(b_tot_list)["share_of_index_cases_causing_80pct"])
            b_inf = sum(cores[i][0]["infections_d1_28"] for i in picks)
            b_cols["infections_share_home"].append(
                sum(cores[i][0]["infections_share_home"] * cores[i][0]["infections_d1_28"] for i in picks) / b_inf
            )
            b_cols["household_secondary_attack_rate"].append(
                sum(cores[i][0]["household_secondary_attack_numerator"] for i in picks)
                / sum(cores[i][0]["household_secondary_attack_denominator"] for i in picks)
            )
            for k_name in (
                "top10_mean_same_household_share",
                "top10_mean_largest_venue_day_share",
                "infection_occupancy_median",
                "infection_occupancy_p90",
                "top10pct_active_venues_share",
                "top10pct_nonhome_active_venues_share",
            ):
                b_cols[k_name].append(sum(cores[i][0][k_name] for i in picks) / n_reps)

        boot_intervals = {}
        for k_name, vals in b_cols.items():
            s_vals = sorted(v for v in vals if v is not None and math.isfinite(v))
            boot_intervals[f"{k_name}_low"] = quantile_linear(s_vals, 0.05)
            boot_intervals[f"{k_name}_high"] = quantile_linear(s_vals, 0.95)

        c_row = {
            "cell": c["cell"],
            "world": c["world"],
            "alpha": c["alpha"],
            "replicates": n_reps,
            "background_coefficient": c["k"],
            "day28_mean": sum(r["day28_cumulative_infections"] for r in r_list) / n_reps,
            "day28_vs_6211.25": (sum(r["day28_cumulative_infections"] for r in r_list) / n_reps) / 6211.25 - 1.0,
            "index_cases": n_idx,
            "early_R": mean_r,
            "k_ml": kml,
            "k_mom": kmom,
            "k_ml_over_k_mom": kml / kmom,
            "share_0": s0,
            "share_1_to_5": s1_5,
            "share_above_5": sab5,
            "nb_own_share_above_5": nb_own_ab5,
            "share_above_5_over_nb_own": sab5 / nb_own_ab5 if nb_own_ab5 else float("nan"),
            "share_at_least_20": sat20,
            "share_at_least_50": sat50,
            "maximum_offspring": max(tot_all),
            "largest_offspring_mean_over_replicates": sum(r["largest_offspring"] for r in r_list) / n_reps,
            "p99_offspring": quantile_linear(tot_sorted, 0.99),
            "nb_zero_at_k_ml": z_nb,
            "observed_minus_nb_zero": s0 - z_nb,
            "share_causing_80pct": ls["share_of_index_cases_causing_80pct"],
            "nb_80pct_at_k_ml": s80_nb,
            "infections_share_home": sum(r["infections_share_home"] * r["infections_d1_28"] for r in r_list) / inf_d1_28_tot,
            "infections_share_school_and_work": sum(r["infections_share_school_and_work"] * r["infections_d1_28"] for r in r_list) / inf_d1_28_tot,
            "infections_share_high_L_types": sum(r["infections_share_high_L_types"] * r["infections_d1_28"] for r in r_list) / inf_d1_28_tot,
            "infections_share_hospital": sum(r["infections_share_hospital"] * r["infections_d1_28"] for r in r_list) / inf_d1_28_tot,
            "household_secondary_attack_rate": hh_num / hh_den,
            "top10_mean_offspring": sum(r["top10_mean_offspring"] for r in r_list) / n_reps,
            "top10_mean_same_household_share": sum(r["top10_mean_same_household_share"] for r in r_list) / n_reps,
            "top10_mean_largest_venue_day_share": sum(r["top10_mean_largest_venue_day_share"] for r in r_list) / n_reps,
            "top10_mean_distinct_venues": sum(r["top10_mean_distinct_venues"] for r in r_list) / n_reps,
            "infection_occupancy_median_pooled": occ_med_pooled,
            "infection_occupancy_p90_pooled": occ_p90_pooled,
            "infection_occupancy_median": sum(r["infection_occupancy_median"] for r in r_list) / n_reps,
            "infection_occupancy_p90": sum(r["infection_occupancy_p90"] for r in r_list) / n_reps,
            "top10pct_active_venues_share": sum(r["top10pct_active_venues_share"] for r in r_list) / n_reps,
            "top10pct_active_venues_share_pooled": top10_active_pooled,
            "top10pct_nonhome_active_venues_share": sum(r["top10pct_nonhome_active_venues_share"] for r in r_list) / n_reps,
            "event_offspring_share": sum(ev_all) / sum(tot_all) if "event_offspring_share" in r_list[0] else "",
            **boot_intervals,
        }
        cell_rows.append(c_row)

        # Calibration log rows for alpha < 1
        st = c["state"]
        for t in st.get("cal_trials", []):
            cal_rows.append({
                "cell": c["cell"],
                "world": c["world"],
                "alpha": c["alpha"],
                "phase": t["phase"],
                "trial": t["trial"],
                "coefficient": t["k"],
                "day28_mean": t["day28"],
                "day28_vs_6211.25": t["day28"] / 6211.25 - 1.0,
                "replicates": len(t["values"]),
                "within_3pct": t["within_3pct"],
            })
        for t in st.get("final_trials", []):
            cal_rows.append({
                "cell": c["cell"],
                "world": c["world"],
                "alpha": c["alpha"],
                "phase": t["phase"],
                "trial": t["trial"],
                "coefficient": t["k"],
                "day28_mean": t["day28"],
                "day28_vs_6211.25": t["day28"] / 6211.25 - 1.0,
                "replicates": len(t["values"]),
                "within_3pct": t["within_3pct"],
            })

        print(
            f"[Run D] {c['cell']:16s} k={c['k']:.6g} day28={c_row['day28_mean']:.1f} ({c_row['day28_vs_6211.25']:+.1%}) "
            f"R={mean_r:.3f} k_ml={kml:.3f} [{c_row['k_ml_low']:.3f},{c_row['k_ml_high']:.3f}] "
            f"k_mom={kmom:.3f} ratio={c_row['k_ml_over_k_mom']:.2f} "
            f"zero={s0:.3f} (gap={c_row['observed_minus_nb_zero']*100:+.2f}pt) "
            f"home={c_row['infections_share_home']:.3f} vday={c_row['top10_mean_largest_venue_day_share']:.3f} "
            f"hh={c_row['top10_mean_same_household_share']:.3f} "
            f"occ_med={occ_med_pooled:.0f} occ_p90={occ_p90_pooled:.0f} "
            f"top10v_rep={c_row['top10pct_active_venues_share']:.3f} top10v_pool={top10_active_pooled:.3f}",
            flush=True,
        )

    write_csv(OUT / "74_d_cells_summary.csv", cell_rows)
    write_csv(OUT / "74_d_replicate_summary.csv", rep_rows)
    write_csv(OUT / "74_d_replicate_histograms.csv", hist_rows)
    write_csv(OUT / "74_d_calibration_log.csv", cal_rows)
    return cell_rows


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("runC", "all"):
        run_c_analysis()
    if cmd in ("runD", "all"):
        run_d_analysis()


if __name__ == "__main__":
    main()
