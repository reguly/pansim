# ACT-049 note 62: round 12, paired world 3b, event rate semantics, and under-detection thinning

19 October 2026. Reply to note 61 (and note 60). Pre-run review and registered predictions: `62a_review_of_note61.md`. Code: `superspreader/study/run_round12.py`, `analyze_round12.py`, `report_round12.py`; binary `build_r10/panSim` (no C++ changes; location and agent files untouched).

## Headline

1. **R12-1 item 1 (Paired World 3b on common seeds `77001..77012`):** Running the Round-6 closed-group event arm (`M = 30`, `--eventRate 0.1456`, `--eventFactor 3000`, duration `2h`, venue types `5,8`) on the common seed set `77001..77012` and calibrating `-k` to `0.000130087` matches day-28 cumulative infections within `+1.3%` (`6,293.9` vs `6,211.25`). It gives likelihood **`k_ml = 0.306`** (`0.294` to `0.318`) and moment **`k_mom = 0.157`** (`0.151` to `0.162`), with ratio **`k_ml / k_mom = 1.95`** (Round 6 on seeds `68101..68112`: `k_ml = 0.33`, `k_mom = 0.152`, ratio `2.16`). Its observed zero share is **`54.4% (53.7 to 55.1)`** (`-3.9` percentage points below the negative-binomial expectation `58.3%` at `k_ml` and own mean `1.48`), `16.8%` of index cases cause 80% of offspring, `64.1% (62.5 to 65.2)` of early index-case offspring occur inside closed-group events, and its top-10 clusters have **`91.5%`** of offspring in a single venue-day and only **`2.9%`** in the infector's household.
2. **R12-1 item 2 (Event rate semantics resolved):** The file (`events_total = 83,249` on `77001..77012`, `83,086` on `68101..68112`) is right and the prose in `59_round11_results.md` ("14.6% of agents attend a closed group every day") was wrong. In C++ (`locationList.h` `updateDailyEvents` and `infectionPolicies.h` `prepareGroupEvents` / `runGroupEvents`), `--eventRate 0.1456` is the **daily Bernoulli probability per eligible venue** of types `5` (`420` restaurants) and `8` (`1,280` long shops). Out of `1,700` eligible venues in `locations1.json`, `1,700 × 0.1456 = 247.52` venues per day are selected (`247.76`/day observed in paired World 3b). Because `32.7%` of selected venues have nobody present at the randomly drawn `startStep` (10:00–20:00) and non-empty events average `12.76` attendees (`min(30, present)`), total attendance is **`2,128.1` person-attendances per day**, which is **`1.19%` of the `178,746` agents per day** and **`8.33%` in person-events per week** (`~8.04%` unique agents per week).
3. **R12-2 Prediction (a) PARTIALLY FAILS (holds for `k_mom` and zero share in all worlds and for `k_ml` in Worlds 1, 2b, and 2a, but fails for `k_ml` in World 3b):** Under random 60% and 30% detection, `k_mom` stays within `6.2%` of its un-thinned value in every world (because $k_{\text{mom}}$ is mathematically invariant to binomial thinning for *any* distribution), and the observed zero share rises from `52.8%–56.6%` to `74.4%–79.5%` at 30% detection (matching the NB zero expectation at `k_ml` and the thinned mean within `0.4` percentage points). However, `k_ml` stays within 15% only when the true distribution is close to a single negative binomial (`+2.4%` and `-1.2%` in World 1; `-3.7%` and `-12.2%` in World 2b; `-3.0%` and `-13.5%` in World 2a). In **World 3b**, where the un-thinned distribution is a two-component mixture (`k_ml = 0.306`, `k_mom = 0.157`), random thinning maps counts of `1–2` in the near-Poisson body to `0` while event clusters of `15–28` still survive as `5–12`, pulling `k_ml` downward toward `k_mom`: `k_ml` drops by **`-19.1%`** (`0.247`) at 60% detection and **`-40.8%`** (`0.181`) at 30% detection, compressing `k_ml / k_mom` from `1.95` to `1.53` and `1.22`.
4. **R12-2 Prediction (b) FAILS:** Under household-clustered detection, the same-household share of detected infectees does **not** fall in Worlds 1 and 3b. When index cases and infectees share the same household detection mask (`household_coupled`), conditioning on a detected index case guarantees (`100%`) that the index case's own household is detected while only a fraction $p$ of outside households are detected, so the same-household share of detected offspring **rises** from `33.9%` to `46.6%` (`p=0.6`) and `62.2%` (`p=0.3`) in World 1 (`17.8%` to `28.8%` and `52.7%` in top-10 clusters) and from `21.7%` to `32.3%` and `47.4%` in World 3b. Even when whole households of infectees vanish with probability $1-p$ independently of the index case (`household_infectee`), every infectee has marginal detection probability $p$ (`all_hh` stays at `33.9%` and `32.4%` in World 1, `21.6%` and `22.3%` in World 3b), and in the top-10 clusters same-household share still rises (`22.5%` and `33.4%` vs random's `19.0%` and `25.2%` in World 1) because whole surviving households stay intact while multi-household clusters are thinned. Nor is `k_ml / k_mom` at least `0.1` lower than random across Worlds 1 and 3b (`+0.02` and `+0.01` under `household_infectee` in World 1; `-0.04` and `-0.06` in World 3b; `+0.23` and `+0.45` under `household_coupled` in World 3b).
5. **R12-2 Prediction (c) PARTIALLY HOLDS at 60% detection and FAILS on the fine separation between Worlds 1 and 2b at 30% detection (while World 3b remains cleanly separated by >53 percentage points on venue-day share, and same-household share separates World 1 from World 2b):** At 60% detection, both the zero gap (`world 3b < world 2b < world 1`: `-1.75 < -0.56 < +0.05` pts under random) and the largest-venue-day share (`world 2b < world 1 < world 3b`: `21.6% < 24.7% < 93.9%`) preserve their exact 100%-detection order. At 30% detection (`R ≈ 0.44`), `75%–80%` of detected index cases have zero offspring, shrinking the NB zero-share gap by tenfold in all worlds (to `-0.39, -0.23, -0.09` pts under random, and `-0.28, -0.33, -0.15` pts under `household_infectee`, where Worlds 3b and 2b swap by `0.05` pts), while discrete small-cluster denominators (`6–8` detected offspring in top-10 clusters) push the largest-venue-day share of both World 1 (`33.4%`) and World 2b (`35.1%`) to `~32%–36%`. Crucially, however, **World 3b stays at `89.6%–92.9%` in a single venue-day** even at 30% detection, and **same-household share** cleanly separates World 1 (`25.2%–52.7%` in top-10 clusters; `32.4%–62.2%` overall) from World 2b (`13.1%–28.7%` in top-10 clusters; `14.6%–38.4%` overall).

