# ACT-049 note 66: round 13 (noise, replication and sensitivity), results

22 October 2026. Reply to note 65. Review of note 65: `66a_review_of_note65.md`. The first report to the checkpoint is kept as `66_round13_results_checkpoint.md`; this file replaces it and adds N1 item 3, N2, N3 and N5 (run after your go-ahead). Code: `study/run_round13.py` (cells, N2, N3, N5), `study/analyze_round13.py` (N0, N4, statistics), `study/build_r13_inputs.py` (N5 venue lists); binary `build_r10/panSim`, no C++ change; location and agent files untouched (N5 writes a new agent file). Command lines, flags and dump options of worlds 1, 2b, 2a and 3b are those of round 12. Reporting rules as in note 65: likelihood k primary, moment k beside it, observed zero share and 80% share, 12 replicates unless stated, day 28 within 3% of 6,211.25 for calibrated cells, failed predictions reported as failed. 90% intervals are replicate-level percentile bootstraps (1,000 resamples) of the pooled statistic; they contain neither between-set nor calibration variance.

## Headline

1. **Between seed sets (N1, 3 sets for worlds 1, 2b, 2a; 4 sets for world 3b).** For worlds 1, 2b and 2a the between-set SD equals the within-set standard error for likelihood k (SD over SE 1.06, 0.68, 1.00) and for the other four statistics (0.2 to 1.6; pooled over the three worlds 0.5 to 1.2): the delivered intervals are about right for these worlds. For world 3b the between-set SD exceeds the within-set SE in all five statistics (1.9 to 2.3): likelihood k 0.330, 0.306, 0.326, 0.321 (SD 0.011, SE 0.006), zero share 52.3, 54.4, 52.9, 52.9 %, ratio 2.17, 1.95, 2.13, 2.04, share causing 80% 18.1, 16.8, 17.8, 17.4 %, observed minus NB zero -4.4, -3.9, -4.2, -4.2 points. One set (round 12, 77001 to 77012) carries the excess; the other three agree within noise.
2. **The excess follows the calibrated coefficient (N1 item 2 and N2).** World 3b needs 0.000130, 0.000142, 0.000141 and 0.000137 on the four sets (9% range); the fingerprints move with it. N2 gives the slope: for a change of 10% in the coefficient (0.9 against 1.1, 12 replicates each) world 3b likelihood k changes by 0.052 (SE 0.011) over the 20% span, zero share by -5.0 points, ratio by +0.22, share causing 80% by +2.8 points; the prediction from this slope for the three other sets (0.306 + 0.26 times the log coefficient ratio) is 0.328, 0.319, 0.329 for sets 78, 79 and 68 against 0.326, 0.321, 0.330 observed. With the round-12 coefficient frozen on 78001 to 78012 world 3b reproduces the round-12 fingerprints (likelihood k 0.304) and misses day 28 by -13.9%. Worlds 1, 2b and 2a are nearly flat in likelihood k (central change over the 20% span 0.000, 0.006, 0.015) but their zero share falls by 2.9 to 3.9 points, because early R rises.
3. **Calibration window.** Day 28 is steep in the coefficient (about -29% to -36% at 0.9 and +39% to +48% at 1.1 in worlds 1, 2a, 2b; -16% and +19% in world 3b), so the 3% window corresponds to about 1% in the coefficient in worlds 1, 2a, 2b and 1.7% in world 3b. The window itself moves world 3b likelihood k by about 0.003 to 0.005; it does not explain the 0.024 between sets. What explains it is that the coefficient needed for day 28 differs by 9% between seed sets.
4. **Target band (N3).** All three mechanisms can be tuned to likelihood k 0.17 to 0.54 (achieved on 12 replicates: world 1 0.19 and 0.54; world 2b 0.17 and 0.48; world 3b 0.21 and 0.52). The ordering of the ratio is world 1 below world 2b below world 3b at k 0.5 (1.09, 1.48, 2.72) but **not** at k 0.2 (1.08, 1.55, 1.26: world 2b is above world 3b). World 1 stays below 1.15 at both. World 3b's observed minus NB zero is -5.4 points at k 0.5 and -1.9 at k 0.2 (against -3.9 at k 0.31): the deficit is not a constant of the mechanism.
5. **Venue lists (N5).** Redrawing the per-agent venue lists (shuffle within 2 km home cells, same counts) and recalibrating moves the fingerprints by at most 1.3 combined standard errors (likelihood k -0.007, +0.001, -0.002 in worlds 1, 2b, 3b), but the stated prediction (each fingerprint inside the range of the N1 sets) fails for 14 of the 24 checks, because the N1 ranges of worlds 1 and 2b are very narrow.
6. **Noise that was missing from the paper (summary).** Thinning-draw SD is 0.5 to 1.4 times the replicate standard error of likelihood k (N4). Between-set noise is as large as within-set noise in worlds 1, 2b, 2a and about twice as large in world 3b. The ordering of the ratio, the 80% share and the zero-share deficit of world 3b (world 1 below worlds 2b and 2a below world 3b at the matched k of 0.35) holds in every set; it does not hold at k 0.2 for the ratio, and the world-3b deficit at k 0.2 is only -1.9 points.

