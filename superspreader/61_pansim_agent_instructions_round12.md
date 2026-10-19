# ACT-049 note 61: instructions for round 12 (a short confirmatory round, then we write)

19 October 2026. Reply to `59_round11_results.md` (read in note 60). Results go to Drive with prefix `62_`, main file `62_round12_results.md`, with a short review of this note first (`62a_review_of_note61.md`). Reporting rules unchanged: likelihood k primary and moment k beside it, observed zero and 80% shares (not projections), 12 replicates, day 28 within 3% of 6,211.25, failed predictions reported as failed, no edits of the location and agent files. This round is meant to be the last mechanism round; the aim is to protect the claims the paper will make, not to open new questions.

## R12-1: world 3b on the common seeds, and what the event rate means

1. Rerun world 3b (group 30, rate 0.1456, factor 3000, duration 2 h) on seeds 77001 to 77012 with the same coefficient calibration to day 28, so that worlds 1, 2a, 2b and 3b are paired. **Prediction:** likelihood k within 10% of 0.330 and the observed zero share within 2 points of 52.3%; if not, the round-6 arm was a lucky seed set and the match is weaker than reported.
2. Report what the event rate is in real-world terms for that arm: events per day, mean and maximum attendees, the share of agents attending any closed group on a given day and in a given week, the share of all infections and of all offspring that happen inside events, and the share of events with an infectious attendee. The round-11 note says 14.6% of agents attend a group every day; the file (`events_total` 83,086 over 12 replicates) implies at most about 4% of agents a day, so one of these is wrong. Say which, and what the event parameters mean physically (who is invited, how groups form).

## R12-2: do the fingerprints survive under-detection?

For worlds 1, 2b and 3b (the paired arms of R12-1), thin the infection traces and recompute on the detected cases:

1. Random detection of infections at 60% and 30%, independent per infection (my histogram-level calculation says the moment k is unchanged and the likelihood k falls: ratio of likelihood to moment k 1.06, 1.24 and 1.30 for worlds 1, 2b and 3b at 30%; see `60_thinning_fingerprints.csv`).
2. Detection clustered by household: all members of a household are detected together or not at all, at 60% and 30% of households (the more realistic case for a contact-tracing study).
3. For each: both k, the ratio, observed zero share minus the negative binomial at the same likelihood k and mean, and, on the largest detected clusters (top 10 per replicate): same-household share, share in one venue-day, number of distinct venues, modal venue-type share.

**Registered predictions.** (a) With random detection, the one-venue-day share and the number of distinct venues of the top clusters change by less than 5 points and 1 venue respectively in every world (these are properties of what happens inside a cluster, so independent thinning should not move them); (b) with household-clustered detection, the same-household share of detected infectees falls in worlds 1 and 3b and the ratio of likelihood to moment k is at least 0.1 lower than under random detection of the same overall rate (because whole households vanish); (c) at 30% detection the ratio no longer separates world 2b from world 3b (1.24 against 1.30 in my calculation) but the one-venue-day share still does (at least 60 points apart); (d) world 1 stays at a ratio below 1.15 in every detection scheme.

## Order and budget

R12-1 item 1 first (it is needed for R12-2), then item 2 (no runs), then R12-2. Three to four runs plus trace processing; about 1.5 hours. If R12-2 item 2 (household clustering) is awkward, do random detection and say so.

## After round 12

Unless it shows that the matched-world conclusions fail, no further simulation rounds are planned. The deliverable becomes the publication.
