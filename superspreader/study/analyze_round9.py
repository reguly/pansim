#!/usr/bin/env python3
"""Note 52 round 9: R9-2 assortative mixing from the round-8 traces, R9-3 per-replicate check, R9-1 analysis."""
import csv
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from r6stats import write_csv  # noqa: E402

OUT = HERE.parent
R8 = HERE / "results" / "round8"
R9 = HERE / "results" / "round9"
UNKNOWN = 4294967295
STEPS = 144


def run_dirs(base, label):
    state = json.loads((base / "state" / f"r{base.name[-1]}_{label}.json").read_text())
    return sorted(p.parent for p in (base / state["prefix"]).glob("rep*/trace.tsv"))


def class_flags(path):
    cls = []
    with open(path) as handle:
        next(handle)
        for line in handle:
            cls.append(line.split(",")[4] == "1")
    return np.asarray(cls)


def r92_arm(label, base=R8):
    dirs = run_dirs(base, label)
    cc = co = oc = oo = 0
    n_class = n_other = 0
    class_infected = other_infected = 0
    seeds_class = 0
    for run in dirs:
        cls = class_flags(run / "hvi.csv")
        n_class += int(cls.sum())
        n_other += int((~cls).sum())
        infected_class = set()
        infected_other = set()
        with open(run / "trace.tsv") as handle:
            header = handle.readline().rstrip("\n").split("\t")
            col = {name: i for i, name in enumerate(header)}
            for line in handle:
                parts = line.split("\t")
                day = int(parts[col["timestamp"]]) // STEPS
                if day > 28:
                    continue
                a = int(parts[col["agent"]])
                inf = int(parts[col["infector"]])
                if cls[a]:
                    infected_class.add(a)
                else:
                    infected_other.add(a)
                if inf == UNKNOWN or day < 1:
                    if cls[a]:
                        seeds_class += 1
                    continue
                ic, ac = bool(cls[inf]), bool(cls[a])
                if ic and ac:
                    cc += 1
                elif ic:
                    co += 1
                elif ac:
                    oc += 1
                else:
                    oo += 1
        class_infected += len(infected_class)
        other_infected += len(infected_other)
    total = cc + co + oc + oo
    to_class = cc + oc
    row = {
        "arm": label, "replicates": len(dirs), "class_agents": n_class, "other_agents": n_other,
        "infections_class_to_class": cc, "infections_class_to_other": co, "infections_other_to_class": oc, "infections_other_to_other": oo,
        "share_class_to_class": cc / total, "share_class_to_other": co / total, "share_other_to_class": oc / total, "share_other_to_other": oo / total,
        "class_share_of_infections_caused": (cc + co) / total, "class_share_of_infections_received": to_class / total,
        "fraction_of_class_infected_by_day28": class_infected / n_class,
        "fraction_of_others_infected_by_day28": other_infected / n_other,
        "ratio_of_infected_fractions_class_to_others": (class_infected / n_class) / (other_infected / n_other),
        "share_of_class_infections_with_class_infector": cc / to_class if to_class else float("nan"),
    }
    per_c = (cc + co) / n_class
    per_o = (oc + oo) / n_other
    row["offspring_ratio_r_observed"] = per_c / per_o
    row["offspring_ratio_r_class_to_other_only_over_other_to_other"] = (co / n_class) / (oo / n_other)
    row["offspring_ratio_r_class_to_other_over_all_other"] = (co / n_class) / per_o
    row["offspring_per_class_agent_to_class"] = cc / n_class
    row["offspring_per_class_agent_to_other"] = co / n_class
    row["offspring_per_other_agent_to_class"] = oc / n_other
    row["offspring_per_other_agent_to_other"] = oo / n_other
    return row


def r92():
    rows = [r92_arm(a) for a in ("s8_3_L10", "s8_2_t1_L30", "s8_2_t1_L10")]
    write_csv(OUT / "53_r92_assortative_mixing.csv", rows)
    for r in rows:
        print(r["arm"], "r", round(r["offspring_ratio_r_observed"], 1), "excluding class targets", round(r["offspring_ratio_r_class_to_other_only_over_other_to_other"], 1),
              "class->other over all other", round(r["offspring_ratio_r_class_to_other_over_all_other"], 1),
              "CC share", round(r["share_class_to_class"], 3), "class infected", round(r["fraction_of_class_infected_by_day28"], 3),
              "class infections with class infector", round(r["share_of_class_infections_with_class_infector"], 3))