## Registered predictions of note 65 (thresholds unchanged)

| prediction | outcome |
|---|---|
| N1 (a) between-set SD of likelihood k above 2 times within-set SE for world 3b, at most 1.5 for worlds 1, 2b, 2a | **Fails narrowly for world 3b** (SD over SE 1.90 with 4 sets; 2.31 with the first 3; the other four statistics of world 3b give 2.1 to 2.3); **holds for worlds 1, 2b, 2a** (1.06, 0.68, 1.00). |
| N1 (b) freezing the coefficient cuts the between-set difference in world 3b zero share (against the round-12 set) by at least half | **Fails narrowly**: difference -1.49 points recalibrated, +0.82 points frozen on 78001 to 78012 (45% reduction). Likelihood k (0.020 to 0.001) and 80% share (1.07 to 0.07 points) are cut by more than half, the ratio by 43%. |
| N1 (c) ordering of the ratio (1 below 2b and 2a below 3b), 3b lowest 80% share, 3b gap below -2.5 and world 1 gap within 0.5 of zero, in every set | **Holds in every cell** (sets 77, 78, 79, and the frozen cells; 2b above 2a in set 78, a reversal allowed in the note). |
| N1 (d) likelihood k of world 3b below world 1 in at least 3 of 4 sets | **Holds, 4 of 4** (0.306 < 0.357, 0.326 < 0.345, 0.321 < 0.345; round-6 set 0.330 below the world-1 mean 0.349). The gap is 0.051, 0.019, 0.024. |
| N2 a 10% change in the coefficient moves likelihood k by less than 0.02 in worlds 1, 2a, 2b and by more than 0.03 in world 3b | **Partly fails.** World 1 (steps 0.010 and -0.009) and world 2b (0.016, -0.010) hold. World 2a: step 0.9 to 1.0 is +0.030, step 1.0 to 1.1 is -0.015 (bootstrap SE about 0.016 each; central 20% change 0.015). World 3b: steps +0.032 and +0.020, central 0.052 over 20% = 0.026 per 10%. So world 3b exceeds 0.03 in one step of two and not in the central estimate, and world 2a exceeds 0.02 in one step of two. Single steps are not resolved by 12 replicates (SE 0.011 to 0.016). |
| N3 (a) ordering of the ratio (world 1 lowest, world 3b highest) at both targets | **Holds at k 0.5** (1.09 < 1.48 < 2.72), **fails at k 0.2** (1.08, 1.55, 1.26: world 3b below world 2b). |
| N3 (b) world 1 below ratio 1.15 at both targets | **Holds** (1.08 and 1.09; upper interval limits 1.11 and 1.12). |
| N3 (c) world 3b at least 3 points below the NB zero share at k 0.2 and 0.5 | **Fails at k 0.2** (-1.85 points), **holds at k 0.5** (-5.36 points). |
| N5 each fingerprint inside the range spanned by the N1 sets | **Fails for 14 of 24 checks** (world 1: 7 of 8 outside; world 2b: 6 of 8; world 3b: 1 of 8). Differences from the N1 mean are at most 1.3 combined standard errors (z for likelihood k -0.7, +0.1, -0.2; ratio +0.5, +1.3, -0.4; zero share +0.9, +1.3, +0.4); the 3-set ranges of worlds 1 and 2b are narrower than a single-set standard error, so the test as defined is stricter than the noise. |
| runner (66a): frozen coefficient misses the 3% window for at least one world; frozen day 28 within 8% for all worlds | first **holds**, second **fails** (w2b -9.9%, w3b -13.9%) |

## N1: cells

