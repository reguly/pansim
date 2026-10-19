#!/usr/bin/env python3
"""Note 49 round 8: R8-0 tables and predictions, and the analysis of the S8 arms."""
import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from r6stats import write_csv  # noqa: E402

R8 = HERE / "results" / "round8"
OUT = HERE.parent
ELIGIBLE = (4, 5, 6, 7, 8)
HPT = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 22, 33, 44)
HDT = (1, 5, 6, 7, 8, 9, 10)
HIGH = (5, 6, 9, 10)
K_BASE = 4.59
# share of infectious time by well-being state (47_r70_state_hours.csv): W, N, M, S
STATE_SHARE = {"W": 0.744, "N": 0.113, "M": 0.117, "S": 0.026}


def load_log(path):
    cols = {"type": [], "age": [], "days": [], "cls": []}
    for t in HPT:
        cols[f"hpt_{t}"] = []
    for t in HDT:
        cols[f"hdt_{t}"] = []
    with open(path) as handle:
        for r in csv.DictReader(handle):
            cols["type"].append(int(r["type"]))
            cols["age"].append(int(r["age"]))
            cols["days"].append(float(r["days_weekday"]) + float(r["days_weekend"]))
            for t in HPT:
                cols[f"hpt_{t}"].append(float(r[f"hpt_{t}"]))
            for t in HDT:
                cols[f"hdt_{t}"].append(float(r[f"hdt_{t}"]))
    data = {k: np.asarray(v) for k, v in cols.items() if v}
    days = data["days"]
    for t in HPT:
        data[f"hpt_{t}"] = data[f"hpt_{t}"] / days
    for t in HDT:
        data[f"hdt_{t}"] = data[f"hdt_{t}"] / days
    dump = path.parent / "hvi.csv"
    cls = np.zeros(len(days), dtype=bool)
    if dump.exists():
        with open(dump) as handle:
            next(handle)
            for i, line in enumerate(handle):
                cls[i] = line.split(",")[4] == "1"
    data["cls"] = cls
    return data


NAME2TYPE = {"home": 2, "school": 3, "classroom": 33, "work_type4": 4, "work_type13": 13, "public_space": 1, "restaurant": 5, "large_venue": 6,
             "shop_short": 7, "shop_long": 8, "church": 9, "recreation": 10, "hospital": 12, "health_centre": 14, "nursing_home": 22, "university": 44}
_PHI = {}


def productivity():
    """Offspring weight per hour at a venue of each physical type, relative to a home hour, at L = 1. Derived from the infection shares by venue type
    of the round-7 S1 arm of shape 3 (nearest to the baseline) and the hours per type of the baseline movement log; the share of infectious time spent
    at home in N, M and S (25.6%) is added to home hours. Public space has L = 0 and no productivity."""
    if _PHI:
        return _PHI
    row = [r for r in csv.DictReader(open(OUT / "47_s1_summary.csv")) if r["cell"] == "s1_a3"][0]
    share = {NAME2TYPE[k[len("infections_share_"):]]: float(v) for k, v in row.items()
             if k.startswith("infections_share_") and k[len("infections_share_"):] in NAME2TYPE}
    base = load_log(R8 / "mob8" / "base" / "mobility.csv")
    n = len(base["days"])
    phi = {}
    for t in HPT:
        hours = float(base[f"hpt_{t}"].sum())
        if t == 2:
            phi[t] = share.get(t, 0.0) / (STATE_SHARE["W"] * hours + (1.0 - STATE_SHARE["W"]) * 24.0 * n)
        else:
            phi[t] = share.get(t, 0.0) / (STATE_SHARE["W"] * hours) if hours > 0 else 0.0
    ref = phi[2]
    for t in HPT:
        _PHI[t] = phi[t] / ref
    return _PHI


def weights(data, lam, isolation=False):
    """Infectious-time offspring weight per agent: W-state hours at venues from the movement log times productivity times L (lam on types 5, 6, 9, 10,
    0 on public space). Infectious time in N, M and S is spent at home (24 hours) unless the agent breaks isolation (then only S is at home)."""
    phi = productivity()
    wW = np.zeros(len(data["days"]))
    for t in HPT:
        L = 0.0 if t == 1 else (lam if t in HIGH else 1.0)
        wW += phi[t] * L * data[f"hpt_{t}"]
    home = 24.0 * phi[2]
    plain = STATE_SHARE["W"] * wW + (1.0 - STATE_SHARE["W"]) * home
    broken = (STATE_SHARE["W"] + STATE_SHARE["N"] + STATE_SHARE["M"]) * wW + STATE_SHARE["S"] * home
    return np.where(data["cls"], broken, plain) if isolation else plain


