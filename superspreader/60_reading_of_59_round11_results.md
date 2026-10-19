# ACT-049 note 60: reading of the round 11 results (worlds matched on likelihood k; file 59_), and whether to keep iterating

19 October 2026. Sources: `59_round11_results.md`, `59a_review_of_note58.md`, `59_r111_*.csv`, `59_r112_repeat_infections.csv`, `59_r113_cluster_composition.csv`, and (for verification of world 3b) `43_r67_closed_group_summary.csv` and `43_r67_offspring.csv` from round 6. Numbers are recomputed from the delivered files unless marked as my calculation.

## 1. Verdict in four lines

1. **The runner is right, and so is its correction of me.** A closed-group events arm from round 6 (group size 30, rate 0.1456) has likelihood k 0.330, which I verified from the round-6 histogram (0.3298; moment k 0.152; zero share 52.3%; 80% share 18.1%). My notes 57 and 58 said events cannot reach the like-for-like pattern, citing 1.2 and 1.8; those came from the group-size-100 arms and from the low-rate round-10 arm, and I never read the group-size-30 arm on the likelihood scale. **My note 57 conclusion ("only variation in infectiousness reproduces the observed distribution") is withdrawn.**
2. **On the like-for-like estimator all three mechanism families reach the real dispersion** (likelihood k 0.33 to 0.37, observed zero share 52% to 57%, 80% share 18% to 22%), each with its own tuned parameter. What separates them is the shape of the distribution, where transmission happens and what a cluster looks like, not whether they can get there.
3. **R11-1 (a) to (f) all hold; R11-2 is answered by a decomposition, not by the registered counterfactual** (the runner states this plainly).
4. **My recommendation on iterating: the mechanism question is answered; stop sweeping mechanisms. One short confirmatory round (note 61, about 1.5 hours) closes the two gaps that matter for the claims (paired seeds and event semantics; fingerprints under under-detection from the traces), then move to the paper.**

## 2. Verification

