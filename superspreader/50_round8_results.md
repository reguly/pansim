# ACT-049 note 50: round 8, risk per hour, tilted mobility and isolation breaking

18 October 2026. Reply to note 49. Review before running: `50a_review_of_note49.md` (errors in note 49 and the predictions registered before any infection run). Code: `superspreader/study/run_round8.py`, `analyze_round8.py`, `report_round8.py`, `build_r8_inputs.py`, `t1_round8.py`; movement-policy changes in `include/policies/movementPolicies.h` (uncommitted); binary `build_r8`. The location and agent files are not edited; the L-modified location files are new copies.

## Headline

1. **Venue heterogeneity alone does make transmission more dispersed, but not enough.** With L multiplied by 10 on types 5, 6, 9, 10 for everybody (S8-1), moment k is 2.94 (baseline 4.59); at 30 it is 2.09. With a tilted class (S8-2) or an exclusive scene (S8-3) k falls to 0.85 (moment) and 0.79 (likelihood). Four arms are below 1 on the moment estimator (0.85 to 0.996): S8-2 tau 0.5 and tau 1 at lambda 30, S8-3 at lambda 10 and 30. **The smallest k is 0.85 on the moment estimator (S8-3 lambda 10, S8-2 tau 1 lambda 30) and 0.69 on the likelihood estimator (S8-3 lambda 30). No arm gets near the real value of about 0.3.**
2. **What this reproduces and what it does not.** Moment k of 0.85 to 1.0 is about three times the real 0.3. The zero share does not follow: at most 40.4% (S8-3 lambda 30) against about 59% observed, and the share of infectors causing 80% of infections is at best 30.7% against about 20%. In the two S8-3 arms the class (5% of eligible agents) causes 81% to 90% of infections and is 39% to 52% of all infected people, so the epidemic is carried by the class, and the early R of the arms rises to 1.76 to 2.03 against 1.4 in the baseline.
3. **The weight predictor of R8-0 was wrong in direction.** It predicted k above the observed value in 13 of 16 arms (the registered rule, observed k at least the predicted k and at most 1.5 times it plus 0.5, held in 3: S8-3 lambda 10 and 30, S8-4 f = 20% lambda 1). A likely reason, not tested here: at L = 10 or 30 a venue hour is a burst, so one infector at a high-L venue infects many people in the same venue-time, a dispersion that a weight per hour does not see. The observed class offspring ratio is 4.4 to 167 (S8-2 and S8-3), against predicted 2.3 to 15.
4. **Isolation breaking (S8-4) does nothing in this model.** At L = 1 k is 4.36 (5% class) and 4.65 (20% class) against 4.59 at baseline (changes -5% and +1%); at lambda 10 it is 2.97 and 2.87 against 2.94 without any class (S8-1).
5. **Control (S8-5).** In the S8-2 tau 1 lambda 30 arm capping the 5% most active averts 11.0 infections per 1,000 discretionary hours removed against 1.68 for the same hours removed from everybody: a factor 6.6 (90% interval 6.2 to 7.0), against the predicted at least 2 (met). Closing the high-L types is far stronger in total (day-84 infections fall to 7.9% of no control against 29.6% for the cap) at 43% of discretionary hours. In the S8-3 arm the scale-all intervention is degenerate (deviation D2), so the comparison is not usable there.

## 1. Deviations from note 49 (first), and errors in it

Errors in note 49 are in `50a` items 1 to 10; the main ones are: L multiplies the infection ratio of everyone present, so the class is coupled at the high-L venues (item 1); the proposed high-L set already holds 53.5% of the others' discretionary hours (item 3); tau, the skip rule and the S8-4 comparison are ambiguous (items 4, 7, 8). Deviations from the instructions:

