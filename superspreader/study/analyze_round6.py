#!/usr/bin/env python3
"""Round 6 (note 42) analyses. Reads stored traces; the run scripts are in run_round6.py.

  python3 superspreader/study/analyze_round6.py r63
"""

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from analyze_round2 import p_total_gt  # noqa: E402
from r6stats import (  # noqa: E402
    BOOT,
    BOOT_SEED,
    bootstrap_pack,
    cv2,
    flatten_row,
    gamma_fit,
    index_table,
    interval,
    load_events,
    mean_of,
    ml_k,
    mom_k,
    pack,
    pool_sufficient,
    trait_sufficient,
    write_csv,
)

OUT = HERE.parent
RESULTS = HERE / "results"
K0_PS1 = 4.661862094720031  # PS1 A0 early k, old map
PS1_ARMS = [
    # label, directory, distribution, nominal a, rho
    ("P0", "P0", "gamma", 0.3, 0.0),
    ("P25", "P25", "gamma", 0.3, 0.25),
    ("P50", "P50", "gamma", 0.3, 0.5),
    ("P100", "P100", "gamma", 0.3, 1.0),
    ("P25k", "P25k", "gamma", 0.08, 0.25),
    ("P100ln", "P100ln", "lognormal", 0.3, 1.0),
]
PS1_EARLY_K = {"P0": 0.2950645, "P25": 0.4707108, "P50": 0.6320079, "P100": 0.9541993, "P25k": 0.2695031, "P100ln": 0.4638499}


def predicted_k(s, k0=K0_PS1):
    if s is None or s <= 0:
        return None
    return 1.0 / ((1.0 + 1.0 / s) * (1.0 + 1.0 / k0) - 1.0)


def read_traits(path):
    traits = []
    with open(path) as handle:
        next(handle)
        for line in handle:
            parts = line.split(",", 2)
            traits.append(float(parts[1]))
    return np.asarray(traits, dtype=np.float64)


def shape_of(stat, dist):
    if dist == "lognormal":
        c = cv2(stat)
        return None if c is None else 1.0 / c
    return gamma_fit(stat)


def r63():
    rows = []
    for label, directory, dist, a, rho in PS1_ARMS:
        base = RESULTS / "ps" / "ps1" / directory
        reps = sorted(base.glob("rep*"))
        pop_stats, idx_stats, all_stats, offspring = [], [], [], []
        for rep in reps:
            traits = read_traits(RESULTS / "round6" / "r63" / directory / rep.name / "agents_trait.csv")
            ids, total, event = index_table(rep / "trace.tsv")
            infected = set()
            with open(rep / "trace.tsv") as handle:
                header = handle.readline().rstrip("\n").split("\t")
                col = header.index("agent")
                for line in handle:
                    infected.add(int(line.split("\t", col + 1)[col]))
            pop_stats.append(trait_sufficient(traits))
            idx_stats.append(trait_sufficient(traits[ids]))
            all_stats.append(trait_sufficient(traits[np.fromiter(infected, dtype=np.int64)]))
            offspring.append((total, event))
        total = np.concatenate([o[0] for o in offspring])
        event = np.concatenate([o[1] for o in offspring])
        point = pack(total, event, nb=False)

        def stats_for(pick):
            pop = pool_sufficient([pop_stats[i] for i in pick])
            idx = pool_sufficient([idx_stats[i] for i in pick])
            allv = pool_sufficient([all_stats[i] for i in pick])
            tot = np.concatenate([offspring[i][0] for i in pick])
            s_pop, s_idx, s_all = shape_of(pop, dist), shape_of(idx, dist), shape_of(allv, dist)
            return {
                "shape_population": s_pop,
                "shape_index": s_idx,
                "shape_all_infected": s_all,
                "mean_trait_population": mean_of(pop),
                "mean_trait_index": mean_of(idx),
                "mean_trait_all_infected": mean_of(allv),
                "pred_k_population_fitted": predicted_k(s_pop),
                "pred_k_index_fitted": predicted_k(s_idx),
                "pred_k_all_infected_fitted": predicted_k(s_all),
                "obs_k_mom": mom_k(tot),
                "obs_k_ml": ml_k(tot),
            }

        everything = list(range(len(reps)))
        est = stats_for(everything)
        rng = np.random.default_rng(BOOT_SEED + len(label))
        draws = {key: [] for key in est}
        for _ in range(BOOT):
            pick = rng.integers(0, len(reps), size=len(reps)).tolist()
            got = stats_for(pick)
            for key, value in got.items():
                draws[key].append(value)
        ci = {key: interval(values) for key, values in draws.items()}
        nominal = a + rho
        row = {
            "arm": label,
            "distribution": dist,
            "nominal_a": a,
            "rho": rho,
            "nominal_a_plus_rho": nominal,
            "replicates": len(reps),
            "index_cases": int(total.size),
            "early_R": point["early_R"],
        }
        for key, value in est.items():
            row[key] = value
            row[key + "_low"], row[key + "_high"] = ci[key]
        row["pred_k_population_nominal"] = predicted_k(a)
        if dist == "lognormal":
            # a + rho is a gamma result; the lognormal arm has no nominal shape to compare with.
            row["nominal_a_plus_rho"] = None
            row["pred_k_index_nominal"] = None
            row["shape_index_over_nominal"] = None
        else:
            row["pred_k_index_nominal"] = predicted_k(nominal)
            row["shape_index_over_nominal"] = est["shape_index"] / nominal if est["shape_index"] else None
        row["obs_k_mom_over_pred_population"] = est["obs_k_mom"] / est["pred_k_population_fitted"]
        row["obs_k_mom_over_pred_index"] = est["obs_k_mom"] / est["pred_k_index_fitted"]
        row["obs_k_ml_over_pred_population"] = est["obs_k_ml"] / est["pred_k_population_fitted"]
        row["obs_k_ml_over_pred_index"] = est["obs_k_ml"] / est["pred_k_index_fitted"]
        row["ps1_early_k_note17"] = PS1_EARLY_K[label]
        rows.append(row)
        print(
            f"{label}: shape pop {est['shape_population']:.3f} idx {est['shape_index']:.3f} all {est['shape_all_infected']:.3f} "
            f"obs k {est['obs_k_mom']:.3f}/{est['obs_k_ml']:.3f} pred pop {est['pred_k_population_fitted']:.3f} idx {est['pred_k_index_fitted']:.3f}",
            flush=True,
        )
    write_csv(OUT / "43_r63_survey_vs_infected.csv", rows)
    return rows


