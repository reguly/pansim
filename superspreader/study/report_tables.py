#!/usr/bin/env python3
"""Print the markdown tables of 43_round6_results.md from the CSVs in superspreader/."""
import csv
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parents[1]


def rows(name):
    with open(OUT / name) as handle:
        return list(csv.DictReader(handle))


def num(row, key):
    value = row.get(key)
    return None if value in (None, "") else float(value)


def fmt(value, digits=3):
    if value is None:
        return "n/a"
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    if abs(value) >= 100:
        return f"{value:.0f}"
    return f"{value:.{digits}g}"


def ci(row, key, digits=3):
    value, lo, hi = num(row, key), num(row, key + "_low"), num(row, key + "_high")
    if value is None:
        return "n/a"
    if lo is None:
        return fmt(value, digits)
    return f"{fmt(value, digits)} ({fmt(lo, digits)} to {fmt(hi, digits)})"


def pct(row, key):
    value, lo, hi = num(row, key), num(row, key + "_low"), num(row, key + "_high")
    if value is None:
        return "n/a"
    if lo is None:
        return f"{100 * value:.1f}%"
    return f"{100 * value:.1f}% ({100 * lo:.1f} to {100 * hi:.1f})"


def table(header, body):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c) for c in line) + " |" for line in body]
    return "\n".join(out)


def r61():
    data = rows("43_r61_grid_summary.csv")
    head = ["shape", "factor", "day 28", "early R", "k moment", "k likelihood", "zero", "NB zero (moment)", "NB zero (likelihood)", "1 to 5", "above 5", "at least 20", "at least 50", "max", "events share", "cluster median", "cluster p90"]
    body = []
    for r in data:
        body.append([
            r["multiplier_shape"], r["event_factor"], fmt(num(r, "day28_mean"), 4), ci(r, "early_R"), ci(r, "k_mom"), ci(r, "k_ml"),
            ci(r, "share_0"), fmt(num(r, "nb_mom_share_0")), fmt(num(r, "nb_ml_share_0")), fmt(num(r, "share_1_to_5")),
            ci(r, "share_above_5"), ci(r, "share_at_least_20"), ci(r, "share_at_least_50", 2), fmt(num(r, "maximum")), pct(r, "event_offspring_share"),
            fmt(num(r, "nonempty_median")), ci(r, "nonempty_p90", 3),
        ])
    return table(head, body)


def r61_nb():
    data = rows("43_r61_grid_summary.csv")
    head = ["shape", "factor", "above 5 data", "NB moment", "NB likelihood", "at least 20 data", "NB moment", "NB likelihood", "at least 50 data", "NB moment", "NB likelihood"]
    body = []
    for r in data:
        body.append([r["multiplier_shape"], r["event_factor"], fmt(num(r, "share_above_5")), fmt(num(r, "nb_mom_share_above_5")), fmt(num(r, "nb_ml_share_above_5")),
                     fmt(num(r, "share_at_least_20")), fmt(num(r, "nb_mom_share_at_least_20")), fmt(num(r, "nb_ml_share_at_least_20")),
                     fmt(num(r, "share_at_least_50")), fmt(num(r, "nb_mom_share_at_least_50")), fmt(num(r, "nb_ml_share_at_least_50"))])
    return table(head, body)


def r63():
    data = rows("43_r63_survey_vs_infected.csv")
    head = ["arm", "a + rho", "shape, population", "shape, index cases", "shape, all infected", "mean trait pop / index / all", "predicted k, population", "predicted k, index (fitted shape)", "predicted k, index (a + rho)", "observed k moment", "observed k likelihood", "obs/pred pop (moment)", "obs/pred index (moment)", "obs/pred index (likelihood)"]
    body = []
    for r in data:
        body.append([
            r["arm"], fmt(num(r, "nominal_a_plus_rho")) if r["nominal_a_plus_rho"] else "n/a (lognormal)", ci(r, "shape_population"), ci(r, "shape_index"), ci(r, "shape_all_infected"),
            " / ".join(fmt(num(r, k)) for k in ("mean_trait_population", "mean_trait_index", "mean_trait_all_infected")),
            ci(r, "pred_k_population_fitted"), ci(r, "pred_k_index_fitted"), fmt(num(r, "pred_k_index_nominal")), ci(r, "obs_k_mom"), ci(r, "obs_k_ml"),
            fmt(num(r, "obs_k_mom_over_pred_population")), fmt(num(r, "obs_k_mom_over_pred_index")), fmt(num(r, "obs_k_ml_over_pred_index")),
        ])
    return table(head, body)