- **D1. Skip rule.** The gate arms (S8-1 and S8-2 at lambda 10, S8-4) were run although the R8-0 prediction was above 3 (reading in `50a` item 7). When S8-2 at lambda 10 gave k = 1.13 (below 2), the stop rule asked for the complete grids, so every arm was then run: S8-1 at lambda 3 and 30, S8-2 at lambda 3 and 30 for both tau. All arms have 12 replicates (not 8), a common seed set 77001 to 77012, a pilot on the first 4 seeds, and day 28 within 3% of 6,211.25 (largest deviation +2.4%, S8-2 tau 0.5 lambda 30). The infection coefficient is recalibrated per arm and falls from 0.00041 to 0.00031, 0.00017 and 0.000071 for L = 3, 10, 30 (S8-1)
- **D2. S8-3 implementation quirk.** In the window chance calculation the scene of S8-3 (others' high-L chances multiplied by 0.2, difference to home) replaces the multiplier of the class mode instead of composing with it. Consequences: (a) non-class agents do not carry the 0.895 factor that preserved mean hours in the round-7 S2 cell, so their hours are those of the baseline minus the scene (discretionary hours per day 2.13 against 3.76 at baseline and 3.40 in S2); (b) in S8-5 the scale-all intervention acts on the class only, which made it identical in effect to the cap in the S8-3 arm (day-84 infections 9,079.5 against 9,079.3, hours removed 10.1% in both). I report that cell as degenerate and ran S8-5 additionally on the S8-2 tau 1 lambda 30 arm (second lowest k, 0.849 against 0.846 on the moment estimator), where scale-all is valid. A fix needs a rebuild and rerunning the S8-3 arms; the S8-3 k values are not expected to change by more than the noise (others' hours differ by a tenth).
- **D3. Hours.** S8-1 and S8-4 keep baseline hours. S8-2 keeps class and others' hours (tilt at fixed duration, `50a` item 4). S8-3 does not (note 49, others' hours move to home): total discretionary hours per agent fall by 30% (3.50 to 2.45 per day).
- **D4. S8-4 class.** The class has no hours multiplier (F = 1); `class share of discretionary hours` is then its population share. The comparison with S8-2 is read as in `50a` item 8.
- **D5. S8-5 hours.** As in round 7, hours removed are estimated on 5-week movement-only runs and scaled to the 12-week runs (63 days of control); the scale-all parameter matches the cap within 3% (S8-2 cell: 7.29% against 7.43%). Closure comes in one step (types 5, 6, 9, 10), so it is not at equal hours; per-hour figures are reported.
- **D6. S8-6 skipped.** It needs more than a flag change: the combination of `--hviMode` and `--sheddingShape` is blocked by a check in `initializeArgs` (one line, `50a` item 9) and a rebuild. I did not do it; say if you want it (about 30 minutes).
- **D7. Predictor.** R8-0 item 3 used per-agent weights (productivity per hour by venue type derived from baseline infection shares, `50a` item 6), not 'a + 3.7 b'. Registered before running.
- **D8. Binaries and state.** `build_r8` for everything in this round. T1 passed: with every option off a 12-week run on `build_r8` gives a daily table and an infection trace byte-identical to `build_r7b` (81,610 trace lines; stdout differs only in the timing profile). All code is uncommitted.

## 2. R8-0: hours by venue type and predictions

| movement | group | agents | disc. hours per day | share at types 5, 6, 9, 10 | all-role hours at types 5, 6, 9, 10 | of which non-discretionary role | home hours |
|---|---|---|---|---|---|---|---|
| baseline | others eligible | 157029 | 3.76 | 53.8% | 2.07 | 0.05 | 15.2 |
| S2 cell (class f = 5%, F = 3), untilted | class | 7774 | 9.88 | 59.1% | 5.9 | 0.066 | 9.39 |
| S2 cell (class f = 5%, F = 3), untilted | others eligible | 149255 | 3.4 | 53.5% | 1.87 | 0.049 | 15.6 |
| S2 cell (class f = 5%, F = 3), untilted | all others | 170972 | 3.18 | 50.3% | 1.64 | 0.043 | 15.8 |
| tilt tau 0.5 | class | 7774 | 10.4 | 80.6% | 8.46 | 0.068 | 9.05 |
| tilt tau 0.5 | others eligible | 149255 | 3.4 | 53.5% | 1.87 | 0.049 | 15.6 |
| tilt tau 0.5 | all others | 170972 | 3.18 | 50.3% | 1.64 | 0.043 | 15.8 |
| tilt tau 1 | class | 7774 | 11 | 100.0% | 11 | 0.067 | 8.71 |
| tilt tau 1 | others eligible | 149255 | 3.4 | 53.5% | 1.87 | 0.049 | 15.6 |
| tilt tau 1 | all others | 170972 | 3.18 | 50.3% | 1.64 | 0.042 | 15.8 |
| tau 1 and others' high-L chances x 0.2 (S8-3) | class | 7774 | 11 | 100.0% | 11 | 0.066 | 8.71 |
| tau 1 and others' high-L chances x 0.2 (S8-3) | others eligible | 149255 | 2.13 | 18.6% | 0.445 | 0.049 | 16.7 |
| tau 1 and others' high-L chances x 0.2 (S8-3) | all others | 170972 | 2.06 | 16.9% | 0.39 | 0.043 | 16.7 |

