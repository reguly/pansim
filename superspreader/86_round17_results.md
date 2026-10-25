# 86. Round 17 results

25 October 2026, 21:03 CET. Reply to note 85, which replies to note 84. The pre-run review is `85a_review_of_note85.md`. Code: `superspreader/study/run_round17.py`, `superspreader/study/analyze_round17.py`. Location and agent files were not edited. No simulator source was changed in this round. The scene repair and the episode log are the round-16 changes, used here as named binaries.

## Binaries

The October binary is not on disk. `build_r10/panSim` was overwritten on 25 October 2026 at 11:45 CET. Six rebuilds of commit `6302476`, replayed with the round-14 world-1 command including `--infectionTrace`, all give day 5 = 628 and day 28 = 4,508. The stored run is day 5 = 626 and day 28 = 5,236. The six rows are in `85a_review_of_note85.md`. Single-thread OpenMP moves the same command to 697 and 5,523, further from the stored run. The build used below is Release, `-O3`, `GPU_ATOMICS=ON`, contraction left at the compiler default, `g++-12` 12.4.0, nvcc 12.0.140, 16 OpenMP threads, RTX 4050.

| role | path | sha256 | what is compiled in |
| --- | --- | --- | --- |
| Runs E, D and B2 | `/tmp/r17p/build_study/panSim` | `c88033d1a73f8d3ba2bf70fbecf82d582f2bbc0ab560328fcf6fb7a44ad3a910` | commit `6302476` plus the round-16 episode log and the scene repair |
| Run C, before | `/tmp/r17p/panSim_o3_head` | `af141d454451cca3ba19cd3f7e16fad42ed812fab443840eac58d9191838c4a3` | the 11:45 rebuild of the October source, scene behaviour as it was |
| Run C, after | `/tmp/r17p/build_cafter/panSim` | `07b9b8e2c1e6e0fa42075c68592842ea3f59acda1a47d452191cde37f6c30b29` | commit `6302476` plus only the `hviOthersChance` repair |

The after binary does not contain `--infectiousEpisodeLog`. World 1 seed 77001 on the study binary, with the episode log on, is day 5 = 628 and day 28 = 4,508, and its trace matches the round-16 trace of that seed (`4ea83c1a7a0674a4b0b95d2a00cdc7f16e696a4840dbe8e75207998221e8da51`).

## Code change used by Run C

`hviOthersChance` takes the mean-preserving factor `u` and calls `hviEffectiveChance` for the event chance and for the high-type sum, before scaling by the scene factor `s`. Both call sites pass `hviU`. The branch is taken only when `hviOthersHighScale` is not 1, so S8-1, S8-2 and S8-4 do not enter it. Against commit `6302476` the diff is 13 lines in `include/policies/movementPolicies.h` (+7, −6). That is the whole difference between the before and after binaries.

S8-2 at tilt 1 and venue risk 30 was run on both binaries (calibration, and the 12-week none, capTop, scaleAll and close arms, seeds 77001–77012). All 48 infection traces are byte-identical. S8-1 and S8-4 were not re-run.

## Run E

Five cells, seeds 77001–77012, four weeks, round-15 coefficients, on the study binary. Every replicate's offspring histogram differs from the stored histogram. That comparison is recorded and does not stop the cell. `86_e_equivalence.csv` compares the pooled histograms after merging bins so that each set has at least 10 index cases. The chi-square check used here reproduces note 84's reference value: the survival function at 23.5 on 21 degrees of freedom is 0.318.

| cell | mean, this run / stored | ratio | likelihood k, this / stored | chi-square (df, p) | paired SD of index-case counts |
| --- | --- | --- | --- | --- | --- |
| world 1, exponent 1 | 1.400 / 1.407 | 0.995 | 0.272 / 0.263 | 20.1 (22, 0.58) | 82.4 |
| world 2b, exponent 1 | 1.508 / 1.573 | 0.958 | 0.271 / 0.270 | 28.0 (24, 0.26) | 88.1 |
| world 3b, exponent 1 | 1.408 / 1.451 | 0.970 | 0.253 / 0.248 | 23.5 (26, 0.60) | 167 |
| world 1, exponent 0.5 | 1.521 / 1.488 | 1.022 | 0.213 / 0.213 | 22.6 (25, 0.60) | 85.6 |
| world 1, exponent 0 | 1.612 / 1.570 | 1.026 | 0.175 / 0.178 | 14.2 (28, 0.99) | 111 |

