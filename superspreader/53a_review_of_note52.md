# ACT-049 note 53a: review of note 52 before the round-9 arms

18 October 2026. Written after removing the blocking check, verifying the new binary, and running the two checks that need no new simulation (R9-2 and R9-3, whose results are in `53_round9_results.md`), and before any round-9 infection arm. The location and agent files are not edited. Binary `build_r9`.

## Verification already done

1. **The one-line change.** In `initializeArgs` (`movementPolicies.h`) the combined check now blocks only `--traitShape`:
   `if ((hviMode != "off" || hviRotateFraction > 0.0) && result["traitShape"].as<double>() > 0.0) throw ...`.
   The `--traitShape` case stays blocked, as note 52 asks, because a persistent per-agent trait and the HVI class would both be per-agent and the combination would need a stated rule for how they multiply.
2. **T1 passed, in the strong form.** I reran the first replicate of three round-8 arms (`s8_1_L10`, `s8_2_t1_L10`, `s8_3_L10`) on `build_r9` with the same command line and no shedding flag. The infection trace, the HVI dump and the daily table are byte-identical to the round-8 files in all three (the stdout differs only in the timing profile lines).
3. **Independence of the two draws, structurally.** The class assignment is drawn on the host at initialisation from its own `mt19937_64`, seeded from the run seed and the agent id (note 46 D8); the per-episode multiplier is drawn in the device kernel at the moment of infection (`locationList.h`, `gammaMeanOne(sheddingShape)`). Adding `--sheddingShape 2` to the three arms above leaves `hvi.csv` byte-identical, so the class assignment does not depend on the shedding option. The epidemic of course differs, so the trace differs. I will also report the realised mean multiplier of infected class members against infected others in every combined arm, as the empirical check; the structural argument predicts a ratio of 1.

## Points on note 52

1. **The composition arithmetic is right.** All 12 rows of `51_round9_composition_predictions.csv` reproduce: for `s8_2_t1_L10` with shape 2, (1 + 1/1.128)(1 + 1/2) = 1.8865 x 1.5 = 2.830, so k = 1/1.830 = 0.547, the 0.55 in the file. The reference values (1 + 1/4.59)(1 + 1/shape) give 1.60, 1.21 and 0.70. No error found.
2. **The rule is a statement about the squared coefficient of variation of expected offspring, and the arms do not share a mean.** The round-8 scenes have early R from 1.41 to 2.03 at a matched day 28, and the combined arms will differ again. For a discrete distribution the moment k at one mean is not the same summary as at another, which is why the predictions can be met or missed partly through the mean. I will score the prediction on the raw moment k as the note specifies, and report the matched-mean table (negative binomial at mean 1.4, as `51_round8_matched_mean_shares.csv`) beside it. My reproduction of that table agrees with note 51 to four decimals on all six arms, so the two sides are computing the same thing.
3. **The zero-share prediction is at the arm's own mean.** "At tau 1 lambda 10 with shape 1, zero share at least 45%, against 34.4% for the scene alone" compares two arms whose means differ (the scene alone has early R 1.58). I will report the observed zero share, the negative-binomial zero share at both estimators, and the matched-mean value, and score the prediction as written on the observed share.
4. **The strongest round-8 scene is not in the grid.** The four scenes are S8-1 lambda 10 and the three S8-2 cells; S8-3 (moment k 0.846) is excluded, which I take to be deliberate given the D2 quirk. The consequence is that the lowest combined k reachable in this round is bounded by the S8-2 tau 1 lambda 30 column (predicted 0.30 at shape 1), not by the lowest scene available.
5. **R9-3 item 2 (correlated multiplier) needs code beyond a flag, so I skip it as instructed.** The per-episode draw happens inside `infectAgents` in `locationList.h`, which receives the shedding shape as a scalar and has no access to the HVI class array held by the movement policy. Giving the draw a class-dependent mean means passing that array (or a per-agent mean multiplier) through `infectAgents`, about ten lines across two headers, plus a rebuild. If you want it, it is roughly half an hour including the run.
6. **Timing, as asked.** A calibration round is 12 runs of about 15 seconds, and an arm takes three to five rounds plus the pilot, so about 10 minutes per arm. The full R9-1 grid (12 cells plus 3 reference arms) is therefore about **2.5 hours**, above the two-hour mark the note asks me to flag. The gating column (3 cells) is about 30 minutes. I am running the gating column and the reference arms first, as the note orders, and will continue into the remaining nine cells unless the rule fails by more than a factor 1.5 there.
7. **A small inconsistency in the order of work.** The note says to run the tau 1 lambda 10 column first and then, if the rule holds there, "the other nine cells and the reference arms", but the reference arms are also what the rule is calibrated against (shedding alone at shapes 3, 2, 1). If the gating column fails, the references are what distinguishes "the composition rule is wrong" from "the shedding multiplier does not behave as in earlier rounds". I therefore run the three reference arms together with the gating column, not after it.

## Predictions as registered (note 52, `51_round9_composition_predictions.csv`)

Predicted moment k, acceptance 0.7 to 1.4 times predicted:

| scene | observed scene k (round 8) | shape 3 | shape 2 | shape 1 |
|---|---|---|---|---|
| S8-1 lambda 10 (no class) | 2.936 | 1.27 | 0.99 | 0.59 |
| S8-2 tau 0.5 lambda 10 | 1.442 | 0.79 | 0.65 | 0.42 |
| S8-2 tau 1 lambda 10 (gate) | 1.128 | 0.66 | 0.55 | 0.36 |
| S8-2 tau 1 lambda 30 | 0.849 | 0.53 | 0.44 | 0.30 |
| shedding alone, no scene | 4.59 (baseline) | 1.60 | 1.21 | 0.70 |

Also registered: the zero share rises with the multiplier, reaching at least 45% at tau 1 lambda 10 with shape 1 (34.4% for that scene alone); and, if the rule fails, a statement of the direction and of whether the cells with a class show an interaction between the class and the multiplier.