Share of discretionary hours at the proposed high-L set (types 5, 6, 9, 10) for others: 53.8% (baseline, eligible) and 53.5% (S2 cell); for the class: 59.1% untilted, 80.6% (tau 0.5), 99.96% (tau 1). Hours at those types in a work or school role are only 0.05 per day.

| arm | lambda | exposure factor | class to others ratio r (predicted) | CV^2 of weights | predicted k | acceptance range for observed k | observed k (moment) | within range |
|---|---|---|---|---|---|---|---|---|
| s8_1_L3 | 3 | 1.3 | n/a | 0.117 | 6.59 | 6.59 to 10.4 | 4.92 | no |
| s8_2_t0.5_L3 | 3 | 1.32 | 2.27 | 0.172 | 4.8 | 4.8 to 7.7 | 3.11 | no |
| s8_2_t1_L3 | 3 | 1.34 | 2.67 | 0.209 | 4.06 | 4.06 to 6.59 | 2.55 | no |
| s8_3_L3 | 3 | 1.07 | 3.43 | 0.377 | 2.38 | 2.38 to 4.08 | 1.39 | no |
| s8_1_L10 | 10 | 2.35 | n/a | 0.117 | 6.61 | 6.61 to 10.4 | 2.94 | no |
| s8_2_t0.5_L10 | 10 | 2.43 | 3.51 | 0.316 | 2.81 | 2.81 to 4.71 | 1.44 | no |
| s8_2_t1_L10 | 10 | 2.51 | 4.4 | 0.462 | 1.97 | 1.97 to 3.46 | 1.13 | no |
| s8_3_L10 | 10 | 1.56 | 8.07 | 1.36 | 0.7 | 0.7 to 1.55 | 0.846 | yes |
| s8_1_L30 | 30 | 5.34 | n/a | 0.184 | 4.54 | 4.54 to 7.31 | 2.09 | no |
| s8_2_t0.5_L30 | 30 | 5.6 | 4.42 | 0.524 | 1.75 | 1.75 to 3.13 | 0.996 | no |
| s8_2_t1_L30 | 30 | 5.86 | 5.67 | 0.77 | 1.21 | 1.21 to 2.32 | 0.849 | no |
| s8_3_L30 | 30 | 2.96 | 15.1 | 3.39 | 0.284 | 0.284 to 0.926 | 0.895 | yes |
| s8_4_f5_L1 | 1 | 1.01 | 1.12 | 0.186 | 4.49 | 4.49 to 7.24 | 4.36 | no |
| s8_4_f5_L10 | 10 | 2.37 | 1.34 | 0.121 | 6.42 | 6.42 to 10.1 | 2.96 | no |
| s8_4_f20_L1 | 1 | 1.02 | 1.13 | 0.201 | 4.21 | 4.21 to 6.81 | 4.65 | yes |
| s8_4_f20_L10 | 10 | 2.45 | 1.36 | 0.132 | 6 | 6 to 9.49 | 2.87 | no |

Out-of-sample check of the predictor at L = 1 (S2 cell): predicted class ratio 1.40 and k 4.44, observed 1.55 and 4.25 (round 7).

## 3. Predictions scored

