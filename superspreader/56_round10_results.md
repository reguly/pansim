# ACT-049 note 56: round 10, the same k in different worlds

19 October 2026. Reply to note 55. Review and the registered predictions: `56a_review_of_note55.md`. Code: `superspreader/study/run_round10.py`, `analyze_round10.py`, `report_round10.py`, `t1_round10.py`, `build_r10_inputs.py`; the per-agent mean of the per-episode multiplier added in `include/locationList.h` and `include/policies/infectionPolicies.h` (uncommitted); binary `build_r10`. The location and agent files are not edited; the household-suppressed location file is a new copy.

## Headline

1. **The three worlds are distinguishable at the same k, and the statistic that does it is not the one note 55 expected.** Tuned to moment k 0.338, 0.349 and 0.385, they differ sharply in where infections happen (home share 34.2%, 14.8%, 40.6%; share at the four high-L venue types 16.7%, 77.1%, 13.4%) and in the shape of their largest clusters, but **not** in cluster size.
2. **The sharpest single discriminator is cluster composition.** In the ten largest clusters of each replicate, the share of infections that happened in one venue on one day is 19.8% in world 1, 15.5% in world 2 and 91.1% in world 3, over 6.2, 8.8 and 2.1 distinct venues. An events world makes single-venue explosions; the other two spread the same number of offspring over six to nine places.
3. **Registered prediction (b) fails, and the reason matters.** The largest cluster of world 2 is 61 against 54 in world 1, a ratio of 1.13, not the predicted 2 or more. The round-9 contrast that motivated the prediction (20 against 61) was measured at unmatched k; once the multiplier is strong enough to reach k = 0.34 on its own, it produces clusters nearly as large as the scene does.
4. **Registered prediction (d) fails, and in the most interesting way.** The offspring correlation across repeated infections of the same agent is -0.0122 in world 1 and 0.104 in world 2. The note expected both below 0.1 and expected this statistic *not* to separate the worlds. It does separate them, because world 2 contains a persistent ingredient that world 1 lacks: the venue class is a property of the agent, carried across episodes, even though its multiplier is drawn per episode.
5. **R10-2 and R10-4 met; R10-3 confirms its direction but misses both thresholds.** The correlated multiplier gives k 0.382 against a predicted 0.41, which is 24.7% below the independent cell. The upper bound gives 0.191 against a predicted 0.18, so the model can overshoot the real value and the round-9 match is a located point. Suppressing households raises the multiplier's realised share of its nominal variance from 0.705 to 0.826, not to 1, so households are about half of that shortfall and a second ceiling remains.

## 1. Deviations and points on note 55

The review (`56a`) is unchanged by the results. Deviations and things worth knowing:

- **D1. The code change for R10-2** adds `--sheddingClassMean` and `--sheddingOthersMean`: the per-episode gamma keeps its shape and is multiplied by a per-agent mean taken from the HVI class flags. Both default off. T1 passed in the strong form: with the options off, the trace and the daily table of three round-9 arms are byte-identical to `build_r9`.
- **D2. R10-3 needed no code.** Household transmission is suppressed with a copy of the location file in which the infectiousness of the 73,036 homes is 0. Movement is unchanged, so agents still go home; they just do not transmit there.
- **D3. A control arm was added to R10-3** (`56a` item 4), because suppressing households changes the baseline dispersion itself: the no-multiplier baseline of that world is moment k 2.33, not 4.59. Both readings are reported below.
- **D4. R10-2 realised means.** Class members drew a mean multiplier of 1.483 and the others 0.975 (nominal 1.5 and 0.974), a ratio of 1.522 against the nominal 1.540. The class is 4.40% of agents, so the population mean is 0.997 rather than 1 (`56a` item 5); among infections the mean is 1.096, because the class is infected more often, and the day-28 recalibration absorbs it.
- **D5. World 3 was retuned**, as foreseen: the round-6 cell with the lowest likelihood k sits at moment k 0.152, so I lowered the event rate to 0.034, which gives 0.385. That is 10% above world 2 and the closest of the settings tried; its interval (0.358 to 0.422) does not overlap world 2's (0.314 to 0.386), so world 3 is matched only approximately and I say so wherever it matters.
- **D6. Day 28** is within 3% in every arm (largest deviation +1.3%, world 1).
- **D7. All code is uncommitted**, as in previous rounds.

