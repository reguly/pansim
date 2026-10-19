# ACT-049 note 53: round 9, do moderate mechanisms add up?

18 October 2026. Reply to note 52. Review before running, with the registered predictions: `53a_review_of_note52.md`. Code: `superspreader/study/run_round9.py`, `analyze_round9.py`, `report_round9.py`, `t1_round9.py`; the one-line change in `include/policies/movementPolicies.h` (uncommitted); binary `build_r9`. The location and agent files are not edited.

## Headline

1. **They add up, and the composition rule predicts how.** Across the 12 combined cells the observed moment k is close to the registered prediction, and every cell is inside the acceptance band of 0.7 to 1.4 times predicted. The rule 1 + 1/k = (1 + 1/k_scene)(1 + 1/shape) is therefore usable as a design rule in this model, which is the question note 52 asked.
2. **A moderate venue scene plus a moderate per-episode multiplier reaches the real pattern.** The gate cell at shape 1 (S8-2 tau 1 lambda 10, a 5% class at venues 10 times riskier per hour, with a per-episode multiplier of squared coefficient of variation 1) gives moment k 0.349 (0.313 to 0.385), and at a matched mean of 1.4 a zero share of 57.0% and 21.1% of infectors causing 80% of infections. The real pattern is about 0.3 for k, about 59% zero, about 20% causing 80%, at a mean of 1.4. This is the first arm in the study that matches all three at once, and neither ingredient does it alone (the scene alone: k 1.13; the multiplier alone at this shape: see the reference arms).
   The closest match in the grid is the strongest cell, S8-2 tau 1 lambda 30 with shape 1: moment k 0.31 (0.272 to 0.348), zero share at matched mean 58.9% and 19.6% causing 80%, against 0.3, 59% and 20%. All three agree within the replicate interval.
3. **Neither ingredient is extreme.** The scene is the round-8 cell that was already one step short, and the multiplier at shape 1 is milder than the shape 0.3 used in rounds 5 and 6. The conclusion of rounds 7 and 8, that no single mechanism in this model reaches the real pattern at plausible settings, survives; what changes is that two moderate ones together do.
4. **The assortative-mixing hypothesis of note 51 is confirmed and quantified (R9-2), but it is not the whole story.** In S8-3 lambda 10, 41.5% of all infections are class to class, 93.7% of the infections the class receives come from a class infector, and 36.7% of the class is infected by day 28 against 2.3% of everyone else, a ratio of 15.8. Removing class-to-class transmission entirely still leaves a class-to-others offspring ratio of 44, against the 8.1 the weight predictor gave. So assortativity and depletion explain about half of the gap, not all of it.
5. **The two S8-3 control arms are not duplicated runs (R9-3).** No replicate pair matches, the mean absolute difference is 208 infections and the correlation is 0.991 (shared seeds, nearly the same intervention). The agreement of their means to 0.002% is a coincidence of about the size note 51 estimated.

## 1. Deviations and points on note 52

The review (`53a`) found no error in the composition arithmetic; all 12 rows of `51_round9_composition_predictions.csv` reproduce the formula. Points and deviations:

- **D1. The reference arms were run with the gate column, not after it** (`53a` item 7): if the rule had failed at the gate, the references are what separates a wrong composition rule from a multiplier that does not behave as in earlier rounds.
- **D2. R9-3 item 2 (correlated multiplier) not run**, as the note instructs, because it needs about ten lines across two headers rather than a flag: the per-episode draw sits in `infectAgents` (`locationList.h`), which has no access to the HVI class array held by the movement policy. About half an hour including the run, if you want it.
- **D3. The strongest round-8 scene (S8-3) is not in the grid**, so the lowest k in this round is bounded by the S8-2 tau 1 lambda 30 column, not by the lowest scene available.
- **D4. Means differ between arms** (early R 1.4 to 1.7 at a matched day 28), so the raw moment k and the matched-mean shares are reported side by side, as the note asks. My reproduction of `51_round8_matched_mean_shares.csv` agrees with note 51 to four decimals on all six of its arms.
- **D5. Binary and state.** `build_r9` for everything. The combined check in `initializeArgs` now blocks only `--traitShape`. T1 passed in the strong form: trace, HVI dump and daily table byte-identical to `build_r8` on three round-8 arms with shedding off; the HVI dump is also unchanged when `--sheddingShape 2` is added, so the class assignment does not depend on the multiplier. All code is uncommitted.

