#!/usr/bin/env python3
"""Equivalence, scene-repair, reinfection and world-3b statistics for note 85."""
import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_round16 as r16  # noqa: E402
import r6stats  # noqa: E402

RESULTS = HERE / "results" / "round17"
OUT = HERE.parent
HOME = 2
RISKY_AND_LONG = {5, 6, 8, 9, 10}


def chi2_sf(x, df):
    """Survival function of a chi-square random variable, via the regularised gamma."""
    if df <= 0:
        return float("nan")
    if x <= 0:
        return 1.0
    return _gamma_q(0.5 * df, 0.5 * x)


def _gamma_q(a, x):
    if x < a + 1.0:
        return 1.0 - _gamma_p_series(a, x)
    return _gamma_q_cf(a, x)


def _gamma_p_series(a, x):
    term = 1.0 / a
    total = term
    for n in range(1, 10000):
        term *= x / (a + n)
        total += term
        if abs(term) < abs(total) * 1e-14:
            break
    return total * math.exp(-x + a * math.log(x) - math.lgamma(a))


def _gamma_q_cf(a, x):
    tiny = 1e-30
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-12:
            break
    return math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def sample_sd(values):
    n = len(values)
    if n < 2:
        return float("nan")
    mean = sum(values) / n
    return math.sqrt(sum((v - mean) ** 2 for v in values) / (n - 1))


def expand(counter):
    out = []
    for k, n in counter.items():
        out.extend([int(k)] * int(n))
    return out


def merge_pair(left, right, minimum=10):
    hi = 0
    if left:
        hi = max(hi, max(left))
    if right:
        hi = max(hi, max(right))
    groups = []
    acc_l = acc_r = 0
    start = 0
    open_group = False
    for k in range(hi + 1):
        if not open_group:
            start = k
            open_group = True
        acc_l += left.get(k, 0)
        acc_r += right.get(k, 0)
        if acc_l >= minimum and acc_r >= minimum:
            groups.append([acc_l, acc_r])
            acc_l = acc_r = 0
            open_group = False
    if open_group:
        if groups:
            groups[-1][0] += acc_l
            groups[-1][1] += acc_r
        else:
            groups.append([acc_l, acc_r])
    return groups


def homogeneity(left, right):
    groups = merge_pair(left, right)
    row_l = sum(g[0] for g in groups)
    row_r = sum(g[1] for g in groups)
    total = row_l + row_r
    chi = 0.0
    used = 0
    for n_l, n_r in groups:
        col = n_l + n_r
        if col == 0 or row_l == 0 or row_r == 0:
            continue
        e_l = row_l * col / total
        e_r = row_r * col / total
        chi += (n_l - e_l) ** 2 / e_l + (n_r - e_r) ** 2 / e_r
        used += 1
    df = used - 1
    p = chi2_sf(chi, df) if df > 0 else float("nan")
    return chi, df, p, used


def pooled_from_hists(by_rep):
    total = Counter()
    for counts in by_rep.values():
        total.update(counts)
    return total


def n_of(counter):
    return sum(counter.values())


def mean_of(counter):
    n = n_of(counter)
    if not n:
        return float("nan")
    return sum(k * v for k, v in counter.items()) / n


def zero_of(counter):
    n = n_of(counter)
    if not n:
        return float("nan")
    return counter.get(0, 0) / n


