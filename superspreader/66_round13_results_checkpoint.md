# ACT-049 note 66: round 13 (noise and replication), results to the checkpoint

22 October 2026. Reply to note 65. Review of note 65 first: `66a_review_of_note65.md`. This file reports N0, N4 and N1 items 1 and 2 (the essential cells). **I stop at the checkpoint, as instructed: N1 item 3 (seed set 79001 to 79012), N2, N3 and N5 are not run.** Nothing was run beyond the cells listed here. Code: `study/run_round13.py` (cells), `study/analyze_round13.py` (N0, N4, statistics); binary `build_r10/panSim` (no C++ change); location and agent files untouched. Command lines, flags and dump options are those of round 12 (rebuilt and compared with the stored `command.json`); only the seed set and, for the calibrated cells, the background coefficient differ. Reporting rules as in note 65: likelihood k primary with moment k beside it, observed zero and 80% shares, 12 replicates, 90% intervals are replicate-level percentile bootstraps (1,000 resamples; they are intervals of the pooled statistic over replicates, not combined noise).

## Headline

1. **N0 done for everything on disk.** 94 matched arms of rounds 6 to 12 (1,096 replicates) plus 7 sixteen-week repeat-infection arms (56 replicates) are exported per replicate; nothing is gone. Pooled from the exported histograms the likelihood k, moment k and household attack rate of the four round-12 worlds reproduce the delivered values exactly.
2. **N4 done.** 20 draws per replicate, 4 worlds, 3 schemes, 2 rates. The standard deviation over draws of the pooled likelihood k is 0.005 to 0.028 (median 0.8 times the replicate-bootstrap standard error of the delivered table, range 0.46 to 1.39): thinning-draw noise is a sizeable part of, but not additional to, the replicate noise that is already in the 62_r122 intervals (the draws reuse the same 12 replicates). The round-12 point values lie inside the draw distributions.
3. **N1 items 1 and 2 done (eight cells).** In worlds 1, 2b and 2a the independently recalibrated seed set 78001 to 78012 agrees with the round-12 set: no difference exceeds 1.8 combined standard errors in any of the five statistics, and the between-set SD of likelihood k is 1.0 to 1.4 times the within-set standard error. In **world 3b the round-12 set (77001 to 77012) is the odd one out**: it differs from both other recalibrated sets, while the other two (68101 and 78001) agree with each other (|z| at most 1.3 in every statistic). The three recalibrated sets give likelihood k 0.330, 0.306 and 0.326 (round 6, round 12, round 13), zero share 52.3%, 54.4% and 52.9%, ratio 2.16, 1.95, 2.13, share causing 80% 18.1%, 16.8%, 17.8%, observed minus NB zero -4.4, -3.9 and -4.2 points.
4. **The excess in world 3b follows the calibrated coefficient, not the seeds.** On seed set 78001 to 78012 with the round-12 coefficient frozen (0.000130087) world 3b gives likelihood k 0.304 (round-12 set: 0.306), zero share 55.2% (54.4%), ratio 2.05 (1.95), 80% share 16.8% (16.8%), but the day-28 mean is 13.9% below the target. Recalibrating on 78001 to 78012 needs 0.000141382 (+8.7%) and moves every fingerprint to the round-6 values. So the fingerprints of world 3b are a function of the coefficient (the balance of background and event transmission) and the coefficient needed to reach day 28 depends on the seed set (0.000130, 0.000142, 0.000141). Size of that dependence: N2 would measure it; not run.
5. **The conclusions that the registered orderings support hold in every set** (prediction (c) below), and the ordering of the means across the three recalibrated world-3b sets is stable. The gap in likelihood k between world 3b and world 1 is 0.051 on the round-12 set and 0.019 on the 78001 set (about 2.4 combined bootstrap standard errors); the between-set range of world 3b (0.306 to 0.330) is of the same order as the gap, so "world 3b is 0.05 below the others" is not supported at that size by the recalibrated sets.

## Registered predictions of note 65, N1 (with 2 sets for worlds 1, 2b, 2a and 3 recalibrated sets for 3b; item 3 pending)

