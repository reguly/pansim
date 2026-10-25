# 83. Round 16 results

25 October 2026, 14:02 CET. Reply to note 82. The pre-run review is `82a_review_of_note82.md`. Code: `superspreader/study/run_round16.py`, `superspreader/study/analyze_round16.py`. Binary: a fresh Release build of `build_r10/panSim`. Location and agent files were not edited.

## What was not run

- **Run E, four of the five cells.** World 1 at density exponent 1 was re-run (seeds 77001–77012). Its offspring histograms differ from the round-15 histograms in every replicate, so that cell was stopped. Worlds 2b and 3b at exponent 1, and world 1 at exponents 0.5 and 0, were not run. No episode file is offered as a round-15 composition table.
- **Run C.** The scene-flag repair is in the source and is described below. The S8-3 re-runs, the Table 5.14b controls, and the S8-2 comparison were not run. Byte-identity against the October S8 deliveries was not established: a fresh build already fails to reproduce a stored world-1 trace (see Run E).
- **Run D.** The 16-week PS1 arms and the enlarged-map world-1 B1 cell with the episode trace were not run.

Runs A, B, F, G and H were completed. F and H use stored traces only.

## A fresh build does not reproduce the October traces

The simulator source under `include/` and `src/` has not changed in git since 19 October 2026 (commit `558295a`), which is before the round-14 and round-15 runs. Recompiling that source on this machine today is bitwise deterministic with itself and does not match the stored runs.

World 1, B1, seed 77001, coefficient `0.00051517`, shedding shape 0.24, four weeks, the command line stored in the round-14 `command.json`:

| run | day-5 cumulative infections | day-28 cumulative infections | trace vs the fresh build |
|---|---|---|---|
| stored round-14 replicate | 626 | 5,236 | differs |
| fresh build of current HEAD, run twice | 628 | 4,508 | the two traces are byte-identical |
| `build_r67/panSim` (16 October) | 628 | 4,508 | same day-5 and day-28 figures |
| fresh build plus `--infectiousEpisodeLog` | 628 | 4,508 | byte-identical to the fresh build with the log off |

The divergence is two infections on day 5. It then compounds. The episode log does not add a further change: with the log on, the world-1 seed-77001 trace equals the fresh build with the log off. Runs A and B below are calibrations on this fresh, deterministic binary. They are not a continuation of the October random stream.

## Errors recorded before running

The five points in `82a_review_of_note82.md` still stand. Two of them are now measured.

1. **Run E.** The shedding multiplier is drawn once per infection, not once per stay. A stay-level concentration H in 0.65–0.90 was not computed, because the cell was stopped on the histogram check.
2. **Run C.** The repair composes the scene scale with the mean-preserving factor. The S8-3 re-run that would test prediction C(a) was not done. The review's expectation, that total non-class discretionary hours stay well below the baseline after the repair, is unchanged and untested.
3. **Run D** was not run. The review's expectation that D(a) fails on the original map is untested.
4. **Run F.** The two script differences named in the review are real. Applying one canonical rule does not make every previously delivered number identical: four cells move by more than 0.6 percentage points. See Run F.
5. **Run G.** The two hour definitions are both in `83_g_hours.csv`. The role-based total is invariant across tilt. The sum over physical types 1, 5, 6, 7, 8, 9 and 10 rises with tilt. See Run G.

## Code changes

| file | what changed | size of the diff against HEAD |
|---|---|---|
| `include/policies/infectionPolicies.h` | New option `--infectiousEpisodeLog`. `recordBackgroundInfectiousEpisodes` and `flushActiveInfectiousEpisode` accumulate one row per venue-stay of a days-1–10 index case over the next 14 days. `runGroupEvents` adds a row for each closed-group event in that window. `writeInfectiousEpisodeLog` writes the TSV at shutdown. The index day is the day the infection was first observed, not `agentStats.infectedTimestamp` after a later reinfection, and a child counted at the time of infection is kept if that child is later reinfected. The expected count is the sum of per-susceptible hazards at multiplier 1 (shed and event boost removed), which is the linear weight the composition formula uses. | +329 lines, −4 lines |
| `include/policies/movementPolicies.h` | `hviOthersChance` takes the mean-preserving factor `u` and calls `hviEffectiveChance` before scaling high-L chances by `s`. The movement kernel passes `hviU` at both call sites. With `hviOthersHighScale` left at 1 the branch is not taken. | +7 lines, −6 lines |

