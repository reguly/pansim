# ACT-049 note 57: reading of the round 10 results (same k, different worlds; file 56_), with a correction to note 54

19 October 2026. Sources: `56_round10_results.md`, `56a_review_of_note55.md`, `56_r101_worlds.csv`, `56_r101_worlds_offspring.csv`, `56_r101_clusters.csv`, `56_r101_repeat_infections.csv`, `56_r102_r104_summary.csv`, `56_r102_r104_offspring.csv`. Numbers are recomputed from the delivered files unless marked as a calculation of mine (`57_recomputed_round10_shapes.csv`).

## 0. Correction to my reading of round 9 (note 54 and my message of 18 October)

I wrote that the round-9 gate cell (S8-2 tau 1, lambda 10, shape 1) "matches all three statistics at once" and that two moderate mechanisms "reach the observed pattern". That used the moment k and the zero and 80% shares of a negative binomial projected to mean 1.4 from the moment k (`zero_at_mean_1.4_mom`), the runner's convention. Those projected shares are not observations: two arms with the same moment k and mean must give the same projected shares. Measured on the observed histograms the gate cell has:

| quantity | gate cell, shape 1 | real pattern |
|---|---|---|
| moment k | 0.349 | about 0.3 |
| likelihood k | 0.510 | about 0.3 (published k are negative-binomial likelihood fits) |
| observed zero share (own mean 1.54) | 47.8% | about 59% |
| observed share of infectors causing 80% | 25.7% | about 19% to 20% |

so the match was on moment k only. In rounds 5 and 6 I held events to the observed zero share (34% against 59%) and called the failure a failure; the same standard applied here gives a gap of 7.7 points to the negative binomial at the same mean and k, and of 11 points to the real pattern. The composition rule itself stands (it is a statement about moment k, and held in 12 of 12 cells). What changes is where the real pattern is reached.

**Where the real pattern is reached on observed statistics** (likelihood k, observed zero share, observed 80% share, all from the histograms):

| arm | mean | moment k | likelihood k | zero share | causing 80% | largest |
|---|---|---|---|---|---|---|
| world 1, multiplier only (shape 0.32) | 1.41 | 0.338 | 0.357 | 56.6% | 21.5% | 54 |
| R10-4, strongest scene plus shape 0.5 (S8-2 tau 1 lambda 30) | 1.66 | 0.191 | 0.284 | 56.9% | 17.9% | 86 |
| round 9 gate cell, shape 1 | 1.54 | 0.349 | 0.510 | 47.8% | 25.7% | 61 |
| round 9 S8-2 tau 1 lambda 30, shape 1 | 1.61 | 0.310 | 0.435 | 49.8% | 24.0% | not recomputed here |
| world 3, closed-group events | 1.43 | 0.385 | 1.199 | 34.1% | 37.4% | 36 |

(For a negative binomial with k = 0.3 at the same mean the zero share is 57% to 59% and 19% of infectors cause 80% of infections.) Two consequences:

1. The R10-4 "upper bound" (moment k 0.191) is, on the likelihood estimator, a match to the real pattern (0.284, 56.9%, 17.9%), not an overshoot. So **the scene-plus-multiplier route reaches the real pattern, on the like-for-like estimator, only with the strongest scene (a 5% minority at venues 30 times riskier for 11 hours a day) and a multiplier of shape 0.5.** That is not two moderate mechanisms; the multiplier alone at shape 0.32 does it with no scene. What the scene buys is a lower variance requirement for the multiplier (squared coefficient of variation 2 instead of 3.1), at the price of an extreme scene.
2. The moment k is not the like-for-like quantity. I will report both estimators everywhere and treat the likelihood k and the observed shares as the test of "reaches the real pattern".

The title and the abstract claims below are revised accordingly (section 5).

## 1. Verification

1. For all 9 arms (three worlds, R10-2, R10-3 with its control, R10-4, two round-9 comparators) the moment k, likelihood k, zero share, 80% share and maximum reproduce from the offspring histograms (for example world 2: 0.349, 0.510, 47.8%, 25.7%, 61). The runner's cluster table (largest offspring, distinct venues, one-venue-day share) reproduces from `56_r101_clusters.csv` (360 rows): 17.3, 18.4 and 22.9 offspring; 6.2, 8.78 and 2.08 distinct venues; 19.8%, 15.5% and 91.1% in one venue-day.
2. The repeat-infection correlations are as reported (world 1: -0.0122, 95% interval -0.0267 to -0.0004, 11,877 pairs; world 2: 0.104, 0.0889 to 0.117, 5,285 pairs).
3. R10-3 arithmetic: the realised share of nominal added variance is (1 + 1/0.621)/(1 + 1/2.331) - 1 = 0.826 against 0.706 in round 9, as reported. The fraction of the round-9 shortfall recovered is (0.826 - 0.705)/(1 - 0.705) = **41%**, which the runner calls "about half".
4. The household secondary attack rates are rates per susceptible household contact summed over the run (16.5, 15.2 and 13.5 million contact-units), so only ratios are interpretable (world 1 over world 2: 1.96, as reported).

## 2. What round 10 shows