| prediction | outcome |
|---|---|
| (a) between-set SD of likelihood k above 2 times within-set SE for world 3b, at most 1.5 for worlds 1, 2b, 2a | **Holds, provisionally.** World 3b: SD over three recalibrated sets 0.0129 over mean bootstrap SE 0.0056 = 2.31 (round-12 vs round-13 set alone: 2.26). Worlds 1, 2b, 2a (two sets, 1 degree of freedom): 1.34, 1.01, 1.38. The 2-set SDs have extremely wide intervals; read as consistent, not as confirmed. |
| (b) freezing the coefficient cuts the world-3b zero-share difference to the round-12 set by at least half | **Fails narrowly.** Recalibrated 78001 set: zero share 52.9%, difference to round 12 -1.49 points. Frozen: 55.2%, difference +0.82 points: reduction 45% (threshold 50%, not changed). The frozen cell is on the other side of the round-12 value. Likelihood k (difference 0.020 to 0.001) and 80% share (1.07 to 0.07 points) are cut by more than half, the ratio (0.18 to 0.10) by 43%. |
| (c) every set: ratio of world 1 below worlds 2b and 2a below world 3b; world 3b lowest share causing 80%; observed minus NB zero below -2.5 points for world 3b and within 0.5 of zero for world 1 | **Holds in every cell** (round-12, recalibrated and frozen 78001 sets): ratios 1.04 to 1.06 < 1.41 to 1.50 < 1.95 to 2.13; world 3b 80% share 16.8 to 17.8% against 20.4 to 21.7% for the others; world 3b gap -3.8 to -4.2 points; world 1 gap -0.01 to +0.04. In s78 recalibrated 2b (1.47) is above 2a (1.41), the reversal allowed in the note. The 2b/2a ratio intervals overlap in every set. |
| (d) likelihood k of world 3b below that of world 1 in at least three of four sets | **Holds so far.** World 1 exists on 2 sets only: 3b is below world 1 in both (0.306 < 0.357 and 0.326 < 0.345); the round-6 set (0.330) is below the mean of the two world-1 sets (0.351). The gap shrinks from 0.051 (round-12 set) to 0.019 (78001 set). Four sets for world 3b need item 3 for world 1. |

Registered by the runner in note 66a (before results): (i) the frozen coefficient misses the 3% window on 78001 to 78012 for at least one world: **holds** (w2a -7.0%, w2b -9.9%, w3b -13.9%; world 1 +1.7%). (ii) frozen day 28 within 8% for every world: **fails** (w2b -9.9%, w3b -13.9%).

## Checkpoint quantities (note 65 definition)

Between-set standard deviation (two sets: |difference| over square root of 2) against the within-set standard error (mean of the two replicate-bootstrap SDs); file `66_n1_checkpoint_pairs.csv` has all comparisons including frozen cells.

By your rule item 3 runs: world 3b exceeds 1.2 times the within-set SE in all five statistics (2.3 to 3.1 against the round-12 set), outside world 3b it is exceeded for world 1 (likelihood k 1.34, share causing 80% 1.80), world 2b (share 80% 1.56) and world 2a (k 1.38, share 80% 1.34). Because 16 to 20 two-set comparisons each have one degree of freedom, a pass of all of them is not an attainable outcome even without between-set variance (see 66a, point 4). Pooled over worlds 1, 2b and 2a (root mean square of the ratio, 3 worlds per statistic): likelihood k 1.26, zero share 0.51, ratio 0.68, share causing 80% 1.58, observed minus NB zero 0.60; all fifteen 1.01.

