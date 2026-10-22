# ACT-049 note 69: round 14 (run A: second seed set for the target band; run B: the worlds at the published k and mean), results

22 October 2026. Reply to note 68. Review of note 68: `69a_review_of_note68.md`. Code: `study/run_round14.py` (run A, B1, B2), `study/extend_b2.py` and `study/b2_extended.py` (replicate extensions and the extended world-3b search of B2), `study/analyze_round14.py`, `study/analyze_round13.py` (extended statistics); binary `build_r10/panSim`, no C++ change; location and agent files untouched. Command lines, flags and dump options are those of round 13. Reporting rules as in note 68: likelihood k primary with moment k beside it, observed zero, 1 to 5, above five and 80% shares, failed predictions reported as failed. 90% intervals are replicate-level percentile bootstraps (1,000 resamples) of the pooled statistic. Index cases: infected on days 1 to 10 with a known infector; offspring within 14 days. The per-replicate files are listed at the end; they are in the repository and need a file copy to Drive (see `69_upload_index.md`).

## Headline

1. **Run A (second seed set for the six target-band cells): every registered prediction holds.** Likelihood k of the six cells differs from round 13 by at most 0.023 (world 3b at 0.5: 0.497 against 0.520; the others 0.000 to 0.012). The ratio order repeats at both targets, including the reversal at 0.2 (world 3b 1.25 below world 2b 1.55; world 1 1.01). The events-world zero-share gap is -1.86 points at the 0.2 target (round 13: -1.85) and -5.31 at the 0.5 target (-5.36). The events-world venue-day share is 80% and 94%, against 14% to 22% in worlds 1 and 2b. Of 84 two-set comparisons (14 statistics in six cells) none exceeds 3 combined standard errors and 3 exceed 2 (world 1 at 0.5: home share, early R, share above five), about the 4 expected.
2. **B1 (likelihood k 0.27 at the usual matching, early R about 1.4 to 1.6): all three worlds reach the window without correction.** World 1 (shape 0.24) 0.263, world 2b (shape 0.40, scene factor 10) 0.270, world 3b (event rate 0.17) 0.248 (the last near the lower edge of 0.24 to 0.30). The events-world observed minus negative-binomial zero share is **-2.91 points** (90% interval -3.05 to -2.76) at k 0.248; world 1 -0.11 (-0.20 to 0.00), world 2b -0.72 (-0.85 to -0.60).
3. **B2 (likelihood k 0.27 at mean offspring 0.88, day 28 not matched) is reachable in all three worlds.** World 1: mean 0.880 (0.846 to 0.915), k 0.278, zero 67.2%, 1 to 5 29.4%, above five 3.4% (24 replicates, 11,322 index cases; published 67%, 30%, 3%). World 2b: mean 0.917 (0.870 to 0.963; 4.2% above 0.88, which fails the 3% window although the interval contains 0.88), k 0.257, zero 67.1%, 1 to 5 29.5%, above five 3.4% (36 replicates, 11,298 index cases). World 3b: the five-trial protocol ended at mean 0.767 and k 0.296 (36 replicates, 11,617 index cases), outside the windows; a model-based search **beyond the trial limit** (four extra trials, two corrections) gives mean 0.867 (0.833 to 0.898) and k 0.265 (0.252 to 0.279): zero 65.7%, 1 to 5 30.9%, above five 3.4% (negative binomial at its own k and mean 3.6%), maximum 40, 99th percentile 16, venue-day share of the ten largest clusters 93% (24 replicates, 9,824 index cases).
4. **At the published mean the events-world zero-share deficit is -2.34 points (90% interval -2.43 to -2.24)**, against -2.91 at mean 1.45 (B1) and -3.90 at likelihood k 0.31 (round 12): the deficit shrinks as the mean falls, and at 0.87 it is only just beyond the -2.2 limit of the range compatible with the published data. The world-1 deficit is -0.09 and the world-2b deficit -0.58 at the published mean.
5. **Shape at the published mean does not separate the worlds on the published shares**: zero 65.7 to 67.2%, 1 to 5 29.4 to 30.9%, above five 3.4% in all three worlds, against the published 67, 30, 3. The worlds differ in the ratio of likelihood to moment k (1.08, 1.59, 2.19), the maximum offspring (28, 54, 40), the home share (36.7%, 17.2%, 25.7%) and the venue-day share (25%, 23%, 93%).