## 2. R10-1: the three worlds at matched k (12 replicates, 4 weeks, same seeds)

| world | coefficient | moment k | likelihood k | k likelihood over moment | early R | zero share | zero at mean 1.4 | causing 80% | causing 80% at mean 1.4 | day 28 vs 6,211 |
|---|---|---|---|---|---|---|---|---|---|---|
| world 1, multiplier only (shape 0.32) | 0.000499 | 0.338 (0.307 to 0.37) | 0.357 (0.346 to 0.368) | 1.06 | 1.4 (1.37 to 1.44) | 56.6% (56.0 to 57.2) | 57.5% | 21.5% | 20.7% | 1.3% |
| world 2, scene plus multiplier (round-9 gate cell) | 0.000119 | 0.349 (0.314 to 0.386) | 0.51 (0.494 to 0.528) | 1.46 | 1.54 (1.48 to 1.58) | 47.8% (47.0 to 48.7) | 57.0% | 25.7% | 21.1% | -0.2% |
| world 3, closed-group events (group 30, rate 0.034) | 0.000332 | 0.385 (0.358 to 0.422) | 1.2 (1.12 to 1.3) | 3.11 | 1.43 (1.39 to 1.47) | 34.1% (33.2 to 35.0) | 55.4% | 37.4% | 22.2% | -1.1% |

Worlds 1 and 2 are matched to 3% on the moment estimator and their intervals overlap; world 3 is 10% above and its interval does not (D5). The real pattern is about 0.3 for k, about 59% of infectors with no offspring and about 20% causing 80%, at a mean of 1.4.

Two things are already visible in this table and were not registered. **The likelihood estimator separates the worlds even though the moment estimator was matched by construction**: the ratio of the two runs 1.06, 1.46 and 3.11. A single pair of estimators on real data would therefore carry information about the mechanism. **And the observed zero share differs by 22 points** (56.6%, 47.8%, 34.1%) at nearly the same moment k, because the three distributions are not equally well described by a negative binomial; projected to a common mean of 1.4 they converge to 57.5%, 57.0% and 55.4%, which is what hides the difference.

### Where transmission happens

| world | home | school and work | the four high-L types | restaurant | large venue | church | recreation | household secondary attack rate |
|---|---|---|---|---|---|---|---|---|
| world 1, multiplier only (shape 0.32) | 34.2% | 17.5% | 16.7% | 5.1% | 5.5% | 1.7% | 4.4% | 0.00165 |
| world 2, scene plus multiplier (round-9 gate cell) | 14.8% | 2.5% | 77.1% | 22.3% | 24.7% | 11.1% | 19.0% | 0.000842 |
| world 3, closed-group events (group 30, rate 0.034) | 40.6% | 10.8% | 13.4% | 5.5% | 3.8% | 1.1% | 3.0% | 0.00228 |

### Cluster size and composition

| world | largest offspring (max over replicates) | largest offspring (mean over replicates) | offspring p99 | offspring p99.9 | ten largest clusters: mean offspring | distinct venues | share in one venue-day |
|---|---|---|---|---|---|---|---|
| world 1, multiplier only (shape 0.32) | 54 | 27.7 | 12.1 | 22.4 | 17.3 | 6.2 | 19.8% |
| world 2, scene plus multiplier (round-9 gate cell) | 61 | 30.8 | 13.6 | 27 | 18.4 | 8.78 | 15.5% |
| world 3, closed-group events (group 30, rate 0.034) | 36 | 31.7 | 10.6 | 28.8 | 22.9 | 2.08 | 91.1% |

The per-cluster rows are in `56_r101_clusters.csv`. Cluster **size** does not separate worlds 1 and 2 at matched k; cluster **shape** separates all three.

### Who the big infectors are