| world | cell | coefficient | day 28 vs 6,211.25 | early R | likelihood k (90%) | moment k | ratio (90%) | zero share % | obs. minus NB zero, points (90%) | share causing 80% % (90%) | home share % | hh SAR | top-10 same-hh % | top-10 venue-day % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| World 1 | 77001-77012 (round 12) | 0.0004992 | +1.3% | 1.405 | 0.357 (0.346 to 0.369) | 0.338 | 1.06 (0.98 to 1.15) | 56.6 | 0.04 (-0.11 to 0.19) | 21.5 (21.1 to 22.0) | 34.2 | 0.00165 | 17.7 | 19.8 |
| World 1 | 78001-78012, recalibrated | 0.0004992 | +1.7% | 1.445 | 0.345 (0.335 to 0.354) | 0.331 | 1.04 (1.01 to 1.08) | 56.6 | -0.01 (-0.12 to 0.11) | 21.0 (20.6 to 21.3) | 34.0 | 0.00159 | 15.5 | 19.6 |
| World 1 | 79001-79012, recalibrated | 0.0005125 | -0.5% | 1.385 | 0.345 (0.332 to 0.356) | 0.328 | 1.05 (1.00 to 1.11) | 57.3 | -0.04 (-0.16 to 0.06) | 21.0 (20.5 to 21.4) | 33.8 | 0.00170 | 19.6 | 20.6 |
| World 2b | 77001-77012 (round 12) | 0.0001172 | -0.2% | 1.550 | 0.365 (0.354 to 0.378) | 0.257 | 1.42 (1.35 to 1.48) | 53.5 | -1.06 (-1.21 to -0.90) | 21.7 (21.2 to 22.2) | 14.1 | 0.00083 | 6.5 | 14.5 |
| World 2b | 78001-78012, recalibrated | 0.0001199 | -0.2% | 1.563 | 0.355 (0.341 to 0.367) | 0.241 | 1.47 (1.40 to 1.54) | 53.8 | -1.20 (-1.40 to -0.98) | 21.1 (20.6 to 21.6) | 14.0 | 0.00087 | 6.7 | 14.2 |
| World 2b | 79001-79012, recalibrated | 0.0001217 | +0.8% | 1.675 | 0.360 (0.347 to 0.376) | 0.249 | 1.45 (1.36 to 1.52) | 52.5 | -1.12 (-1.31 to -0.95) | 21.6 (21.0 to 22.2) | 14.1 | 0.00082 | 6.0 | 14.0 |
| World 2b | 78001-78012, frozen coefficient | 0.0001172 | -9.9% | 1.521 | 0.353 (0.337 to 0.369) | 0.238 | 1.48 (1.42 to 1.55) | 54.3 | -1.13 (-1.30 to -0.95) | 21.1 (20.5 to 21.7) | 14.1 | 0.00082 | 6.8 | 14.7 |
| World 2a | 77001-77012 (round 12) | 4.294e-05 | +0.3% | 1.644 | 0.355 (0.340 to 0.373) | 0.236 | 1.50 (1.30 to 1.68) | 52.8 | -1.29 (-1.51 to -1.04) | 21.1 (20.5 to 21.7) | 6.0 | 0.00041 | 3.3 | 14.7 |
| World 2a | 78001-78012, recalibrated | 4.369e-05 | +1.4% | 1.683 | 0.337 (0.324 to 0.350) | 0.239 | 1.41 (1.32 to 1.52) | 53.4 | -1.23 (-1.44 to -1.00) | 20.4 (19.7 to 21.0) | 5.9 | 0.00045 | 4.1 | 13.9 |
| World 2a | 79001-79012, recalibrated | 4.504e-05 | -0.3% | 1.722 | 0.344 (0.330 to 0.359) | 0.238 | 1.44 (1.35 to 1.56) | 52.7 | -1.30 (-1.44 to -1.17) | 20.7 (20.1 to 21.3) | 6.0 | 0.00043 | 4.3 | 14.3 |
| World 2a | 78001-78012, frozen coefficient | 4.294e-05 | -7.0% | 1.645 | 0.336 (0.321 to 0.350) | 0.236 | 1.42 (1.32 to 1.53) | 53.9 | -1.22 (-1.42 to -0.98) | 20.4 (19.7 to 20.9) | 5.9 | 0.00042 | 4.1 | 14.2 |
| World 3b | 68101-68112 (round 6) | 0.0001422 | +0.2% | 1.518 | 0.330 (0.323 to 0.337) | 0.152 | 2.16 (2.10 to 2.23) | 52.3 | -4.36 (-4.49 to -4.24) | 18.1 (17.7 to 18.4) | 22.6 | 0.00190 | 3.9 | 88.2 |
| World 3b | 77001-77012 (round 12) | 0.0001301 | +1.3% | 1.482 | 0.306 (0.295 to 0.317) | 0.157 | 1.95 (1.88 to 2.03) | 54.4 | -3.90 (-4.03 to -3.77) | 16.8 (16.2 to 17.4) | 21.3 | 0.00148 | 2.9 | 91.5 |
| World 3b | 78001-78012, recalibrated | 0.0001414 | -0.8% | 1.491 | 0.326 (0.317 to 0.335) | 0.153 | 2.13 (2.06 to 2.21) | 52.9 | -4.24 (-4.36 to -4.12) | 17.8 (17.4 to 18.3) | 22.5 | 0.00126 | 4.3 | 91.1 |
| World 3b | 79001-79012, recalibrated | 0.0001369 | +1.4% | 1.515 | 0.321 (0.312 to 0.330) | 0.157 | 2.04 (1.97 to 2.12) | 52.9 | -4.24 (-4.43 to -4.06) | 17.4 (17.0 to 17.8) | 22.7 | 0.00196 | 3.0 | 90.9 |
| World 3b | 78001-78012, frozen coefficient | 0.0001301 | -13.9% | 1.417 | 0.304 (0.296 to 0.314) | 0.148 | 2.05 (1.97 to 2.15) | 55.2 | -3.81 (-3.96 to -3.68) | 16.8 (16.4 to 17.5) | 21.8 | 0.00105 | 4.5 | 91.3 |