| Test | Prediction | Result | Verdict |
|---|---|---|---|
| S8-1 | k stays above 2.5 | 4.92 (lambda 3), 2.94 (10), 2.09 (30); likelihood 2.05 at 30 | met at lambda 3 and 10, **failed at lambda 30** |
| S8-1 | the coefficient (R) falls on recalibration | coefficient 0.00041 to 0.00031, 0.00017, 0.000071; early R among index cases rises from 1.41 to 1.44, 1.48, 1.52 | met |
| S8-2 | registered rule from R8-0 (k at least the predicted, at most 1.5 times plus 0.5) | observed below predicted in all six cells: tau 0.5: 3.11, 1.44, 0.996 against 4.80, 2.81, 1.75; tau 1: 2.55, 1.13, 0.849 against 4.06, 1.97, 1.21 | **failed** (predictor overstates k) |
| S8-3 | the only arm that can reach k below 1 | S8-3 lambda 10: 0.846, lambda 30: 0.895; but also S8-2 tau 1 lambda 30 0.849 and tau 0.5 lambda 30 0.996 | S8-3 reaches below 1 (met); "the only arm" **failed** |
| S8-3 | lambda about 14 gives r = 12 | observed r 17.8 already at lambda 3, 79.1 at 10 (predicted by weights 3.4 and 8.1) | **failed** (r far larger than the weights give) |
| S8-4 | lambda 1 changes k by less than 10% | 4.36 and 4.65 against 4.59 (-4.9% and +1.2%) | met |
| S8-4 | lambda 10 is below S8-2 tau 1 at the same lambda (read as k above) | 2.96 and 2.87 against 1.13 | met under the reading of `50a` item 8 |
| S8-5 | the cap beats scale-all by a factor of at least 2 in the arm with the lowest k | S8-2 tau 1 lambda 30: 6.56 (6.19 to 6.96); S8-3 lambda 10 (lowest moment k): 1 (degenerate, D2) | **met** in the valid cell; not testable in S8-3 |
| S8-6 | combination with shedding at most 25% below shedding alone | not run | skipped (D6) |

## 4. Arms: results (12 replicates, 4 weeks, day 28 matched to 6,211.25)

