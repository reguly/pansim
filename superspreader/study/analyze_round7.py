#!/usr/bin/env python3
"""Round 7 (note 46) analyses.

  python3 superspreader/study/analyze_round7.py t3 s1 ...
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

from r6stats import BOOT, BOOT_SEED, bootstrap_pack, flatten_row, index_table, interval, pack, write_csv  # noqa: E402

OUT = HERE.parent
R7 = HERE / "results" / "round7"
ELIGIBLE = (4, 5, 6, 7, 8)


def read_mob(path):
    rows = {}
    with open(path) as handle:
        for r in csv.DictReader(handle):
            rows[int(r["agent"])] = r
    return rows


def spearman(x, y):
    def ranks(v):
        order = np.argsort(v, kind="mergesort")
        rk = np.empty(len(v))
        s = np.asarray(v)[order]
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and s[j + 1] == s[i]:
                j += 1
            rk[order[i:j + 1]] = 0.5 * (i + j) + 1
            i = j + 1
        return rk
    return float(np.corrcoef(ranks(x), ranks(y))[0, 1])


def t_tests(labels, accepted):
    """T2 to T4 from the accepted calibration logs (2 weeks) and the 1-week logs."""
    base = json.loads((R7 / "state" / "baseline_means.json").read_text())
    rows = []
    for label in labels:
        state = json.loads((R7 / "state" / f"scale_{label}.json").read_text())
        it = state["accepted_iteration"] if state["accepted_iteration"] is not None else len(state["history"]) - 1
        mob = read_mob(R7 / "mob" / label / f"it{it}" / "mobility.csv")
        wk1 = read_mob(R7 / "mob" / label / "wk1" / "mobility.csv") if (R7 / "mob" / label / "wk1" / "mobility.csv").exists() else None
        scale = {int(k): v for k, v in state["scale"]["wd"].items()}
        ids = [a for a, r in mob.items() if int(r["type"]) in ELIGIBLE and int(r["age"]) >= 15]
        t = np.asarray([int(mob[a]["type"]) for a in ids])
        m = np.asarray([float(mob[a]["m"]) for a in ids])
        raw = m / np.asarray([scale[x] for x in t])
        hwd = np.asarray([float(mob[a]["h_wd_role_disc"]) / float(mob[a]["days_weekday"]) for a in ids])
        hwe = np.asarray([float(mob[a]["h_we_role_disc"]) / float(mob[a]["days_weekend"]) for a in ids])
        vwd = np.asarray([float(mob[a]["visits_wd"]) / float(mob[a]["days_weekday"]) for a in ids])
        vwe = np.asarray([float(mob[a]["visits_we"]) / float(mob[a]["days_weekend"]) for a in ids])
        bwd = np.asarray([base[str(x)]["wd"] for x in t])
        rel = hwd / bwd
        row = {"arm": label, "eligible_agents": len(ids), "mean_multiplier_unscaled": float(raw.mean()), "cv2_unscaled": float(raw.var() / raw.mean() ** 2),
               "accepted_iteration": it}
        for tt in ELIGIBLE:
            sel = t == tt
            row[f"hours_wd_vs_baseline_type{tt}"] = float(hwd[sel].mean() / base[str(tt)]["wd"] - 1)
            row[f"hours_we_vs_baseline_type{tt}"] = float(hwe[sel].mean() / base[str(tt)]["we"] - 1)
            row[f"visits_wd_vs_baseline_type{tt}"] = float(vwd[sel].mean() / base[str(tt)]["visits_wd"] - 1)
            row[f"visits_we_vs_baseline_type{tt}"] = float(vwe[sel].mean() / base[str(tt)]["visits_we"] - 1)
        for q in (50, 90, 99, 99.9):
            row[f"p{q}_hours_wd_per_day"] = float(np.percentile(hwd, q))
            row[f"p{q}_visits_wd_per_day"] = float(np.percentile(vwd, q))
        row["realised_cv2_relative_hours_wd"] = float(rel.var() / rel.mean() ** 2)
        row["share_realised_below_half_of_multiplier"] = float(np.mean((m > 1.5) & (rel < 0.5 * m)) / max(np.mean(m > 1.5), 1e-12))
        # T4: realised relative hours on the applied multiplier
        for tag, sel in (("all", np.ones(len(m), bool)), ("m_le_2", m <= 2.0)):
            x, y = m[sel], rel[sel]
            slope = float(np.polyfit(x, y, 1)[0])
            r2 = float(np.corrcoef(x, y)[0, 1] ** 2)
            row[f"t4_slope_{tag}"] = slope
            row[f"t4_r2_{tag}"] = r2
        # persistence
        if wk1 is not None:
            h1 = np.asarray([float(wk1[a]["h_wd_role_disc"]) + float(wk1[a]["h_we_role_disc"]) for a in ids])
            h2 = np.asarray([float(mob[a]["h_wd_role_disc"]) + float(mob[a]["h_we_role_disc"]) for a in ids]) - h1
            row["persistence_spearman_week1_week2"] = spearman(h1, h2)
        rows.append(row)
        print(label, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in row.items() if k in ("mean_multiplier_unscaled", "cv2_unscaled", "realised_cv2_relative_hours_wd", "t4_slope_all", "t4_r2_all", "t4_slope_m_le_2", "persistence_spearman_week1_week2", "p99_hours_wd_per_day")}, flush=True)
    write_csv(OUT / f"47_t3_t4_{accepted}.csv", rows)
    return rows


def lorenz_shares(total):
    """Smallest fraction of index cases that cause 80% and 50% of the early offspring, and the top 1% and 5% shares."""
    v = np.sort(np.asarray(total, dtype=float))[::-1]
    c = np.cumsum(v)
    tot = c[-1] if c.size else 0.0
    if tot <= 0:
        return {}
    out = {}
    for frac in (0.8, 0.5):
        out[f"share_of_index_cases_causing_{int(frac * 100)}pct"] = float((np.searchsorted(c, frac * tot) + 1) / v.size)
    for top in (0.01, 0.05):
        k = max(1, int(round(top * v.size)))
        out[f"top_{int(top * 100)}pct_share_of_offspring"] = float(c[k - 1] / tot)
    return out


def load_hvi(path, scale=None):
    """Agent multiplier and class. The dump holds the multiplier times the calibrated per-type scale; with `scale` (type to weekday scale) the unscaled draw is returned."""
    m = {}
    cls = {}
    with open(path) as handle:
        next(handle)
        for line in handle:
            a, t, age, mult, c, rot = line.rstrip("\n").split(",")[:6]
            value = float(mult)
            if scale is not None and int(t) in scale:
                value /= scale[int(t)]
            m[int(a)] = value
            cls[int(a)] = int(c)
    return m, cls


def eligible_ids(path):
    """Agents the multiplier applies to (agent types 4 to 8, age 15 and over)."""
    out = set()
    with open(path) as handle:
        next(handle)
        for line in handle:
            a, t, age = line.split(",")[:3]
            if 4 <= int(t) <= 8 and int(age) >= 15:
                out.add(int(a))
    return out


def scale_of(label):
    """Weekday per-type scales used by an arm (S3 and S4 arms use the S2 cell's)."""
    mapped = "s1_a" + label.split("_a")[-1] if label.startswith("s5_unc") else label
    for name in (mapped, "s2_f0.05_F3"):
        path = R7 / "state" / f"scale_{name}.json"
        if path.exists():
            return {int(k): v for k, v in json.loads(path.read_text())["scale"]["wd"].items()}
    return None


LOCTYPE_NAMES = {2: "home", 3: "school", 33: "classroom", 4: "work_type4", 13: "work_type13", 1: "public_space", 5: "restaurant", 6: "large_venue",
                 7: "shop_short", 8: "shop_long", 9: "church", 10: "recreation", 12: "hospital", 14: "health_centre", 22: "nursing_home", 44: "university"}


def cell_stats(label, run_dirs, seed_offset=0):
    reps, ms, ms_elig, days, loc_counts, cls_idx, m_all_idx = [], [], [], [], Counter(), [], []
    for run in run_dirs:
        hvi, cls = load_hvi(run / "hvi.csv", scale_of(label))
        ids, total, event = index_table(run / "trace.tsv")
        reps.append((total, event))
        ms.append(np.asarray([hvi[a] for a in ids.tolist()]))
        elig = eligible_ids(run / "hvi.csv")
        ms_elig.append(np.asarray([hvi[a] for a in ids.tolist() if a in elig]))
        cls_idx.append(np.asarray([cls[a] for a in ids.tolist()]))
        from analyze import load_daily
        days.append(int(load_daily(run / "stdout.txt")[27]["INF"]))
        with open(run / "trace.tsv") as handle:
            header = handle.readline().rstrip("\n").split("\t")
            col = {name: i for i, name in enumerate(header)}
            for line in handle:
                parts = line.split("\t")
                if 1 <= int(parts[col["timestamp"]]) // 144 <= 28:
                    loc_counts[int(parts[col["locType"]])] += 1
    total = np.concatenate([r[0] for r in reps])
    event = np.concatenate([r[1] for r in reps])
    m_idx = np.concatenate(ms)
    point = pack(total, event)
    ci = bootstrap_pack(reps, seed=BOOT_SEED + seed_offset)
    row = flatten_row(label, point, ci)
    row.update(lorenz_shares(total))
    # bootstrap of the mean multiplier of index cases
    rng = np.random.default_rng(BOOT_SEED + 1000 + seed_offset)
    draws = []
    for _ in range(300):
        pick = rng.integers(0, len(ms), size=len(ms))
        draws.append(float(np.concatenate([ms[i] for i in pick]).mean()))
    lo, hi = interval(draws)
    row.update({"mean_m_index_cases_eligible": float(np.concatenate(ms_elig).mean()), "mean_m_index_cases": float(m_idx.mean()), "mean_m_index_cases_low": lo, "mean_m_index_cases_high": hi,
                "replicates": len(run_dirs), "day28_mean": float(np.mean(days)), "day28_vs_6211.25": float(np.mean(days)) / 6211.25 - 1})
    tot_loc = sum(loc_counts.values())
    for t, name in LOCTYPE_NAMES.items():
        row[f"infections_share_{name}"] = loc_counts.get(t, 0) / tot_loc
    row["infections_share_other_types"] = 1 - sum(loc_counts.get(t, 0) for t in LOCTYPE_NAMES) / tot_loc
    joint = [{"cell": label, "offspring_total": a, "offspring_at_events": 0, "index_cases": n}
             for (a, _e), n in sorted(Counter(zip(total.tolist(), event.tolist())).items())]
    return row, joint, (ms, reps, cls_idx)


def run_dirs_of(name):
    state = json.loads((R7 / "state" / f"r7_{name}.json").read_text())
    return sorted(p.parent for p in (R7 / state["prefix"]).glob("rep*/trace.tsv")), state


def s1():
    rows, joint = [], []
    for i, a in enumerate(("3", "1", "0.5", "0.3", "0.15")):
        label = f"s1_a{a}"
        dirs, state = run_dirs_of(label)
        row, j, _ = cell_stats(label, dirs, 7 * i)
        row.update({"shape": a, "background_coefficient": state["k"], "calibration_matched": state["matched"]})
        rows.append(row)
        joint += j
        print(label, "R", round(row["early_R"], 3), "kmom", round(row["k_mom"], 3), "kml", round(row["k_ml"], 3), "zero", round(row["share_0"], 3),
              "80%", round(row.get("share_of_index_cases_causing_80pct", 0), 3), "m_idx", round(row["mean_m_index_cases"], 2), flush=True)
    write_csv(OUT / "47_s1_summary.csv", rows)
    write_csv(OUT / "47_s1_offspring.csv", joint)
    return rows


def load_hvi_full(path):
    """agent -> (type, age, m, class, rotate)"""
    out = {}
    with open(path) as handle:
        next(handle)
        for line in handle:
            parts = line.rstrip("\n").split(",")
            out[int(parts[0])] = (int(parts[1]), int(parts[2]), float(parts[3]), int(parts[4]), int(parts[5]))
    return out


def t5(label="s1_a0.3"):
    """Natural coupling check: infections received per eligible agent by day 28, and mean offspring of index cases, by decile of m."""
    dirs, state = run_dirs_of(label)
    deciles = 10
    per_rep = []
    for run in dirs:
        hv = load_hvi_full(run / "hvi.csv")
        ids = [a for a, v in hv.items() if v[0] in ELIGIBLE and v[1] >= 15]
        m_all = np.asarray([hv[a][2] for a in ids])
        per_rep.append((ids, m_all, run))
    edges = np.quantile(np.concatenate([p[1] for p in per_rep]), np.linspace(0, 1, deciles + 1))
    edges[0], edges[-1] = -1, 1e12
    acc = []
    for ids, m_all, run in per_rep:
        dec = np.searchsorted(edges, m_all, side="right") - 1
        dec = np.clip(dec, 0, deciles - 1)
        dec_of = dict(zip(ids, dec.tolist()))
        n = np.bincount(dec, minlength=deciles).astype(float)
        msum = np.bincount(dec, weights=m_all, minlength=deciles)
        received = np.zeros(deciles)
        with open(run / "trace.tsv") as handle:
            header = handle.readline().rstrip("\n").split("\t")
            col = {name: i for i, name in enumerate(header)}
            for line in handle:
                parts = line.split("\t")
                d = int(parts[col["timestamp"]]) // 144
                if 1 <= d <= 28 and int(parts[col["agent"]]) in dec_of:
                    received[dec_of[int(parts[col["agent"]])]] += 1
        idx_ids, total, _event = index_table(run / "trace.tsv")
        off_sum = np.zeros(deciles)
        off_n = np.zeros(deciles)
        for a, o in zip(idx_ids.tolist(), total.tolist()):
            if a in dec_of:
                off_sum[dec_of[a]] += o
                off_n[dec_of[a]] += 1
        acc.append((n, msum, received, off_sum, off_n))

    def slopes(parts):
        n = sum(p[0] for p in parts); msum = sum(p[1] for p in parts); rec = sum(p[2] for p in parts)
        osum = sum(p[3] for p in parts); on = sum(p[4] for p in parts)
        mm = msum / n
        rate = rec / n
        off = np.where(on > 0, osum / np.maximum(on, 1), np.nan)
        ok = np.isfinite(off) & (off > 0) & (rate > 0)
        s_rec = float(np.polyfit(np.log(mm[ok]), np.log(rate[ok]), 1)[0])
        s_off = float(np.polyfit(np.log(mm[ok]), np.log(off[ok]), 1)[0])
        return s_rec, s_off, mm, rate, off, on

    s_rec, s_off, mm, rate, off, on = slopes(acc)
    rng = np.random.default_rng(BOOT_SEED + 55)
    boots = [slopes([acc[i] for i in rng.integers(0, len(acc), size=len(acc))])[:2] for _ in range(400)]
    lo_r, hi_r = interval([b[0] for b in boots]); lo_o, hi_o = interval([b[1] for b in boots])
    rows = [{"arm": label, "decile": d + 1, "mean_m": float(mm[d]), "infections_received_per_agent_day28": float(rate[d]),
             "index_cases": int(on[d]), "mean_offspring": float(off[d])} for d in range(deciles)]
    write_csv(OUT / "47_t5_deciles.csv", rows)
    write_csv(OUT / "47_t5_slopes.csv", [{"arm": label, "slope_received_vs_m": s_rec, "slope_received_low": lo_r, "slope_received_high": hi_r,
                                          "slope_offspring_vs_m": s_off, "slope_offspring_low": lo_o, "slope_offspring_high": hi_o}])
    print("T5", label, "received slope", round(s_rec, 3), (round(lo_r, 3), round(hi_r, 3)), "offspring slope", round(s_off, 3), (round(lo_o, 3), round(hi_o, 3)))
    for r in rows:
        print(r["decile"], round(r["mean_m"], 3), round(r["infections_received_per_agent_day28"], 4), r["index_cases"], round(r["mean_offspring"], 3))


def t6():
    state = json.loads((R7 / "state" / "scale_s2_f0.05_F3.json").read_text())
    scale = {int(k): v for k, v in state["scale"]["wd"].items()}
    fixed_class = set()
    with open(R7 / "s3" / "hvi_fixed.csv") as handle:
        next(handle)
        for line in handle:
            p = line.split(",")
            if int(p[4]) == 1:
                fixed_class.add(int(p[0]))
    rows = []
    for name in ("v1", "v2", "v4", "rep1", "rep3", "rep10"):
        log = R7 / "mob" / ("t6b" if name in ("v2", "v4") else "t6") / name / "mobility.csv"
        if not log.exists():
            continue
        mob = read_mob(log)
        groups = {"class": [], "others": []}
        for a, r in mob.items():
            if int(r["type"]) not in ELIGIBLE or int(r["age"]) < 15:
                continue
            if name.startswith("rep"):
                is_class = a in fixed_class
            else:
                is_class = float(r["m"]) / scale[int(r["type"])] > 1.0001
            groups["class" if is_class else "others"].append(r)
        for g, rs in groups.items():
            def mean(f):
                return float(np.mean([f(r) for r in rs]))
            rows.append({
                "arm": name, "group": g, "agents": len(rs),
                "disc_hours_wd_per_day": mean(lambda r: float(r["h_wd_role_disc"]) / float(r["days_weekday"])),
                "disc_hours_we_per_day": mean(lambda r: float(r["h_we_role_disc"]) / float(r["days_weekend"])),
                "disc_visits_wd_per_day": mean(lambda r: float(r["visits_wd"]) / float(r["days_weekday"])),
                "disc_visits_we_per_day": mean(lambda r: float(r["visits_we"]) / float(r["days_weekend"])),
                "distinct_disc_venues_per_day_wd": mean(lambda r: float(r["distinct_day_wd"])),
                "distinct_disc_venues_per_week": mean(lambda r: float(r["distinct_week"])),
                "moves_wd_per_day": mean(lambda r: float(r["moves_weekday"]) / float(r["days_weekday"])),
            })
    ref = {r["group"]: r for r in rows if r["arm"] == "v1"}
    ref_rep = {r["group"]: r for r in rows if r["arm"] == "rep1"}
    for r in rows:
        rr = ref_rep if r["arm"].startswith("rep") else ref
        base = rr.get(r["group"])
        if base:
            r["hours_wd_vs_reference"] = r["disc_hours_wd_per_day"] / base["disc_hours_wd_per_day"] - 1
            r["visits_wd_vs_reference"] = r["disc_visits_wd_per_day"] / base["disc_visits_wd_per_day"] - 1
            r["distinct_week_vs_reference"] = r["distinct_disc_venues_per_week"] / base["distinct_disc_venues_per_week"] - 1
    write_csv(OUT / "47_t6_levers.csv", rows)
    for r in rows:
        print(r["arm"], r["group"], r["agents"], round(r["disc_hours_wd_per_day"], 2), round(r["disc_visits_wd_per_day"], 2), round(r["distinct_disc_venues_per_day_wd"], 2), round(r["distinct_disc_venues_per_week"], 1),
              {k: round(r[k], 3) for k in ("hours_wd_vs_reference", "visits_wd_vs_reference", "distinct_week_vs_reference") if k in r})


def class_flow(dirs, rotate=False):
    """Class share of infections caused and received (days 1 to 28, known infector) and of index cases, pooled over replicates."""
    caused = received = known = idx_class = idx_all = 0
    pop_class = pop_all = n_agents = 0
    for run in dirs:
        hv = load_hvi_full(run / "hvi.csv")
        n_agents += len(hv)
        flag = {a: (v[4] if rotate else v[3]) for a, v in hv.items()}
        elig = {a for a, v in hv.items() if (v[4] == 1 if rotate else (v[0] in ELIGIBLE and v[1] >= 15))}
        pop_all += len(elig)
        pop_class += sum(1 for a in elig if flag[a])
        with open(run / "trace.tsv") as handle:
            header = handle.readline().rstrip("\n").split("\t")
            col = {name: i for i, name in enumerate(header)}
            for line in handle:
                parts = line.split("\t")
                d = int(parts[col["timestamp"]]) // 144
                inf = int(parts[col["infector"]])
                if not (1 <= d <= 28) or inf == 4294967295:
                    continue
                known += 1
                if flag.get(inf, 0):
                    caused += 1
                if flag.get(int(parts[col["agent"]]), 0):
                    received += 1
        ids, total, _ = index_table(run / "trace.tsv")
        for a in ids.tolist():
            idx_all += 1
            idx_class += flag.get(a, 0)
    return {"class_share_of_population": pop_class / max(pop_all, 1) if not rotate else pop_class / max(n_agents, 1),
            "class_share_of_infections_caused": caused / max(known, 1), "class_share_of_infections_received": received / max(known, 1),
            "class_share_of_index_cases": idx_class / max(idx_all, 1)}


def class_hours_share(label, rotate=False):
    """Class share of discretionary hours from the accepted calibration movement log (class = multiplier above 1 before scaling)."""
    if rotate:
        return {}
    state = json.loads((R7 / "state" / f"scale_{label}.json").read_text())
    it = state["accepted_iteration"] if state["accepted_iteration"] is not None else len(state["history"]) - 1
    scale = {int(k): v for k, v in state["scale"]["wd"].items()}
    mob = read_mob(R7 / "mob" / label / f"it{it}" / "mobility.csv")
    cls = tot = 0.0
    for r in mob.values():
        if int(r["type"]) in ELIGIBLE and int(r["age"]) >= 15:
            h = float(r["h_wd_role_disc"]) + float(r["h_we_role_disc"])
            tot += h
            if float(r["m"]) / scale[int(r["type"])] > 1.0001:
                cls += h
    return {"class_share_of_discretionary_hours": cls / tot}


def s2():
    rows, joint = [], []
    labels = [p.stem[6:] for p in sorted((R7 / "state").glob("scale_s2_*.json"))]
    for i, label in enumerate(labels):
        try:
            dirs, state = run_dirs_of(label)
        except FileNotFoundError:
            continue
        row, j, _ = cell_stats(label, dirs, 11 * i)
        rotate = label == "s2_rotate1"
        row.update(class_flow(dirs, rotate))
        row.update(class_hours_share(label, rotate))
        row.update({"background_coefficient": state["k"], "calibration_matched": state["matched"]})
        rows.append(row)
        joint += j
        print(label, "R", round(row["early_R"], 3), "kmom", round(row["k_mom"], 3), "zero", round(row["share_0"], 3), "caused", round(row["class_share_of_infections_caused"], 4),
              "hours", round(row.get("class_share_of_discretionary_hours", float("nan")), 4), flush=True)
    write_csv(OUT / "47_s2_summary.csv", rows)
    write_csv(OUT / "47_s2_offspring.csv", joint)
    return rows


def home_xy():
    """Home coordinates of every agent (cached)."""
    cache = R7 / "state" / "home_xy.npy"
    if cache.exists():
        return np.load(cache)
    ROOT = HERE.parents[1]
    locs = json.load(open(ROOT / "inputRealExample" / "locations1.json"))["places"]
    coord = {p["ID"]: p["coordinates"] for p in locs}
    people = json.load(open(ROOT / "inputRealExample" / "agents2.json"))["people"]
    xy = np.full((len(people), 2), np.nan)
    for i, person in enumerate(people):
        for l in person["locations"]:
            if l["typeID"] == 2 and l["locID"] in coord:
                xy[i] = coord[l["locID"]]
                break
    np.save(cache, xy)
    return xy


def hvi_children_stats(dirs, xy):
    """For infections of days 1 to 28 with a known infector in the class: venue-type shares, distinct venues per class index case,
    and the distance between the infector's and the infectee's homes (metres)."""
    type_counts = Counter()
    dist = []
    dist_other = []
    distinct = []
    for run in dirs:
        hv = load_hvi_full(run / "hvi.csv")
        flag = {a: v[3] for a, v in hv.items()}
        kids = defaultdict(list)
        with open(run / "trace.tsv") as handle:
            header = handle.readline().rstrip("\n").split("\t")
            col = {name: i for i, name in enumerate(header)}
            day = {}
            for line in handle:
                parts = line.split("\t")
                d = int(parts[col["timestamp"]]) // 144
                inf = int(parts[col["infector"]])
                a = int(parts[col["agent"]])
                day[a] = d
                if inf == 4294967295 or not (1 <= d <= 28):
                    continue
                loc = int(parts[col["location"]])
                if flag.get(inf, 0):
                    type_counts[int(parts[col["locType"]])] += 1
                    dist.append(float(np.hypot(*(xy[a] - xy[inf]))))
                else:
                    if len(dist_other) < 200000:
                        dist_other.append(float(np.hypot(*(xy[a] - xy[inf]))))
                kids[inf].append((d, loc))
        ids, total, _ = index_table(run / "trace.tsv")
        for a, o in zip(ids.tolist(), total.tolist()):
            if flag.get(a, 0) and o > 0:
                lim = day.get(a, 0) + 14
                distinct.append(len({loc for d, loc in kids.get(a, ()) if d <= lim}))
    dist = np.asarray([d for d in dist if np.isfinite(d)])
    dist_other = np.asarray([d for d in dist_other if np.isfinite(d)])
    tot = sum(type_counts.values())
    out = {"class_children": tot,
           "class_mean_distinct_venues_of_offspring": float(np.mean(distinct)) if distinct else None,
           "class_index_cases_with_offspring": len(distinct),
           "class_mean_home_distance_m": float(dist.mean()) if dist.size else None, "class_p90_home_distance_m": float(np.percentile(dist, 90)) if dist.size else None,
           "other_mean_home_distance_m": float(dist_other.mean()) if dist_other.size else None, "other_p90_home_distance_m": float(np.percentile(dist_other, 90)) if dist_other.size else None}
    for t, name in LOCTYPE_NAMES.items():
        out[f"class_children_share_{name}"] = type_counts.get(t, 0) / max(tot, 1)
    return out


def fixed_dirs(name):
    return sorted(p.parent for p in (R7 / "r7" / name).glob("rep*/trace.tsv"))


def s34(prefix, labels, tag):
    xy = home_xy()
    rows, joint = [], []
    for i, label in enumerate(labels):
        dirs = fixed_dirs(label) if prefix != "s4_v1" else None
        if label == "s4_v1":
            dirs, _ = run_dirs_of(S2_CELL_LABEL)
        row, j, _ = cell_stats(label, dirs, 17 * i)
        row.update(hvi_children_stats(dirs, xy))
        rows.append(row)
        joint += j
        print(label, "R", round(row["early_R"], 3), "kmom", round(row["k_mom"], 3), "kml", round(row["k_ml"], 3), "zero", round(row["share_0"], 3),
              "distinct", row["class_mean_distinct_venues_of_offspring"], "dist", row["class_mean_home_distance_m"], flush=True)
    write_csv(OUT / f"47_{tag}_summary.csv", rows)
    write_csv(OUT / f"47_{tag}_offspring.csv", joint)


S2_CELL_LABEL = "s2_f0.05_F3"


def s3():
    s34("s3", ["s3_rep1", "s3_rep3", "s3_rep10"], "s3")


def s4():
    s34("s4", ["s4_v1", "s4_v2", "s4_v4"], "s4")


def s5():
    from analyze import load_daily
    from analyze_round6 import episode_pairs, pearson, spearman as sp6
    rows, joint = [], []
    for i, a in enumerate(("0.5", "0.3")):
        label = f"s5_unc_a{a}"
        dirs, state = run_dirs_of(label)
        row, j, _ = cell_stats(label, dirs, 23 * i)
        coupled = next(r for r in csv.DictReader(open(OUT / "47_s1_summary.csv")) if r["cell"] == f"s1_a{a}")
        row.update({"coupled_k_mom": float(coupled["k_mom"]), "k_mom_ratio_to_coupled": row["k_mom"] / float(coupled["k_mom"]),
                    "coupled_mean_m_index": float(coupled["mean_m_index_cases"]), "background_coefficient": state["k"]})
        rows.append(row)
        joint += j
        print(label, "kmom", round(row["k_mom"], 3), "ratio", round(row["k_mom_ratio_to_coupled"], 3), "m_idx", round(row["mean_m_index_cases"], 3), flush=True)
    write_csv(OUT / "47_s5_summary.csv", rows)
    write_csv(OUT / "47_s5_offspring.csv", joint)
    # infection pairs, persistent main arm
    runs = sorted((R7 / "r7" / "s5_pairs").glob("rep*"))
    per_rep = []
    for run in runs:
        last_day = len(load_daily(run / "stdout.txt")) - 1
        pairs, with_two, multi, n_agents = episode_pairs(run, last_day)
        per_rep.append(pairs)
    allp = [p for rep in per_rep for p in rep]
    x = [p[2] for p in allp]; y = [p[4] for p in allp]
    rp, rs = pearson(x, y), sp6(x, y)
    rng = np.random.default_rng(BOOT_SEED + 91)
    bp, bs = [], []
    for _ in range(400):
        pick = rng.integers(0, len(per_rep), size=len(per_rep))
        pp = [p for i in pick for p in per_rep[i]]
        bp.append(pearson([p[2] for p in pp], [p[4] for p in pp])); bs.append(sp6([p[2] for p in pp], [p[4] for p in pp]))
    lo, hi = interval(bp); slo, shi = interval(bs)
    write_csv(OUT / "47_s5_pairs.csv", [{"arm": "s1_a0.3 persistent HVI", "replicates": len(per_rep), "pairs": len(allp), "pearson": rp, "pearson_low": lo, "pearson_high": hi,
                                           "spearman": rs, "spearman_low": slo, "spearman_high": shi, "reference_persistent_trait_pearson_R6_2": 0.5436}])
    print("S5 pairs", len(allp), "pearson", round(rp, 3), (round(lo, 3), round(hi, 3)), "spearman", round(rs, 3))


def s6():
    from analyze import load_daily
    rows = []
    for tag in ("cell", "shape"):
        prep = json.loads((R7 / "state" / f"s6_prep_{tag}.json").read_text())
        data = {}
        for mode in ("none", "capTop", "scaleAll", "close"):
            label = f"s6_{tag}_{mode}"
            runs = sorted((R7 / "r7" / label).glob("rep*"))
            d84 = np.asarray([float(load_daily(r / "stdout.txt")[83]["INF"]) for r in runs])
            d56 = np.asarray([float(load_daily(r / "stdout.txt")[55]["INF"]) for r in runs])
            d28 = np.asarray([float(load_daily(r / "stdout.txt")[27]["INF"]) for r in runs])
            data[mode] = (d28, d56, d84)
        none = data["none"]
        per_day = prep["baseline_post_hours"] / 14.0
        for mode in ("capTop", "scaleAll", "close"):
            removes = {"capTop": prep["cap_removes"], "scaleAll": prep["scale_removes"], "close": prep["close_options"][prep["close_choice"] - 1]["removes"]}[mode]
            hours = removes * per_day * 63
            rng = np.random.default_rng(BOOT_SEED + 700 + len(rows))
            ratios, averted = [], []
            n = len(none[2])
            for _ in range(BOOT):
                pick = rng.integers(0, n, size=n)
                a = data[mode][2][pick].mean(); b = none[2][pick].mean()
                ratios.append(a / b); averted.append((b - a) / hours * 1000.0)
            lo, hi = interval(ratios); alo, ahi = interval(averted)
            rows.append({"base": tag, "intervention": mode, "replicates": n, "hours_removed_fraction": removes, "hours_removed_total": hours,
                         "infections_day84_none": float(none[2].mean()), "infections_day84": float(data[mode][2].mean()),
                         "ratio_to_none": float(data[mode][2].mean() / none[2].mean()), "ratio_low": lo, "ratio_high": hi,
                         "infections_day56_ratio": float(data[mode][1].mean() / none[1].mean()),
                         "infections_averted_per_1000_hours_removed": float((none[2].mean() - data[mode][2].mean()) / hours * 1000.0),
                         "averted_per_1000h_low": alo, "averted_per_1000h_high": ahi,
                         "closure_types": " ".join(map(str, prep["close_types"])) if mode == "close" else "", "scale_param": prep["scale_param"] if mode == "scaleAll" else ""})
            print(tag, mode, "removes", round(removes, 4), "ratio", round(rows[-1]["ratio_to_none"], 3), "per1000h", round(rows[-1]["infections_averted_per_1000_hours_removed"], 3), flush=True)
    write_csv(OUT / "47_s6_summary.csv", rows)


def main():
    which = sys.argv[1]
    if which == "t3_s1":
        t_tests([f"s1_a{a}" for a in ("3", "1", "0.5", "0.3", "0.15")], "s1")
    elif which == "s1":
        s1()
    elif which == "t5":
        t5()
    elif which == "s2":
        s2()
    elif which == "s3":
        s3()
    elif which == "s5":
        s5()
    elif which == "s6":
        s6()
    elif which == "s4":
        s4()
    elif which == "t6":
        t6()
    elif which == "t3_s2":
        t_tests([p.stem[6:] for p in sorted((R7 / "state").glob("scale_s2_*.json"))], "s2")
    else:
        raise SystemExit("unknown task")


if __name__ == "__main__":
    main()