## 1. R12-1 Item 1: Paired World 3b on Common Seeds (`77001..77012`) Alongside Worlds 1, 2a, and 2b

| world | coeff (-k) | likelihood k (primary) | moment k | k_ml / k_mom | early R | observed zero share | NB zero (at k_ml, own mean) | observed minus NB zero | observed causing 80% | NB causing 80% (at k_ml, own mean) | event offspring share | day 28 vs 6,211 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| World 1 (multiplier sh=0.32) | 0.000499 | 0.357 (0.346 to 0.368) | 0.338 (0.307 to 0.37) | 1.06 | 1.4 (1.37 to 1.44) | 56.6% (56.0 to 57.2) | 56.5% | +0.0 pts | 21.5% | 21.4% | 0.0% | 1.3% |
| World 2a (scene L=30, sh=0.70) | 4.29e-05 | 0.355 (0.339 to 0.373) | 0.236 (0.202 to 0.282) | 1.50 | 1.64 (1.58 to 1.71) | 52.8% (52.1 to 53.6) | 54.1% | -1.3 pts | 21.1% | 21.5% | 0.0% | 0.3% |
| World 2b (scene L=10, sh=0.58) | 0.000117 | 0.365 (0.354 to 0.377) | 0.257 (0.241 to 0.278) | 1.42 | 1.55 (1.5 to 1.6) | 53.5% (53.1 to 54.1) | 54.6% | -1.1 pts | 21.7% | 21.8% | 0.0% | -0.2% |
| World 3b paired (events M=30, r=0.1456) | 0.00013 | 0.306 (0.294 to 0.318) | 0.157 (0.151 to 0.162) | 1.95 | 1.48 (1.42 to 1.53) | 54.4% (53.7 to 55.1) | 58.3% | -3.9 pts | 16.8% | 19.5% | 64.1% (62.5 to 65.2) | 1.3% |
| World 3b round 6 (events M=30, r=0.1456) | 0.000142 | 0.33 (0.322 to 0.337) | 0.152 (0.15 to 0.155) | 2.16 | 1.52 (1.47 to 1.56) | 52.3% (51.7 to 52.9) | 56.6% | -4.4 pts | 18.1% | 20.5% | 61.7% (60.9 to 62.3) | 0.2% |

