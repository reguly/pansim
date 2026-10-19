# ACT-049 note 58: instructions for round 11 (matched on the like-for-like estimator)

19 October 2026. Reply to `56_round10_results.md` (read in note 57, which also corrects my reading of round 9). Results go to Drive with prefix `59_`, main file `59_round11_results.md`, with a review of this note and the registered predictions first (`59a_review_of_note58.md`). Reporting rules as before, with one change: **the likelihood k is now the primary estimator** (published k are negative-binomial likelihood fits), with the moment k beside it, and the observed zero share and observed 80% share (not the negative-binomial projections to mean 1.4) are the shares to compare with the real pattern (zero share about 59%, 80% share about 19% to 20% at k = 0.3, at the same mean). 12 replicates, same seeds, day 28 within 3% of 6,211.25, no edits of the location and agent files, failed predictions reported as failed.

## Why

Round 10 matched three worlds on moment k and showed they differ in place, cluster composition, repeat infections and the gap between the two estimators. On the likelihood estimator the round-9 gate cell (shape 1) sits at 0.51 with an observed zero share of 47.8%, so it did not reach the real pattern; the R10-4 cell (strongest scene, shape 0.5) did (likelihood k 0.284, zero share 56.9%, 80% share 17.9%). The comparison has to be redone with the worlds matched on the likelihood k, otherwise the "same k" claim is not like-for-like.

## R11-1 (main): worlds matched on likelihood k of about 0.35

Tune each world's multiplier shape (one parameter, interpolating on the log of likelihood k; the interval of a likelihood k near 0.35 with 12 replicates is about plus or minus 3%, so aim for within 10%):

1. **World 1, multiplier only.** The round-10 arm (shape 0.32, likelihood k 0.357) as it is.
2. **World 2a, strongest scene.** S8-2 tau 1 lambda 30 with the shape tuned. Starting value 0.73 (log interpolation between shape 1, likelihood 0.435, and shape 0.5, likelihood 0.284).
3. **World 2b, moderate scene.** S8-2 tau 1 lambda 10 with the shape tuned. Starting value 0.46 (extrapolation from shapes 1, 2, 3 at 0.51, 0.70, 0.81; expect more tuning rounds; if it needs a shape below 0.3 report that, since then the scene adds little).
4. **World 3, events.** Report the lowest likelihood k reached by the closed-group events at any rate and group size you have run (round 6 gave 1.8, round 10 gave 1.2 at rate 0.034); do not run new tuning unless one arm is cheap, and say it cannot be matched.

For each world report: both k, observed zero share, observed 80% share, the NB zero and 80% shares at the likelihood k and own mean, and the round-10 discriminators: home share, share at the four high-L types, household attack rate, largest offspring and percentiles, the ten largest clusters (distinct venues, share in one venue-day), the top 1% of infectors by age and agent type with the number of infectors in the top 1% (so that sampling error can be judged), the ratio of likelihood to moment k, and the repeat-infection correlation (16 weeks, 8 replicates, if time allows; drop first).

**Registered predictions** (all at matched likelihood k):
(a) World 2a has a home share at least 10 points below world 1 (34.2% in round 10).
(b) The ten largest clusters of world 2a have at least 7 distinct venues and at most 25% of their infections in one venue-day (8.8 and 15.5% in round 10).
(c) Likelihood k over moment k is at most 1.1 in world 1 and at least 1.3 in worlds 2a and 2b (1.06 in world 1; the R10-4 cell gave 1.49).
(d) The observed zero share of worlds 2a and 2b at likelihood k 0.35 is within 4 points of the negative binomial at the same k and mean (it was within 1 to 2 points for the gate cell on the likelihood fit: 47.8% against 49.2%).
(e) Repeat-infection correlation at least 0.05 in world 2a and at most 0.02 in world 1.
(f) The occupational profile of world 1 (elementary-school children over-represented in the top 1%, stay-at-home adults under-represented) persists at the new shape, and the share of pupils in the top 1% of world 2a stays at 0% (the latter by construction; state this).

## R11-2: is the repeat-infection fingerprint the persistent class?

Redraw the class membership for each infection (the class flag and its venue tilt resampled each time an agent is infected, keeping the population share) in the world-2a arm; if that needs more than a flag, drop it and say so. **Registered prediction:** repeat-infection correlation falls to at most 0.03, from the persistent arm's value; if it does not fall, the correlation comes from something other than class membership (for example household or location persistence) and the interpretation in note 57 is wrong.

## R11-3: cheap, no new runs

From existing traces of the round-10 worlds, tabulate for the ten largest clusters of each replicate the share of offspring in the same household, in the same venue type, and the age range of the infectees, so that cluster composition can be described in terms a contact-tracing study uses.

## Order and budget

R11-1 world 2a first (tuning), then world 1 statistics (already run), then world 2b, then R11-3. R11-2 and the repeat-infection runs last. If the total exceeds about three hours, drop the repeat-infection runs and R11-2 and say so.
