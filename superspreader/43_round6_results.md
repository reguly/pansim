# ACT-049 note 43: round 6

16 October 2026. Instructions are note 42. Reads with notes 37, 38 and 41. Review of note 42 before running: `43a_review_of_note42.md` (already uploaded). Nothing in `locations1.json`, `agents2.json`, `locations3.json` or `agents4.json` was edited. The ward files for R6-5 are new files under `study/inputs/r65_w*/`.

Definitions as in note 38 unless stated. Trace day is `timestamp // 144`. An index case is infected on days 1 to 10 with a known infector; its offspring are the infections it causes on or before day + 14; initial `-r` seeds are excluded. "Above 5" means strictly more than 5, "at least 20" means 20 or more. Moment k is the pooled method of moments (variance with divisor n - 1) and likelihood k is the negative-binomial maximum-likelihood k with the mean fixed at the sample mean, both on the pooled index-case offspring of all replicates. Every early-offspring table gives the share with no offspring next to the negative-binomial value at each estimator. A 90% interval is a replicate bootstrap, 1,000 draws, 5th and 95th percentiles. The bootstrap seed is 20261016. CSV files carry six significant digits.

New or changed simulator options (all in `include/policies/infectionPolicies.h`, uncommitted): `--episodeTrace PATH` (R6-2) and `--eventGroupSize M`, `--eventDurationHours H`, `--eventGroupLog PATH` (R6-7). Each is off by default. With the options off, two checks give byte-identical output to the previous binary: a 12-week E run with `--infectionTrace` (`build_r62`), and a 3-week venue-day event run with `--infectionTrace` and `--eventLog` (`build_r67`). The older binary, `build_gpu/panSim`, ran R6-1, R6-3, R6-4, R6-5 and R6-6. The seed of any single run is in its `command.json`.

## Deviations, and errors found in note 42

1. **Errors in the note** are in `43a_review_of_note42.md`. In short: R6-1 prediction 1 was already contradicted for the none shape by round 5 (and it is also contradicted for a = 1.0 and a = 0.5 here); prediction 3 is met by the existing E cell, and "narrower" is ambiguous (I read it as a smaller shape); R6-4 prediction (i) compares across maps and matching; R6-2 prediction (ii) could fail from structural correlation, so A0 was added as a control; R6-5 prediction (i) depends on the recalibration of the unsplit arm. A twelfth item belongs here: R6-7 says the zero share stays near 0.30 "as for venue-day events", but venue-day events raised it to 0.339 at k near 0.3 in round 5 and in R6-1.
2. **R6-3 needed no epidemic runs, but traits for 66 of 72 replicates were not stored.** Only `rep1101` of each arm had `agents_trait.csv`. The other eleven replicates of each arm were re-dumped by a one-week run with the stored command (traits depend on the seed and the trait flags only), and the re-dump of `rep1101` is byte-identical to the stored file in all six arms. The traces are the stored PS1 traces. The runs are on the old map (`agents1.json`, `locations0.json`), as the PS1 runs were.
3. **R6-1.** Four of the 16 cells are reused (none by 0, none by 600, none by 1,091, and 0.3 by 0 = E), as the note allowed. All cells are within 3% of 6,211.25 on the reported 12 replicates (-2.6% to +2.2%).
4. **R6-2.** A0 was added as a control arm (proposed in note 43a). Vaccination was switched off (`--immunizationStart 100000`); every other R6-2 run uses the earlier coefficients, which were not recalibrated (day 28 averages 5,913, 6,104, 6,285 for A0, E, P0, against the R3-5 target 6,220). The per-pair file `43_r62_repeat_pairs.csv` (34,036 rows, 849 KB) is in the local folder `superspreader/` but was **not uploaded** to Drive, because its size makes the upload costly; `43_r62_pairs_joint.csv` (arm, similar-incidence flag, offspring in episode 1, offspring in episode 2, pairs) carries everything needed to recompute the correlations. Say if the per-pair file is wanted and it will be sent in pieces.
5. **R6-4.** Day-28 matching is to 6,000 (not 6,211) within 3%; the reported replicates are 5,883 to 6,173 (-1.9% to +2.9%). Because that tolerance still moves the final size, a day-28-adjusted ratio is reported next to the raw one. The calibrations used 4-week runs of the same twelve seeds and the 16-week runs reuse them.
6. **R6-5.** The four-seed pilot can pass while the 40-replicate mean misses the 3% band (the standard error of the pilot is about 7%), so extra 40-replicate sets were run after each miss. Three of the five arms have superseded sets, all reported. The first sets used the mean of the per-replicate ratios as the criterion rather than the pooled mean offspring. The final sets are within 3% on the pooled mean. W30 is the R3-4 set, reused.
7. **R6-6.** The alpha = 1 cell is the R3-6 baseline, reused.
8. **R6-7 was implemented**, which took a new simulator mechanism (described in section 8). The factor alone cannot reach moment k 0.3 at the event rate of 0.3% (the group attack rate saturates; section 8), so the factor is fixed at a saturated value and the event rate is the tuned parameter.
9. **No attempt was made to commit.** The simulator changes, the scripts (`study/run_round6.py`, `study/analyze_round6.py`, `study/r6stats.py`, `study/report_tables.py`, `study/build_wards_r65.py`, `study/dump_traits_r63.py`) and the results folder `study/results/round6/` are uncommitted in the working tree. The two new build directories are `build_r62` and `build_r67`.

## 1. Registered predictions, scored

| task | prediction | result |
|---|---|---|
| R6-1 (1) | zero share within 0.03 between factor 0 and 1,091, each shape | failed in three of four shapes (none +0.042, a = 1.0 +0.037, a = 0.5 +0.031; a = 0.3 +0.008 met) |
| R6-1 (2) | likelihood k within 20% of moment k under 5% events share, at least 1.5 times over 10% | failed in one cell (a = 0.3 by 300, ratio 1.25); the over-10% half is met in all four cells |
| R6-1 (3) | a cell with moment k 0.25 to 0.35 and zero share within 0.03 of its likelihood-NB value, all such cells a at most 0.5 | met (E, a = 0.3 by 300, a = 0.5 by 300); only E qualifies against the moment-k negative binomial. Upper bound on events share: 8.2% (6.3 to 10.0) |
| R6-2 (i) | P0 Pearson at least 0.2 | met, 0.544 (0.512 to 0.572) |
| R6-2 (ii) | E within plus or minus 0.05 of zero | met, -0.014 (-0.026 to -0.003) |
| R6-2 (iii) | fewer than 500 pairs for 80% power under P0 | met, 25 pairs (Pearson), 29 (Spearman) |
| R6-3 (i) | index-case shape within 15% of a + rho | met in all four gamma arms (8% to 13% below) |
| R6-3 (ii) | population-based k at least 1.5 times too low; index-case-based within 20% | first half met (2.0 to 4.1); second half met for the four gamma arms by the moment estimator (17% to 19% low), failed for P100ln (31%) and for all five by the likelihood estimator; P0 about 21% (moment) to 27% (likelihood) low as expected |
| R6-4 (i) | coupled-arm moment k within 15% of PS1 | met (-8.8% to +4.7%) |
| R6-4 (ii) | P25k day-112 count 0.62 to 0.95 of E's | failed, 0.522 (0.515 to 0.529) |
| R6-4 (iii) | early R of every coupled arm above E's | met (1.49 to 1.77 against 1.335) |
| R6-5 (i) | P(longest at least observed) above 0.05 at wards 10, 30, 100 and below 0.05 unsplit | failed on the unsplit clause (0.336); the other three met (0.075, 0.687, 0.223) |
| R6-5 (ii) | share of hospital cases' children also infected in hospital rises with ward size | met on the point estimates (0.067, 0.176, 0.231, 0.367, 0.553), wide intervals at the small sizes |
| R6-6 (i) | moment k decreases monotonically as alpha decreases | met (4.59, 3.68, 2.37, 1.70, 1.57) |
| R6-6 (ii) | no cell below 1.5 | met on point estimates; the alpha = 0 interval (1.45 to 1.72) includes values below 1.5 |
| R6-7 | zero share within 0.03 of the no-event baseline | met for M = 100 (0.318 at moment k 0.327), failed for M = 30 (0.361 at moment k 0.280) |

## 2. R6-1. How much of superspreading can events carry?