| world | comparison | statistic | first | second | difference | z (combined SE) | between-set SD / within-set SE |
|---|---|---|---|---|---|---|---|
| w1 | s77_cal vs s78_cal | likelihood k | 0.357 | 0.345 | -0.012 | -1.3 | 1.34 |
| w1 | s77_cal vs s78_cal | zero share | 56.588 | 56.640 | +0.052 | +0.1 | 0.10 |
| w1 | s77_cal vs s78_cal | ratio | 1.057 | 1.043 | -0.014 | -0.3 | 0.29 |
| w1 | s77_cal vs s78_cal | share causing 80% | 21.548 | 20.958 | -0.590 | -1.8 | 1.80 |
| w1 | s77_cal vs s78_cal | obs. minus NB zero | 0.042 | -0.015 | -0.057 | -0.5 | 0.48 |
| w2b | s77_cal vs s78_cal | likelihood k | 0.365 | 0.355 | -0.011 | -1.0 | 1.01 |
| w2b | s77_cal vs s78_cal | zero share | 53.538 | 53.769 | +0.231 | +0.4 | 0.37 |
| w2b | s77_cal vs s78_cal | ratio | 1.420 | 1.471 | +0.052 | +0.9 | 0.88 |
| w2b | s77_cal vs s78_cal | share causing 80% | 21.721 | 21.083 | -0.638 | -1.6 | 1.56 |
| w2b | s77_cal vs s78_cal | obs. minus NB zero | -1.057 | -1.196 | -0.139 | -0.9 | 0.88 |
| w2b | s77_cal vs s78_frozen | likelihood k | 0.365 | 0.353 | -0.012 | -1.0 | 1.02 |
| w2b | s77_cal vs s78_frozen | zero share | 53.538 | 54.338 | +0.800 | +1.1 | 1.19 |
| w2b | s77_cal vs s78_frozen | ratio | 1.420 | 1.484 | +0.065 | +1.2 | 1.16 |
| w2b | s77_cal vs s78_frozen | share causing 80% | 21.721 | 21.095 | -0.626 | -1.3 | 1.34 |
| w2b | s77_cal vs s78_frozen | obs. minus NB zero | -1.057 | -1.127 | -0.070 | -0.5 | 0.48 |
| w2a | s77_cal vs s78_cal | likelihood k | 0.355 | 0.337 | -0.018 | -1.4 | 1.38 |
| w2a | s77_cal vs s78_cal | zero share | 52.847 | 53.443 | +0.596 | +0.8 | 0.80 |
| w2a | s77_cal vs s78_cal | ratio | 1.502 | 1.411 | -0.091 | -0.7 | 0.72 |
| w2a | s77_cal vs s78_cal | share causing 80% | 21.098 | 20.373 | -0.725 | -1.3 | 1.34 |
| w2a | s77_cal vs s78_cal | obs. minus NB zero | -1.286 | -1.231 | +0.055 | +0.3 | 0.28 |
| w2a | s77_cal vs s78_frozen | likelihood k | 0.355 | 0.336 | -0.020 | -1.5 | 1.47 |
| w2a | s77_cal vs s78_frozen | zero share | 52.847 | 53.894 | +1.048 | +1.4 | 1.37 |
| w2a | s77_cal vs s78_frozen | ratio | 1.502 | 1.423 | -0.079 | -0.6 | 0.61 |
| w2a | s77_cal vs s78_frozen | share causing 80% | 21.098 | 20.369 | -0.729 | -1.3 | 1.34 |
| w2a | s77_cal vs s78_frozen | obs. minus NB zero | -1.286 | -1.218 | +0.068 | +0.3 | 0.34 |
| w3b | s77_cal vs s78_cal | likelihood k | 0.306 | 0.326 | +0.020 | +2.2 | 2.26 |
| w3b | s77_cal vs s78_cal | zero share | 54.383 | 52.898 | -1.485 | -2.9 | 2.94 |
| w3b | s77_cal vs s78_cal | ratio | 1.950 | 2.130 | +0.180 | +2.7 | 2.70 |
| w3b | s77_cal vs s78_cal | share causing 80% | 16.763 | 17.835 | +1.072 | +2.4 | 2.38 |
| w3b | s77_cal vs s78_cal | obs. minus NB zero | -3.895 | -4.238 | -0.342 | -3.1 | 3.10 |
| w3b | s77_cal vs s68_cal | likelihood k | 0.306 | 0.330 | +0.024 | +3.0 | 3.05 |
| w3b | s77_cal vs s68_cal | zero share | 54.383 | 52.285 | -2.098 | -3.8 | 3.79 |
| w3b | s77_cal vs s68_cal | ratio | 1.950 | 2.165 | +0.215 | +3.5 | 3.52 |
| w3b | s77_cal vs s68_cal | share causing 80% | 16.763 | 18.075 | +1.311 | +3.1 | 3.18 |
| w3b | s77_cal vs s68_cal | obs. minus NB zero | -3.895 | -4.362 | -0.467 | -4.1 | 4.14 |
| w3b | s77_cal vs s78_frozen | likelihood k | 0.306 | 0.304 | -0.001 | -0.1 | 0.14 |
| w3b | s77_cal vs s78_frozen | zero share | 54.383 | 55.205 | +0.822 | +1.6 | 1.64 |
| w3b | s77_cal vs s78_frozen | ratio | 1.950 | 2.053 | +0.103 | +1.4 | 1.40 |
| w3b | s77_cal vs s78_frozen | share causing 80% | 16.763 | 16.835 | +0.072 | +0.1 | 0.15 |
| w3b | s77_cal vs s78_frozen | obs. minus NB zero | -3.895 | -3.813 | +0.083 | +0.7 | 0.69 |

(The world-1 comparison against the frozen cell is identical to the recalibrated one, because the cells are the same configuration; omitted here, present in the CSV.)


## Cells of N1 items 1 and 2 (and the existing sets for reference)

