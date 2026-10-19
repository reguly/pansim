#!/usr/bin/env python3
"""Write 47_round7_results.md from the CSVs in superspreader/ (tables) plus the fixed prose below."""
import csv
import json
from pathlib import Path

from report_tables import OUT, ci, fmt, num, pct, rows, table

STATE = Path(__file__).resolve().parent / "results" / "round7" / "state"


def pick(name, key, value):
    return next(r for r in rows(name) if r[key] == value)


def shape_table(data, extra=()):
    head = ["arm", "day 28 vs 6,211", "early R", "k moment", "k likelihood", "zero", "NB zero (moment)", "NB zero (likelihood)", "1 to 5", "above 5",
            "at least 20", "max", "causing 80%", "causing 50%", "top 1%", "top 5%"] + [h for h, _ in extra]
    body = []
    for r in data:
        body.append([r["cell"], pct({"v": r["day28_vs_6211.25"]}, "v"), ci(r, "early_R"), ci(r, "k_mom"), ci(r, "k_ml"), pct(r, "share_0"),
                     pct(r, "nb_mom_share_0"), pct(r, "nb_ml_share_0"), pct(r, "share_1_to_5"), pct(r, "share_above_5"),
                     pct(r, "share_at_least_20"), fmt(num(r, "maximum")), pct(r, "share_of_index_cases_causing_80pct"),
                     pct(r, "share_of_index_cases_causing_50pct"), pct(r, "top_1pct_share_of_offspring"), pct(r, "top_5pct_share_of_offspring")]
                    + [f(r) for _, f in extra])
    return table(head, body)