def predicted_k(cv2, cv2_base=0.0):
    """1 + 1/k = (1 + 1/4.59)(1 + CV^2 of the weights), the CV^2 taken relative to the weights of the baseline (L = 1, no class)."""
    return 1.0 / ((1.0 + 1.0 / K_BASE) * (1.0 + cv2) / (1.0 + cv2_base) - 1.0)


def groups(data):
    el = np.isin(data["type"], ELIGIBLE) & (data["age"] >= 15)
    return {"class": data["cls"] & el, "others_eligible": ~data["cls"] & el, "all_others": ~data["cls"], "all": np.ones(len(el), dtype=bool)}


def hours_table(variants):
    rows = []
    for name, data in variants.items():
        for gname, mask in groups(data).items():
            if not mask.any():
                continue
            row = {"movement_variant": name, "group": gname, "agents": int(mask.sum())}
            disc = {t: float(data[f"hdt_{t}"][mask].mean()) for t in HDT}
            total_disc = sum(disc.values())
            for t in HDT:
                row[f"disc_role_hours_type{t}"] = disc[t]
            row["disc_role_hours_total"] = total_disc
            row["disc_role_share_at_high_types"] = sum(disc[t] for t in HIGH) / total_disc if total_disc else 0.0
            allh = {t: float(data[f"hpt_{t}"][mask].mean()) for t in HPT}
            row["all_hours_at_high_types"] = sum(allh[t] for t in HIGH)
            row["all_hours_at_high_types_nondisc_role"] = sum(allh[t] - (disc[t] if t in disc else 0.0) for t in HIGH)
            row["all_hours_home_type2"] = allh[2]
            row["all_hours_public_space"] = allh[1]
            for t in HPT:
                row[f"all_hours_type{t}"] = allh[t]
            rows.append(row)
    return rows


ARM_PRED = {}
for lam in (3, 10, 30):
    ARM_PRED[f"s8_1_L{lam}"] = ("base", lam, False)
    ARM_PRED[f"s8_2_t0.5_L{lam}"] = ("f3_t0.5", lam, False)
    ARM_PRED[f"s8_2_t1_L{lam}"] = ("f3_t1", lam, False)
    ARM_PRED[f"s8_3_L{lam}"] = ("f3_t1_o0.2", lam, False)
for f, v in ((5, "c5_F1"), (20, "c20_F1")):
    for lam in (1, 10):
        ARM_PRED[f"s8_4_f{f}_L{lam}"] = (v, lam, True)
ARM_PRED["check_base_L1"] = ("base", 1, False)
ARM_PRED["check_s2cell_F3_L1"] = ("f3_t0", 1, False)


def r80():
    names = ["base", "f3_t0", "f3_t0.5", "f3_t1", "f3_t1_o0.2", "c5_F1", "c20_F1"]
    variants = {n: load_log(R8 / "mob8" / n / "mobility.csv") for n in names}
    write_csv(OUT / "50_r80_hours_by_type.csv", hours_table(variants))
    wb = weights(variants["base"], 1)
    base_w1 = wb.mean()
    cv2_base = float(wb.var() / wb.mean() ** 2)
    phi = productivity()
    write_csv(OUT / "50_r80_productivity.csv", [{"location_type": t, "relative_offspring_weight_per_hour": phi[t]} for t in HPT])
    rows = []
    k0 = {}
    for arm, (variant, lam, iso) in ARM_PRED.items():
        data = variants[variant]
        w = weights(data, lam, iso)
        cls = data["cls"]
        cv2 = float(w.var() / w.mean() ** 2)
        row = {"arm": arm, "movement_variant": variant, "lambda": lam, "isolation_breaking": int(iso),
               "mean_weight": float(w.mean()), "exposure_factor_vs_L1": float(w.mean() / base_w1), "cv2_of_weights": cv2, "cv2_of_baseline_weights": cv2_base, "predicted_k": predicted_k(cv2, cv2_base)}
        if cls.any():
            r = float(w[cls].mean() / w[~cls].mean())
            row["class_to_others_offspring_ratio_r"] = r
            # share of the class's hours at high-L venues, all roles, and its share of the population-wide high-L hours
            high = sum(data[f"hpt_{t}"] for t in HIGH)
            row["class_high_hours_per_day"] = float(high[cls].mean())
            row["others_high_hours_per_day"] = float(high[~cls].mean())
            row["class_share_of_high_hours"] = float(high[cls].sum() / high.sum())
            row["class_share_of_weight"] = float(w[cls].sum() / w.sum())
            row["class_share_of_population"] = float(cls.mean())
        row["skip_rule_predicted_k_above_3"] = int(row["predicted_k"] > 3.0)
        row["acceptance_low"] = row["predicted_k"]
        row["acceptance_high"] = 1.5 * row["predicted_k"] + 0.5
        rows.append(row)
        k0[arm] = 0.00041 / row["exposure_factor_vs_L1"]
    write_csv(OUT / "50_r80_predictions.csv", rows)
    (R8 / "state").mkdir(parents=True, exist_ok=True)
    (R8 / "state" / "k0.json").write_text(json.dumps(k0, indent=1))
    for r in rows:
        print(r["arm"], "f", round(r["exposure_factor_vs_L1"], 2), "cv2", round(r["cv2_of_weights"], 3), "kpred", round(r["predicted_k"], 2),
              "r", round(r.get("class_to_others_offspring_ratio_r", float("nan")), 2), "skip", r["skip_rule_predicted_k_above_3"])