| world | seed set, coefficient | coefficient | day 28 vs 6,211.25 | early R | likelihood k (90% rep. bootstrap) | moment k | ratio (90%) | zero share % | obs. minus NB zero, points (90%) | share causing 80% % (90%) | home share % | hh SAR | top-10 same-hh % | top-10 venue-day % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| World 1 | 77001-77012 (round 12) | 0.0004992 | +1.3% | 1.405 | 0.357 (0.346 to 0.369) | 0.338 | 1.06 (0.98 to 1.15) | 56.6 | 0.04 (-0.11 to 0.19) | 21.5 (21.1 to 22.0) | 34.2 | 0.00165 | 17.7 | 19.8 |
| World 1 | 78001-78012, recalibrated | 0.0004992 | +1.7% | 1.445 | 0.345 (0.335 to 0.354) | 0.331 | 1.04 (1.01 to 1.08) | 56.6 | -0.01 (-0.12 to 0.11) | 21.0 (20.6 to 21.3) | 34.0 | 0.00159 | 15.5 | 19.6 |
| World 1 | 78001-78012, frozen | 0.0004992 | +1.7% | 1.445 | 0.345 (0.335 to 0.354) | 0.331 | 1.04 (1.01 to 1.08) | 56.6 | -0.01 (-0.12 to 0.11) | 21.0 (20.6 to 21.3) | 34.0 | 0.00159 | 15.5 | 19.6 |
| World 2b | 77001-77012 (round 12) | 0.0001172 | -0.2% | 1.550 | 0.365 (0.354 to 0.378) | 0.257 | 1.42 (1.35 to 1.48) | 53.5 | -1.06 (-1.21 to -0.90) | 21.7 (21.2 to 22.2) | 14.1 | 0.00083 | 6.5 | 14.5 |
| World 2b | 78001-78012, recalibrated | 0.0001199 | -0.2% | 1.563 | 0.355 (0.341 to 0.367) | 0.241 | 1.47 (1.40 to 1.54) | 53.8 | -1.20 (-1.40 to -0.98) | 21.1 (20.6 to 21.6) | 14.0 | 0.00087 | 6.7 | 14.2 |
| World 2b | 78001-78012, frozen | 0.0001172 | -9.9% | 1.521 | 0.353 (0.337 to 0.369) | 0.238 | 1.48 (1.42 to 1.55) | 54.3 | -1.13 (-1.30 to -0.95) | 21.1 (20.5 to 21.7) | 14.1 | 0.00082 | 6.8 | 14.7 |
| World 2a | 77001-77012 (round 12) | 4.294e-05 | +0.3% | 1.644 | 0.355 (0.340 to 0.373) | 0.236 | 1.50 (1.30 to 1.68) | 52.8 | -1.29 (-1.51 to -1.04) | 21.1 (20.5 to 21.7) | 6.0 | 0.00041 | 3.3 | 14.7 |
| World 2a | 78001-78012, recalibrated | 4.369e-05 | +1.4% | 1.683 | 0.337 (0.324 to 0.350) | 0.239 | 1.41 (1.32 to 1.52) | 53.4 | -1.23 (-1.44 to -1.00) | 20.4 (19.7 to 21.0) | 5.9 | 0.00045 | 4.1 | 13.9 |
| World 2a | 78001-78012, frozen | 4.294e-05 | -7.0% | 1.645 | 0.336 (0.321 to 0.350) | 0.236 | 1.42 (1.32 to 1.53) | 53.9 | -1.22 (-1.42 to -0.98) | 20.4 (19.7 to 20.9) | 5.9 | 0.00042 | 4.1 | 14.2 |
| World 3b | 68101-68112 (round 6) | 0.0001422 | +0.2% | 1.518 | 0.330 (0.323 to 0.337) | 0.152 | 2.16 (2.10 to 2.23) | 52.3 | -4.36 (-4.49 to -4.24) | 18.1 (17.7 to 18.4) | 22.6 | 0.00190 | 3.9 | 88.2 |
| World 3b | 77001-77012 (round 12) | 0.0001301 | +1.3% | 1.482 | 0.306 (0.295 to 0.317) | 0.157 | 1.95 (1.88 to 2.03) | 54.4 | -3.90 (-4.03 to -3.77) | 16.8 (16.2 to 17.4) | 21.3 | 0.00148 | 2.9 | 91.5 |
| World 3b | 78001-78012, recalibrated | 0.0001414 | -0.8% | 1.491 | 0.326 (0.317 to 0.335) | 0.153 | 2.13 (2.06 to 2.21) | 52.9 | -4.24 (-4.36 to -4.12) | 17.8 (17.4 to 18.3) | 22.5 | 0.00126 | 4.3 | 91.1 |
| World 3b | 78001-78012, frozen | 0.0001301 | -13.9% | 1.417 | 0.304 (0.296 to 0.314) | 0.148 | 2.05 (1.97 to 2.15) | 55.2 | -3.81 (-3.96 to -3.68) | 16.8 (16.4 to 17.5) | 21.8 | 0.00105 | 4.5 | 91.3 |