def main():
    s1 = rows("47_s1_summary.csv")
    s2 = rows("47_s2_summary.csv")
    s3 = rows("47_s3_summary.csv")
    s4 = rows("47_s4_summary.csv")
    s5 = rows("47_s5_summary.csv")
    s6 = rows("47_s6_summary.csv")
    t34 = rows("47_t3_t4_s1.csv")
    t5 = rows("47_t5_slopes.csv")[0]
    dec = rows("47_t5_deciles.csv")
    t6 = rows("47_t6_levers.csv")
    pairs = rows("47_s5_pairs.csv")[0]
    out = []
    w = out.append

    w("# ACT-049 note 47: round 7, high-velocity individuals (HVIs) in PanSim\n")
    w("18 October 2026. Reply to note 46. Review before running: `47a_review_of_note46.md`. All numbers below come from the CSVs listed at the end; the code is in `superspreader/study/` (`run_round7.py`, `analyze_round7.py`, `report_round7.py`, `build_hvi_agents.py`, `r70_*.py`) and the movement-policy changes are in `include/policies/movementPolicies.h` (uncommitted, as the other working-tree changes). Nothing in `locations1.json`, `agents2.json`, `locations3.json` or `agents4.json` was edited; the S3 agents files are new (`inputs/r7_agents_rep3.json`, `r7_agents_rep10.json`).\n")

    w("## Headline\n")
    w("1. **Mobility heterogeneity, as an HVI multiplier on discretionary hours, hardly changes the shape of the offspring distribution.** Every S1 to S6 arm has a moment k between 3.2 and 5.0 (round-6 baseline 4.59), zero share 28.9% to 31.0% (both negative binomials predict the observed zero share within 1 point), and 40% to 43% of infected people causing 80% of infections, against the real pattern of about 20%. The abstract trait of rounds 5 and 6 reached k near 0.3; mobility does not.")
    w("2. **Why.** (a) The time budget saturates: a mean-1 multiplier cannot be realised as hours, so at gamma shape 0.3 the realised CV^2 of discretionary hours is 1.21 against 3.35 uncapped (T3), and the realised hours rise with the multiplier with slope 0.20 over the whole range (1.03 below m = 2). (b) Only part of transmission is discretionary: from the trace, an index case's offspring rise with the multiplier decile with log-log slope 0.075, not 0.5 to 1 (T5). (c) A class that holds 13.1% of discretionary hours (S2, f = 5%, F = 3) causes 7.6% of infections: it causes about 60% of its hours share, in every S2 cell.")
    w("3. **Predictions.** Met: S1 (i), (ii), (iv); S2 (ii); S3 (kernel invariance, weakly on the distinct-venue part); S4 (R and k); S5 (no selection, pair correlation below 0.544); S6 (a) and (b). Failed: S1 (iii), T5, S2 (i) and (iii), S4 (venue-type shares), S5 (uncoupled k ratio), T6 (visits lever). Section 3 lists each with the number.")
    w("4. **Control (S6).** Capping the 5% most active agents removes 1.7 infections per 1,000 discretionary hours removed in the S2 cell against 1.4 for the same hours removed from everybody (ratio 1.26), and 1.62 against 1.42 (ratio 1.14) in the S1 shape-0.3 arm. Concentrating the cut on the most active is worth 14% to 26% more per hour removed, not more. Closing the venue types that hold most class hours removes the most per hour (1.85 and 1.81), but removes 10.8% and 12.6% of hours, not the 7.45% and 8.4% of the cap (deviation D8).\n")

    w("## 1. Deviations from note 46, and errors in it (first)\n")
    w("Departures are numbered D1 to D9; items E1 to E5 are errors or unsupported assumptions in note 46 (E1 to E3 and the others in `47a`).\n")
    w("- **D1. The hours lever is a chance lever, not a duration lever.** The first implementation scaled the duration of each discretionary stay. Its elasticity was 0.3 (T4 slope 0.18 at shape 3, 0.04 at shape 0.3 over the whole range) because a window is a renewal process: a longer stay uses up the window and the agent redraws less often. Realised CV^2 of hours at shape 0.3 was 0.20 against 3.35 uncapped. I archived those runs (`results/round7_duration_lever/`, table `47_t3_t4_duration_lever_s1.csv`) and replaced the lever with a per-agent change of the event chances inside each window: the discretionary chances are scaled by g against the home event, capped where the home chance reaches 0 (saturation near 2.9 times baseline hours). All S arms use the chance lever. Durations are unchanged.")
    w("- **D2. Classification by role, not by physical venue type.** `agents2.json` workplaces are venues of any physical type (only about 7.5% of type-6 workplaces are type 4), so a worker at work in a shop would be counted as discretionary shop time by a physical-type rule. The mobility log and the lever classify each stay by the agent's role (home, school, work, discretionary, institutional) using the closure flag, and report physical groups separately. Mandatory time is never scaled.")
    w("- **D3. Mean hours preserved by separate weekday and weekend scales per agent type** (`--hviScaleByType`, `--hviScaleByTypeWeekend`), calibrated on movement-only runs (`-k 0`, 2 weeks). A single scale per type left up to 14% deviation between weekday and weekend. Realised deviations from baseline by agent type, weekday and weekend, at the accepted iteration: at most 1.8%, 0.8%, 0.7%, 1.8%, 1.9% for shapes 3, 1, 0.5, 0.3, 0.15 (T3 table). The S2 cells use the same procedure (`results/round7/state/scale_*.json`). Visit counts are not preserved: they fall by up to 3.3%, 7.2%, 10.0%, 12.6%, 14.9% (type 6 weekdays) because HVIs take longer stays near the cap.")
    w("- **D4. Eligibility** is age 15 and over and agent types 4 to 8 (157,029 agents). Multiplier applies in W and N, not in M and S (`--hviStates`, default W and N). The hvi dump (`hvi.csv`) holds the multiplier times the calibrated per-type scale; every statistic below that selects on the multiplier (mean multiplier of index cases, T5) uses the unscaled draw, and I corrected the first version of the S1 and S5 tables for this (see S1 (iii)). Where the multiplier is quoted for the S2 class it is the nominal factor F.")
    w("- **D5. Type-mix lever not implemented** (E2: L is 1 for every venue type except public space and the commuter box, so there is nothing to shift).")
    w("- **D6. Visits lever.** V - 1 forced consecutive visits to other venues of the same type (per-agent repeat counter). The first version returned to the same venue and lost slack (visits +51% and +155%, class hours -9% and -7%). The fix (`build_r7b`) gives T6: class visits +77% (V = 2) and +236% (V = 4) with hours -8.8% and -6.7%. Not at ×V and not within 2%; S4 therefore tests visits at roughly ×1.8 and ×3.4 with 7% to 9% fewer class hours.")
    w("- **D7. Repertoire lever** uses new agents files with the nearest N venues by home distance for a fixed HVI class (`--hviSeed 424242`, the same assignment in every replicate; the other arms draw the class per replicate from the run seed). S3 arms at fixed hours: class hours exactly equal, visits +4% and +6% at ×3 and ×10. The distinct venues per week rise +61% and +99%, not ×3 and ×10, because a class member makes only 6 discretionary visits a day.")
    w("- **D8. S6.** Three interventions from day 21 (`--hviControlMode capTop` with parameter 0.05; `scaleAll` with the parameter found by secant to match the cap's removal within 3%; closure with the existing closure rules). The hours removed are estimated on a 5-week movement-only run (post day 21, `-k 0`), then multiplied to the 12-week run (63 days of control), not measured in the infection runs. The scaleAll hours match the cap within 3% (7.31% against 7.45%; 8.56% against 8.36%). Closure comes in coarse steps (closing one physical type, then two, then three), so I took the step nearest to the cap: closing type 6 removes 10.8% of hours in the cell, type 5 removes 12.6% in the shape arm. Per-hour figures are reported to account for that, but closure is not at equal reduction. Closing a physical type also closes the workplaces of that type, and the hours removed are role-based discretionary hours only.")
    w("- **D9. Binaries and code state.** `build_r7` for T1 to T5, S1, S2, S3, S5 (including the pairs); `build_r7b` (visits-lever fix) for T6 v2 and v4, S4 v2 and v4, and S6. S4 v1 is the S2 cell itself (`build_r7`), and S4 v2 and v4 use its seeds. The no-HVI path is identical in the two builds by construction; I did not rerun S2 on `build_r7b`. All code is uncommitted (nothing committed or pushed). S3 and S4 arms were run at the S2 cell's matched coefficient (0.00041), not recalibrated, so day 28 is outside 3% for the three S3 repertoire arms (-4.4%, -5.8%, -4.5% from 6,211.25) and, by 0.05 points, for S4 v4 (-3.05%; v1 -2.0%, v2 -2.2%). Early R is 1.41 to 1.43 in all of them, so I did not recalibrate. All other arms are within 3%.")
    w("- **E1 (note 46, section 2 item 5, and the baseline file).** Durations are hh.mm: 0.3 is 30 minutes and 1.3 is 90 minutes, so the baseline file understates hours at types 1 and 7 (and 9). Measured baselines are in `47_r70_baseline_mobility.csv` (adults about 4.2 role-discretionary hours on weekdays, not 2.7).")
    w("- **E2.** L is 1 for all place types except public space (type 1, L = 0, 4,103 places) and type 15. Public space holds no transmission at all (`infections_share_public_space` is 0 in every arm). This also kills the premise of the occupational cell: a workplace has L = 1 too, so moving a worker's 8 hours from a workplace to 10 shops and restaurants does not raise L-weighted hours (S2).")
    w("- **E3.** The window is a renewal process and gaps are filled (stay, public space, home), so hours are not proportional to a duration multiplier and the multiplier is not a hours multiplier (T4). The chance lever is bounded: realised hours saturate near 2.9 times baseline.")
    w("- **E4. The thresholds of S1 (i) and (ii) cannot discriminate.** They were set with the real k near 0.3 in mind, but the round-6 baseline model already has moment k = 4.59, so any arm meets them and they do not test the hypothesis. The test that matters, whether k approaches 0.3, fails: no arm is below 3.2.")
    w("- **E5. S2 (i)** (class share of infections caused within 30% of its share of discretionary hours) ignores household, school and work transmission, which are not scaled, so it fails by construction. The right comparison is with the share of the class's infectious hours that are discretionary.\n")

    # R7-0, T1, T2
    w("## 2. Verification tests and R7-0\n")
    w("**R7-0** (files `47_r70_repertoire.csv`, `47_r70_location_L.csv`, `47_r70_baseline_mobility.csv`, `47_r70_state_hours.csv`; details in `47a`): window sums, W/N/M/S, repertoire by type, L by type, measured baseline and the 10-minute time step are as listed in `47a` items 1 to 8. Infectious time by state, from `47_r70_state_hours.csv` (agent-hours while infectious, all agent types): W 74.4%, N 11.3%, M 11.7%, S 2.6%. The main arms apply m in W and N, hence in 85.7% of infectious time.\n")
    w("**T1 passed.** With every new option off, a 12-week run on the new binary gives a daily table and an infection trace byte-identical (`cmp`) to the previous binary (84 days; trace of 79,317 lines).\n")
    w("**T2 passed.** The multiplier vector is the same for the same seed under different flags and different for another seed (`cmp` on the dumps); constant over time (single draw at start). Mean over the 157,029 eligible agents and CV^2 against 1/a: shape 3: mean 0.99999, CV^2 0.3338 (+0.1%); shape 1: 1.0066 (+0.7%); shape 0.5: 2.0056 (+0.3%); shape 0.3: 3.3478 (+0.4%); shape 0.15: 6.6927 (+0.4%).\n")

    w("### T3 and T4 (chance lever, S1 arms, `47_t3_t4_s1.csv`)\n")
    head = ["shape", "max hours deviation by type and day type", "lowest visits deviation (type 6 weekday)", "p50 / p90 / p99 / p99.9 daily hours", "CV^2 uncapped", "CV^2 realised (relative hours)", "T4 slope, all", "R^2", "T4 slope, m up to 2", "Spearman, week 1 vs week 2"]
    body = []
    for r in t34:
        hd = max(abs(float(v)) for k, v in r.items() if k.startswith("hours_") and "baseline" in k)
        body.append([r["arm"].replace("s1_a", ""), pct({"v": hd}, "v"), pct({"v": r["visits_wd_vs_baseline_type6"]}, "v"),
                     " / ".join(fmt(float(r[f"p{q}_hours_wd_per_day"]), 3) for q in ("50", "90", "99", "99.9")), fmt(float(r["cv2_unscaled"])),
                     fmt(float(r["realised_cv2_relative_hours_wd"])), fmt(float(r["t4_slope_all"])), fmt(float(r["t4_r2_all"])), fmt(float(r["t4_slope_m_le_2"])),
                     fmt(float(r["persistence_spearman_week1_week2"]))])
    w(table(head, body) + "\n")
    w("T3 hours within 2%: **passed** (all arms at most 1.9%). T3 visits within 2%: **failed** (lowest column). Persistence (rank correlation of weekly activity between two weeks) is 0.86 to 0.96: the multiplier is a persistent trait in behaviour. The waking-day cap binds in the following sense: at shape 0.3, 35% of agents realise less than half of their multiplier, and the 99.9th percentile of weekday hours is 15.5 h (of 24, with fixed mandatory hours). T4 slope 0.97 (R^2 0.86) at shape 3 and 0.20 (R^2 0.45) at shape 0.3 over the whole range; below m = 2 the slope is 1.02 to 1.06 in every arm.\n")

    w("## 3. Predictions scored\n")
    w("| Test | Prediction | Result | Verdict |\n|---|---|---|---|")
    a03 = pick("47_s1_summary.csv", "cell", "s1_a0.3")
    a015 = pick("47_s1_summary.csv", "cell", "s1_a0.15")
    min_k = min(float(r["k_mom"]) for r in s1)
    min80 = min(float(r["share_of_index_cases_causing_80pct"]) for r in s1)
    w(f"| S1 (i) | moment k at least 0.44 at shape 0.3, at least 0.34 at 0.15 | {fmt(num(a03, 'k_mom'), 3)} and {fmt(num(a015, 'k_mom'), 3)} | met (E4) |")
    w(f"| S1 (ii) | no arm with moment k below 0.3 or share causing 80% below 0.25 | minimum k {fmt(min_k, 3)}, minimum share {100 * min80:.1f}% | met; **S2 to S6 were run** |")
    w(f"| S1 (iii) | mean m of index cases above 1.5 at shape 0.3 | {fmt(num(a03, 'mean_m_index_cases'), 3)} ({fmt(num(a03, 'mean_m_index_cases_low'), 3)} to {fmt(num(a03, 'mean_m_index_cases_high'), 3)}); {fmt(num(a03, 'mean_m_index_cases_eligible'), 3)} over eligible index cases only | **failed** (1.45 at shape 0.15) |")
    w("| S1 (iv) | realised variance of hours at least 20% below 1/a at shapes 0.3 and 0.15 | 1.21 against 3.35 (-64%) and 1.48 against 6.69 (-78%) | met |")
    w(f"| T5 | both log-log slopes between 0.5 and 1.0 | received {fmt(num(t5, 'slope_received_vs_m'))} ({fmt(num(t5, 'slope_received_low'))} to {fmt(num(t5, 'slope_received_high'))}); offspring {fmt(num(t5, 'slope_offspring_vs_m'))} ({fmt(num(t5, 'slope_offspring_low'))} to {fmt(num(t5, 'slope_offspring_high'))}) | **failed** (both far below 0.5) |")
    w("| T6 | visits and repertoire levers act as intended, hours within 2% | repertoire: hours +0.0%, distinct venues per week +61% and +99%; visits lever: visits ×1.77 and ×3.36, hours -8.8% and -6.7% | repertoire met; visits **failed** |")
    # S2 verdicts
    ratios = []
    for r in s2:
        if r["class_share_of_discretionary_hours"]:
            ratios.append(float(r["class_share_of_infections_caused"]) / float(r["class_share_of_discretionary_hours"]))
    rot = pick("47_s2_summary.csv", "cell", "s2_rotate1")
    kmin_nonrot = min(float(r["k_mom"]) for r in s2 if r["cell"] != "s2_rotate1")
    w(f"| S2 (i) | class share of infections caused within 30% of its share of discretionary hours | ratio {min(ratios):.2f} to {max(ratios):.2f} over the 12 cells | **failed** (E5) |")
    w(f"| S2 (ii) | no non-occupational cell with moment k below 0.6 | minimum {fmt(kmin_nonrot, 3)} | met |")
    w(f"| S2 (iii) | the occupational cell has a lower k than every other cell | {fmt(num(rot, 'k_mom'), 3)}, the highest of the 13 | **failed** (E2) |")
    k3 = [float(r["k_mom"]) for r in s3]
    r3 = [float(r["early_R"]) for r in s3]
    d3 = [float(r["class_mean_distinct_venues_of_offspring"]) for r in s3]
    sp3 = [float(r["class_mean_home_distance_m"]) for r in s3]
    w(f"| S3 | early R and k change by less than 10%; distinct venues of offspring rise | R {fmt(r3[0])}, {fmt(r3[1])}, {fmt(r3[2])}; k {fmt(k3[0])}, {fmt(k3[1])}, {fmt(k3[2])} (largest change {100 * max(abs(x / k3[0] - 1) for x in k3[1:]):.1f}%); distinct venues {fmt(d3[0], 4)}, {fmt(d3[1], 4)}, {fmt(d3[2], 4)}; mean distance {sp3[0]:.0f}, {sp3[1]:.0f}, {sp3[2]:.0f} m | met for R and k; distinct venues rise by 3% only; distance rises at ×10 only |")
    k4 = [float(r["k_mom"]) for r in s4]
    r4 = [float(r["early_R"]) for r in s4]
    w(f"| S4 | early R and k change by less than 10%; HVI infections by venue type unchanged within 10% | R {fmt(r4[0])}, {fmt(r4[1])}, {fmt(r4[2])}; k {fmt(k4[0])}, {fmt(k4[1])}, {fmt(k4[2])}; type shares: restaurant 5%, large venue 6%, shop short 18%, shop long 15%, recreation 12%, health centre 18% largest deviations | R and k met; venue types **failed** (7% to 9% fewer class hours, D6; 5,400 to 5,700 class offspring, so shares carry about 4% to 10% relative noise) |")
    w(f"| S5 (a) | uncoupled k at most 0.7 times coupled at each shape | ratio {fmt(float(s5[0]['k_mom_ratio_to_coupled']))} (shape 0.5), {fmt(float(s5[1]['k_mom_ratio_to_coupled']))} (shape 0.3) | **failed** |")
    w(f"| S5 (b) | mean m of index cases of the uncoupled arm within 10% of 1 | {fmt(float(s5[0]['mean_m_index_cases']), 3)}, {fmt(float(s5[1]['mean_m_index_cases']), 3)} | met |")
    w(f"| S5 (c) | Pearson correlation of offspring across infections of one agent positive and below 0.544 | {fmt(num(pairs, 'pearson'), 3)} ({fmt(num(pairs, 'pearson_low'), 3)} to {fmt(num(pairs, 'pearson_high'), 3)}), {pairs['pairs']} pairs, Spearman {fmt(num(pairs, 'spearman'), 3)} | met (barely positive) |")
    c = {(r["base"], r["intervention"]): r for r in s6}
    w(f"| S6 | (a) removes more per hour than (b) in the S2 cell; at most 1.5 times in the S1 shape-0.3 arm | cell {fmt(num(c[('cell', 'capTop')], 'infections_averted_per_1000_hours_removed'), 3)} against {fmt(num(c[('cell', 'scaleAll')], 'infections_averted_per_1000_hours_removed'), 3)} (×{num(c[('cell', 'capTop')], 'infections_averted_per_1000_hours_removed') / num(c[('cell', 'scaleAll')], 'infections_averted_per_1000_hours_removed'):.2f}); shape {fmt(num(c[('shape', 'capTop')], 'infections_averted_per_1000_hours_removed'), 3)} against {fmt(num(c[('shape', 'scaleAll')], 'infections_averted_per_1000_hours_removed'), 3)} (×{num(c[('shape', 'capTop')], 'infections_averted_per_1000_hours_removed') / num(c[('shape', 'scaleAll')], 'infections_averted_per_1000_hours_removed'):.2f}) | met on the point estimates; the cell's 90% intervals overlap (1.56 to 1.89 and 1.08 to 1.66) |")
    w("")

    w("## 4. S1: hours lever, gamma multiplier (12 replicates, 4 weeks, day 28 matched to 6,211.25 within 3%; `47_s1_summary.csv`, `47_s1_offspring.csv`)\n")
    w(shape_table(s1, extra=[("mean m of index cases", lambda r: ci(r, "mean_m_index_cases")), ("home share of infections", lambda r: pct(r, "infections_share_home")),
                             ("coefficient", lambda r: fmt(float(r["background_coefficient"]), 4))]) + "\n")
    w("Share of infections by location type for each arm is in the CSV (`infections_share_*`; the trace carries the physical type only, so work taking place in shops is counted under shops). Round-6 baseline (no HVI): moment k 4.59. The shape of the distribution moves little and in the expected direction: k falls from 4.07 (shape 3) to 3.20 (shape 0.15) and the shape-0.3 arm is not lower than shape 0.5. 80% of infections come from 40% to 42% of index cases in every arm.\n")

    w("## 5. T5: natural coupling (S1 shape 0.3, `47_t5_deciles.csv`, `47_t5_slopes.csv`)\n")
    w(table(["decile of m", "mean m (unscaled)", "infections received per agent by day 28", "index cases", "mean offspring"],
            [[r["decile"], fmt(float(r["mean_m"]), 3), fmt(float(r["infections_received_per_agent_day28"]), 3), r["index_cases"], fmt(float(r["mean_offspring"]), 3)] for r in dec]) + "\n")
    w("Coupling exists but is flat. Received infections rise from 0.0237 to 0.054 per agent across deciles (×2.3 for a multiplier range of ×20,000) and mean offspring from 1.00 to 1.93. The two log-log slopes against the mean multiplier of the decile are 0.093 and 0.075 because the realised hours saturate (T4) and household, school and work transmission is not scaled. Against realised hours, the relation would be much steeper: below m = 2 the slope of realised hours on m is about 1.\n")

    w("## 6. T6: visits and repertoire levers (`47_t6_levers.csv`)\n")
    w("S2 cell (f = 5%, F = 3), 2-week movement-only runs, one seed. `reference` is v1 for visits and rep1 for repertoire.\n")
    body = []
    for r in t6:
        if r["group"] != "class":
            continue
        body.append([r["arm"], r["agents"], fmt(float(r["disc_hours_wd_per_day"]), 4), fmt(float(r["disc_visits_wd_per_day"]), 4), fmt(float(r["distinct_disc_venues_per_day_wd"]), 3),
                     fmt(float(r["distinct_disc_venues_per_week"]), 3), pct({"v": r["hours_wd_vs_reference"]}, "v"), pct({"v": r["visits_wd_vs_reference"]}, "v"),
                     pct({"v": r["distinct_week_vs_reference"]}, "v")])
    w(table(["arm", "class agents", "hours per weekday", "visits per weekday", "distinct venues per day", "distinct venues per week", "hours vs reference", "visits vs reference", "distinct per week vs reference"], body) + "\n")
    w("Class hours per weekday are 10.3 against 3.7 for the others: a ratio of 2.8, short of F = 3 because of the cap. The others' rows are unchanged by the levers (checked in the CSV).\n")

    w("## 7. S2: discrete class (`47_s2_summary.csv`, `47_s2_offspring.csv`)\n")
    head = ["cell", "day 28 vs 6,211", "early R", "k moment", "k likelihood", "zero", "causing 80%", "class share of population", "of discretionary hours", "of infections caused", "of infections received", "of index cases", "caused / hours share", "realised hours ratio class to others"]
    body = []
    for r in s2:
        hs = r["class_share_of_discretionary_hours"]
        ps = float(r["class_share_of_population"])
        body.append([r["cell"], pct({"v": r["day28_vs_6211.25"]}, "v"), ci(r, "early_R"), ci(r, "k_mom"), ci(r, "k_ml"), pct(r, "share_0"), pct(r, "share_of_index_cases_causing_80pct"),
                     f"{100 * ps:.2f}%", f"{100 * float(hs):.1f}%" if hs else "n/a", f"{100 * float(r['class_share_of_infections_caused']):.2f}%", f"{100 * float(r['class_share_of_infections_received']):.2f}%",
                     f"{100 * float(r['class_share_of_index_cases']):.2f}%",
                     f"{float(r['class_share_of_infections_caused']) / float(hs):.2f}" if hs else "n/a",
                     f"{(float(hs) / ps) / ((1 - float(hs)) / (1 - ps)):.2f}" if hs else "n/a"])
    w(table(head, body) + "\n")
    w("Zero shares, negative-binomial zero shares at both k and the other shape measures are in the CSV. In every non-rotating cell the class causes about 60% of its hours share, and receives somewhat less than it causes. Cells with the largest class and factor (f = 20%, F = 3 and 4.5) have the lowest k (3.69 and 3.41) with a realised class to others hours ratio of 4.5 and 5.9, the only place where k is visibly below 4. Calibration needed a per-type scale up to 5.5 for those cells (saturation).\n")
    w("**Occupational cell** (`s2_rotate1`): 1% of full-time workers (agent type 6, 0.42% of agents) replace the 8 hours at their workplace by 1-hour visits to their own venues of types 5, 7 and 8 (about 10.5 venues). It causes 0.416% of infections for 0.419% of agents: no excess. Its L-weighted hours are unchanged because the workplace is an L = 1 venue (E2), and its susceptible fraction at shops is no higher than at work. This cell does not test what note 46 wanted; a test would need rotating visits in venues where the susceptible fraction and L are higher, which does not exist in this model (L is 1 almost everywhere).\n")

    w("## 8. S3: repertoire lever (S2 cell f = 5%, F = 3, fixed class, `47_s3_summary.csv`)\n")
    w(shape_table(s3, extra=[("class offspring", lambda r: r["class_children"]), ("distinct venues of class offspring", lambda r: fmt(float(r["class_mean_distinct_venues_of_offspring"]), 4)),
                             ("mean home distance infector to infectee, class (m)", lambda r: f"{float(r['class_mean_home_distance_m']):.0f}"),
                             ("p90 distance, class (m)", lambda r: f"{float(r['class_p90_home_distance_m']):.0f}"),
                             ("mean distance, others (m)", lambda r: f"{float(r['other_mean_home_distance_m']):.0f}")]) + "\n")
    w("Day 28 is outside 3% for these three arms (D9). Repertoire barely changes where HVIs infect. Venue choices are uniform among the list, and offspring concentrate in households (28% to 29% of class offspring are in homes), so the mean distance to infectees moves by under 10%.\n")

    w("## 9. S4: visits lever (S2 cell, `47_s4_summary.csv`)\n")
    w(shape_table(s4, extra=[("class offspring", lambda r: r["class_children"]), ("distinct venues of class offspring", lambda r: fmt(float(r["class_mean_distinct_venues_of_offspring"]), 4))]) + "\n")
    keys = [k for k in s4[0] if k.startswith("class_children_share_")]
    body = [[k.replace("class_children_share_", "")] + [pct({"v": r[k]}, "v") for r in s4] for k in keys if float(s4[0][k]) > 0]
    w(table(["venue type of class offspring", "v1", "v2", "v4"], body) + "\n")
    w("v1 is the S2 cell f = 5%, F = 3 (the same 12 runs; v2 and v4 use the same seeds and coefficient). Class hours are 7% to 9% below v1 in v2 and v4 (D6).\n")

    w("## 10. S5: coupled against uncoupled (`47_s5_summary.csv`, `47_s5_pairs.csv`)\n")
    w(shape_table(s5, extra=[("k ratio to coupled", lambda r: fmt(float(r["k_mom_ratio_to_coupled"]), 3)), ("mean m of index cases", lambda r: ci(r, "mean_m_index_cases"))]) + "\n")
    w(f"Uncoupled arms: the multiplier acts only while the agent is infectious (`--hviWhen infectious`); the coefficient was recalibrated to day 28 (coefficients 0.00041 and 0.000414). Removing the susceptibility coupling lowers k by 1.5% (shape 0.5) and 16% (shape 0.3), not by 30%, and index cases are not selected on m (0.99, 0.97). The coupled arm with the same shape had a mean m of index cases of 1.26 and 1.32. Infection pairs for the persistent S1 shape-0.3 arm (16 weeks, 8 replicates, vaccination off, `--episodeTrace`): {pairs['pairs']} pairs, Pearson {fmt(num(pairs, 'pearson'), 3)} ({fmt(num(pairs, 'pearson_low'), 3)} to {fmt(num(pairs, 'pearson_high'), 3)}), Spearman {fmt(num(pairs, 'spearman'), 3)} ({fmt(num(pairs, 'spearman_low'), 3)} to {fmt(num(pairs, 'spearman_high'), 3)}), against 0.544 for the persistent abstract trait of R6-2. Behavioural persistence (rank correlation 0.96 of weekly activity) transfers almost nothing to repeated offspring, because the hours saturate and most transmission is not discretionary.\n")

    w("## 11. S6: control from day 21 (`47_s6_summary.csv`; 12 replicates, 12 weeks; same seeds in every arm)\n")
    head = ["base", "intervention", "hours removed (share of post-day-21 hours)", "infections at day 84, none", "infections at day 84", "ratio to none (90% interval)", "infections averted per 1,000 hours removed (90% interval)", "parameter"]
    body = []
    for r in s6:
        iv = lambda v, lo, hi: f"{fmt(float(r[v]), 3)} ({fmt(float(r[lo]), 3)} to {fmt(float(r[hi]), 3)})"
        body.append([r["base"], r["intervention"], f"{100 * float(r['hours_removed_fraction']):.2f}%", fmt(float(r["infections_day84_none"]), 5), fmt(float(r["infections_day84"]), 5),
                     iv("ratio_to_none", "ratio_low", "ratio_high"), iv("infections_averted_per_1000_hours_removed", "averted_per_1000h_low", "averted_per_1000h_high"),
                     r["closure_types"] or r["scale_param"] or "5%"])
    w(table(head, body) + "\n")
    w("`cell` is the S2 cell (f = 5%, F = 3, the most active 5%), `shape` the S1 shape-0.3 arm. Closure types are physical types (6 large venues, 5 restaurants). Closing venue types removes the most infections per hour (1.85 and 1.81 per 1,000 hours); a closure acts on every agent at those venues, not only on the class, and it hits transmission at all hours there. Capping the 5% most active removes 7.45% (cell) and 8.4% (shape) of discretionary hours and reduces day-84 infections by 7.1% and 7.2%. The same hours cut for everyone gives 5.5% and 6.5%.\n")

    w("## 12. Open points and decisions for the coordinator\n")
    w("1. The result is robust to everything I tried inside the model: shape, class fraction and factor, repertoire, visits, uncoupling. If mobility is to explain the real pattern (2 in 10 causing 80%, k near 0.3), I read this as: the model would need a form of mobility that raises L-weighted hours by an order of magnitude, which the time budget (baseline 3.7 role-discretionary hours, saturation near 2.9 times) forbids, or heterogeneity in what happens at the venues, which is the trait route of rounds 5 and 6. Lever by lever, nothing here needs a large change to the movement policy; the type-mix lever does need a model change (L by type).")
    w("2. Setting different L per venue type (as `--venueProfile` can) is the one change that would make the type-mix lever and the occupational cell meaningful. I did not run it; say if you want it.")
    w("3. S7 (optional, ward size with HVI staff) was not run.")
    w("4. Open: S1 (iii) was first recorded as met on the dumped, scaled multiplier; the unscaled value (1.32) fails. I corrected the S1 and S5 CSVs and this note.\n")

    w("## Files\n")
    w("`47_round7_results.md` (this note), `47a_review_of_note46.md`, `47_r70_*.csv` (4), `47_t3_t4_s1.csv`, `47_t3_t4_duration_lever_s1.csv`, `47_t5_deciles.csv`, `47_t5_slopes.csv`, `47_t6_levers.csv`, `47_s1_summary.csv`, `47_s1_offspring.csv`, `47_s2_summary.csv`, `47_s2_offspring.csv`, `47_s3_*.csv`, `47_s4_*.csv`, `47_s5_summary.csv`, `47_s5_offspring.csv`, `47_s5_pairs.csv`, `47_s6_summary.csv`, `47_upload_index.md`. No file exceeds 1 MB.")
    text = "\n".join(out) + "\n"
    (OUT / "47_round7_results.md").write_text(text, newline="\n")
    print(len(text), "characters")


if __name__ == "__main__":
    main()