World 1 on sets 78 and 79: the round-12 coefficient is within 3% on set 78 (+1.7%); on set 79 it gives -9% at 12 replicates and recalibration needs 0.000512543 (+2.7%). On set 78 the recalibrated and frozen cells of world 1 are one configuration and identical to the last digit (the simulator is deterministic for identical inputs).

### Between-set SD against within-set standard error

Within-set SE is the mean of the sets' replicate-bootstrap standard deviations; SD uses n - 1.

| world | statistic | sets | values (in set order) | between-set SD | within-set SE | SD / SE |
|---|---|---|---|---|---|---|
| w1 | likelihood k | 3 | 0.357 / 0.345 / 0.345 | 0.007 | 0.007 | 1.06 |
| w1 | zero share (points) | 3 | 56.588 / 56.640 / 57.312 | 0.404 | 0.427 | 0.95 |
| w1 | ratio | 3 | 1.057 / 1.043 / 1.051 | 0.007 | 0.035 | 0.21 |
| w1 | share causing 80% (points) | 3 | 21.548 / 20.958 / 20.982 | 0.334 | 0.244 | 1.37 |
| w1 | obs. minus NB zero (points) | 3 | 0.042 / -0.015 / -0.038 | 0.041 | 0.077 | 0.53 |
| w2b | likelihood k | 3 | 0.365 / 0.355 / 0.360 | 0.005 | 0.008 | 0.68 |
| w2b | zero share (points) | 3 | 53.538 / 53.769 / 52.461 | 0.698 | 0.432 | 1.62 |
| w2b | ratio | 3 | 1.420 / 1.471 / 1.450 | 0.026 | 0.044 | 0.59 |
| w2b | share causing 80% (points) | 3 | 21.721 / 21.083 / 21.580 | 0.335 | 0.316 | 1.06 |
| w2b | obs. minus NB zero (points) | 3 | -1.057 / -1.196 / -1.125 | 0.069 | 0.111 | 0.62 |
| w2a | likelihood k | 3 | 0.355 / 0.337 / 0.344 | 0.009 | 0.009 | 1.00 |
| w2a | zero share (points) | 3 | 52.847 / 53.443 / 52.675 | 0.403 | 0.532 | 0.76 |
| w2a | ratio | 3 | 1.502 / 1.411 / 1.444 | 0.046 | 0.081 | 0.57 |
| w2a | share causing 80% (points) | 3 | 21.098 / 20.373 / 20.692 | 0.363 | 0.379 | 0.96 |
| w2a | obs. minus NB zero (points) | 3 | -1.286 / -1.231 / -1.300 | 0.037 | 0.121 | 0.30 |
| w3b | likelihood k | 4 | 0.330 / 0.306 / 0.326 / 0.321 | 0.011 | 0.006 | 1.90 |
| w3b | zero share (points) | 4 | 52.285 / 54.383 / 52.898 / 52.905 | 0.892 | 0.393 | 2.27 |
| w3b | ratio | 4 | 2.165 / 1.950 / 2.130 / 2.037 | 0.097 | 0.044 | 2.18 |
| w3b | share causing 80% (points) | 4 | 18.075 / 16.763 / 17.835 / 17.422 | 0.574 | 0.274 | 2.09 |
| w3b | obs. minus NB zero (points) | 4 | -4.362 / -3.895 / -4.238 / -4.244 | 0.201 | 0.086 | 2.34 |

(Set order: worlds 1, 2b, 2a: 77, 78, 79; world 3b: 68, 77, 78, 79.) Checkpoint rule of note 65 (SD at most 1.2 times SE for all worlds and statistics) is not met (world 3b 1.9 to 2.3; world 2b zero share 1.62; world 1 share 80% 1.37). Pooled over worlds 1, 2b, 2a (root mean square of the ratio): likelihood k 0.93, zero share 1.17, ratio 0.49, share causing 80% 1.14, obs. minus NB zero 0.50.