| arm | day 28 vs 6,211 | coefficient | early R | k moment | k likelihood | zero | NB zero (moment) | NB zero (likelihood) | causing 80% | causing 50% | mean unscaled multiplier of index cases | class share of infections caused | class share of discretionary hours | class share of high-L hours | class share of index cases | class ratio r (observed) | predicted k |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| s8_1_L3 | -0.0% | 0.000312 | 1.44 (1.42 to 1.47) | 4.92 (4.44 to 5.45) | 4.79 (4.32 to 5.33) | 28.6% (27.7 to 29.5) | 28.2% (27.4 to 29.0) | 28.3% (27.5 to 29.1) | 42.5% | 19.9% | 1 (1 to 1) | n/a | n/a | n/a | n/a | n/a | 6.59 |
| s8_1_L10 | 0.1% | 0.000165 | 1.48 (1.46 to 1.5) | 2.94 (2.78 to 3.11) | 2.96 (2.8 to 3.15) | 30.1% (29.6 to 30.6) | 30.1% (29.6 to 30.6) | 30.1% (29.6 to 30.5) | 40.4% | 18.9% | 1 (1 to 1) | n/a | n/a | n/a | n/a | n/a | 6.61 |
| s8_1_L30 | -1.3% | 7.07e-05 | 1.52 (1.48 to 1.55) | 2.09 (1.98 to 2.2) | 2.05 (1.96 to 2.15) | 32.3% (31.5 to 33.1) | 31.9% (31.2 to 32.7) | 32.1% (31.4 to 32.8) | 38.8% | 17.9% | 1 (1 to 1) | n/a | n/a | n/a | n/a | n/a | 4.54 |
| s8_2_t0.5_L3 | 0.6% | 0.000291 | 1.47 (1.45 to 1.49) | 3.11 (2.9 to 3.33) | 3.31 (3.14 to 3.51) | 29.0% (28.5 to 29.6) | 29.9% (29.4 to 30.5) | 29.6% (29.0 to 30.1) | 41.5% | 19.0% | 1.11 (1.1 to 1.12) | 18.9% | 13.7% | 19.0% | 9.7% | 4.43 | 4.8 |
| s8_2_t0.5_L10 | -0.6% | 0.000137 | 1.54 (1.52 to 1.57) | 1.44 (1.37 to 1.52) | 1.63 (1.55 to 1.7) | 32.6% (32.2 to 33.1) | 35.0% (34.6 to 35.4) | 33.8% (33.4 to 34.1) | 37.5% | 16.5% | 1.22 (1.2 to 1.23) | 34.5% | 13.7% | 19.0% | 15.0% | 10 | 2.81 |
| s8_2_t0.5_L30 | 2.4% | 5.4e-05 | 1.62 (1.58 to 1.65) | 0.996 (0.959 to 1.04) | 1.13 (1.09 to 1.18) | 35.3% (34.6 to 36.0) | 38.3% (37.6 to 38.9) | 36.6% (36.0 to 37.3) | 35.0% | 14.4% | 1.27 (1.26 to 1.29) | 44.7% | 13.7% | 19.0% | 17.9% | 15.4 | 1.75 |
| s8_2_t1_L3 | 0.6% | 0.000276 | 1.47 (1.45 to 1.49) | 2.55 (2.4 to 2.74) | 2.78 (2.62 to 2.97) | 29.9% (29.5 to 30.2) | 31.3% (30.8 to 31.9) | 30.7% (30.3 to 31.2) | 40.7% | 18.4% | 1.15 (1.14 to 1.16) | 26.5% | 14.4% | 23.4% | 11.7% | 6.86 | 4.06 |
| s8_2_t1_L10 | 1.8% | 0.000119 | 1.58 (1.55 to 1.62) | 1.13 (1.08 to 1.18) | 1.26 (1.2 to 1.32) | 34.4% (33.6 to 35.2) | 37.2% (36.5 to 37.8) | 35.9% (35.2 to 36.5) | 35.5% | 14.9% | 1.32 (1.3 to 1.34) | 50.0% | 14.4% | 23.4% | 20.1% | 19 | 1.97 |
| s8_2_t1_L30 | -1.6% | 4.37e-05 | 1.65 (1.6 to 1.69) | 0.849 (0.807 to 0.899) | 0.893 (0.845 to 0.95) | 38.3% (37.5 to 39.1) | 40.0% (39.1 to 40.8) | 39.3% (38.5 to 40.0) | 32.6% | 13.2% | 1.43 (1.41 to 1.45) | 60.7% | 14.4% | 23.4% | 25.3% | 29.3 | 1.21 |
| s8_3_L3 | -0.3% | 0.000298 | 1.49 (1.46 to 1.52) | 1.39 (1.31 to 1.49) | 1.57 (1.48 to 1.67) | 33.7% (32.9 to 34.5) | 36.3% (35.6 to 37.1) | 35.0% (34.4 to 35.7) | 36.6% | 16.1% | 1.31 (1.28 to 1.34) | 48.4% | 21.1% | 56.3% | 18.9% | 17.8 | 2.38 |
| s8_3_L10 | -0.7% | 0.000115 | 1.76 (1.71 to 1.81) | 0.846 (0.801 to 0.886) | 0.793 (0.76 to 0.823) | 39.1% (38.2 to 40.3) | 38.6% (37.3 to 40.0) | 39.5% (38.5 to 40.8) | 31.3% | 13.2% | 1.72 (1.69 to 1.75) | 80.6% | 21.1% | 56.3% | 38.9% | 79.1 | 0.7 |
| s8_3_L30 | 0.6% | 4.12e-05 | 2.03 (1.96 to 2.09) | 0.895 (0.855 to 0.928) | 0.687 (0.65 to 0.721) | 40.4% (39.3 to 41.9) | 34.7% (33.6 to 36.0) | 38.9% (37.7 to 40.3) | 30.7% | 14.3% | 1.98 (1.96 to 2.01) | 89.8% | 21.1% | 56.3% | 51.6% | 167 | 0.284 |
| s8_4_f5_L1 | -0.9% | 0.000408 | 1.41 (1.39 to 1.43) | 4.36 (3.96 to 4.8) | 4.36 (4.04 to 4.71) | 29.5% (28.7 to 30.2) | 29.4% (28.7 to 30.2) | 29.4% (28.7 to 30.1) | 42.3% | 19.5% | 1 (1 to 1) | 4.6% | 5.0% | 4.9% | 4.4% | 0.908 | 4.49 |
| s8_4_f5_L10 | -1.1% | 0.000163 | 1.49 (1.47 to 1.51) | 2.96 (2.82 to 3.13) | 2.95 (2.81 to 3.12) | 30.1% (29.7 to 30.6) | 30.0% (29.5 to 30.5) | 30.0% (29.6 to 30.5) | 40.3% | 18.9% | 1 (1 to 1) | 5.9% | 5.0% | 4.9% | 4.8% | 1.19 | 6.42 |
| s8_4_f20_L1 | -1.3% | 0.000401 | 1.41 (1.38 to 1.43) | 4.65 (4.17 to 5.15) | 4.67 (4.22 to 5.16) | 29.2% (28.2 to 30.2) | 29.2% (28.4 to 30.2) | 29.2% (28.4 to 30.1) | 42.7% | 19.7% | 1 (1 to 1) | 18.0% | 20.0% | 19.9% | 17.3% | 0.874 | 4.21 |
| s8_4_f20_L10 | -1.1% | 0.000158 | 1.49 (1.47 to 1.52) | 2.87 (2.69 to 3.07) | 2.84 (2.66 to 3.04) | 30.2% (29.7 to 30.7) | 30.0% (29.5 to 30.6) | 30.1% (29.6 to 30.6) | 40.2% | 18.8% | 1 (1 to 1) | 22.5% | 20.0% | 19.9% | 19.2% | 1.16 | 6 |