### Spatial and cluster-composition fingerprints across the paired worlds

| world | infections at home | school + work | 4 high-L types | shop_long (type 8) | restaurant (type 5) | hh SAR | largest offspring (max / rep mean) | top-10 clusters: mean offspring | distinct venues | largest venue-day share | same-household share | same-venue-type share (modal) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| World 1 (multiplier sh=0.32) | 34.2% | 17.5% | 16.7% | 10.4% | 5.1% | 0.001647 | 54 / 27.7 | 17.3 | 6.20 | 19.8% | 17.7% | 49.2% (school) |
| World 2a (scene L=30, sh=0.70) | 6.0% | 0.8% | 91.2% | 0.7% | 26.2% | 0.0004123 | 88 / 37.6 | 22.5 | 9.22 | 14.7% | 3.3% | 41.9% (large_venue) |
| World 2b (scene L=10, sh=0.58) | 14.1% | 2.3% | 77.9% | 1.9% | 22.6% | 0.0008257 | 57 / 36.8 | 21.5 | 9.40 | 14.5% | 6.5% | 40.5% (large_venue) |
| World 3b paired (events M=30, r=0.1456) | 21.3% | 3.2% | 13.5% | 57.6% | 10.3% | 0.001475 | 46 / 32.4 | 25.2 | 1.73 | 91.5% | 2.9% | 96.2% (shop_long) |
| World 3b round 6 (events M=30, r=0.1456) | 22.6% | 3.5% | 12.5% | 56.8% | 9.3% | 0.001902 | 50 / 39.0 | 26.8 | 1.74 | 88.2% | 3.9% | 96.8% (shop_long) |

Running World 3b on the common seeds `77001..77012` confirms every structural property seen in the Round-6 seed set (`68101..68112`): `k_ml = 0.306` (`0.294` to `0.318`), `k_mom = 0.157` (`0.151` to `0.162`), `k_ml / k_mom = 1.95`, a `-3.9`-point zero-share deficit below the negative binomial at `k_ml` (`54.4%` observed vs `58.3%` NB), `64.1%` of early index-case offspring (`63.1%` of all non-seed infections) occurring inside closed-group events, and top-10 clusters that occur almost entirely in a single venue on a single day (`91.5%` largest-venue-day share, `1.58` distinct venues, `2.9%` same-household share).

## 2. R12-1 Item 2: Exact Closed-Group Event Rate Semantics (`62_r121_event_semantics.csv`)

