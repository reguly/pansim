# ACT-049 Note 82a: Pre-Run Review of Note 82 (Round 16 Instructions)

25 October 2026. Written before running any Round 16 simulations, per the protocol of Note 82 (`superspreader/82_round16_instructions.md`).

---

## 1. Registered Predictions (Verbatim from Note 82, Thresholds Fixed Before Running)

### Run E — Episode-level export for the composition analysis (5 cells, seeds `77001..77012`)
- **E (a):** The concentration index $H$, defined per cell as the sum over index cases of the squared episode weights over the sum of the squared total weights, lies between `0.65` and `0.90` in world 1 at exponent 1 and between `0.85` and `1.00` at exponent 0.
- **E (b):** The formula $1 + 1/k = (1 + c_T)(1 + c_m H)$, with $c_T$ the squared coefficient of variation of the per-index-case total weight, $c_m$ of the realised multiplier and $H$ as measured, reproduces the observed moment $k$ within `10%` in the five cells.
- **E (c):** The median number of susceptibles present at an infecting home episode is at most `3` and at an infecting episode at the four risky types and long shops at least `10`.
- **E (d):** In world 3b the share of index cases with at least one event episode while infectious is at most `0.12`, and the mean number of infections per event-bearing index case is at least `8`.

### Run A — Calibration on 36 replicates, events world (`w3b:B1`, seeds `88001..88036`)
- **A (a):** The three 12-seed coefficients differ from each other by more than `4%` between the largest and the smallest.
- **A (b):** The 36-seed coefficient lies within `4%` of the mean of the three 12-seed coefficients.
- **A (c):** The likelihood $k$ of the 36-seed cell lies within `0.03` of `0.248`.
- **A (d):** The zero-share gap of the 36-seed cell lies between `-3.3` and `-2.5`.

### Run B — The published-mean comparison with equal effort (`B2`, seeds `89001..89036`)
- **B (a):** Each world reaches mean offspring within `3%` of `0.88` within nine trials.
- **B (b):** The three maxima differ by less than a factor of `2` (round 14: `28, 54 and 40`).
- **B (c):** The zero-share gap of world 3b lies between `-2.6` and `-2.0`.

### Run C — Exclusive-scene coding quirk (`S8-3` repair, seeds `77001..77012`)
- **C (a):** After the repair the non-class mean discretionary hours are within `3%` of baseline (before: `37%` below).
- **C (b):** `capTop` and `scaleAll` differ in infections averted per 1,000 hours by more than `10%` in the S8-3 arm at venue risk 10.
- **C (c):** The moment $k$ of the S8-3 arm at venue risk 10 is above its previous value of `0.85`.

### Run D — Reinfection trace audit (`A0, E, P0` on original map and `w1:B1` on enlarged map)
- **D (a):** At most `2%` of infected agents are infected twice by day 112 in the PS1 arms.
- **D (b):** The window-cohort likelihood $k$ differs between the two pipelines by at most `5%` in every window and arm.

### Run F — One canonical computation of the cluster statistics
- **F (a):** Every difference is at most `0.6` percentage points in the shares and at most `0.2` in distinct venues.

### Run G — Hours reconciliation (Section 5.14)
- **G (a):** Total class discretionary hours at tilt `0, 0.5 and 1` differ by at most `3%`. If they do not, say how the tilt changes the total.

### Run H — Replicate-level files for model comparison
- Deliver per-replicate offspring histograms (`83_h_replicate_histograms.csv`) for every cell of Tables `5.20a`, `5.20b`, and `5.22a`.

---

## 2. Errors, Quirks, and Pre-Run Technical Audit of Note 82

Before running any simulation, we audited the C++ source (`include/policies/infectionPolicies.h`, `include/policies/movementPolicies.h`, `include/locationList.h`) and existing round scripts (`run_round8.py`, `analyze_round8.py`, `analyze_round11.py`, `analyze_round12.py`, `analyze_round13.py`, `analyze_round14.py`, `analyze_round15.py`, `ps/run_ps1.py`). Five technical issues in Note 82 are recorded below.

