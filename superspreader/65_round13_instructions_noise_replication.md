# ACT-049 note 65: instructions for round 13 (noise, replication and sensitivity)

22 October 2026. Reply to the question of how noise in inputs and results is handled in paper v8 (reading: note 64). Results go to Drive with prefix `66_`, main file `66_round13_results.md`, with a short review of this note first (`66a_review_of_note65.md`: please say where these instructions are wrong or unworkable, as in earlier rounds). Reporting rules unchanged: likelihood k primary with moment k beside it, observed zero and 80% shares (not projections), 12 replicates unless stated, day 28 within 3% of 6,211.25, failed predictions reported as failed, no edits of the location and agent files. Use the exact command lines, flags and cell definitions of round 12 (note 61 and `62_r121_*`) for worlds 1, 2b, 2a and 3b, changing only what is stated below. Report any code change, even an export.

**Why this round.** Note 64 shows that (i) the delivered intervals are reasonable for sampling noise within one seed set, (ii) world 3b run on two independent seed sets (68101 to 68112 and 77001 to 77012, each with its own calibration) differs by 2.9 and 3.6 combined standard errors in likelihood k and zero share, with calibrated coefficients 0.000142 and 0.000130, and (iii) the paper reports no interval at all for the estimator ratio, the share causing 80%, observed minus negative binomial zero share, cluster composition, home share, household attack rate, top 1% profiles or any thinning result. The aim is to measure the noise that the delivered files do not contain, not to open new mechanisms.

## Phase 1: no new simulation (do first)

**N0. Replicate-level exports.** For every arm of rounds 6 to 12 whose traces are still on disk (priority: the four worlds of round 12, then the arms of Tables 5.15a and 5.15b, then rounds 7 and 8; say what is gone), write three files:

1. `66_n0_replicate_histograms.csv`: arm, seed, replicate, offspring_total, offspring_at_events (if applicable), index_cases (one row per offspring count per replicate).
2. `66_n0_replicate_summary.csv`: one row per arm and replicate: seed, background_coefficient, day 28, 56, 84 and 112 cumulative infections where run, early R, index cases, mean offspring, moment k, likelihood k (per replicate, noisy but needed), zero share, share causing 80%, the infection shares by place used in Table 5.16b (home, school and work, four high-risk types, hospital), household secondary attack numerator and denominator, largest offspring, mean over that replicate's ten largest clusters of: offspring, same-household share, largest venue-day share, distinct venues; number of top 1% infectors by agent type (using the pooled top 1% threshold of the arm, stated), events_total, event infections and event offspring share where applicable.
3. `66_n0_repeat_pairs_by_replicate.csv` for the arms with repeat infection data (round 11): replicate, first-infection offspring, second-infection offspring, one row per pair.

**N4. Thinning-draw noise.** For the four worlds on seeds 77001 to 77012 and the schemes of round 12 (random, household clustered with infectee and coupled variants if available) at 60% and 30%, repeat the thinning with 20 independent draws per replicate, using the stored traces (no simulation). Write `66_n4_thinning_draws.csv`: arm, scheme, rate, replicate, draw, and the statistics of Table 5.17a (both k, ratio, observed minus negative binomial zero, same-household share and venue-day share of the ten largest detected clusters). I will separate draw noise from replicate noise.

## Phase 2: independent seed sets (the central measurement)

**N1. Between-seed-set variance.** For worlds 1, 2b, 2a and 3b (parameters exactly as round 12):

1. Seed set 78001 to 78012: calibrate the background coefficient independently to day 28 (within 3% of 6,211.25) on that seed set, then measure. Log every calibration iteration (coefficient and day-28 mean).
2. Same seed set 78001 to 78012 with the coefficient frozen at the round-12 value for that world (no recalibration). Report day 28 as it falls.
3. After the checkpoint below, seed set 79001 to 79012, independently calibrated, as in item 1.

Write N0-style per-replicate files for every cell (`66_n1_*`) plus the usual summary. World 3b already has two independent recalibrated sets (68101 and 77001), so it will have four.