Configuration (a), types 5 and 8, capacity at most 100, event rate 0.3%, `locations1.json` with `agents2.json`, 4 weeks, 12 replicates per cell. A cell is a per-episode multiplier shape (`--sheddingShape`) and an event factor (`--eventFactor`). Twelve cells were run new. Four were reused from rounds 3 to 5 and are marked: none by 0 (the R3-6 baseline, directory `r36/baseline`), none by 600 and none by 1,091 (`r42/cap100_f600`, `r42/cap100_f1091`), and 0.3 by 0 (E, `r3cal/r35_E/round0`). All 16 cells are inside 3% of 6,211.25 at day 28 (the reported sets range from -2.6% to +2.2%). "Events share" is the pooled share of the index cases' offspring that were infected at an event location on an event day. A cluster is the offspring count of an index case with at least one offspring. Intervals are replicate bootstraps, 90%.

Predictions, as registered, and what happened.

| prediction | result |
|---|---|
| 1. Within each multiplier shape the zero share changes by less than 0.03 between factor 0 and factor 1,091 | **failed in three of four shapes.** none: 0.297 to 0.339, change +0.042. a = 1.0: 0.420 to 0.457, +0.037. a = 0.5: 0.502 to 0.533, +0.031. a = 0.3: 0.585 to 0.593, +0.008 (met). Round 5 already showed the none case (note 43a, item 1). Events do add non-transmitters, by 3 to 4 points |
| 2. Likelihood k within 20% of moment k where events carry under 5% of offspring, and at least 1.5 times moment k where they carry over 10% | **failed in one cell.** Under 5%: the four factor-0 cells (ratios 1.00, 1.03, 1.03, 1.07) are inside, and a = 0.3 by 300 (events share 3.0%) is outside, with a ratio of 1.25. Over 10%: all four factor-1,091 cells are above 1.5 (4.4, 3.6, 4.0 and 1.9; their events shares are 12.7%, 13.3%, 14.7% and 10.8%). The six cells with 5% to 10% are not covered by the prediction |
| 3. At least one cell has moment k from 0.25 to 0.35 and a zero share within 0.03 of its likelihood-NB value, and every such cell has a at most 0.5 | **met** (see below), with a caveat on the estimator |

Cells meeting prediction 3 (moment k from 0.25 to 0.35, zero share within 0.03 of the negative binomial at the likelihood k):

| cell | moment k (90% interval) | likelihood k | zero share | NB zero at likelihood k | NB zero at moment k | events share (90% interval) |
|---|---|---|---|---|---|---|
| a = 0.3, factor 0 (E) | 0.297 (0.280 to 0.315) | 0.319 | 0.585 | 0.586 | 0.597 | 0 |
| a = 0.3, factor 300 | 0.253 (0.222 to 0.286) | 0.317 | 0.582 | 0.585 | 0.621 | 3.0% (2.1 to 3.9) |
| a = 0.5, factor 300 | 0.276 (0.235 to 0.338) | 0.468 | 0.510 | 0.516 | 0.603 | 8.2% (6.3 to 10.0) |

No cell with no multiplier (none) or with a = 1.0 qualifies. The none by 1,091 cell has moment k 0.310 and a zero share 0.046 below its likelihood NB value (0.339 against 0.384), so it fails the shape criterion, as round 5 found.

**The upper bound asked for:** among the cells that keep both the moment k near 0.3 and the zero share, events carry at most about 8% of early offspring (a = 0.5 with factor 300: 8.2%, 6.3% to 10.0%). With a = 0.3, the multiplier that alone reproduces the shape, the qualifying cell with events carries 3.0% (2.1% to 3.9%). Larger event shares come with the zero share falling short of the data's shape: at 10.8% to 14.7% (factor 1,091) every cell has a likelihood k of 0.29 to 1.36 against moment k of 0.10 to 0.31.

Caveat on the estimator. The registered criterion uses the negative binomial at the likelihood k. Against the negative binomial at the moment k, only E qualifies: the zero share is below its moment-k value by 0.040 (a = 0.3, factor 300) and by 0.093 (a = 0.5, factor 300). Whenever events are present, the moment k is lower than the likelihood k and the moment-k negative binomial predicts more non-transmitters than the data have. The two estimators therefore disagree about shape exactly in the cells with events, which is the point of reporting both.

Grid summary (all columns for all 16 cells are in `43_r61_grid_summary.csv`, with intervals for every share, ratio and k; the joint histograms are in `43_r61_offspring.csv`):

| shape | factor | day 28 | early R | k moment | k likelihood | zero | NB zero (moment) | NB zero (likelihood) | 1 to 5 | above 5 | at least 20 | at least 50 | max | events share | cluster median | cluster p90 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| none | 0 | 6,211 | 1.41 (1.4 to 1.42) | 4.59 (4.29 to 4.92) | 4.59 (4.22 to 5) | 0.297 (0.291 to 0.303) | 0.293 | 0.293 | 0.691 | 0.0122 (0.0113 to 0.013) | 0 (0 to 0) | 0 (0 to 0) | 11 | 0 | 2 | 4 (3 to 4) |
| 1.0 | 0 | 6,218 | 1.44 (1.42 to 1.47) | 0.893 (0.847 to 0.94) | 0.92 (0.89 to 0.95) | 0.42 (0.413 to 0.425) | 0.424 | 0.42 | 0.536 | 0.0445 (0.0418 to 0.047) | 0.000226 (7.18e-05 to 0.000439) | 0 (0 to 0) | 23 | 0 | 2 | 5 (5 to 5) |
| 0.5 | 0 | 6,274 | 1.42 (1.39 to 1.45) | 0.512 (0.498 to 0.525) | 0.526 (0.513 to 0.538) | 0.502 (0.497 to 0.508) | 0.507 | 0.503 | 0.438 | 0.0595 (0.0577 to 0.0613) | 0.000825 (0.000531 to 0.00111) | 0 (0 to 0) | 30 | 0 | 2 | 6 (6 to 6) |
| 0.3 | 0 | 6,124 | 1.39 (1.36 to 1.42) | 0.297 (0.28 to 0.315) | 0.319 (0.311 to 0.328) | 0.585 (0.58 to 0.59) | 0.597 | 0.586 | 0.346 | 0.0685 (0.0653 to 0.0723) | 0.00265 (0.00209 to 0.00321) | 7.8e-05 (0 to 0.00022) | 63 | 0 | 2 | 7 (7 to 8) |
| none | 300 | 6,061 | 1.42 (1.4 to 1.44) | 1.39 (1.2 to 1.65) | 2.47 (2.29 to 2.7) | 0.304 (0.298 to 0.31) | 0.375 | 0.325 | 0.682 | 0.0143 (0.0127 to 0.016) | 0.000791 (0.000425 to 0.00117) | 0 (0 to 0) | 41 | 6.0% (5.0 to 7.0) | 2 | 4 (4 to 4) |
| 1.0 | 300 | 6,183 | 1.41 (1.35 to 1.45) | 0.5 (0.423 to 0.633) | 0.814 (0.775 to 0.863) | 0.429 (0.422 to 0.436) | 0.512 | 0.442 | 0.531 | 0.0405 (0.0374 to 0.0436) | 0.00158 (0.000777 to 0.0024) | 0.00015 (0 to 0.00031) | 61 | 5.9% (4.0 to 7.8) | 2 | 5 (5 to 5) |
| 0.5 | 300 | 6,052 | 1.45 (1.4 to 1.5) | 0.276 (0.235 to 0.338) | 0.468 (0.446 to 0.493) | 0.51 (0.502 to 0.518) | 0.603 | 0.516 | 0.433 | 0.0575 (0.0541 to 0.0607) | 0.00305 (0.00225 to 0.0038) | 0.00031 (8.4e-05 to 0.00052) | 104 | 8.2% (6.3 to 10.0) | 2 | 6 (6 to 6) |
| 0.3 | 300 | 6,196 | 1.41 (1.37 to 1.45) | 0.253 (0.222 to 0.286) | 0.317 (0.309 to 0.326) | 0.582 (0.577 to 0.587) | 0.621 | 0.585 | 0.35 | 0.0682 (0.0646 to 0.072) | 0.00282 (0.00223 to 0.00349) | 0.00016 (0 to 0.00033) | 109 | 3.0% (2.1 to 3.9) | 2 | 7 (7 to 8) |
| none | 600 | 6,064 | 1.4 (1.37 to 1.43) | 0.641 (0.544 to 0.777) | 1.7 (1.55 to 1.87) | 0.326 (0.321 to 0.331) | 0.476 | 0.36 | 0.66 | 0.0143 (0.0127 to 0.016) | 0.00257 (0.0019 to 0.00331) | 0 (0 to 0) | 47 | 9.5% (8.1 to 11.0) | 2 | 3 (3 to 4) |
| 1.0 | 600 | 6,156 | 1.39 (1.36 to 1.42) | 0.378 (0.309 to 0.478) | 0.776 (0.741 to 0.815) | 0.439 (0.435 to 0.443) | 0.558 | 0.451 | 0.523 | 0.0379 (0.0364 to 0.0395) | 0.00195 (0.0012 to 0.00275) | 0.00037 (0.00016 to 0.00057) | 95 | 7.4% (5.7 to 9.1) | 2 | 5 (5 to 5) |
| 0.5 | 600 | 6,232 | 1.43 (1.36 to 1.49) | 0.24 (0.191 to 0.317) | 0.447 (0.431 to 0.467) | 0.518 (0.513 to 0.524) | 0.628 | 0.527 | 0.427 | 0.0549 (0.0508 to 0.0584) | 0.00344 (0.00223 to 0.00463) | 0.00046 (8e-05 to 0.00088) | 121 | 8.3% (5.4 to 11.2) | 2 | 6 (6 to 6) |
| 0.3 | 600 | 6,344 | 1.44 (1.4 to 1.49) | 0.175 (0.138 to 0.222) | 0.298 (0.287 to 0.31) | 0.587 (0.583 to 0.593) | 0.678 | 0.591 | 0.345 | 0.0679 (0.0647 to 0.0712) | 0.00483 (0.00381 to 0.00607) | 0.00071 (0.00042 to 0.001) | 155 | 8.0% (5.3 to 11.0) | 2 | 7 (7 to 7) |
| none | 1091 | 6,194 | 1.39 (1.36 to 1.42) | 0.31 (0.275 to 0.353) | 1.36 (1.26 to 1.47) | 0.339 (0.334 to 0.343) | 0.59 | 0.384 | 0.649 | 0.0126 (0.0112 to 0.0141) | 0.00388 (0.00309 to 0.00467) | 0.00039 (0.00016 to 0.00062) | 91 | 12.7% (10.9 to 14.6) | 2 | 3 (3 to 3) |
| 1.0 | 1091 | 6,190 | 1.41 (1.36 to 1.46) | 0.173 (0.136 to 0.242) | 0.627 (0.587 to 0.675) | 0.457 (0.45 to 0.464) | 0.682 | 0.478 | 0.507 | 0.0357 (0.0335 to 0.0382) | 0.00353 (0.00279 to 0.00434) | 0.0012 (0.00056 to 0.0018) | 156 | 13.3% (10.4 to 16.2) | 2 | 5 (5 to 5) |
| 0.5 | 1091 | 6,346 | 1.41 (1.34 to 1.48) | 0.0995 (0.0762 to 0.16) | 0.397 (0.37 to 0.432) | 0.533 (0.527 to 0.539) | 0.763 | 0.548 | 0.419 | 0.0473 (0.043 to 0.0516) | 0.00328 (0.00224 to 0.00424) | 0.0012 (0.00075 to 0.0018) | 214 | 14.7% (10.7 to 18.4) | 2 | 6 (5 to 6) |
| 0.3 | 1091 | 6,178 | 1.39 (1.35 to 1.44) | 0.155 (0.128 to 0.197) | 0.294 (0.278 to 0.31) | 0.593 (0.587 to 0.598) | 0.7 | 0.599 | 0.346 | 0.0614 (0.058 to 0.0644) | 0.0044 (0.00339 to 0.00522) | 0.0011 (0.00051 to 0.0017) | 110 | 10.8% (7.5 to 13.8) | 2 | 7 (7 to 7) |