| metric | World 3b paired (77001..77012) | World 3b round 6 (68101..68112) |
|---|---|---|
| Total locations in `locations1.json` | 81471 | 81471 |
| Eligible type 5 (`restaurant`) locations | 420 | 420 |
| Eligible type 8 (`shop_long`) locations | 1280 | 1280 |
| Total eligible venues (`--eventTypes 5,8`) | 1700 | 1700 |
| `--eventRate` flag (daily probability per eligible venue) | 0.1456 | 0.1456 |
| Expected venue-events per day (`1,700 × 0.1456`) | 247.52 | 247.52 |
| Total scheduled events over 12 reps × 28 days (`events.tsv` rows) | 83249 | 83086 |
| Observed scheduled events per day (`events_total / 336`) | 247.76 | 247.28 |
| Scheduled events per day by type (`type 5` / `type 8`) | 60.95 / 186.81 | 60.62 / 186.66 |
| Empty events (`present == 0` at `startStep`): count and share | 27221 (32.7%) | 27271 (32.8%) |
| Non-empty events (`present > 0`): total and per day | 56028 (166.75/day) | 55815 (166.12/day) |
| Agents present at venue (`present`): mean all / mean non-empty / median non-empty / max | 11.16 / 16.58 / 10 / 1314 | 11.20 / 16.67 / 10 / 1225 |
| Attendees in closed group (`group = min(30, present)`): mean all / mean non-empty / median non-empty / max | 8.59 / 12.76 / 10 / 30 | 8.52 / 12.69 / 10 / 30 |
| Share of events hitting the cap `M = 30` (all / non-empty) | 8.6% / 12.8% | 8.6% / 12.8% |
| Person-attendances per day (`sum(group) / 336`) | 2128.1 | 2107.8 |
| **Share of agents (`N = 178,746`) attending any closed group on a given day** | 1.2% | 1.2% |
| **Share of agents attending in a given week (person-events / unique binomial approx)** | 8.3% / ~8.0% | 8.3% / ~8.0% |
| Events with >=1 infectious attendee (`infectious_in_group > 0`): total and per day | 3601 (10.72/day, 6.4% of non-empty) | 3379 (10.06/day, 6.1% of non-empty) |
| Events with >=1 transmission (`infected > 0`): total and per day | 3476 (10.35/day) | 3258 (9.70/day) |
| Secondary infections per active event (`infectious_in_group > 0`): mean / max | 13.56 / 28 | 13.94 / 28 |
| Total infections inside closed-group events (`events.tsv.infections`) | 48829 | 47089 |
| Share of all non-seed infections (days 1..28) inside events | 63.1% | 61.2% |
| Share of early index-case offspring (days 1..10) inside events | 64.1% | 61.7% |

**How closed-group events work in C++ (`include/locationList.h` and `include/policies/infectionPolicies.h`):**

1. At the start of each simulation day, `updateDailyEvents(day)` iterates over the `1,700` venues of types `5` and `8` and selects each venue independently with probability `--eventRate 0.1456` (`247.5` venues/day).

2. `prepareGroupEvents` assigns each selected venue a single random `startStep` between 10:00 and 20:00 and resets its venue-day `eventBoost` to `1.0`.

3. At `startStep`, `runGroupEvents` inspects the `present` agents who happen to be at that venue at that exact step under their normal daily movement schedule. If `present > 0` (`67.3%` of scheduled events, `166.8`/day), it samples `group = min(30, present)` attendees without replacement (mean `12.76` attendees per non-empty event, `8.59` across all scheduled events). That yields `2,128.1` person-attendances/day, or **`1.19%` of the city population per day** (`~8.04%` unique agents per week).

4. If at least one sampled attendee is infectious (`10.72` events/day), each susceptible attendee in `group` faces a 2-hour (`120`-minute) closed-group hazard with `eventFactor = 3000`, producing an average of **`13.56` secondary infections per active event** (maximum `28`) and accounting for **`63.1%` of all non-seed infections** and **`64.1%` of early index-case offspring**.

## 3. R12-2: Under-Detection Thinning (`p = 1.0, 0.6, 0.3`) on Paired Traces (`62_r122_thinning.csv`)

As detailed in `62a_review_of_note61.md`, we evaluate both random per-infection detection (`random`) and two variants of household-clustered detection on the paired traces (`77001..77012`) for Worlds 1, 2b, 3b, and 2a:

- **`random`:** Each infected agent in `trace.tsv` is detected independently with probability $p \in \{0.6, 0.3\}$.

- **`household_infectee` (uncoupled household thinning of infectees):** Index cases (days 1–10) are detected at rate $p$, and each household of infectees is detected as a whole with probability $p$ drawn independently of the index case's own detection (so an infector's entire household cluster vanishes with probability $1-p$ or survives intact with probability $p$).