| world | mean age of the top 1% of infectors | mean age of all infectors | difference | share of the top 1% in the class |
|---|---|---|---|---|
| world 1, multiplier only (shape 0.32) | 31.66 | 38.08 | -6.42 | n/a |
| world 2, scene plus multiplier (round-9 gate cell) | 48.08 | 43.63 | 4.45 | 94.4% |
| world 3, closed-group events (group 30, rate 0.034) | 38.5 | 38.95 | -0.442 | n/a |

The age profile is a third discriminator and it points in opposite directions: in world 1 the biggest infectors are **younger** than average infectors by 6.4 years, in world 2 they are **older** by 4.5 years, and in world 3 they are an ordinary sample (0.4 years). In world 2, 94.4% of the top 1% of infectors belong to the 5% class.

The occupational profile is sharper still, and it is the kind of thing a contact-tracing study records. Share of the top 1% of infectors against the share of all infectors, by agent type:

| agent type | world 1: top 1% / all | world 2: top 1% / all | world 3: top 1% / all |
|---|---|---|---|
| kindergarten | 2.2% / 3.7% | 0.0% / 1.3% | 0.7% / 3.8% |
| elementary school | 21.5% / 9.8% | 0.0% / 3.1% | 13.3% / 9.1% |
| high school | 9.6% / 6.2% | 5.2% / 4.9% | 0.7% / 4.8% |
| university | 4.4% / 5.9% | 3.1% / 5.7% | 0.7% / 5.1% |
| full-time worker | 48.1% / 44.9% | 35.4% / 42.1% | 62.2% / 47.5% |
| afternoon-shift worker | 4.4% / 3.9% | 8.3% / 4.3% | 3.0% / 3.2% |
| stay at home | 9.6% / 24.1% | 47.9% / 37.3% | 19.3% / 24.8% |

**The three worlds put superspreading in three different occupations.** In world 1 it is schoolchildren: elementary pupils are 21.5% of the top 1% of infectors against 9.8% of all infectors, a factor of 2.2, while people who stay at home are strongly under-represented (9.6% against 24.1%). A large per-episode multiplier pays off wherever the agent happens to be, and the densest places an ordinary agent goes are classrooms. In world 2 it is stay-at-home adults (47.9% against 37.3%), because the venue class is drawn from agents aged 15 and over and those with the most discretionary hours gain the most from it; no pupil can be a superspreader there at all (0% of the top 1%). In world 3 it is full-time workers (62.2% against 47.5%), because the events are drawn at restaurants and shops. An epidemiologist who knew only k would miss this entirely.

### Repeat infections (R10-1 item 4)

| world | replicates | pairs | Pearson correlation of offspring across two infections of the same agent | Spearman |
|---|---|---|---|---|
| world 1, multiplier only (shape 0.32) | 8 | 11877 | -0.0122 (-0.0267 to -0.000444) | -0.027 (-0.039 to -0.0171) |
| world 2, scene plus multiplier (round-9 gate cell) | 8 | 5285 | 0.104 (0.0889 to 0.117) | 0.113 (0.0961 to 0.132) |

16 weeks, 8 replicates, vaccination off, every episode logged. References: 0.544 for the persistent abstract trait of R6-2 and 0.041 for persistent mobility (round 7, S5).

This is the registered prediction that failed most informatively. Note 55 expected both worlds below 0.1 and expected the statistic not to separate them, on the ground that both causes are per-episode. World 1 is indeed per-episode and shows no correlation at all (slightly negative). World 2 is **not** purely per-episode: the agent's membership of the venue class persists for life, so an agent who is infected twice is at the high-L venues on both occasions, and only the multiplier is redrawn. The correlation of 0.104 is the persistent part showing through. **A repeat-infection study could therefore tell a purely biological per-episode cause from one with a behavioural component, even when k, the mean and the zero share agree.**

## 3. R10-2, R10-3 and R10-4

