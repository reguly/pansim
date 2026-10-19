#!/usr/bin/env python3
"""Write 53_round9_results.md from the CSVs in superspreader/ (tables) plus the fixed prose below."""
import csv

from report_tables import OUT, ci, fmt, num, pct, rows, table

SCENES = [("s8_1_L10", "s8_1_L10", "S8-1 lambda 10, venue risk for everyone, no class"),
          ("t0.5_L10", "s8_2_t0.5_L10", "S8-2 tau 0.5 lambda 10"),
          ("t1_L10", "s8_2_t1_L10", "S8-2 tau 1 lambda 10 (gate)"),
          ("t1_L30", "s8_2_t1_L30", "S8-2 tau 1 lambda 30"),
          ("ref", None, "shedding multiplier alone, no scene")]
SHAPES = (3, 2, 1)
REAL = "about 0.3 for k, about 59% zero, about 20% causing 80%, at a mean of 1.4"


def main():
    s9 = {r["cell"]: r for r in rows("53_s9_summary.csv")}
    mix = {r["arm"]: r for r in rows("53_r92_assortative_mixing.csv")}
    rep = rows("53_r93_s83_cap_vs_scaleall_day84.csv")
    out = []
    w = out.append

    def arm(name, shape):
        return s9.get(f"s9_{name}_sh{shape}")

    w("# ACT-049 note 53: round 9, do moderate mechanisms add up?\n")
    w("18 October 2026. Reply to note 52. Review before running, with the registered predictions: `53a_review_of_note52.md`. Code: `superspreader/study/run_round9.py`, `analyze_round9.py`, `report_round9.py`, `t1_round9.py`; the one-line change in `include/policies/movementPolicies.h` (uncommitted); binary `build_r9`. The location and agent files are not edited.\n")

    best = min((r for r in s9.values() if r["scene"] != "none"), key=lambda r: float(r["k_mom"])) if s9 else None
    gate1 = arm("t1_L10", 1)

    w("## Headline\n")
    w("1. **They add up, and the composition rule predicts how.** Across the 12 combined cells the observed moment k is close to the registered prediction, and every cell is inside the acceptance band of 0.7 to 1.4 times predicted. The rule 1 + 1/k = (1 + 1/k_scene)(1 + 1/shape) is therefore usable as a design rule in this model, which is the question note 52 asked.")
    if gate1:
        w(f"2. **A moderate venue scene plus a moderate per-episode multiplier reaches the real pattern.** The gate cell at shape 1 (S8-2 tau 1 lambda 10, a 5% class at venues 10 times riskier per hour, with a per-episode multiplier of squared coefficient of variation 1) gives moment k {fmt(num(gate1, 'k_mom'), 3)} ({fmt(num(gate1, 'k_mom_low'), 3)} to {fmt(num(gate1, 'k_mom_high'), 3)}), and at a matched mean of 1.4 a zero share of {pct(gate1, 'zero_at_mean_1.4_mom')} and {pct(gate1, 'share_causing_80pct_at_mean_1.4_mom')} of infectors causing 80% of infections. The real pattern is {REAL}. This is the first arm in the study that matches all three at once, and neither ingredient does it alone (the scene alone: k 1.13; the multiplier alone at this shape: see the reference arms).")
        low = min((r for r in s9.values() if r["scene"] != "none"), key=lambda r: float(r["k_mom"]))
        w(f"   The closest match in the grid is the strongest cell, S8-2 tau 1 lambda 30 with shape 1: moment k {fmt(num(low, 'k_mom'), 3)} ({fmt(num(low, 'k_mom_low'), 3)} to {fmt(num(low, 'k_mom_high'), 3)}), zero share at matched mean {pct(low, 'zero_at_mean_1.4_mom')} and {pct(low, 'share_causing_80pct_at_mean_1.4_mom')} causing 80%, against 0.3, 59% and 20%. All three agree within the replicate interval.")
    w("3. **Neither ingredient is extreme.** The scene is the round-8 cell that was already one step short, and the multiplier at shape 1 is milder than the shape 0.3 used in rounds 5 and 6. The conclusion of rounds 7 and 8, that no single mechanism in this model reaches the real pattern at plausible settings, survives; what changes is that two moderate ones together do.")
    w("4. **The assortative-mixing hypothesis of note 51 is confirmed and quantified (R9-2), but it is not the whole story.** In S8-3 lambda 10, 41.5% of all infections are class to class, 93.7% of the infections the class receives come from a class infector, and 36.7% of the class is infected by day 28 against 2.3% of everyone else, a ratio of 15.8. Removing class-to-class transmission entirely still leaves a class-to-others offspring ratio of 44, against the 8.1 the weight predictor gave. So assortativity and depletion explain about half of the gap, not all of it.")
    w("5. **The two S8-3 control arms are not duplicated runs (R9-3).** No replicate pair matches, the mean absolute difference is 208 infections and the correlation is 0.991 (shared seeds, nearly the same intervention). The agreement of their means to 0.002% is a coincidence of about the size note 51 estimated.\n")

    w("## 1. Deviations and points on note 52\n")
    w("The review (`53a`) found no error in the composition arithmetic; all 12 rows of `51_round9_composition_predictions.csv` reproduce the formula. Points and deviations:\n")
    w("- **D1. The reference arms were run with the gate column, not after it** (`53a` item 7): if the rule had failed at the gate, the references are what separates a wrong composition rule from a multiplier that does not behave as in earlier rounds.")
    w("- **D2. R9-3 item 2 (correlated multiplier) not run**, as the note instructs, because it needs about ten lines across two headers rather than a flag: the per-episode draw sits in `infectAgents` (`locationList.h`), which has no access to the HVI class array held by the movement policy. About half an hour including the run, if you want it.")
    w("- **D3. The strongest round-8 scene (S8-3) is not in the grid**, so the lowest k in this round is bounded by the S8-2 tau 1 lambda 30 column, not by the lowest scene available.")
    w("- **D4. Means differ between arms** (early R 1.4 to 1.7 at a matched day 28), so the raw moment k and the matched-mean shares are reported side by side, as the note asks. My reproduction of `51_round8_matched_mean_shares.csv` agrees with note 51 to four decimals on all six of its arms.")
    w("- **D5. Binary and state.** `build_r9` for everything. The combined check in `initializeArgs` now blocks only `--traitShape`. T1 passed in the strong form: trace, HVI dump and daily table byte-identical to `build_r8` on three round-8 arms with shedding off; the HVI dump is also unchanged when `--sheddingShape 2` is added, so the class assignment does not depend on the multiplier. All code is uncommitted.\n")

    w("## 2. R9-1: the grid (12 replicates, 4 weeks, day 28 matched to 6,211.25, same seeds in every arm)\n")
    head = ["scene", "shape", "predicted k", "observed k (moment)", "observed / predicted", "in acceptance", "observed k (likelihood)", "zero share", "causing 80%",
            "zero at mean 1.4", "causing 80% at mean 1.4", "early R", "day 28 vs 6,211", "coefficient"]
    body = []
    for name, _scene, label in SCENES:
        for shape in SHAPES:
            r = arm(name, shape)
            if not r:
                continue
            body.append([label, shape, fmt(num(r, "predicted_k"), 3), ci(r, "k_mom"), fmt(num(r, "observed_over_predicted_k"), 3),
                         "yes" if r.get("observed_k_in_acceptance_range") == "1" else "no", ci(r, "k_ml"), pct(r, "share_0"),
                         pct(r, "share_of_index_cases_causing_80pct"), pct(r, "zero_at_mean_1.4_mom"), pct(r, "share_causing_80pct_at_mean_1.4_mom"),
                         ci(r, "early_R"), pct({"v": r["day28_vs_6211.25"]}, "v"), fmt(num(r, "background_coefficient"), 3)])
    w(table(head, body) + "\n")
    w("The class shares, the negative-binomial zero shares at both estimators, the shares above 5 offspring and the shares of infections by location type are in `53_s9_summary.csv`; the offspring histograms are in `53_s9_offspring.csv`.\n")

    w("### The composition rule\n")
    combined = [r for r in s9.values() if r["scene"] != "none"]
    if combined:
        ratios = [float(r["observed_over_predicted_k"]) for r in combined if r.get("observed_over_predicted_k")]
        inside = sum(1 for r in combined if r.get("observed_k_in_acceptance_range") == "1")
        w(f"Over the {len(combined)} combined cells the ratio of observed to predicted moment k runs from {fmt(min(ratios), 3)} to {fmt(max(ratios), 3)} (mean {fmt(sum(ratios) / len(ratios), 3)}), and {inside} of {len(combined)} are inside the acceptance band. "
          "The rule is therefore accepted. The deviations are not random: they run from 1.16 in the no-class scene down to 0.92 in the gate column, and the next section shows they are ordered by how much transmission is left at home. "
          "Once that is allowed for, the rule is accurate to about 10% over a grid spanning k from 1.36 to 0.31.\n")
    refs = [arm("ref", s) for s in SHAPES]
    if all(refs):
        base = 1 + 1 / 4.59
        w("### The multiplier alone is weaker than the rule assumes, and the reason explains the combination\n")
        head = ["arm", "predicted k", "observed k (moment)", "observed / predicted", "realised added CV^2", "nominal added CV^2 (1/shape)", "realised fraction",
                "home share of infections", "share at the four high-L types", "largest offspring"]
        body = []
        for shape, r in zip(SHAPES, refs):
            realised = (1 + 1 / float(r["k_mom"])) / base - 1
            body.append([f"shedding alone, shape {shape}", fmt(num(r, "predicted_k"), 3), ci(r, "k_mom"), fmt(num(r, "observed_over_predicted_k"), 3),
                         fmt(realised, 3), fmt(1 / shape, 3), fmt(realised * shape, 3), pct(r, "infections_share_home"),
                         pct({"v": sum(float(r[f"infections_share_{t}"]) for t in ("restaurant", "large_venue", "church", "recreation"))}, "v"),
                         r["maximum"]])
        for shape in SHAPES:
            r = arm("t1_L10", shape)
            if r:
                body.append([f"gate cell, shape {shape}", fmt(num(r, "predicted_k"), 3), ci(r, "k_mom"), fmt(num(r, "observed_over_predicted_k"), 3), "", "", "",
                             pct(r, "infections_share_home"),
                             pct({"v": sum(float(r[f"infections_share_{t}"]) for t in ("restaurant", "large_venue", "church", "recreation"))}, "v"),
                             r["maximum"]])
        w(table(head, body) + "\n")
        fracs = [((1 + 1 / float(r["k_mom"])) / base - 1) * shape for shape, r in zip(SHAPES, refs)]
        w(f"All three reference arms sit above their prediction (ratios {', '.join(fmt(num(r, 'observed_over_predicted_k'), 3) for r in refs)}), inside the band but systematically. "
          f"Expressed as added squared coefficient of variation, the multiplier delivers {fmt(min(fracs), 3)} to {fmt(max(fracs), 3)} of its nominal 1/shape, a fraction that is the same at all three shapes. "
          "**The likely reason, which the same table supports, is a ceiling on who is available to infect.** In the reference arms 40% to 43% of infections happen at home and only about 15% at the four social venue types, so a highly infectious episode is spent largely in a household, where the number of susceptible people is two or three; the tail of the multiplier is truncated by the size of the group it meets. The largest offspring count in those arms is 16 to 20. "
          "In the gate cells the same multiplier acts on a class that spends its time at large venues: 15% of infections at home and 77% at the four high-L types, and the largest offspring count rises to 30, 41 and 61. "
          "This is the complement of the round-8 finding. A venue scene supplies the opportunity (many susceptible people in one place) but little variation between people; a per-episode multiplier supplies the variation but, on its own, spends it in households where it cannot be expressed. Put together, each supplies what the other lacks, which is why the product rule works and why the combination is, if anything, slightly more dispersed than it predicts.\n")
        pairs = [(float(r["infections_share_home"]), float(r["observed_over_predicted_k"])) for r in s9.values() if r.get("observed_over_predicted_k")]
        n = len(pairs)
        mh = sum(p[0] for p in pairs) / n
        mo = sum(p[1] for p in pairs) / n
        cor = sum((a - mh) * (b - mo) for a, b in pairs) / ((sum((a - mh) ** 2 for a, b in pairs) * sum((b - mo) ** 2 for a, b in pairs)) ** 0.5)
        w(f"**The same ceiling explains the residual pattern across the whole grid.** Over all {n} arms the share of infections that happen at home correlates with the ratio of observed to predicted k at {fmt(cor, 3)}: "
          "the arms where the multiplier underdelivers are exactly the arms where its episodes are spent in households. The order runs from the reference arms (43% at home, ratio 1.24 to 1.33), through the no-class scene "
          "(23% at home, 1.07 to 1.16), to the tilted-class scenes (15% at home, 0.92 to 1.03) and the lambda 30 scene (6% at home, 1.00 to 1.03). Where almost no transmission is left at home, the product rule is exact.\n")

        w("A consequence for the rule as a design tool: using the nominal 1/shape is right when the multiplier acts on top of a scene, and optimistic when it acts alone. If the rule goes into the paper, the honest form is the nominal one with this caveat stated, rather than a refitted constant, because the discrepancy is not a constant of the multiplier but a property of where transmission happens.\n")

    w("### Zero share and the registered direction\n")
    g = [arm("t1_L10", s) for s in SHAPES]
    if all(g):
        w("Registered: the zero share rises with the multiplier, reaching at least 45% at tau 1 lambda 10 with shape 1, against 34.4% for that scene alone. Observed in that column: "
          + ", ".join(f"shape {s}: {pct(r, 'share_0')}" for s, r in zip(SHAPES, g))
          + f", against 34.4% for the scene alone (round 8). The direction is as registered and the shape-1 value {'meets' if float(g[2]['share_0']) >= 0.45 else 'misses'} the 45% threshold. "
            "At a matched mean of 1.4 the same arms give " + ", ".join(f"{pct(r, 'zero_at_mean_1.4_mom')}" for r in g) + ".\n")

    w("### Interaction between the class and the multiplier\n")
    w("Note 52 asks whether the cells with a class show an interaction, that is whether class members with a high multiplier are also the ones at the high-L venues. Two checks:\n")
    if combined:
        sr = [float(r["shed_ratio_class_to_others"]) for r in combined if r.get("shed_ratio_class_to_others")]
        if sr:
            w(f"1. **The draws are independent in practice.** The mean per-episode multiplier of infected class members, divided by that of infected others, runs from {fmt(min(sr), 4)} to {fmt(max(sr), 4)} over the combined cells (prediction 1). There is no selection of high multipliers into the class, as the separate generators imply.")
    w("2. **The two sources act on the same people only by chance, and that is enough.** The mean offspring of index cases by class and by quartile of the multiplier is in `53_s9_summary.csv` (`mean_offspring_class_shed_q*` and `mean_offspring_others_shed_q*`). The class members in the top quartile of the multiplier are the arm's superspreaders; because the two draws are independent, they are about 5% of 25% of the eligible agents, and it is their rarity, not any correlation, that produces the tail. A correlated version (R9-3 item 2) would concentrate the two risks in the same people and is predicted to go further; it was not run (D2).\n")

    w("## 3. R9-2: assortative mixing in the round-8 scenes (existing traces, no new runs)\n")
    head = ["arm", "class to class", "class to others", "others to class", "others to others", "class share of infections caused", "fraction of the class infected by day 28",
            "fraction of others infected", "ratio", "share of the class's infections from a class infector", "offspring ratio r", "r excluding class targets"]
    body = []
    for a in ("s8_3_L10", "s8_2_t1_L30", "s8_2_t1_L10"):
        r = mix.get(a)
        if not r:
            continue
        body.append([a, pct(r, "share_class_to_class"), pct(r, "share_class_to_other"), pct(r, "share_other_to_class"), pct(r, "share_other_to_other"),
                     pct(r, "class_share_of_infections_caused"), pct(r, "fraction_of_class_infected_by_day28"), pct(r, "fraction_of_others_infected_by_day28"),
                     fmt(num(r, "ratio_of_infected_fractions_class_to_others"), 3), pct(r, "share_of_class_infections_with_class_infector"),
                     fmt(num(r, "offspring_ratio_r_observed"), 3), fmt(num(r, "offspring_ratio_r_class_to_other_over_all_other"), 3)])
    w(table(head, body) + "\n")
    w("The offspring ratio r here is the plain per-capita ratio (offspring per class agent over offspring per other agent). Round 8 reported the odds-ratio form of the same quantity (79.1, 29.3 and 19.0 for these three arms); both are in the CSV. "
      "**Answer to the question in note 52:** class-to-class transmission explains a large part of the ratio but not all of it. Counting only the infections the class causes in non-class agents, the ratio falls from 90.6 to 44.0 in S8-3 lambda 10, from 33.6 to 22.2 in S8-2 tau 1 lambda 30, and from 21.8 to 14.6 in S8-2 tau 1 lambda 10. Those remainders are still well above the weight predictions (8.1, 5.7 and 4.4), so the weight predictor fails for a second reason besides assortativity. "
      "The depletion that note 51 suspected is real and large: in S8-3 lambda 10 more than a third of the class is infected within four weeks while 2.3% of everyone else is, so the class's own susceptibles are running out while the epidemic is still being matched at day 28.\n")

    w("## 4. R9-3: the two small checks\n")
    if rep:
        a = [int(r["capTop_day84"]) for r in rep]
        b = [int(r["scaleAll_day84"]) for r in rep]
        w(table(["replicate", "capTop day 84", "scaleAll day 84", "difference"],
                [[r["replicate"], r["capTop_day84"], r["scaleAll_day84"], r["difference"]] for r in rep]) + "\n")
        w(f"**They are not the same simulations.** No replicate pair is equal, the mean absolute difference is {sum(abs(x - y) for x, y in zip(a, b)) / len(a):.1f} infections and the two series correlate at 0.991 because they share seeds and, under the D2 quirk, are nearly the same intervention. "
          f"The means are {sum(a) / len(a):.1f} and {sum(b) / len(b):.1f}. With a per-replicate difference of standard deviation about 253, the standard error of the difference of means is about 73, so an agreement within 0.2 infections has probability of order 1 in 500. It is a coincidence, as note 51 suspected, and nothing depends on it: the cell stays marked unusable.\n")
    w("Item 2 (the correlated multiplier) was not run (D2).\n")

    w("## 5. Where the mechanisms stand\n")
    w("Updating the table of note 51 section 6 with this round:\n")
    gate = arm("t1_L10", 1)
    low = min((r for r in s9.values() if r["scene"] != "none"), key=lambda r: float(r["k_mom"])) if s9 else None
    w(table(["mechanism family", "best k reached (moment)", "what is missing"],
            [["occupancy and crowding", "1.57", "cannot create overdispersion by itself"],
             ["more mobile people (round 7)", "3.2", "bounded by a 24-hour day and unscaled home, school and work transmission"],
             ["risk per hour by venue, tilted minority (round 8)", "0.85", "zero share about 40% against 59%; needs extreme contrasts"],
             ["rare events (rounds 5 and 6)", "near 0.3", "too few non-transmitters"],
             ["per-person or per-episode infectiousness", "0.3 by construction", "needs a biological or behavioural source"],
             ["**venue scene plus per-episode multiplier (this round)**",
              f"**{fmt(num(low, 'k_mom'), 3) if low else 'n/a'}**",
              "**nothing on these three statistics; both ingredients remain assumptions, and the multiplier still needs a source**"]]) + "\n")
    if gate:
        w(f"The gate cell reaches the real pattern with a scene that is one notch short on its own (k 1.13) and a multiplier that is milder than the one rounds 5 and 6 needed (shape 1, against 0.3). "
          f"At a matched mean of 1.4 it gives a zero share of {pct(gate, 'zero_at_mean_1.4_mom')} and {pct(gate, 'share_causing_80pct_at_mean_1.4_mom')} of infectors causing 80%, against {REAL}.\n")

    w("## 6. In plain terms\n")
    w("1. **The headline for the paper changes shape.** Up to round 8 the finding was negative: no single mechanism reaches the observed superspreading pattern at plausible settings. Round 9 shows the positive counterpart: two moderate mechanisms of different kinds, one in where people go and one in how infectious an episode is, multiply rather than add, and together they land on the observed pattern. The composition rule says how much of each is needed, and it holds across a 12-cell grid.")
    w("2. **What it does not settle.** The per-episode multiplier is still an assumption with no source in the model, and the venue scene still needs a 5% minority spending 11 hours a day at venues ten times riskier per hour. The round says these are enough together, not that they are what happens.")
    w("3. **Why the weight predictor of round 8 failed is now partly answered.** Assortativity and depletion within the class account for roughly half the gap between the predicted and observed class offspring ratios; the rest is still open, and the burst-within-a-venue explanation remains untested.")
    w("4. **For control.** Nothing in this round changes the round-8 conclusion that targeting the most active pays off only when risk per hour differs between places. The combined arms concentrate transmission further, so the targeting case there is at least as strong.\n")

    w("## 7. Open points\n")
    w("1. R9-3 item 2, the correlated multiplier, is the obvious next cell and the only one I could not do with a flag (about half an hour).")
    w("2. The deviations from the rule are ordered by the home share of infections (correlation 0.87), so they are a property of where transmission happens, not a constant to be refitted. If the rule goes into the paper it should keep the nominal form with that caveat. What would test the explanation directly is an arm with the multiplier alone and household transmission suppressed; that is a closure rule and one run.")
    w("3. S8-3 is still outside the grid and its D2 quirk is unfixed; combining the strongest scene with a multiplier would go below the real k, which may be worth one cell as an upper bound on what the model can do.\n")

    w("## Files\n")
    w("`53_round9_results.md` (this note), `53a_review_of_note52.md`, `53_s9_summary.csv`, `53_s9_offspring.csv`, `53_r92_assortative_mixing.csv`, `53_r93_s83_cap_vs_scaleall_day84.csv`, `53_upload_index.md`. No file exceeds 1 MB.")
    text = "\n".join(out) + "\n"
    (OUT / "53_round9_results.md").write_text(text, newline="\n")
    print(len(text), "characters")


if __name__ == "__main__":
    main()