**Checkpoint after items 1 and 2** (upload and tell me before item 3): I compute the between-set standard deviation of likelihood k, zero share, ratio and share causing 80% against the within-set standard errors. If between-set SD is at most 1.2 times the within-set standard error for all worlds and statistics, item 3 is skipped.

**Registered predictions for N1** (written before running; thresholds will not be changed). (a) Between-set SD of likelihood k exceeds 2 times the within-set standard error (half-width of the delivered 90% interval divided by 1.645) for world 3b, and is at most 1.5 times for worlds 1, 2b and 2a. (b) Freezing the coefficient cuts the between-set difference in world 3b zero share, relative to the round-12 set, by at least half. (c) In every seed set the ordering of the estimator ratio is world 1 below worlds 2b and 2a below world 3b (2b against 2a may reverse), world 3b has the lowest share causing 80%, and observed minus negative binomial zero share is below -2.5 points for world 3b and within 0.5 of zero for world 1. (d) Likelihood k of world 3b stays below that of world 1 in at least three of its four sets.

## Phase 3: sensitivity (after the checkpoint)

**N2. Calibration sensitivity.** For each of the four worlds on seeds 77001 to 77012, run with the round-12 coefficient multiplied by 0.9 and by 1.1, no recalibration. Report day 28, early R, both k, ratio, zero share, share causing 80%, home share, same-household and venue-day shares of the ten largest clusters. The aim is the local derivative of each fingerprint with respect to the coefficient, which converts the 3% calibration window into an uncertainty. If time is short, use 8 replicates (state it) or drop worlds 2a and 2b (they share a mechanism).

**Registered prediction (exploratory; thresholds mine).** A 10% change in the coefficient moves likelihood k by less than 0.02 in worlds 1, 2a and 2b and by more than 0.03 in world 3b.

**N3. The target band.** The literature interquartile range of k is 0.20 to 0.51 (Section 3.2), and the worlds were tuned to 0.35 only. For worlds 1, 2b and 3b, retune one parameter to give likelihood k of 0.20 and of 0.50 (world 1: multiplier shape; world 2b: multiplier shape with the venue factor fixed at 10; world 3b: event rate with factor 3000 and group size 30 fixed), using at most three secant iterations of 6 replicates on a calibration seed set (76001 to 76006), then run 12 replicates on seeds 77001 to 77012 with day 28 recalibrated. Report the tuned parameter, both k, ratio, zero share, share causing 80%, home share and the ten-largest-cluster composition. Six final cells plus calibration.

**Registered predictions for N3.** (a) The ordering of the ratio (world 1 lowest, world 3b highest) holds at both targets. (b) World 1 stays below a ratio of 1.15 at both targets. (c) World 3b stays at least 3 points below the negative binomial zero share at k 0.20 and at k 0.50 (exploratory: I do not know whether it vanishes at 0.50).

## Phase 4: optional

**N5. One more realisation of the fixed inputs.** Redraw the per-agent venue lists (restaurants, long shops, churches, parks) with a different seed, same quotas, and rerun worlds 1, 2b and 3b on seeds 77001 to 77012 (recalibrated). The aim is to see whether the fingerprints depend on the one venue assignment used so far. **Prediction:** each fingerprint falls inside the range spanned by the N1 seed sets. Do this only if time remains; say how the lists were redrawn.

## Order, cost and what to drop

Order: N0, N4, then N1 items 1 and 2 (8 cells), checkpoint, then N1 item 3, N2, N3, N5. From round 12 (3 to 4 runs in about 1.5 hours) I estimate N1 items 1 and 2 at about 3.5 hours and the full round at about 12 hours; please correct this. If the round must be cut, drop in this order: N5, N3, N2 for worlds 2a and 2b, N1 item 3. N0, N4 and N1 items 1 and 2 are the essential ones. If N0 is impossible for old rounds, do it for rounds 10 to 12 and say so.

## What I will do with it

Variance components (within seed set, between seed set, calibration, thinning draw) for each fingerprint; intervals that combine them; paired (common seed) differences between worlds; a seed-set figure; and a revised Section 5.16 with the conclusions stated at the strength the noise supports. Unless this shows that a matched-world conclusion fails, no further rounds are planned.