## N2: calibration sensitivity (seeds 77001 to 77012, round-12 coefficient x 0.9 and x 1.1, no recalibration, 12 replicates)

| world | statistic | coefficient x0.9 | x1.0 (round 12) | x1.1 | change 0.9 to 1.0 | change 1.0 to 1.1 | central change 0.9 to 1.1 (bootstrap SE) |
|---|---|---|---|---|---|---|---|
| w1 | day 28 vs target (%) | -28.481 | 1.308 | 39.479 | +29.789 | +38.171 | +67.960 |
| w1 | early R | 1.265 | 1.405 | 1.516 | +0.140 | +0.111 | +0.251 (0.046) |
| w1 | likelihood k | 0.347 | 0.357 | 0.348 | +0.010 | -0.010 | +0.000 (0.009) |
| w1 | moment k | 0.320 | 0.338 | 0.326 | +0.018 | -0.012 | +0.006 (0.015) |
| w1 | ratio | 1.086 | 1.057 | 1.068 | -0.029 | +0.011 | -0.018 (0.033) |
| w1 | zero share (points) | 58.592 | 56.588 | 55.676 | -2.004 | -0.912 | -2.917 (0.674) |
| w1 | obs. minus NB zero (points) | -0.087 | 0.042 | -0.113 | +0.128 | -0.155 | -0.027 (0.076) |
| w1 | share causing 80% (points) | 20.754 | 21.548 | 21.156 | +0.794 | -0.392 | +0.402 (0.354) |
| w1 | home share (points) | 34.641 | 34.224 | 33.072 | -0.416 | -1.152 | -1.569 (0.268) |
| w1 | top-10 same-household share (points) | 19.448 | 17.680 | 17.672 | -1.767 | -0.008 | -1.775 (2.033) |
| w1 | top-10 venue-day share (points) | 21.164 | 19.766 | 20.796 | -1.397 | +1.030 | -0.368 (1.000) |
| w2b | day 28 vs target (%) | -35.764 | -0.250 | 48.396 | +35.515 | +48.646 | +84.160 |
| w2b | early R | 1.392 | 1.550 | 1.747 | +0.157 | +0.198 | +0.355 (0.060) |
| w2b | likelihood k | 0.349 | 0.365 | 0.355 | +0.016 | -0.010 | +0.006 (0.015) |
| w2b | moment k | 0.210 | 0.257 | 0.231 | +0.047 | -0.026 | +0.021 (0.029) |
| w2b | ratio | 1.662 | 1.420 | 1.535 | -0.243 | +0.115 | -0.128 (0.178) |
| w2b | zero share (points) | 55.963 | 53.538 | 52.079 | -2.425 | -1.459 | -3.884 (0.778) |
| w2b | obs. minus NB zero (points) | -1.106 | -1.057 | -1.102 | +0.049 | -0.045 | +0.004 (0.168) |
| w2b | share causing 80% (points) | 20.825 | 21.721 | 21.389 | +0.896 | -0.332 | +0.565 (0.510) |
| w2b | home share (points) | 14.534 | 14.090 | 14.110 | -0.444 | +0.020 | -0.424 (0.255) |
| w2b | top-10 same-household share (points) | 8.321 | 6.533 | 5.809 | -1.787 | -0.725 | -2.512 (1.116) |
| w2b | top-10 venue-day share (points) | 15.908 | 14.490 | 12.645 | -1.417 | -1.845 | -3.263 (0.761) |
| w2a | day 28 vs target (%) | -33.730 | 0.323 | 46.084 | +34.054 | +45.761 | +79.815 |
| w2a | early R | 1.509 | 1.644 | 1.825 | +0.135 | +0.181 | +0.316 (0.059) |
| w2a | likelihood k | 0.325 | 0.355 | 0.340 | +0.030 | -0.015 | +0.015 (0.016) |
| w2a | moment k | 0.215 | 0.236 | 0.232 | +0.022 | -0.004 | +0.018 (0.022) |
| w2a | ratio | 1.517 | 1.502 | 1.465 | -0.015 | -0.037 | -0.052 (0.125) |
| w2a | zero share (points) | 55.810 | 52.847 | 51.982 | -2.964 | -0.865 | -3.828 (0.832) |
| w2a | obs. minus NB zero (points) | -1.153 | -1.286 | -1.287 | -0.133 | -0.001 | -0.133 (0.128) |
| w2a | share causing 80% (points) | 19.903 | 21.098 | 20.550 | +1.195 | -0.548 | +0.647 (0.636) |
| w2a | home share (points) | 6.047 | 5.998 | 6.051 | -0.049 | +0.052 | +0.003 (0.144) |
| w2a | top-10 same-household share (points) | 5.352 | 3.280 | 4.315 | -2.072 | +1.035 | -1.038 (0.944) |
| w2a | top-10 venue-day share (points) | 15.114 | 14.659 | 12.990 | -0.455 | -1.669 | -2.124 (0.876) |
| w3b | day 28 vs target (%) | -16.179 | 1.331 | 19.333 | +17.510 | +18.002 | +35.512 |
| w3b | early R | 1.414 | 1.482 | 1.545 | +0.068 | +0.063 | +0.131 (0.053) |
| w3b | likelihood k | 0.274 | 0.306 | 0.326 | +0.032 | +0.020 | +0.052 (0.011) |
| w3b | moment k | 0.149 | 0.157 | 0.159 | +0.008 | +0.002 | +0.010 (0.005) |
| w3b | ratio | 1.835 | 1.950 | 2.050 | +0.115 | +0.100 | +0.216 (0.065) |
| w3b | zero share (points) | 57.328 | 54.383 | 52.324 | -2.945 | -2.059 | -5.004 (0.700) |
| w3b | obs. minus NB zero (points) | -3.450 | -3.895 | -4.260 | -0.446 | -0.365 | -0.810 (0.146) |
| w3b | share causing 80% (points) | 15.045 | 16.763 | 17.859 | +1.718 | +1.095 | +2.814 (0.557) |
| w3b | home share (points) | 20.523 | 21.282 | 22.397 | +0.759 | +1.115 | +1.874 (0.449) |
| w3b | top-10 same-household share (points) | 3.952 | 2.871 | 3.552 | -1.081 | +0.681 | -0.401 (1.156) |
| w3b | top-10 venue-day share (points) | 92.975 | 91.527 | 89.713 | -1.448 | -1.813 | -3.262 (2.219) |