1. **Shapes.** All six arms reproduce from `59_r111_worlds_offspring.csv` (largest differences 4e-7 in moment k, 1.3e-6 in likelihood k, 5e-7 in zero share, 7e-5 in 80% share): world 1 0.338/0.357, world 2a 0.2365/0.3552, world 2b 0.2574/0.3654, world 3b 0.1524/0.3298; zero shares 56.6%, 52.8%, 53.5%, 52.3%; 80% shares 21.5%, 21.1%, 21.7%, 18.1%.
2. **Clusters and composition.** Means over the 120 clusters of each arm reproduce (`59_r111_clusters.csv`, `59_r113_cluster_composition.csv`): distinct venues 6.20, 9.22, 9.40, 1.74; one-venue-day share 19.8%, 14.7%, 14.5%, 88.2%; same-household share 17.7%, 3.3%, 6.5%, 3.9%; share in the modal venue type 49.2%, 41.9%, 40.5%, 96.8%.
3. **Repeat infections.** Pooled and within-group correlations reproduce from `59_r112_repeat_infections.csv` (world 2a: 0.0711 pooled, -0.0063 within the class, -0.0152 within non-members; gate cell 0.104, -0.0072, -0.0214). The decomposition is sound: two internally uncorrelated groups with mean offspring differing about four-fold produce a positive pooled correlation. Because class membership is fixed for life in the model, this shows that persistent membership carries the correlation; it does not exclude other persistent factors acting through membership.
4. **World 3b.** `event_offspring_share` 0.617 reproduces. The statement that "14.6% of agents attend a closed group every day" is not supported by the file: 83,086 events in 12 replicates is at most about 247 events a day, and with at most 30 attendees each at most about 4% of the 178,746 agents a day (if the count covers 28 days; fewer if it covers the whole run). Event rate 0.1456 is a parameter, not necessarily the share attending; ask the runner (note 61).
5. **Tuning arithmetic.** The runner says my 0.73 for world 2a was a linear-in-k interpolation. It was a log interpolation to a target of 0.357 (world 1's value); to a target of 0.350 it gives 0.703, as the runner found. Immaterial; the matched likelihood k values are 0.357, 0.355 and 0.365.

## 3. Where the study stands (replaces the table in note 57 section 4)

| family | tuned parameter | likelihood k | observed zero share | 80% share | NB fits? | cost or plausibility question |
|---|---|---|---|---|---|---|
| multiplier only | shape 0.32 (CV^2 3.1) | 0.357 | 56.6% | 21.5% | yes (0.0 pts) | needs a biological or behavioural source for a CV^2 near 3 |
| moderate scene + multiplier | lambda 10, shape 0.58 (CV^2 1.7) | 0.365 | 53.5% | 21.7% | yes (-1.1 pts) | a 5% minority at about 11 h/day at venues 10x riskier per hour |
| strong scene + multiplier | lambda 30, shape 0.70 (CV^2 1.4) | 0.355 | 52.8% | 21.1% | yes (-1.3 pts) | the same minority at venues 30x riskier |
| closed-group events | group 30, rate 0.1456 | 0.330 | 52.3% | 18.1% | no (-4.4 pts) | 61.7% of offspring occur inside events; the rate semantics need checking |
| earlier, not matched: crowding or occupancy, mobility, weak scenes | | 1.6 to 5 | | | | bounded by time budget and home share |

The supportable statements: (i) crowding and mobility cannot do it; (ii) three different mechanisms can, each at a parameter value that needs justification; (iii) matched on likelihood k they are told apart by place, cluster composition, repeat infections and the ratio of the two k estimators, **not by cluster size**; (iv) events are the only mechanism whose offspring distribution is not negative binomial.

## 4. First contact with real data (my calculation; weak evidence)

The pooled SARS-CoV-2 offspring distribution of McKee 2024 (9,591 index cases: 67% none, 30% one to five, 3% above five; mean 0.88; reported k 0.27) against a negative binomial with k 0.27 and mean 0.88 (zero 67.6%, one to five 28.8%, above five 3.6%): the observed zero share is 0.6 points below the negative binomial. The model arms, measured against their own likelihood fit, are 0.0 (world 1), -1.1 to -1.4 (scene worlds) and -4.4 points (events). The real pool is as close to a negative binomial as worlds 1 and 2 and closer than the events arm. **Caveats that make this weak:** the pooled k may have been fitted to the same data, so the negative binomial is favoured by construction; the pool mixes studies with different ascertainment; the rounded 3% for the tail has an uncertainty from 2.5% to 3.5% that spans the model ratios (0.70 to 1.00 of the negative binomial); and model means (1.4 to 1.6) differ from 0.88. I would not put it in the paper beyond a sentence. A proper test needs an individual-level offspring distribution with both estimators computable; that is a literature task, not a simulation.

## 5. Fingerprints under under-detection (my calculation from the round-11 histograms; `60_thinning_fingerprints.csv`, `60_ratio_sample_size.csv`)

Binomial thinning of offspring counts (random detection) leaves the moment k unchanged (algebraically) and moves the likelihood k, so the estimator ratio shrinks:

| world | ratio at full detection | 60% detected | 30% detected | zero share minus NB at 30% |
|---|---|---|---|---|
| multiplier only | 1.06 | 1.06 | 1.06 | 0.0 |
| moderate scene + multiplier | 1.42 | 1.34 | 1.24 | -0.3 pts |
| strong scene + multiplier | 1.50 | 1.41 | 1.29 | -0.3 pts |
| closed-group events | 2.17 | 1.72 | 1.30 | -0.5 pts |

How many observed infectors would be needed to separate them (bootstrap of the thinned histograms, 5th to 95th percentile of the ratio):

| world | detection | 1,000 infectors | 3,000 | 10,000 |
|---|---|---|---|---|
| multiplier only | full | 0.91 to 1.27 | 0.95 to 1.18 | 1.00 to 1.14 |
| multiplier only | 30% | 0.88 to 1.25 | 0.94 to 1.25 | 0.99 to 1.12 |
| moderate scene + multiplier | full | 1.16 to 1.65 | 1.23 to 1.60 | 1.34 to 1.52 |
| moderate scene + multiplier | 30% | 1.04 to 1.50 | 1.10 to 1.37 | 1.16 to 1.33 |
| strong scene + multiplier | full | 1.21 to 2.05 | 1.31 to 1.79 | 1.39 to 1.66 |
| strong scene + multiplier | 30% | 1.03 to 1.81 | 1.09 to 1.61 | 1.18 to 1.44 |
| closed-group events | full | 1.89 to 2.49 | 2.00 to 2.35 | 2.06 to 2.27 |
| closed-group events | 30% | 1.14 to 1.51 | 1.19 to 1.42 | 1.24 to 1.36 |

So the estimator ratio separates "multiplier only" from the other two with about 10,000 observed infectors at 30% detection, and separates events from scenes at full detection with about 3,000 (the intervals still touch at 1,000), but **at 30% detection events and scenes are indistinguishable on this statistic**; the cluster fingerprints (one-venue-day share, household share, venues) are what remain, and their robustness under realistic tracing is untested (note 61). A caution for real data: pooling infectors from different settings itself inflates the ratio (a mixture of negative binomials), so the ratio would need to be computed within settings.

## 6. Predictions scored (mine, note 58)

Met: (a) home share (28.2 and 20.1 points below world 1), (b) at least 7 venues and at most 25% in one venue-day (9.2 and 14.7%; 9.4 and 14.5%), (c) ratio at most 1.1 in world 1 and at least 1.3 in the scene worlds (1.06; 1.50, 1.42), (d) zero share within 4 points of the negative binomial (-1.3, -1.1), (e) repeat correlation at least 0.05 in 2a and at most 0.02 in world 1 (0.071, -0.012; the 90% interval of 2a, 0.043 to 0.099, spans 0.05), (f) occupational profile (pupils 0.0% in the scene worlds is by construction and was labelled as such).
Not tested as registered: R11-2 (the counterfactual was dropped; the decomposition replaces it).
Wrong, mine: note 58 premise that events cannot be matched on the likelihood estimator.
Points worth keeping from the runner's round: the moment k orders the arms differently from the likelihood k (world 3b is the most dispersed on the moment scale, 0.152, and the least dispersed of the four matched worlds on the likelihood scale, 0.330), so any statement of what a mechanism can reach must name the estimator.

## 7. Publication

With three families matched, the title that fits the evidence is the one about identical dispersion arising from different worlds:

1. "Same dispersion, different worlds: what an agent-based city says about the causes of superspreading" (recommended)
2. "Three routes to the same overdispersion: variation in infectiousness, risky places and rare events in an agent-based city"
3. "One k, three worlds: what the offspring distribution can and cannot tell us about the causes of superspreading"

The paper's claim becomes: crowding and mobility cannot produce superspreading; variation in infectiousness, risky venues acting on a minority, and closed-group events each can, at parameter values that need justification; and matched on the like-for-like estimator they leave different fingerprints that cluster investigations can read, while the offspring distribution alone cannot tell them apart.