def read_episodes(path):
    rows = []
    with open(path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        col = {name: i for i, name in enumerate(header)}
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(header):
                continue
            rows.append({
                "infector": int(parts[col["infector_id"]]),
                "day": int(parts[col["day"]]),
                "venue_type": int(parts[col["venue_type"]]),
                "where": parts[col["household_vs_other"]],
                "sus": float(parts[col["susceptibles_present"]]),
                "weight": float(parts[col["expected_infections_mult1"]]),
                "mult": float(parts[col["realised_multiplier"]]),
                "actual": int(parts[col["actual_infected"]]),
                "event": int(parts[col["event_flag"]]),
            })
    return rows


def index_days(trace_path):
    days = {}
    with open(trace_path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        col = {name: i for i, name in enumerate(header)}
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            inf = int(parts[col["infector"]])
            day = int(parts[col["timestamp"]]) // r16.STEPS
            agent = int(parts[col["agent"]])
            if inf != r16.UNKNOWN and 1 <= day <= 10:
                days[agent] = day
    return days


def cv2(values):
    n = len(values)
    if n < 2:
        return float("nan")
    mean = sum(values) / n
    if mean == 0:
        return float("nan")
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return var / (mean * mean)


def median(values):
    if not values:
        return float("nan")
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return 0.5 * (ordered[mid - 1] + ordered[mid])


def episode_record(cell_name, world, alpha):
    prefix = RESULTS / "E" / cell_name
    by_case = defaultdict(list)
    mult = {}
    for i in range(1, 13):
        rep = prefix / f"rep{i:02d}"
        days = index_days(rep / "trace.tsv")
        for row in read_episodes(rep / "episodes_inf.tsv"):
            infector = row["infector"]
            if infector not in days:
                continue
            iday = days[infector]
            if row["day"] < iday or row["day"] > iday + 14:
                continue
            by_case[(i, infector)].append(row)
            mult[(i, infector)] = row["mult"]
    sum_w2 = 0.0
    sum_t2 = 0.0
    totals = []
    multipliers = []
    offspring = []
    home_sus = []
    public_sus = []
    event_cases = 0
    event_offspring = []
    for key, rows in by_case.items():
        weights = [row["weight"] for row in rows]
        total = sum(weights)
        totals.append(total)
        multipliers.append(mult.get(key, rows[0]["mult"]))
        got = sum(row["actual"] for row in rows)
        offspring.append(got)
        sum_w2 += sum(w * w for w in weights)
        sum_t2 += total * total
        for row in rows:
            if row["actual"] <= 0:
                continue
            if row["venue_type"] == HOME or row["where"] == "household":
                home_sus.append(row["sus"])
            if row["venue_type"] in RISKY_AND_LONG:
                public_sus.append(row["sus"])
        if any(row["event"] for row in rows):
            event_cases += 1
            event_offspring.append(got)
    h = sum_w2 / sum_t2 if sum_t2 else float("nan")
    c_t = cv2(totals)
    c_m = cv2(multipliers)
    k_mom = r6stats.mom_k(offspring)
    product = (1.0 + c_t) * (1.0 + c_m * h)
    k_formula = 1.0 / (product - 1.0) if product > 1 else float("nan")
    n_cases = len(by_case)
    return {
        "cell": cell_name,
        "world": world,
        "alpha": alpha,
        "index_cases": n_cases,
        "H": h,
        "c_T": c_t,
        "c_m": c_m,
        "k_mom": k_mom,
        "k_formula": k_formula,
        "formula_over_moment": (k_formula / k_mom) if k_mom else float("nan"),
        "home_infecting_episodes": len(home_sus),
        "home_sus_median": median(home_sus),
        "public_infecting_episodes": len(public_sus),
        "public_sus_median": median(public_sus),
        "event_bearing_cases": event_cases,
        "event_bearing_share": event_cases / n_cases if n_cases else float("nan"),
        "event_bearing_mean_offspring": (sum(event_offspring) / len(event_offspring)) if event_offspring else float("nan"),
    }


def equivalence_rows():
    rows = []
    for cell in r16.e_cells():
        name = cell["name"]
        prefix = RESULTS / "E" / name
        reference = r16.ref_hists(cell["ref_arm"])
        got_reps = {}
        ns_got, ns_ref = [], []
        for i in range(1, 13):
            got = r16.offspring_hist(prefix / f"rep{i:02d}" / "trace.tsv")
            ref = reference.get(i, Counter())
            got_reps[i] = got
            ns_got.append(n_of(got))
            ns_ref.append(n_of(ref))
        pooled_got = pooled_from_hists(got_reps)
        pooled_ref = pooled_from_hists(reference)
        values_got = expand(pooled_got)
        values_ref = expand(pooled_ref)
        chi, df, p, groups = homogeneity(pooled_got, pooled_ref)
        paired = [a - b for a, b in zip(ns_got, ns_ref)]
        rows.append({
            "cell": name,
            "ref_arm": cell["ref_arm"],
            "mean_got": mean_of(pooled_got),
            "mean_ref": mean_of(pooled_ref),
            "mean_ratio": mean_of(pooled_got) / mean_of(pooled_ref),
            "zero_got": zero_of(pooled_got),
            "zero_ref": zero_of(pooled_ref),
            "k_ml_got": r6stats.ml_k(values_got),
            "k_ml_ref": r6stats.ml_k(values_ref),
            "chi2": chi,
            "df": df,
            "p": p,
            "merged_bins": groups,
            "sd_n_got": sample_sd(ns_got),
            "sd_n_ref": sample_sd(ns_ref),
            "sd_paired_diff": sample_sd(paired),
        })
    return rows


def run_e():
    equiv = equivalence_rows()
    episodes = []
    for cell in r16.e_cells():
        episodes.append(episode_record(cell["name"], cell["world"], cell["alpha"]))
    r6stats.write_csv(OUT / "86_e_equivalence.csv", equiv)
    r6stats.write_csv(OUT / "86_e_episodes.csv", episodes)
    probe = chi2_sf(23.5, 21)
    print(f"chi2_sf(23.5, 21) = {probe:.4f}", flush=True)


ELIGIBLE_AGENT = {4, 5, 6, 7, 8}
HDT_TYPES = (1, 5, 6, 7, 8, 9, 10)
LOW_L = (1, 7, 8)
HIGH_L = (5, 6, 9, 10)
C_ARMS = ("s8_3_L10", "s8_3_L30", "s8_2_t1_L30")
C_MODES = ("none", "capTop", "scaleAll", "close")
BASELINE_OTHERS_HDT = 3.404
PREVIOUS_K_MOM = 0.85
STEPS = 144
UNKNOWN = 4294967295


def _mean(values):
    return sum(values) / len(values) if values else float("nan")


def class_of(path):
    flags = {}
    with open(path) as handle:
        next(handle)
        for line in handle:
            parts = line.split(",")
            flags[int(parts[0])] = parts[4] == "1"
    return flags


def nonclass_hours(mobility, hvi):
    """Mean daily hours of eligible non-class agents. hdt is the Section 5.14 discretionary sum."""
    cls = class_of(hvi)
    total, low, high, role, n = [], [], [], [], 0
    with open(mobility) as handle:
        for row in csv.DictReader(handle):
            if int(row["type"]) not in ELIGIBLE_AGENT or int(row["age"]) < 15 or cls.get(int(row["agent"]), False):
                continue
            days = float(row["days_weekday"]) + float(row["days_weekend"])
            if days <= 0:
                continue
            hdt = {t: float(row[f"hdt_{t}"]) / days for t in HDT_TYPES}
            total.append(sum(hdt.values()))
            low.append(sum(hdt[t] for t in LOW_L))
            high.append(sum(hdt[t] for t in HIGH_L))
            role.append((float(row["h_wd_role_disc"]) + float(row["h_we_role_disc"])) / days)
            n += 1
    return {"agents": n, "hdt": _mean(total), "low_l_hdt": _mean(low), "high_l_hdt": _mean(high), "role_disc": _mean(role)}


def population_hours(mobility):
    disc = high = 0.0
    with open(mobility) as handle:
        for row in csv.DictReader(handle):
            disc += float(row["h_wd_role_disc"]) + float(row["h_we_role_disc"])
            high += sum(float(row[f"hpt_{t}"]) for t in HIGH_L)
    return disc, high


def day84(run):
    from analyze import load_daily
    rows = load_daily(Path(run) / "stdout.txt")
    if len(rows) < 84:
        raise RuntimeError(f"{run} has {len(rows)} days")
    return int(rows[83]["INF"])


def moment_k_of(prefix):
    import analyze_round13 as a13
    import numpy as np
    dirs = sorted(Path(prefix).glob("rep*"))
    totals = [a13.replicate_core(d)[2] for d in dirs]
    y = np.concatenate(totals) if totals else np.asarray([])
    return {
        "replicates": len(dirs),
        "index_cases": int(y.size),
        "mean": float(y.mean()) if y.size else float("nan"),
        "k_mom": float(r6stats.mom_k(y)) if y.size > 1 else float("nan"),
        "k_ml": float(r6stats.ml_k(y)) if y.size > 1 else float("nan"),
    }


def run_c_analysis():
    state = RESULTS / "state"
    hour_rows = []
    control_rows = []
    for which in ("before", "after"):
        for arm in C_ARMS:
            cal = json.loads((state / f"c_{which}_{arm}.json").read_text())
            runs = json.loads((state / f"c_{which}_{arm}_runs.json").read_text())
            krow = moment_k_of(RESULTS / cal["prefix"])
            mob = RESULTS / f"C/{which}/{arm}/none/rep01/mobility.csv"
            hvi = RESULTS / f"C/{which}/{arm}/none/rep01/hvi.csv"
            hours = nonclass_hours(mob, hvi)
            hour_rows.append({
                "binary": which, "arm": arm, "coefficient": runs["k"], "day28": runs["day28"], "matched": int(runs["matched"]),
                "k_mom": krow["k_mom"], "k_ml": krow["k_ml"], "early_mean": krow["mean"], "index_cases": krow["index_cases"],
                "nonclass_hdt_per_day": hours["hdt"], "nonclass_low_l_hdt": hours["low_l_hdt"],
                "nonclass_high_l_hdt": hours["high_l_hdt"], "nonclass_role_disc": hours["role_disc"],
                "nonclass_agents": hours["agents"], "vs_baseline_3.404": hours["hdt"] / BASELINE_OTHERS_HDT - 1.0,
                "k_mom_above_0.85": int(krow["k_mom"] > PREVIOUS_K_MOM),
            })
            base_disc, base_high = population_hours(mob)
            infections = {}
            removed = {}
            for mode in C_MODES:
                reps = sorted((RESULTS / f"C/{which}/{arm}/{mode}").glob("rep*"))
                infections[mode] = _mean([day84(r) for r in reps])
                disc, high = population_hours(RESULTS / f"C/{which}/{arm}/{mode}/rep01/mobility.csv")
                removed[mode] = (base_disc - disc, base_high - high)
            for mode in ("capTop", "scaleAll", "close"):
                disc_removed, high_removed = removed[mode]
                averted = infections["none"] - infections[mode]
                control_rows.append({
                    "binary": which, "arm": arm, "intervention": mode, "replicates": 12,
                    "infections_day84_none": infections["none"], "infections_day84": infections[mode],
                    "infections_averted": averted,
                    "disc_hours_removed": disc_removed, "high_L_hours_removed": high_removed,
                    "averted_per_1000_disc_hours": averted / disc_removed * 1000.0 if disc_removed else float("nan"),
                    "averted_per_1000_high_L_hours": averted / high_removed * 1000.0 if high_removed else float("nan"),
                    "scale_param": runs["scale"] if mode == "scaleAll" else "",
                    "hours_source": "seed 77001 12-week infection mobility log",
                })
    # capTop versus scaleAll on the S8-3 venue-risk-10 arm, the comparison in C(b)
    for which in ("before", "after"):
        pair = {r["intervention"]: r for r in control_rows if r["binary"] == which and r["arm"] == "s8_3_L10"}
        cap = pair["capTop"]["averted_per_1000_disc_hours"]
        scale = pair["scaleAll"]["averted_per_1000_disc_hours"]
        ratio = cap / scale if scale else float("nan")
        for row in control_rows:
            if row["binary"] == which and row["arm"] == "s8_3_L10":
                row["cap_over_scale_per_1000_disc"] = ratio
                row["cap_scale_differ_by_more_than_10pct"] = int(ratio < 0.9 or ratio > 1.1)
    r6stats.write_csv(OUT / "86_c_hours.csv", hour_rows)
    r6stats.write_csv(OUT / "86_c_controls.csv", control_rows)
    for row in hour_rows:
        print(f"C {row['binary']} {row['arm']}: hdt {row['nonclass_hdt_per_day']:.3f} ({row['vs_baseline_3.404']:+.1%}) k_mom {row['k_mom']:.3f}", flush=True)


def load_episodes(path):
    out = []
    with open(path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        index = {name: pos for pos, name in enumerate(header)}
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            inf = int(parts[index["infector"]])
            day = int(parts[index["timestamp"]]) // STEPS
            out.append((int(parts[index["agent"]]), int(parts[index["episode"]]), None if inf == UNKNOWN else inf, day))
    return out


def load_single(path):
    """One row per agent from the single-trace file: the latest infection."""
    out = []
    with open(path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        index = {name: pos for pos, name in enumerate(header)}
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            inf = int(parts[index["infector"]])
            ts = int(parts[index["timestamp"]])
            if ts == UNKNOWN:
                continue
            out.append((int(parts[index["agent"]]), None if inf == UNKNOWN else inf, ts // STEPS))
    return out


def first_events(episodes):
    best = {}
    for agent, episode, inf, day in episodes:
        cur = best.get(agent)
        if cur is None or episode < cur[0]:
            best[agent] = (episode, inf, day)
    return [(agent, inf, day) for agent, (_episode, inf, day) in best.items()]


def infection_days(episodes):
    by_agent = defaultdict(list)
    for agent, _episode, _inf, day in episodes:
        by_agent[agent].append(day)
    for days in by_agent.values():
        days.sort()
    return by_agent


def offspring_counts(events, first, last, horizon=14):
    children = defaultdict(list)
    for _agent, inf, day in events:
        if inf is not None:
            children[inf].append(day)
    counts = []
    for agent, inf, day in events:
        if inf is None or not (first <= day <= last):
            continue
        counts.append(sum(1 for child_day in children.get(agent, ()) if child_day <= day + horizon))
    return counts


def run_d_analysis():
    arms = {
        "ps1_A0": RESULTS / "D/ps1_A0",
        "ps1_E": RESULTS / "D/ps1_E",
        "ps1_P0": RESULTS / "D/ps1_P0",
        "w1_b1": RESULTS / "D/w1_b1",
    }
    daily_rows = []
    window_rows = []
    windows = [(start, start + 9) for start in range(1, 111, 10)]
    for arm, directory in arms.items():
        reps = sorted(p for p in directory.glob("rep*") if (p / "episodes.tsv").exists())
        per_day_infected = [0] * 113
        per_day_twice = [0] * 113
        first_pool = {w: [] for w in windows}
        single_pool = {w: [] for w in windows}
        for rep in reps:
            days = infection_days(load_episodes(rep / "episodes.tsv"))
            firsts = []
            seconds = []
            for agent_days in days.values():
                firsts.append(agent_days[0])
                if len(agent_days) >= 2:
                    seconds.append(agent_days[1])
            for day in range(113):
                per_day_infected[day] += sum(1 for d in firsts if d <= day)
                per_day_twice[day] += sum(1 for d in seconds if d <= day)
            first = first_events(load_episodes(rep / "episodes.tsv"))
            single = load_single(rep / "trace.tsv")
            for window in windows:
                first_pool[window].extend(offspring_counts(first, *window))
                single_pool[window].extend(offspring_counts(single, *window))
        for day in range(1, 113):
            infected = per_day_infected[day]
            twice = per_day_twice[day]
            daily_rows.append({
                "arm": arm, "day": day, "infected": infected, "infected_twice": twice,
                "share_infected_twice": twice / infected if infected else float("nan"),
                "first_records_lost_by_single_trace": twice,
            })
        for window in windows:
            last = window[1]
            follow = int(last + 14 <= 112)
            row = {"arm": arm, "window_first": window[0], "window_last": last, "followup_complete": follow}
            for name, counts in (("first", first_pool[window]), ("single", single_pool[window])):
                row[f"n_{name}"] = len(counts)
                row[f"k_ml_{name}"] = r6stats.ml_k(counts) if len(counts) > 1 else float("nan")
                row[f"k_mom_{name}"] = r6stats.mom_k(counts) if len(counts) > 1 else float("nan")
                row[f"zero_{name}"] = sum(1 for c in counts if c == 0) / len(counts) if counts else float("nan")
            k1, k2 = row["k_ml_first"], row["k_ml_single"]
            if k1 and k2 and math.isfinite(k1) and math.isfinite(k2) and k2 != 0:
                row["k_ml_ratio_first_over_single"] = k1 / k2
                row["k_ml_within_5pct"] = int(abs(k1 / k2 - 1.0) <= 0.05)
            else:
                row["k_ml_ratio_first_over_single"] = float("nan")
                row["k_ml_within_5pct"] = 0
            window_rows.append(row)
            print(f"D {arm} {window}: k_ml first {row['k_ml_first']} single {row['k_ml_single']} ratio {row['k_ml_ratio_first_over_single']}", flush=True)
    r6stats.write_csv(OUT / "86_d_daily.csv", daily_rows)
    r6stats.write_csv(OUT / "86_d_windows.csv", window_rows)


def run_b2_analysis():
    trials = json.loads((RESULTS / "state" / "b2_trials.json").read_text())
    final = json.loads((RESULTS / "state" / "b2_final.json").read_text())["final36"]
    import analyze_round13 as a13
    import numpy as np
    dirs = [Path(p) for p in json.loads((RESULTS / "state" / "b2_final.json").read_text())["dirs"]]
    y = np.concatenate([a13.replicate_core(d)[2] for d in dirs])
    zero = float(np.mean(y == 0))
    nb = float(r6stats.nb_pmf(float(y.mean()), float(r6stats.ml_k(y)), 0))
    rows = []
    for row in trials:
        rows.append({
            "phase": row["phase"], "iteration": row["iteration"], "seeds": "89001-89012",
            "rate": row["rate"], "coefficient": row["coefficient"], "mean_offspring": row["R"],
            "mean_vs_0.88": row["R"] / 0.88 - 1.0, "k_ml": row["k_ml"], "k_ml_vs_0.27": row["k_ml"] - 0.27,
            "k_mom": row["k_mom"], "index_cases": row["index_cases"], "day28": row["day28"],
            "both_targets": int(abs(row["R"] / 0.88 - 1.0) <= 0.03 and abs(row["k_ml"] - 0.27) <= 0.03),
        })
    rows.append({
        "phase": "final36", "iteration": "", "seeds": "89001-89036",
        "rate": final and json.loads((RESULTS / "state" / "b2_final.json").read_text())["best_trial"]["rate"],
        "coefficient": json.loads((RESULTS / "state" / "b2_final.json").read_text())["best_trial"]["coefficient"],
        "mean_offspring": float(y.mean()), "mean_vs_0.88": float(y.mean()) / 0.88 - 1.0,
        "k_ml": float(r6stats.ml_k(y)), "k_ml_vs_0.27": float(r6stats.ml_k(y)) - 0.27,
        "k_mom": float(r6stats.mom_k(y)), "index_cases": int(y.size), "day28": final["day28"],
        "zero_share": zero, "nb_zero_share": nb, "zero_gap_points": 100.0 * (zero - nb),
        "both_targets": int(abs(float(y.mean()) / 0.88 - 1.0) <= 0.03 and abs(float(r6stats.ml_k(y)) - 0.27) <= 0.03),
    })
    r6stats.write_csv(OUT / "86_b2_trials.csv", rows)
    print(f"B2 final36 mean {float(y.mean()):.4f} k {float(r6stats.ml_k(y)):.4f} gap {100*(zero-nb):.3f}", flush=True)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "E"
    if cmd == "E":
        run_e()
    elif cmd == "C":
        run_c_analysis()
    elif cmd == "D":
        run_d_analysis()
    elif cmd == "B2":
        run_b2_analysis()
    else:
        raise SystemExit(f"unknown command {cmd}")


if __name__ == "__main__":
    main()