- **`household_coupled` (coupled agent-level household mask):** Each household in the city is selected with probability $p$; both index cases and infectees are detected iff their household is selected (so conditioning on a detected index case guarantees with probability `1` that the index case's own household is detected, while outside-household infectees are detected with probability $p$).

| world | scheme | rate p | detected index cases | thinned R | k_ml (rel change) | k_mom (rel change) | k_ml / k_mom | observed zero | NB zero (at k_ml) | zero gap (obs - NB) | causing 80% | all-offspring same-hh | top-10 clusters: mean offspring | top-10 same-hh share | top-10 largest venue-day share | top-10 distinct venues |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| World 1 (multiplier sh=0.32) | full | 1.0 | 13593 | 1.405 | 0.357 (+0.0%) | 0.338 (+0.0%) | 1.06 | 56.6% (56.0 to 57.2) | 56.5% | +0.04 pts | 21.5% | 33.9% | 17.3 | 17.8% | 20.3% | 6.05 |
| World 1 (multiplier sh=0.32) | random | 0.6 | 8190 | 0.865 | 0.366 (+2.4%) | 0.352 (+4.1%) | 1.04 | 64.2% (63.3 to 64.9) | 64.1% | +0.00 pts | 19.0% | 32.9% | 9.6 | 19.0% | 24.7% | 4.65 |
| World 1 (multiplier sh=0.32) | random | 0.3 | 4136 | 0.406 | 0.353 (-1.2%) | 0.319 (-5.8%) | 1.11 | 76.2% (75.4 to 77.0) | 76.3% | -0.11 pts | 15.7% | 33.5% | 4.4 | 25.2% | 33.4% | 2.95 |
| World 1 (multiplier sh=0.32) | household_infectee | 0.6 | 8086 | 0.841 | 0.321 (-10.3%) | 0.302 (-10.7%) | 1.06 | 66.2% (65.4 to 67.2) | 66.2% | +0.04 pts | 17.9% | 33.9% | 10.0 | 22.5% | 25.9% | 4.38 |
| World 1 (multiplier sh=0.32) | household_infectee | 0.3 | 4091 | 0.454 | 0.287 (-19.8%) | 0.256 (-24.2%) | 1.12 | 76.0% (74.5 to 77.6) | 76.2% | -0.12 pts | 14.9% | 32.4% | 5.0 | 33.4% | 36.1% | 2.69 |
| World 1 (multiplier sh=0.32) | household_coupled | 0.6 | 8113 | 1.038 | 0.395 (+10.6%) | 0.400 (+18.5%) | 0.99 | 60.3% (59.5 to 61.3) | 60.1% | +0.24 pts | 21.2% | 46.6% | 10.5 | 28.8% | 25.0% | 4.43 |
| World 1 (multiplier sh=0.32) | household_coupled | 0.3 | 4314 | 0.781 | 0.445 (+24.5%) | 0.490 (+44.8%) | 0.91 | 64.1% (63.3 to 64.9) | 63.7% | +0.39 pts | 20.3% | 62.2% | 6.2 | 52.7% | 34.0% | 2.94 |
| World 2b (scene L=10, sh=0.58) | full | 1.0 | 9737 | 1.550 | 0.365 (+0.0%) | 0.257 (+0.0%) | 1.42 | 53.5% (53.1 to 54.1) | 54.6% | -1.06 pts | 21.7% | 16.0% | 21.5 | 6.5% | 14.7% | 9.32 |
| World 2b (scene L=10, sh=0.58) | random | 0.6 | 5871 | 0.920 | 0.352 (-3.7%) | 0.273 (+6.2%) | 1.29 | 63.1% (62.3 to 63.8) | 63.6% | -0.57 pts | 18.8% | 16.1% | 10.9 | 6.1% | 21.6% | 6.39 |
| World 2b (scene L=10, sh=0.58) | random | 0.3 | 2936 | 0.449 | 0.321 (-12.2%) | 0.267 (+3.8%) | 1.20 | 75.3% (74.3 to 76.2) | 75.5% | -0.23 pts | 15.7% | 17.8% | 4.4 | 13.1% | 35.1% | 3.43 |
| World 2b (scene L=10, sh=0.58) | household_infectee | 0.6 | 5789 | 0.929 | 0.339 (-7.1%) | 0.265 (+3.0%) | 1.28 | 63.3% (61.8 to 64.8) | 63.9% | -0.66 pts | 18.3% | 16.5% | 10.7 | 8.4% | 20.2% | 6.38 |
| World 2b (scene L=10, sh=0.58) | household_infectee | 0.3 | 2952 | 0.444 | 0.276 (-24.4%) | 0.196 (-23.7%) | 1.41 | 76.4% (75.0 to 77.9) | 76.8% | -0.33 pts | 14.7% | 14.6% | 4.7 | 13.4% | 35.2% | 3.38 |
| World 2b (scene L=10, sh=0.58) | household_coupled | 0.6 | 5629 | 1.020 | 0.373 (+2.1%) | 0.271 (+5.4%) | 1.38 | 60.5% (59.5 to 61.3) | 61.2% | -0.69 pts | 20.1% | 23.7% | 11.7 | 10.1% | 19.7% | 6.73 |
| World 2b (scene L=10, sh=0.58) | household_coupled | 0.3 | 3038 | 0.621 | 0.408 (+11.7%) | 0.350 (+36.1%) | 1.17 | 68.3% (67.0 to 69.8) | 68.6% | -0.25 pts | 19.3% | 38.4% | 5.2 | 28.7% | 32.1% | 3.83 |
| World 3b paired (events M=30, r=0.1456) | full | 1.0 | 13655 | 1.482 | 0.306 (+0.0%) | 0.157 (+0.0%) | 1.95 | 54.4% (53.7 to 55.2) | 58.3% | -3.90 pts | 16.8% | 21.7% | 25.2 | 2.9% | 91.6% | 1.73 |
| World 3b paired (events M=30, r=0.1456) | random | 0.6 | 8252 | 0.911 | 0.247 (-19.1%) | 0.161 (+2.9%) | 1.53 | 66.5% (65.6 to 67.4) | 68.3% | -1.75 pts | 15.3% | 21.6% | 14.8 | 3.8% | 93.9% | 1.39 |
| World 3b paired (events M=30, r=0.1456) | random | 0.3 | 4111 | 0.444 | 0.181 (-40.8%) | 0.148 (-5.8%) | 1.22 | 79.5% (78.6 to 80.5) | 79.9% | -0.41 pts | 11.6% | 22.2% | 6.7 | 5.2% | 92.9% | 1.26 |
| World 3b paired (events M=30, r=0.1456) | household_infectee | 0.6 | 8132 | 0.883 | 0.229 (-25.2%) | 0.154 (-2.0%) | 1.49 | 68.2% (67.3 to 69.3) | 69.7% | -1.47 pts | 14.2% | 21.6% | 14.6 | 3.0% | 93.8% | 1.43 |
| World 3b paired (events M=30, r=0.1456) | household_infectee | 0.3 | 4110 | 0.436 | 0.175 (-42.6%) | 0.151 (-3.4%) | 1.16 | 80.1% (79.1 to 81.2) | 80.3% | -0.25 pts | 11.2% | 22.3% | 6.6 | 7.4% | 89.6% | 1.32 |
| World 3b paired (events M=30, r=0.1456) | household_coupled | 0.6 | 8159 | 0.992 | 0.360 (+17.7%) | 0.204 (+30.3%) | 1.76 | 59.5% (58.9 to 60.2) | 62.1% | -2.61 pts | 20.7% | 32.3% | 14.7 | 4.8% | 92.1% | 1.61 |
| World 3b paired (events M=30, r=0.1456) | household_coupled | 0.3 | 4261 | 0.698 | 0.465 (+52.0%) | 0.278 (+77.4%) | 1.67 | 63.6% (62.6 to 64.7) | 65.3% | -1.68 pts | 22.4% | 47.4% | 7.6 | 13.5% | 90.8% | 1.43 |
| World 2a (scene L=30, sh=0.70) | full | 1.0 | 8835 | 1.644 | 0.355 (+0.0%) | 0.236 (+0.0%) | 1.50 | 52.8% (52.0 to 53.6) | 54.1% | -1.29 pts | 21.1% | 8.4% | 22.5 | 3.3% | 15.0% | 9.12 |
| World 2a (scene L=30, sh=0.70) | random | 0.6 | 5339 | 0.943 | 0.345 (-3.0%) | 0.230 (-2.6%) | 1.50 | 62.7% (61.9 to 63.5) | 63.5% | -0.84 pts | 18.5% | 8.5% | 11.2 | 3.8% | 20.7% | 6.30 |
| World 2a (scene L=30, sh=0.70) | random | 0.3 | 2586 | 0.484 | 0.307 (-13.5%) | 0.244 (+3.3%) | 1.26 | 74.4% (73.2 to 76.0) | 74.8% | -0.34 pts | 15.9% | 8.9% | 4.5 | 7.5% | 36.5% | 3.48 |
| World 2a (scene L=30, sh=0.70) | household_infectee | 0.6 | 5253 | 0.986 | 0.322 (-9.3%) | 0.223 (-5.7%) | 1.44 | 63.0% (62.1 to 64.0) | 63.7% | -0.66 pts | 18.2% | 7.7% | 11.3 | 3.1% | 20.8% | 6.47 |
| World 2a (scene L=30, sh=0.70) | household_infectee | 0.3 | 2676 | 0.521 | 0.286 (-19.5%) | 0.249 (+5.3%) | 1.15 | 74.1% (72.7 to 75.7) | 74.3% | -0.20 pts | 15.5% | 8.7% | 5.0 | 8.3% | 32.0% | 3.77 |
| World 2a (scene L=30, sh=0.70) | household_coupled | 0.6 | 5136 | 1.016 | 0.349 (-1.6%) | 0.266 (+12.4%) | 1.32 | 61.4% (60.1 to 62.6) | 62.1% | -0.70 pts | 19.2% | 12.6% | 11.2 | 7.1% | 20.9% | 6.48 |
| World 2a (scene L=30, sh=0.70) | household_coupled | 0.3 | 2677 | 0.559 | 0.351 (-1.1%) | 0.262 (+10.9%) | 1.34 | 71.1% (69.4 to 72.9) | 71.6% | -0.44 pts | 17.7% | 24.8% | 4.9 | 17.1% | 34.8% | 3.68 |

## 4. Evaluation of Registered Predictions in Note 61

1. **Prediction (a) — PARTIALLY FAILS (holds for `k_mom` and zero share across all worlds and for `k_ml` in Worlds 1, 2b, and 2a, but fails for `k_ml` in World 3b):**

   - *What holds:* Under random 60% and 30% detection, `k_mom` stays within `6.2%` of its un-thinned value in all worlds (`+4.1%, -5.8%` in World 1; `+6.2%, +3.8%` in World 2b; `+2.9%, -5.8%` in World 3b; `-2.6%, +3.3%` in World 2a), and the observed zero share rises from `52.8%–56.6%` to `74.4%–79.5%` at `p = 0.3`, matching the negative-binomial expectation at `k_ml` and the thinned mean within `0.1` to `0.4` percentage points (`76.2%` vs `76.3%` in World 1; `75.3%` vs `75.5%` in World 2b; `79.5%` vs `79.9%` in World 3b; `74.4%` vs `74.8%` in World 2a). Likewise, `k_ml` stays within the `15%` bound in World 1 (`+2.4%, -1.2%`), World 2b (`-3.7%, -12.2%`), and World 2a (`-3.0%, -13.5%`).

   - *What fails and why:* In **World 3b**, `k_ml` drops from `0.306` to **`0.247` (`-19.1%`)** at `p = 0.6` and **`0.181` (`-40.8%`)** at `p = 0.3`. Because World 3b is a two-component mixture (a near-Poisson background for non-event infectors plus a heavy closed-group event tail) rather than a true negative binomial, its un-thinned distribution has a large deficit of zeros relative to `k_mom` (`54.4%` observed vs `69.8%` NB at `k_mom = 0.157`), which keeps `k_ml` elevated at `0.306`. Random binomial thinning turns `1`s and `2`s in the near-Poisson body into `0`s while large event clusters (`15–28`) still survive as `5–12` offspring, pulling `k_ml` downward toward the thinning-invariant `k_mom` (`0.157`) and compressing `k_ml / k_mom` from `1.95` to `1.53` (`p = 0.6`) and `1.22` (`p = 0.3`).

2. **Prediction (b) — FAILS:**

   - Under **`household_coupled`** (where index cases and infectees use the same per-household detection mask), conditioning on a detected index case means the index case's own household is detected with probability `1` while outside households are detected with probability $p$. As a result, the same-household share of detected infectees **rises** strongly instead of falling: across all detected offspring, from `33.9%` (`p=1.0`) to `46.6%` (`p=0.6`) and `62.2%` (`p=0.3`) in World 1 (`17.8%` to `28.8%` and `52.7%` in top-10 clusters) and from `21.7%` to `32.3%` and `47.4%` in World 3b (`2.9%` to `4.8%` and `13.5%` in top-10 clusters). And in World 3b, keeping `100%` of same-household offspring prevents `k_ml` from dropping, so `k_ml / k_mom` (`1.76` at `0.6`, `1.67` at `0.3`) is `+0.23` and `+0.45` *higher* (not lower) than under random detection (`1.53` and `1.22`).

   - Under **`household_infectee`** (where whole households of infectees vanish with probability $1-p$ independently of index-case detection), every infectee has marginal detection probability $p$, so the overall same-household share is invariant (`33.9%` and `32.4%` in World 1; `21.6%` and `22.3%` in World 3b), while in the top-10 clusters same-household share still increases relative to random detection in World 1 (`22.5%` vs `19.0%` at `0.6`; `33.4%` vs `25.2%` at `0.3`) because surviving households stay intact as a block. Meanwhile, both `k_ml` and `k_mom` fall together (`-10.3%` and `-10.7%` at `0.6`; `-19.8%` and `-24.2%` at `0.3` in World 1), so `k_ml / k_mom` differs from random detection by only `+0.02` (`p=0.6`) and `+0.01` (`p=0.3`) in World 1 and `-0.04` and `-0.06` in World 3b.

3. **Prediction (c) — HOLDS at 60% detection; PARTIALLY FAILS at 30% detection on the fine ordering between Worlds 1 and 2b (while World 3b remains separated by >53 points on venue-day share, and same-household share separates Worlds 1 and 2b):**

   - Note first a typo in Note 61's parenthetical description of the 100%-detection venue-day order: as established in Note 59 and Note 60 Section 4, at 100% detection the largest-venue-day share of top-10 clusters is ordered **`world 2b (14.7%) < world 1 (20.3%) < world 3b (91.6%)`** (not `world 1 < world 3b < world 2b`).

   - At **60% detection (`p = 0.6`)**, both metrics preserve their exact 100%-detection order across all three schemes:

     - Zero gap (`observed - NB at k_ml`): `world 3b (-1.75 pts) < world 2b (-0.56 pts) < world 1 (+0.05 pts)` under `random` (`-1.53 < -0.67 < +0.01` under `household_infectee`; `-2.57 < -0.68 < +0.15` under `household_coupled`).

     - Top-10 largest-venue-day share: `world 2b (21.6%) < world 1 (24.7%) < world 3b (93.9%)` under `random` (`20.2% < 25.9% < 93.8%` under `household_infectee`; `19.7% < 25.0% < 92.1%` under `household_coupled`).

   - At **30% detection (`p = 0.3`)**:

     - The zero gap shrinks by ~10x (because `75%–80%` of index cases have 0 detected offspring at `R ≈ 0.44`): it still orders `world 3b (-0.39 pts) < world 2b (-0.23 pts) < world 1 (-0.09 pts)` under `random` and `-1.69 < -0.28 < +0.36` pts under `household_coupled`, but under `household_infectee` Worlds 3b (`-0.28 pts`) and 2b (`-0.33 pts`) are within `0.05` percentage points and swap.

     - On top-10 largest-venue-day share, **World 3b (`92.9%` random, `89.6%` `household_infectee`, `90.8%` `household_coupled`) remains >53 percentage points above both World 1 and World 2b**, effortlessly identifying closed-group events at 30% detection. However, because top-10 clusters in Worlds 1 and 2b shrink from `17–22` offspring to `6–8` detected offspring at `p = 0.3`, the discrete ratio `max(venue_day) / len(kids)` rises to `~33%–36%` in both (`33.4%` in World 1 vs `35.1%` in World 2b under `random`), erasing the small 5-point gap between Worlds 1 and 2b on venue-day share.

     - Instead, **same-household share** provides the thinning-robust separator between World 1 and World 2b at `p = 0.3`: in top-10 clusters, World 1 has **`25.2%`** (`random`), **`33.4%`** (`household_infectee`), and **`52.7%`** (`household_coupled`) same-household share, against **`13.1%`**, **`13.4%`**, and **`28.7%`** in World 2b (and `7.5%`, `8.3%`, `17.1%` in World 2a).
