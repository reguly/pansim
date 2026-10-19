#!/usr/bin/env python3
"""Note 61 round 12 analysis:
- R12-1 item 1: paired World 3b on common seeds 77001..77012 alongside Worlds 1, 2a, 2b (and Round-6 World 3b).
- R12-1 item 2: closed-group event rate semantics audit from locations1.json, events.tsv, and events.tsv.infections.
- R12-2: under-detection thinning (p = 1.0, 0.6, 0.3) under random per-infection and household-clustered schemes.

  python3 superspreader/study/analyze_round12.py all
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from r6stats import BOOT_SEED, bootstrap_pack, flatten_row, index_table, interval, load_event_agents, pack, write_csv  # noqa: E402
import analyze_round6 as a6  # noqa: E402
import analyze_round10 as a10  # noqa: E402
import analyze_round11 as a11  # noqa: E402
from analyze_round7 import lorenz_shares  # noqa: E402
from analyze_round9 import nb_shares  # noqa: E402

OUT = HERE.parent
ROOT = HERE.parents[1]
R6 = HERE / "results" / "round6"
R10 = HERE / "results" / "round10"
R11 = HERE / "results" / "round11"
R12 = HERE / "results" / "round12"
UNKNOWN = a10.UNKNOWN
POPULATION = 178746


def world_stats_with_events(label, dirs, seed_offset=0):
    """Same as a10.world_stats + a11.extras, but passes events.tsv.infections into index_table when present."""
    age, atype, home = a10.agent_table()
    reps, days = [], []
    loc_counts = Counter()
    cluster_rows = []
    comp_rows = []
    top_age, top_type, top_class = [], [], []
    pop_age, pop_type = [], []
    hh_trans = hh_denom = 0
    maxima, p99, p999 = [], [], []
    top_n = 0

    ev_total = ev_inf = ev_tx = ev_infected = 0
    ev_max_inf = 0
    has_events = False

    hh_size = Counter(home[home >= 0].tolist())

    for run in dirs:
        rows = a10.read_trace(run)
        ev_inf_path = run / "events.tsv.infections"
        ev_log_path = run / "events.tsv"
        ev_agents = load_event_agents(ev_inf_path) if ev_inf_path.exists() else None
        ids, total, event = index_table(run / "trace.tsv", None, ev_agents)
        reps.append((total, event))

        if ev_log_path.exists():
            has_events = True
            with open(ev_log_path) as handle:
                for r in csv.DictReader(handle, delimiter="\t"):
                    ev_total += 1
                    inf_in = float(r["infectious_in_group"])
                    inf_out = int(r["infected"])
                    if inf_in > 0:
                        ev_inf += 1
                    if inf_out > 0:
                        ev_tx += 1
                    ev_infected += inf_out
                    if inf_out > ev_max_inf:
                        ev_max_inf = inf_out

        from analyze import load_daily
        days.append(int(load_daily(run / "stdout.txt")[27]["INF"]))
        children = defaultdict(list)
        for a, inf, loc, lt, d in rows:
            if 1 <= d <= 28:
                loc_counts[lt] += 1
                if inf != UNKNOWN and home[a] >= 0 and home[a] == home[inf]:
                    hh_trans += 1
            if inf != UNKNOWN:
                children[inf].append((loc, lt, d, a))

        if len(total):
            maxima.append(int(total.max()))
            p99.append(float(np.quantile(total, 0.99)))
            p999.append(float(np.quantile(total, 0.999)))
            top_n += max(1, int(round(0.01 * len(total))))

        order = np.argsort(total)[::-1][:10]
        for j in order:
            inf_id = int(ids[j])
            kids = children.get(inf_id, [])
            if not kids:
                continue
            venues = {loc for loc, _lt, _d, _a in kids}
            by_venue_day = Counter((loc, d) for loc, _lt, d, _a in kids)
            cluster_rows.append({
                "arm": label,
                "offspring": int(total[j]),
                "distinct_venues": len(venues),
                "largest_venue_day_share": max(by_venue_day.values()) / len(kids),
            })
            kid_ids = np.asarray([a for _l, _t, _d, a in kids])
            ages = age[kid_ids]
            by_type = Counter(t for _l, t, _d, _a in kids)
            modal_type, modal_n = by_type.most_common(1)[0]
            same_home = int(np.sum((home[kid_ids] >= 0) & (home[kid_ids] == home[inf_id]))) if home[inf_id] >= 0 else 0
            comp_rows.append({
                "arm": label,
                "infector": inf_id,
                "offspring": int(total[j]),
                "same_household_share": same_home / len(kids),
                "largest_venue_day_share": max(by_venue_day.values()) / len(kids),
                "distinct_venues": len(venues),
                "modal_venue_type": int(modal_type),
                "modal_venue_type_name": a10.LOCTYPE_NAMES.get(int(modal_type), str(modal_type)),
                "same_venue_type_share": modal_n / len(kids),
                "distinct_venue_types": len(by_type),
                "infectee_age_min": int(ages.min()),
                "infectee_age_max": int(ages.max()),
                "infectee_age_mean": float(ages.mean()),
                "infectee_age_range": int(ages.max() - ages.min()),
                "infector_age": int(age[inf_id]),
                "infector_agent_type": int(atype[inf_id]),
            })

        for a in ids.tolist():
            if home[a] >= 0:
                hh_denom += max(hh_size[int(home[a])] - 1, 0)

        if len(total):
            cut = max(1, int(round(0.01 * len(total))))
            top = ids[np.argsort(total)[::-1][:cut]]
            top_age += age[top].tolist()
            top_type += atype[top].tolist()
            cls = run / "hvi.csv"
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
    row.update(lorenz_shares(total_all))
    tot_loc = sum(loc_counts.values())
    for t, name in a10.LOCTYPE_NAMES.items():
        row[f"infections_share_{name}"] = loc_counts.get(t, 0) / tot_loc
    row["infections_share_high_L_types"] = sum(loc_counts.get(t, 0) for t in a10.HIGH) / tot_loc
    row["infections_share_school_and_work"] = sum(loc_counts.get(t, 0) for t in (3, 33, 4, 13, 44)) / tot_loc
    row.update({
        "replicates": len(dirs),
        "day28_mean": float(np.mean(days)),
        "day28_vs_6211.25": float(np.mean(days)) / 6211.25 - 1,
        "largest_offspring_mean_over_replicates": float(np.mean(maxima)),
        "largest_offspring_max": int(max(maxima)),
        "offspring_p99": float(np.mean(p99)),
        "offspring_p999": float(np.mean(p999)),
        "household_secondary_attack_rate": hh_trans / hh_denom if hh_denom else float("nan"),
        "household_transmissions": hh_trans,
        "household_susceptible_contacts": hh_denom,
        "top1pct_infectors": top_n,
    })
    if cluster_rows:
        row["top10_clusters_mean_distinct_venues"] = float(np.mean([r["distinct_venues"] for r in cluster_rows]))
        row["top10_clusters_mean_largest_venue_day_share"] = float(np.mean([r["largest_venue_day_share"] for r in cluster_rows]))
        row["top10_clusters_mean_offspring"] = float(np.mean([r["offspring"] for r in cluster_rows]))
    if comp_rows:
        for key in ("same_household_share", "same_venue_type_share", "distinct_venue_types",
                    "infectee_age_mean", "infectee_age_range"):
            row[f"top10_clusters_mean_{key}"] = float(np.mean([r[key] for r in comp_rows]))
        row["top10_clusters_modal_venue_type_mode"] = Counter(r["modal_venue_type_name"] for r in comp_rows).most_common(1)[0][0]
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
    if has_events:
        row.update({
            "events_total": ev_total,
            "events_with_infectious": ev_inf,
            "events_with_transmission": ev_tx,
            "event_infections_total": ev_infected,
            "event_infections_share_of_all_d1_28": ev_infected / tot_loc if tot_loc else float("nan"),
            "mean_infected_when_infectious": ev_infected / ev_inf if ev_inf else 0.0,
            "max_infected_in_event": ev_max_inf,
        })
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

    joint = [{"cell": label, "offspring_total": a, "offspring_at_events": e, "index_cases": n}
             for (a, e), n in sorted(Counter(zip(total_all.tolist(), event_all.tolist())).items())]
    return row, joint, comp_rows


def run_r121_worlds():
    """Generate 62_r121_worlds_paired.csv, 62_r121_worlds_paired_offspring.csv, and 62_r121_clusters.csv."""
    labels = [
        ("world1_multiplier_only", R10, "r10_w1_sh0.32", "77001..77012"),
        ("world2a_scene_L30_sh0.70", R11, "r11_w2_L30_sh0.70", "77001..77012"),
        ("world2b_scene_L10_sh0.58", R11, "r11_w2_L10_sh0.58", "77001..77012"),
        ("world3b_events_M30_rate0.146_paired", R12, "r12_w3b_M30_rate0.1456", "77001..77012"),
        ("world3b_events_M30_rate0.146_round6", R6, "r67_M30", "68101..68112"),
    ]
    rows, joint, clusters = [], [], []
    for i, (name, base, label, seed_range) in enumerate(labels):
        dirs, state = a10.run_dirs(base, label)
        row, j, c = world_stats_with_events(name, dirs, 13 * i)
        row.update({
            "seed_range": seed_range,
            "background_coefficient": state["k"],
            "calibration_matched": state["matched"],
            "state_label": label,
        })
        rows.append(row)
        joint += j
        clusters += c
        print(
            f"[R12-1] {name} ({seed_range}): k_ml={row['k_ml']:.3f} [{row['k_ml_low']:.3f},{row['k_ml_high']:.3f}] "
            f"k_mom={row['k_mom']:.3f} [{row['k_mom_low']:.3f},{row['k_mom_high']:.3f}] "
            f"ratio={row['k_ml_over_k_mom']:.2f} R={row['early_R']:.3f} "
            f"zero={row['share_0']:.3f} (nb={row['nb_zero_at_k_ml_own_mean']:.3f}, gap={row['observed_zero_minus_nb_zero_at_k_ml']:+.3f}) "
            f"80%={row['share_of_index_cases_causing_80pct']:.3f} "
            f"vday={row['top10_clusters_mean_largest_venue_day_share']:.3f} "
            f"hh={row['top10_clusters_mean_same_household_share']:.3f} "
            f"ev_off={row.get('event_offspring_share', 0.0):.3f} "
            f"day28={row['day28_mean']:.1f} ({row['day28_vs_6211.25']:+.3%})",
            flush=True,
        )
    write_csv(OUT / "62_r121_worlds_paired.csv", rows)
    write_csv(OUT / "62_r121_worlds_paired_offspring.csv", joint)
    write_csv(OUT / "62_r121_clusters.csv", clusters)
    return rows


def run_r121_event_semantics():
    """Audit locations1.json, events.tsv, and events.tsv.infections for R12-1 item 2."""
    locs_data = json.loads((ROOT / "inputRealExample" / "locations1.json").read_text())["places"]
    type_counts = Counter(int(p.get("type", p.get("typeID", -1))) for p in locs_data)
    n_type5 = type_counts[5]
    n_type8 = type_counts[8]
    n_eligible = n_type5 + n_type8
    rate = 0.1456

    out_rows = []
    for name, base, label, seed_range in [
        ("world3b_events_M30_rate0.146_paired", R12, "r12_w3b_M30_rate0.1456", "77001..77012"),
        ("world3b_events_M30_rate0.146_round6", R6, "r67_M30", "68101..68112"),
    ]:
        dirs, _state = a10.run_dirs(base, label)
        n_reps = len(dirs)
        n_days = 28
        rep_days = n_reps * n_days

        present_all = []
        group_all = []
        inf_in_all = []
        infected_all = []
        by_type = Counter()
        by_type_nonempty = Counter()
        daily_group_sums = []
        weekly_group_sums = []

        total_nonseed_infections = 0
        total_d1_28_infections = 0
        event_inf_rows = 0
        event_inf_d1_28 = 0
        index_offspring_total = 0
        index_offspring_events = 0

        for run in dirs:
            rows = a10.read_trace(run)
            for _a, inf, _loc, _lt, d in rows:
                if inf != UNKNOWN:
                    total_nonseed_infections += 1
                    if 1 <= d <= 28:
                        total_d1_28_infections += 1

            ev_agents = load_event_agents(run / "events.tsv.infections")
            _ids, tot, ev = index_table(run / "trace.tsv", None, ev_agents)
            index_offspring_total += int(tot.sum())
            index_offspring_events += int(ev.sum())

            with open(run / "events.tsv.infections") as handle:
                for r in csv.DictReader(handle, delimiter="\t"):
                    event_inf_rows += 1
                    d = int(r["day"])
                    if 1 <= d <= 28:
                        event_inf_d1_28 += 1

            day_groups = defaultdict(int)
            with open(run / "events.tsv") as handle:
                for r in csv.DictReader(handle, delimiter="\t"):
                    d = int(r["day"])
                    lt = int(r["locType"])
                    pr = int(r["present"])
                    gr = int(r["group"])
                    ii = float(r["infectious_in_group"])
                    inf_c = int(r["infected"])
                    present_all.append(pr)
                    group_all.append(gr)
                    inf_in_all.append(ii)
                    infected_all.append(inf_c)
                    by_type[lt] += 1
                    if pr > 0:
                        by_type_nonempty[lt] += 1
                    day_groups[d] += gr

            for d in range(n_days):
                daily_group_sums.append(day_groups[d])
            for w in range(4):
                weekly_group_sums.append(sum(day_groups[7 * w + k] for k in range(7)))

        present_arr = np.asarray(present_all)
        group_arr = np.asarray(group_all)
        inf_in_arr = np.asarray(inf_in_all)
        infected_arr = np.asarray(infected_all)
        nonempty = group_arr > 0
        active = inf_in_arr > 0
        transmitting = infected_arr > 0

        events_total = len(group_arr)
        events_per_day = events_total / rep_days
        nonempty_events = int(nonempty.sum())
        nonempty_per_day = nonempty_events / rep_days
        empty_share = 1.0 - (nonempty_events / events_total)

        person_attendances_total = int(group_arr.sum())
        person_attendances_per_day = float(np.mean(daily_group_sums))
        person_attendances_per_week = float(np.mean(weekly_group_sums))
        daily_pop_share = person_attendances_per_day / POPULATION
        weekly_pop_share_person_events = person_attendances_per_week / POPULATION
        weekly_pop_share_unique_binomial_approx = 1.0 - (1.0 - daily_pop_share) ** 7

        row = {
            "arm": name,
            "seed_range": seed_range,
            "replicates": n_reps,
            "days_per_replicate": n_days,
            "total_locations_in_city": len(locs_data),
            "eligible_type5_restaurants": n_type5,
            "eligible_type8_long_shops": n_type8,
            "eligible_venues_total": n_eligible,
            "event_rate_flag": rate,
            "expected_events_per_day_from_venues": n_eligible * rate,
            "events_total": events_total,
            "observed_events_per_day": events_per_day,
            "observed_events_per_day_type5": by_type[5] / rep_days,
            "observed_events_per_day_type8": by_type[8] / rep_days,
            "empty_events_total": events_total - nonempty_events,
            "empty_events_share": empty_share,
            "nonempty_events_total": nonempty_events,
            "nonempty_events_per_day": nonempty_per_day,
            "mean_present_all_events": float(present_arr.mean()),
            "mean_present_nonempty_events": float(present_arr[nonempty].mean()),
            "median_present_nonempty_events": float(np.median(present_arr[nonempty])),
            "max_present_in_event": int(present_arr.max()),
            "mean_group_size_all_events": float(group_arr.mean()),
            "mean_group_size_nonempty_events": float(group_arr[nonempty].mean()),
            "median_group_size_nonempty_events": float(np.median(group_arr[nonempty])),
            "max_group_size_in_event": int(group_arr.max()),
            "share_all_events_at_cap_M30": float((group_arr == 30).mean()),
            "share_nonempty_events_at_cap_M30": float((group_arr[nonempty] == 30).mean()),
            "person_attendances_total": person_attendances_total,
            "person_attendances_per_day": person_attendances_per_day,
            "daily_agent_attendance_share": daily_pop_share,
            "person_attendances_per_week": person_attendances_per_week,
            "weekly_agent_attendance_share_person_events": weekly_pop_share_person_events,
            "weekly_unique_agent_attendance_share_approx": weekly_pop_share_unique_binomial_approx,
            "events_with_infectious_total": int(active.sum()),
            "events_with_infectious_per_day": float(active.sum() / rep_days),
            "events_with_infectious_share_of_all": float(active.mean()),
            "events_with_infectious_share_of_nonempty": float(active.sum() / nonempty_events),
            "events_with_transmission_total": int(transmitting.sum()),
            "events_with_transmission_per_day": float(transmitting.sum() / rep_days),
            "events_with_transmission_share_of_infectious": float(transmitting.sum() / active.sum()),
            "mean_infections_per_infectious_event": float(infected_arr[active].mean()),
            "mean_infections_per_transmitting_event": float(infected_arr[transmitting].mean()),
            "max_infections_in_single_event": int(infected_arr.max()),
            "event_infections_total": int(infected_arr.sum()),
            "event_infections_share_of_all_nonseed": float(infected_arr.sum() / total_nonseed_infections),
            "event_infections_share_of_d1_28": float(event_inf_d1_28 / total_d1_28_infections),
            "event_offspring_share_early_index_d1_10": float(index_offspring_events / index_offspring_total),
        }
        out_rows.append(row)
        print(
            f"[R12-1 Event Audit] {name}: eligible_venues={n_eligible} (type5={n_type5}, type8={n_type8}), "
            f"events/day={events_per_day:.2f} (nonempty={nonempty_per_day:.2f}, empty_share={empty_share:.3f}), "
            f"mean_group_all={row['mean_group_size_all_events']:.2f} (nonempty={row['mean_group_size_nonempty_events']:.2f}), "
            f"person_attendances/day={person_attendances_per_day:.1f} ({daily_pop_share:.3%} of pop/day, "
            f"{weekly_pop_share_person_events:.3%} person-events/wk, ~{weekly_pop_share_unique_binomial_approx:.3%} unique/wk), "
            f"active_events/day={row['events_with_infectious_per_day']:.2f}, "
            f"mean_inf_when_active={row['mean_infections_per_infectious_event']:.2f}, max_inf={row['max_infections_in_single_event']}, "
            f"share_all_inf={row['event_infections_share_of_all_nonseed']:.3f}, share_d1_10_offspring={row['event_offspring_share_early_index_d1_10']:.3f}",
            flush=True,
        )
    write_csv(OUT / "62_r121_event_semantics.csv", out_rows)
    return out_rows


def thin_replicate(run, home, unique_homes, scheme, rate, rng):
    """Return thinned (ids, total_offspring, event_offspring, cluster_metrics_list, all_hh_num, all_hh_den) for one replicate."""
    rows = a10.read_trace(run)
    # Identify early index cases: infected on days 1..10 with known infector (preserving trace order like index_table)
    index_ids = []
    index_day = {}
    children = defaultdict(list)
    for a, inf, loc, lt, d in rows:
        index_day[a] = d
        if inf != UNKNOWN:
            if 1 <= d <= 10:
                index_ids.append(a)
            children[inf].append((loc, lt, d, a))
    index_ids = np.asarray(index_ids, dtype=np.int64)

    if rate >= 1.0 or scheme == "full":
        det_index_mask = np.ones(len(index_ids), dtype=bool)
        det_child_fn = lambda _inf_id, _kid_id: True
    elif scheme == "random":
        # Every infected agent is detected independently with probability `rate`
        all_agents = sorted({a for a, _inf, _loc, _lt, _d in rows})
        draws = rng.random(len(all_agents)) < rate
        det_map = dict(zip(all_agents, draws))
        det_index_mask = np.asarray([det_map[int(i)] for i in index_ids], dtype=bool)
        det_child_fn = lambda _inf_id, kid_id: det_map[int(kid_id)]
    elif scheme == "household_coupled":
        # Each household is detected with probability `rate`; both index cases and infectees use the same household mask
        hh_draws = rng.random(len(unique_homes)) < rate
        hh_map = dict(zip(unique_homes.tolist(), hh_draws.tolist()))
        det_index_mask = np.asarray([hh_map.get(int(home[i]), False) for i in index_ids], dtype=bool)
        det_child_fn = lambda _inf_id, kid_id: hh_map.get(int(home[kid_id]), False)
    elif scheme == "household_infectee":
        # Index cases are detected at rate `rate`, and whole households of infectees are detected at rate `rate`
        # (uncoupled from the index case's own detection so whole infectee households vanish with probability 1 - rate)
        det_index_mask = rng.random(len(index_ids)) < rate
        hh_draws = rng.random(len(unique_homes)) < rate
        hh_map = dict(zip(unique_homes.tolist(), hh_draws.tolist()))
        det_child_fn = lambda _inf_id, kid_id: hh_map.get(int(home[kid_id]), False)
    else:
        raise ValueError(f"Unknown scheme: {scheme}")

    kept_ids = index_ids[det_index_mask]
    totals = np.zeros(len(kept_ids), dtype=np.int64)
    events = np.zeros(len(kept_ids), dtype=np.int64)
    kept_children = {}
    all_hh_num = 0
    all_hh_den = 0

    for idx, inf_id in enumerate(kept_ids.tolist()):
        limit = index_day[int(inf_id)] + 14
        kids = [k for k in children.get(int(inf_id), []) if k[2] <= limit and det_child_fn(inf_id, k[3])]
        kept_children[int(inf_id)] = kids
        totals[idx] = len(kids)
        all_hh_den += len(kids)
        if home[inf_id] >= 0 and kids:
            all_hh_num += sum(1 for _l, _t, _d, a in kids if home[a] == home[inf_id])

    cluster_list = []
    if len(totals):
        order = np.argsort(totals)[::-1][:10]
        for j in order:
            inf_id = int(kept_ids[j])
            kids = kept_children.get(inf_id, [])
            if not kids:
                continue
            venues = {loc for loc, _lt, _d, _a in kids}
            by_venue_day = Counter((loc, d) for loc, _lt, d, _a in kids)
            by_type = Counter(lt for _loc, lt, _d, _a in kids)
            _modal_t, modal_n = by_type.most_common(1)[0]
            same_hh = sum(1 for _l, _t, _d, a in kids if home[inf_id] >= 0 and home[a] == home[inf_id])
            cluster_list.append({
                "offspring": int(totals[j]),
                "same_household_share": same_hh / len(kids),
                "largest_venue_day_share": max(by_venue_day.values()) / len(kids),
                "distinct_venues": len(venues),
                "same_venue_type_share": modal_n / len(kids),
            })

    return kept_ids, totals, events, cluster_list, all_hh_num, all_hh_den


def run_r122_thinning():
    """Run R12-2 under-detection thinning across worlds 1, 2b, 3b (and 2a)."""
    _age, _atype, home = a10.agent_table()
    unique_homes = np.unique(home[home >= 0])

    worlds = [
        ("world1_multiplier_only", R10, "r10_w1_sh0.32"),
        ("world2b_scene_L10_sh0.58", R11, "r11_w2_L10_sh0.58"),
        ("world3b_events_M30_rate0.146_paired", R12, "r12_w3b_M30_rate0.1456"),
        ("world2a_scene_L30_sh0.70", R11, "r11_w2_L30_sh0.70"),
    ]
    configs = [
        ("full", 1.0),
        ("random", 0.6),
        ("random", 0.3),
        ("household_infectee", 0.6),
        ("household_infectee", 0.3),
        ("household_coupled", 0.6),
        ("household_coupled", 0.3),
    ]

    out_rows = []
    for w_idx, (w_name, base, label) in enumerate(worlds):
        dirs, _state = a10.run_dirs(base, label)
        base_stats = {}
        for c_idx, (scheme, rate) in enumerate(configs):
            reps = []
            clusters = []
            hh_num_tot = 0
            hh_den_tot = 0
            for r_idx, run in enumerate(dirs):
                # Deterministic RNG per replicate, scheme, and rate (shared across worlds on the same seed!)
                scheme_code = {"full": 0, "random": 1, "household_infectee": 2, "household_coupled": 3}[scheme]
                rng = np.random.default_rng(910000 + r_idx * 1000 + scheme_code * 100 + int(round(rate * 100)))
                _ids, tot, ev, cl, h_num, h_den = thin_replicate(run, home, unique_homes, scheme, rate, rng)
                reps.append((tot, ev))
                clusters.extend(cl)
                hh_num_tot += h_num
                hh_den_tot += h_den

            total_all = np.concatenate([r[0] for r in reps])
            event_all = np.concatenate([r[1] for r in reps])
            cell_label = f"{w_name}__{scheme}_{rate:.1f}"
            row = flatten_row(
                cell_label,
                pack(total_all, event_all),
                bootstrap_pack(reps, seed=BOOT_SEED + 101 * w_idx + 17 * c_idx),
            )
            row.update(lorenz_shares(total_all))
            mean = row["early_R"]
            for est in ("mom", "ml"):
                z, s80 = nb_shares(row[f"k_{est}"], mean)
                row[f"nb_zero_at_k_{est}_own_mean"] = z
                row[f"nb_80pct_at_k_{est}_own_mean"] = s80
            row["k_ml_over_k_mom"] = row["k_ml"] / row["k_mom"]
            row["observed_zero_minus_nb_zero_at_k_ml"] = row["share_0"] - row["nb_zero_at_k_ml_own_mean"]
            row["all_detected_offspring_same_household_share"] = hh_num_tot / hh_den_tot if hh_den_tot else float("nan")
            if clusters:
                for key in ("offspring", "same_household_share", "largest_venue_day_share", "distinct_venues", "same_venue_type_share"):
                    row[f"top10_clusters_mean_{key}"] = float(np.mean([c[key] for c in clusters]))

            if scheme == "full" and rate == 1.0:
                base_stats = {
                    "k_ml": row["k_ml"],
                    "k_mom": row["k_mom"],
                    "k_ml_over_k_mom": row["k_ml_over_k_mom"],
                    "top10_hh": row["top10_clusters_mean_same_household_share"],
                    "all_hh": row["all_detected_offspring_same_household_share"],
                }

            row["world"] = w_name
            row["scheme"] = scheme
            row["detection_rate"] = rate
            row["k_ml_rel_change_vs_full"] = row["k_ml"] / base_stats["k_ml"] - 1.0
            row["k_mom_rel_change_vs_full"] = row["k_mom"] / base_stats["k_mom"] - 1.0
            row["ratio_diff_vs_full"] = row["k_ml_over_k_mom"] - base_stats["k_ml_over_k_mom"]
            out_rows.append(row)

            print(
                f"[R12-2] {w_name:36s} | {scheme:18s} p={rate:.1f} | "
                f"n={row['index_cases']:5d} R={mean:.3f} | "
                f"k_ml={row['k_ml']:.3f} ({row['k_ml_rel_change_vs_full']:+.1%}) "
                f"k_mom={row['k_mom']:.3f} ({row['k_mom_rel_change_vs_full']:+.1%}) "
                f"ratio={row['k_ml_over_k_mom']:.2f} | "
                f"zero={row['share_0']:.3f} (nb={row['nb_zero_at_k_ml_own_mean']:.3f}, gap={row['observed_zero_minus_nb_zero_at_k_ml']:+.3f}) | "
                f"top10_hh={row['top10_clusters_mean_same_household_share']:.3f} "
                f"all_hh={row['all_detected_offspring_same_household_share']:.3f} "
                f"vday={row['top10_clusters_mean_largest_venue_day_share']:.3f}",
                flush=True,
            )

    # Also compute explicit differences between household schemes and random at the same rate
    by_key = {(r["world"], r["scheme"], r["detection_rate"]): r for r in out_rows}
    for r in out_rows:
        rnd = by_key.get((r["world"], "random", r["detection_rate"]))
        if rnd is not None and r["scheme"].startswith("household"):
            r["ratio_minus_random_same_rate"] = r["k_ml_over_k_mom"] - rnd["k_ml_over_k_mom"]
            r["top10_hh_minus_random_same_rate"] = (
                r["top10_clusters_mean_same_household_share"] - rnd["top10_clusters_mean_same_household_share"]
            )
            r["all_hh_minus_random_same_rate"] = (
                r["all_detected_offspring_same_household_share"] - rnd["all_detected_offspring_same_household_share"]
            )
        else:
            r["ratio_minus_random_same_rate"] = 0.0
            r["top10_hh_minus_random_same_rate"] = 0.0
            r["all_hh_minus_random_same_rate"] = 0.0

    write_csv(OUT / "62_r122_thinning.csv", out_rows)
    return out_rows


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("worlds", "all"):
        run_r121_worlds()
    if cmd in ("events", "all"):
        run_r121_event_semantics()
    if cmd in ("thinning", "all"):
        run_r122_thinning()


if __name__ == "__main__":
    main()