Tail shares against the negative binomial at each estimator (data, then the negative binomial at the moment k, then at the likelihood k):

| shape | factor | above 5 data | NB moment | NB likelihood | at least 20 data | NB moment | NB likelihood | at least 50 data | NB moment | NB likelihood |
|---|---|---|---|---|---|---|---|---|---|---|
| none | 0 | 0.0122 | 0.011 | 0.0111 | 0 | 5.44e-10 | 5.49e-10 | 0 | 1.48e-27 | 1.53e-27 |
| 1.0 | 0 | 0.0445 | 0.0461 | 0.0451 | 0.000226 | 4.87e-05 | 4.19e-05 | 0 | 2.37e-11 | 1.49e-11 |
| 0.5 | 0 | 0.0595 | 0.0616 | 0.0608 | 0.000825 | 0.00051 | 0.000462 | 0 | 3.3e-08 | 2.45e-08 |
| 0.3 | 0 | 0.0685 | 0.0722 | 0.0708 | 0.00265 | 0.00246 | 0.00205 | 7.78e-05 | 4.08e-06 | 2.35e-06 |
| none | 300 | 0.0143 | 0.0317 | 0.0194 | 0.000791 | 3.42e-06 | 6.73e-08 | 0 | 6.31e-15 | 1.91e-20 |
| 1.0 | 300 | 0.0405 | 0.0612 | 0.0461 | 0.00158 | 0.000527 | 6.38e-05 | 0.00015 | 3.77e-08 | 6.11e-11 |
| 0.5 | 300 | 0.0575 | 0.0782 | 0.0666 | 0.00305 | 0.00349 | 0.000787 | 0.000312 | 1.04e-05 | 1.15e-07 |
| 0.3 | 300 | 0.0682 | 0.0762 | 0.0725 | 0.00282 | 0.00379 | 0.0022 | 0.000157 | 1.45e-05 | 2.82e-06 |
| none | 600 | 0.0143 | 0.053 | 0.0254 | 0.00257 | 0.000187 | 7.71e-07 | 0 | 1.66e-09 | 6.19e-17 |
| 1.0 | 600 | 0.0379 | 0.0674 | 0.0464 | 0.00195 | 0.00127 | 7.39e-05 | 0.000374 | 5.61e-07 | 1.01e-10 |
| 0.5 | 600 | 0.0549 | 0.0782 | 0.0658 | 0.00344 | 0.00444 | 0.000841 | 0.000459 | 2.28e-05 | 1.48e-07 |
| 0.3 | 600 | 0.0679 | 0.081 | 0.0762 | 0.00483 | 0.00798 | 0.00284 | 0.000713 | 0.000135 | 5.7e-06 |
| none | 1091 | 0.0126 | 0.0715 | 0.0301 | 0.00388 | 0.00221 | 3.11e-06 | 0.000388 | 2.96e-06 | 5.48e-15 |
| 1.0 | 1091 | 0.0357 | 0.079 | 0.0544 | 0.00353 | 0.00763 | 0.000215 | 0.00115 | 0.000125 | 2.48e-09 |
| 0.5 | 1091 | 0.0473 | 0.0753 | 0.0674 | 0.00328 | 0.0143 | 0.00115 | 0.00123 | 0.000964 | 4e-07 |
| 0.3 | 1091 | 0.0614 | 0.0782 | 0.073 | 0.0044 | 0.0087 | 0.00259 | 0.00108 | 0.000193 | 4.7e-06 |

Reading, limited to what the table shows. The multiplier alone fixes both the moment k and the zero share together (a = 0.5: 0.512 and 0.502; a = 0.3: 0.297 and 0.585; each close to its negative binomial). Events alone (none row) lower the moment k from 4.6 to 0.31 at factor 1,091 but leave the zero share at 0.34, where a negative binomial of that moment k would have 0.59. In the grid, the likelihood k never falls below 0.29 where events carry more than 10% of offspring. The events share of offspring is 3% to 15% in every cell with events, and it rises with the factor within each shape.


## 3. R6-2. Would we recognise a superspreader twice?

**How reinfection works in the model.** An agent leaves the infectious states, passes through R (mean 21 days, at most 42) and returns to S. Protection after infection is the prior-infection term of `include/immunization.h` (case 1). For the same variant the protection against infection starts at 0.95 and falls by 0.003 per week, so the hazard multiplier is 0.05 just after recovery and rises by about 0.003 per week of age. There is one variant and no drift. Vaccination, which starts on day 96 by default, was switched off for this task (`--immunizationStart 100000`) so that only infection-acquired protection acts. The reinfection counter (REINF column of the daily table) at day 112 averages 1,789 (A0), 1,959 (E) and 1,959 (P0) per replicate.

**Horizon.** With the 8 replicates run, the number of agents with two logged episodes whose second episode starts at least 14 days before the end of the run (so both offspring counts are complete) is 1,180 (P0) at 10 weeks, 3,604 at 12 weeks and 11,715 at 16 weeks. So 2,000 pairs are reached at about 11 weeks (a single replicate at 16 weeks gives about 1,460). The runs are 16 weeks.