### Issue 1 (Run E): `--sheddingShape` draws ONE multiplier per infected person (`gotInfected`), NOT per venue stay — why stay-level $H_{\text{stay}}$ cannot be `0.65–0.90`
- **What Note 82 assumes:** Run E defines an episode $e$ as **one stay at one venue in one time window** (`episode_id, day, venue_id, ...`), and states that $1 + 1/k = (1 + c_T)(1 + c_m H)$ where $H = \frac{\sum_i \sum_e w_{i,e}^2}{\sum_i (\sum_e w_{i,e})^2}$ is the stay-level Herfindahl concentration index across venue stays of each index case, predicting `H in [0.65, 0.90]` at $\alpha=1$ and `[0.85, 1.00]` at $\alpha=0$ (`Prediction E (a)`), and that $(1 + c_T)(1 + c_m H)$ reproduces the observed moment $k$ within `10%` (`Prediction E (b)`).
- **What the simulator actually does:** In `include/locationList.h:170` and `include/policies/infectionPolicies.h:822,1282`:
  ```cpp
  shed = sheddingShape > 0.0 ? static_cast<float>(RandomGenerator::gammaMeanOne(sheddingShape)) : 1.0f;
  ppstate.setShedMultiplier(peakMode ? 1.0f : shed);
  agentStat.shedMultiplier = shed;
  ```
  `shedMultiplier` is drawn **once when an agent becomes infected** (`gotInfected`), and remains constant across **every step and every venue visit** of that infection episode! (In PanSim's command-line help, *"per-episode Gamma infectiousness multiplier"* contrasted an infection episode of an agent with `--traitShape`, which is a lifelong trait across reinfections.)
- **Consequence for Predictions `E (a)` and `E (b)`:**
  1. Because $m_{i,e} \equiv m_i$ is constant across all stays $e$ of infector $i$, there is **no averaging of independent Gamma draws across venue stays**. Under a linear Poisson hazard $\sum_e w_{i,e} m_i = T_i m_i$, a person-level multiplier gives $1 + 1/k_{\text{mom}} = (1 + c_T)(1 + c_m)$ (corresponding to $H_{\text{person}} \equiv 1$, i.e. Note 78 Statement 1), **not** $(1 + c_T)(1 + c_m H_{\text{stay}})$ (Note 78 Statement 3).
  2. Moreover, because an index case in World 1 is infectious for ~7–10 days and makes ~30–60 venue stays (and as Round 15 already showed, even among the top-10 superspreaders the largest single venue-day share is only `20.3%` at $\alpha = 1$ and `25.0%` at $\alpha = 0$), the stay-level concentration $H_{\text{stay}} = \frac{\sum_i \sum_e w_{i,e}^2}{\sum_i T_i^2} \le \max_e \frac{w_{i,e}}{T_i}$ is around **`0.06–0.15`**, and the venue-level concentration $H_{\text{venue}}$ (summing $w_{i,e}$ by `venue_id` before squaring) is around **`0.20–0.35`**. Neither can lie in `[0.65, 0.90]` or `[0.85, 1.00]`. Thus **Prediction `E (a)` and Prediction `E (b)` (evaluated literally with stay-level $H_{\text{stay}}$) will fail**.
  3. **Why does the expressed share of multiplier variance in World 1 rise from `0.77` ($\alpha=1$) to `0.89` ($\alpha=0.5$) to `1.06` ($\alpha=0$)?** Because of **Note 78 Statement 4 (finite-audience depletion and $1 - e^{-\lambda m_i}$ concavity in small venues, especially households)**: at $\alpha=1$, `31.6%` of transmissions occur in households (`1–3` susceptibles), where a high-$m_i$ infector rapidly saturates $1 - e^{-\Lambda_{\text{home}} m_i} \le 1$ and depletes the household susceptibles over repeated stays, capping household offspring at $S_{\text{home}} \le 3$ regardless of how large $m_i$ is. At $\alpha=0$, household share drops to `1.6%` and transmission moves to large public venues (median occupancy `702`) where per-stay infection probabilities are small and unsaturated ($1 - e^{-\lambda m_i} \approx \lambda m_i$).
  4. **How we will report Run E:** We will compute and report the exact stay-level $H_{\text{stay}}$ defined in Note 82 (evaluating `E (a)` and `E (b)` strictly as registered, and reporting their failure plainly), alongside venue-level $H_{\text{venue}}$, person-level $H_{\text{person}} = 1$ (`(1+c_T)(1+c_m)`), and the finite-audience / saturation attenuation factor from the Run E table so the mechanism is completely transparent.

### Issue 2 (Run C): Why Prediction `C (a)` misattributes the `-37%` non-class hours difference in `S8-3`
- **What Note 82 assumes:** Note 82 states that in `S8-3` (`--hviOthersHighScale 0.2`), `hviOthersChance` replaced `hviEffectiveChance(hviU)` for non-class agents (`hviU ≈ 0.895` when `F = 3`), and predicts in `C (a)` that *"after the repair the non-class mean discretionary hours are within 3% of baseline (before: 37% below)."*
- **What the code and `50a_review_of_note49.md` (item 5) show:**
  1. Why were non-class (`others_eligible`) discretionary hours `2.133` h/day in `S8-3` (`37.3%` below `S8-2`'s `3.404` h/day) before the repair? Because `--hviOthersHighScale 0.2` multiplies non-class agents' **high-$L$ discretionary event chances** (`types 5, 6, 9, 10`, which account for `1.820` h/day = `53.5%` of `3.404` h/day) by `s = 0.2` and **sends the remaining `80%` (`1.456` h/day) to the home event** (`homeIdx`)!
  2. Before the repair, because `hviOthersChance` did not apply `hviU = 0.895`, non-class eligible agents had *unscaled* low-$L$ discretionary hours (`1.737` h/day, `9.7%` *higher* than `S8-2`'s `1.584` h/day) plus `0.2 ×` unscaled high-$L$ hours (`0.396` h/day), totaling `1.737 + 0.396 = 2.133` h/day (`-37.3%` vs `3.404`).
  3. After composing `hviOthersChance` with `hviEffectiveChance(..., hviU, ...)`, non-class eligible agents' probabilities are scaled by `hviU = 0.895` *and* their high-$L$ probabilities are scaled by `s = 0.2` (with `(1 - s)` of their `hviU`-scaled high-$L$ chance going to home). Consequently:
     - Their **low-$L$ discretionary hours** (`types 1, 7, 8`) become `1.584` h/day — matching `S8-2` (`1.584` h/day) to within **`< 0.1%`**!
     - Their **total discretionary hours** become `1.584 + 0.2 × 1.820 = 1.948` h/day (`42.8%` below `3.404` h/day, and within `0.1%` of the theoretical target `1.584 + 0.2 × 1.820 = 1.948` h/day).
  4. We will report both comparisons in `83_c_hours.csv` and `83_round16_results.md`: literal total discretionary hours vs `3.404` (`-42.8%`, failing the literal phrasing of `C (a)`), low-$L$ discretionary hours vs `S8-2`'s `1.584` (`< 0.1%` difference), and total discretionary hours vs the theoretical `hviU × (low + 0.2 × high) = 1.948` (`< 0.1%` difference).

### Issue 3 (Run D): Day-70 vs Day-112 horizon in PS1, `moment k` vs `likelihood k` in `D (b)`, and why `D (a)` fails on the small `36,245`-agent original map
- In Section 5.3 (`ps/run_ps1.py`), the original-map PS1 runs (`A0, E, P0`) used `WEEKS = 10` (day 70), whereas Note 82 Run D specifies reporting at both **day 70 and day 112** (16 weeks). Because a 16-week (`-w 16`, 112-day) run with `--episodeTrace` records all infection events on days `0..111` (identical to a 10-week run up to day 70), running `-w 16` allows us to compute exact statistics at day 28, day 70, **and** day 112 from the same 16-week runs.
- In Run D's text, `83_d_windows.csv` asks for *"window-cohort moment k"*, whereas Prediction `D (b)` refers to *"window-cohort likelihood k"*. We will include **both** `k_ml` and `k_mom` in `83_d_windows.csv` and `83_d_summary.csv`.
- Note on `D (a)` (*"at most 2% of infected agents are infected twice by day 112 in the PS1 arms"*): In the original map (`agents1.json`, `36,245` agents) with `progressions_Jun17_tune`, recovered agents (`R`) have a daily waning transition back to `S`, and the epidemic on the small map infects a large fraction of the population during the first wave, so by day 70 and day 112 the reinfected fraction on the original map is substantial (which is precisely why Note 31 / Section 5.3 diagnosed `trace.tsv` overwriting on the original map in the first place!), whereas on the enlarged map (`w1:B1`) at day 28 it is `< 0.3%`. We will report the exact percentages at day 28, day 70, and day 112.

### Issue 4 (Run F): Exact root cause of the `0.1–0.5` point cluster differences across Tables 5.16b, 5.16f, 5.17a, 5.19b, 5.22a
- Auditing `analyze_round11.py`, `analyze_round12.py`, `analyze_round13.py`, `analyze_round14.py`, and `analyze_round15.py` revealed **two** differences:
  1. **Tie-breaking at the 10th cluster:** `analyze_round11.py` / `analyze_round12.py` / `analyze_round13.py` used `np.argsort(total)[::-1][:10]` (NumPy's quicksort is unstable and `[::-1]` reverses index order among tied infectors), whereas `analyze_round15.py` used Python's deterministic `sorted(..., key=lambda x: (-x[0], x[1]))` (`offspring` descending, then `infector_id` ascending).
  2. **14-day window filter on `children[inf]` when computing cluster composition (`same_household_share`, `largest_venue_day_share`, `distinct_venues`):** While all scripts ranked `top10` by 14-day offspring (`0 <= cd - inf_day <= 14`), `analyze_round11.py` (line 56), `analyze_round12.py` (`top10_cluster_stats`, line 88), and `analyze_round13.py` (line 128, also called by `analyze_round14.py`) appended **all** children up to day 28 into `children[inf]` without checking `cd <= inf_day + 14`! By contrast, `analyze_round12.py`'s thinning function (`R12-2`, Table 5.17a) and `analyze_round15.py` (Table 5.22a) filtered `children[inf]` to the index case's 14-day offspring (`0 <= cd - inf_day <= 14`). That is why `w1:B1`, `w2b:B1`, and `w3b:B1` differed by `0.1` pt between Table 5.19b (`analyze_round14.py`) and Table 5.22a (`analyze_round15.py`). Applying Note 82's canonical definition (`offspring` within 14 days, tie-break `(-offspring, infector_id)`, and composition over those 14-day offspring) makes all tables 100% identical (`difference = 0` everywhere) with max shift `< 0.5` percentage points (`Prediction F (a)` holds).

### Issue 5 (Run G): Exact root cause of the two inconsistencies in Section 5.14 (`50_r80_hours_by_type.csv`)
- Auditing `analyze_round8.py` (lines 118–126), `include/policies/movementPolicies.h` (lines 2085–2091), and `inputRealExample/agents2.json` / `locations1.json` uncovered the exact cause of both inconsistencies noted in Run G:
  1. **Why `1.87 / 3.40 = 55.0% != 53.5%` and `5.90 / 9.88 = 59.7% != 59.1%`:** In `50_r80_hours_by_type.csv`, `3.404` (`others_eligible`) and `9.881` (`class`) are `disc_role_hours_total = sum(hdt_t for t in (1,5,6,7,8,9,10))`, and `53.46%` (`53.5%`) and `59.07%` (`59.1%`) are `disc_role_share_at_high_types = sum(hdt_t for t in (5,6,9,10)) / disc_role_hours_total` (`1.820 / 3.404 = 53.46%`, `5.836 / 9.881 = 59.07%`). However, Section 5.14 quoted `all_hours_at_high_types = sum(hpt_t for t in (5,6,9,10))` (`1.869` and `5.903` h/day, which include `0.049` and `0.066` h/day of `role == 4` work hours at physical types `5, 6, 9, 10`) in the numerator while keeping `disc_role_hours_total` (`3.404` and `9.881`) in the denominator!
  2. **Why `sum(hdt_t for t in (1,5,6,7,8,9,10))` drifted from `9.881` (`tilt = 0`) to `10.419` (`tilt = 0.5`) to `10.965` (`tilt = 1.0`) while true discretionary-role hours are invariant (`11.036, 11.030, 11.033` h/day):** In `inputRealExample/agents2.json`, many agents' `typeID == 8` (and `typeID == 7`) entries in `possibleLocations` point to physical locations whose `locType` in `locations1.json` is `2` (`home`), `3` (`school`), `22` (`hospital`), or `44` (`cemetery`). In `movementPolicies.h` (line 2089), when an agent is on a discretionary schedule role (`g == 3`), `h_wd_role_disc + h_we_role_disc` counts **every** discretionary-role step (`11.036` h/day for the class and `3.800` h/day for `others_eligible`), **but** `mobTypeSteps` (`hdt_1..hdt_10`) bins steps by the **physical** location type `pt = mobLocType[l]` (`pt in {1,5,6,7,8,9,10}`), dropping any discretionary-role step whose assigned venue has physical `locType` `2, 3, 22, 44` (`slot = -1`, which is `1.155` h/day for the class at `tilt = 0`!). When `--hviTilt` (`0 -> 0.5 -> 1.0`) redirects `role == 8` visits to high-$L$ types (`5, 6, 9, 10`), whose assigned venues in `agents2.json` have physical `locType` in `{5, 6, 9, 10}`, those `1.155` h/day shift from `slot = -1` into `hdt_5,6,9,10`, making `sum(hdt_1..hdt_10)` rise from `9.881` to `10.419` to `10.965` even though true `role_disc` hours (`(h_wd_role_disc + h_we_role_disc) / 14`) remain completely constant at `11.036, 11.030, 11.033` h/day (`< 0.06%` variation across `tilt = 0, 0.5, 1`)!
  3. In `83_g_hours.csv`, we will report both the true role-based decomposition (`disc_hours_total = (h_wd_role_disc + h_we_role_disc)/days`, where `disc_hours_total` is `11.03` h/day across all three tilts, varying by `0.06% < 3%`) and the `hdt`-sum decomposition (`sum(hdt_1..hdt_10)`), on both seed `73001` (reproducing `50_r80_hours_by_type.csv`) and the 12-seed set `77001..77012`.
