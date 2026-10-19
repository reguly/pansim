#!/usr/bin/env python3
"""Write 50_round8_results.md from the CSVs in superspreader/ (tables) plus the fixed prose below."""
import csv

from report_tables import OUT, ci, fmt, num, pct, rows, table


def pick(name, key, value, group=None):
    return next(r for r in rows(name) if r[key] == value and (group is None or r["group"] == group))


def main():
    s8 = {r["cell"]: r for r in rows("50_s8_summary.csv")}
    s85 = rows("50_s85_summary.csv")
    pred = rows("50_r80_predictions.csv")
    hours = rows("50_r80_hours_by_type.csv")
    out = []
    w = out.append

    w("# ACT-049 note 50: round 8, risk per hour, tilted mobility and isolation breaking\n")
    w("18 October 2026. Reply to note 49. Review before running: `50a_review_of_note49.md` (errors in note 49 and the predictions registered before any infection run). Code: `superspreader/study/run_round8.py`, `analyze_round8.py`, `report_round8.py`, `build_r8_inputs.py`, `t1_round8.py`; movement-policy changes in `include/policies/movementPolicies.h` (uncommitted); binary `build_r8`. The location and agent files are not edited; the L-modified location files are new copies.\n")

    w("## Headline\n")
    w("1. **Venue heterogeneity alone does make transmission more dispersed, but not enough.** With L multiplied by 10 on types 5, 6, 9, 10 for everybody (S8-1), moment k is 2.94 (baseline 4.59); at 30 it is 2.09. With a tilted class (S8-2) or an exclusive scene (S8-3) k falls to 0.85 (moment) and 0.79 (likelihood). Four arms are below 1 on the moment estimator (0.85 to 0.996): S8-2 tau 0.5 and tau 1 at lambda 30, S8-3 at lambda 10 and 30. **The smallest k is 0.85 on the moment estimator (S8-3 lambda 10, S8-2 tau 1 lambda 30) and 0.69 on the likelihood estimator (S8-3 lambda 30). No arm gets near the real value of about 0.3.**")
    w("2. **What this reproduces and what it does not.** Moment k of 0.85 to 1.0 is about three times the real 0.3. The zero share does not follow: at most 40.4% (S8-3 lambda 30) against about 59% observed, and the share of infectors causing 80% of infections is at best 30.7% against about 20%. In the two S8-3 arms the class (5% of eligible agents) causes 81% to 90% of infections and is 39% to 52% of all infected people, so the epidemic is carried by the class, and the early R of the arms rises to 1.76 to 2.03 against 1.4 in the baseline.")
    w("3. **The weight predictor of R8-0 was wrong in direction.** It predicted k above the observed value in 13 of 16 arms (the registered rule, observed k at least the predicted k and at most 1.5 times it plus 0.5, held in 3: S8-3 lambda 10 and 30, S8-4 f = 20% lambda 1). A likely reason, not tested here: at L = 10 or 30 a venue hour is a burst, so one infector at a high-L venue infects many people in the same venue-time, a dispersion that a weight per hour does not see. The observed class offspring ratio is 4.4 to 167 (S8-2 and S8-3), against predicted 2.3 to 15.")
    w("4. **Isolation breaking (S8-4) does nothing in this model.** At L = 1 k is 4.36 (5% class) and 4.65 (20% class) against 4.59 at baseline (changes -5% and +1%); at lambda 10 it is 2.97 and 2.87 against 2.94 without any class (S8-1).")
    w("5. **Control (S8-5).** In the S8-2 tau 1 lambda 30 arm capping the 5% most active averts 11.0 infections per 1,000 discretionary hours removed against 1.68 for the same hours removed from everybody: a factor 6.6 (90% interval 6.2 to 7.0), against the predicted at least 2 (met). Closing the high-L types is far stronger in total (day-84 infections fall to 7.9% of no control against 29.6% for the cap) at 43% of discretionary hours. In the S8-3 arm the scale-all intervention is degenerate (deviation D2), so the comparison is not usable there.\n")

    w("## 1. Deviations from note 49 (first), and errors in it\n")
    w("Errors in note 49 are in `50a` items 1 to 10; the main ones are: L multiplies the infection ratio of everyone present, so the class is coupled at the high-L venues (item 1); the proposed high-L set already holds 53.5% of the others' discretionary hours (item 3); tau, the skip rule and the S8-4 comparison are ambiguous (items 4, 7, 8). Deviations from the instructions:\n")
    w("- **D1. Skip rule.** The gate arms (S8-1 and S8-2 at lambda 10, S8-4) were run although the R8-0 prediction was above 3 (reading in `50a` item 7). When S8-2 at lambda 10 gave k = 1.13 (below 2), the stop rule asked for the complete grids, so every arm was then run: S8-1 at lambda 3 and 30, S8-2 at lambda 3 and 30 for both tau. All arms have 12 replicates (not 8), a common seed set 77001 to 77012, a pilot on the first 4 seeds, and day 28 within 3% of 6,211.25 (largest deviation +2.4%, S8-2 tau 0.5 lambda 30). The infection coefficient is recalibrated per arm and falls from 0.00041 to 0.00031, 0.00017 and 0.000071 for L = 3, 10, 30 (S8-1)")
    w("- **D2. S8-3 implementation quirk.** In the window chance calculation the scene of S8-3 (others' high-L chances multiplied by 0.2, difference to home) replaces the multiplier of the class mode instead of composing with it. Consequences: (a) non-class agents do not carry the 0.895 factor that preserved mean hours in the round-7 S2 cell, so their hours are those of the baseline minus the scene (discretionary hours per day 2.13 against 3.76 at baseline and 3.40 in S2); (b) in S8-5 the scale-all intervention acts on the class only, which made it identical in effect to the cap in the S8-3 arm (day-84 infections 9,079.5 against 9,079.3, hours removed 10.1% in both). I report that cell as degenerate and ran S8-5 additionally on the S8-2 tau 1 lambda 30 arm (second lowest k, 0.849 against 0.846 on the moment estimator), where scale-all is valid. A fix needs a rebuild and rerunning the S8-3 arms; the S8-3 k values are not expected to change by more than the noise (others' hours differ by a tenth).")
    w("- **D3. Hours.** S8-1 and S8-4 keep baseline hours. S8-2 keeps class and others' hours (tilt at fixed duration, `50a` item 4). S8-3 does not (note 49, others' hours move to home): total discretionary hours per agent fall by 30% (3.50 to 2.45 per day).")
    w("- **D4. S8-4 class.** The class has no hours multiplier (F = 1); `class share of discretionary hours` is then its population share. The comparison with S8-2 is read as in `50a` item 8.")
    w("- **D5. S8-5 hours.** As in round 7, hours removed are estimated on 5-week movement-only runs and scaled to the 12-week runs (63 days of control); the scale-all parameter matches the cap within 3% (S8-2 cell: 7.29% against 7.43%). Closure comes in one step (types 5, 6, 9, 10), so it is not at equal hours; per-hour figures are reported.")
    w("- **D6. S8-6 skipped.** It needs more than a flag change: the combination of `--hviMode` and `--sheddingShape` is blocked by a check in `initializeArgs` (one line, `50a` item 9) and a rebuild. I did not do it; say if you want it (about 30 minutes).")
    w("- **D7. Predictor.** R8-0 item 3 used per-agent weights (productivity per hour by venue type derived from baseline infection shares, `50a` item 6), not 'a + 3.7 b'. Registered before running.")
    w("- **D8. Binaries and state.** `build_r8` for everything in this round. T1 passed: with every option off a 12-week run on `build_r8` gives a daily table and an infection trace byte-identical to `build_r7b` (81,610 trace lines; stdout differs only in the timing profile). All code is uncommitted.\n")

    w("## 2. R8-0: hours by venue type and predictions\n")
    head = ["movement", "group", "agents", "disc. hours per day", "share at types 5, 6, 9, 10", "all-role hours at types 5, 6, 9, 10", "of which non-discretionary role", "home hours"]
    body = []
    labels = {"base": "baseline", "f3_t0": "S2 cell (class f = 5%, F = 3), untilted", "f3_t0.5": "tilt tau 0.5", "f3_t1": "tilt tau 1", "f3_t1_o0.2": "tau 1 and others' high-L chances x 0.2 (S8-3)"}
    for r in hours:
        if r["movement_variant"] in labels and r["group"] in ("class", "others_eligible", "all_others"):
            if r["movement_variant"] == "base" and r["group"] != "others_eligible":
                continue
            body.append([labels[r["movement_variant"]], r["group"].replace("_", " "), r["agents"], fmt(float(r["disc_role_hours_total"]), 3), pct({"v": r["disc_role_share_at_high_types"]}, "v"),
                         fmt(float(r["all_hours_at_high_types"]), 3), fmt(float(r["all_hours_at_high_types_nondisc_role"]), 2), fmt(float(r["all_hours_home_type2"]), 3)])
    w(table(head, body) + "\n")
    w("Share of discretionary hours at the proposed high-L set (types 5, 6, 9, 10) for others: 53.8% (baseline, eligible) and 53.5% (S2 cell); for the class: 59.1% untilted, 80.6% (tau 0.5), 99.96% (tau 1). Hours at those types in a work or school role are only 0.05 per day.\n")
    head = ["arm", "lambda", "exposure factor", "class to others ratio r (predicted)", "CV^2 of weights", "predicted k", "acceptance range for observed k", "observed k (moment)", "within range"]
    body = []
    for r in pred:
        a = r["arm"]
        if a.startswith("check"):
            continue
        o = s8.get(a)
        body.append([a, r["lambda"], fmt(float(r["exposure_factor_vs_L1"]), 3), fmt(float(r["class_to_others_offspring_ratio_r"]), 3) if r.get("class_to_others_offspring_ratio_r") else "n/a",
                     fmt(float(r["cv2_of_weights"]), 3), fmt(float(r["predicted_k"]), 3), f"{fmt(float(r['acceptance_low']), 3)} to {fmt(float(r['acceptance_high']), 3)}",
                     fmt(num(o, "k_mom"), 3) if o else "not run", ("yes" if o and o["observed_k_in_acceptance_range"] == "1" else "no") if o else "n/a"])
    w(table(head, body) + "\n")
    w("Out-of-sample check of the predictor at L = 1 (S2 cell): predicted class ratio 1.40 and k 4.44, observed 1.55 and 4.25 (round 7).\n")

    w("## 3. Predictions scored\n")
    w("| Test | Prediction | Result | Verdict |\n|---|---|---|---|")
    k = lambda a: float(s8[a]["k_mom"])
    w(f"| S8-1 | k stays above 2.5 | {fmt(k('s8_1_L3'), 3)} (lambda 3), {fmt(k('s8_1_L10'), 3)} (10), {fmt(k('s8_1_L30'), 3)} (30); likelihood {fmt(float(s8['s8_1_L30']['k_ml']), 3)} at 30 | met at lambda 3 and 10, **failed at lambda 30** |")
    w("| S8-1 | the coefficient (R) falls on recalibration | coefficient 0.00041 to 0.00031, 0.00017, 0.000071; early R among index cases rises from 1.41 to 1.44, 1.48, 1.52 | met |")
    w(f"| S8-2 | registered rule from R8-0 (k at least the predicted, at most 1.5 times plus 0.5) | observed below predicted in all six cells: tau 0.5: {fmt(k('s8_2_t0.5_L3'), 3)}, {fmt(k('s8_2_t0.5_L10'), 3)}, {fmt(k('s8_2_t0.5_L30'), 3)} against 4.80, 2.81, 1.75; tau 1: {fmt(k('s8_2_t1_L3'), 3)}, {fmt(k('s8_2_t1_L10'), 3)}, {fmt(k('s8_2_t1_L30'), 3)} against 4.06, 1.97, 1.21 | **failed** (predictor overstates k) |")
    w(f"| S8-3 | the only arm that can reach k below 1 | S8-3 lambda 10: {fmt(k('s8_3_L10'), 3)}, lambda 30: {fmt(k('s8_3_L30'), 3)}; but also S8-2 tau 1 lambda 30 {fmt(k('s8_2_t1_L30'), 3)} and tau 0.5 lambda 30 {fmt(k('s8_2_t0.5_L30'), 3)} | S8-3 reaches below 1 (met); \"the only arm\" **failed** |")
    w(f"| S8-3 | lambda about 14 gives r = 12 | observed r {fmt(float(s8['s8_3_L3']['class_offspring_ratio_r_observed']), 3)} already at lambda 3, {fmt(float(s8['s8_3_L10']['class_offspring_ratio_r_observed']), 3)} at 10 (predicted by weights 3.4 and 8.1) | **failed** (r far larger than the weights give) |")
    w(f"| S8-4 | lambda 1 changes k by less than 10% | {fmt(k('s8_4_f5_L1'), 3)} and {fmt(k('s8_4_f20_L1'), 3)} against 4.59 (-4.9% and +1.2%) | met |")
    w(f"| S8-4 | lambda 10 is below S8-2 tau 1 at the same lambda (read as k above) | {fmt(k('s8_4_f5_L10'), 3)} and {fmt(k('s8_4_f20_L10'), 3)} against {fmt(k('s8_2_t1_L10'), 3)} | met under the reading of `50a` item 8 |")
    c = {(r["base"], r["intervention"]): r for r in s85}
    cs = c[("s8_2_t1_L30", "capTop")]
    w(f"| S8-5 | the cap beats scale-all by a factor of at least 2 in the arm with the lowest k | S8-2 tau 1 lambda 30: {fmt(num(cs, 'cap_over_scaleall_per_disc_hour'), 3)} ({fmt(num(cs, 'cap_over_scaleall_low'), 3)} to {fmt(num(cs, 'cap_over_scaleall_high'), 3)}); S8-3 lambda 10 (lowest moment k): {fmt(num(c[('s8_3_L10', 'capTop')], 'cap_over_scaleall_per_disc_hour'), 3)} (degenerate, D2) | **met** in the valid cell; not testable in S8-3 |")
    w("| S8-6 | combination with shedding at most 25% below shedding alone | not run | skipped (D6) |")
    w("")

    w("## 4. Arms: results (12 replicates, 4 weeks, day 28 matched to 6,211.25)\n")
    head = ["arm", "day 28 vs 6,211", "coefficient", "early R", "k moment", "k likelihood", "zero", "NB zero (moment)", "NB zero (likelihood)", "causing 80%", "causing 50%", "mean unscaled multiplier of index cases",
            "class share of infections caused", "class share of discretionary hours", "class share of high-L hours", "class share of index cases", "class ratio r (observed)", "predicted k"]
    body = []
    for a, r in s8.items():
        cls = r.get("class_share_of_infections_caused")
        body.append([a, pct({"v": r["day28_vs_6211.25"]}, "v"), fmt(float(r["background_coefficient"]), 3), ci(r, "early_R"), ci(r, "k_mom"), ci(r, "k_ml"), pct(r, "share_0"), pct(r, "nb_mom_share_0"),
                     pct(r, "nb_ml_share_0"), pct(r, "share_of_index_cases_causing_80pct"), pct(r, "share_of_index_cases_causing_50pct"), ci(r, "mean_m_index_cases"),
                     pct({"v": cls}, "v") if cls and float(r["class_share_of_population"]) > 0 else "n/a",
                     pct({"v": r["class_share_of_discretionary_hours"]}, "v") if r.get("class_share_of_discretionary_hours") else "n/a",
                     pct({"v": r["class_share_of_high_L_hours"]}, "v") if r.get("class_share_of_high_L_hours") else "n/a",
                     pct({"v": r["class_share_of_index_cases"]}, "v") if float(r["class_share_of_population"]) > 0 else "n/a",
                     fmt(float(r["class_offspring_ratio_r_observed"]), 3) if r.get("class_offspring_ratio_r_observed") else "n/a",
                     fmt(float(r["predicted_k"]), 3) if r.get("predicted_k") else "n/a"])
    w(table(head, body) + "\n")
    w("Share above 5 offspring, share with at least 20 and the shares of infections by location type are in `50_s8_summary.csv`; the offspring histograms are in `50_s8_offspring.csv`. Public space has L = 0 and carries no infection in any arm. Class share of the population is 5% (S8-2, S8-3, S8-4 f = 5%) and 20% (S8-4 f = 20%).\n")

    w("## 5. Summary row\n")
    best = min(s8.values(), key=lambda r: float(r["k_mom"]))
    best_ml = min(s8.values(), key=lambda r: float(r["k_ml"]))
    t1 = s8["s8_2_t1_L30"]
    s3 = s8["s8_3_L10"]
    w(table(["criterion", "arm", "k moment", "k likelihood", "zero share", "causing 80%", "class high-L hours per day", "others' high-L hours per day", "ratio of high-L hours, class to others", "lambda"],
            [["smallest moment k", "s8_3_L10", fmt(float(s3["k_mom"]), 3), fmt(float(s3["k_ml"]), 3), pct(s3, "share_0"), pct(s3, "share_of_index_cases_causing_80pct"), fmt(float(s3["class_high_L_hours_per_day"]), 3),
              fmt(float(s3["others_high_L_hours_per_day"]), 3), fmt(float(s3["class_high_L_hours_per_day"]) / float(s3["others_high_L_hours_per_day"]), 3), "10"],
             ["same, second arm (0.849)", "s8_2_t1_L30", fmt(float(t1["k_mom"]), 3), fmt(float(t1["k_ml"]), 3), pct(t1, "share_0"), pct(t1, "share_of_index_cases_causing_80pct"), fmt(float(t1["class_high_L_hours_per_day"]), 3),
              fmt(float(t1["others_high_L_hours_per_day"]), 3), fmt(float(t1["class_high_L_hours_per_day"]) / float(t1["others_high_L_hours_per_day"]), 3), "30"],
             ["smallest likelihood k", best_ml["cell"], fmt(float(best_ml["k_mom"]), 3), fmt(float(best_ml["k_ml"]), 3), pct(best_ml, "share_0"), pct(best_ml, "share_of_index_cases_causing_80pct"),
              fmt(float(best_ml["class_high_L_hours_per_day"]), 3), fmt(float(best_ml["others_high_L_hours_per_day"]), 3),
              fmt(float(best_ml["class_high_L_hours_per_day"]) / float(best_ml["others_high_L_hours_per_day"]), 3), "30"]]) + "\n")
    w("The ratio of high-L hours needed for k near 0.85 is between 7 and 28 together with a lambda of 10 to 30, that is a class that spends 11 hours a day at venues with L 10 to 30 times larger while everyone else spends 0.4 to 1.6 hours. The baseline ratio (untilted class) is 3.2; the others' share of high-L hours is the binding constraint (S8-2 at lambda 30 reaches only 0.85 although the ratio is 6.7, S8-3 at lambda 10 reaches the same with a ratio of 28).\n")

    w("## 6. S8-5: policy contrast (`50_s85_summary.csv`; 12 replicates, 12 weeks, same seeds in every arm, control from day 21)\n")
    head = ["base", "intervention", "discretionary hours removed", "high-L hours removed", "infections at day 84, none", "infections at day 84", "ratio to none (90% interval)",
            "averted per 1,000 discretionary hours (90% interval)", "averted per 1,000 high-L hours (90% interval)", "cap over scale-all per hour (90% interval)"]
    body = []
    for r in s85:
        iv = lambda v, lo, hi: f"{fmt(float(r[v]), 3)} ({fmt(float(r[lo]), 3)} to {fmt(float(r[hi]), 3)})"
        body.append([r["base"], r["intervention"], f"{100 * float(r['disc_hours_removed_fraction']):.2f}%", f"{100 * float(r['high_L_hours_removed_fraction']):.2f}%",
                     fmt(float(r["infections_day84_none"]), 5), fmt(float(r["infections_day84"]), 5), iv("ratio_to_none", "ratio_low", "ratio_high"),
                     iv("averted_per_1000_disc_hours", "averted_per_1000_disc_hours_low", "averted_per_1000_disc_hours_high"),
                     iv("averted_per_1000_high_L_hours", "averted_per_1000_high_L_hours_low", "averted_per_1000_high_L_hours_high"),
                     iv("cap_over_scaleall_per_disc_hour", "cap_over_scaleall_low", "cap_over_scaleall_high") if r["intervention"] == "capTop" else ""])
    w(table(head, body) + "\n")
    w("In the S8-2 tau 1 lambda 30 arm the cap removes 7.4% of discretionary hours but 14.3% of the high-L hours, and cuts day-84 infections to 29.6%; the same discretionary hours removed from everybody (scale-all, 0.9163) removes 7.2% of high-L hours and cuts infections only to 89.5%. Closing the high-L types removes 97.6% of high-L hours and 43.4% of discretionary hours, and cuts infections to 7.9%, but per hour removed it is less efficient than the cap (2.5 against 11.0 per 1,000 discretionary hours). In S8-3 lambda 10 scale-all is degenerate (D2): cap and scale-all are the same intervention. The two capped arms give the same day-84 mean to 0.002%; this is a coincidence of the replicate means, the replicates differ individually by up to 5%.\n")

    w("## 7. In plain terms\n")
    w("1. **What a high-risk scene can do.** If a 5% minority spends 11 hours a day at venues that are 10 to 30 times riskier per hour and, in S8-3, everybody else is largely kept away from them, transmission becomes concentrated enough to give moment k of 0.85 to 1.0 and a class that causes 80% to 90% of infections. That is the superspreading mechanism of the note, and it works only with an extreme contrast, and in this model the class is also infected at a high rate (44% of infections received in S8-3 at lambda 10, 26% in S8-2 tau 1 at lambda 30), because L acts on exposure as well.")
    w("2. **What it does not do.** It does not get k to 0.3, the zero share to about 59%, or the share of infectors causing 80% to about 20%. I did not decompose the zero share; in the best arms the class is 39% to 52% of all infected people, so the distribution over all infected people mixes a heavy class with an ordinary remainder. Round 8 therefore leaves the per-person or per-episode trait route (rounds 5 and 6) as the only one in this model that reaches real k.")
    w("3. **Isolation breaking and venue heterogeneity for everyone.** Isolation breaking has no measurable effect. L = 10 for all agents, with no class at all, takes k from 4.59 to 2.94; at 30, 2.09. Venue heterogeneity is a real source of dispersion, an order of magnitude weaker than needed.")
    w("4. **Control.** When transmission is concentrated, targeting the most active reduces infections 6.6 times more per hour than uniform reduction, as note 49 predicted, and closing the risky venue types is the strongest single measure. The round-7 result (1.26 times, overlapping intervals) is consistent with being the low-contrast end of the same comparison.\n")

    w("## 8. Open points\n")
    w("1. S8-3: fix the quirk in D2 (compose the scene with the class multiplier) if the S8-3 values or the S8-5 cell on S8-3 are to be used in the paper. I expect k to be unchanged within noise.")
    w("2. S8-6 (combination with a per-episode multiplier) was not run (D6).")
    w("3. The registered predictor (weights per hour) fails in direction at high L: observed k is below predicted. A prediction that works at high L would have to model the burst at a venue (an infector in a room with L = 30 infects several people at once); that is a different calculation from per-hour weights.")
    w("4. The reading of the S8-4 comparison (`50a` item 8) and of tau (`50a` item 4) should be confirmed.\n")

    w("## Files\n")
    w("`50_round8_results.md` (this note), `50a_review_of_note49.md`, `50_r80_hours_by_type.csv`, `50_r80_predictions.csv`, `50_r80_productivity.csv`, `50_s8_summary.csv`, `50_s8_offspring.csv`, `50_s85_summary.csv`, `50_upload_index.md`. No file exceeds 1 MB.")
    text = "\n".join(out) + "\n"
    (OUT / "50_round8_results.md").write_text(text, newline="\n")
    print(len(text), "characters")


if __name__ == "__main__":
    main()