R61_REUSED_DIRS = {
    ("none", 0): RESULTS / "round2" / "r36" / "baseline",
    ("none", 600): RESULTS / "round2" / "r42" / "cap100_f600",
    ("none", 1091): RESULTS / "round2" / "r42" / "cap100_f1091",
    ("0.3", 0): RESULTS / "round2" / "r3cal" / "r35_E" / "round0",
}


def day28_of(run_dir):
    from analyze import load_daily
    rows = load_daily(Path(run_dir) / "stdout.txt")
    return int(rows[27]["INF"])


def event_file(trace):
    own = trace.parent / "events.tsv"
    if own.exists():
        return own
    sibling = trace.parent.parent / f"{trace.parent.name}.events.tsv"
    return sibling if sibling.exists() else None


def cell_runs(shape, factor):
    """Run directories of one R6-1 cell, and the note on where they came from."""
    if (shape, factor) in R61_REUSED_DIRS:
        base = R61_REUSED_DIRS[(shape, factor)]
        return sorted(p.parent for p in base.glob("rep*/trace.tsv")), "reused from round 3 to 5", None
    state = json.loads((HERE / "results" / "round6" / "state" / f"r61_a{shape}_f{factor}.json").read_text())
    base = HERE / "results" / "round6" / state["prefix"]
    return sorted(p.parent for p in base.glob("rep*/trace.tsv")), "new in round 6", state


def collect_cell(shape, factor):
    runs, source, state = cell_runs(shape, factor)
    reps, days = [], []
    for run in runs:
        trace = run / "trace.tsv"
        events = None
        if factor > 0:
            path = event_file(trace)
            if path is None:
                raise RuntimeError(f"no event log for {trace}")
            events = load_events(path)
        ids, total, event = index_table(trace, events)
        if np.any(event > total):
            raise RuntimeError(f"event offspring exceed total in {trace}")
        reps.append((total, event))
        days.append(day28_of(run))
    return reps, days, source, state


def r61():
    summary, joint = [], []
    for factor in (0, 300, 600, 1091):
        for shape in ("none", "1.0", "0.5", "0.3"):
            label = f"a{shape}_f{factor}"
            print("R6-1", label, flush=True)
            reps, days, source, state = collect_cell(shape, factor)
            total = np.concatenate([r[0] for r in reps])
            event = np.concatenate([r[1] for r in reps])
            point = pack(total, event)
            ci = bootstrap_pack(reps, seed=BOOT_SEED + 7 * len(summary))
            row = flatten_row(label, point, ci)
            row.update({
                "multiplier_shape": shape,
                "event_factor": factor,
                "replicates": len(reps),
                "day28_mean": float(np.mean(days)),
                "day28_vs_6211.25": float(np.mean(days)) / 6211.25 - 1.0,
                "background_coefficient": state["k"] if state else None,
                "calibration_matched": state["matched"] if state else True,
                "source": source,
            })
            summary.append(row)
            counts = Counter(zip(total.tolist(), event.tolist()))
            for (off, ev), number in sorted(counts.items()):
                joint.append({"cell": label, "offspring_total": off, "offspring_at_events": ev, "index_cases": number})
            print(
                f"   n {point['index_cases']} day28 {np.mean(days):.0f} R {point['early_R']:.3f} kmom {point['k_mom']:.3f} kml {point['k_ml']:.3f} "
                f"zero {point['share_0']:.3f} nb_ml0 {point['nb_ml_share_0']:.3f} events {point['event_offspring_share']}",
                flush=True,
            )
    write_csv(OUT / "43_r61_grid_summary.csv", summary)
    write_csv(OUT / "43_r61_offspring.csv", joint)
    return summary


# ---------------------------------------------------------------- R6-2

def fisher_ci(r, n, z=1.959964):
    if n <= 3 or r is None or abs(r) >= 1:
        return None, None
    center = math.atanh(r)
    half = z / math.sqrt(n - 3)
    return math.tanh(center - half), math.tanh(center + half)