## Registered predictions of note 68 (thresholds unchanged)

| prediction | outcome |
|---|---|
| **Run A (a)** likelihood k of every cell within 0.04 of round 13 | **Holds.** Differences: world 1 +0.001 (0.2), -0.012 (0.5); world 2b 0.000, +0.008; world 3b -0.001, -0.023. |
| **A (b)** ratio order repeats (0.5: 1 < 2b < 3b; 0.2: 3b below 2b) | **Holds.** At 0.5: 1.06 < 1.41 < 2.68. At 0.2: world 3b 1.25 below world 2b 1.55 (world 1 1.01). |
| **A (c)** events-world gap between -1.0 and -2.8 at 0.2 and below -4.5 at 0.5 | **Holds**: -1.86 and -5.31. |
| **A (d)** events-world venue-day share at least 75% (0.2) and 88% (0.5); at most 25% in worlds 1 and 2b | **Holds**: 80.2% and 94.4%; world 1 18.7% and 21.7%, world 2b 15.1% and 14.3%. |
| **A (e)** no statistic more than 3 combined SE from round 13 | **Holds** (0 of 84 above 3; 3 above 2: world 1 at 0.5 home share z 2.4, early R 2.1, share above five 2.6). |
| **B (a)** B1 reaches likelihood k 0.24 to 0.30 in all three worlds within the trial limit | **Holds**: 0.263, 0.270, 0.248 (one trial each, final cell on the first attempt). |
| **B (b)** at k 0.27 (usual regime): events-world gap -2.6 to -3.6 and below -2.2; world 1 within 0.5 of zero; world 2b -0.3 to -1.4 | **Holds**: -2.91 (at k 0.248), -0.11, -0.72. |
| **B (c)** B2 reaches mean 0.88 within 3% and k 0.24 to 0.30 in worlds 1 and 2b | **Holds for world 1** (0.880, 0.278). **Fails narrowly for world 2b**: k 0.257 but mean 0.917 (+4.2%) on the 36-replicate cell; it was 0.885 on the first 24 replicates and 0.842 on the first 12 (replicate-to-replicate noise in the mean is of the order of the 3% window). |
| **B (d)** B2 worlds 1 and 2b: zero share within 2 points of 67%, share above five 2.5% to 4.5% | **Holds**: 67.2% and 67.1%; 3.4% and 3.4%. |
| **B (e)** B2 events world: above-five share at most 0.85 of the negative binomial at its own k and mean; world 1 between 0.9 and 1.1 | **Fails for the events world**: 0.97 (protocol cell) and 0.94 (extended-search cell). **Holds for world 1** (0.96). (World 2b: 0.84.) |
| **B (f)** B2 events-world zero-share gap below -2.2 | **Holds**: -2.43 (mean 0.767) and -2.34 (mean 0.867, interval -2.43 to -2.24). |

## Run A: cells and two-set comparison

Each cell keeps the tuned parameter of round 13 and is calibrated independently to day 28 on seeds 78001 to 78012, starting from the round-13 coefficient (pilot of 4 replicates, then 12). Round-13 cells are recomputed with the same code for the comparison (the earlier tables did not have the new columns).