In world 1 the round-12 coefficient is already within 3% on seed set 78001 to 78012 (+1.7%), so the recalibrated and the frozen cell are the same configuration; both cells have identical results to the last digit, which confirms that the simulator is deterministic for identical inputs and seeds. The round-10 repeat-infection run of world 1 on seed 78001 differs from the new run on the same seed and coefficient already in the first week; those runs carry other flags (vaccination off, episode trace, 16 weeks); I did not trace which one changes the random stream.

Calibration logs for the 78001 set (every iteration; the first row of each cell is the 4-replicate pilot as in round 12):

| cell | iteration | coefficient | day-28 mean | replicates | pilot | chosen |
|---|---|---|---|---|---|---|
| w1:s78_cal | 1 | 0.000499174 | 6516.5 | 4 | True | False |
| w1:s78_cal | 2 | 0.000499174 | 6318.6 | 12 | False | True |
| w2a:s78_cal | 1 | 4.29375e-05 | 5848.8 | 4 | True | False |
| w2a:s78_cal | 2 | 4.29375e-05 | 5775.5 | 12 | False | False |
| w2a:s78_cal | 3 | 4.50709e-05 | 7067.3 | 12 | False | False |
| w2a:s78_cal | 4 | 4.36944e-05 | 6295.5 | 12 | False | True |
| w2b:s78_cal | 1 | 0.000117185 | 6046.2 | 4 | True | False |
| w2b:s78_cal | 2 | 0.000117185 | 5593.4 | 12 | False | False |
| w2b:s78_cal | 3 | 0.000125663 | 7671.5 | 12 | False | False |
| w2b:s78_cal | 4 | 0.000119931 | 6196.2 | 12 | False | True |
| w3b:s78_cal | 1 | 0.000130087 | 5174.0 | 4 | True | False |
| w3b:s78_cal | 2 | 0.000146939 | 6144.5 | 4 | True | False |
| w3b:s78_cal | 3 | 0.000146939 | 6735.8 | 12 | False | False |
| w3b:s78_cal | 4 | 0.000139208 | 6012.2 | 12 | False | False |
| w3b:s78_cal | 5 | 0.000141382 | 6160.2 | 12 | False | True |

## N0 files

- `66_n0_replicate_histograms.csv` (18,173 rows): arm, seed, replicate, offspring_total, offspring_at_events (blank where the arm has no event log), index_cases. Arm names are `round<r>:<state file name>`.
- `66_n0_replicate_summary.csv` (1,152 rows, 101 arms): per replicate the columns requested; event columns for the closed-group arms (events_total, events_with_infectious, event_infections, event_offspring_share) and, for the older venue-day boost arms, the number of distinct event venue-days and the event offspring share; `top1pct_*` columns use the pooled top 1% of the arm (exactly round(1%) of the pooled index cases, ties broken by a fixed random order; the smallest included offspring count is `top1pct_threshold_pooled`). Day 56, 84 and 112 are filled only for the 16-week arms. The three ward-split arms (`r65_*`, another agent file) have no household columns.
- `66_n0_repeat_pairs_by_replicate.csv` (66,477 rows): arm, seed, replicate, agent, first and second infection day and offspring; the pair counts of note 64 are reproduced (11,877; 5,285; 3,459).

## N4 files

`66_n4_thinning_draws.csv` (5,760 rows: per replicate and draw), `66_n4_thinning_draws_pooled.csv` (480 rows: each draw pooled over the 12 replicates, the Table 5.17a statistics), `66_n4_noise_summary.csv` (draw SD against the replicate standard error of the delivered table). Random numbers per replicate, scheme, rate and draw are fixed (generator key: 13, replicate, scheme, rate, draw), so worlds are thinned with the same stream of random numbers (not the same agents).

## What is not done and why

N1 item 3, N2, N3, N5: the note asks for the checkpoint first. The eight cells above took about 55 minutes of wall clock in total (calibrations and frozen cells of the four worlds in parallel); N1 item 3, N2 and N3 would each take of the order of one hour, and I can run them on your word.

## Code and data changes

No C++ change. New files: `study/run_round13.py`, `study/analyze_round13.py`, results under `study/results/round13/` (traces, states). Git commits use a repository-local identity argument; no config was changed.
