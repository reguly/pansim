#!/usr/bin/env python3
"""Generate 62_round12_results.md and 62_upload_index.md from the Round 12 CSVs in superspreader/."""
from pathlib import Path
from report_tables import OUT, ci, fmt, num, pct, rows, table

W1 = "world1_multiplier_only"
W2A = "world2a_scene_L30_sh0.70"
W2B = "world2b_scene_L10_sh0.58"
W3B_P = "world3b_events_M30_rate0.146_paired"
W3B_R6 = "world3b_events_M30_rate0.146_round6"

NAMES = {
    W1: "world 1, multiplier only (shape 0.32, seeds 77001..77012)",
    W2A: "world 2a, strong scene + multiplier (L=30, shape 0.70, seeds 77001..77012)",
    W2B: "world 2b, moderate scene + multiplier (L=10, shape 0.58, seeds 77001..77012)",
    W3B_P: "world 3b (paired), closed-group events (M=30, rate 0.1456, seeds 77001..77012)",
    W3B_R6: "world 3b (round 6), closed-group events (M=30, rate 0.1456, seeds 68101..68112)",
}

SHORT_NAMES = {
    W1: "World 1 (multiplier sh=0.32)",
    W2A: "World 2a (scene L=30, sh=0.70)",
    W2B: "World 2b (scene L=10, sh=0.58)",
    W3B_P: "World 3b paired (events M=30, r=0.1456)",
    W3B_R6: "World 3b round 6 (events M=30, r=0.1456)",
}