| arm | coefficient | moment k | likelihood k | zero share | home share | high-L share | largest offspring | day 28 vs 6,211 | predicted | observed over predicted |
|---|---|---|---|---|---|---|---|---|---|---|
| r102_correlated | 9.2e-05 | 0.382 (0.356 to 0.41) | 0.532 (0.516 to 0.548) | 45.3% (44.4 to 46.2) | 12.7% | 80.9% | 50 | -1.6% | 0.41 | 0.933 |
| r103_nohome_sh1 | 0.000734 | 0.621 (0.588 to 0.657) | 0.684 (0.655 to 0.716) | 43.8% (43.1 to 44.4) | 0.0% | 24.0% | 27 | -0.3% |  |  |
| r103_nohome_base | 0.000717 | 2.33 (2.14 to 2.53) | 2.47 (2.28 to 2.67) | 29.3% (28.3 to 30.4) | 0.0% | 23.8% | 16 | -0.5% |  |  |
| r104_upper | 4.32e-05 | 0.191 (0.174 to 0.208) | 0.284 (0.279 to 0.288) | 56.9% (56.2 to 57.5) | 5.9% | 91.3% | 86 | -0.4% | 0.18 | 1.06 |
| round9_reference_sh1 | 0.000453 | 0.928 (0.896 to 0.968) | 0.948 (0.913 to 0.987) | 42.2% (41.6 to 42.8) | 40.2% | 15.3% | 20 | -0.4% |  |  |
| round9_gate_sh2 | 0.000117 | 0.508 (0.477 to 0.544) | 0.702 (0.676 to 0.735) | 42.0% (41.4 to 42.5) | 15.2% | 76.8% | 41 | 0.9% |  |  |

### R10-2, the correlated multiplier

Observed moment k 0.382 (0.356 to 0.41) against the registered 0.41, acceptance 0.29 to 0.57: **met**, ratio 0.93. Against the independent cell of round 9 (0.508) it is **24.7% below**, where note 55's revised calculation expected about 19% and note 52 had said at least 20%. Concentrating the two risks in the same people therefore buys about a quarter of the dispersion, and the direction and size of the effect are as the coordinator calculated.

### R10-3, the multiplier without households

| reading | baseline k of that world | predicted k | observed k | observed over predicted | realised share of the nominal added CV^2 | largest offspring |
|---|---|---|---|---|---|---|
| round 9 reference, households present | 4.59 (model baseline) | 0.697 | 0.928 | 1.333 | 0.705 | 20 |
| R10-3, households suppressed, nominal baseline | 4.59 (nominal) | 0.697 | 0.621 | 0.891 | n/a | 27 |
| R10-3, households suppressed, measured baseline | 2.331 (control arm) | 0.538 | 0.621 | 1.154 | 0.826 | 27 |

The like-for-like comparison is the first and third rows, each using its own world's baseline. On that reading the ratio falls from 1.333 to 1.154 and the realised share of the multiplier's nominal variance rises from 0.705 to 0.826. **The direction is confirmed and the size is substantial, but both registered thresholds are missed**: the ratio does not fall below 1.1 and the largest cluster rises to 27, not above 30. The honest conclusion is that households are about half of the shortfall and that a second ceiling remains. The obvious candidate is the rest of the finite settings: with homes removed, the no-multiplier baseline is still only 2.33, school and work carry 22.1% of infections, the two shop types 30.4% and the four high-L types 24.0%, so most transmission still happens in places of fixed, modest size. Note also that suppressing households is not a small perturbation: it removes about 40% of all transmission and the coefficient has to rise from 0.00041 to 0.00073 to hold day 28.

### R10-4, the upper bound

Observed moment k 0.191 (0.174 to 0.208) against the registered 0.18, acceptance 0.126 to 0.252: **met**, ratio 1.06. The largest cluster is 86 and the zero share 56.9% (56.2 to 57.5). The model can therefore produce dispersion well past the observed value, which is what the cell was for: the round-9 match at shape 1 is a located point on a continuum, not the edge of what the model can do.

## 4. Predictions scored