**Trace change.** A new option `--episodeTrace PATH` (in `include/policies/infectionPolicies.h`, not committed) writes one row per infection episode at the time of infection: agent, episode number, infector, the infector's own infection timestamp (which identifies the infector's episode), location, location type, timestamp, shed multiplier, the infector's shed multiplier, occupancy and infectious presence. It adds no random draw and changes no other output: a 12-week E run with and without it has an identical `--infectionTrace` file, and the latest-episode rows of the new file match the old trace for all 68,922 agents. Initial `-r` seeds have no row for their first episode. The build is `build_r62`.

Arms: P0 (persistent gamma trait, shape 0.3, no coupling), E (per-episode multiplier, shape 0.3) and, added, A0 (no multiplier, no trait), 8 replicates each, 16 weeks, `locations1.json` with `agents2.json`, coefficients 0.00041 (A0), 0.000497841 (E) and 0.000497259 (P0) from R3-5. They were not recalibrated; day 28 averages 5,913 (A0), 6,104 (E) and 6,285 (P0), against the R3-5 target of 6,220 (-4.9%, -1.9% and +1.0%). Offspring of an episode are the children whose infector is that agent and whose infector timestamp is that episode's timestamp, infected within 14 days of it. A pair is an agent with logged episodes 1 and 2 where day 2 + 14 is inside the run. Where two episodes have "similar incidence", the 7-day centred mean of daily new infections on the day of the second infection is between 0.5 and 2 times that on the day of the first (62% to 64% of the pairs qualify). The correlation intervals are replicate bootstraps (90%); the Fisher-z intervals, which treat pairs as independent, are in `43_r62_summary.csv`. Power: pairs needed = ((1.960 + 0.842) / atanh(r))^2 + 3.

| arm | infected agents | agents with two logged episodes | three or more | pairs, both observed | mean offspring ep 1 / ep 2 | Pearson | Spearman | pairs, similar incidence | Pearson, similar | Spearman, similar | pairs for 80% power (Pearson / Spearman) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P0 | 734,894 | 14,781 | 96 | 11,715 | 1.07 / 0.622 | 0.544 (0.512 to 0.572) | 0.507 (0.488 to 0.523) | 7,350 | 0.528 (0.497 to 0.557) | 0.504 (0.484 to 0.519) | 25 / 29 |
| E | 735,735 | 14,752 | 92 | 11,615 | 1.09 / 0.727 | -0.0143 (-0.0263 to -0.00299) | -0.0369 (-0.0551 to -0.0171) | 7,391 | -0.016 (-0.0287 to -0.00286) | -0.0499 (-0.064 to -0.0358) | not applicable (correlation near zero) |
| A0 | 782,742 | 13,392 | 82 | 10,706 | 1.26 / 0.625 | 3.1e-05 (-0.017 to 0.0189) | 0.00555 (-0.00954 to 0.0215) | 6,658 | 0.00504 (-0.0126 to 0.0234) | 0.00766 (-0.0104 to 0.0244) | not applicable (correlation near zero) |

Pairs with both episodes observed, by horizon (8 replicates):

| horizon (weeks) | P0 pairs, 8 replicates | E pairs, 8 replicates | A0 pairs, 8 replicates |
|---|---|---|---|
| 4 | 8 | 3 | 3 |
| 6 | 66 | 73 | 67 |
| 8 | 284 | 313 | 295 |
| 10 | 1,180 | 1,100 | 1,122 |
| 12 | 3,604 | 3,453 | 3,315 |
| 14 | 7,583 | 7,257 | 7,040 |
| 16 | 11,715 | 11,615 | 10,706 |

Predictions, as registered.

| prediction | result |
|---|---|
| (i) P0 Pearson correlation at least 0.2 | **met.** 0.544 (0.512 to 0.572); Spearman 0.507 (0.488 to 0.523). With similar incidence 0.528 (0.497 to 0.557) and 0.504 |
| (ii) E within plus or minus 0.05 of zero | **met.** Pearson -0.014 (-0.026 to -0.003), Spearman -0.037 (-0.055 to -0.017). The interval excludes zero by a small margin; with similar incidence Pearson is -0.016 and Spearman -0.050 |
| (iii) Fewer than 500 pairs needed for 80% power under P0 | **met.** 25 pairs for the Pearson 0.544 and 29 for the Spearman 0.507 (26 with the similar-incidence Pearson 0.528) |

The A0 control (no multiplier, no trait) has a correlation of 0.000 (-0.017 to 0.019): in this model, agents' fixed home, school, work and schedule give no repeat correlation of offspring. All of P0's correlation therefore comes from the persistent trait, and the per-episode multiplier produces none. Mean offspring is lower in the second episode in every arm (P0 1.07 to 0.62, E 1.09 to 0.73, A0 1.26 to 0.62) because the second episodes fall later in the epidemic; the similar-incidence restriction leaves the correlations unchanged within 0.02 for P0 and E.


## 4. R6-3. What does a contact survey see?

No new epidemic runs. Traits are stored for one replicate per arm (`rep1101/agents_trait.csv`). For the other eleven replicates of each of P0, P25, P50, P100, P25k and P100ln (old map, `agents1.json` with `locations0.json`, the PS1 runs, 12 replicates each) the trait was re-written by a one-week run with the stored command; traits depend on the seed and the trait flags only. The re-dump for `rep1101` is byte-identical to the stored file in all six arms. Index cases are infected on days 1 to 10 with a known infector. Shapes are the maximum-likelihood gamma shape with free scale (for P100ln, one over the squared coefficient of variation). The predictions use `1 + 1/k = (1 + 1/s)(1 + 1/4.66)`, with 4.66 the PS1 A0 early k (old map). Intervals are replicate bootstraps, 90%. Observed k is the pooled estimate over 12 replicates, by both estimators. Columns "fitted shape" and "a + rho" are two ways of choosing s for the index-case prediction.

| arm | a + rho | shape, population | shape, index cases | shape, all infected | mean trait pop / index / all | predicted k, population | predicted k, index (fitted shape) | predicted k, index (a + rho) | observed k moment | observed k likelihood | obs/pred pop (moment) | obs/pred index (moment) | obs/pred index (likelihood) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P0 | 0.3 | 0.3 (0.3 to 0.301) | 0.299 (0.294 to 0.305) | 0.301 (0.3 to 0.301) | 0.999 / 0.996 / 1 | 0.235 (0.234 to 0.235) | 0.234 (0.23 to 0.238) | 0.235 | 0.295 (0.272 to 0.321) | 0.323 (0.308 to 0.337) | 1.26 | 1.26 | 1.38 |
| P25 | 0.55 | 0.3 (0.3 to 0.301) | 0.506 (0.498 to 0.514) | 0.482 (0.48 to 0.484) | 0.999 / 1.65 / 1.55 | 0.235 (0.234 to 0.235) | 0.382 (0.377 to 0.388) | 0.413 | 0.471 (0.43 to 0.512) | 0.514 (0.484 to 0.545) | 2.01 | 1.23 | 1.34 |
| P50 | 0.8 | 0.3 (0.3 to 0.301) | 0.719 (0.699 to 0.74) | 0.681 (0.678 to 0.685) | 0.999 / 2.31 / 2.15 | 0.235 (0.234 to 0.235) | 0.525 (0.512 to 0.539) | 0.577 | 0.632 (0.561 to 0.711) | 0.688 (0.64 to 0.742) | 2.69 | 1.2 | 1.31 |
| P100 | 1.3 | 0.3 (0.3 to 0.301) | 1.15 (1.11 to 1.19) | 1.02 (1.01 to 1.03) | 0.999 / 3.67 / 3.28 | 0.235 (0.234 to 0.235) | 0.787 (0.765 to 0.812) | 0.871 | 0.954 (0.869 to 1.07) | 1.01 (0.94 to 1.1) | 4.07 | 1.21 | 1.28 |
| P25k | 0.33 | 0.0801 (0.08 to 0.0803) | 0.286 (0.276 to 0.296) | 0.259 (0.258 to 0.26) | 0.998 / 3.44 / 3.14 | 0.0651 (0.065 to 0.0652) | 0.224 (0.217 to 0.232) | 0.257 | 0.27 (0.243 to 0.302) | 0.291 (0.274 to 0.312) | 4.14 | 1.2 | 1.3 |
| P100ln | n/a (lognormal) | 0.296 (0.29 to 0.303) | 0.414 (0.369 to 0.459) | 0.421 (0.408 to 0.435) | 1 / 3.1 / 2.37 | 0.232 (0.227 to 0.237) | 0.318 (0.285 to 0.35) | n/a | 0.464 (0.432 to 0.501) | 0.65 (0.629 to 0.673) | 2 | 1.46 | 2.05 |