def rows_of(path):
    with open(path) as handle:
        return list(csv.DictReader(handle))


def hours_shares(variant):
    """Class share of discretionary hours and of hours at the high-L types (all roles), and the class hours at the high-L types per day, from the movement log."""
    data = load_log(R8 / "mob8" / variant / "mobility.csv")
    el = np.isin(data["type"], ELIGIBLE) & (data["age"] >= 15)
    cls = data["cls"]
    disc = sum(data[f"hdt_{t}"] for t in HDT)
    high = sum(data[f"hpt_{t}"] for t in HIGH)
    return {"class_share_of_discretionary_hours": float(disc[cls & el].sum() / disc[el].sum()),
            "class_share_of_high_L_hours": float(high[cls].sum() / high.sum()),
            "class_high_L_hours_per_day": float(high[cls].mean()), "others_high_L_hours_per_day": float(high[~cls].mean()),
            "class_disc_hours_per_day": float(disc[cls & el].mean()), "others_disc_hours_per_day": float(disc[~cls & el].mean())}


ARM_MOVEMENT = {}
for _lam in (3, 10, 30):
    ARM_MOVEMENT[f"s8_2_t0.5_L{_lam}"] = "f3_t0.5"
    ARM_MOVEMENT[f"s8_2_t1_L{_lam}"] = "f3_t1"
    ARM_MOVEMENT[f"s8_3_L{_lam}"] = "f3_t1_o0.2"
for _f, _v in ((5, "c5_F1"), (20, "c20_F1")):
    for _lam in (1, 10):
        ARM_MOVEMENT[f"s8_4_f{_f}_L{_lam}"] = _v


def run_dirs8(label):
    state = json.loads((R8 / "state" / f"r8_{label}.json").read_text())
    return sorted(p.parent for p in (R8 / state["prefix"]).glob("rep*/trace.tsv")), state


def s8(labels):
    import analyze_round7 as A7
    s2_scale = A7.scale_of("s2_f0.05_F3")
    A7.scale_of = lambda label: s2_scale if label.startswith(("s8_2", "s8_3")) else None
    pred = {r["arm"]: r for r in rows_of(OUT / "50_r80_predictions.csv")}
    rows, joint = [], []
    for i, label in enumerate(labels):
        try:
            dirs, state = run_dirs8(label)
        except FileNotFoundError:
            continue
        row, j, _ = A7.cell_stats(label, dirs, 31 * i)
        flow = A7.class_flow(dirs)
        row.update(flow)
        if label in ARM_MOVEMENT:
            row.update(hours_shares(ARM_MOVEMENT[label]))
        cp, sp = flow["class_share_of_population"], flow["class_share_of_infections_caused"]
        if 0 < cp < 1 and 0 < sp < 1:
            row["class_offspring_ratio_r_observed"] = (sp / cp) / ((1 - sp) / (1 - cp))
        pr = pred.get(label)
        if pr:
            row["predicted_k"] = float(pr["predicted_k"])
            row["predicted_r"] = float(pr.get("class_to_others_offspring_ratio_r", "nan") or "nan")
            row["acceptance_low"] = float(pr["acceptance_low"])
            row["acceptance_high"] = float(pr["acceptance_high"])
            row["observed_k_in_acceptance_range"] = int(row["acceptance_low"] <= row["k_mom"] <= row["acceptance_high"])
            row["skip_rule_predicted_k_above_3"] = int(pr["skip_rule_predicted_k_above_3"])
        row.update({"background_coefficient": state["k"], "calibration_matched": state["matched"]})
        rows.append(row)
        joint += j
        print(label, "R", round(row["early_R"], 3), "kmom", round(row["k_mom"], 3), "kml", round(row["k_ml"], 3), "zero", round(row["share_0"], 3),
              "80%", round(row.get("share_of_index_cases_causing_80pct", 0), 3), "r", round(row.get("class_offspring_ratio_r_observed", float("nan")), 2),
              "pred k", round(row.get("predicted_k", float("nan")), 2), "day28", round(row["day28_vs_6211.25"], 3), flush=True)
    write_csv(OUT / "50_s8_summary.csv", rows)
    write_csv(OUT / "50_s8_offspring.csv", joint)
    return rows