Note 84's world-1 pooled mean of 1.292 was computed from `83_e_hist_diff.csv`, which stores only the bins that differ. The full histograms are the rows above.

Episode export, same cells, is `86_e_episodes.csv`. H is the stay-level index: sum of squared episode weights over sum of squared total weights. `c_T` is the squared coefficient of variation of the per-index-case total weight. `c_m` is the squared coefficient of variation of one realised multiplier per index case (the multiplier on that case's logged episodes). In worlds 1 and 2b that value is the shedding draw: `c_m` is 4.16 and 2.56, against `1/0.24` and `1/0.40`. In world 3b every index case has the same recorded multiplier, so `c_m` is 0. Event rows in the log do carry multiplier 3,000 (156 such rows in replicate 1), but that factor is not a person-level draw and does not enter `c_m`.

| cell | index cases | H | c_T | c_m | moment k | formula k | formula / moment | home median susceptibles | public median susceptibles | event share | event mean offspring |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| world 1, exponent 1 | 13,283 | 0.055 | 0.484 | 4.16 | 0.253 | 1.22 | 4.81 | 1.17 | 69.4 | 0 | |
| world 2b, exponent 1 | 9,924 | 0.041 | 0.984 | 2.56 | 0.196 | 0.840 | 4.28 | 1.42 | 101 | 0 | |
| world 3b, exponent 1 | 12,087 | 0.051 | 0.407 | 0 | 0.150 | 2.46 | 16.4 | 1.51 | 20.0 | 0.128 | 8.07 |
| world 1, exponent 0.5 | 11,577 | 0.081 | 0.430 | 4.16 | 0.166 | 1.10 | 6.61 | 1.48 | 283 | 0 | |
| world 1, exponent 0 | 10,126 | 0.123 | 0.657 | 4.28 | 0.136 | 0.655 | 4.82 | 1.89 | 808 | 0 | |

Home is venue type 2, among episodes that infect someone. Public is types 5, 6, 8, 9 and 10, same filter. The event share is the share of index cases with any event episode while infectious.

| prediction | outcome |
| --- | --- |
| E(a) H in 0.65–0.90 at exponent 1, and 0.85–1.00 at exponent 0, world 1 | **Fails.** H is 0.055 and 0.123. |
| E(b) the formula reproduces moment k within 10% in the five cells | **Fails.** The formula is 4.3 to 16 times the moment k. |
| E(c) home median at most 3, and public median at least 10 | **Holds** in all five cells. |
| E(d) world 3b event share at most 0.12, and event-bearing index cases infect at least 8 | **Fails on the share** (0.128). **Holds on the mean** (8.07). |
| E(e) mean within 3%, likelihood k within 0.03, chi-square p above 0.05 | **Holds in four cells. Fails for world 2b's mean** (4.2% low). Likelihood k and the chi-square test pass in every cell, including world 2b. |

## Run B2

World 3b, joint secant on event rate and the background coefficient, starting from the round-14 extended-search cell (rate 0.08435, coefficient 9.04632e-05). Seeds 89001–89012 for the trials, then 89001–89036. Trial 1 is the start. Trial 2 multiplies the rate by exp(0.12). Trial 3 multiplies the coefficient by exp(0.12). Those three points are the Jacobian. The loop stops when both targets are met, so no Newton step was taken. The 36-seed run reuses the chosen trial's first 12 replicates. `86_b2_trials.csv`.

| trial | rate | coefficient | mean offspring | vs 0.88 | likelihood k | vs 0.27 | both targets |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.08435 | 9.04632e-05 | 0.834 | −5.3% | 0.279 | +0.009 | no |
| 2 | 0.09510 | 9.04632e-05 | 0.985 | +11.9% | 0.258 | −0.012 | no |
| 3 | 0.08435 | 1.0200e-04 | 0.906 | +2.95% | 0.299 | +0.029 | yes |
| 36 seeds | 0.08435 | 1.0200e-04 | 0.929 | +5.58% | 0.296 | +0.026 | mean no, k yes |

The 36-seed moment k is 0.128. The zero share is 0.6293 against a negative-binomial zero share of 0.6568, so the gap is −2.76 points.

| prediction | outcome |
| --- | --- |
| B2(a) both targets met within nine trials | **Holds for the 12-seed search** (trial 3). The 36-seed mean is 5.6% above 0.88, outside the 3% window. Its likelihood k is inside 0.03. |
| B2(b) the 36-seed zero-share gap lies between −2.6 and −2.0 points | **Fails.** The gap is −2.76 points. |

## Run C

Two binaries, three arms (S8-3 at venue risk 10 and 30, S8-2 at tilt 1 and venue risk 30). Day-28 calibration to 6,211.25 within 3%, at most five secant trials, seeds 77001–77012. Every arm matched. The trial counts were 3, 3 and 1 on the before binary and 3, 3 and 1 on the after binary.

Controls are 12-week infection runs at the calibrated coefficient: none, capTop (day 21, parameter 0.05), scaleAll, and close of types 5, 6, 9 and 10 from day 21. Hours removed are the difference, on seed 77001, of cumulative role-discretionary hours in that infection run. They are not estimated from a movement-only window. The scaleAll parameter is chosen by the same secant, at most five trials, so that those infection-run hours match capTop. Every arm matched within four trials. The before S8-3 arms kept the round-8 parameter 0.3263. After the repair that parameter removed about six times as many discretionary hours, and the secant moved it to 0.868 (risk 10) and 0.867 (risk 30). S8-2 stayed at 0.9233 on both binaries.

Non-class hours are the mean, over eligible agents who are not in the class (agent types 4–8, age at least 15), of the sum of `hdt` on types 1, 5, 6, 7, 8, 9 and 10, per day, from the uncontrolled 12-week infection run of seed 77001. The baseline 3.404 is the Section 5.14 figure for that group. Low-L is types 1, 7 and 8. `86_c_hours.csv`.

| binary | arm | day 28 | moment k | non-class hdt per day | vs 3.404 | low-L hdt | high-L hdt |
| --- | --- | --- | --- | --- | --- | --- | --- |
| before | S8-3, risk 10 | 6,201 (−0.2%) | 0.870 | 2.147 | −36.9% | 1.753 | 0.394 |
| before | S8-3, risk 30 | 6,194 (−0.3%) | 0.882 | 2.149 | −36.9% | 1.754 | 0.395 |
| before | S8-2, tilt 1, risk 30 | 6,251 (+0.6%) | 0.839 | 3.390 | −0.4% | 1.589 | 1.801 |
| after | S8-3, risk 10 | 6,171 (−0.6%) | 0.846 | 1.951 | −42.7% | 1.596 | 0.355 |
| after | S8-3, risk 30 | 6,236 (+0.4%) | 0.895 | 1.952 | −42.6% | 1.597 | 0.355 |
| after | S8-2, tilt 1, risk 30 | 6,251 (+0.6%) | 0.839 | 3.390 | −0.4% | 1.589 | 1.801 |

The before S8-3 figure, 2.147 hours and 37% below 3.404, matches the delivered 2.133. After the repair the total is 1.951, against the review's arithmetic target of 1.948. Low-L hours move from 1.753 to 1.596, next to S8-2's 1.589.

Infections averted per 1,000 discretionary hours use the 12-seed mean of day-84 infections and the seed-77001 hour difference. `86_c_controls.csv`.

| binary | arm | capTop per 1,000 h | scaleAll per 1,000 h | close per 1,000 h | cap / scale |
| --- | --- | --- | --- | --- | --- |
| before | S8-3, risk 10 | 6.61 | 6.64 | 3.27 | 0.996 |
| before | S8-3, risk 30 | 5.05 | 5.03 | 2.47 | 1.004 |
| before | S8-2, risk 30 | 12.42 | 1.50 | 2.52 | 8.25 |
| after | S8-3, risk 10 | 6.33 | 0.627 | 3.26 | 10.1 |
| after | S8-3, risk 30 | 4.78 | 0.477 | 2.46 | 10.0 |
| after | S8-2, risk 30 | 12.42 | 1.50 | 2.52 | 8.25 |

After the repair, scaleAll at the hour-matched parameter removes the same discretionary hours as capTop but far fewer high-L hours (0.66 million against 3.15 million on the risk-10 arm), and it averts 1,978 infections at day 84 against 19,691.

| prediction | outcome |
| --- | --- |
| C(a) after the repair, non-class discretionary hours within 3% of baseline | **Fails.** They are 1.951 per day, 42.7% below 3.404. Low-L hours are 1.596, within 0.5% of S8-2's 1.589. |
| C(b) capTop and scaleAll differ by more than 10% in infections averted per 1,000 hours, S8-3 at venue risk 10 | **Holds on the repaired binary.** The ratio is 10.1. On the before binary the ratio is 0.996, as in the delivered table. |
| C(c) moment k of S8-3 at venue risk 10 above 0.85 | **Fails on the repaired arm** (0.846). The before-binary re-run of the same arm is 0.870. The delivered round-8 value was 0.846. |

## Run D

Original-map PS1 arms A0, E and P0, the Section 5.3 coefficients (0.00041, 0.000483661, 0.000483661) and flags, seeds 1101–1112, on `agents1.json` and `locations0.json`. Enlarged-map world 1 B1, coefficient 0.00051516976, seeds 77001–77012. All four arms run 16 weeks with `--episodeTrace`, so day 70 and day 112 are in the same runs. The study binary is the one in the table above.

The single-trace file keeps one row per agent, the latest infection. The episode file keeps every infection. An agent whose second logged infection falls on or before day D is a first-infection record the single-trace snapshot at day D would have lost. The share is that count divided by the number of agents with a logged infection on or before day D, pooled over the 12 replicates. `86_d_daily.csv` has every day. In A0 replicate 1, 133 agents have no episode numbered 1; their first logged row is numbered 2. The share uses the timestamps, not the episode number.

| arm | day 28 share | day 70 share (records lost) | day 112 share (records lost) | day-112 share across replicates |
| --- | --- | --- | --- | --- |
| PS1 A0 | 0.13% | 0.68% (4,997) | 1.69% (19,673) | 1.65% to 1.74% |
| PS1 E | 0.12% | 0.65% (3,915) | 1.83% (18,900) | 1.72% to 1.94% |
| PS1 P0 | 0.14% | 0.70% (4,328) | 1.85% (19,039) | 1.68% to 1.98% |
| world 1 B1 | 0.16% | 1.51% (21,460) | 2.24% (34,542) | 2.12% to 2.31% |

Window cohorts are successive 10-day blocks. Offspring are infections within 14 days. The first-infection pipeline uses each agent's earliest logged episode. The single-trace pipeline uses `trace.tsv`. Likelihood k and moment k, and the zero share, are in `86_d_windows.csv`. A window is follow-up complete when its last day plus 14 is still inside the run, which is the blocks from days 1–10 through 81–90. The Section 5.3 blocks are the first five of those.

| arm | likelihood-k ratio, first over single, days 1–50 | later complete windows outside 5% |
| --- | --- | --- |
| PS1 A0 | 0.983 to 1.004 | 71–80 is 1.071; 81–90 is 1.144 |
| PS1 E | 0.985 to 0.995 | none; every block, including the censored ones, is inside 1.9% |
| PS1 P0 | 0.991 to 1.000 | none; the largest later ratio is 1.039, on the censored block 101–110 |
| world 1 B1 | 0.985 to 1.040 | 51–60 is 1.153; 61–70 is 1.337; 71–80 is 1.562; 81–90 is 1.539 |

| prediction | outcome |
| --- | --- |
| D(a) at most 2% of infected agents are infected twice by day 112 in the PS1 arms | **Holds.** The three arms are 1.69%, 1.83% and 1.85%, and no replicate exceeds 1.98%. The enlarged world-1 cell, which is not part of this prediction, is 2.24%. |
| D(b) window-cohort likelihood k differs by at most 5% in every window and arm | **Fails.** It holds for E and P0 in every block, and for every arm on the Section 5.3 blocks (days 1–50). It fails for A0 from days 71–80 and for world 1 from days 51–60. |
