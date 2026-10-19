#!/usr/bin/env python3
"""Write 59_round11_results.md and 59_upload_index.md from the CSVs in superspreader/."""
from collections import Counter
from report_tables import OUT, ci, fmt, num, pct, rows, table

W1 = "world1_multiplier_only"
W2A = "world2a_scene_L30_sh0.70"
W2B = "world2b_scene_L10_sh0.58"
W3 = "world3_events_only"
W2_R10 = "world2_round10_gate_L10_sh1"

NAMES = {
    W1: "world 1, multiplier only (shape 0.32)",
    W2A: "world 2a, strongest scene plus multiplier (lambda 30, shape 0.70)",
    W2B: "world 2b, moderate scene plus multiplier (lambda 10, shape 0.58)",
    W3: "world 3, closed-group events (group 30, rate 0.034; unmatched)",
    W2_R10: "round-10 gate cell comparator (lambda 10, shape 1.00)",
}

ALL_WORLDS = (W1, W2A, W2B, W3, W2_R10)
MAIN_WORLDS = (W1, W2A, W2B, W3)


def main():
    w = {r["cell"]: r for r in rows("59_r111_worlds.csv")}
    pr = {r["world"]: r for r in rows("59_r112_repeat_infections.csv")}
    comp_rows = rows("59_r113_cluster_composition.csv")

    out = []
    a = out.append

    def v(cell, key, d=3):
        return fmt(num(w[cell], key), d)

    a("# ACT-049 note 59: round 11, the worlds matched on the like-for-like estimator\n")
    a("19 October 2026. Reply to note 58 (and note 57). Review and the registered predictions: `59a_review_of_note58.md`. Code: `superspreader/study/run_round11.py`, `analyze_round11.py`, `report_round11.py`; binary `build_r10` (no C++ changes in round 11; T1 byte-identity verified in round 10). The location and agent files are not edited.\n")

    a("## Headline\n")
    a(f"1. **Worlds 1, 2a and 2b are matched on the negative-binomial likelihood estimator (`k_ml` {v(W1, 'k_ml')}, {v(W2A, 'k_ml')} and {v(W2B, 'k_ml')}, within 3% of each other and within 4.4% of the 0.35 target, with overlapping 90% intervals), and at matched likelihood k they also match the observed body of the offspring distribution.** Their observed zero shares are {pct(w[W1], 'share_0')}, {pct(w[W2A], 'share_0')} and {pct(w[W2B], 'share_0')} (within 0.04, 1.3 and 1.1 percentage points of the negative binomial at each arm's own likelihood k and mean: {pct(w[W1], 'nb_zero_at_k_ml_own_mean')}, {pct(w[W2A], 'nb_zero_at_k_ml_own_mean')}, {pct(w[W2B], 'nb_zero_at_k_ml_own_mean')}), and the observed shares of infectors causing 80% of infections are {pct(w[W1], 'share_of_index_cases_causing_80pct')}, {pct(w[W2A], 'share_of_index_cases_causing_80pct')} and {pct(w[W2B], 'share_of_index_cases_causing_80pct')} (negative binomial: {pct(w[W1], 'nb_80pct_at_k_ml_own_mean')}, {pct(w[W2A], 'nb_80pct_at_k_ml_own_mean')}, {pct(w[W2B], 'nb_80pct_at_k_ml_own_mean')}).")
    a(f"2. **All six registered predictions (a) to (f) in R11-1 hold.** Matching on the likelihood k rather than the moment k preserves every discriminator found in round 10 and sharpens two of them: the ratio of likelihood k to moment k cleanly separates the multiplier-only world ({v(W1, 'k_ml_over_k_mom', 3)}) from both scene-plus-multiplier worlds ({v(W2A, 'k_ml_over_k_mom', 3)} in world 2a and {v(W2B, 'k_ml_over_k_mom', 3)} in world 2b), and the far tail now separates them as well (largest offspring {w[W2A]['largest_offspring_max']} in world 2a and {w[W2B]['largest_offspring_max']} in world 2b, replicate mean {v(W2A, 'largest_offspring_mean_over_replicates', 3)} and {v(W2B, 'largest_offspring_mean_over_replicates', 3)}, against {w[W1]['largest_offspring_max']} and {v(W1, 'largest_offspring_mean_over_replicates', 3)} in world 1), because matching the body on likelihood k forces the scene worlds to carry a lower moment k ({v(W2A, 'k_mom')} and {v(W2B, 'k_mom')}).")
    a(f"3. **World 2b (moderate scene, lambda 10) reaches likelihood k {v(W2B, 'k_ml')} at multiplier shape 0.58.** It does not need a shape near or below 0.32 (world 1's shape), because the log-log slope of likelihood k against shape steepens below shape 1 (`59a` item 2). A moderate scene (`lambda = 10`, `tau = 1`) cuts the required squared coefficient of variation of the per-episode multiplier from 3.125 (shape 0.32) to 1.724 (shape 0.58), almost in half; the strongest scene (`lambda = 30`) cuts it to 1.429 (shape 0.70).")
    a(f"4. **World 3 (closed-group events) cannot be matched on likelihood k.** Across all event rates and group sizes run in rounds 6 and 10, the lowest likelihood k reached is {v(W3, 'k_ml')} (round 10, group size 30, rate 0.034; round 6 reached 1.80 at rate 0.08), more than three times the target, with an observed zero share of {pct(w[W3], 'share_0')}.")
    a(f"5. **R11-2 (whether the repeat-infection correlation comes from the persistent class) is settled by decomposing the correlation within and between class membership.** In world 2a (`lambda = 30`, shape 0.70), the overall Pearson correlation across {pr['world2a_w2_L30_sh0.70']['all_pairs']} repeat-infection pairs is {fmt(num(pr['world2a_w2_L30_sh0.70'], 'all_pearson'), 3)} ({fmt(num(pr['world2a_w2_L30_sh0.70'], 'all_pearson_low'), 3)} to {fmt(num(pr['world2a_w2_L30_sh0.70'], 'all_pearson_high'), 3)}; Spearman {fmt(num(pr['world2a_w2_L30_sh0.70'], 'all_spearman'), 3)}), against {fmt(num(pr[W1], 'all_pearson'), 3)} in world 1. Computed separately *within* class members ({pr['world2a_w2_L30_sh0.70']['class_pairs']} pairs) and *within* non-members ({pr['world2a_w2_L30_sh0.70']['others_pairs']} pairs), the Pearson correlation drops to **{fmt(num(pr['world2a_w2_L30_sh0.70'], 'class_pearson'), 3)}** and **{fmt(num(pr['world2a_w2_L30_sh0.70'], 'others_pearson'), 3)}**. The same decomposition on the round-10 gate cell (overall Pearson {fmt(num(pr[W2_R10], 'all_pearson'), 3)} across {pr[W2_R10]['all_pairs']} pairs) gives **{fmt(num(pr[W2_R10], 'class_pearson'), 3)}** within class members and **{fmt(num(pr[W2_R10], 'others_pearson'), 3)}** within non-members. Both within-group correlations sit below 0 and well below the registered 0.03 threshold: the positive repeat-infection correlation is carried entirely by persistent class membership, not by household, home-location or age persistence.")
    a(f"6. **R11-3 (cluster composition in contact-tracing terms) separates all three mechanism families.** In the ten largest clusters of each replicate, the share of offspring in the infector's own household is {pct(w[W1], 'top10_clusters_mean_same_household_share')} in world 1, {pct(w[W2A], 'top10_clusters_mean_same_household_share')} in world 2a ({pct(w[W2B], 'top10_clusters_mean_same_household_share')} in world 2b, {pct(w[W2_R10], 'top10_clusters_mean_same_household_share')} in the round-10 gate cell), and {pct(w[W3], 'top10_clusters_mean_same_household_share')} in world 3; the share in the cluster's single modal venue type is {pct(w[W1], 'top10_clusters_mean_same_venue_type_share')}, {pct(w[W2A], 'top10_clusters_mean_same_venue_type_share')} ({pct(w[W2B], 'top10_clusters_mean_same_venue_type_share')}, {pct(w[W2_R10], 'top10_clusters_mean_same_venue_type_share')}) and {pct(w[W3], 'top10_clusters_mean_same_venue_type_share')}.\n")

    a("## 1. Deviations and points on note 58\n")
    a("The pre-run review (`59a_review_of_note58.md`) was written before any round-11 arm was launched. Points and deviations:\n")
    a("- **D1. Starting shapes for worlds 2a and 2b landed inside the window on the first run (`59a` items 1 and 2).** For world 2a (`lambda = 30`), exact log-log interpolation between `(shape 1, k_ml 0.435)` and `(shape 0.5, k_ml 0.284)` gives shape `0.703` (note 58's `0.73` interpolates linearly in k); running `0.70` gave `k_ml = 0.355` (`+1.5%` vs `0.350`, `-0.6%` vs world 1's `0.357`). For world 2b (`lambda = 10`), accounting for the `1.49x` steepening of the log-log slope below shape 1 observed at `lambda = 30` gave starting shape `0.58` instead of the note's linear extrapolation `0.46`; running `0.58` gave `k_ml = 0.365` (`+4.4%` vs `0.350`, `+2.3%` vs world 1, with overlapping 90% intervals `0.354 to 0.377` against `0.346 to 0.368`). The realised log-log slope between shapes 1 and 0.58 at `lambda = 10` is `(ln 0.510 - ln 0.365) / (ln 1 - ln 0.58) = 0.613`, which is `1.32` times the slope between shapes 1 and 2 (`0.463`); had `0.46` been run, `k_ml` would have landed near `0.31`. Neither arm needed a second tuning round.")
    a("- **D2. World 1 is reused unchanged (`59a` item 3).** The round-10 arm `r10_w1_sh0.32` (`k_ml = 0.357`) is already matched; its tables are recomputed from the stored traces with the added columns.")
    a("- **D3. World 3 is not tuned (`59a` item 4).** Across all closed-group event arms run in rounds 6 and 10, the lowest likelihood k is `1.199` (round 10, group size 30, rate 0.034, factor 3000; round 6 reached `1.802` at group size 30, rate 0.08, and `2.10` to `2.47` at group size 100). As instructed, no new tuning was run and world 3 is reported as unable to be matched on likelihood k.")
    a("- **D4. R11-2 counterfactual run dropped per the flag rule and replaced by within-class correlation decomposition (`59a` item 5).** Note 58 specifies dropping R11-2 if redrawing class membership per infection needs more than a flag. Because `initHvi()` assigns class membership once on the host (`movementPolicies.h`) and sets persistent device arrays (`hviMult`, `hviMultWeekend`, `hviClass`), redrawing per episode requires cross-policy device writes from the infection kernel plus a rebuild and T1 check. Instead, using the per-agent class flag in `hvi.csv`, I compute the repeat-infection correlation separately within class members and within non-members for both world 2a and the round-10 gate cell. That tests the exact hypothesis of R11-2 without a code change.")
    a("- **D5. Number of infectors in the top 1% (`top1pct_infectors`).** As in round 10, the top 1% is taken per replicate (`max(1, round(0.01 * n_rep))`) and pooled across the 12 replicates, giving `135, 89, 98, 135` (and `96` in the round-10 gate cell). This is the exact denominator of the top-1% age and occupation shares and differs by at most 1 from `round(0.01 * index_cases)` due to per-replicate rounding.")
    a("- **D6. Calibration and binary.** Day-28 cumulative infections are within 3% of `6,211.25` in every arm (`+1.3%` in world 1, `+0.3%` in world 2a, `-0.2%` in world 2b, `-1.1%` in world 3, `-0.2%` in the round-10 gate cell). Binary `build_r10/panSim` is used throughout.\n")

    a("## 2. R11-1: the worlds matched on likelihood k (12 replicates, 4 weeks, same seeds)\n")
    head = [
        "world", "coefficient", "likelihood k (primary)", "moment k", "likelihood / moment k",
        "early R", "observed zero share", "NB zero (at k_ml, own mean)", "observed minus NB zero",
        "observed causing 80%", "NB causing 80% (at k_ml, own mean)", "day 28 vs 6,211"
    ]
    body = []
    for c in ALL_WORLDS:
        body.append([
            NAMES[c], fmt(num(w[c], "background_coefficient"), 3),
            ci(w[c], "k_ml"), ci(w[c], "k_mom"), fmt(num(w[c], "k_ml_over_k_mom"), 3),
            ci(w[c], "early_R"), pct(w[c], "share_0"), pct(w[c], "nb_zero_at_k_ml_own_mean"),
            f"{100 * num(w[c], 'observed_zero_minus_nb_zero_at_k_ml'):+.1f} pts",
            pct(w[c], "share_of_index_cases_causing_80pct"), pct(w[c], "nb_80pct_at_k_ml_own_mean"),
            pct({"v": w[c]["day28_vs_6211.25"]}, "v")
        ])
    a(table(head, body) + "\n")
    a("The real pattern is about 0.3 for k, about 59% of infectors with zero offspring and about 19% to 20% causing 80% of infections (at a negative-binomial mean of 1.4; at the slightly higher early R of worlds 2a and 2b, 1.64 and 1.55, a negative binomial with `k = 0.355` to `0.365` has a zero share of `54.1%` to `54.6%` and `21.5%` to `21.8%` causing 80%, and projected to mean 1.4 at `k_ml` gives `56.7%` and `56.2%` zero share and `21.3%` and `21.6%` causing 80%).\n")
    a("Three findings stand out in the main table:\n")
    a("1. **Matching on likelihood k aligns the observed body of the offspring distribution across worlds 1, 2a and 2b.** In round 10, matching on moment k left an 8.8-point gap in observed zero share between world 1 (56.6%) and the gate cell (47.8%). Matched on likelihood k (`0.357, 0.355, 0.365`), the observed zero shares are `56.6%, 52.8%, 53.5%` (the remaining 3 to 4 points come from the higher early R of the scene worlds, `1.64` and `1.55` vs `1.40`), and the observed shares causing 80% of infections agree to within 0.6 points (`21.5%, 21.1%, 21.7%`).")
    a("2. **In both scene worlds, the negative binomial at `k_ml` and the arm's own mean fits the observed zero share within 1.1 to 1.3 percentage points** (`52.8%` vs `54.1%` in world 2a; `53.5%` vs `54.6%` in world 2b) and fits the 80% share within 0.1 to 0.4 points (`21.1%` vs `21.5%`; `21.7%` vs `21.8%`). By contrast, the negative binomial evaluated at the *moment* k overpredicts the zero share by 8.4 points in world 2a (`61.2%`) and 7.0 points in world 2b (`60.6%`), because the moment estimator is pulled down by the far tail.")
    a("3. **The ratio `k_ml / k_mom` remains a sharp fingerprint at matched likelihood k**: `1.06` in world 1 against `1.50` in world 2a and `1.42` in world 2b (and `3.11` in world 3).\n")

    a("### Where transmission happens\n")
    head = ["world", "home", "school and work", "the four high-L types", "restaurant", "large venue", "church", "recreation", "household secondary attack rate"]
    body = []
    for c in ALL_WORLDS:
        body.append([
            NAMES[c], pct(w[c], "infections_share_home"), pct(w[c], "infections_share_school_and_work"),
            pct(w[c], "infections_share_high_L_types"), pct(w[c], "infections_share_restaurant"),
            pct(w[c], "infections_share_large_venue"), pct(w[c], "infections_share_church"),
            pct(w[c], "infections_share_recreation"), fmt(num(w[c], "household_secondary_attack_rate"), 3)
        ])
    a(table(head, body) + "\n")
    a("The spatial separation is even larger in world 2a than in round 10: only `6.0%` of infections happen at home (28.2 points below world 1's `34.2%`) and `91.2%` happen at the four high-L venue types. In world 2b (`lambda = 10`, shape 0.58), the venue shares (`14.1%` home, `77.9%` high-L) are nearly identical to the round-10 gate cell (`14.8%` home, `77.1%` high-L), because changing the per-episode multiplier shape from 1.00 to 0.58 changes the dispersion of episodes without changing where people spend time. The household secondary attack rate in world 1 (`0.00165`) is `4.00` times world 2a (`0.000412`) and `2.00` times world 2b (`0.000826`).\n")

    a("### Cluster size and composition\n")
    head = [
        "world", "largest offspring (max over replicates)", "largest offspring (mean over replicates)",
        "offspring p99", "offspring p99.9", "ten largest clusters: mean offspring",
        "distinct venues", "share in one venue-day"
    ]
    body = []
    for c in ALL_WORLDS:
        body.append([
            NAMES[c], w[c]["largest_offspring_max"], fmt(num(w[c], "largest_offspring_mean_over_replicates"), 3),
            fmt(num(w[c], "offspring_p99"), 3), fmt(num(w[c], "offspring_p999"), 3),
            fmt(num(w[c], "top10_clusters_mean_offspring"), 3), fmt(num(w[c], "top10_clusters_mean_distinct_venues"), 3),
            pct(w[c], "top10_clusters_mean_largest_venue_day_share")
        ])
    a(table(head, body) + "\n")
    a("The per-cluster rows are in `59_r111_clusters.csv`. Matching on likelihood k instead of moment k changes the cluster-size comparison in a way worth noting: because worlds 2a and 2b must reach `k_mom = 0.236` and `0.257` in order to match world 1's `k_ml = 0.357`, their largest clusters are now noticeably larger than world 1's (replicate-mean maximum `37.6` and `36.8` against `27.7`; overall maximum `88` in world 2a and `57` in world 2b against `54` in world 1; 99th percentile `16.8` and `15.3` against `12.1`). And cluster shape continues to separate the mechanisms cleanly: the ten largest clusters of worlds 2a and 2b span `9.22` and `9.40` distinct venues with only `14.7%` and `14.5%` of their infections in a single venue-day, against `6.20` venues and `19.8%` in world 1 and `2.08` venues and `91.1%` in world 3.\n")

    a("### Who the big infectors are\n")
    head = ["world", "top 1% infectors (n)", "mean age of the top 1% of infectors", "mean age of all infectors", "difference", "share of the top 1% in the class"]
    body = []
    for c in ALL_WORLDS:
        body.append([
            NAMES[c], w[c]["top1pct_infectors"],
            fmt(num(w[c], "top1pct_mean_age"), 4), fmt(num(w[c], "all_infectors_mean_age"), 4),
            f"{num(w[c], 'top1pct_mean_age') - num(w[c], 'all_infectors_mean_age'):+.2f}",
            pct(w[c], "top1pct_share_in_class") if w[c].get("top1pct_share_in_class") else "n/a"
        ])
    a(table(head, body) + "\n")
    a("With the sample sizes (`n = 135, 89, 98, 135, 96`) beside the proportions, sampling uncertainty can be read directly (for a share near 20% at `n = 135`, one standard error is `3.4` percentage points; at `n = 89` or `98`, a 0% cell has a 95% upper bound of `3.4%` or `3.1%`). Share of the top 1% of infectors against the share of all infectors, by agent type:\n")
    types = {
        1: "infant / toddler (type 1)",
        2: "kindergarten (type 2)",
        3: "elementary school (type 3)",
        4: "high school (type 4)",
        5: "university (type 5)",
        6: "full-time worker (type 6)",
        7: "afternoon-shift worker (type 7)",
        8: "stay at home (type 8)"
    }
    short_names = {
        W1: "world 1 (n=135)",
        W2A: "world 2a (n=89)",
        W2B: "world 2b (n=98)",
        W3: "world 3 (n=135)",
        W2_R10: "R10 gate (n=96)"
    }
    head = ["agent type"] + [f"{short_names[c]}: top 1% / all" for c in ALL_WORLDS]
    body = []
    for t, nm in types.items():
        cells = []
        for c in ALL_WORLDS:
            top = num(w[c], f"top1pct_share_agent_type{t}") or 0.0
            allv = num(w[c], f"all_infectors_share_agent_type{t}") or 0.0
            cells.append(f"{100 * top:.1f}% / {100 * allv:.1f}%")
        body.append([nm] + cells)
    a(table(head, body) + "\n")
    a("As registered in prediction (f), **the occupational contrast holds and its pupil cell in worlds 2a and 2b is 0.0% by construction.** Specifically, `initHvi()` restricts high-volume class eligibility to `--hviTypes 4,5,6,7,8` and `--hviMinAge 15`, so children in agent types 1, 2 and 3 (infants, kindergarten and elementary school) and 14-year-olds in type 4 can never be class members. Because `94.5%` of the top 1% in world 2a and `93.0%` in world 2b belong to the class, types 1 to 3 have `0.0%` in the top 1% of both scene worlds (and high-school pupils, type 4, are `2.2%` in world 2a and `1.0%` in world 2b). Conversely, among eligible adults, stay-at-home adults (type 8, which includes retirees and adults without a workplace schedule) have the most discretionary time slots to redirect to the high-L venues, so they rise to `58.4%` of the top 1% in world 2a (against `40.4%` of all infectors) and `57.1%` in world 2b (against `38.1%`). In world 1, where there is no class and every agent draws from the same gamma multiplier, elementary-school children are strongly over-represented (`21.5%` vs `9.8%`) and stay-at-home adults are under-represented (`9.6%` vs `24.1%`).\n")

    a("## 3. Repeat infections and R11-2: decomposing the correlation by class membership\n")
    head = [
        "world", "group", "pairs", "Pearson r (90% interval)", "Spearman",
        "mean offspring: 1st episode", "mean offspring: 2nd episode"
    ]
    body = []
    r1 = pr[W1]
    body.append([
        NAMES[W1], "all agents", r1["all_pairs"], ci(r1, "all_pearson"),
        fmt(num(r1, "all_spearman"), 3), fmt(num(r1, "all_mean_ep1"), 3), fmt(num(r1, "all_mean_ep2"), 3)
    ])
    for key, label in (("world2a_w2_L30_sh0.70", NAMES[W2A]), (W2_R10, NAMES[W2_R10])):
        rk = pr[key]
        for pref, gname in (("all", "all pairs (pooled)"), ("class", "within class members only"), ("others", "within non-members only")):
            body.append([
                label, gname, rk[f"{pref}_pairs"],
                f"{fmt(num(rk, f'{pref}_pearson'), 3)} ({fmt(num(rk, f'{pref}_pearson_low'), 3)} to {fmt(num(rk, f'{pref}_pearson_high'), 3)})",
                fmt(num(rk, f"{pref}_spearman"), 3),
                fmt(num(rk, f"{pref}_mean_ep1"), 3), fmt(num(rk, f"{pref}_mean_ep2"), 3)
            ])
    a(table(head, body) + "\n")
    a("16 weeks, 8 replicates (seeds 78001 to 78008), vaccination off, every episode logged (`59_r112_repeat_infections.csv`). Reference correlations from earlier rounds: `0.544` for the persistent biological trait (R6-2) and `0.041` for persistent mobility without a venue scene (R7-S5).\n")
    a("This table answers both R11-1 prediction (e) and R11-2:\n")
    a("1. **Prediction (e) is met on the point estimate.** Pooled across all repeat-infection pairs, world 2a has a Pearson correlation of `0.0711` (`0.0431` to `0.0985`; Spearman `0.0991`), above the `0.05` threshold (its 90% replicate bootstrap interval spans `0.05`), while world 1 sits at `-0.0122` (`-0.0267` to `-0.000444`), well below `0.02`. World 2a's overall correlation (`0.0711`) is slightly lower than the round-10 gate cell's (`0.104`) for two reasons: its per-episode gamma noise has higher variance (`1/0.70 = 1.43` vs `1/1.00 = 1.00`), and at `lambda = 30` class members are depleted faster (`1,959` of `3,459` repeat pairs, `56.6%`, are class members, with mean offspring falling from `3.16` on the first episode to `2.40` on the second).")
    a("2. **R11-2 is answered unequivocally: within class members and within non-members, the repeat-infection correlation is zero (slightly negative), matching world 1.** In world 2a, restricting to class members (`1,959` pairs) reduces Pearson r from `+0.0711` to **`-0.00628`** (`-0.0343` to `+0.0250`, Spearman `-0.00390`), and restricting to non-members (`1,500` pairs) reduces it to **`-0.0152`** (`-0.0473` to `+0.0113`, Spearman `-0.0356`). Both are well below the registered `0.03` threshold. The exact same collapse occurs in the round-10 gate cell (`lambda = 10`, shape 1): overall Pearson r is `+0.104`, but within class members (`2,295` pairs) it is **`-0.00715`** and within non-members (`2,990` pairs) it is **`-0.0214`**. Why is the pooled correlation positive when both subgroup correlations are slightly negative? Because class members average `3.16` and `2.40` offspring on their first and second episodes in world 2a (and `3.14` and `2.16` in the gate cell), whereas non-members average `0.80` and `0.64` (`0.85` and `0.66`). Mixing two internally uncorrelated subgroups whose means differ by a factor of four creates a purely between-group covariance. That proves the interpretation in note 57: the repeat-infection correlation in the scene worlds comes from persistent membership in the high-volume class, not from household size, home location, or age.\n")

    a("## 4. R11-3: contact-tracing composition of the ten largest clusters\n")
    # Also compute modal venue type breakdown across the 120 clusters of each arm
    by_arm = {c: [r for r in comp_rows if r["arm"] == c] for c in ALL_WORLDS}
    head = [
        "world", "clusters (10 x 12 reps)", "mean offspring", "same-household share",
        "modal venue-type share", "most frequent modal venue type (count / 120)",
        "distinct venue types", "distinct venues", "one venue-day share",
        "mean infectee age", "infectee age range (mean min to max)"
    ]
    body = []
    for c in ALL_WORLDS:
        cr = by_arm[c]
        modes = Counter(r["modal_venue_type_name"] for r in cr).most_common(3)
        mode_str = ", ".join(f"{m} ({n})" for m, n in modes)
        min_age = sum(float(r["infectee_age_min"]) for r in cr) / len(cr)
        max_age = sum(float(r["infectee_age_max"]) for r in cr) / len(cr)
        body.append([
            NAMES[c], str(len(cr)),
            fmt(num(w[c], "top10_clusters_mean_offspring"), 3),
            pct(w[c], "top10_clusters_mean_same_household_share"),
            pct(w[c], "top10_clusters_mean_same_venue_type_share"),
            mode_str,
            fmt(num(w[c], "top10_clusters_mean_distinct_venue_types"), 3),
            fmt(num(w[c], "top10_clusters_mean_distinct_venues"), 3),
            pct(w[c], "top10_clusters_mean_largest_venue_day_share"),
            fmt(num(w[c], "top10_clusters_mean_infectee_age_mean"), 3),
            f"{fmt(num(w[c], 'top10_clusters_mean_infectee_age_range'), 3)} yr ({min_age:.1f} to {max_age:.1f})"
        ])
    a(table(head, body) + "\n")
    a("All 600 per-cluster rows (120 per arm across the three round-10 worlds and the two new round-11 scene worlds) are in `59_r113_cluster_composition.csv`. Expressed in the quantities a contact-tracing investigation records for a recognized cluster, the three mechanism families look completely different:\n")
    a("1. **World 1 (multiplier only):** A large cluster (mean `17.3` secondary cases) is a mixed household-plus-routine-setting cluster. On average **`17.7%`** of the secondary cases live in the index case's own household (about 3 household members), and **`49.2%`** are infected in the cluster's modal venue type, which is spread across school (`27` of `120` clusters), long shop (`22`), hospital (`17`), classroom (`16`), short shop (`12`) and health centre (`11`), spanning `4.77` venue types and `6.20` distinct venues. Infectees average `35.5` years of age and span a `60.0`-year range (mean min `11.2` to mean max `71.2`).")
    a("2. **Worlds 2a and 2b (and the round-10 gate cell, scene plus multiplier):** A large cluster (`22.5` and `21.5` secondary cases in worlds 2a and 2b; `18.4` in the gate cell) is a multi-venue social-scene cluster with almost no household component. Only **`3.3%`** (world 2a) to **`6.5%`** (world 2b; `7.3%` gate cell) of secondary cases are in the index case's household. The modal venue type is almost always one of the four high-L social settings—`large_venue` (`46` and `48` of `120` clusters), `restaurant` (`41` and `38`), `recreation` (`26` and `27`), or `church` (`7` and `7`)—accounting for `41.9%` and `40.5%` of the cluster's cases, while the cluster as a whole spans `4.28` to `4.70` venue types and `9.22` to `9.40` distinct venues, with less than `15%` in any single venue-day. Infectees are older (mean `46.8` and `46.0` years) and span `67.2` and `66.1` years (`14.9` to `82.1` and `14.9` to `81.0`).")
    a("3. **World 3 (closed-group events):** A large cluster (`22.9` secondary cases) is a single-venue, single-day point-source outbreak. Only **`5.6%`** of secondary cases are in the index case's household, **`93.4%`** occur in a single venue type (`shop_long` in `102` of `120` clusters, `restaurant` in `14`), **`91.1%`** occur in a single venue on a single day, and the entire cluster spans only `1.99` venue types and `2.08` venues (the event venue plus one or two household transmissions).\n")

    a("## 5. Registered predictions scored\n")
    a("| Test | Registered prediction (note 58) | Observed result | Verdict |\n|---|---|---|---|")
    d_home_2a = 100 * (num(w[W1], "infections_share_home") - num(w[W2A], "infections_share_home"))
    d_home_2b = 100 * (num(w[W1], "infections_share_home") - num(w[W2B], "infections_share_home"))
    a(f"| R11-1 (a) | World 2a home share at least 10 points below world 1 (34.2%) | World 2a: {pct(w[W2A], 'infections_share_home')} vs world 1: {pct(w[W1], 'infections_share_home')}, difference **{d_home_2a:.1f} points** (world 2b: {pct(w[W2B], 'infections_share_home')}, difference **{d_home_2b:.1f} points**) | **met** |")
    a(f"| R11-1 (b) | Ten largest clusters of world 2a have at least 7 distinct venues and at most 25% of infections in one venue-day | **{v(W2A, 'top10_clusters_mean_distinct_venues', 3)}** distinct venues and **{pct(w[W2A], 'top10_clusters_mean_largest_venue_day_share')}** in one venue-day (world 2b: **{v(W2B, 'top10_clusters_mean_distinct_venues', 3)}** and **{pct(w[W2B], 'top10_clusters_mean_largest_venue_day_share')}**) | **met** |")
    a(f"| R11-1 (c) | `k_ml / k_mom` at most 1.1 in world 1 and at least 1.3 in worlds 2a and 2b | World 1: **{v(W1, 'k_ml_over_k_mom', 3)}** (<= 1.1); world 2a: **{v(W2A, 'k_ml_over_k_mom', 3)}** (>= 1.3); world 2b: **{v(W2B, 'k_ml_over_k_mom', 3)}** (>= 1.3) | **met** |")
    a(f"| R11-1 (d) | Observed zero share of worlds 2a and 2b at `k_ml ~ 0.35` within 4 points of the NB at the same k and mean | World 2a: {pct(w[W2A], 'share_0')} vs NB {pct(w[W2A], 'nb_zero_at_k_ml_own_mean')} (**{100 * num(w[W2A], 'observed_zero_minus_nb_zero_at_k_ml'):+.1f} points**); world 2b: {pct(w[W2B], 'share_0')} vs NB {pct(w[W2B], 'nb_zero_at_k_ml_own_mean')} (**{100 * num(w[W2B], 'observed_zero_minus_nb_zero_at_k_ml'):+.1f} points**) | **met** |")
    a(f"| R11-1 (e) | Repeat-infection correlation at least 0.05 in world 2a and at most 0.02 in world 1 | World 2a: **{fmt(num(pr['world2a_w2_L30_sh0.70'], 'all_pearson'), 3)}** (0.0431 to 0.0985; Spearman 0.0991); world 1: **{fmt(num(pr[W1], 'all_pearson'), 3)}** (-0.0267 to -0.000444) | **met** (90% interval of world 2a spans 0.05) |")
    a(f"| R11-1 (f) | Elementary-school over-representation (`21.5%` vs `9.8%`) and stay-at-home under-representation (`9.6%` vs `24.1%`) in world 1; pupil share in top 1% of world 2a stays at 0% (by construction) | World 1 unchanged; kindergarten + elementary share in top 1% is **0.0%** in both world 2a (`n=89`) and world 2b (`n=98`) by construction (`--hviMinAge 15`, `--hviTypes 4..8`); stay-at-home adults are **58.4%** vs **40.4%** in world 2a and **57.1%** vs **38.1%** in world 2b | **met** |")
    a(f"| R11-2 | Removing persistent class membership reduces repeat-infection correlation to at most 0.03 | Counterfactual run dropped per flag rule (D4); within-group decomposition gives **`-0.0063`** within class members and **`-0.0152`** within non-members in world 2a (and **`-0.0072`** and **`-0.0214`** in the round-10 gate cell), all below 0.03 | **met via within-group decomposition** |")
    a("")

    a("## 6. What the like-for-like match changes for the paper\n")
    a("1. **Both the moderate scene (`lambda = 10`) and the strongest scene (`lambda = 30`) reach the real pattern on the like-for-like likelihood estimator when paired with a sub-exponential multiplier (shapes 0.58 and 0.70).** Note 57's concern that the moderate scene might require a multiplier shape near 0.32 (leaving nothing for the scene to contribute) does not materialize: because `k_ml` steepens below shape 1, shape `0.58` suffices at `lambda = 10` (`k_ml = 0.365`, zero share `53.5%`, 80% share `21.7%`), and shape `0.70` suffices at `lambda = 30` (`k_ml = 0.355`, zero share `52.8%`, 80% share `21.1%`). The moderate scene cuts the required multiplier variance `1/shape` from `3.125` (world 1, shape 0.32) to `1.724` (shape 0.58), and the strongest scene cuts it to `1.429` (shape 0.70).")
    a("2. **Every qualitative discriminator from round 10 survives when the worlds are matched on likelihood k and the observed body shares:** home share (`34.2%` vs `6.0%` and `14.1%`), high-L venue share (`16.7%` vs `91.2%` and `77.9%`), household secondary attack rate (`2x` to `4x` higher in world 1), ratio of likelihood to moment k (`1.06` vs `1.50` and `1.42`), repeat-infection correlation (`-0.012` vs `+0.071`), and the contact-tracing structure of large clusters (household share `17.7%` vs `3.3%–6.5%` vs `5.6%`; single venue-day share `19.8%` vs `14.5%–14.7%` vs `91.1%`).")
    a("3. **The repeat-infection fingerprint is now explained, not just observed.** Conditioning on the agent's class flag zeroes out the repeat-infection correlation in both world 2a and the round-10 gate cell (`r = -0.006` to `-0.021`), proving that the correlation is a between-group mixture effect of the persistent behavioural class rather than a byproduct of household size or geography.\n")

    a("## Files\n")
    a("`59_round11_results.md` (this note), `59a_review_of_note58.md`, `59_r111_worlds.csv`, `59_r111_worlds_offspring.csv`, `59_r111_clusters.csv`, `59_r112_repeat_infections.csv`, `59_r113_cluster_composition.csv`, `59_upload_index.md`. No file exceeds 1 MB.")

    text = "\n".join(out) + "\n"
    (OUT / "59_round11_results.md").write_text(text, newline="\n")
    print("59_round11_results.md:", len(text.encode("utf-8")), "bytes")

    idx_files = [
        ("59_round11_results.md", "main note: headline, deviations, R11-1 worlds matched on likelihood k, R11-2 within-class repeat-infection decomposition, R11-3 cluster composition, predictions scored"),
        ("59a_review_of_note58.md", "pre-run review of note 58 and starting-shape derivations, written before the round-11 arms were run"),
        ("59_r111_worlds.csv", "the round-11 worlds (worlds 1, 2a, 2b, 3 plus the round-10 gate comparator): likelihood and moment k with 90% intervals, observed and NB zero/80% shares at own mean and mean 1.4, venue shares, cluster and top-1% statistics"),
        ("59_r111_worlds_offspring.csv", "pooled offspring histograms of the worlds in 59_r111_worlds.csv"),
        ("59_r111_clusters.csv", "the ten largest clusters of each replicate in each world: offspring, distinct venues, share in one venue-day (600 rows)"),
        ("59_r112_repeat_infections.csv", "repeat-infection correlations (16 weeks, 8 replicates) for world 1, world 2a and the round-10 gate cell, decomposed into all pairs, within-class pairs and within-others pairs"),
        ("59_r113_cluster_composition.csv", "R11-3 contact-tracing composition of the ten largest clusters per replicate across all five arms: same-household share, modal venue type and share, distinct venue types, infectee age min/max/mean/range (600 rows)"),
    ]
    idx = [
        "# 59 upload index (round 11)\n",
        "19 October 2026. Every file is in `superspreader/` with Unix newlines (`\\n`) and under 1 MB.\n",
        "| File | Bytes (local) | Content |",
        "|---|---|---|",
    ]
    for fn, desc in idx_files:
        sz = (OUT / fn).stat().st_size
        idx.append(f"| {fn} | {sz} | {desc} |")
    idx.append("\nNotes:\n")
    idx.append("1. Not uploaded to root: run directories, traces, episode logs and HVI dumps (stored in `superspreader/study/results/round11/`), and the study scripts (`superspreader/study/run_round11.py`, `analyze_round11.py`, `report_round11.py`).")
    idx.append("2. Still outstanding from earlier rounds on Drive: `47_s1_summary_BAD_upload_ignore.csv` and `50_r80_hours_by_type_BAD_upload_ignore.csv` are superseded duplicates.")
    idx_text = "\n".join(idx) + "\n"
    (OUT / "59_upload_index.md").write_text(idx_text, newline="\n")
    print("59_upload_index.md:", len(idx_text.encode("utf-8")), "bytes")


if __name__ == "__main__":
    main()