## 2. R9-1: the grid (12 replicates, 4 weeks, day 28 matched to 6,211.25, same seeds in every arm)

| scene | shape | predicted k | observed k (moment) | observed / predicted | in acceptance | observed k (likelihood) | zero share | causing 80% | zero at mean 1.4 | causing 80% at mean 1.4 | early R | day 28 vs 6,211 | coefficient |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S8-1 lambda 10, venue risk for everyone, no class | 3 | 1.27 | 1.36 (1.27 to 1.47) | 1.07 | yes | 1.43 (1.36 to 1.52) | 35.4% (34.9 to 35.9) | 36.0% | 38.2% | 34.6% | 1.5 (1.47 to 1.52) | -0.1% | 0.000167 |
| S8-1 lambda 10, venue risk for everyone, no class | 2 | 0.99 | 1.11 (1.05 to 1.19) | 1.13 | yes | 1.17 (1.11 to 1.23) | 37.9% (37.4 to 38.4) | 34.2% | 40.4% | 33.1% | 1.49 (1.46 to 1.52) | 0.0% | 0.000168 |
| S8-1 lambda 10, venue risk for everyone, no class | 1 | 0.59 | 0.685 (0.645 to 0.73) | 1.16 | yes | 0.737 (0.7 to 0.776) | 44.0% (43.2 to 44.9) | 29.8% | 46.7% | 28.6% | 1.48 (1.45 to 1.52) | -0.2% | 0.00017 |
| S8-2 tau 0.5 lambda 10 | 3 | 0.79 | 0.81 (0.766 to 0.857) | 1.02 | yes | 1 (0.962 to 1.05) | 38.3% (37.6 to 39.0) | 33.3% | 44.4% | 30.3% | 1.52 (1.49 to 1.54) | -2.9% | 0.000137 |
| S8-2 tau 0.5 lambda 10 | 2 | 0.65 | 0.648 (0.618 to 0.681) | 0.996 | yes | 0.845 (0.817 to 0.875) | 40.1% (39.4 to 40.7) | 31.6% | 47.4% | 28.0% | 1.54 (1.51 to 1.57) | 1.0% | 0.000139 |
| S8-2 tau 0.5 lambda 10 | 1 | 0.42 | 0.434 (0.411 to 0.455) | 1.03 | yes | 0.602 (0.586 to 0.618) | 45.2% (44.3 to 46.1) | 27.9% | 53.5% | 23.6% | 1.54 (1.5 to 1.59) | 2.5% | 0.000142 |
| S8-2 tau 1 lambda 10 (gate) | 3 | 0.66 | 0.638 (0.618 to 0.66) | 0.967 | yes | 0.812 (0.793 to 0.835) | 39.8% (39.3 to 40.3) | 31.3% | 47.7% | 27.9% | 1.59 (1.55 to 1.62) | -0.1% | 0.000116 |
| S8-2 tau 1 lambda 10 (gate) | 2 | 0.55 | 0.508 (0.475 to 0.542) | 0.923 | yes | 0.702 (0.677 to 0.734) | 42.0% (41.5 to 42.5) | 29.8% | 51.1% | 25.4% | 1.58 (1.55 to 1.61) | 0.9% | 0.000117 |
| S8-2 tau 1 lambda 10 (gate) | 1 | 0.36 | 0.349 (0.313 to 0.385) | 0.97 | yes | 0.51 (0.494 to 0.527) | 47.8% (47.0 to 48.7) | 25.7% | 57.0% | 21.1% | 1.54 (1.49 to 1.58) | -0.2% | 0.000119 |
| S8-2 tau 1 lambda 30 | 3 | 0.53 | 0.536 (0.509 to 0.565) | 1.01 | yes | 0.649 (0.621 to 0.681) | 42.5% (41.8 to 43.1) | 29.0% | 50.2% | 26.0% | 1.65 (1.61 to 1.7) | -0.9% | 4.31e-05 |
| S8-2 tau 1 lambda 30 | 2 | 0.44 | 0.442 (0.411 to 0.472) | 1 | yes | 0.581 (0.561 to 0.601) | 44.2% (43.4 to 44.9) | 27.7% | 53.2% | 23.8% | 1.66 (1.61 to 1.71) | -0.6% | 4.31e-05 |
| S8-2 tau 1 lambda 30 | 1 | 0.3 | 0.31 (0.272 to 0.348) | 1.03 | yes | 0.435 (0.421 to 0.452) | 49.8% (49.0 to 50.6) | 24.0% | 58.9% | 19.6% | 1.61 (1.53 to 1.67) | -2.7% | 4.37e-05 |
| shedding multiplier alone, no scene | 3 | 1.6 | 1.99 (1.88 to 2.12) | 1.24 | yes | 2.07 (1.94 to 2.2) | 33.8% (33.2 to 34.5) | 38.0% | 34.6% | 37.4% | 1.41 (1.38 to 1.42) | -0.0% | 0.000428 |
| shedding multiplier alone, no scene | 2 | 1.21 | 1.56 (1.47 to 1.67) | 1.29 | yes | 1.62 (1.53 to 1.74) | 35.9% (35.3 to 36.6) | 36.1% | 36.8% | 35.6% | 1.41 (1.39 to 1.44) | 0.2% | 0.000436 |
| shedding multiplier alone, no scene | 1 | 0.7 | 0.928 (0.895 to 0.97) | 1.33 | yes | 0.948 (0.914 to 0.988) | 42.2% (41.6 to 42.8) | 31.7% | 42.6% | 31.5% | 1.4 (1.37 to 1.43) | -0.4% | 0.000453 |