def pearson(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    if x.size < 3 or x.std() == 0 or y.std() == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def average_ranks(values):
    values = np.asarray(values, dtype=float)
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(values.size, dtype=float)
    sorted_values = values[order]
    start = 0
    while start < values.size:
        end = start
        while end + 1 < values.size and sorted_values[end + 1] == sorted_values[start]:
            end += 1
        ranks[order[start:end + 1]] = 0.5 * (start + end) + 1.0
        start = end + 1
    return ranks


def spearman(x, y):
    return pearson(average_ranks(x), average_ranks(y))


def required_pairs(r, power_z=0.841621, alpha_z=1.959964):
    if r is None or r < 0.05:
        return None
    return math.ceil(((alpha_z + power_z) / math.atanh(r)) ** 2 + 3)


def episode_pairs(run_dir, last_day):
    """Pairs (episode 1, episode 2) of agents whose two episodes are both logged, with offspring in 14 days."""
    episodes = {}
    children = defaultdict(list)
    with open(run_dir / "episodes.tsv") as handle:
        header = handle.readline().rstrip("\n").split("\t")
        col = {name: i for i, name in enumerate(header)}
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            agent = int(parts[col["agent"]])
            episode = int(parts[col["episode"]])
            stamp = int(parts[col["timestamp"]])
            infector = int(parts[col["infector"]])
            infector_stamp = int(parts[col["infectorTimestamp"]])
            episodes.setdefault(agent, {})[episode] = stamp
            if infector != UNKNOWN_ID:
                children[(infector, infector_stamp)].append(stamp // STEPS_PER_DAY)
    pairs = []
    multi = 0
    for agent, eps in episodes.items():
        if len(eps) >= 3:
            multi += 1
        if 1 in eps and 2 in eps:
            t1, t2 = eps[1], eps[2]
            d1, d2 = t1 // STEPS_PER_DAY, t2 // STEPS_PER_DAY
            if d2 + 14 > last_day:
                continue
            o1 = sum(1 for d in children.get((agent, t1), ()) if d <= d1 + 14)
            o2 = sum(1 for d in children.get((agent, t2), ()) if d <= d2 + 14)
            pairs.append((agent, d1, o1, d2, o2))
    with_two = sum(1 for eps in episodes.values() if 2 in eps and 1 in eps)
    return pairs, with_two, multi, len(episodes)


UNKNOWN_ID = 4294967295
STEPS_PER_DAY = 144


def r62():
    from analyze import load_daily
    pair_rows, summary = [], []
    for arm in ("P0", "E", "A0"):
        base = HERE / "results" / "round6" / "r62" / arm
        runs = sorted(base.glob("rep*"))
        per_rep = []
        agents_two = agents_three = infected = 0
        for run in runs:
            rows = load_daily(run / "stdout.txt")
            last_day = len(rows) - 1
            ni = np.asarray([int(r.get("NI", 0)) for r in rows], dtype=float)
            smooth = np.convolve(ni, np.ones(7) / 7.0, mode="same")
            pairs, with_two, multi, n_agents = episode_pairs(run, last_day)
            agents_two += with_two
            agents_three += multi
            infected += n_agents
            records = []
            for agent, d1, o1, d2, o2 in pairs:
                i1 = float(smooth[min(d1, len(smooth) - 1)])
                i2 = float(smooth[min(d2, len(smooth) - 1)])
                records.append((agent, d1, o1, d2, o2, i1, i2))
                pair_rows.append({
                    "arm": arm, "rep": run.name, "agent": agent, "day1": d1, "offspring1": o1, "day2": d2, "offspring2": o2,
                    "incidence1_7day": i1, "incidence2_7day": i2,
                    "similar_incidence": int(i1 > 0 and i2 > 0 and 0.5 <= i2 / i1 <= 2.0),
                })
            per_rep.append(records)
        allp = [r for rep in per_rep for r in rep]
        x = np.asarray([r[2] for r in allp], dtype=float)
        y = np.asarray([r[4] for r in allp], dtype=float)
        sim = [r for r in allp if i_ok(r)]
        xs = np.asarray([r[2] for r in sim], dtype=float)
        ys = np.asarray([r[4] for r in sim], dtype=float)

        def boot(selector):
            rng = np.random.default_rng(BOOT_SEED + len(arm))
            vals_p, vals_s = [], []
            for _ in range(BOOT):
                pick = rng.integers(0, len(per_rep), size=len(per_rep))
                rows_ = [r for i in pick for r in per_rep[i] if selector(r)]
                if len(rows_) < 5:
                    continue
                a = [r[2] for r in rows_]
                b = [r[4] for r in rows_]
                vals_p.append(pearson(a, b))
                vals_s.append(spearman(a, b))
            return interval(vals_p), interval(vals_s)

        (pp_lo, pp_hi), (ps_lo, ps_hi) = boot(lambda r: True)
        (qp_lo, qp_hi), (qs_lo, qs_hi) = boot(i_ok)
        rp, rs = pearson(x, y), spearman(x, y)
        rp_sim, rs_sim = pearson(xs, ys), spearman(xs, ys)
        fp = fisher_ci(rp, len(x))
        fps = fisher_ci(rp_sim, len(xs))
        summary.append({
            "arm": arm,
            "replicates": len(runs),
            "agents_infected_any": infected,
            "agents_with_two_logged_episodes": agents_two,
            "agents_with_three_or_more": agents_three,
            "pairs_both_observed": len(x),
            "mean_offspring_ep1": float(x.mean()), "mean_offspring_ep2": float(y.mean()),
            "pearson": rp, "pearson_low": pp_lo, "pearson_high": pp_hi, "pearson_fisher_low": fp[0], "pearson_fisher_high": fp[1],
            "spearman": rs, "spearman_low": ps_lo, "spearman_high": ps_hi,
            "pairs_similar_incidence": len(xs),
            "mean_offspring_ep1_similar": float(xs.mean()), "mean_offspring_ep2_similar": float(ys.mean()),
            "pearson_similar": rp_sim, "pearson_similar_low": qp_lo, "pearson_similar_high": qp_hi,
            "pearson_similar_fisher_low": fps[0], "pearson_similar_fisher_high": fps[1],
            "spearman_similar": rs_sim, "spearman_similar_low": qs_lo, "spearman_similar_high": qs_hi,
            "pairs_needed_80pct_pearson": required_pairs(rp),
            "pairs_needed_80pct_pearson_similar": required_pairs(rp_sim),
            "pairs_needed_80pct_spearman": required_pairs(rs),
        })
        print(f"R6-2 {arm}: pairs {len(x)} ({len(xs)} similar) pearson {rp:.3f} spearman {rs:.3f} similar {rp_sim:.3f}", flush=True)
    plain = [{key: row[key] for key in ("arm", "rep", "agent", "day1", "offspring1", "day2", "offspring2")} for row in pair_rows]
    write_csv(OUT / "43_r62_repeat_pairs.csv", plain)
    write_csv(OUT / "43_r62_repeat_pairs_extended.csv", pair_rows)
    horizon_rows = []
    for arm in ("P0", "E", "A0"):
        days = [row["day2"] for row in pair_rows if row["arm"] == arm]
        for weeks in (4, 6, 8, 10, 12, 14, 16):
            horizon = 7 * weeks
            horizon_rows.append({"arm": arm, "horizon_weeks": weeks, "pairs_both_observed_8_replicates": sum(1 for d in days if d + 14 <= horizon - 1),
                                 "pairs_per_replicate": sum(1 for d in days if d + 14 <= horizon - 1) / 8.0})
    write_csv(OUT / "43_r62_pairs_by_horizon.csv", horizon_rows)
    joint = Counter((row["arm"], row["similar_incidence"], row["offspring1"], row["offspring2"]) for row in pair_rows)
    write_csv(OUT / "43_r62_pairs_joint.csv", [
        {"arm": a, "similar_incidence": sim, "offspring1": o1, "offspring2": o2, "pairs": n} for (a, sim, o1, o2), n in sorted(joint.items())
    ])
    write_csv(OUT / "43_r62_summary.csv", summary)
    return summary


def i_ok(record):
    return record[5] > 0 and record[6] > 0 and 0.5 <= record[6] / record[5] <= 2.0


# ---------------------------------------------------------------- R6-4

PS1_VALUES = {"P25": 0.471, "P50": 0.632, "P100": 0.954, "P25k": 0.270, "P100ln": 0.464}
R64_ARMS = ["E", "P0", "P25", "P50", "P100", "P25k", "P100ln"]


def daily_tables(run_dir):
    from analyze import load_daily, prevalence
    rows = load_daily(run_dir / "stdout.txt")
    return [(i + 1, int(r.get("NI", 0)), prevalence(r), int(r.get("INF", 0))) for i, r in enumerate(rows)]


def growth_rate(series, first=7, last=28):
    days = np.arange(first, last + 1, dtype=float)
    values = np.asarray([series[d - 1][1] for d in days.astype(int)], dtype=float)
    if np.any(values <= 0):
        return None
    slope = np.polyfit(days, np.log(values), 1)[0]
    return float(slope)


def mean_interval(values, seed):
    values = [v for v in values if v is not None]
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    draws = [float(arr[rng.integers(0, arr.size, size=arr.size)].mean()) for _ in range(BOOT)]
    return float(arr.mean()), interval(draws)


def r64():
    summary, daily = [], []
    per_arm = {}
    for arm_index, arm in enumerate(R64_ARMS):
        base = HERE / "results" / "round6" / "r64" / arm
        runs = sorted(base.glob("rep*"))
        state = json.loads((HERE / "results" / "round6" / "state" / f"r64_{arm}.json").read_text())
        reps, tables, traits = [], [], []
        for run in runs:
            ids, total, event = index_table(run / "trace.tsv")
            reps.append((total, event))
            table = daily_tables(run)
            tables.append(table)
            for day, ni, prev, cum in table:
                daily.append({"arm": arm, "rep": run.name, "day": day, "new_infections": ni, "prevalence": prev, "cumulative": cum})
            shed = {}
            with open(run / "trace.tsv") as handle:
                header = handle.readline().rstrip("\n").split("\t")
                col = {name: i for i, name in enumerate(header)}
                for line in handle:
                    parts = line.split("\t")
                    shed[int(parts[col["agent"]])] = float(parts[col["shed"]])
            traits.append(float(np.mean([shed[a] for a in ids.tolist()])))
        total = np.concatenate([r[0] for r in reps])
        event = np.concatenate([r[1] for r in reps])
        point = pack(total, event)
        ci = bootstrap_pack(reps, seed=BOOT_SEED + 11 * arm_index)
        row = flatten_row(arm, point, ci)
        row = {"arm": row.pop("cell"), **row}
        d28 = [t[27][3] for t in tables]
        d70 = [t[69][3] for t in tables]
        d112 = [t[111][3] for t in tables]
        peaks = [max(r[2] for r in t) for t in tables]
        peak_days = [max(t, key=lambda r: r[2])[0] for t in tables]
        growth = [growth_rate(t) for t in tables]
        for name, values in (("day28", d28), ("day70", d70), ("day112", d112), ("peak_prevalence", peaks), ("peak_day", peak_days), ("growth_rate_7_28", growth), ("mean_shed_index_cases", traits)):
            m, (lo, hi) = mean_interval(values, BOOT_SEED + 97 * arm_index + len(name))
            row[name] = m
            row[name + "_low"], row[name + "_high"] = lo, hi
        row["replicates"] = len(runs)
        row["background_coefficient"] = state["k"]
        row["calibration_matched"] = state["matched"]
        row["day28_vs_6000"] = row["day28"] / 6000.0 - 1.0
        row["doubling_time_days_7_28"] = math.log(2) / row["growth_rate_7_28"] if row["growth_rate_7_28"] else None
        per_arm[arm] = {"d28": d28, "d70": d70, "d112": d112}
        summary.append(row)
        print(f"R6-4 {arm}: day28 {row['day28']:.0f} R {row['early_R']:.3f} kmom {row['k_mom']:.3f} kml {row['k_ml']:.3f} day112 {row['day112']:.0f}", flush=True)
    rng = np.random.default_rng(BOOT_SEED + 5)
    e = per_arm["E"]
    for row in summary:
        arm = row["arm"]
        for tag in ("d70", "d112"):
            a = np.asarray(per_arm[arm][tag], dtype=float)
            b = np.asarray(e[tag], dtype=float)
            ratios = []
            for _ in range(BOOT):
                ra = a[rng.integers(0, a.size, size=a.size)].mean()
                rb = b[rng.integers(0, b.size, size=b.size)].mean()
                ratios.append(ra / rb)
            lo, hi = interval(ratios)
            row[f"ratio_{tag}_to_E"] = float(a.mean() / b.mean())
            row[f"ratio_{tag}_to_E_low"], row[f"ratio_{tag}_to_E_high"] = lo, hi
    # Final-size ratio adjusted to a common day-28 count: within-arm regression of the day-N count on the
    # day-28 count with one common slope, each arm moved to the target of 6,000.
    def adjusted(parts, tag):
        xs, ys, labels = [], [], []
        for arm, data in parts.items():
            xs += list(data["d28"])
            ys += list(data[tag])
            labels += [arm] * len(data["d28"])
        xs, ys = np.asarray(xs, dtype=float), np.asarray(ys, dtype=float)
        sxy = sxx = 0.0
        means = {}
        for arm in parts:
            mask = np.asarray([lab == arm for lab in labels])
            means[arm] = (xs[mask].mean(), ys[mask].mean())
            sxy += float(((xs[mask] - xs[mask].mean()) * (ys[mask] - ys[mask].mean())).sum())
            sxx += float(((xs[mask] - xs[mask].mean()) ** 2).sum())
        slope = sxy / sxx
        return slope, {arm: m[1] + slope * (6000.0 - m[0]) for arm, m in means.items()}

    for tag in ("d70", "d112"):
        slope, adj = adjusted(per_arm, tag)
        rng2 = np.random.default_rng(BOOT_SEED + 77 + len(tag))
        slopes, ratios = [], {arm: [] for arm in per_arm}
        for _ in range(BOOT):
            boot_parts = {}
            for arm, data in per_arm.items():
                pick = rng2.integers(0, len(data["d28"]), size=len(data["d28"]))
                boot_parts[arm] = {key: np.asarray(values)[pick] for key, values in data.items()}
            s, a = adjusted(boot_parts, tag)
            slopes.append(s)
            for arm in per_arm:
                ratios[arm].append(a[arm] / a["E"])
        slo, shi = interval(slopes)
        for row in summary:
            arm = row["arm"]
            row[f"adjusted_{tag}"] = adj[arm]
            row[f"adjusted_ratio_{tag}_to_E"] = adj[arm] / adj["E"]
            row[f"adjusted_ratio_{tag}_to_E_low"], row[f"adjusted_ratio_{tag}_to_E_high"] = interval(ratios[arm])
            row[f"adjustment_slope_{tag}_per_day28_infection"] = slope
            row[f"adjustment_slope_{tag}_low"], row[f"adjustment_slope_{tag}_high"] = slo, shi
    write_csv(OUT / "43_r64_summary.csv", summary)
    write_csv(OUT / "43_r64_daily.csv", daily)
    return summary


# ---------------------------------------------------------------- R6-5

CHAIN_CAP = 5000
HOSPITAL_TYPE = 12
R65_DIRS = {
    "w10": ("round6", "r65/w10"),
    "w30 (R3-4)": ("round2", "r34/shape0.03"),
    "w100": ("round6", "r65/w100"),
    "w300": ("round6", "r65/w300"),
    "unsplit": ("round6", "r65/unsplit"),
}


def dwass_pmf(mean_r, k, n_max):
    """P(total progeny = n) for n = 1..n_max of one introduction, negative-binomial offspring."""
    p = k / (k + mean_r)
    out = np.empty(n_max)
    for n in range(1, n_max + 1):
        out[n - 1] = math.exp(math.log(1.0 / n) + log_nbinom_pmf(n - 1, n * k, p))
    return out


def log_nbinom_pmf(failures, successes, p):
    return (
        math.lgamma(failures + successes) - math.lgamma(successes) - math.lgamma(failures + 1)
        + successes * math.log(p) + failures * math.log(1.0 - p)
    )


def longest_distribution(mean_r, k, n_chains, n_max=20000):
    pmf = dwass_pmf(mean_r, k, n_max)
    cdf = np.cumsum(pmf)
    # P(longest <= m) = cdf(m) ** n_chains
    with np.errstate(divide="ignore"):
        logf = n_chains * np.log(np.clip(cdf, 1e-300, 1.0))
    f = np.exp(logf)
    def quantile(q):
        idx = int(np.searchsorted(f, q))
        return idx + 1
    return quantile(0.025), quantile(0.5), quantile(0.975), f


def chains_with_types(trace_path):
    """Chain sizes and, per chain, its hospital infections, from one trace."""
    agent_parent, loc_type = {}, {}
    with open(trace_path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        col = {name: i for i, name in enumerate(header)}
        for line in handle:
            parts = line.split("\t")
            agent = int(parts[col["agent"]])
            infector = int(parts[col["infector"]])
            agent_parent[agent] = None if infector == UNKNOWN_ID else infector
            loc_type[agent] = int(parts[col["locType"]])
    children = defaultdict(list)
    roots = []
    for agent, parent in agent_parent.items():
        if parent is not None and parent in agent_parent:
            children[parent].append(agent)
        else:
            roots.append(agent)
    sizes, hospital_in_chain = [], []
    for root in roots:
        stack = [root]
        seen = set()
        size = hosp = 0
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            size += 1
            hosp += loc_type[node] == HOSPITAL_TYPE
            stack.extend(children.get(node, ()))
        sizes.append(size)
        hospital_in_chain.append(hosp)
    # children of hospital-infected agents
    h_children = h_children_in_hospital = h_cases = 0
    for agent, kids in children.items():
        if loc_type[agent] == HOSPITAL_TYPE:
            h_children += len(kids)
            h_children_in_hospital += sum(1 for c in kids if loc_type[c] == HOSPITAL_TYPE)
    h_cases = sum(1 for a, t in loc_type.items() if t == HOSPITAL_TYPE)
    types = Counter(loc_type.values())
    return {
        "sizes": np.asarray(sizes, dtype=np.int64),
        "hospital_in_chain": np.asarray(hospital_in_chain, dtype=np.int64),
        "nodes": len(agent_parent),
        "hospital_cases": h_cases,
        "hospital_children": h_children,
        "hospital_children_in_hospital": h_children_in_hospital,
        "offspring": np.asarray([len(children.get(a, ())) for a in agent_parent], dtype=np.int32),
        "types": types,
    }


def r65_sets():
    """(label, directory, note) for every R6-5 replicate set. The last set of an arm is its primary set."""
    out = []
    for label, (root, rel) in R65_DIRS.items():
        if root == "round2":
            out.append((label, HERE / "results" / root / rel, "reused from R3-4", True))
            continue
        name = label
        state = json.loads((HERE / "results" / "round6" / "state" / f"r65_{name}_final.json").read_text())
        sets = state.get("sets") or [{"dir": f"r65/{name}", "k": state["k"], "mean_40": state["mean_40"]}]
        for i, item in enumerate(sets):
            primary = i == len(sets) - 1
            out.append((label if primary else f"{label} (set {i + 1}, superseded)", HERE / "results" / "round6" / item["dir"], f"k {item['k']:.6g}, run set {item['dir'].split('/')[-1]}", primary))
    return out


def r65():
    rows, hist_rows = [], []
    for index, (label, base, note, primary) in enumerate(r65_sets()):
        reps = [chains_with_types(p) for p in sorted(base.glob("rep*/trace.tsv"))]
        sizes = np.concatenate([r["sizes"] for r in reps])
        offspring = np.concatenate([r["offspring"] for r in reps])
        mean_r = float(offspring.mean())
        k = mom_k(offspring)
        n = int(sizes.size)
        longest = int(sizes.max())
        q_lo, q_med, q_hi, f = longest_distribution(mean_r, k, n)
        p_ge = 1.0 - (float(f[longest - 2]) if longest >= 2 else 0.0)
        groups = [sizes[i:i + 5] for i in range(0, n - (n % 5), 5)]
        five_obs = float(np.mean([g.sum() > 50 for g in groups]))
        five_exact = float(p_total_gt(mean_r, k, 5, 50))
        hist = Counter(sizes.tolist())
        for size in sorted(hist):
            hist_rows.append({"arm": label, "chain_size": size, "chains": hist[size]})
        longest_rep = max(range(len(reps)), key=lambda i: int(reps[i]["sizes"].max()))
        li = int(np.argmax(reps[longest_rep]["sizes"]))
        hosp_all = sum(r["types"].get(HOSPITAL_TYPE, 0) for r in reps) / sum(r["nodes"] for r in reps)
        hosp_longest = int(reps[longest_rep]["hospital_in_chain"][li]) / longest

        def stat(parts, name):
            if name == "hosp_share":
                return sum(p["types"].get(HOSPITAL_TYPE, 0) for p in parts) / sum(p["nodes"] for p in parts)
            if name == "hosp_children_mean":
                c = sum(p["hospital_cases"] for p in parts)
                return sum(p["hospital_children"] for p in parts) / c if c else None
            if name == "hosp_children_in_hosp":
                c = sum(p["hospital_children"] for p in parts)
                return sum(p["hospital_children_in_hospital"] for p in parts) / c if c else None
            if name == "mean_offspring":
                return float(np.concatenate([p["offspring"] for p in parts]).mean())
            if name.startswith("above"):
                t = int(name[5:])
                return float(np.sum(np.concatenate([p["sizes"] for p in parts]) > t))
            if name == "longest":
                return float(max(p["sizes"].max() for p in parts))
        rng = np.random.default_rng(BOOT_SEED + 31 * index)
        names = ["hosp_share", "hosp_children_mean", "hosp_children_in_hosp", "mean_offspring", "above10", "above50", "above100", "above200", "above500", "longest"]
        draws = {name: [] for name in names}
        for _ in range(BOOT):
            pick = rng.integers(0, len(reps), size=len(reps))
            parts = [reps[i] for i in pick]
            for name in names:
                draws[name].append(stat(parts, name))
        ci = {name: interval(v) for name, v in draws.items()}
        row = {
            "arm": label, "set_note": note, "primary": primary, "replicates": len(reps), "chains": n, "nodes": int(offspring.size),
            "mean_offspring": mean_r, "mean_offspring_low": ci["mean_offspring"][0], "mean_offspring_high": ci["mean_offspring"][1],
            "k_mom": k,
            "longest_chain": longest, "longest_low": ci["longest"][0], "longest_high": ci["longest"][1],
            "dwass_longest_median": q_med, "dwass_longest_2.5pct": q_lo, "dwass_longest_97.5pct": q_hi,
            "p_longest_at_least_observed": p_ge,
            "five_seed_observed": five_obs, "five_seed_groups": len(groups), "five_seed_exact": five_exact,
            "hospital_share_of_infections": hosp_all, "hospital_share_low": ci["hosp_share"][0], "hospital_share_high": ci["hosp_share"][1],
            "hospital_share_of_longest_chain": hosp_longest,
            "hospital_cases": sum(r["hospital_cases"] for r in reps),
            "mean_offspring_of_hospital_cases": stat(reps, "hosp_children_mean"),
            "mean_offspring_of_hospital_cases_low": ci["hosp_children_mean"][0], "mean_offspring_of_hospital_cases_high": ci["hosp_children_mean"][1],
            "share_children_also_in_hospital": stat(reps, "hosp_children_in_hosp"),
            "share_children_also_in_hospital_low": ci["hosp_children_in_hosp"][0], "share_children_also_in_hospital_high": ci["hosp_children_in_hosp"][1],
        }
        for t in (10, 50, 100, 200, 500):
            row[f"chains_above_{t}"] = int(np.sum(sizes > t))
            row[f"chains_above_{t}_low"], row[f"chains_above_{t}_high"] = ci[f"above{t}"]
        rows.append(row)
        print(f"R6-5 {label}: chains {n} mean {mean_r:.4f} k {k:.4f} longest {longest} dwass median {q_med} p {p_ge:.3f} hospital children {row['share_children_also_in_hospital']:.3f}", flush=True)
    write_csv(OUT / "43_r65_ward_sweep.csv", rows)
    primary = {row["arm"] for row in rows if row["primary"]}
    write_csv(OUT / "43_r65_chain_hist.csv", [row for row in hist_rows if row["arm"] in primary])
    write_csv(OUT / "43_r65_chain_hist_all_sets.csv", hist_rows)
    return rows


# ---------------------------------------------------------------- R6-6

R66_CELLS = [
    (1.0, ("round2", "r36/baseline")),
    (0.75, None), (0.5, None), (0.25, None), (0.0, None),
]


def r66():
    from analyze import load_daily
    rows = []
    for index, (alpha, ref) in enumerate(R66_CELLS):
        if ref:
            base = HERE / "results" / ref[0] / ref[1]
            runs = sorted(p.parent for p in base.glob("rep*/trace.tsv"))
            state = None
        else:
            state = json.loads((HERE / "results" / "round6" / "state" / f"r66_alpha{alpha:g}.json").read_text())
            runs = sorted(p.parent for p in (HERE / "results" / "round6" / state["prefix"]).glob("rep*/trace.tsv"))
        reps, days, occ = [], [], []
        for run in runs:
            ids, total, event = index_table(run / "trace.tsv")
            reps.append((total, event))
            days.append(day28_of(run))
            with open(run / "trace.tsv") as handle:
                header = handle.readline().rstrip("\n").split("\t")
                col = {name: i for i, name in enumerate(header)}
                values = []
                for line in handle:
                    parts = line.split("\t")
                    d = int(parts[col["timestamp"]]) // STEPS_PER_DAY
                    if 1 <= d <= 28:
                        values.append(int(parts[col["occupancy"]]))
                occ.append(np.asarray(values, dtype=np.int64))
        total = np.concatenate([r[0] for r in reps])
        event = np.concatenate([r[1] for r in reps])
        point = pack(total, event)
        ci = bootstrap_pack(reps, seed=BOOT_SEED + 13 * index)
        row = flatten_row(f"alpha{alpha:g}", point, ci)
        pooled = np.concatenate(occ)
        rng = np.random.default_rng(BOOT_SEED + 17 * index)
        med, p90 = [], []
        for _ in range(BOOT):
            pick = rng.integers(0, len(occ), size=len(occ))
            both = np.concatenate([occ[i] for i in pick])
            med.append(float(np.median(both)))
            p90.append(float(np.quantile(both, 0.9)))
        row.update({
            "alpha": alpha,
            "replicates": len(runs),
            "day28_mean": float(np.mean(days)),
            "day28_vs_6211.25": float(np.mean(days)) / 6211.25 - 1.0,
            "background_coefficient": state["k"] if state else None,
            "calibration_matched": state["matched"] if state else True,
            "occupancy_at_infection_median": float(np.median(pooled)),
            "occupancy_at_infection_median_low": interval(med)[0], "occupancy_at_infection_median_high": interval(med)[1],
            "occupancy_at_infection_p90": float(np.quantile(pooled, 0.9)),
            "occupancy_at_infection_p90_low": interval(p90)[0], "occupancy_at_infection_p90_high": interval(p90)[1],
            "infections_days_1_28": int(pooled.size),
        })
        rows.append(row)
        print(f"R6-6 alpha {alpha}: R {point['early_R']:.3f} kmom {point['k_mom']:.3f} kml {point['k_ml']:.3f} zero {point['share_0']:.3f} occ med {np.median(pooled)} p90 {np.quantile(pooled, 0.9)}", flush=True)
    write_csv(OUT / "43_r66_alpha_sweep.csv", rows)
    return rows


# ---------------------------------------------------------------- R6-7

def r67_cells():
    """(label, group, rate, factor, state name) for every matched R6-7 cell that exists."""
    state_dir = HERE / "results" / "round6" / "state"
    cells = []
    for group in (30, 100):
        params = json.loads((state_dir / f"r67_M{group}_params.json").read_text())
        cells.append((f"M{group}_rate{params['rate']:.4g}", group, params["rate"], params["factor"], f"r67_M{group}"))
        for path in sorted(state_dir.glob(f"r67_M{group}_rate*.json")):
            rate = float(path.stem.split("rate")[1])
            cells.append((f"M{group}_rate{rate:g}", group, rate, params["factor"], path.stem))
    return cells


def r67():
    from r6stats import load_event_agents
    summary, joint = [], []
    for index, (label, group, rate, factor, state_name) in enumerate(r67_cells()):
        state = json.loads((HERE / "results" / "round6" / "state" / f"{state_name}.json").read_text())
        if not state.get("prefix"):
            continue
        runs = sorted(p.parent for p in (HERE / "results" / "round6" / state["prefix"]).glob("rep*/trace.tsv"))
        reps, days, n_events, n_event_inf, n_events_with_inf = [], [], 0, 0, 0
        for run in runs:
            agents = load_event_agents(run / "events.tsv.infections")
            ids, total, event = index_table(run / "trace.tsv", None, agents)
            if np.any(event > total):
                raise RuntimeError(f"event offspring exceed total in {run}")
            reps.append((total, event))
            days.append(day28_of(run))
            n_event_inf += len(agents)
            with open(run / "events.tsv") as handle:
                next(handle)
                for line in handle:
                    parts = line.rstrip("\n").split("\t")
                    n_events += 1
                    n_events_with_inf += float(parts[6]) > 0
        total = np.concatenate([r[0] for r in reps])
        event = np.concatenate([r[1] for r in reps])
        point = pack(total, event)
        ci = bootstrap_pack(reps, seed=BOOT_SEED + 19 * index)
        row = flatten_row(label, point, ci)
        total_infected = float(np.mean(days)) * len(reps)
        row.update({
            "group_size_max": group, "event_factor": factor, "event_duration_hours": 2, "event_rate": rate,
            "replicates": len(reps), "day28_mean": float(np.mean(days)), "day28_vs_6211.25": float(np.mean(days)) / 6211.25 - 1.0,
            "background_coefficient": state["k"], "calibration_matched": state["matched"],
            "events_total": n_events, "events_with_infectious_attendee": n_events_with_inf, "infections_at_events_whole_run": n_event_inf,
            "baseline_zero_share_anone_f0": 0.297,
        })
        summary.append(row)
        counts = Counter(zip(total.tolist(), event.tolist()))
        for (off, ev), number in sorted(counts.items()):
            joint.append({"cell": label, "offspring_total": off, "offspring_at_events": ev, "index_cases": number})
        print(f"R6-7 {label}: R {point['early_R']:.3f} kmom {point['k_mom']:.3f} kml {point['k_ml']:.3f} zero {point['share_0']:.3f} nb_ml0 {point['nb_ml_share_0']:.3f} events {point['event_offspring_share']:.3f}", flush=True)
    write_csv(OUT / "43_r67_closed_group_summary.csv", summary)
    write_csv(OUT / "43_r67_offspring.csv", joint)
    return summary


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "r63"
    if which == "r63":
        r63()
    elif which == "r61":
        r61()
    elif which == "r62":
        r62()
    elif which == "r64":
        r64()
    elif which == "r65":
        r65()
    elif which == "r66":
        r66()
    elif which == "r67":
        r67()
    else:
        raise SystemExit(f"unknown task {which}")


if __name__ == "__main__":
    main()