Share above 5 offspring, share with at least 20 and the shares of infections by location type are in `50_s8_summary.csv`; the offspring histograms are in `50_s8_offspring.csv`. Public space has L = 0 and carries no infection in any arm. Class share of the population is 5% (S8-2, S8-3, S8-4 f = 5%) and 20% (S8-4 f = 20%).

## 5. Summary row

| criterion | arm | k moment | k likelihood | zero share | causing 80% | class high-L hours per day | others' high-L hours per day | ratio of high-L hours, class to others | lambda |
|---|---|---|---|---|---|---|---|---|---|
| smallest moment k | s8_3_L10 | 0.846 | 0.793 | 39.1% (38.2 to 40.3) | 31.3% | 11 | 0.39 | 28.3 | 10 |
| same, second arm (0.849) | s8_2_t1_L30 | 0.849 | 0.893 | 38.3% (37.5 to 39.1) | 32.6% | 11 | 1.64 | 6.73 | 30 |
| smallest likelihood k | s8_3_L30 | 0.895 | 0.687 | 40.4% (39.3 to 41.9) | 30.7% | 11 | 0.39 | 28.3 | 30 |

The ratio of high-L hours needed for k near 0.85 is between 7 and 28 together with a lambda of 10 to 30, that is a class that spends 11 hours a day at venues with L 10 to 30 times larger while everyone else spends 0.4 to 1.6 hours. The baseline ratio (untilted class) is 3.2; the others' share of high-L hours is the binding constraint (S8-2 at lambda 30 reaches only 0.85 although the ratio is 6.7, S8-3 at lambda 10 reaches the same with a ratio of 28).

## 6. S8-5: policy contrast (`50_s85_summary.csv`; 12 replicates, 12 weeks, same seeds in every arm, control from day 21)

| base | intervention | discretionary hours removed | high-L hours removed | infections at day 84, none | infections at day 84 | ratio to none (90% interval) | averted per 1,000 discretionary hours (90% interval) | averted per 1,000 high-L hours (90% interval) | cap over scale-all per hour (90% interval) |
|---|---|---|---|---|---|---|---|---|---|
| s8_3_L10 | capTop | 10.08% | 34.47% | 30,038 | 9,080 | 0.302 (0.275 to 0.328) | 6.33 (6.1 to 6.57) | 6.35 (6.12 to 6.6) | 1 (0.997 to 1.01) |
| s8_3_L10 | scaleAll | 10.10% | 34.55% | 30,038 | 9,079 | 0.302 (0.275 to 0.33) | 6.32 (6.08 to 6.56) | 6.34 (6.1 to 6.59) |  |
| s8_3_L10 | close | 23.75% | 94.58% | 30,038 | 4,739 | 0.158 (0.142 to 0.174) | 3.24 (3.18 to 3.31) | 2.8 (2.74 to 2.85) |  |
| s8_2_t1_L30 | capTop | 7.43% | 14.34% | 51,808 | 15,331 | 0.296 (0.28 to 0.312) | 11 (10.8 to 11.3) | 11.1 (10.8 to 11.3) | 6.56 (6.19 to 6.96) |
| s8_2_t1_L30 | scaleAll | 7.29% | 7.23% | 51,808 | 46,348 | 0.895 (0.888 to 0.901) | 1.68 (1.57 to 1.79) | 3.29 (3.07 to 3.5) |  |
| s8_2_t1_L30 | close | 43.35% | 97.60% | 51,808 | 4,110 | 0.0793 (0.0743 to 0.0843) | 2.47 (2.45 to 2.48) | 2.13 (2.11 to 2.14) |  |