def r93():
    from analyze import load_daily
    rows = []
    vals = {}
    for mode in ("capTop", "scaleAll"):
        runs = sorted((R8 / "r8" / f"s85_s8_3_L10_{mode}").glob("rep*"))
        vals[mode] = [int(load_daily(r / "stdout.txt")[83]["INF"]) for r in runs]
    a, b = np.asarray(vals["capTop"]), np.asarray(vals["scaleAll"])
    for i, (x, y) in enumerate(zip(a, b), start=1):
        rows.append({"replicate": i, "capTop_day84": int(x), "scaleAll_day84": int(y), "difference": int(y - x)})
    write_csv(OUT / "53_r93_s83_cap_vs_scaleall_day84.csv", rows)
    print("capTop", a.tolist(), "mean", a.mean())
    print("scaleAll", b.tolist(), "mean", b.mean())
    print("identical replicates:", int((a == b).sum()), "mean abs diff", float(np.abs(a - b).mean()), "corr", float(np.corrcoef(a, b)[0, 1]), "sd of difference", float((b - a).std(ddof=1)))




# ---------------------------------------------------------------- R9-1

def nb_shares(k, mean, nmax=4000):
    """Zero share and smallest share of infectors causing 80% of offspring, for a negative binomial of this k at this mean.
    The bin where the 80% threshold falls is split, as the empirical estimator does over individuals with the same count."""
    from math import lgamma, log
    logp = [k * log(k / (k + mean)) + n * log(mean / (k + mean)) + lgamma(n + k) - lgamma(k) - lgamma(n + 1) for n in range(nmax)]
    p = np.exp(np.asarray(logp))
    p = p / p.sum()
    n = np.arange(nmax)
    off = p * n
    total = off.sum()
    people = 0.0
    got = 0.0
    for j in range(nmax - 1, -1, -1):     # from the largest offspring count downward
        if off[j] <= 0.0:
            continue
        if got + off[j] >= 0.8 * total:
            people += p[j] * (0.8 * total - got) / off[j]
            break
        got += off[j]
        people += p[j]
    return float(p[0]), float(people)


def composition_predictions():
    """Registered predictions of note 52 (51_round9_composition_predictions.csv), by (scene, shape)."""
    out = {}
    with open(OUT / "51_round9_composition_predictions.csv") as handle:
        for r in csv.DictReader(handle):
            scene = r["scene"].split(" ")[0]
            out[(scene, int(r["shedding_shape"]))] = {"scene_k": float(r["scene_k"]), "shedding_alone_k": float(r["shedding_alone_k"]),
                                                      "predicted_k": float(r["predicted_combined_k"])}
    return out


def shed_stats(dirs):
    """Per-infection shedding multiplier by class, and the offspring of index cases by class and shedding quartile."""
    import r6stats
    shed_class, shed_other = [], []
    cells = {}
    for run in dirs:
        cls = class_flags(run / "hvi.csv")
        shed = {}
        with open(run / "trace.tsv") as handle:
            header = handle.readline().rstrip("\n").split("\t")
            col = {name: i for i, name in enumerate(header)}
            for line in handle:
                parts = line.split("\t")
                a = int(parts[col["agent"]])
                s = float(parts[col["shed"]])
                shed[a] = s
                day = int(parts[col["timestamp"]]) // STEPS
                if 1 <= day <= 28:
                    (shed_class if cls[a] else shed_other).append(s)
        ids, total, _event = r6stats.index_table(run / "trace.tsv")
        for a, o in zip(ids.tolist(), total.tolist()):
            if a in shed:
                cells.setdefault((bool(cls[a]),), []).append((shed[a], o))
    row = {"mean_shed_class": float(np.mean(shed_class)) if shed_class else float("nan"),
           "mean_shed_others": float(np.mean(shed_other)) if shed_other else float("nan"),
           "infections_class": len(shed_class), "infections_others": len(shed_other)}
    row["shed_ratio_class_to_others"] = row["mean_shed_class"] / row["mean_shed_others"] if shed_other else float("nan")
    # interaction: mean offspring of index cases by class and shedding quartile (quartiles over all index cases)
    allpairs = [p for v in cells.values() for p in v]
    if allpairs:
        arr = np.asarray(allpairs)
        qs = np.quantile(arr[:, 0], [0.25, 0.5, 0.75])
        for name, key in (("class", (True,)), ("others", (False,))):
            v = np.asarray(cells.get(key, []))
            if len(v) == 0:
                continue
            q = np.searchsorted(qs, v[:, 0])
            for j in range(4):
                sel = v[q == j]
                row[f"mean_offspring_{name}_shed_q{j + 1}"] = float(sel[:, 1].mean()) if len(sel) else float("nan")
                row[f"index_cases_{name}_shed_q{j + 1}"] = int(len(sel))
    return row