Predictions, as registered.

| prediction | result |
|---|---|
| (i) Fitted shape among index cases within 15% of a + rho for the gamma arms | **met in all four.** P25 0.506 against 0.55 (-8%), P50 0.719 against 0.80 (-10%), P100 1.15 against 1.30 (-12%), P25k 0.286 against 0.33 (-13%). The fitted shapes are consistently 8% to 13% below a + rho. The population shape is the nominal one in every arm (0.300, 0.0801) |
| (ii) Population-based k at least 1.5 times too low in every coupled arm | **met.** Observed moment k over the population-based prediction: 2.01 (P25), 2.69 (P50), 4.07 (P100), 4.14 (P25k), 2.00 (P100ln). By the likelihood estimator the ratios are larger |
| (ii) Index-case-based prediction within 20% of observed | **met for the four gamma arms by the moment estimator, failed for P100ln, and failed for all five by the likelihood estimator.** The prediction is below the observed moment k by 18.8% (P25), 16.9% (P50), 17.5% (P100), 16.8% (P25k) and 31.5% (P100ln). Against the likelihood k it is 25.6%, 23.7%, 21.9%, 23.0% and 51.1% below. With s = a + rho the gaps are 12%, 9%, 9% and 5% for the gamma arms, as the registered note said |
| P0: the two predictions coincide and are about 25% low | **met.** Both are 0.234 to 0.235 against observed 0.295 (moment, 20.7% low) and 0.323 (likelihood, 27.5% low) |

What this says about a contact survey: the trait of the whole population has the nominal shape (0.30), but index cases carry a mean trait of 1.65 (P25) to 3.67 (P100) times the population mean (whole-population mean 1.00), and all infected agents carry 1.55 to 3.28. A model built on the population distribution underestimates the early k by a factor of 2 to 4. A model built on the distribution among index cases is 17% to 19% too low by the moment estimator, and the shape among all infected is a little narrower than among index cases (0.482 against 0.506 in P25, 1.02 against 1.15 in P100). The lognormal arm (P100ln) is the exception: its index-case distribution is not gamma, so the gamma-style relation misses its early k by 31% (moment) to 51% (likelihood).


## 5. R6-4. The coupled arms at matched growth

Arms E, P0, P25, P50, P100, P25k and P100ln as in PS1 (trait shape 0.3 and susceptibility exponent 0, 0.25, 0.5, 1 for P0, P25, P50, P100; shape 0.08 and exponent 0.25 for P25k; lognormal shape 0.3 and exponent 1 for P100ln; E is the per-episode multiplier, shape 0.3), `locations1.json` with `agents2.json`, 12 replicates, 16 weeks. Each arm's background coefficient was calibrated on 4-week runs of the same 12 seeds until the mean day-28 count was inside 3% of 6,000; the 16-week runs reuse the accepted coefficient and seeds, so their day-28 values are the calibrated ones. The accepted day-28 means are 5,883 to 6,173 (-1.9% to +2.9%). The growth rate is the least-squares slope of the log daily new infections on days 7 to 28, per replicate, averaged. "Mean trait of index cases" is the mean of the trace's `shed` column over index cases (the trait for the P arms, the per-episode multiplier for E). Intervals are replicate bootstraps, 90%.


| arm | calibrated k | day 28 | early R | k moment | k likelihood | zero (NB moment / likelihood) | growth rate 7 to 28 (per day) | doubling time (days) | day 70 | day 112 | peak prevalence | peak day | mean trait of index cases |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E | 0.000498 | 6,173 (5,638 to 6,712) | 1.34 (1.3 to 1.38) | 0.312 (0.299 to 0.325) | 0.331 (0.325 to 0.338) | 0.586 (0.595 / 0.586) | 0.0649 (0.06 to 0.069) | 10.7 | 57,993 (54,900 to 61,104) | 93,357 (92,359 to 94,375) | 15,738 (15,376 to 16,085) | 68.2 (65.8 to 71.1) | 1.02 (0.991 to 1.04) |
| P0 | 0.000497 | 6,141 (5,732 to 6,535) | 1.36 (1.31 to 1.4) | 0.287 (0.254 to 0.322) | 0.313 (0.299 to 0.327) | 0.592 (0.606 / 0.592) | 0.0687 (0.0668 to 0.0707) | 10.1 | 57,293 (55,545 to 59,111) | 91,724 (91,152 to 92,348) | 15,377 (15,168 to 15,601) | 68.7 (66.8 to 70.4) | 1.02 (0.988 to 1.05) |
| P25 | 0.0003235 | 5,883 (5,610 to 6,187) | 1.49 (1.45 to 1.54) | 0.493 (0.461 to 0.529) | 0.505 (0.491 to 0.521) | 0.5 (0.503 / 0.499) | 0.0875 (0.0849 to 0.09) | 7.93 | 58,660 (57,502 to 59,833) | 75,419 (74,848 to 75,972) | 14,807 (14,558 to 15,034) | 59.7 (59.3 to 59.9) | 1.66 (1.61 to 1.71) |
| P50 | 0.0002523 | 6,034 (5,570 to 6,468) | 1.56 (1.54 to 1.58) | 0.661 (0.619 to 0.715) | 0.719 (0.689 to 0.755) | 0.433 (0.449 / 0.436) | 0.1 (0.0975 to 0.103) | 6.93 | 50,500 (49,683 to 51,273) | 58,297 (58,020 to 58,567) | 12,670 (12,509 to 12,836) | 53.4 (52.7 to 54.6) | 2.36 (2.33 to 2.39) |
| P100 | 0.0002011 | 5,993 (5,615 to 6,389) | 1.73 (1.69 to 1.77) | 0.914 (0.858 to 0.984) | 0.997 (0.962 to 1.04) | 0.361 (0.378 / 0.366) | 0.12 (0.116 to 0.123) | 5.79 | 36,065 (35,762 to 36,342) | 38,303 (38,084 to 38,531) | 9,700 (9,573 to 9,807) | 46.2 (45.6 to 47) | 3.48 (3.42 to 3.52) |
| P25k | 0.000223 | 6,024 (5,340 to 6,827) | 1.77 (1.69 to 1.84) | 0.271 (0.247 to 0.302) | 0.303 (0.287 to 0.323) | 0.557 (0.579 / 0.559) | 0.121 (0.115 to 0.126) | 5.73 | 45,753 (45,183 to 46,352) | 48,745 (48,416 to 49,087) | 12,543 (12,298 to 12,784) | 49.3 (48 to 50.4) | 3.39 (3.26 to 3.51) |
| P100ln | 0.0002085 | 6,098 (5,645 to 6,593) | 1.64 (1.6 to 1.68) | 0.423 (0.373 to 0.483) | 0.667 (0.623 to 0.713) | 0.419 (0.512 / 0.437) | 0.101 (0.0986 to 0.102) | 6.9 | 34,550 (34,060 to 35,029) | 38,790 (38,490 to 39,139) | 8,256 (8,100 to 8,410) | 47.9 (46.8 to 49.2) | 3.06 (2.97 to 3.15) |

Final-size ratios to E. The raw ratio compares the arm means. The adjusted ratio moves each arm to a day-28 count of 6,000 with one common slope from the within-arm regression of the day-N count on the day-28 count (0.475 extra day-112 infections per extra day-28 infection, 90% interval 0.303 to 0.691 from a bootstrap over replicates inside each arm; at day 70 the slope is 1.94, 1.41 to 2.71).


| arm | day 70 / E | day 70 / E, adjusted | day 112 / E | day 112 / E, adjusted to day 28 = 6,000 |
|---|---|---|---|---|
| E | 1 (0.929 to 1.08) | 1 (1 to 1) | 1 (0.983 to 1.02) | 1 (1 to 1) |
| P0 | 0.988 (0.93 to 1.05) | 0.989 (0.95 to 1.03) | 0.983 (0.97 to 0.997) | 0.983 (0.971 to 0.995) |
| P25 | 1.01 (0.96 to 1.07) | 1.02 (0.983 to 1.06) | 0.808 (0.797 to 0.819) | 0.809 (0.8 to 0.819) |
| P50 | 0.871 (0.828 to 0.925) | 0.875 (0.843 to 0.908) | 0.624 (0.617 to 0.632) | 0.625 (0.617 to 0.632) |
| P100 | 0.622 (0.593 to 0.661) | 0.626 (0.602 to 0.651) | 0.41 (0.405 to 0.416) | 0.411 (0.406 to 0.416) |
| P25k | 0.789 (0.748 to 0.834) | 0.793 (0.76 to 0.835) | 0.522 (0.515 to 0.529) | 0.522 (0.516 to 0.53) |
| P100ln | 0.596 (0.565 to 0.633) | 0.596 (0.574 to 0.621) | 0.416 (0.409 to 0.422) | 0.415 (0.41 to 0.421) |