| world | cell | coefficient | day 28 vs 6,211.25 | early R | likelihood k (90%) | moment k | ratio (90%) | zero share % | obs. minus NB zero, points (90%) | share causing 80% % (90%) | home share % | hh SAR | top-10 offspring | top-10 same-hh % | top-10 venue-day % | top-10 distinct venues |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| World 1 | target 0.2, shape 0.1639: round 13, seeds 77001-77012 | 0.0005464 | +0.5% | 1.429 | 0.187 (0.179 to 0.195) | 0.173 | 1.08 (1.04 to 1.11) | 66.8 | -0.03 (-0.07 to 0.02) | 14.4 (13.9 to 14.9) | 28.9 | 0.00120 | 26.2 | 14.8 | 18.9 | 7.0 |
| World 1 | target 0.2, shape 0.1639: **run A, seeds 78001-78012** | 0.0005464 | -2.9% | 1.429 | 0.188 (0.184 to 0.193) | 0.185 | 1.01 (0.96 to 1.06) | 66.8 | 0.04 (-0.04 to 0.13) | 14.6 (14.3 to 14.8) | 29.1 | 0.00119 | 24.4 | 16.0 | 18.7 | 7.2 |
| World 1 | target 0.5, shape 0.5075: round 13, seeds 77001-77012 | 0.0004781 | -0.1% | 1.373 | 0.543 (0.522 to 0.565) | 0.497 | 1.09 (1.06 to 1.12) | 50.2 | -0.28 (-0.40 to -0.17) | 26.0 (25.5 to 26.5) | 36.6 | 0.00173 | 14.2 | 21.1 | 20.4 | 5.5 |
| World 1 | target 0.5, shape 0.5075: **run A, seeds 78001-78012** | 0.0004781 | +1.2% | 1.433 | 0.531 (0.517 to 0.546) | 0.500 | 1.06 (1.04 to 1.08) | 49.8 | -0.16 (-0.24 to -0.06) | 26.0 (25.7 to 26.3) | 37.1 | 0.00181 | 14.6 | 21.4 | 21.7 | 5.2 |
| World 2b | target 0.2, shape 0.2173: round 13, seeds 77001-77012 | 0.0001173 | +2.3% | 1.581 | 0.169 (0.161 to 0.177) | 0.109 | 1.55 (1.43 to 1.67) | 66.8 | -0.56 (-0.66 to -0.44) | 12.7 (12.1 to 13.1) | 12.2 | 0.00073 | 34.9 | 5.2 | 14.0 | 10.2 |
| World 2b | target 0.2, shape 0.2173: **run A, seeds 78001-78012** | 0.000122 | +1.1% | 1.590 | 0.169 (0.160 to 0.179) | 0.109 | 1.55 (1.38 to 1.71) | 66.7 | -0.56 (-0.63 to -0.48) | 12.7 (12.0 to 13.3) | 12.3 | 0.00082 | 32.8 | 5.4 | 15.1 | 10.0 |
| World 2b | target 0.5, shape 0.9694: round 13, seeds 77001-77012 | 0.000118 | -0.8% | 1.584 | 0.484 (0.462 to 0.507) | 0.326 | 1.48 (1.38 to 1.59) | 48.1 | -1.41 (-1.59 to -1.21) | 25.3 (24.8 to 25.9) | 14.8 | 0.00089 | 19.4 | 7.4 | 15.2 | 9.0 |
| World 2b | target 0.5, shape 0.9694: **run A, seeds 78001-78012** | 0.000118 | -1.8% | 1.565 | 0.492 (0.476 to 0.509) | 0.349 | 1.41 (1.34 to 1.48) | 48.0 | -1.51 (-1.67 to -1.31) | 25.4 (24.9 to 25.8) | 14.8 | 0.00088 | 18.7 | 6.0 | 14.3 | 9.1 |
| World 3b | target 0.2, event rate 0.2198: round 13, seeds 77001-77012 | 7.915e-05 | -2.4% | 1.489 | 0.209 (0.200 to 0.218) | 0.166 | 1.26 (1.21 to 1.31) | 62.7 | -1.85 (-1.94 to -1.75) | 11.9 (11.2 to 12.4) | 14.0 | 0.00091 | 22.8 | 3.0 | 80.2 | 1.8 |
| World 3b | target 0.2, event rate 0.2198: **run A, seeds 78001-78012** | 8.031e-05 | +2.6% | 1.527 | 0.208 (0.203 to 0.212) | 0.166 | 1.25 (1.21 to 1.29) | 62.5 | -1.86 (-1.96 to -1.76) | 11.7 (11.4 to 12.0) | 13.9 | 0.00100 | 23.3 | 4.0 | 80.2 | 1.8 |
| World 3b | target 0.5, event rate 0.09658: round 13, seeds 77001-77012 | 0.000206 | +1.9% | 1.418 | 0.520 (0.502 to 0.540) | 0.191 | 2.72 (2.66 to 2.78) | 45.1 | -5.36 (-5.55 to -5.15) | 26.6 (25.7 to 27.3) | 30.5 | 0.00228 | 25.8 | 4.5 | 95.1 | 1.9 |
| World 3b | target 0.5, event rate 0.09658: **run A, seeds 78001-78012** | 0.000206 | -2.0% | 1.487 | 0.497 (0.473 to 0.526) | 0.185 | 2.68 (2.57 to 2.80) | 44.9 | -5.31 (-5.55 to -5.10) | 25.3 (24.3 to 26.6) | 30.2 | 0.00200 | 27.1 | 4.1 | 94.4 | 1.9 |