1. **Three mechanisms at the same moment k (0.338, 0.349, 0.385) are distinguishable, mostly by shape and place, not by size.** Home share 34.2%, 14.8%, 40.6%; high-L venue types 16.7%, 77.1%, 13.4%; share of the ten largest clusters in one venue-day 19.8%, 15.5%, 91.1% (distinct venues 6.2, 8.8, 2.1); largest offspring 54, 61, 36 (no separation of worlds 1 and 2). World 3 is matched only to 10% and its interval does not overlap world 2's (0.358 to 0.422 against 0.314 to 0.386), so the world 3 contrasts are approximate.
2. **The two estimators are a fingerprint.** Likelihood over moment k is 1.06, 1.46 and 3.11, and the observed zero share falls short of the negative binomial at the same moment k by 0.9, 7.7 and 21 points. This is the quantity round 9 hid by projecting to a matched mean. A heavy far tail on a negative-binomial body (events, a class at risky venues) separates the estimators; a smooth per-episode multiplier does not. Real datasets give both estimators at once, so this is a testable prediction. A caveat for use on real data: ascertainment (under-detection) changes both estimators (note 44), so the ratio would have to be recomputed under thinning.
3. **Repeat infections separate worlds 1 and 2** (-0.012 against 0.104), because membership of the venue class persists across episodes. My registered "below 0.1 in both" is borderline rather than clearly failed: world 2's interval (0.089 to 0.117) spans 0.1. The registered claim that the statistic should not separate the worlds fails clearly.
4. **Who the top 1% of infectors are** differs by world, with sampling uncertainty that the note does not give (top 1% is 136, 96 and 134 infectors; my z-scores against the all-infector share): world 1, elementary-school children 21.5% against 9.8% (z 4.6) and stay-at-home adults 9.6% against 24.1% (z -3.9); world 2, stay-at-home adults 47.9% against 37.3% (z 2.1) and mean age +4.5 years (about 2 standard errors); world 3, full-time workers 62.2% against 47.5% (z 3.4). **Treat these as properties of this model's rules, not as predictions.** In world 2 pupils are excluded by construction (the class is drawn from agent types 4 to 8, age 15 and over), and in world 3 events are placed at restaurants and shops. The reason given for world 1 (classrooms are the densest places an ordinary agent visits) is plausible and untested.
5. **R10-2 met** (correlated multiplier: k 0.382, 24.7% below the independent cell; registered 0.41, about 19% below). **R10-4 met on moment k (0.191 against 0.18)**, and see section 0 for its likelihood k.
6. **R10-3 scoring.** My note 55 did not say which baseline the "ratio to prediction" used. On the nominal baseline of 4.59 the ratio is 0.891 (below 1.1, as registered); on the like-for-like baseline of that world (2.33) it is 1.154 (not below 1.1). The largest cluster rose from 20 to 27, below the registered 30. The direction (ratio down, cluster larger, realised variance share 0.705 to 0.826) confirms the ceiling explanation; households recover 41% of the shortfall and a second ceiling remains.

## 3. Predictions scored (mine, note 55)

Met: (a) home share (19.4 points), (c) household attack rate ratio 1.96, (e) events keep the lowest zero share, R10-2, R10-4 (moment k).
Failed: (b) largest cluster ratio 1.13 against at least 2; (d) in its claim that repeat correlation does not separate the worlds (point estimate 0.104 against below 0.1, interval spans 0.1).
Mixed: R10-3 (0.891 on the nominal baseline, 1.154 like-for-like; largest cluster 27 against 30).
My own error to carry: I matched the worlds on moment k; matched on likelihood k the comparison is not yet done, and events cannot reach it (likelihood k 1.2 at best here, 1.8 for the best round-6 cell).

## 4. The honest state of the study

| mechanism family | reaches likelihood k near 0.3 on observed statistics? | note |
|---|---|---|
| occupancy and crowding, mobility | no (k 1.6 to 5) | bounded by time budget and home share |
| risk per hour, tilted minority | no at plausible settings; moment k 0.85 | |
| rare events, closed groups | no (likelihood k 1.2 to 1.8; zero share 34%) | tail without shape |
| per-person or per-episode infectiousness | yes (0.357, 56.6%, 21.5%) | needs a source |
| strongest venue scene plus shape 0.5 | yes (0.284, 56.9%, 17.9%) | extreme scene; multiplier still required |
| venue scene (moderate) plus shape 1 | no: 0.43 to 0.51, zero share 48% to 50% | closer than any single mechanism except the multiplier |

So the supportable sentence is: **in this model only variation in infectiousness between infections reproduces the observed offspring distribution; places and events do not do it, but they change what the superspreading looks like (cluster composition, home share, occupation, repeat correlation, the gap between estimators), and a strong venue scene lets a milder multiplier suffice.**

## 5. Publication

Titles that follow from this (the earlier candidates over-claimed in round 9):

1. "Same dispersion, different worlds: what an agent-based city says about the causes of superspreading"
2. "Superspreading is variation in infectiousness; places and events decide what it looks like"
3. "Not crowds, not commuters, not events: only unequal infectiousness reproduces superspreading in an agent-based city"
4. "What produces superspreading? Four explanations compared in an agent-based city"

My preference is 1 or 2: the paper's distinctive contribution is that identical k can arise from observably different worlds and that the fingerprints are cluster composition, place, the pair of k estimators and repeat infections. Title 3 states the negative result, which is the firmest.

## 6. What to run next (note 58)

Matching on the like-for-like estimator: scene-plus-multiplier arms tuned to likelihood k about 0.35, with world 1 as comparator, and a per-episode redrawn class to test the repeat-infection fingerprint. Events cannot be matched and are reported at their lowest likelihood k.