Predictions, as registered.

| prediction | result |
|---|---|
| (i) Each coupled arm's early moment k within 15% of its PS1 value | **met.** P25 0.493 against 0.471 (+4.7%), P50 0.661 against 0.632 (+4.6%), P100 0.914 against 0.954 (-4.2%), P25k 0.271 against 0.270 (+0.4%), P100ln 0.423 against 0.464 (-8.8%). The new map and the day-28 matching do not move the moment k by more than 9% in any arm |
| (ii) At matched day-28 incidence, P25k's day-112 count is 0.62 to 0.95 of E's | **failed.** The ratio is 0.522 (0.515 to 0.529); adjusted to day 28 = 6,000 it is 0.522 (0.516 to 0.530). At day 70 it is 0.789 raw and 0.793 adjusted. The gap is wider than in round 5 (0.618 at day 70 on the old map, adjusted by regression) |
| (iii) Early R of every coupled arm above E's at matched day-28 incidence | **met.** E 1.335 (1.30 to 1.38); P25 1.49, P50 1.56, P100 1.73, P25k 1.77, P100ln 1.64, with lower interval ends of 1.45 or more. P0 (not coupled) is 1.355 (1.31 to 1.40) |

Further observations from the table. At matched day 28, every coupled arm grows faster over days 7 to 28 than E: doubling time 10.7 days for E, 10.1 for P0, then 7.9 (P25), 6.9 (P50), 5.8 (P100), 5.7 (P25k) and 6.9 (P100ln). Their background coefficients are lower than E's (P25k 2.2e-4, P100 2.0e-4, E 5.0e-4). The coupled arms peak earlier and lower (peak prevalence 8,300 to 14,800 on day 46 to 60, against 15,700 on day 68 for E) and have smaller day-112 counts, 0.41 to 0.81 of E's. P25 has the same day-70 count as E (1.01) and a day-112 count of 0.81. The index cases' mean trait is 1.7 to 3.5 in the coupled arms against 1.02 in E and P0.


## 6. R6-5. How big can a room be?

The arm is the shape-0.03 per-episode multiplier chain arm of R3-4 (`--sheddingShape 0.03 --shuffleSchedules 1`, 1,000 introductions from `closures_seed1000.json`, 7 weeks, `locations1.json` with `agents2.json`, no `-r`), with hospitals, health centres and nursing homes (types 12, 14 and 22; 120 locations) split into wards. The ward files are built by `study/build_wards_r65.py`, which calls `build_wards.py` with the target size changed; at target 30 it reproduces the R3-4 file byte for byte. A location is left whole when it has 4/3 of the target agents or fewer (40 at target 30, as in R3-4). Built: target 10 gives 38,661 wards (all 120 locations split, mean 10.0 assigned agents per ward), target 100 gives 3,865 wards (119 split, mean 100.0, largest 104.7), target 300 gives 1,297 wards (118 split, mean 297.7, largest 366.5). Total capacity is unchanged, 106,990. The unsplit arm is `locations1.json` with `agents2.json`. W30 is the R3-4 result (`round2/r34/shape0.03`), reused.

Calibration. Mean offspring is the pooled chain mean, (infected agents with an infector) / (infected agents), target 0.345. Each coefficient was calibrated on four seeds, 7 weeks, to within 3% (pilot values: w10 +2.3%, w100 -2.3%, w300 -2.9%, unsplit -0.5%). A four-seed pilot has a standard error of about 7% on this quantity (the standard deviation across replicates is 14% of the mean), so the 40-replicate mean can miss by more than 3% even when the pilot is inside. The first 40-replicate sets missed on the mean of the per-replicate ratios, the criterion first used, by -4.0% (w10), -3.1% (w100), +2.8% (w300, accepted) and -1.8% (unsplit, accepted). On the pooled mean, which is the quantity in the table, they are -3.2% (w10), -2.0% (w100), +4.1% (w300) and -0.8% (unsplit). After each miss the coefficient was rescaled from the 40-replicate mean (exponent 1/1.6) and 40 new replicates were run, up to three more times, so w10 has three sets, w100 and w300 two, and unsplit one (the w300 second set was run after the criterion was changed to the pooled mean). All sets are in `43_r65_ward_sweep.csv`, marked superseded when a later set exists, and the table below shows all of them. The primary sets are inside 3% of 0.345 on the pooled mean: w10 +0.4%, w30 -0.1%, w100 -0.2%, w300 +2.3%, unsplit -0.8%.

The Dwass expected longest chain is the exact distribution of the maximum of n independent total-progeny variables at the arm's own mean and moment k (negative-binomial offspring), n the number of chains; the median and the 2.5th and 97.5th percentiles are given. "P(longest at least observed)" is one minus the distribution function of that maximum just below the observed value. The five-seed figure is the share of non-overlapping groups of five chains, in file order, with a total size above 50, against the exact Dwass probability. Hospital means location type 12 only. Intervals are replicate bootstraps, 90%.

| arm | run set | chains | mean offspring | k moment | chains above 10 | above 50 | above 100 | above 200 | above 500 | longest chain | Dwass median (95% range) | P(longest at least observed) | five-seed: observed / exact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| w10 (set 1, superseded) | k 0.000138, run set w10 | 38,337 | 0.334 (0.3218 to 0.3465) | 0.0338 | 492 (453 to 531) | 42 (33 to 54) | 7 (3 to 12) | 1 (0 to 3) | 0 | 206 | 147 (104 to 241) | 0.0829 | 0.00704 / 0.00678 |
| w10 (set 2, superseded) | k 0.00014161, run set w10_p2 | 38,910 | 0.3365 (0.3237 to 0.3499) | 0.032 | 504 (464 to 547) | 36 (27 to 46) | 6 (3 to 10) | 1 (0 to 3) | 0 | 236 | 156 (109 to 256) | 0.0481 | 0.00565 / 0.00739 |
| w10 | k 0.00014494, run set w10_p3 | 38,698 | 0.3464 (0.3343 to 0.3586) | 0.0324 | 501 (469 to 532) | 57 (46 to 69) | 11 (6 to 16) | 1 (0 to 3) | 0 | 233 | 163 (115 to 269) | 0.0746 | 0.00982 / 0.00814 |
| w30 (R3-4) | reused from R3-4 | 38,499 | 0.3448 (0.333 to 0.3563) | 0.0315 | 523 (495 to 553) | 49 (38 to 60) | 7 (3 to 11) | 0 (0 to 0) | 0 | 150 | 165 (116 to 273) | 0.687 | 0.00857 / 0.00823 |
| w100 (set 1, superseded) | k 0.000138, run set w100 | 38,909 | 0.3381 (0.325 to 0.3511) | 0.0328 | 529 (487 to 573) | 36 (27 to 46) | 6 (3 to 10) | 1 (0 to 3) | 0 | 233 | 155 (109 to 254) | 0.0495 | 0.00553 / 0.00735 |
| w100 | k 0.000140766, run set w100_p2 | 38,618 | 0.3442 (0.3299 to 0.3589) | 0.0321 | 501 (467 to 537) | 45 (33 to 56) | 9 (5 to 14) | 0 (0 to 0) | 0 | 194 | 162 (114 to 268) | 0.223 | 0.00686 / 0.00802 |
| w300 (set 1, superseded) | k 0.000144096, run set w300 | 38,618 | 0.3593 (0.3449 to 0.3728) | 0.0326 | 530 (493 to 566) | 53 (41 to 66) | 10 (5 to 15) | 1 (0 to 3) | 0 | 201 | 176 (123 to 290) | 0.28 | 0.00829 / 0.00928 |
| w300 | k 0.000140489, run set w300_p2 | 38,917 | 0.3531 (0.3414 to 0.3656) | 0.0324 | 549 (514 to 584) | 46 (36 to 57) | 6 (2 to 10) | 0 (0 to 0) | 0 | 192 | 170 (119 to 281) | 0.302 | 0.00809 / 0.00876 |
| unsplit | k 0.000126784, run set unsplit | 38,918 | 0.3423 (0.33 to 0.3554) | 0.03 | 529 (493 to 564) | 41 (32 to 50) | 8 (3 to 13) | 0 (0 to 0) | 0 | 187 | 170 (118 to 280) | 0.336 | 0.0072 / 0.0084 |