The class shares, the negative-binomial zero shares at both estimators, the shares above 5 offspring and the shares of infections by location type are in `53_s9_summary.csv`; the offspring histograms are in `53_s9_offspring.csv`.

### The composition rule

Over the 12 combined cells the ratio of observed to predicted moment k runs from 0.923 to 1.16 (mean 1.03), and 12 of 12 are inside the acceptance band. The rule is therefore accepted. The deviations are not random: they run from 1.16 in the no-class scene down to 0.92 in the gate column, and the next section shows they are ordered by how much transmission is left at home. Once that is allowed for, the rule is accurate to about 10% over a grid spanning k from 1.36 to 0.31.

### The multiplier alone is weaker than the rule assumes, and the reason explains the combination

| arm | predicted k | observed k (moment) | observed / predicted | realised added CV^2 | nominal added CV^2 (1/shape) | realised fraction | home share of infections | share at the four high-L types | largest offspring |
|---|---|---|---|---|---|---|---|---|---|
| shedding alone, shape 3 | 1.6 | 1.99 (1.88 to 2.12) | 1.24 | 0.234 | 0.333 | 0.702 | 43.2% | 14.4% | 16 |
| shedding alone, shape 2 | 1.21 | 1.56 (1.47 to 1.67) | 1.29 | 0.347 | 0.5 | 0.694 | 42.3% | 14.7% | 16 |
| shedding alone, shape 1 | 0.7 | 0.928 (0.895 to 0.97) | 1.33 | 0.705 | 1 | 0.705 | 40.2% | 15.3% | 20 |
| gate cell, shape 3 | 0.66 | 0.638 (0.618 to 0.66) | 0.967 |  |  |  | 15.4% | 76.6% | 30 |
| gate cell, shape 2 | 0.55 | 0.508 (0.475 to 0.542) | 0.923 |  |  |  | 15.2% | 76.8% | 41 |
| gate cell, shape 1 | 0.36 | 0.349 (0.313 to 0.385) | 0.97 |  |  |  | 14.8% | 77.1% | 61 |

All three reference arms sit above their prediction (ratios 1.24, 1.29, 1.33), inside the band but systematically. Expressed as added squared coefficient of variation, the multiplier delivers 0.694 to 0.705 of its nominal 1/shape, a fraction that is the same at all three shapes. **The likely reason, which the same table supports, is a ceiling on who is available to infect.** In the reference arms 40% to 43% of infections happen at home and only about 15% at the four social venue types, so a highly infectious episode is spent largely in a household, where the number of susceptible people is two or three; the tail of the multiplier is truncated by the size of the group it meets. The largest offspring count in those arms is 16 to 20. In the gate cells the same multiplier acts on a class that spends its time at large venues: 15% of infections at home and 77% at the four high-L types, and the largest offspring count rises to 30, 41 and 61. This is the complement of the round-8 finding. A venue scene supplies the opportunity (many susceptible people in one place) but little variation between people; a per-episode multiplier supplies the variation but, on its own, spends it in households where it cannot be expressed. Put together, each supplies what the other lacks, which is why the product rule works and why the combination is, if anything, slightly more dispersed than it predicts.