def s85_rows(base):
    from analyze import load_daily
    from r6stats import BOOT, BOOT_SEED, interval
    prep = json.loads((R8 / "state" / f"s85_prep_{base}.json").read_text())
    per_day_disc = prep["post_hours_disc"] / 14.0
    per_day_high = prep["post_hours_high"] / 14.0
    removed = {"capTop": prep["cap"], "scaleAll": prep["scale"], "close": prep["close"]}
    data = {}
    for mode in ("none", "capTop", "scaleAll", "close"):
        runs = sorted((R8 / "r8" / f"s85_{base}_{mode}").glob("rep*"))
        data[mode] = np.asarray([float(load_daily(r / "stdout.txt")[83]["INF"]) for r in runs])
    n = len(data["none"])
    rows = []
    rng = np.random.default_rng(BOOT_SEED + 850)
    picks = [rng.integers(0, n, size=n) for _ in range(BOOT)]
    for mode in ("capTop", "scaleAll", "close"):
        rd, rh = removed[mode]
        hours_d = rd * per_day_disc * 63.0
        hours_h = rh * per_day_high * 63.0
        ratios, ad, ah = [], [], []
        for pick in picks:
            a, b = data[mode][pick].mean(), data["none"][pick].mean()
            ratios.append(a / b)
            ad.append((b - a) / hours_d * 1000.0)
            ah.append((b - a) / hours_h * 1000.0)
        rows.append({"base": base, "intervention": mode, "replicates": n, "disc_hours_removed_fraction": rd, "high_L_hours_removed_fraction": rh,
                     "disc_hours_removed_total": hours_d, "high_L_hours_removed_total": hours_h,
                     "infections_day84_none": float(data["none"].mean()), "infections_day84": float(data[mode].mean()),
                     "ratio_to_none": float(data[mode].mean() / data["none"].mean()), "ratio_low": interval(ratios)[0], "ratio_high": interval(ratios)[1],
                     "averted_per_1000_disc_hours": float((data["none"].mean() - data[mode].mean()) / hours_d * 1000.0),
                     "averted_per_1000_disc_hours_low": interval(ad)[0], "averted_per_1000_disc_hours_high": interval(ad)[1],
                     "averted_per_1000_high_L_hours": float((data["none"].mean() - data[mode].mean()) / hours_h * 1000.0),
                     "averted_per_1000_high_L_hours_low": interval(ah)[0], "averted_per_1000_high_L_hours_high": interval(ah)[1],
                     "scale_param": prep["scale_param"] if mode == "scaleAll" else ""})
    # ratio of the cap to scale-all in infections averted per discretionary hour removed, bootstrapped over replicates
    def per_hour(mode, pick):
        rd, _ = removed[mode]
        return (data["none"][pick].mean() - data[mode][pick].mean()) / (rd * per_day_disc * 63.0)
    rat = [per_hour("capTop", pick) / per_hour("scaleAll", pick) for pick in picks]
    point = per_hour("capTop", np.arange(n)) / per_hour("scaleAll", np.arange(n))
    lo, hi = interval(rat)
    for r in rows:
        r["cap_over_scaleall_per_disc_hour"] = float(point)
        r["cap_over_scaleall_low"] = lo
        r["cap_over_scaleall_high"] = hi
    for r in rows:
        print(base, r["intervention"], "removes", round(r["disc_hours_removed_fraction"], 4), "disc,", round(r["high_L_hours_removed_fraction"], 4), "high; ratio", round(r["ratio_to_none"], 3),
              "per1000 disc", round(r["averted_per_1000_disc_hours"], 3), "per1000 high", round(r["averted_per_1000_high_L_hours"], 3))
    print(base, "cap over scaleAll", round(point, 2), (round(lo, 2), round(hi, 2)))
    return rows


def s85(*bases):
    rows = []
    for base in bases:
        rows += s85_rows(base)
    write_csv(OUT / "50_s85_summary.csv", rows)


def main():
    cmd = sys.argv[1]
    if cmd == "s85":
        s85(*sys.argv[2:])
    if cmd == "r80":
        r80()
    elif cmd == "s8":
        s8(sys.argv[2:])


if __name__ == "__main__":
    main()