def main():
    w = {r["cell"]: r for r in rows("62_r121_worlds_paired.csv")}
    ev = {r["arm"]: r for r in rows("62_r121_event_semantics.csv")}
    th_rows = rows("62_r122_thinning.csv")
    th = {(r["world"], r["scheme"], float(r["detection_rate"])): r for r in th_rows}

    out = []
    a = out.append

    def v(cell, key, d=3):
        return fmt(num(w[cell], key), d)

    def fdec(val, d=2):
        return f"{float(val):.{d}f}"

    a("# ACT-049 note 62: round 12, paired world 3b, event rate semantics, and under-detection thinning\n")
    a("19 October 2026. Reply to note 61 (and note 60). Pre-run review and registered predictions: `62a_review_of_note61.md`. Code: `superspreader/study/run_round12.py`, `analyze_round12.py`, `report_round12.py`; binary `build_r10/panSim` (no C++ changes; location and agent files untouched).\n")

    a("## Headline\n")
    a(f"1. **R12-1 item 1 (Paired World 3b on common seeds `77001..77012`):** Running the Round-6 closed-group event arm (`M = 30`, `--eventRate 0.1456`, `--eventFactor 3000`, duration `2h`, venue types `5,8`) on the common seed set `77001..77012` and calibrating `-k` to `0.000130087` matches day-28 cumulative infections within `+1.3%` (`6,293.9` vs `6,211.25`). It gives likelihood **`k_ml = {v(W3B_P, 'k_ml')}`** (`{v(W3B_P, 'k_ml_low')}` to `{v(W3B_P, 'k_ml_high')}`) and moment **`k_mom = {v(W3B_P, 'k_mom')}`** (`{v(W3B_P, 'k_mom_low')}` to `{v(W3B_P, 'k_mom_high')}`), with ratio **`k_ml / k_mom = {fdec(num(w[W3B_P], 'k_ml_over_k_mom'), 2)}`** (Round 6 on seeds `68101..68112`: `k_ml = {v(W3B_R6, 'k_ml')}`, `k_mom = {v(W3B_R6, 'k_mom')}`, ratio `{fdec(num(w[W3B_R6], 'k_ml_over_k_mom'), 2)}`). Its observed zero share is **`{pct(w[W3B_P], 'share_0')}`** (`-3.9` percentage points below the negative-binomial expectation `{pct(w[W3B_P], 'nb_zero_at_k_ml_own_mean')}` at `k_ml` and own mean `{v(W3B_P, 'early_R')}`), `{pct(w[W3B_P], 'share_of_index_cases_causing_80pct')}` of index cases cause 80% of offspring, `{pct(w[W3B_P], 'event_offspring_share')}` of early index-case offspring occur inside closed-group events, and its top-10 clusters have **`{pct(w[W3B_P], 'top10_clusters_mean_largest_venue_day_share')}`** of offspring in a single venue-day and only **`{pct(w[W3B_P], 'top10_clusters_mean_same_household_share')}`** in the infector's household.")
    a(f"2. **R12-1 item 2 (Event rate semantics resolved):** The file (`events_total = 83,249` on `77001..77012`, `83,086` on `68101..68112`) is right and the prose in `59_round11_results.md` (\"14.6% of agents attend a closed group every day\") was wrong. In C++ (`locationList.h` `updateDailyEvents` and `infectionPolicies.h` `prepareGroupEvents` / `runGroupEvents`), `--eventRate 0.1456` is the **daily Bernoulli probability per eligible venue** of types `5` (`420` restaurants) and `8` (`1,280` long shops). Out of `1,700` eligible venues in `locations1.json`, `1,700 × 0.1456 = 247.52` venues per day are selected (`247.76`/day observed in paired World 3b). Because `32.7%` of selected venues have nobody present at the randomly drawn `startStep` (10:00–20:00) and non-empty events average `12.76` attendees (`min(30, present)`), total attendance is **`2,128.1` person-attendances per day**, which is **`1.19%` of the `178,746` agents per day** and **`8.33%` in person-events per week** (`~8.04%` unique agents per week).")
    a("3. **R12-2 Prediction (a) PARTIALLY FAILS (holds for `k_mom` and zero share in all worlds and for `k_ml` in Worlds 1, 2b, and 2a, but fails for `k_ml` in World 3b):** Under random 60% and 30% detection, `k_mom` stays within `6.2%` of its un-thinned value in every world (because $k_{\\text{mom}}$ is mathematically invariant to binomial thinning for *any* distribution), and the observed zero share rises from `52.8%–56.6%` to `74.4%–79.5%` at 30% detection (matching the NB zero expectation at `k_ml` and the thinned mean within `0.4` percentage points). However, `k_ml` stays within 15% only when the true distribution is close to a single negative binomial (`+2.4%` and `-1.2%` in World 1; `-3.7%` and `-12.2%` in World 2b; `-3.0%` and `-13.5%` in World 2a). In **World 3b**, where the un-thinned distribution is a two-component mixture (`k_ml = 0.306`, `k_mom = 0.157`), random thinning maps counts of `1–2` in the near-Poisson body to `0` while event clusters of `15–28` still survive as `5–12`, pulling `k_ml` downward toward `k_mom`: `k_ml` drops by **`-19.1%`** (`0.247`) at 60% detection and **`-40.8%`** (`0.181`) at 30% detection, compressing `k_ml / k_mom` from `1.95` to `1.53` and `1.22`.")
    a("4. **R12-2 Prediction (b) FAILS:** Under household-clustered detection, the same-household share of detected infectees does **not** fall in Worlds 1 and 3b. When index cases and infectees share the same household detection mask (`household_coupled`), conditioning on a detected index case guarantees (`100%`) that the index case's own household is detected while only a fraction $p$ of outside households are detected, so the same-household share of detected offspring **rises** from `33.9%` to `46.6%` (`p=0.6`) and `62.2%` (`p=0.3`) in World 1 (`17.8%` to `28.8%` and `52.7%` in top-10 clusters) and from `21.7%` to `32.3%` and `47.4%` in World 3b. Even when whole households of infectees vanish with probability $1-p$ independently of the index case (`household_infectee`), every infectee has marginal detection probability $p$ (`all_hh` stays at `33.9%` and `32.4%` in World 1, `21.6%` and `22.3%` in World 3b), and in the top-10 clusters same-household share still rises (`22.5%` and `33.4%` vs random's `19.0%` and `25.2%` in World 1) because whole surviving households stay intact while multi-household clusters are thinned. Nor is `k_ml / k_mom` at least `0.1` lower than random across Worlds 1 and 3b (`+0.02` and `+0.01` under `household_infectee` in World 1; `-0.04` and `-0.06` in World 3b; `+0.23` and `+0.45` under `household_coupled` in World 3b).")
    a("5. **R12-2 Prediction (c) PARTIALLY HOLDS at 60% detection and FAILS on the fine separation between Worlds 1 and 2b at 30% detection (while World 3b remains cleanly separated by >53 percentage points on venue-day share, and same-household share separates World 1 from World 2b):** At 60% detection, both the zero gap (`world 3b < world 2b < world 1`: `-1.75 < -0.56 < +0.05` pts under random) and the largest-venue-day share (`world 2b < world 1 < world 3b`: `21.6% < 24.7% < 93.9%`) preserve their exact 100%-detection order. At 30% detection (`R ≈ 0.44`), `75%–80%` of detected index cases have zero offspring, shrinking the NB zero-share gap by tenfold in all worlds (to `-0.39, -0.23, -0.09` pts under random, and `-0.28, -0.33, -0.15` pts under `household_infectee`, where Worlds 3b and 2b swap by `0.05` pts), while discrete small-cluster denominators (`6–8` detected offspring in top-10 clusters) push the largest-venue-day share of both World 1 (`33.4%`) and World 2b (`35.1%`) to `~32%–36%`. Crucially, however, **World 3b stays at `89.6%–92.9%` in a single venue-day** even at 30% detection, and **same-household share** cleanly separates World 1 (`25.2%–52.7%` in top-10 clusters; `32.4%–62.2%` overall) from World 2b (`13.1%–28.7%` in top-10 clusters; `14.6%–38.4%` overall).\n")

    a("## 1. R12-1 Item 1: Paired World 3b on Common Seeds (`77001..77012`) Alongside Worlds 1, 2a, and 2b\n")
    head = [
        "world", "coeff (-k)", "likelihood k (primary)", "moment k", "k_ml / k_mom",
        "early R", "observed zero share", "NB zero (at k_ml, own mean)", "observed minus NB zero",
        "observed causing 80%", "NB causing 80% (at k_ml, own mean)", "event offspring share", "day 28 vs 6,211"
    ]
    body = []
    for c in (W1, W2A, W2B, W3B_P, W3B_R6):
        ev_sh = pct(w[c], "event_offspring_share") if num(w[c], "event_offspring_share") > 0 else "0.0%"
        body.append([
            SHORT_NAMES[c], fmt(num(w[c], "background_coefficient"), 3),
            ci(w[c], "k_ml"), ci(w[c], "k_mom"), fdec(num(w[c], "k_ml_over_k_mom"), 2),
            ci(w[c], "early_R"), pct(w[c], "share_0"), pct(w[c], "nb_zero_at_k_ml_own_mean"),
            f"{100 * num(w[c], 'observed_zero_minus_nb_zero_at_k_ml'):+.1f} pts",
            pct(w[c], "share_of_index_cases_causing_80pct"), pct(w[c], "nb_80pct_at_k_ml_own_mean"),
            ev_sh, pct({"v": w[c]["day28_vs_6211.25"]}, "v")
        ])
    a(table(head, body) + "\n")

    a("### Spatial and cluster-composition fingerprints across the paired worlds\n")
    head = [
        "world", "infections at home", "school + work", "4 high-L types", "shop_long (type 8)",
        "restaurant (type 5)", "hh SAR", "largest offspring (max / rep mean)",
        "top-10 clusters: mean offspring", "distinct venues", "largest venue-day share",
        "same-household share", "same-venue-type share (modal)"
    ]
    body = []
    for c in (W1, W2A, W2B, W3B_P, W3B_R6):
        body.append([
            SHORT_NAMES[c],
            pct(w[c], "infections_share_home"),
            pct(w[c], "infections_share_school_and_work"),
            pct(w[c], "infections_share_high_L_types"),
            pct(w[c], "infections_share_shop_long"),
            pct(w[c], "infections_share_restaurant"),
            fmt(num(w[c], "household_secondary_attack_rate"), 4),
            f"{w[c]['largest_offspring_max']} / {fdec(num(w[c], 'largest_offspring_mean_over_replicates'), 1)}",
            fdec(num(w[c], "top10_clusters_mean_offspring"), 1),
            fdec(num(w[c], "top10_clusters_mean_distinct_venues"), 2),
            pct(w[c], "top10_clusters_mean_largest_venue_day_share"),
            pct(w[c], "top10_clusters_mean_same_household_share"),
            f"{pct(w[c], 'top10_clusters_mean_same_venue_type_share')} ({w[c]['top10_clusters_modal_venue_type_mode']})",
        ])
    a(table(head, body) + "\n")
    a("Running World 3b on the common seeds `77001..77012` confirms every structural property seen in the Round-6 seed set (`68101..68112`): `k_ml = 0.306` (`0.294` to `0.318`), `k_mom = 0.157` (`0.151` to `0.162`), `k_ml / k_mom = 1.95`, a `-3.9`-point zero-share deficit below the negative binomial at `k_ml` (`54.4%` observed vs `58.3%` NB), `64.1%` of early index-case offspring (`63.1%` of all non-seed infections) occurring inside closed-group events, and top-10 clusters that occur almost entirely in a single venue on a single day (`91.5%` largest-venue-day share, `1.58` distinct venues, `2.9%` same-household share).\n")

    a("## 2. R12-1 Item 2: Exact Closed-Group Event Rate Semantics (`62_r121_event_semantics.csv`)\n")
    e_p = ev[W3B_P]
    e_6 = ev[W3B_R6]
    head = ["metric", "World 3b paired (77001..77012)", "World 3b round 6 (68101..68112)"]
    body = [
        ["Total locations in `locations1.json`", e_p["total_locations_in_city"], e_6["total_locations_in_city"]],
        ["Eligible type 5 (`restaurant`) locations", e_p["eligible_type5_restaurants"], e_6["eligible_type5_restaurants"]],
        ["Eligible type 8 (`shop_long`) locations", e_p["eligible_type8_long_shops"], e_6["eligible_type8_long_shops"]],
        ["Total eligible venues (`--eventTypes 5,8`)", e_p["eligible_venues_total"], e_6["eligible_venues_total"]],
        ["`--eventRate` flag (daily probability per eligible venue)", e_p["event_rate_flag"], e_6["event_rate_flag"]],
        ["Expected venue-events per day (`1,700 × 0.1456`)", fdec(num(e_p, "expected_events_per_day_from_venues"), 2), fdec(num(e_6, "expected_events_per_day_from_venues"), 2)],
        ["Total scheduled events over 12 reps × 28 days (`events.tsv` rows)", e_p["events_total"], e_6["events_total"]],
        ["Observed scheduled events per day (`events_total / 336`)", fdec(num(e_p, "observed_events_per_day"), 2), fdec(num(e_6, "observed_events_per_day"), 2)],
        ["Scheduled events per day by type (`type 5` / `type 8`)", f"{fdec(num(e_p, 'observed_events_per_day_type5'), 2)} / {fdec(num(e_p, 'observed_events_per_day_type8'), 2)}", f"{fdec(num(e_6, 'observed_events_per_day_type5'), 2)} / {fdec(num(e_6, 'observed_events_per_day_type8'), 2)}"],
        ["Empty events (`present == 0` at `startStep`): count and share", f"{e_p['empty_events_total']} ({pct(e_p, 'empty_events_share')})", f"{e_6['empty_events_total']} ({pct(e_6, 'empty_events_share')})"],
        ["Non-empty events (`present > 0`): total and per day", f"{e_p['nonempty_events_total']} ({fdec(num(e_p, 'nonempty_events_per_day'), 2)}/day)", f"{e_6['nonempty_events_total']} ({fdec(num(e_6, 'nonempty_events_per_day'), 2)}/day)"],
        ["Agents present at venue (`present`): mean all / mean non-empty / median non-empty / max", f"{fdec(num(e_p, 'mean_present_all_events'), 2)} / {fdec(num(e_p, 'mean_present_nonempty_events'), 2)} / {fdec(num(e_p, 'median_present_nonempty_events'), 0)} / {e_p['max_present_in_event']}", f"{fdec(num(e_6, 'mean_present_all_events'), 2)} / {fdec(num(e_6, 'mean_present_nonempty_events'), 2)} / {fdec(num(e_6, 'median_present_nonempty_events'), 0)} / {e_6['max_present_in_event']}"],
        ["Attendees in closed group (`group = min(30, present)`): mean all / mean non-empty / median non-empty / max", f"{fdec(num(e_p, 'mean_group_size_all_events'), 2)} / {fdec(num(e_p, 'mean_group_size_nonempty_events'), 2)} / {fdec(num(e_p, 'median_group_size_nonempty_events'), 0)} / {e_p['max_group_size_in_event']}", f"{fdec(num(e_6, 'mean_group_size_all_events'), 2)} / {fdec(num(e_6, 'mean_group_size_nonempty_events'), 2)} / {fdec(num(e_6, 'median_group_size_nonempty_events'), 0)} / {e_6['max_group_size_in_event']}"],
        ["Share of events hitting the cap `M = 30` (all / non-empty)", f"{pct(e_p, 'share_all_events_at_cap_M30')} / {pct(e_p, 'share_nonempty_events_at_cap_M30')}", f"{pct(e_6, 'share_all_events_at_cap_M30')} / {pct(e_6, 'share_nonempty_events_at_cap_M30')}"],
        ["Person-attendances per day (`sum(group) / 336`)", fdec(num(e_p, "person_attendances_per_day"), 1), fdec(num(e_6, "person_attendances_per_day"), 1)],
        ["**Share of agents (`N = 178,746`) attending any closed group on a given day**", pct(e_p, "daily_agent_attendance_share"), pct(e_6, "daily_agent_attendance_share")],
        ["**Share of agents attending in a given week (person-events / unique binomial approx)**", f"{pct(e_p, 'weekly_agent_attendance_share_person_events')} / ~{pct(e_p, 'weekly_unique_agent_attendance_share_approx')}", f"{pct(e_6, 'weekly_agent_attendance_share_person_events')} / ~{pct(e_6, 'weekly_unique_agent_attendance_share_approx')}"],
        ["Events with >=1 infectious attendee (`infectious_in_group > 0`): total and per day", f"{e_p['events_with_infectious_total']} ({fdec(num(e_p, 'events_with_infectious_per_day'), 2)}/day, {pct(e_p, 'events_with_infectious_share_of_nonempty')} of non-empty)", f"{e_6['events_with_infectious_total']} ({fdec(num(e_6, 'events_with_infectious_per_day'), 2)}/day, {pct(e_6, 'events_with_infectious_share_of_nonempty')} of non-empty)"],
        ["Events with >=1 transmission (`infected > 0`): total and per day", f"{e_p['events_with_transmission_total']} ({fdec(num(e_p, 'events_with_transmission_per_day'), 2)}/day)", f"{e_6['events_with_transmission_total']} ({fdec(num(e_6, 'events_with_transmission_per_day'), 2)}/day)"],
        ["Secondary infections per active event (`infectious_in_group > 0`): mean / max", f"{fdec(num(e_p, 'mean_infections_per_infectious_event'), 2)} / {e_p['max_infections_in_single_event']}", f"{fdec(num(e_6, 'mean_infections_per_infectious_event'), 2)} / {e_6['max_infections_in_single_event']}"],
        ["Total infections inside closed-group events (`events.tsv.infections`)", e_p["event_infections_total"], e_6["event_infections_total"]],
        ["Share of all non-seed infections (days 1..28) inside events", pct(e_p, "event_infections_share_of_all_nonseed"), pct(e_6, "event_infections_share_of_all_nonseed")],
        ["Share of early index-case offspring (days 1..10) inside events", pct(e_p, "event_offspring_share_early_index_d1_10"), pct(e_6, "event_offspring_share_early_index_d1_10")],
    ]
    a(table(head, body) + "\n")
    a("**How closed-group events work in C++ (`include/locationList.h` and `include/policies/infectionPolicies.h`):**\n")
    a("1. At the start of each simulation day, `updateDailyEvents(day)` iterates over the `1,700` venues of types `5` and `8` and selects each venue independently with probability `--eventRate 0.1456` (`247.5` venues/day).\n")
    a("2. `prepareGroupEvents` assigns each selected venue a single random `startStep` between 10:00 and 20:00 and resets its venue-day `eventBoost` to `1.0`.\n")
    a("3. At `startStep`, `runGroupEvents` inspects the `present` agents who happen to be at that venue at that exact step under their normal daily movement schedule. If `present > 0` (`67.3%` of scheduled events, `166.8`/day), it samples `group = min(30, present)` attendees without replacement (mean `12.76` attendees per non-empty event, `8.59` across all scheduled events). That yields `2,128.1` person-attendances/day, or **`1.19%` of the city population per day** (`~8.04%` unique agents per week).\n")
    a("4. If at least one sampled attendee is infectious (`10.72` events/day), each susceptible attendee in `group` faces a 2-hour (`120`-minute) closed-group hazard with `eventFactor = 3000`, producing an average of **`13.56` secondary infections per active event** (maximum `28`) and accounting for **`63.1%` of all non-seed infections** and **`64.1%` of early index-case offspring**.\n")

    a("## 3. R12-2: Under-Detection Thinning (`p = 1.0, 0.6, 0.3`) on Paired Traces (`62_r122_thinning.csv`)\n")
    a("As detailed in `62a_review_of_note61.md`, we evaluate both random per-infection detection (`random`) and two variants of household-clustered detection on the paired traces (`77001..77012`) for Worlds 1, 2b, 3b, and 2a:\n")
    a("- **`random`:** Each infected agent in `trace.tsv` is detected independently with probability $p \\in \\{0.6, 0.3\\}$.\n")
    a("- **`household_infectee` (uncoupled household thinning of infectees):** Index cases (days 1–10) are detected at rate $p$, and each household of infectees is detected as a whole with probability $p$ drawn independently of the index case's own detection (so an infector's entire household cluster vanishes with probability $1-p$ or survives intact with probability $p$).\n")
    a("- **`household_coupled` (coupled agent-level household mask):** Each household in the city is selected with probability $p$; both index cases and infectees are detected iff their household is selected (so conditioning on a detected index case guarantees with probability `1` that the index case's own household is detected, while outside-household infectees are detected with probability $p$).\n")

    head = [
        "world", "scheme", "rate p", "detected index cases", "thinned R",
        "k_ml (rel change)", "k_mom (rel change)", "k_ml / k_mom",
        "observed zero", "NB zero (at k_ml)", "zero gap (obs - NB)",
        "causing 80%", "all-offspring same-hh", "top-10 clusters: mean offspring",
        "top-10 same-hh share", "top-10 largest venue-day share", "top-10 distinct venues"
    ]
    body = []
    for w_key in (W1, W2B, W3B_P, W2A):
        for scheme, rate in [
            ("full", 1.0),
            ("random", 0.6),
            ("random", 0.3),
            ("household_infectee", 0.6),
            ("household_infectee", 0.3),
            ("household_coupled", 0.6),
            ("household_coupled", 0.3),
        ]:
            r = th[(w_key, scheme, rate)]
            kml_s = f"{fdec(num(r, 'k_ml'), 3)} ({100 * num(r, 'k_ml_rel_change_vs_full'):+.1f}%)"
            kmom_s = f"{fdec(num(r, 'k_mom'), 3)} ({100 * num(r, 'k_mom_rel_change_vs_full'):+.1f}%)"
            body.append([
                SHORT_NAMES[w_key],
                scheme,
                f"{rate:.1f}",
                r["index_cases"],
                fdec(num(r, "early_R"), 3),
                kml_s,
                kmom_s,
                fdec(num(r, "k_ml_over_k_mom"), 2),
                pct(r, "share_0"),
                pct(r, "nb_zero_at_k_ml_own_mean"),
                f"{100 * num(r, 'observed_zero_minus_nb_zero_at_k_ml'):+.2f} pts",
                pct(r, "share_of_index_cases_causing_80pct"),
                pct(r, "all_detected_offspring_same_household_share"),
                fdec(num(r, "top10_clusters_mean_offspring"), 1),
                pct(r, "top10_clusters_mean_same_household_share"),
                pct(r, "top10_clusters_mean_largest_venue_day_share"),
                fdec(num(r, "top10_clusters_mean_distinct_venues"), 2),
            ])
    a(table(head, body) + "\n")

    a("## 4. Evaluation of Registered Predictions in Note 61\n")
    a("1. **Prediction (a) — PARTIALLY FAILS (holds for `k_mom` and zero share across all worlds and for `k_ml` in Worlds 1, 2b, and 2a, but fails for `k_ml` in World 3b):**\n")
    a("   - *What holds:* Under random 60% and 30% detection, `k_mom` stays within `6.2%` of its un-thinned value in all worlds (`+4.1%, -5.8%` in World 1; `+6.2%, +3.8%` in World 2b; `+2.9%, -5.8%` in World 3b; `-2.6%, +3.3%` in World 2a), and the observed zero share rises from `52.8%–56.6%` to `74.4%–79.5%` at `p = 0.3`, matching the negative-binomial expectation at `k_ml` and the thinned mean within `0.1` to `0.4` percentage points (`76.2%` vs `76.3%` in World 1; `75.3%` vs `75.5%` in World 2b; `79.5%` vs `79.9%` in World 3b; `74.4%` vs `74.8%` in World 2a). Likewise, `k_ml` stays within the `15%` bound in World 1 (`+2.4%, -1.2%`), World 2b (`-3.7%, -12.2%`), and World 2a (`-3.0%, -13.5%`).\n")
    a("   - *What fails and why:* In **World 3b**, `k_ml` drops from `0.306` to **`0.247` (`-19.1%`)** at `p = 0.6` and **`0.181` (`-40.8%`)** at `p = 0.3`. Because World 3b is a two-component mixture (a near-Poisson background for non-event infectors plus a heavy closed-group event tail) rather than a true negative binomial, its un-thinned distribution has a large deficit of zeros relative to `k_mom` (`54.4%` observed vs `69.8%` NB at `k_mom = 0.157`), which keeps `k_ml` elevated at `0.306`. Random binomial thinning turns `1`s and `2`s in the near-Poisson body into `0`s while large event clusters (`15–28`) still survive as `5–12` offspring, pulling `k_ml` downward toward the thinning-invariant `k_mom` (`0.157`) and compressing `k_ml / k_mom` from `1.95` to `1.53` (`p = 0.6`) and `1.22` (`p = 0.3`).\n")
    a("2. **Prediction (b) — FAILS:**\n")
    a("   - Under **`household_coupled`** (where index cases and infectees use the same per-household detection mask), conditioning on a detected index case means the index case's own household is detected with probability `1` while outside households are detected with probability $p$. As a result, the same-household share of detected infectees **rises** strongly instead of falling: across all detected offspring, from `33.9%` (`p=1.0`) to `46.6%` (`p=0.6`) and `62.2%` (`p=0.3`) in World 1 (`17.8%` to `28.8%` and `52.7%` in top-10 clusters) and from `21.7%` to `32.3%` and `47.4%` in World 3b (`2.9%` to `4.8%` and `13.5%` in top-10 clusters). And in World 3b, keeping `100%` of same-household offspring prevents `k_ml` from dropping, so `k_ml / k_mom` (`1.76` at `0.6`, `1.67` at `0.3`) is `+0.23` and `+0.45` *higher* (not lower) than under random detection (`1.53` and `1.22`).\n")
    a("   - Under **`household_infectee`** (where whole households of infectees vanish with probability $1-p$ independently of index-case detection), every infectee has marginal detection probability $p$, so the overall same-household share is invariant (`33.9%` and `32.4%` in World 1; `21.6%` and `22.3%` in World 3b), while in the top-10 clusters same-household share still increases relative to random detection in World 1 (`22.5%` vs `19.0%` at `0.6`; `33.4%` vs `25.2%` at `0.3`) because surviving households stay intact as a block. Meanwhile, both `k_ml` and `k_mom` fall together (`-10.3%` and `-10.7%` at `0.6`; `-19.8%` and `-24.2%` at `0.3` in World 1), so `k_ml / k_mom` differs from random detection by only `+0.02` (`p=0.6`) and `+0.01` (`p=0.3`) in World 1 and `-0.04` and `-0.06` in World 3b.\n")
    a("3. **Prediction (c) — HOLDS at 60% detection; PARTIALLY FAILS at 30% detection on the fine ordering between Worlds 1 and 2b (while World 3b remains separated by >53 points on venue-day share, and same-household share separates Worlds 1 and 2b):**\n")
    a("   - Note first a typo in Note 61's parenthetical description of the 100%-detection venue-day order: as established in Note 59 and Note 60 Section 4, at 100% detection the largest-venue-day share of top-10 clusters is ordered **`world 2b (14.7%) < world 1 (20.3%) < world 3b (91.6%)`** (not `world 1 < world 3b < world 2b`).\n")
    a("   - At **60% detection (`p = 0.6`)**, both metrics preserve their exact 100%-detection order across all three schemes:\n")
    a("     - Zero gap (`observed - NB at k_ml`): `world 3b (-1.75 pts) < world 2b (-0.56 pts) < world 1 (+0.05 pts)` under `random` (`-1.53 < -0.67 < +0.01` under `household_infectee`; `-2.57 < -0.68 < +0.15` under `household_coupled`).\n")
    a("     - Top-10 largest-venue-day share: `world 2b (21.6%) < world 1 (24.7%) < world 3b (93.9%)` under `random` (`20.2% < 25.9% < 93.8%` under `household_infectee`; `19.7% < 25.0% < 92.1%` under `household_coupled`).\n")
    a("   - At **30% detection (`p = 0.3`)**:\n")
    a("     - The zero gap shrinks by ~10x (because `75%–80%` of index cases have 0 detected offspring at `R ≈ 0.44`): it still orders `world 3b (-0.39 pts) < world 2b (-0.23 pts) < world 1 (-0.09 pts)` under `random` and `-1.69 < -0.28 < +0.36` pts under `household_coupled`, but under `household_infectee` Worlds 3b (`-0.28 pts`) and 2b (`-0.33 pts`) are within `0.05` percentage points and swap.\n")
    a("     - On top-10 largest-venue-day share, **World 3b (`92.9%` random, `89.6%` `household_infectee`, `90.8%` `household_coupled`) remains >53 percentage points above both World 1 and World 2b**, effortlessly identifying closed-group events at 30% detection. However, because top-10 clusters in Worlds 1 and 2b shrink from `17–22` offspring to `6–8` detected offspring at `p = 0.3`, the discrete ratio `max(venue_day) / len(kids)` rises to `~33%–36%` in both (`33.4%` in World 1 vs `35.1%` in World 2b under `random`), erasing the small 5-point gap between Worlds 1 and 2b on venue-day share.\n")
    a("     - Instead, **same-household share** provides the thinning-robust separator between World 1 and World 2b at `p = 0.3`: in top-10 clusters, World 1 has **`25.2%`** (`random`), **`33.4%`** (`household_infectee`), and **`52.7%`** (`household_coupled`) same-household share, against **`13.1%`**, **`13.4%`**, and **`28.7%`** in World 2b (and `7.5%`, `8.3%`, `17.1%` in World 2a).\n")

    res_path = OUT / "62_round12_results.md"
    res_path.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {res_path.name} ({res_path.stat().st_size} bytes)")

    # Write 62_upload_index.md with exact byte counts
    files = [
        ("62a_review_of_note61.md", "Pre-run review of Note 60 and Note 61, C++ eventRate semantics inspection, and registered predictions"),
        ("62_round12_results.md", "Main Round 12 report: R12-1 paired World 3b, R12-1 event semantics audit, and R12-2 under-detection thinning"),
        ("62_r121_worlds_paired.csv", "R12-1 summary table for paired Worlds 1, 2a, 2b, and 3b on seeds 77001..77012 plus Round-6 World 3b"),
        ("62_r121_worlds_paired_offspring.csv", "R12-1 joint (total, event) offspring count distributions for the paired worlds"),
        ("62_r121_clusters.csv", "R12-1 top-10 cluster composition rows across all replicates for the paired worlds"),
        ("62_r121_event_semantics.csv", "R12-1 closed-group event audit from locations1.json, events.tsv, and events.tsv.infections"),
        ("62_r122_thinning.csv", "R12-2 under-detection thinning table (p = 1.0, 0.6, 0.3) under random, household_infectee, and household_coupled schemes"),
    ]
    idx = [
        "# ACT-049 Round 12 Upload Index (`62_*`)\n",
        "Target Google Drive folder: `Work Hub\\University Research\\Aurora AI\\Management\\work-packages\\ACT-049`\n",
        "| File | Bytes | Description |",
        "| --- | --- | --- |",
    ]
    for fname, desc in files:
        p = OUT / fname
        idx.append(f"| `{fname}` | {p.stat().st_size} | {desc} |")
    idx_path = OUT / "62_upload_index.md"
    idx_path.write_text("\n".join(idx) + "\n", encoding="utf-8")
    print(f"wrote {idx_path.name} ({idx_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