def r64():
    data = rows("43_r64_summary.csv")
    head = ["arm", "calibrated k", "day 28", "early R", "k moment", "k likelihood", "zero (NB moment / likelihood)", "growth rate 7 to 28 (per day)", "doubling time (days)", "day 70", "day 112", "peak prevalence", "peak day", "mean trait of index cases"]
    body = []
    for r in data:
        body.append([r["arm"], fmt(num(r, "background_coefficient"), 4), ci(r, "day28"), ci(r, "early_R"), ci(r, "k_mom"), ci(r, "k_ml"),
                     f"{fmt(num(r, 'share_0'))} ({fmt(num(r, 'nb_mom_share_0'))} / {fmt(num(r, 'nb_ml_share_0'))})",
                     ci(r, "growth_rate_7_28", 3), fmt(num(r, "doubling_time_days_7_28"), 3), ci(r, "day70"), ci(r, "day112"), ci(r, "peak_prevalence"), ci(r, "peak_day", 3), ci(r, "mean_shed_index_cases", 3)])
    return table(head, body)


def r64_ratio():
    data = rows("43_r64_summary.csv")
    head = ["arm", "day 70 / E", "day 70 / E, adjusted", "day 112 / E", "day 112 / E, adjusted to day 28 = 6,000"]
    body = []
    for r in data:
        body.append([r["arm"], ci(r, "ratio_d70_to_E"), ci(r, "adjusted_ratio_d70_to_E"), ci(r, "ratio_d112_to_E"), ci(r, "adjusted_ratio_d112_to_E")])
    return table(head, body)


def r65():
    data = rows("43_r65_ward_sweep.csv")
    head = ["arm", "run set", "chains", "mean offspring", "k moment", "chains above 10", "above 50", "above 100", "above 200", "above 500", "longest chain", "Dwass median (95% range)", "P(longest at least observed)", "five-seed: observed / exact"]
    body = []
    for r in data:
        body.append([r["arm"], r["set_note"], fmt(num(r, "chains")), ci(r, "mean_offspring", 4), fmt(num(r, "k_mom")),
                     ci(r, "chains_above_10", 4), ci(r, "chains_above_50", 3), ci(r, "chains_above_100", 3), ci(r, "chains_above_200", 3), fmt(num(r, "chains_above_500")),
                     ci(r, "longest_chain", 4), f"{fmt(num(r, 'dwass_longest_median'))} ({fmt(num(r, 'dwass_longest_2.5pct'))} to {fmt(num(r, 'dwass_longest_97.5pct'))})",
                     fmt(num(r, "p_longest_at_least_observed")), f"{fmt(num(r, 'five_seed_observed'))} / {fmt(num(r, 'five_seed_exact'))}"])
    return table(head, body)


def r65_hospital():
    data = rows("43_r65_ward_sweep.csv")
    head = ["arm", "hospital cases", "hospital share of all infections", "hospital share of the longest chain", "mean offspring of hospital-infected cases", "share of their children also infected in hospital"]
    body = []
    for r in data:
        body.append([r["arm"], fmt(num(r, "hospital_cases")), pct(r, "hospital_share_of_infections"), pct(r, "hospital_share_of_longest_chain"),
                     ci(r, "mean_offspring_of_hospital_cases"), ci(r, "share_children_also_in_hospital")])
    return table(head, body)