`66_n2_derivatives.csv` has the slope per unit log coefficient. Day 28 differs by -29% to -36% and +39% to +48% in worlds 1, 2a, 2b and by -16% and +19% in world 3b.

## N3: target band (calibration seeds 76001 to 76006, 6 replicates; final cells on 77001 to 77012, 12 replicates, day 28 recalibrated)

Tuning log (a trial is one value of the tuned parameter with its coefficient calibrated to day 28 on the 6 replicates; the likelihood k of that calibrated cell is the quantity compared with the target; stop at |k - target| at most 0.03):

| world | target k | trial | tuned parameter | coefficient | day 28 (6 reps) | likelihood k (6 reps) | used for final |
|---|---|---|---|---|---|---|---|
| w1 | 0.2 | 1 | 0.1639 | 0.0005458 | 6029 | 0.184 | True |
| w1 | 0.5 | 1 | 0.4721 | 0.0004736 | 6037 | 0.470 | False |
| w1 | 0.5 | 2 | 0.5075 | 0.0004736 | 6236 | 0.496 | True |
| w2b | 0.2 | 1 | 0.2173 | 0.0001262 | 6067 | 0.173 | True |
| w2b | 0.5 | 1 | 0.9694 | 0.0001197 | 6152 | 0.484 | True |
| w3b | 0.2 | 1 | 0.2198 | 7.461e-05 | 6158 | 0.194 | True |
| w3b | 0.5 | 1 | 0.09049 | 0.0002287 | 6287 | 0.535 | False |
| w3b | 0.5 | 2 | 0.09658 | 0.0002099 | 6226 | 0.471 | True |

Final cells (12 replicates, coefficient recalibrated on 77001 to 77012 starting from the trial coefficient):

