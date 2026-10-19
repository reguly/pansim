# ACT-049 note 56a: review of note 55 before the round-10 arms

18 October 2026. Written before any round-10 infection arm. Results will be in `56_round10_results.md`. The location and agent files are not edited.

## What is already prepared

1. R10-2 needs a code change, now made and building (`build_r10`): a per-agent mean for the per-episode multiplier. Options `--sheddingClassMean` and `--sheddingOthersMean`; the gamma draw keeps its shape and is multiplied by the agent's mean. Off by default, so with the options off nothing changes (I will repeat the byte-identity check on the new binary).
2. R10-3 needs no code: household transmission is suppressed by a copy of the location file with the infectiousness of the home type set to zero (movement is unchanged).

## Points on note 55

1. The tuning in R10-1 world 1 is limited by the noise of k itself. The 90% interval of a moment k near 0.35 with 12 replicates is about plus or minus 10% (round 9: 0.349, 0.313 to 0.385), so "within 5% of world 2" cannot be guaranteed by one run. I will tune the shape by interpolation on the log of k, report the closest of the arms run with its interval, and say if the interval of world 1 and of world 2 overlap rather than claim an exact match.
2. World 3 (events): the setting with the lowest likelihood k in round 6 (group 30, rate 0.1456) has moment k 0.152, below 0.35. Round 6 shows moment k falls as the rate rises, so a lower rate should reach 0.35; I will tune the rate for that and say if it cannot.
3. Household secondary attack rate: the trace has no household table, so I use the agents file to find household members, and take every other member of the index case's household as susceptible. This overstates the denominator a little late in the epidemic and not at all at the start.
4. R10-3 baseline: the nominal prediction uses the baseline factor 1 + 1/4.59, but with household transmission removed the baseline dispersion itself changes. I will add one control arm (no multiplier, same suppression) so the ratio of observed to predicted k can be read both with the nominal baseline and with the new one.
5. R10-2: the note gives others a mean of 0.974. With the class at 4.35% of all agents the population mean is 0.997, not 1. I use the values as given and report the realised means by group.
6. R10-4 uses S8-2 tau 1 lambda 30 (no code change), not S8-3, so the round-8 quirk is not touched.
7. Time: tuning arms are about 10 minutes each. I expect about 3 hours in total with the repeat-infection runs, which is the item I will drop first, as the note says, if the budget is exceeded.