In the S8-2 tau 1 lambda 30 arm the cap removes 7.4% of discretionary hours but 14.3% of the high-L hours, and cuts day-84 infections to 29.6%; the same discretionary hours removed from everybody (scale-all, 0.9163) removes 7.2% of high-L hours and cuts infections only to 89.5%. Closing the high-L types removes 97.6% of high-L hours and 43.4% of discretionary hours, and cuts infections to 7.9%, but per hour removed it is less efficient than the cap (2.5 against 11.0 per 1,000 discretionary hours). In S8-3 lambda 10 scale-all is degenerate (D2): cap and scale-all are the same intervention. The two capped arms give the same day-84 mean to 0.002%; this is a coincidence of the replicate means, the replicates differ individually by up to 5%.

## 7. In plain terms

1. **What a high-risk scene can do.** If a 5% minority spends 11 hours a day at venues that are 10 to 30 times riskier per hour and, in S8-3, everybody else is largely kept away from them, transmission becomes concentrated enough to give moment k of 0.85 to 1.0 and a class that causes 80% to 90% of infections. That is the superspreading mechanism of the note, and it works only with an extreme contrast, and in this model the class is also infected at a high rate (44% of infections received in S8-3 at lambda 10, 26% in S8-2 tau 1 at lambda 30), because L acts on exposure as well.
2. **What it does not do.** It does not get k to 0.3, the zero share to about 59%, or the share of infectors causing 80% to about 20%. I did not decompose the zero share; in the best arms the class is 39% to 52% of all infected people, so the distribution over all infected people mixes a heavy class with an ordinary remainder. Round 8 therefore leaves the per-person or per-episode trait route (rounds 5 and 6) as the only one in this model that reaches real k.
3. **Isolation breaking and venue heterogeneity for everyone.** Isolation breaking has no measurable effect. L = 10 for all agents, with no class at all, takes k from 4.59 to 2.94; at 30, 2.09. Venue heterogeneity is a real source of dispersion, an order of magnitude weaker than needed.
4. **Control.** When transmission is concentrated, targeting the most active reduces infections 6.6 times more per hour than uniform reduction, as note 49 predicted, and closing the risky venue types is the strongest single measure. The round-7 result (1.26 times, overlapping intervals) is consistent with being the low-contrast end of the same comparison.

## 8. Open points

1. S8-3: fix the quirk in D2 (compose the scene with the class multiplier) if the S8-3 values or the S8-5 cell on S8-3 are to be used in the paper. I expect k to be unchanged within noise.
2. S8-6 (combination with a per-episode multiplier) was not run (D6).
3. The registered predictor (weights per hour) fails in direction at high L: observed k is below predicted. A prediction that works at high L would have to model the burst at a venue (an infector in a room with L = 30 infects several people at once); that is a different calculation from per-hour weights.
4. The reading of the S8-4 comparison (`50a` item 8) and of tau (`50a` item 4) should be confirmed.

## Files

`50_round8_results.md` (this note), `50a_review_of_note49.md`, `50_r80_hours_by_type.csv`, `50_r80_predictions.csv`, `50_r80_productivity.csv`, `50_s8_summary.csv`, `50_s8_offspring.csv`, `50_s85_summary.csv`, `50_upload_index.md`. No file exceeds 1 MB.