**The same ceiling explains the residual pattern across the whole grid.** Over all 15 arms the share of infections that happen at home correlates with the ratio of observed to predicted k at 0.87: the arms where the multiplier underdelivers are exactly the arms where its episodes are spent in households. The order runs from the reference arms (43% at home, ratio 1.24 to 1.33), through the no-class scene (23% at home, 1.07 to 1.16), to the tilted-class scenes (15% at home, 0.92 to 1.03) and the lambda 30 scene (6% at home, 1.00 to 1.03). Where almost no transmission is left at home, the product rule is exact.

A consequence for the rule as a design tool: using the nominal 1/shape is right when the multiplier acts on top of a scene, and optimistic when it acts alone. If the rule goes into the paper, the honest form is the nominal one with this caveat stated, rather than a refitted constant, because the discrepancy is not a constant of the multiplier but a property of where transmission happens.

### Zero share and the registered direction

Registered: the zero share rises with the multiplier, reaching at least 45% at tau 1 lambda 10 with shape 1, against 34.4% for that scene alone. Observed in that column: shape 3: 39.8% (39.3 to 40.3), shape 2: 42.0% (41.5 to 42.5), shape 1: 47.8% (47.0 to 48.7), against 34.4% for the scene alone (round 8). The direction is as registered and the shape-1 value meets the 45% threshold. At a matched mean of 1.4 the same arms give 47.7%, 51.1%, 57.0%.

### Interaction between the class and the multiplier

Note 52 asks whether the cells with a class show an interaction, that is whether class members with a high multiplier are also the ones at the high-L venues. Two checks:

1. **The draws are independent in practice.** The mean per-episode multiplier of infected class members, divided by that of infected others, runs from 0.9795 to 1 over the combined cells (prediction 1). There is no selection of high multipliers into the class, as the separate generators imply.
2. **The two sources act on the same people only by chance, and that is enough.** The mean offspring of index cases by class and by quartile of the multiplier is in `53_s9_summary.csv` (`mean_offspring_class_shed_q*` and `mean_offspring_others_shed_q*`). The class members in the top quartile of the multiplier are the arm's superspreaders; because the two draws are independent, they are about 5% of 25% of the eligible agents, and it is their rarity, not any correlation, that produces the tail. A correlated version (R9-3 item 2) would concentrate the two risks in the same people and is predicted to go further; it was not run (D2).

## 3. R9-2: assortative mixing in the round-8 scenes (existing traces, no new runs)

| arm | class to class | class to others | others to class | others to others | class share of infections caused | fraction of the class infected by day 28 | fraction of others infected | ratio | share of the class's infections from a class infector | offspring ratio r | r excluding class targets |
|---|---|---|---|---|---|---|---|---|---|---|---|
| s8_3_L10 | 41.5% | 39.2% | 2.8% | 16.6% | 80.6% | 36.7% | 2.3% | 15.8 | 93.7% | 90.6 | 44 |
| s8_2_t1_L30 | 20.5% | 40.2% | 5.9% | 33.5% | 60.7% | 21.5% | 2.9% | 7.3 | 77.8% | 33.6 | 22.2 |
| s8_2_t1_L10 | 16.4% | 33.6% | 5.9% | 44.1% | 50.0% | 18.8% | 3.2% | 5.89 | 73.6% | 21.8 | 14.6 |

The offspring ratio r here is the plain per-capita ratio (offspring per class agent over offspring per other agent). Round 8 reported the odds-ratio form of the same quantity (79.1, 29.3 and 19.0 for these three arms); both are in the CSV. **Answer to the question in note 52:** class-to-class transmission explains a large part of the ratio but not all of it. Counting only the infections the class causes in non-class agents, the ratio falls from 90.6 to 44.0 in S8-3 lambda 10, from 33.6 to 22.2 in S8-2 tau 1 lambda 30, and from 21.8 to 14.6 in S8-2 tau 1 lambda 10. Those remainders are still well above the weight predictions (8.1, 5.7 and 4.4), so the weight predictor fails for a second reason besides assortativity. The depletion that note 51 suspected is real and large: in S8-3 lambda 10 more than a third of the class is infected within four weeks while 2.3% of everyone else is, so the class's own susceptibles are running out while the epidemic is still being matched at day 28.

## 4. R9-3: the two small checks