Coefficients on set 78: world 1 unchanged at both targets (0.000546 and 0.000478; day 28 -2.9% and +1.2% within the window); world 2b 0.000122 (+4% from round 13) at 0.2 and unchanged at 0.5; world 3b 8.03e-05 (+1.5%) at 0.2 and unchanged at 0.5. Calibration iterations are in `69_a_calibration_log.csv`.

Two-set comparison (difference over the combined bootstrap standard error; the full list of 14 statistics per cell is in `69_runA_two_set.csv`):

| world | target | statistic | round 13 (77001-77012) | run A (78001-78012) | difference | combined SE | z |
|---|---|---|---|---|---|---|---|
| w1 | 0.2 | likelihood k | 0.187 | 0.188 | +0.001 | 0.006 | +0.2 |
| w1 | 0.2 | ratio | 1.079 | 1.015 | -0.064 | 0.038 | -1.7 |
| w1 | 0.2 | observed minus NB zero (points) | -0.031 | 0.043 | +0.074 | 0.060 | +1.2 |
| w1 | 0.2 | share causing 80% (points) | 14.415 | 14.587 | +0.171 | 0.332 | +0.5 |
| w1 | 0.2 | home share (points) | 28.891 | 29.083 | +0.191 | 0.398 | +0.5 |
| w1 | 0.2 | top-10 venue-day share (points) | 18.854 | 18.677 | -0.177 | 0.632 | -0.3 |
| w1 | 0.5 | likelihood k | 0.543 | 0.531 | -0.012 | 0.016 | -0.8 |
| w1 | 0.5 | ratio | 1.092 | 1.061 | -0.030 | 0.026 | -1.2 |
| w1 | 0.5 | observed minus NB zero (points) | -0.280 | -0.157 | +0.123 | 0.088 | +1.4 |
| w1 | 0.5 | share causing 80% (points) | 25.995 | 26.003 | +0.008 | 0.359 | +0.0 |
| w1 | 0.5 | home share (points) | 36.630 | 37.125 | +0.495 | 0.207 | +2.4 |
| w1 | 0.5 | top-10 venue-day share (points) | 20.359 | 21.655 | +1.297 | 0.916 | +1.4 |
| w2b | 0.2 | likelihood k | 0.169 | 0.169 | -0.000 | 0.008 | -0.0 |
| w2b | 0.2 | ratio | 1.549 | 1.546 | -0.003 | 0.123 | -0.0 |
| w2b | 0.2 | observed minus NB zero (points) | -0.562 | -0.555 | +0.006 | 0.081 | +0.1 |
| w2b | 0.2 | share causing 80% (points) | 12.659 | 12.653 | -0.006 | 0.484 | -0.0 |
| w2b | 0.2 | home share (points) | 12.209 | 12.292 | +0.083 | 0.257 | +0.3 |
| w2b | 0.2 | top-10 venue-day share (points) | 14.010 | 15.050 | +1.040 | 1.042 | +1.0 |
| w2b | 0.5 | likelihood k | 0.484 | 0.492 | +0.009 | 0.017 | +0.5 |
| w2b | 0.5 | ratio | 1.482 | 1.410 | -0.072 | 0.077 | -0.9 |
| w2b | 0.5 | observed minus NB zero (points) | -1.412 | -1.505 | -0.094 | 0.157 | -0.6 |
| w2b | 0.5 | share causing 80% (points) | 25.322 | 25.359 | +0.037 | 0.444 | +0.1 |
| w2b | 0.5 | home share (points) | 14.806 | 14.779 | -0.027 | 0.233 | -0.1 |
| w2b | 0.5 | top-10 venue-day share (points) | 15.172 | 14.317 | -0.855 | 0.972 | -0.9 |
| w3b | 0.2 | likelihood k | 0.209 | 0.208 | -0.002 | 0.006 | -0.3 |
| w3b | 0.2 | ratio | 1.260 | 1.251 | -0.009 | 0.040 | -0.2 |
| w3b | 0.2 | observed minus NB zero (points) | -1.845 | -1.863 | -0.018 | 0.084 | -0.2 |
| w3b | 0.2 | share causing 80% (points) | 11.854 | 11.667 | -0.186 | 0.403 | -0.5 |
| w3b | 0.2 | home share (points) | 13.977 | 13.925 | -0.052 | 0.235 | -0.2 |
| w3b | 0.2 | top-10 venue-day share (points) | 80.210 | 80.210 | +0.001 | 3.279 | +0.0 |
| w3b | 0.5 | likelihood k | 0.520 | 0.497 | -0.023 | 0.020 | -1.2 |
| w3b | 0.5 | ratio | 2.724 | 2.684 | -0.039 | 0.079 | -0.5 |
| w3b | 0.5 | observed minus NB zero (points) | -5.362 | -5.307 | +0.054 | 0.182 | +0.3 |
| w3b | 0.5 | share causing 80% (points) | 26.560 | 25.327 | -1.233 | 0.848 | -1.5 |
| w3b | 0.5 | home share (points) | 30.480 | 30.171 | -0.309 | 0.500 | -0.6 |
| w3b | 0.5 | top-10 venue-day share (points) | 95.124 | 94.397 | -0.727 | 0.953 | -0.8 |