With the log off, world 1 seed 77001 is byte-identical to a fresh build of HEAD. That is the byte-identity check for this code change. It does not reproduce the October binary.

## Run E

Stopped on world 1, exponent 1, seeds 77001–77012, coefficient `0.00051516976`, four weeks. All 12 replicates differ from `74_d_replicate_histograms.csv` (`w1:B1_alpha1`). Replicate 1 moves 75 index cases across 17 bins (for example the zero-offspring count is 502 against 560). The full bin list is `83_e_hist_diff.csv`. Day 28 of replicate 1 is 4,508 against 5,236 in the stored run.

The same command without the episode log, on the fresh binary, produces the same trace. The histogram failure is the rebuild, not the log. The other four cells were not run.

Predictions E(a)–E(d) are not scored.

## Run A

World 3b, B1 mechanism: event rate 0.17, group 30, factor 3,000, types 5 and 8, duration 2 hours. Background coefficient calibrated to day 28 within 3% of 6,211.25 by the secant loop, at most five trials, no pilot. Each accepted coefficient was then run on seeds 88001–88036.

The October coefficient `0.000105872` gives day 28 about 14% low on this binary (5,294, 5,121, 5,575 and 5,330 on the four sets). The secant corrects it in two or three trials.

| set | trials | coefficient | day 28 on its own seeds | day 28 on all 36 | early R | likelihood k (90% bootstrap) | jackknife-t | moment k | zero-share gap, points (bootstrap) | Delaporte baseline |
|---|---|---|---|---|---|---|---|---|---|---|
| 88001–88012 | 3 | 0.000114064 | 6,183 (−0.5%) | 5,922 | 1.463 | 0.269 (0.263 to 0.276) | 0.262 to 0.276 | 0.154 | −3.17 (−3.25 to −3.07) | 0.271 |
| 88013–88024 | 2 | 0.000120413 | 6,397 (+3.0%) | 6,795 | 1.517 | 0.276 (0.271 to 0.282) | 0.270 to 0.282 | 0.153 | −3.49 (−3.56 to −3.40) | 0.276 |
| 88025–88036 | 2 | 0.000113783 | 6,027 (−3.0%) | 5,906 | 1.462 | 0.269 (0.263 to 0.276) | 0.262 to 0.276 | 0.154 | −3.16 (−3.24 to −3.07) | 0.270 |
| 88001–88036 | 2 | 0.000117243 | 6,388 (+2.8%) | 6,388 | 1.507 | 0.272 (0.266 to 0.278) | 0.265 to 0.279 | 0.155 | −3.34 (−3.42 to −3.25) | 0.271 |