| Test | Prediction | Result | Verdict |
|---|---|---|---|
| R10-1 (a) | home share differs by at least 15 points between worlds 1 and 2 | 34.2% against 14.8%, a difference of 19.4 points | **met** |
| R10-1 (b) | largest offspring of world 2 at least twice world 1 | 61 against 54, ratio 1.13 | **failed** |
| R10-1 (c) | household secondary attack rate of world 1 at least 1.5 times world 2 | 0.00165 against 0.000842, ratio 1.96 | **met** |
| R10-1 (d) | repeat-infection correlation below 0.1 in both, and should not separate the worlds | -0.0122 and 0.104 | **failed**: world 2 is above 0.1 and the statistic does separate them |
| R10-1 (e) | world 3 keeps a lower zero share than worlds 1 and 2 at the same k | 34.1% (33.2 to 35.0) against 56.6% (56.0 to 57.2) and 47.8% (47.0 to 48.7) | **met** |
| R10-2 | moment k 0.41, acceptance 0.29 to 0.57 | 0.382 | **met** |
| R10-3 | observed over predicted falls from 1.33 to below 1.1; largest offspring above 30 | 1.154 on the like-for-like reading; largest offspring 27 | **failed on both thresholds**, direction confirmed |
| R10-4 | moment k 0.18, acceptance 0.126 to 0.252 | 0.191 | **met** |

The note's own conclusion test was: if (a) to (c) hold, the paper can say that k alone does not identify the mechanism and that cluster composition does. (a) and (c) hold, (b) fails. **The conclusion survives in a stronger form than the test was written for**: k alone does not identify the mechanism, and cluster composition does, but cluster *size* does not, so the discriminating statistic has to be the shape of a cluster, not how big it is.

## 5. In plain terms

1. **The identifiability question has a clean answer.** Three mechanisms tuned to the same dispersion produce visibly different epidemics. An observer with cluster investigations could tell them apart: in the events world 91% of a large cluster happens in one place on one day, in the other two worlds 15% to 20% and the cluster is spread over six to nine venues. An observer with only k, the mean and the zero share at a matched mean could not.
2. **The statistic the paper should recommend is not cluster size.** At matched k the largest clusters are 54, 61 and 36, which is no basis for telling the worlds apart. What works is the share of a cluster concentrated in one venue-day, the share of infections at home, the household attack rate, the occupation and age of the biggest infectors, and the gap between the two k estimators.
3. **Each world puts superspreading in a different occupation**: schoolchildren, stay-at-home adults and full-time workers respectively. That is a prediction a real contact-tracing dataset could check directly, and it does not depend on measuring dispersion at all.
4. **A behavioural cause leaves a fingerprint in repeat infections that a biological one does not.** This was predicted to be the one statistic that would not separate the worlds, and it separates them, because a scene is a property of a person while shedding is a property of an episode.
5. **The household ceiling is real but partial.** Removing household transmission recovers about half of what the multiplier loses against its nominal variance. The rest is the other finite settings, so the round-9 explanation should be stated as 'the finite size of the groups an infectious person meets', of which households are the largest single part, rather than as households alone.

## 6. Open points

1. World 3 is matched only to 10% (D5). If the comparison matters for the paper, one more rate between 0.034 and 0.05 would bring it inside the interval; about 10 minutes.
2. The repeat-infection result suggests an experiment the study has not done: the same scene with the class redrawn every episode, which would remove the persistent part and should take the correlation back to zero. That would turn a suggestive difference into a controlled one; about 25 minutes.
3. R10-3's second ceiling is untested. With homes removed the largest remaining categories are the two shop types (30.4% of infections) and school and work (22.1%), all of them places of fixed and modest occupancy, so the natural follow-up is to suppress those too and see whether the realised fraction goes above 0.9.
4. World 3 was tuned on the event rate at one group size (30). The group size is the parameter that sets how large a single-venue explosion can be, so a sweep over it would say how much of the 91% one-venue-day share is a property of events in general rather than of this setting.

## Files

`56_round10_results.md` (this note), `56a_review_of_note55.md`, `56_r101_worlds.csv`, `56_r101_worlds_offspring.csv`, `56_r101_clusters.csv`, `56_r101_repeat_infections.csv`, `56_r102_r104_summary.csv`, `56_r102_r104_offspring.csv`, `56_upload_index.md`. No file exceeds 1 MB.