| replicate | capTop day 84 | scaleAll day 84 | difference |
|---|---|---|---|
| 1 | 6448 | 6137 | -311 |
| 2 | 10195 | 10456 | 261 |
| 3 | 9974 | 10401 | 427 |
| 4 | 10386 | 10378 | -8 |
| 5 | 8686 | 8859 | 173 |
| 6 | 9213 | 8870 | -343 |
| 7 | 12631 | 12449 | -182 |
| 8 | 10398 | 10198 | -200 |
| 9 | 7423 | 7478 | 55 |
| 10 | 6425 | 6454 | 29 |
| 11 | 9333 | 9632 | 299 |
| 12 | 7842 | 7640 | -202 |

**They are not the same simulations.** No replicate pair is equal, the mean absolute difference is 207.5 infections and the two series correlate at 0.991 because they share seeds and, under the D2 quirk, are nearly the same intervention. The means are 9079.5 and 9079.3. With a per-replicate difference of standard deviation about 253, the standard error of the difference of means is about 73, so an agreement within 0.2 infections has probability of order 1 in 500. It is a coincidence, as note 51 suspected, and nothing depends on it: the cell stays marked unusable.

Item 2 (the correlated multiplier) was not run (D2).

## 5. Where the mechanisms stand

Updating the table of note 51 section 6 with this round:

| mechanism family | best k reached (moment) | what is missing |
|---|---|---|
| occupancy and crowding | 1.57 | cannot create overdispersion by itself |
| more mobile people (round 7) | 3.2 | bounded by a 24-hour day and unscaled home, school and work transmission |
| risk per hour by venue, tilted minority (round 8) | 0.85 | zero share about 40% against 59%; needs extreme contrasts |
| rare events (rounds 5 and 6) | near 0.3 | too few non-transmitters |
| per-person or per-episode infectiousness | 0.3 by construction | needs a biological or behavioural source |
| **venue scene plus per-episode multiplier (this round)** | **0.31** | **nothing on these three statistics; both ingredients remain assumptions, and the multiplier still needs a source** |

The gate cell reaches the real pattern with a scene that is one notch short on its own (k 1.13) and a multiplier that is milder than the one rounds 5 and 6 needed (shape 1, against 0.3). At a matched mean of 1.4 it gives a zero share of 57.0% and 21.1% of infectors causing 80%, against about 0.3 for k, about 59% zero, about 20% causing 80%, at a mean of 1.4.

## 6. In plain terms

1. **The headline for the paper changes shape.** Up to round 8 the finding was negative: no single mechanism reaches the observed superspreading pattern at plausible settings. Round 9 shows the positive counterpart: two moderate mechanisms of different kinds, one in where people go and one in how infectious an episode is, multiply rather than add, and together they land on the observed pattern. The composition rule says how much of each is needed, and it holds across a 12-cell grid.
2. **What it does not settle.** The per-episode multiplier is still an assumption with no source in the model, and the venue scene still needs a 5% minority spending 11 hours a day at venues ten times riskier per hour. The round says these are enough together, not that they are what happens.
3. **Why the weight predictor of round 8 failed is now partly answered.** Assortativity and depletion within the class account for roughly half the gap between the predicted and observed class offspring ratios; the rest is still open, and the burst-within-a-venue explanation remains untested.
4. **For control.** Nothing in this round changes the round-8 conclusion that targeting the most active pays off only when risk per hour differs between places. The combined arms concentrate transmission further, so the targeting case there is at least as strong.

## 7. Open points

1. R9-3 item 2, the correlated multiplier, is the obvious next cell and the only one I could not do with a flag (about half an hour).
2. The deviations from the rule are ordered by the home share of infections (correlation 0.87), so they are a property of where transmission happens, not a constant to be refitted. If the rule goes into the paper it should keep the nominal form with that caveat. What would test the explanation directly is an arm with the multiplier alone and household transmission suppressed; that is a closure rule and one run.
3. S8-3 is still outside the grid and its D2 quirk is unfixed; combining the strongest scene with a multiplier would go below the real k, which may be worth one cell as an upper bound on what the model can do.

## Files

`53_round9_results.md` (this note), `53a_review_of_note52.md`, `53_s9_summary.csv`, `53_s9_offspring.csv`, `53_r92_assortative_mixing.csv`, `53_r93_s83_cap_vs_scaleall_day84.csv`, `53_upload_index.md`. No file exceeds 1 MB.