The +3.0% and −3.0% rows are inside the 3% window (2.99% and 2.97%). Intervals are replicate bootstrap, 1,000 draws, 5th and 95th percentiles, seed 20261016, and the jackknife-t interval used in note 81 (leave-one-replicate-out standard error times the 95% point of t on 35 degrees of freedom). The zero-share gap is 100 times (observed zero share minus the negative-binomial zero share at the cell's own mean and likelihood k). Trials are in `83_a_trials.csv`. The pooled rows are in `83_a_summary.csv`.

| prediction | outcome |
|---|---|
| A(a) the three 12-seed coefficients differ by more than 4% between the largest and the smallest | **Holds.** 0.000120413 / 0.000113783 − 1 = 5.83%. |
| A(b) the 36-seed coefficient is within 4% of the mean of the three | **Holds.** Mean of the three is 0.000116087. The 36-seed coefficient is 1.00% above it. |
| A(c) likelihood k of the 36-seed cell is within 0.03 of 0.248 | **Holds.** 0.272 is 0.024 above 0.248. |
| A(d) the 36-seed zero-share gap is between −3.3 and −2.5 points | **Fails, narrowly.** The gap is −3.34 points. The bootstrap interval is −3.42 to −3.25, which crosses −3.3. |

## Run B

Round-14 B2 parameters and coefficients were the starting point (not the world-3b search that ran past the old trial limit). Up to five trials on seeds 89001–89012, then up to four more if the mean was still outside 3% of 0.88, then one 36-seed run at the trial closest to 0.88. Both the background coefficient and the tuned parameter (shedding shape, or the event rate in world 3b) were updated each trial, as in round 14. No trial was added after the ninth.

| world | trials | parameter | coefficient | 36-seed early R | vs 0.88 | likelihood k | moment k | zero gap, points | share 0 | share 1–5 | share above 5 | maximum | NB value with P(X ≥ m) = 1/n |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| world 1 | 1 | shape 0.2437 | 0.00029674 | 0.890 | +1.1% | 0.252 | 0.247 | −0.04 | 68.3% | 27.9% | 3.85% | 27 | 28 |
| world 2b | 1 | shape 0.3966 | 7.114e-05 | 0.902 | +2.5% | 0.258 | 0.181 | −0.50 | 67.3% | 29.2% | 3.45% | 41 | 26 |
| world 3b | 9 | rate 0.07216 | 0.00011309 | 0.889 | +1.0% | 0.350 | 0.133 | −3.07 | 61.2% | 36.1% | 2.72% | 28 | 22 |

World 3b's 12-seed trial 2 had mean 0.900 (+2.3%) and likelihood k 0.353. Later trials, still inside the nine, moved the event rate and the mean left that window (means 0.72 to 1.00, likelihood k 0.185 to 0.353). The 36-seed cell uses trial 2, the closest mean. Likelihood k on that cell is 0.350, not 0.27. Every trial is in `83_b_trials.csv`. The 36-seed rows are in `83_b_summary.csv`.

The negative-binomial column is the smallest integer m such that a negative binomial with the cell's own mean and likelihood k has P(X ≥ m) ≤ 1/n, n the number of index cases (16,853, 10,529 and 14,491).

| prediction | outcome |
|---|---|
| B(a) each world reaches mean 0.88 within 3% within nine trials | **Holds** on the 36-seed cells: +1.1%, +2.5%, +1.0%. World 3b's matching 12-seed trial is trial 2. |
| B(b) the three maxima differ by less than a factor of 2 | **Holds.** Maxima 27, 41 and 28. The largest is 1.52 times the smallest. Round 14 was 28, 54 and 40. |
| B(c) world 3b zero-share gap between −2.6 and −2.0 | **Fails.** The gap is −3.07 points. The cell's likelihood k is 0.350, not the 0.27 the published comparison was built at. |

## Run F

One rule, applied to the stored traces: index cases are infections on days 1–10 with a known infector; offspring and cluster composition both use children with 0 ≤ child day − index day ≤ 14; the ten largest clusters are offspring descending, then infector id ascending. `83_f_diff.csv` has 39 cells.

Which table used which script before this run:

| table | previous script | what differed from the rule above |
|---|---|---|
| 5.16b | `analyze_round11.py`, and the round-13 reanalysis `analyze_round13.py` `replicate_core` that wrote `66_n0_replicate_summary.csv` | `np.argsort` (unstable), and composition included children past day 14 |
| 5.16f | `analyze_round13.py` `replicate_core`, file `66_n1_replicate_summary.csv` | the same two differences |
| 5.17a, all-detected rows (`detection_rate` 1, scheme `full`) | `analyze_round12.py` thinning | already limited composition to 14 days; tie-break was not infector id |
| 5.19b | `analyze_round14.py`, which calls `analyze_round13.py` | the same two differences as 5.16 |
| 5.22a | `analyze_round15.py` `replicate_core_d` | composition used every child in the trace; ties kept trace order |

The canonical numbers for a trace are the same wherever that trace appears. World 1's new same-household share is 0.171 in both Table 5.16b and the all-detected row of Table 5.17a. The old figures were 0.177 and 0.178.

| prediction | outcome |
|---|---|
| F(a) every difference at most 0.6 percentage points in the shares and at most 0.2 in distinct venues | **Fails in 4 of 39 cells.** Distinct venues stay inside 0.2 everywhere (largest shift 0.192). The share failures are: 5.16f `w2b:s78_frozen` same-household 0.68 points; 5.17a world 1 all-detected same-household 0.74 points; 5.22a `w1:D_alpha0.5` venue-day 0.62 points; 5.22a `w2b:D_alpha0` venue-day 0.70 points. The other 35 cells are inside both bars. Largest shifts by table: 5.16b 0.57 points and 0.11 venues; 5.19b 0.39 points and 0.18 venues. |

## Run G

Movement only, two weeks, background coefficient 0, the round-8 class (5% of eligible agents, hours multiplier 3, mean-preserving scales). Seeds 77001–77012 at tilt 0, 0.5 and 1, and seed 73001 at the same three tilts (the seed behind `50_r80_hours_by_type.csv`). Eligible agents are types 4–8 aged 15 or older. The class is that design's class among them. `83_g_hours.csv`.

Two totals, class, seeds 77001–77012:

| tilt | role-discretionary hours per day | sum of hdt over types 1, 5, 6, 7, 8, 9, 10 | hdt share at types 5, 6, 9, 10 | all hours at types 5, 6, 9, 10 |
|---|---|---|---|---|
| 0 | 11.083 | 9.943 | 58.8% | 5.903 |
| 0.5 | 11.084 | 10.486 | 80.4% | 8.494 |
| 1 | 11.082 | 11.022 | 100.0% | 11.080 |

Everyone else who is eligible, same seeds: role-discretionary hours 3.831 per day at all three tilts; the hdt sum is 3.420; the hdt share at the four risky types is 53.2%; all hours at those types are 1.868. Seed 73001 is within 0.2% of these figures (class hdt 9.926, 10.464, 11.014; others hdt 3.425; all hours at the four types 5.900 and 1.869).

The published figures and which total they are:

| published figure | what it is | population | this run, tilt 0, seeds 77001–77012 |
|---|---|---|---|
| 9.88 | sum of hdt over types 1, 5, 6, 7, 8, 9, 10 | class | 9.943 |
| 5.90 | all hours at types 5, 6, 9, 10, including role-4 work | class | 5.903 |
| 59.1% | hdt at types 5, 6, 9, 10, divided by the hdt sum | class | 58.8% |
| 3.40 | the same hdt sum | other eligible agents | 3.420 |
| 1.87 | all hours at types 5, 6, 9, 10 | other eligible agents | 1.868 |
| 53.5% | hdt at types 5, 6, 9, 10, divided by the hdt sum | other eligible agents | 53.2% |

1.87/3.40 is not 53.5% because 1.87 counts work hours at those physical types and 3.40 does not. 5.90/9.88 is the same mismatch for the class.

| prediction | outcome |
|---|---|
| G(a) total class discretionary hours at tilt 0, 0.5 and 1 differ by at most 3% | **Holds for role-discretionary hours.** Seeds 77001–77012: 11.083, 11.084, 11.082 (spread 0.019%). Seed 73001: spread 0.11%. **Fails for the hdt sum** that Section 5.14 quoted: 9.943, 10.486, 11.022 (spread 10.9%). The tilt does not change the time spent on a discretionary role. It moves some of that time from physical types that the hdt sum drops (home, school, hospital, nursing, university) onto types 5, 6, 9 and 10, so the sum rises until, at tilt 1, it meets the role total. |

## Run H

`83_h_replicate_histograms.csv`, 15,762 rows, 1,053,222 bytes. Every cell of `70_delaporte_fits_A.csv` (Table 5.20a, 12 cells), `70_delaporte_fits_B.csv` (Table 5.20b, 10 cells) and `74_d_cells_summary.csv` (Table 5.22a, 9 cells). Columns: table, cell, source file, replicate, seed, number of index cases in the replicate, offspring, count of index cases. Offspring runs from 0 to the replicate maximum, including bins with count 0. No new runs. No cell was missing from the stored histogram files.

## Files

`83_e_hist_diff.csv`, `83_a_trials.csv`, `83_a_summary.csv`, `83_b_trials.csv`, `83_b_summary.csv`, `83_f_diff.csv`, `83_g_hours.csv`, `83_h_replicate_histograms.csv`.