def r62():
    data = rows("43_r62_summary.csv")
    head = ["arm", "infected agents", "agents with two logged episodes", "three or more", "pairs, both observed", "mean offspring ep 1 / ep 2", "Pearson", "Spearman", "pairs, similar incidence", "Pearson, similar", "Spearman, similar", "pairs for 80% power (Pearson / Spearman)"]
    body = []
    for r in data:
        body.append([r["arm"], fmt(num(r, "agents_infected_any")), fmt(num(r, "agents_with_two_logged_episodes")), fmt(num(r, "agents_with_three_or_more")), fmt(num(r, "pairs_both_observed")),
                     f"{fmt(num(r, 'mean_offspring_ep1'))} / {fmt(num(r, 'mean_offspring_ep2'))}", ci(r, "pearson"), ci(r, "spearman"), fmt(num(r, "pairs_similar_incidence")),
                     ci(r, "pearson_similar"), ci(r, "spearman_similar"),
                     f"{fmt(num(r, 'pairs_needed_80pct_pearson'))} / {fmt(num(r, 'pairs_needed_80pct_spearman'))}" if r["pairs_needed_80pct_pearson"] else "not applicable (correlation near zero)"])
    return table(head, body)


def r62_horizon():
    data = rows("43_r62_pairs_by_horizon.csv")
    arms = ["P0", "E", "A0"]
    weeks = sorted({int(r["horizon_weeks"]) for r in data})
    body = []
    for w in weeks:
        line = [w]
        for arm in arms:
            hit = [r for r in data if r["arm"] == arm and int(r["horizon_weeks"]) == w][0]
            line.append(fmt(num(hit, "pairs_both_observed_8_replicates")))
        body.append(line)
    return table(["horizon (weeks)"] + [f"{a} pairs, 8 replicates" for a in arms], body)


def r66():
    data = rows("43_r66_alpha_sweep.csv")
    head = ["alpha", "calibrated k", "day 28", "early R", "k moment", "k likelihood", "zero", "NB zero (moment)", "NB zero (likelihood)", "occupancy at infection, median", "p90"]
    body = []
    for r in data:
        body.append([r["alpha"], fmt(num(r, "background_coefficient"), 4) if r.get("background_coefficient") else "0.00041", fmt(num(r, "day28_mean"), 4), ci(r, "early_R"), ci(r, "k_mom"), ci(r, "k_ml"), ci(r, "share_0"),
                     fmt(num(r, "nb_mom_share_0")), fmt(num(r, "nb_ml_share_0")), ci(r, "occupancy_at_infection_median"), ci(r, "occupancy_at_infection_p90")])
    return table(head, body)


def r67():
    data = rows("43_r67_closed_group_summary.csv")
    head = ["cell", "group size (max)", "event rate", "factor", "background k", "day 28", "early R", "k moment", "k likelihood", "zero", "NB zero (moment)", "NB zero (likelihood)", "1 to 5", "above 5", "at least 20", "at least 50", "max", "events share", "events (12 replicates)", "with an infectious attendee"]
    body = []
    for r in data:
        body.append([r["cell"], r["group_size_max"], fmt(num(r, "event_rate")), fmt(num(r, "event_factor")), fmt(num(r, "background_coefficient"), 4), fmt(num(r, "day28_mean"), 4), ci(r, "early_R"),
                     ci(r, "k_mom"), ci(r, "k_ml"), ci(r, "share_0"), fmt(num(r, "nb_mom_share_0")), fmt(num(r, "nb_ml_share_0")), fmt(num(r, "share_1_to_5")), ci(r, "share_above_5"),
                     ci(r, "share_at_least_20"), ci(r, "share_at_least_50", 2), fmt(num(r, "maximum")), pct(r, "event_offspring_share"), fmt(num(r, "events_total")), fmt(num(r, "events_with_infectious_attendee"))])
    return table(head, body)


if __name__ == "__main__":
    for name in sys.argv[1:]:
        print(f"### {name}\n")
        print(globals()[name]())
        print()