Hospital columns:

| arm | hospital cases | hospital share of all infections | hospital share of the longest chain | mean offspring of hospital-infected cases | share of their children also infected in hospital |
|---|---|---|---|---|---|
| w10 (set 1, superseded) | 79 | 0.1% | 1.0% | 0.392 (0.163 to 0.681) | 0 (0 to 0) |
| w10 (set 2, superseded) | 70 | 0.1% | 0.4% | 0.243 (0.0634 to 0.484) | 0 (0 to 0) |
| w10 | 77 | 0.1% | 0.0% | 0.195 (0.075 to 0.33) | 0.0667 (0 to 0.167) |
| w30 (R3-4) | 160 | 0.3% | 0.0% | 0.106 (0.0377 to 0.178) | 0.176 (0 to 0.364) |
| w100 (set 1, superseded) | 410 | 0.7% | 0.4% | 0.383 (0.284 to 0.478) | 0.223 (0.154 to 0.299) |
| w100 | 432 | 0.7% | 0.5% | 0.211 (0.129 to 0.307) | 0.231 (0.118 to 0.376) |
| w300 (set 1, superseded) | 749 | 1.2% | 2.0% | 0.36 (0.257 to 0.456) | 0.33 (0.264 to 0.395) |
| w300 | 811 | 1.3% | 1.0% | 0.494 (0.375 to 0.622) | 0.367 (0.297 to 0.43) |
| unsplit | 1,615 | 2.7% | 56.7% | 0.568 (0.376 to 0.771) | 0.553 (0.473 to 0.621) |

Predictions, as registered.

| prediction | result |
|---|---|
| (i) P(longest at least observed) above 0.05 at ward sizes 10, 30 and 100 and below 0.05 unsplit | **failed on the unsplit clause, met on the other three.** w10 0.075, w30 0.687, w100 0.223 are above 0.05. Unsplit is 0.336, not below 0.05: its longest chain (187) is close to the Dwass median (170, 95% range 118 to 280). The 585 of V4 was at mean offspring 0.397; at mean 0.342 the unsplit arm has no unusual chain. The three above-0.05 clauses are fragile: two superseded sets sit at the threshold (w10 set 2: 0.048; w100 set 1: 0.0495) |
| (ii) The share of hospital-infected cases' children also infected in hospital rises monotonically with ward size | **met on the point estimates**: 0.067 (w10), 0.176 (w30), 0.231 (w100), 0.367 (w300), 0.553 (unsplit). The small-ward values rest on few cases (77 hospital cases at w10, 160 at w30) and their intervals are wide, 0 to 0.17 and 0 to 0.36 |

Further observations from the table. Hospital infections are a small part of the chain arm and rise with ward size: 0.13% of infections at w10, 0.27% at w30, 0.73% at w100, 1.3% at w300 and 2.7% unsplit. At the same mean offspring, the number of chains above 50, 100 and 200 does not move systematically with ward size (above 100: 11, 7, 9, 6 and 8 chains; the bootstrap intervals overlap for every pair). The longest chain is 150 to 233 across arms and sits inside the Dwass 95% range in every primary set. What changes is where the longest chain sits: it contains no hospital infections in w10 and w30, 0.5% in w100, 1.0% in w300 and 56.7% unsplit (106 of 187 infections). Mean offspring of hospital-infected cases: 0.195, 0.106, 0.211, 0.494 and 0.568 (w10 to unsplit).


## 7. R6-6. Is the crowding answer an assumption?

No multiplier, no events, default venues (`--venueProfile off`), `locations1.json` with `agents2.json`, 4 weeks, 12 replicates per cell. The density exponent `--densityExponent` is alpha: the hazard at a location is proportional to (infectious presence) divided by (agents present) to the power alpha, so alpha = 1 is the model's frequency-dependent default and alpha = 0 is mass action, where a venue's hazard grows with the number of infectious people present regardless of how many others are there. The alpha = 1 cell is the R3-6 baseline (coefficient 0.00041, day 28 = 6,211.25), reused. The other four were calibrated on the same 12 seeds (a three-seed pilot first) until the mean day-28 count was within 3% of 6,211.25; the accepted means are 6,218, 6,156, 6,196 and 6,200 (within 0.9%). "Occupancy at infection" is the trace's occupancy column (the number of agents at the location when the agent was infected) over all infections on days 1 to 28, pooled over replicates. Intervals are replicate bootstraps, 90%.

| alpha | calibrated k | day 28 | early R | k moment | k likelihood | zero | NB zero (moment) | NB zero (likelihood) | occupancy at infection, median | p90 |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.00041 | 6,211 | 1.41 (1.4 to 1.42) | 4.59 (4.29 to 4.92) | 4.59 (4.22 to 5) | 0.297 (0.291 to 0.303) | 0.293 | 0.293 | 12 (11 to 12) | 253 (246 to 260) |
| 0.75 | 0.0001674 | 6,218 | 1.49 (1.46 to 1.52) | 3.68 (3.43 to 3.99) | 3.58 (3.35 to 3.82) | 0.29 (0.283 to 0.298) | 0.286 | 0.287 | 55 (54 to 55) | 777 (767 to 785) |
| 0.5 | 5.429e-05 | 6,156 | 1.54 (1.51 to 1.58) | 2.37 (2.23 to 2.52) | 2.36 (2.23 to 2.52) | 0.305 (0.298 to 0.312) | 0.305 | 0.305 | 170 (168 to 173) | 993 (989 to 996) |
| 0.25 | 1.425e-05 | 6,196 | 1.57 (1.54 to 1.6) | 1.7 (1.63 to 1.78) | 1.68 (1.6 to 1.77) | 0.33 (0.324 to 0.337) | 0.329 | 0.33 | 444 (423 to 471) | 1,080 (1,070 to 1,091) |
| 0 | 3.166e-06 | 6,200 | 1.57 (1.54 to 1.59) | 1.57 (1.45 to 1.72) | 1.51 (1.41 to 1.63) | 0.344 (0.335 to 0.353) | 0.338 | 0.342 | 698 (692 to 703) | 1,179 (1,175 to 1,183) |

Predictions, as registered.

| prediction | result |
|---|---|
| (i) Early moment k decreases monotonically as alpha decreases | **met.** 4.59, 3.68, 2.37, 1.70, 1.57 for alpha = 1, 0.75, 0.5, 0.25, 0. The likelihood k follows (4.59, 3.58, 2.36, 1.68, 1.51) |
| (ii) No cell has moment k below 1.5 | **met on the point estimates, with no margin at alpha = 0.** The moment k at alpha = 0 is 1.57 (1.45 to 1.72) and the likelihood k is 1.51 (1.41 to 1.63), so the interval at alpha = 0 includes values below 1.5. Every other cell is above 1.6 |

Reading, limited to the table. Removing the dependence on crowding moves the early moment k from 4.6 to 1.6 and the early R from 1.41 to 1.57 at the same day-28 count, but not near the moment k of about 0.3 that the earlier rounds used as the target. The zero share rises from 0.297 to 0.344, and it stays on the negative binomial of the same mean and k in every cell (within 0.006 at either estimator). The median occupancy at infection rises from 12 to 698 and the 90th percentile from 253 to 1,179, as infections move from small settings to large venues. So the density assumption controls how overdispersed a model with no person-level variation is, but even mass action leaves it far from k near 0.3.


## 8. R6-7. Closed-group events

**Mechanism (new, `--eventGroupSize M --eventDurationHours 2 --eventGroupLog PATH`, build `build_r67`).** Event locations are drawn each day exactly as for venue-day events (rate, types 5 and 8, same draw order), but the venue-day boost is not applied. Each event gets a start time drawn uniformly between 10:00 and 20:00. At the start step, a group of at most M agents is drawn at random from those present at the location (all of them if fewer than M). The group is exposed once, for 2 hours: for each susceptible member, the infection probability is the usual susceptibility times 1 - exp(-k * (sum of infectiousness in the group / group size^alpha) * location infectiousness * factor * seasonality * 120 minutes), the same hazard form as the main model. Members who are infected get an infector drawn in proportion to infectiousness among the other group members, and the usual infection statistics. Events with nobody present, or no infectious attendee, do nothing. Event infections are in the ordinary infection trace; the infected attendees are listed in `<eventGroupLog>.infections`, and "infected at an event" below means listed there (an exact match, unlike the location-and-day match of venue-day events). Types 5 and 8 with no capacity limit (so that M, not the venue, caps the group), event rate and factor below, 4 weeks, 12 replicates, day 28 matched to 6,211.25 within 3% (accepted -2.4% to +1.0%).