def s9(labels):
    import analyze_round7 as A7
    import analyze_round8 as A8
    s2_scale = A7.scale_of("s2_f0.05_F3")
    A7.scale_of = lambda label: s2_scale if ("t0.5" in label or "t1" in label) else None
    pred = composition_predictions()
    scene_of = {"s8_1_L10": "s8_1_L10", "t0.5_L10": "s8_2_t0.5_L10", "t1_L10": "s8_2_t1_L10", "t1_L30": "s8_2_t1_L30"}
    rows, joint = [], []
    for i, label in enumerate(labels):
        try:
            state = json.loads((R9 / "state" / f"r9_{label}.json").read_text())
        except FileNotFoundError:
            continue
        dirs = sorted(p.parent for p in (R9 / state["prefix"]).glob("rep*/trace.tsv"))
        row, j, _ = A7.cell_stats(label, dirs, 41 * i)
        name = label[len("s9_"):].rsplit("_sh", 1)[0]
        shape = int(label.rsplit("_sh", 1)[1])
        row["shedding_shape"] = shape
        row["scene"] = scene_of.get(name, "none")
        if name != "ref":
            row.update(A7.class_flow(dirs))
            cp, sp = row["class_share_of_population"], row["class_share_of_infections_caused"]
            if 0 < cp < 1 and 0 < sp < 1:
                row["class_offspring_ratio_r_observed"] = (sp / cp) / ((1 - sp) / (1 - cp))
        key = (scene_of.get(name), shape)
        if key in pred:
            p = pred[key]
            row.update({"scene_k_round8": p["scene_k"], "shedding_alone_k_predicted": p["shedding_alone_k"], "predicted_k": p["predicted_k"],
                        "acceptance_low": 0.7 * p["predicted_k"], "acceptance_high": 1.4 * p["predicted_k"]})
            row["observed_k_in_acceptance_range"] = int(row["acceptance_low"] <= row["k_mom"] <= row["acceptance_high"])
            row["observed_over_predicted_k"] = row["k_mom"] / p["predicted_k"]
        elif name == "ref":
            alone = {3: 1.6, 2: 1.21, 1: 0.7}[shape]
            row.update({"predicted_k": alone, "acceptance_low": 0.7 * alone, "acceptance_high": 1.4 * alone})
            row["observed_k_in_acceptance_range"] = int(row["acceptance_low"] <= row["k_mom"] <= row["acceptance_high"])
            row["observed_over_predicted_k"] = row["k_mom"] / alone
        for est in ("mom", "ml"):
            z, s80 = nb_shares(row[f"k_{est}"], 1.4)
            row[f"zero_at_mean_1.4_{est}"] = z
            row[f"share_causing_80pct_at_mean_1.4_{est}"] = s80
        row.update(shed_stats(dirs))
        row.update({"background_coefficient": state["k"], "calibration_matched": state["matched"]})
        rows.append(row)
        joint += j
        print(label, "kmom", round(row["k_mom"], 3), "kml", round(row["k_ml"], 3), "pred", row.get("predicted_k"), "obs/pred", round(row.get("observed_over_predicted_k", float("nan")), 2),
              "zero", round(row["share_0"], 3), "zero@1.4", round(row["zero_at_mean_1.4_mom"], 3), "R", round(row["early_R"], 3), "day28", round(row["day28_vs_6211.25"], 3), flush=True)
    write_csv(OUT / "53_s9_summary.csv", rows)
    write_csv(OUT / "53_s9_offspring.csv", joint)
    return rows


def main():
    cmd = sys.argv[1]
    if cmd == "r92":
        r92()
    elif cmd == "r93":
        r93()
    elif cmd == "s9":
        s9(sys.argv[2:])


if __name__ == "__main__":
    main()
