# ACT-049 note 43a: review of note 42 before running

16 October 2026. Written before any round-6 run. Results will be in `43_round6_results.md`. Nothing in `locations1.json`, `agents2.json`, `locations3.json` or `agents4.json` will be edited.

## Errors and problems found

1. **R6-1 prediction 1 is already contradicted for the "none" shape.** Round 5 (note 38, section 3) has the matched no-event baseline at 0.297 non-transmitters and the capacity-100, factor-1,091 arm at 0.339, a change of 0.042. The prediction needs less than 0.03. Factor 600 is 0.326 (change 0.029). The grid will still be run and scored, but for the "none" row at factor 1,091 the outcome is known: failed. Events do raise the zero share a little, by 3 to 4 points at k near 0.3. That also qualifies the statement in note 41, 4.1, that events "do not raise the share of non-transmitters".
2. **R6-1 prediction 3 is met by the existing E cell.** E (shape 0.3, factor 0) has moment k 0.297 and a zero share of 0.585 against 0.586 from the likelihood fit, and a = 0.3 is at most 0.5. So the "at least one cell" clause holds before any run. What carries information is the clause "every such cell has a at most 0.5" and the events share in the qualifying cells with factor above 0. I will report the events share for every qualifying cell, and say which have factor 0.
3. **"0.5 or narrower" is ambiguous.** A smaller gamma shape is a wider multiplier distribution (CV squared is 1/a). I use the parenthetical, a at most 0.5, and read "narrower" as "smaller shape".
4. **R6-1 reuse of E.** The E cell on the new map (`r3cal/r35_E`) has day-28 mean 6,124, which is 1.4% below 6,211. It is inside 3% and is reused. The none by factor-0 cell is the R3-6 baseline (6,211.25), reused.
5. **Different matching targets.** R6-1 and R6-6 match to 6,211, R6-4 to 6,000. The E arm of R6-4 is therefore a new calibration, not the E of R6-1. I will keep both and label them.
6. **R6-4 prediction (i) compares across maps and matching.** The PS1 values (P25 0.471 and so on) are from the old map (`agents1.json`, `locations0.json`), matched on early R near 1.39. R6-4 is on the new map, matched on day-28 infections. A departure of more than 15% would not by itself show an error in either set. I will report it as a combined map-and-matching difference.
7. **R6-3 uses old-map runs.** Traits are stored for P0, P25, P50, P100, P25k and P100ln in `results/ps/ps1/<arm>/rep1101` through `rep1112` as `agents_trait.csv`, so no re-run is needed. The observed early k in prediction (ii) is therefore the PS1 old-map value, and the 4.66 in the formula is the PS1 A0 value on the same map (the new map's A0 is 4.59).
8. **R6-2 prediction (ii) may fail for structural reasons.** Agents have fixed home size, school, work and schedule, so a no-multiplier arm can carry a positive repeat correlation of offspring. E is within plus or minus 0.05 of zero only if that structural part is small. I propose adding **A0 (no multiplier, no trait) as a control arm**. It is the same cost per replicate and separates the structural correlation from the trait. This is an addition, not a change.
9. **R6-2 prediction (iii) follows from (i).** With r at least 0.2, the Fisher-z bound is about 195 pairs, so (iii) holds whenever (i) does. Not an error. I will report the number for the observed P0 correlation.
10. **R6-5 ward sizes.** `build_wards.py` leaves a location whole when it has 40 or fewer assigned agents (1.33 times the target of 30). For targets 10, 100 and 300 I scale the same rule, leaving a location whole at or below 4/3 of the target, and round the ward count as before. At 300 most health centres and nursing homes stay whole, so only the large hospitals are split. The achieved ward-size distribution will be in the output. The unsplit arm is the V4 map recalibrated to mean 0.345, because V4's own mean is 0.397.
11. **R6-5 prediction (i) depends on the recalibration.** V4's longest chain of 585 was at mean 0.397. At mean 0.345 an unsplit hospital map may have a much shorter longest chain, so the "below 0.05 unsplit" clause is not guaranteed by the earlier result. I will report whichever it is.

## Definitions I will use (all as in note 38 unless stated)

- Trace day is `timestamp // 144`. Index cases are infected on days 1 to 10 with a known infector. Offspring are infections caused on or before day + 14. Initial `-r` seeds are excluded.
- "Share of offspring infected at events" is the sum over index cases of offspring infected at an event location on an event day, divided by the sum of their offspring (pooled over replicates). Round 5 also reported it among index cases with any event offspring; both are given.
- Moment k is the pooled method of moments with variance divided by n minus 1. Likelihood k is the maximum-likelihood negative-binomial k with the mean fixed at the sample mean. Zero shares are given for the data and for the negative binomial at each estimator.
- 90% intervals are replicate bootstraps (1,000 draws, 5th and 95th percentiles).

## Proposed additions

- R6-2: control arm A0.
- R6-2: the trace change writes one row per infection episode to a new file; the existing trace is unchanged, so earlier outputs stay valid.

## Reinfection in the model (R6-2, first request)

An agent who recovers moves from R to S after 21 days on average (maximum 42). Immunity after infection is the prior-infection term in `include/immunization.h` (case 1): the hazard multiplier is one minus the protection against infection. For the same variant the protection starts at 0.95 and falls by the waning rate of 0.003 per week, so the multiplier is 0.05 just after recovery and grows about 0.003 per week of age. The model has one variant. There is no antigenic drift. Vaccination also starts on day 96 by default (`--immunizationStart`), which adds protection after that day and affects every 16-week arm in R6-4 over its last 16 days alike. For R6-2 I will switch it off (`--immunizationStart` beyond the horizon) so that reinfection is governed by the infection-acquired term only, and I will say so in the results. In earlier runs, 1,801 of about 98,800 infected agents (1.8%) were infected twice by day 112 in A0, and 377 of 53,000 by day 70 in E on the old map. The horizon needed for 2,000 pairs is measured in R6-2, not assumed.