## Run B: cells

Both B cells use seeds 77001 to 77012 (or more, as stated) and the command lines of round 13. The negative binomial with the published mean 0.88 and k 0.27 has zero share 67.6% and share above five 3.6% (checked). B1 is calibrated to day 28; B2 is not (the epidemic shrinks; day 28 is the cumulative infection count).

| world | cell | replicates | index cases | coefficient | tuned parameter | day 28 infections | early R (90%) | likelihood k (90%) | moment k | ratio | zero share % | 1-5 % | above 5 % | NB own above 5 % | above 5 / NB own | at least 20 % | at least 50 % | maximum | p99 | obs. minus NB zero, points (90%) | 80% share % | home % | hh SAR | top-10 offspring | top-10 same-hh % | top-10 venue-day % | distinct venues |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| World 1 | round 12 reference (k about 0.35, usual matching) | 12 | 13593 | 0.0004992 | round-12 value | 6292 | 1.405 (1.370 to 1.441) | 0.357 (0.346 to 0.369) | 0.338 | 1.06 | 56.6 | 36.4 | 7.0 | 7.0 | 1.00 | 0.21 | 0.007 | 54 | 12 | 0.04 (-0.11 to 0.19) | 21.5 | 34.2 | 0.00165 | 17.3 | 17.7 | 19.8 | 6.2 |
| World 1 | **B1**: k 0.27, usual matching | 12 | 13197 | 0.0005152 | shape 0.24 | 6274 | 1.407 (1.344 to 1.478) | 0.263 (0.254 to 0.272) | 0.241 | 1.09 | 61.4 | 31.3 | 7.3 | 7.6 | 0.96 | 0.44 | 0.000 | 43 | 14 | -0.11 (-0.20 to -0.00) | 17.6 | 31.6 | 0.00138 | 21.1 | 18.7 | 20.2 | 6.3 |
| World 1 | **B2**: k 0.27, mean 0.88, five-trial protocol | 24 | 11322 | 0.0002967 | shape 0.2437 | 1565 | 0.880 (0.846 to 0.915) | 0.278 (0.268 to 0.288) | 0.256 | 1.08 | 67.2 | 29.4 | 3.4 | 3.6 | 0.96 | 0.10 | 0.000 | 28 | 9 | -0.09 (-0.18 to 0.01) | 16.8 | 36.7 | 0.00074 | 10.2 | 25.5 | 25.2 | 4.4 |
| World 2b | round 12 reference (k about 0.35, usual matching) | 12 | 9737 | 0.0001172 | round-12 value | 6196 | 1.550 (1.498 to 1.598) | 0.365 (0.354 to 0.378) | 0.257 | 1.42 | 53.5 | 39.4 | 7.1 | 8.0 | 0.88 | 0.64 | 0.010 | 57 | 15 | -1.06 (-1.21 to -0.90) | 21.7 | 14.1 | 0.00083 | 21.5 | 6.5 | 14.5 | 9.4 |
| World 2b | **B1**: k 0.27, usual matching | 12 | 10301 | 0.0001169 | shape 0.40 | 6285 | 1.573 (1.509 to 1.645) | 0.270 (0.260 to 0.282) | 0.170 | 1.59 | 58.8 | 34.0 | 7.2 | 8.7 | 0.83 | 0.93 | 0.058 | 126 | 19 | -0.72 (-0.85 to -0.60) | 17.9 | 13.7 | 0.00077 | 27.7 | 6.9 | 13.9 | 9.8 |
| World 2b | **B2**: k 0.27, mean 0.88, five-trial protocol | 36 | 11298 | 7.114e-05 | shape 0.3966 | 1276 | 0.917 (0.870 to 0.963) | 0.257 (0.242 to 0.274) | 0.162 | 1.59 | 67.1 | 29.5 | 3.4 | 4.0 | 0.84 | 0.32 | 0.018 | 54 | 11 | -0.58 (-0.69 to -0.45) | 16.0 | 17.2 | 0.00040 | 10.7 | 11.3 | 23.2 | 6.1 |
| World 3b | round 12 reference (k about 0.35, usual matching) | 12 | 13655 | 0.0001301 | round-12 value | 6294 | 1.482 (1.428 to 1.527) | 0.306 (0.295 to 0.317) | 0.157 | 1.95 | 54.4 | 39.6 | 6.0 | 7.9 | 0.76 | 1.70 | 0.000 | 46 | 22 | -3.90 (-4.03 to -3.77) | 16.8 | 21.3 | 0.00148 | 25.2 | 2.9 | 91.5 | 1.7 |
| World 3b | **B1**: k 0.27, usual matching | 12 | 13620 | 0.0001059 | event rate 0.17 | 6281 | 1.451 (1.402 to 1.501) | 0.248 (0.239 to 0.258) | 0.152 | 1.63 | 59.2 | 34.1 | 6.7 | 8.0 | 0.84 | 1.30 | 0.000 | 40 | 21 | -2.91 (-3.05 to -2.76) | 13.7 | 18.2 | 0.00125 | 24.5 | 2.6 | 87.0 | 1.8 |
| World 3b | **B2**: k 0.27, mean 0.88, five-trial protocol | 36 | 11617 | 9.172e-05 | event rate 0.05956 | 1064 | 0.767 (0.721 to 0.811) | 0.296 (0.277 to 0.318) | 0.117 | 2.54 | 66.1 | 31.4 | 2.5 | 2.6 | 0.97 | 0.46 | 0.000 | 26 | 16 | -2.43 (-2.55 to -2.30) | 18.6 | 30.3 | 0.00068 | 11.5 | 11.1 | 83.4 | 1.5 |
| World 3b | **B2, extended search** (beyond the trial limit) | 24 | 9824 | 9.046e-05 | event rate 0.08435 | 1360 | 0.867 (0.833 to 0.898) | 0.265 (0.252 to 0.279) | 0.121 | 2.19 | 65.7 | 30.9 | 3.4 | 3.6 | 0.94 | 0.41 | 0.000 | 40 | 16 | -2.34 (-2.43 to -2.24) | 16.9 | 25.7 | 0.00062 | 15.1 | 6.0 | 93.2 | 1.5 |