| world | cell | coefficient | day 28 vs 6,211.25 | early R | likelihood k (90%) | moment k | ratio (90%) | zero share % | obs. minus NB zero, points (90%) | share causing 80% % (90%) | home share % | hh SAR | top-10 same-hh % | top-10 venue-day % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| World 1 | round-12 setting (k about 0.35) | 0.0004992 | +1.3% | 1.405 | 0.357 (0.346 to 0.369) | 0.338 | 1.06 (0.98 to 1.15) | 56.6 | 0.04 (-0.11 to 0.19) | 21.5 (21.1 to 22.0) | 34.2 | 0.00165 | 17.7 | 19.8 |
| World 1 | target 0.2: shape 0.1639 | 0.0005464 | +0.5% | 1.429 | 0.187 (0.179 to 0.195) | 0.173 | 1.08 (1.04 to 1.11) | 66.8 | -0.03 (-0.07 to 0.02) | 14.4 (13.9 to 14.9) | 28.9 | 0.00120 | 14.8 | 18.9 |
| World 1 | target 0.5: shape 0.5075 | 0.0004781 | -0.1% | 1.373 | 0.543 (0.522 to 0.565) | 0.497 | 1.09 (1.06 to 1.12) | 50.2 | -0.28 (-0.40 to -0.17) | 26.0 (25.5 to 26.5) | 36.6 | 0.00173 | 21.1 | 20.4 |
| World 2b | round-12 setting (k about 0.35) | 0.0001172 | -0.2% | 1.550 | 0.365 (0.354 to 0.378) | 0.257 | 1.42 (1.35 to 1.48) | 53.5 | -1.06 (-1.21 to -0.90) | 21.7 (21.2 to 22.2) | 14.1 | 0.00083 | 6.5 | 14.5 |
| World 2b | target 0.2: shape 0.2173 | 0.0001173 | +2.3% | 1.581 | 0.169 (0.161 to 0.177) | 0.109 | 1.55 (1.43 to 1.67) | 66.8 | -0.56 (-0.66 to -0.44) | 12.7 (12.1 to 13.1) | 12.2 | 0.00073 | 5.2 | 14.0 |
| World 2b | target 0.5: shape 0.9694 | 0.000118 | -0.8% | 1.584 | 0.484 (0.462 to 0.507) | 0.326 | 1.48 (1.38 to 1.59) | 48.1 | -1.41 (-1.59 to -1.21) | 25.3 (24.8 to 25.9) | 14.8 | 0.00089 | 7.4 | 15.2 |
| World 3b | round-12 setting (k about 0.35) | 0.0001301 | +1.3% | 1.482 | 0.306 (0.295 to 0.317) | 0.157 | 1.95 (1.88 to 2.03) | 54.4 | -3.90 (-4.03 to -3.77) | 16.8 (16.2 to 17.4) | 21.3 | 0.00148 | 2.9 | 91.5 |
| World 3b | target 0.2: event rate 0.2198 | 7.915e-05 | -2.4% | 1.489 | 0.209 (0.200 to 0.218) | 0.166 | 1.26 (1.21 to 1.31) | 62.7 | -1.85 (-1.94 to -1.75) | 11.9 (11.2 to 12.4) | 14.0 | 0.00091 | 3.0 | 80.2 |
| World 3b | target 0.5: event rate 0.09658 | 0.000206 | +1.9% | 1.418 | 0.520 (0.502 to 0.540) | 0.191 | 2.72 (2.66 to 2.78) | 45.1 | -5.36 (-5.55 to -5.15) | 26.6 (25.7 to 27.3) | 30.5 | 0.00228 | 4.5 | 95.1 |

Achieved likelihood k on 12 replicates differs from the 6-replicate trial value by up to 0.05 (world 1 target 0.5: 0.496 at 6 replicates, 0.542 at 12; world 3b 0.5: 0.471 and 0.520): the trials are not accurate to better than about 0.03 to 0.05. World 2b targets use shape alone with the scene factor lambda 10 (as in round 11); the shape needed is 0.22 for k 0.2 and 0.97 for k 0.5 (round 12: 0.58 at k 0.365). World 3b needs event rate 0.22 and 0.097 (round 12: 0.1456), with the factor 3000 and group size 30 fixed. Event offspring share in world 3b: 77% at k 0.2, 64% at k 0.31, 44% at k 0.52.

## N5: one more realisation of the venue lists

**How the lists were redrawn** (`study/build_r13_inputs.py`, seed 20261022): a copy of `agents2.json` (original untouched) in which, for each of the types 5 (restaurants), 8 (long shops), 9 (churches) and 10 (parks) separately, the venue ids of all slots are shuffled among agents whose home lies in the same 2 km grid cell (EOV coordinates read from the home id; 28,446 agents without coordinates form one extra cell), then repeated venues within an agent are swapped away. Every venue keeps its count in every cell and in total (checked), every agent keeps its number of slots per type, and no agent has a repeated venue in the new file (two agents had a repeated type-8 venue in the original). 447,026, 729,906, 447,003 and 477,112 slots changed (97%, 97%, 91%, 95% of the slots of types 5, 8, 9, 10). This is my reading of "same quotas"; it keeps the geography of the assignment at the 2 km scale, which a global shuffle (round 3, type 5) does not. Worlds 1, 2b, 3b on seeds 77001 to 77012, coefficient recalibrated (world 1 0.000499174, +0.0% change, day 28 -1.5%; world 2b 0.000118804, +1.4%; world 3b 0.00013774, +5.9%).