**Why the rate, not only the factor, was tuned.** At the registered rate of 0.3% the factor cannot reach moment k 0.3: the group attack rate is already near 1 at a factor of 3,000 (M = 30) and few events have an infectious attendee. In pilots of 6 seeds, 4 weeks, background coefficient 0.00038, M = 30, the moment k was 5.16, 5.03, 5.13, 5.13 and 5.13 at factors 300, 1,000, 3,000, 10,000 and 30,000 (no-event value 4.59). So the factor was fixed at a saturated value (3,000 for M = 30; 10,000 for M = 100, where the attack rate per infectious attendee is smaller) and the event rate was tuned, with the background coefficient re-matched to day 28 each time. Rate scan at fixed background coefficient, M = 30, moment k and day 28: 0.003: 5.13, 4,797; 0.01: 1.08, 5,700; 0.03: 0.56, 8,756; 0.1: 0.29, 22,548; 0.3: 0.31, 83,082; 1.0: 0.35, 151,620. M = 100: 0.003: 1.08, 5,140; 0.01: 0.26, 6,831; 0.03: 0.19, 12,955.

All matched cells are in the table; the cells near moment k 0.3 are M30 at rate 0.05 and M100 at rate 0.0075.

| cell | group size (max) | event rate | factor | background k | day 28 | early R | k moment | k likelihood | zero | NB zero (moment) | NB zero (likelihood) | 1 to 5 | above 5 | at least 20 | at least 50 | max | events share | events (12 replicates) | with an infectious attendee |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M30_rate0.1456 | 30 | 0.146 | 3,000 | 0.0001422 | 6,223 | 1.52 (1.47 to 1.56) | 0.152 (0.15 to 0.155) | 0.33 (0.323 to 0.337) | 0.523 (0.518 to 0.529) | 0.694 | 0.566 | 0.421 | 0.0559 (0.0533 to 0.0582) | 0.019 (0.0174 to 0.0207) | 8.2e-05 (0 to 0.00023) | 50 | 61.7% (60.9 to 62.3) | 83,086 | 3,379 |
| M30_rate0.05 | 30 | 0.05 | 3,000 | 0.0003043 | 6,209 | 1.49 (1.46 to 1.52) | 0.28 (0.266 to 0.295) | 0.889 (0.856 to 0.925) | 0.361 (0.355 to 0.366) | 0.597 | 0.417 | 0.616 | 0.0233 (0.0219 to 0.0246) | 0.0101 (0.00883 to 0.0115) | 0 (0 to 0) | 49 | 25.5% (24.0 to 27.0) | 28,638 | 1,087 |
| M30_rate0.08 | 30 | 0.08 | 3,000 | 0.0002312 | 6,273 | 1.53 (1.47 to 1.59) | 0.188 (0.181 to 0.196) | 0.568 (0.54 to 0.598) | 0.415 (0.408 to 0.422) | 0.659 | 0.476 | 0.549 | 0.0361 (0.032 to 0.0403) | 0.0155 (0.0136 to 0.0175) | 0.00023 (7.4e-05 to 0.00045) | 57 | 41.6% (39.3 to 43.7) | 45,837 | 1,909 |
| M100_rate0.00897 | 100 | 0.00897 | 10,000 | 0.0003675 | 6,199 | 1.43 (1.39 to 1.46) | 0.244 (0.186 to 0.374) | 1.53 (1.33 to 1.81) | 0.321 (0.315 to 0.328) | 0.625 | 0.365 | 0.67 | 0.00964 (0.0083 to 0.011) | 0.00248 (0.00191 to 0.00312) | 0.0011 (0.0007 to 0.0015) | 99 | 9.8% (7.3 to 12.1) | 5,129 | 211 |
| M100_rate0.005 | 100 | 0.005 | 10,000 | 0.0003869 | 6,189 | 1.41 (1.38 to 1.45) | 0.404 (0.256 to 0.913) | 2.03 (1.65 to 2.63) | 0.312 (0.304 to 0.32) | 0.545 | 0.342 | 0.677 | 0.0108 (0.00924 to 0.0122) | 0.00134 (0.000817 to 0.00183) | 0.00052 (0.00015 to 0.00092) | 102 | 5.4% (3.1 to 7.8) | 2,840 | 120 |
| M100_rate0.0065 | 100 | 0.0065 | 10,000 | 0.0003748 | 6,062 | 1.41 (1.37 to 1.44) | 0.479 (0.374 to 0.688) | 1.99 (1.73 to 2.36) | 0.315 (0.308 to 0.322) | 0.519 | 0.345 | 0.674 | 0.0111 (0.00924 to 0.0127) | 0.00172 (0.00108 to 0.00248) | 0.00052 (0.00025 to 0.00077) | 88 | 6.0% (4.4 to 7.6) | 3,675 | 153 |
| M100_rate0.0075 | 100 | 0.0075 | 10,000 | 0.0003788 | 6,190 | 1.42 (1.37 to 1.46) | 0.327 (0.213 to 0.647) | 1.8 (1.48 to 2.26) | 0.318 (0.311 to 0.325) | 0.579 | 0.352 | 0.672 | 0.0107 (0.00882 to 0.0125) | 0.00166 (0.00112 to 0.00217) | 0.00075 (0.00031 to 0.0012) | 100 | 7.0% (4.5 to 9.5) | 4,251 | 181 |

Prediction, as registered: the zero share stays within 0.03 of the no-event baseline (about 0.30; the matched baseline is 0.297).

| cell near moment k 0.3 | moment k | zero share | difference from 0.297 | result |
|---|---|---|---|---|
| M = 100, rate 0.0075 | 0.327 (0.213 to 0.647) | 0.318 (0.311 to 0.325) | +0.021 | **met** |
| M = 30, rate 0.05 | 0.280 (0.266 to 0.295) | 0.361 (0.355 to 0.366) | +0.064 | **failed** |

Reading, limited to the table. With groups capped at 100 the zero share stays at 0.31 to 0.32 across the four matched rates (0.005 to 0.009), and the likelihood k stays at 1.5 to 2.0 while the moment k is 0.24 to 0.48; events carry 5% to 10% of offspring. With groups capped at 30, a moment k of 0.28 needs events to carry 25.5% of offspring (28,638 events in 12 replicates) and the zero share rises to 0.36; at rate 0.1456 events carry 61.7%, the moment k is 0.15 and the zero share 0.52. The moment k of the M = 100 cells has wide intervals (0.213 to 0.647 at rate 0.0075; 0.256 to 0.913 at 0.005), because a few very large clusters set it, and it is not monotone in the rate across the four M = 100 cells (0.404, 0.479, 0.327, 0.244 at 0.005, 0.0065, 0.0075, 0.00897), so the rate that gives exactly 0.3 is not resolved by 12 replicates. The negative binomial at the moment k overstates the zero share (0.52 to 0.63 for M = 100) in the same way as for venue-day events in R6-1.


## Files

In the ACT-049 folder (prefix 43): `43a_review_of_note42.md`; `43_r61_grid_summary.csv`, `43_r61_offspring.csv`; `43_r62_summary.csv`, `43_r62_pairs_joint.csv`, `43_r62_pairs_by_horizon.csv`; `43_r63_survey_vs_infected.csv`; `43_r64_summary.csv`, `43_r64_daily.csv`; `43_r65_ward_sweep.csv`, `43_r65_chain_hist.csv` (primary sets); `43_r66_alpha_sweep.csv`; `43_r67_closed_group_summary.csv`, `43_r67_offspring.csv`.

Local only (in `superspreader/`): `43_r62_repeat_pairs.csv` (all pairs, 849 KB), `43_r62_repeat_pairs_extended.csv` (adds the incidence columns), `43_r65_chain_hist_all_sets.csv` (adds the superseded sets). Code: `study/run_round6.py` (runs), `study/analyze_round6.py` and `study/r6stats.py` (analysis), `study/report_tables.py` (the tables in this note), `study/build_wards_r65.py`, `study/dump_traits_r63.py`. Run directories and calibration state are in `study/results/round6/`.