`NB own above 5` is the share above five of the negative binomial at the cell's own likelihood k and mean; `above 5 / NB own` is the ratio of the two. Intervals for every statistic are in `69_b_cells_summary.csv`.

### Tuning logs

B1: one trial of 6 replicates (calibrated to day 28 on 76001 to 76006) per world was inside |k - 0.27| of at most 0.02; the final 12 replicates (77001 to 77012, calibrated) were inside 0.24 to 0.30 at the first attempt in all three worlds. B2: coefficient and tuned parameter updated together in each trial (see `69a_review_of_note68.md`, point 4). B2 world 3b reached no point inside both windows in five trials (k jumps from 0.17 to 0.43 when the rate falls below about 0.06, and the mean follows the coefficient and the rate together); the extended search fitted a log-linear model of mean and k in coefficient and rate to all points of that world with rate up to 0.13 and solved it for mean 0.88 and k 0.27 (first proposal: coefficient 8.7e-05, rate 0.081, which gave mean 0.843 and k 0.267 on 6 replicates).

| world | stage | trial | tuned parameter | coefficient | day 28 | early R | likelihood k | index cases | replicates |
|---|---|---|---|---|---|---|---|---|---|
| w1 | B1 | 1 | 0.24 | 0.0005152 | 6284 | 1.467 | 0.257 | 6259 | 6 |
| w1 | B2 | 1 | 0.24 | 0.0003349 | 1862 | 1.013 | 0.263 | 3166 | 6 |
| w1 | B2 | 2 | 0.2465 | 0.0002864 | 1405 | 0.876 | 0.269 | 2615 | 6 |
| w1 | B1_final | r14_b1final_w1 | 0.24 | 0.0005152 | 6274 | 1.407 | 0.263 |  |  |
| w1 | B2_final | b2final_w1 | 0.2465 | 0.0002864 | 1504 | 0.852 | 0.273 | 5581 | 12 |
| w1 | B2_final | b2final-c1_w1 | 0.2437 | 0.0002967 | 1591 | 0.877 | 0.269 | 5844 | 12 |
| w2b | B1 | 1 | 0.4 | 0.0001219 | 6274 | 1.557 | 0.267 | 4502 | 6 |
| w2b | B2 | 1 | 0.4 | 7.597e-05 | 1313 | 0.961 | 0.251 | 1899 | 6 |
| w2b | B2 | 2 | 0.444 | 6.889e-05 | 1048 | 0.859 | 0.272 | 1615 | 6 |
| w2b | B2 | 3 | 0.4395 | 7.037e-05 | 1091 | 0.876 | 0.270 | 1650 | 6 |
| w2b | B1_final | r14_b1final_w2b | 0.4 | 0.0001169 | 6285 | 1.573 | 0.270 |  |  |
| w2b | B2_final | b2final_w2b | 0.4395 | 7.037e-05 | 1216 | 0.828 | 0.287 | 3746 | 12 |
| w2b | B2_final | b2final-c1_w2b | 0.4031 | 7.526e-05 | 1437 | 0.926 | 0.273 | 4239 | 12 |
| w2b | B2_final | b2final-c2_w2b | 0.3966 | 7.114e-05 | 1239 | 0.842 | 0.268 | 3796 | 12 |
| w3b | B1 | 1 | 0.17 | 0.0001124 | 6111 | 1.476 | 0.279 | 6481 | 6 |
| w3b | B2 | 1 | 0.17 | 5.294e-05 | 1799 | 1.013 | 0.173 | 3002 | 6 |
| w3b | B2 | 2 | 0.1136 | 4.527e-05 | 894 | 0.755 | 0.161 | 1553 | 6 |
| w3b | B2 | 3 | 0.07115 | 4.912e-05 | 735 | 0.571 | 0.169 | 1156 | 6 |
| w3b | B2 | 4 | 0.04667 | 7.944e-05 | 753 | 0.522 | 0.430 | 1386 | 6 |
| w3b | B2 | 5 | 0.05757 | 0.000142 | 1678 | 0.964 | 0.426 | 3008 | 6 |
| w3b | B2ext | 1 | 0.0812 | 8.708e-05 | 1144 | 0.843 | 0.267 | 2057 | 6 |
| w3b | B2ext | 2 | 0.08169 | 8.797e-05 | 1088 | 0.804 | 0.290 | 2036 | 6 |
| w3b | B2ext | 3 | 0.08428 | 8.782e-05 | 1322 | 0.922 | 0.262 | 2307 | 6 |
| w3b | B2ext | 4 | 0.08319 | 8.777e-05 | 1234 | 0.832 | 0.282 | 2147 | 6 |
| w3b | B1_final | r14_b1final_w3b | 0.17 | 0.0001059 | 6281 | 1.451 | 0.248 |  |  |
| w3b | B2_final | b2final_w3b | 0.1136 | 4.527e-05 | 902 | 0.681 | 0.165 | 3147 | 12 |
| w3b | B2_final | b2final-c1_w3b | 0.07302 | 6.02e-05 | 878 | 0.602 | 0.215 | 3159 | 12 |
| w3b | B2_final | b2final-c2_w3b | 0.05956 | 9.172e-05 | 1098 | 0.747 | 0.307 | 4046 | 12 |
| w3b | B2ext_final | b2extfinal_w3b | 0.0812 | 8.708e-05 | 1325 | 0.845 | 0.252 | 4699 | 12 |
| w3b | B2ext_final | b2extfinal-c1_w3b | 0.08303 | 8.946e-05 | 1327 | 0.812 | 0.272 | 4758 | 12 |
| w3b | B2ext_final | b2extfinal-c2_w3b | 0.08435 | 9.046e-05 | 1366 | 0.855 | 0.259 | 5036 | 12 |