| world | cell | coefficient | day 28 vs 6,211.25 | early R | likelihood k (90%) | moment k | ratio (90%) | zero share % | obs. minus NB zero, points (90%) | share causing 80% % (90%) | home share % | hh SAR | top-10 same-hh % | top-10 venue-day % |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| World 1 | original venue lists, 77001-77012 | 0.0004992 | +1.3% | 1.405 | 0.357 (0.346 to 0.369) | 0.338 | 1.06 (0.98 to 1.15) | 56.6 | 0.04 (-0.11 to 0.19) | 21.5 (21.1 to 22.0) | 34.2 | 0.00165 | 17.7 | 19.8 |
| World 1 | redrawn venue lists, 77001-77012, recalibrated | 0.0004992 | -1.5% | 1.384 | 0.342 (0.329 to 0.356) | 0.320 | 1.07 (1.03 to 1.11) | 57.5 | 0.01 (-0.09 to 0.13) | 21.0 (20.5 to 21.4) | 34.7 | 0.00144 | 20.3 | 21.3 |
| World 2b | original venue lists, 77001-77012 | 0.0001172 | -0.2% | 1.550 | 0.365 (0.354 to 0.378) | 0.257 | 1.42 (1.35 to 1.48) | 53.5 | -1.06 (-1.21 to -0.90) | 21.7 (21.2 to 22.2) | 14.1 | 0.00083 | 6.5 | 14.5 |
| World 2b | redrawn venue lists, 77001-77012, recalibrated | 0.0001188 | +0.7% | 1.505 | 0.362 (0.348 to 0.375) | 0.230 | 1.57 (1.44 to 1.71) | 54.0 | -1.20 (-1.40 to -1.01) | 21.3 (20.9 to 21.8) | 14.2 | 0.00078 | 7.7 | 14.7 |
| World 3b | original venue lists, 77001-77012 | 0.0001301 | +1.3% | 1.482 | 0.306 (0.295 to 0.317) | 0.157 | 1.95 (1.88 to 2.03) | 54.4 | -3.90 (-4.03 to -3.77) | 16.8 (16.2 to 17.4) | 21.3 | 0.00148 | 2.9 | 91.5 |
| World 3b | redrawn venue lists, 77001-77012, recalibrated | 0.0001377 | +1.0% | 1.499 | 0.318 (0.306 to 0.331) | 0.156 | 2.04 (1.96 to 2.14) | 53.4 | -4.07 (-4.23 to -3.92) | 17.5 (17.0 to 18.1) | 23.0 | 0.00180 | 3.1 | 90.5 |

Comparison with the range of the recalibrated N1 sets (`66_n5_vs_n1_range.csv`): world 1 inside the range for 1 of 8 statistics, world 2b for 2 of 8, world 3b for 7 of 8 (all except home share, 23.0 against 21.3 to 22.7).

## N4 (thinning draws), N0 (exports): unchanged from the checkpoint report

N4: 20 draws per replicate, three schemes, two rates, four worlds; the SD over draws of the pooled likelihood k is 0.005 to 0.028, 0.5 to 1.4 times the replicate standard error of table 62_r122; the round-12 values lie inside the draw distributions. N0: 101 arms, 1,152 replicates (all arms of rounds 6 to 12 and the seven 16-week repeat arms); details in `66_round13_results_checkpoint.md`.

## Limits that matter for reading these numbers

- Three or four seed sets per world: SD of the set-to-set SD is large (a 2-set or 3-set SD has 1 or 2 degrees of freedom); "SD over SE of 1.0" is consistent with equal between and within noise and with up to about 1.7 times excess at 3 sets.
- Intervals in the tables are within-set only. A combined interval needs the between-set term, which you compute.
- N3 final cells have 12 replicates and one seed set; the targets were met to 0.03 to 0.05 only; the 6-replicate trial values are noisy.
- N5 tests one realisation of one kind of redraw (2 km local shuffle); a global shuffle or a redraw based on the original assignment rule would be a different test.
- N2 has one 12-replicate cell per side; a single step is not resolved (SE 0.011 to 0.016 for likelihood k).

## Files

Drive: this file, `66a_review_of_note65.md`, `66_upload_index.md`, `66_n1_calibration_log.csv`, `66_n1_between_set_sd.csv`, `66_n3_tuning_log.csv`, `66_n4_noise_summary.csv`, `66_n5_vs_n1_range.csv`. Local only (too large for the connector, or fully tabulated above): `66_n2_derivatives.csv`, all `*_replicate_*.csv`, `*_cells_summary.csv`, `66_n1_checkpoint_pairs.csv`, `66_n4_thinning_draws*.csv`, `66_n0_*.csv`; see `66_upload_index.md`. Per-cell files exist for N1, N2, N3 and N5 (`66_n*_replicate_summary.csv`, `_replicate_histograms.csv`, `_cells_summary.csv`, `_calibration_log.csv`).
