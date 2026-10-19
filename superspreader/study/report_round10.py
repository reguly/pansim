#!/usr/bin/env python3
"""Write 56_round10_results.md from the CSVs in superspreader/."""
from report_tables import OUT, ci, fmt, num, pct, rows, table

W1, W2, W3 = "world1_w1_sh0.32", "world2_scene_plus_multiplier", "world3_w3_rate0.034"
NAMES = {W1: "world 1, multiplier only (shape 0.32)", W2: "world 2, scene plus multiplier (round-9 gate cell)",
         W3: "world 3, closed-group events (group 30, rate 0.034)"}
REAL = "about 0.3 for k, about 59% of infectors with no offspring and about 20% causing 80%, at a mean of 1.4"


def main():
    w = {r["cell"]: r for r in rows("56_r101_worlds.csv")}
    o = {r["cell"]: r for r in rows("56_r102_r104_summary.csv")}
    pr = {r["world"]: r for r in rows("56_r101_repeat_infections.csv")}
    out = []
    a = out.append

    def v(cell, key, d=3):
        return fmt(num(w[cell], key), d)

    a("# ACT-049 note 56: round 10, the same k in different worlds\n")
    a("19 October 2026. Reply to note 55. Review and the registered predictions: `56a_review_of_note55.md`. Code: `superspreader/study/run_round10.py`, `analyze_round10.py`, `report_round10.py`, `t1_round10.py`, `build_r10_inputs.py`; the per-agent mean of the per-episode multiplier added in `include/locationList.h` and `include/policies/infectionPolicies.h` (uncommitted); binary `build_r10`. The location and agent files are not edited; the household-suppressed location file is a new copy.\n")

    a("## Headline\n")
    a(f"1. **The three worlds are distinguishable at the same k, and the statistic that does it is not the one note 55 expected.** Tuned to moment k {v(W1, 'k_mom')}, {v(W2, 'k_mom')} and {v(W3, 'k_mom')}, they differ sharply in where infections happen (home share {pct(w[W1], 'infections_share_home')}, {pct(w[W2], 'infections_share_home')}, {pct(w[W3], 'infections_share_home')}; share at the four high-L venue types {pct(w[W1], 'infections_share_high_L_types')}, {pct(w[W2], 'infections_share_high_L_types')}, {pct(w[W3], 'infections_share_high_L_types')}) and in the shape of their largest clusters, but **not** in cluster size.")
    a(f"2. **The sharpest single discriminator is cluster composition.** In the ten largest clusters of each replicate, the share of infections that happened in one venue on one day is {pct(w[W1], 'top10_clusters_mean_largest_venue_day_share')} in world 1, {pct(w[W2], 'top10_clusters_mean_largest_venue_day_share')} in world 2 and {pct(w[W3], 'top10_clusters_mean_largest_venue_day_share')} in world 3, over {v(W1, 'top10_clusters_mean_distinct_venues', 2)}, {v(W2, 'top10_clusters_mean_distinct_venues', 2)} and {v(W3, 'top10_clusters_mean_distinct_venues', 2)} distinct venues. An events world makes single-venue explosions; the other two spread the same number of offspring over six to nine places.")
    a(f"3. **Registered prediction (b) fails, and the reason matters.** The largest cluster of world 2 is {w[W2]['largest_offspring_max']} against {w[W1]['largest_offspring_max']} in world 1, a ratio of {num(w[W2], 'largest_offspring_max') / num(w[W1], 'largest_offspring_max'):.2f}, not the predicted 2 or more. The round-9 contrast that motivated the prediction (20 against 61) was measured at unmatched k; once the multiplier is strong enough to reach k = 0.34 on its own, it produces clusters nearly as large as the scene does.")
    a(f"4. **Registered prediction (d) fails, and in the most interesting way.** The offspring correlation across repeated infections of the same agent is {fmt(num(pr['world1_multiplier_only'], 'pearson'), 3)} in world 1 and {fmt(num(pr['world2_scene_plus_multiplier'], 'pearson'), 3)} in world 2. The note expected both below 0.1 and expected this statistic *not* to separate the worlds. It does separate them, because world 2 contains a persistent ingredient that world 1 lacks: the venue class is a property of the agent, carried across episodes, even though its multiplier is drawn per episode.")
    a(f"5. **R10-2 and R10-4 met; R10-3 confirms its direction but misses both thresholds.** The correlated multiplier gives k {fmt(num(o['r102_correlated'], 'k_mom'), 3)} against a predicted 0.41, which is 24.7% below the independent cell. The upper bound gives {fmt(num(o['r104_upper'], 'k_mom'), 3)} against a predicted 0.18, so the model can overshoot the real value and the round-9 match is a located point. Suppressing households raises the multiplier's realised share of its nominal variance from 0.705 to 0.826, not to 1, so households are about half of that shortfall and a second ceiling remains.\n")

    a("## 1. Deviations and points on note 55\n")
    a("The review (`56a`) is unchanged by the results. Deviations and things worth knowing:\n")
    a("- **D1. The code change for R10-2** adds `--sheddingClassMean` and `--sheddingOthersMean`: the per-episode gamma keeps its shape and is multiplied by a per-agent mean taken from the HVI class flags. Both default off. T1 passed in the strong form: with the options off, the trace and the daily table of three round-9 arms are byte-identical to `build_r9`.")
    a("- **D2. R10-3 needed no code.** Household transmission is suppressed with a copy of the location file in which the infectiousness of the 73,036 homes is 0. Movement is unchanged, so agents still go home; they just do not transmit there.")
    a("- **D3. A control arm was added to R10-3** (`56a` item 4), because suppressing households changes the baseline dispersion itself: the no-multiplier baseline of that world is moment k 2.33, not 4.59. Both readings are reported below.")
    a(f"- **D4. R10-2 realised means.** Class members drew a mean multiplier of 1.483 and the others 0.975 (nominal 1.5 and 0.974), a ratio of 1.522 against the nominal 1.540. The class is 4.40% of agents, so the population mean is 0.997 rather than 1 (`56a` item 5); among infections the mean is 1.096, because the class is infected more often, and the day-28 recalibration absorbs it.")
    a("- **D5. World 3 was retuned**, as foreseen: the round-6 cell with the lowest likelihood k sits at moment k 0.152, so I lowered the event rate to 0.034, which gives 0.385. That is 10% above world 2 and the closest of the settings tried; its interval (0.358 to 0.422) does not overlap world 2's (0.314 to 0.386), so world 3 is matched only approximately and I say so wherever it matters.")
    a("- **D6. Day 28** is within 3% in every arm (largest deviation +1.3%, world 1).")
    a("- **D7. All code is uncommitted**, as in previous rounds.\n")

    a("## 2. R10-1: the three worlds at matched k (12 replicates, 4 weeks, same seeds)\n")
    head = ["world", "coefficient", "moment k", "likelihood k", "k likelihood over moment", "early R", "zero share", "zero at mean 1.4",
            "causing 80%", "causing 80% at mean 1.4", "day 28 vs 6,211"]
    body = []
    for c in (W1, W2, W3):
        body.append([NAMES[c], fmt(num(w[c], "background_coefficient"), 3), ci(w[c], "k_mom"), ci(w[c], "k_ml"),
                     fmt(num(w[c], "k_ml") / num(w[c], "k_mom"), 3), ci(w[c], "early_R"), pct(w[c], "share_0"),
                     pct(w[c], "zero_at_mean_1.4_mom"), pct(w[c], "share_of_index_cases_causing_80pct"),
                     pct(w[c], "share_causing_80pct_at_mean_1.4_mom"), pct({"v": w[c]["day28_vs_6211.25"]}, "v")])
    a(table(head, body) + "\n")
    a(f"Worlds 1 and 2 are matched to 3% on the moment estimator and their intervals overlap; world 3 is 10% above and its interval does not (D5). The real pattern is {REAL}.\n")
    a("Two things are already visible in this table and were not registered. **The likelihood estimator separates the worlds even though the moment estimator was matched by construction**: the ratio of the two runs 1.06, 1.46 and 3.11. A single pair of estimators on real data would therefore carry information about the mechanism. **And the observed zero share differs by 22 points** (56.6%, 47.8%, 34.1%) at nearly the same moment k, because the three distributions are not equally well described by a negative binomial; projected to a common mean of 1.4 they converge to 57.5%, 57.0% and 55.4%, which is what hides the difference.\n")

    a("### Where transmission happens\n")
    head = ["world", "home", "school and work", "the four high-L types", "restaurant", "large venue", "church", "recreation", "household secondary attack rate"]
    body = []
    for c in (W1, W2, W3):
        body.append([NAMES[c], pct(w[c], "infections_share_home"), pct(w[c], "infections_share_school_and_work"),
                     pct(w[c], "infections_share_high_L_types"), pct(w[c], "infections_share_restaurant"),
                     pct(w[c], "infections_share_large_venue"), pct(w[c], "infections_share_church"),
                     pct(w[c], "infections_share_recreation"), fmt(num(w[c], "household_secondary_attack_rate"), 3)])
    a(table(head, body) + "\n")

    a("### Cluster size and composition\n")
    head = ["world", "largest offspring (max over replicates)", "largest offspring (mean over replicates)", "offspring p99", "offspring p99.9",
            "ten largest clusters: mean offspring", "distinct venues", "share in one venue-day"]
    body = []
    for c in (W1, W2, W3):
        body.append([NAMES[c], w[c]["largest_offspring_max"], fmt(num(w[c], "largest_offspring_mean_over_replicates"), 3),
                     fmt(num(w[c], "offspring_p99"), 3), fmt(num(w[c], "offspring_p999"), 3),
                     fmt(num(w[c], "top10_clusters_mean_offspring"), 3), fmt(num(w[c], "top10_clusters_mean_distinct_venues"), 3),
                     pct(w[c], "top10_clusters_mean_largest_venue_day_share")])
    a(table(head, body) + "\n")
    a("The per-cluster rows are in `56_r101_clusters.csv`. Cluster **size** does not separate worlds 1 and 2 at matched k; cluster **shape** separates all three.\n")

    a("### Who the big infectors are\n")
    head = ["world", "mean age of the top 1% of infectors", "mean age of all infectors", "difference", "share of the top 1% in the class"]
    body = []
    for c in (W1, W2, W3):
        body.append([NAMES[c], fmt(num(w[c], "top1pct_mean_age"), 4), fmt(num(w[c], "all_infectors_mean_age"), 4),
                     fmt(num(w[c], "top1pct_mean_age") - num(w[c], "all_infectors_mean_age"), 3),
                     pct(w[c], "top1pct_share_in_class") if w[c].get("top1pct_share_in_class") else "n/a"])
    a(table(head, body) + "\n")
    a("The age profile is a third discriminator and it points in opposite directions: in world 1 the biggest infectors are **younger** than average infectors by 6.4 years, in world 2 they are **older** by 4.5 years, and in world 3 they are an ordinary sample (0.4 years). In world 2, 94.4% of the top 1% of infectors belong to the 5% class.\n")
    a("The occupational profile is sharper still, and it is the kind of thing a contact-tracing study records. Share of the top 1% of infectors against the share of all infectors, by agent type:\n")
    types = {2: "kindergarten", 3: "elementary school", 4: "high school", 5: "university", 6: "full-time worker", 7: "afternoon-shift worker", 8: "stay at home"}
    head = ["agent type"] + [f"{NAMES[c].split(',')[0]}: top 1% / all" for c in (W1, W2, W3)]
    body = []
    for t, nm in types.items():
        cells = []
        for c in (W1, W2, W3):
            top = num(w[c], f"top1pct_share_agent_type{t}") or 0.0
            allv = num(w[c], f"all_infectors_share_agent_type{t}") or 0.0
            cells.append(f"{100 * top:.1f}% / {100 * allv:.1f}%")
        body.append([nm] + cells)
    a(table(head, body) + "\n")
    a("**The three worlds put superspreading in three different occupations.** In world 1 it is schoolchildren: elementary pupils are 21.5% of the top 1% of infectors against 9.8% of all infectors, a factor of 2.2, while people who stay at home are strongly under-represented (9.6% against 24.1%). A large per-episode multiplier pays off wherever the agent happens to be, and the densest places an ordinary agent goes are classrooms. In world 2 it is stay-at-home adults (47.9% against 37.3%), because the venue class is drawn from agents aged 15 and over and those with the most discretionary hours gain the most from it; no pupil can be a superspreader there at all (0% of the top 1%). In world 3 it is full-time workers (62.2% against 47.5%), because the events are drawn at restaurants and shops. An epidemiologist who knew only k would miss this entirely.\n")

    a("### Repeat infections (R10-1 item 4)\n")
    head = ["world", "replicates", "pairs", "Pearson correlation of offspring across two infections of the same agent", "Spearman"]
    body = []
    for key, name in (("world1_multiplier_only", NAMES[W1]), ("world2_scene_plus_multiplier", NAMES[W2])):
        r = pr[key]
        body.append([name, r["replicates"], r["pairs"], ci(r, "pearson"), ci(r, "spearman")])
    a(table(head, body) + "\n")
    a("16 weeks, 8 replicates, vaccination off, every episode logged. References: 0.544 for the persistent abstract trait of R6-2 and 0.041 for persistent mobility (round 7, S5).\n")
    a("This is the registered prediction that failed most informatively. Note 55 expected both worlds below 0.1 and expected the statistic not to separate them, on the ground that both causes are per-episode. World 1 is indeed per-episode and shows no correlation at all (slightly negative). World 2 is **not** purely per-episode: the agent's membership of the venue class persists for life, so an agent who is infected twice is at the high-L venues on both occasions, and only the multiplier is redrawn. The correlation of 0.104 is the persistent part showing through. **A repeat-infection study could therefore tell a purely biological per-episode cause from one with a behavioural component, even when k, the mean and the zero share agree.**\n")

    a("## 3. R10-2, R10-3 and R10-4\n")
    head = ["arm", "coefficient", "moment k", "likelihood k", "zero share", "home share", "high-L share", "largest offspring", "day 28 vs 6,211", "predicted", "observed over predicted"]
    preds = {"r102_correlated": 0.41, "r104_upper": 0.18}
    body = []
    for c in ("r102_correlated", "r103_nohome_sh1", "r103_nohome_base", "r104_upper", "round9_reference_sh1", "round9_gate_sh2"):
        p = preds.get(c)
        body.append([c, fmt(num(o[c], "background_coefficient"), 3), ci(o[c], "k_mom"), ci(o[c], "k_ml"), pct(o[c], "share_0"),
                     pct(o[c], "infections_share_home"), pct(o[c], "infections_share_high_L_types"), o[c]["largest_offspring_max"],
                     pct({"v": o[c]["day28_vs_6211.25"]}, "v"), fmt(p, 3) if p else "", fmt(num(o[c], "k_mom") / p, 3) if p else ""])
    a(table(head, body) + "\n")

    a("### R10-2, the correlated multiplier\n")
    a(f"Observed moment k {fmt(num(o['r102_correlated'], 'k_mom'), 3)} ({fmt(num(o['r102_correlated'], 'k_mom_low'), 3)} to {fmt(num(o['r102_correlated'], 'k_mom_high'), 3)}) against the registered 0.41, acceptance 0.29 to 0.57: **met**, ratio 0.93. Against the independent cell of round 9 (0.508) it is **24.7% below**, where note 55's revised calculation expected about 19% and note 52 had said at least 20%. Concentrating the two risks in the same people therefore buys about a quarter of the dispersion, and the direction and size of the effect are as the coordinator calculated.\n")

    a("### R10-3, the multiplier without households\n")
    head = ["reading", "baseline k of that world", "predicted k", "observed k", "observed over predicted", "realised share of the nominal added CV^2", "largest offspring"]
    body = [["round 9 reference, households present", "4.59 (model baseline)", "0.697", "0.928", "1.333", "0.705", "20"],
            ["R10-3, households suppressed, nominal baseline", "4.59 (nominal)", "0.697", "0.621", "0.891", "n/a", "27"],
            ["R10-3, households suppressed, measured baseline", "2.331 (control arm)", "0.538", "0.621", "1.154", "0.826", "27"]]
    a(table(head, body) + "\n")
    a("The like-for-like comparison is the first and third rows, each using its own world's baseline. On that reading the ratio falls from 1.333 to 1.154 and the realised share of the multiplier's nominal variance rises from 0.705 to 0.826. **The direction is confirmed and the size is substantial, but both registered thresholds are missed**: the ratio does not fall below 1.1 and the largest cluster rises to 27, not above 30. The honest conclusion is that households are about half of the shortfall and that a second ceiling remains. The obvious candidate is the rest of the finite settings: with homes removed, the no-multiplier baseline is still only 2.33, school and work carry 22.1% of infections, the two shop types 30.4% and the four high-L types 24.0%, so most transmission still happens in places of fixed, modest size. Note also that suppressing households is not a small perturbation: it removes about 40% of all transmission and the coefficient has to rise from 0.00041 to 0.00073 to hold day 28.\n")

    a("### R10-4, the upper bound\n")
    a(f"Observed moment k {fmt(num(o['r104_upper'], 'k_mom'), 3)} ({fmt(num(o['r104_upper'], 'k_mom_low'), 3)} to {fmt(num(o['r104_upper'], 'k_mom_high'), 3)}) against the registered 0.18, acceptance 0.126 to 0.252: **met**, ratio 1.06. The largest cluster is {o['r104_upper']['largest_offspring_max']} and the zero share {pct(o['r104_upper'], 'share_0')}. The model can therefore produce dispersion well past the observed value, which is what the cell was for: the round-9 match at shape 1 is a located point on a continuum, not the edge of what the model can do.\n")

    a("## 4. Predictions scored\n")
    a("| Test | Prediction | Result | Verdict |\n|---|---|---|---|")
    d_home = 100 * (num(w[W1], "infections_share_home") - num(w[W2], "infections_share_home"))
    a(f"| R10-1 (a) | home share differs by at least 15 points between worlds 1 and 2 | {pct(w[W1], 'infections_share_home')} against {pct(w[W2], 'infections_share_home')}, a difference of {d_home:.1f} points | **met** |")
    a(f"| R10-1 (b) | largest offspring of world 2 at least twice world 1 | {w[W2]['largest_offspring_max']} against {w[W1]['largest_offspring_max']}, ratio {num(w[W2], 'largest_offspring_max') / num(w[W1], 'largest_offspring_max'):.2f} | **failed** |")
    a(f"| R10-1 (c) | household secondary attack rate of world 1 at least 1.5 times world 2 | {fmt(num(w[W1], 'household_secondary_attack_rate'), 3)} against {fmt(num(w[W2], 'household_secondary_attack_rate'), 3)}, ratio {num(w[W1], 'household_secondary_attack_rate') / num(w[W2], 'household_secondary_attack_rate'):.2f} | **met** |")
    a(f"| R10-1 (d) | repeat-infection correlation below 0.1 in both, and should not separate the worlds | {fmt(num(pr['world1_multiplier_only'], 'pearson'), 3)} and {fmt(num(pr['world2_scene_plus_multiplier'], 'pearson'), 3)} | **failed**: world 2 is above 0.1 and the statistic does separate them |")
    a(f"| R10-1 (e) | world 3 keeps a lower zero share than worlds 1 and 2 at the same k | {pct(w[W3], 'share_0')} against {pct(w[W1], 'share_0')} and {pct(w[W2], 'share_0')} | **met** |")
    a(f"| R10-2 | moment k 0.41, acceptance 0.29 to 0.57 | {fmt(num(o['r102_correlated'], 'k_mom'), 3)} | **met** |")
    a("| R10-3 | observed over predicted falls from 1.33 to below 1.1; largest offspring above 30 | 1.154 on the like-for-like reading; largest offspring 27 | **failed on both thresholds**, direction confirmed |")
    a(f"| R10-4 | moment k 0.18, acceptance 0.126 to 0.252 | {fmt(num(o['r104_upper'], 'k_mom'), 3)} | **met** |")
    a("")
    a("The note's own conclusion test was: if (a) to (c) hold, the paper can say that k alone does not identify the mechanism and that cluster composition does. (a) and (c) hold, (b) fails. **The conclusion survives in a stronger form than the test was written for**: k alone does not identify the mechanism, and cluster composition does, but cluster *size* does not, so the discriminating statistic has to be the shape of a cluster, not how big it is.\n")

    a("## 5. In plain terms\n")
    a("1. **The identifiability question has a clean answer.** Three mechanisms tuned to the same dispersion produce visibly different epidemics. An observer with cluster investigations could tell them apart: in the events world 91% of a large cluster happens in one place on one day, in the other two worlds 15% to 20% and the cluster is spread over six to nine venues. An observer with only k, the mean and the zero share at a matched mean could not.")
    a("2. **The statistic the paper should recommend is not cluster size.** At matched k the largest clusters are 54, 61 and 36, which is no basis for telling the worlds apart. What works is the share of a cluster concentrated in one venue-day, the share of infections at home, the household attack rate, the occupation and age of the biggest infectors, and the gap between the two k estimators.")
    a("3. **Each world puts superspreading in a different occupation**: schoolchildren, stay-at-home adults and full-time workers respectively. That is a prediction a real contact-tracing dataset could check directly, and it does not depend on measuring dispersion at all.")
    a("4. **A behavioural cause leaves a fingerprint in repeat infections that a biological one does not.** This was predicted to be the one statistic that would not separate the worlds, and it separates them, because a scene is a property of a person while shedding is a property of an episode.")
    a("5. **The household ceiling is real but partial.** Removing household transmission recovers about half of what the multiplier loses against its nominal variance. The rest is the other finite settings, so the round-9 explanation should be stated as 'the finite size of the groups an infectious person meets', of which households are the largest single part, rather than as households alone.\n")

    a("## 6. Open points\n")
    a("1. World 3 is matched only to 10% (D5). If the comparison matters for the paper, one more rate between 0.034 and 0.05 would bring it inside the interval; about 10 minutes.")
    a("2. The repeat-infection result suggests an experiment the study has not done: the same scene with the class redrawn every episode, which would remove the persistent part and should take the correlation back to zero. That would turn a suggestive difference into a controlled one; about 25 minutes.")
    a("3. R10-3's second ceiling is untested. With homes removed the largest remaining categories are the two shop types (30.4% of infections) and school and work (22.1%), all of them places of fixed and modest occupancy, so the natural follow-up is to suppress those too and see whether the realised fraction goes above 0.9.")
    a("4. World 3 was tuned on the event rate at one group size (30). The group size is the parameter that sets how large a single-venue explosion can be, so a sweep over it would say how much of the 91% one-venue-day share is a property of events in general rather than of this setting.\n")

    a("## Files\n")
    a("`56_round10_results.md` (this note), `56a_review_of_note55.md`, `56_r101_worlds.csv`, `56_r101_worlds_offspring.csv`, `56_r101_clusters.csv`, `56_r101_repeat_infections.csv`, `56_r102_r104_summary.csv`, `56_r102_r104_offspring.csv`, `56_upload_index.md`. No file exceeds 1 MB.")
    text = "\n".join(out) + "\n"
    (OUT / "56_round10_results.md").write_text(text, newline="\n")
    print(len(text), "characters")


if __name__ == "__main__":
    main()