Final cells and replicate counts: B2 world 1 24 replicates (12 + 12, seeds 77001 to 77024), world 2b 36 (77001 to 77036), world 3b five-trial protocol 36, extended search 24; the extensions were run because the 12-replicate cells had fewer than 8,000 index cases (5,844; 3,796; 4,046; 5,036). There is no command-line option for the number of initial infections and the agent file may not be edited, so I used replicates, as the note allows; all replicates use the same coefficient and parameter. World 2b still needed 36 (24 gave 7,497).

## What this says about reachability

- At the published mean 0.88 all three worlds can be put at likelihood k 0.26 to 0.28 with the shares of the published compilation (zero about 67%, 1 to 5 about 30%, above five about 3.4%). In world 3b the combination needs more background transmission relative to events (coefficient 9.0e-05 against 1.06e-04 in B1, event rate 0.084 against 0.17), so the share of index-case offspring infected at events is lower than in B1 (56% in the extended-search cell, 50% in the protocol cell, against 70% in B1 and 64% in round 12).
- The five-trial protocol alone does not find that point in world 3b because the two quantities interact (k rises with the coefficient at fixed rate; the mean rises with both); this is a limit of the search I used, not of the world.

## Limits

- Mean offspring of a 12-replicate cell has a standard error of about 0.02 to 0.03 at mean 0.9 (90% intervals 0.85 to 0.92 for 24 replicates, 0.87 to 0.96 at 36), the same order as the 3% window; the final pooled values of the B2 cells are reported with their intervals, and world 2b misses the window on its final pooled value.
- B2 cells have 24 or 36 replicates, B1 and run A have 12; the intervals of B2 are narrower for that reason.
- Run A is one more seed set for six cells; between-set SD per cell is not estimated (two sets); it is a screen, as stated in the note.
- The extended world-3b search used four trials and two corrections beyond the five-trial limit; I report both the protocol cell and the extended cell.

## Files

On Drive: this file, `69a_review_of_note68.md`, `69_upload_index.md`, `69_b_calibration_log.csv`, `69_tuning_log.csv`. Not on Drive (in the repository, `superspreader/`; sizes, row counts and checksums in `69_upload_index.md`): `69_a_cells_summary.csv`, `69_b_cells_summary.csv`, `69_runA_two_set.csv`, `69_a_calibration_log.csv` and the four per-replicate files `69_a_replicate_summary.csv`, `69_a_replicate_histograms.csv`, `69_b_replicate_summary.csv`, `69_b_replicate_histograms.csv`. I did not upload these through the connector: it requires typing the content into the call, and a test piece came back one byte short (a digit lost in a 17-digit number), so I deleted it. Note 68 asked for the per-replicate files on Drive; they need a file copy, as in round 13.
