# ACT-049 note 74a: pre-run review of note 73 (round 15 instructions)

23 October 2026. Pre-run review of `73_round15_instructions_parent_child_and_density.md`, written before launching Run C or Run D.

## 1. Summary of review and feasibility

All runs requested in Note 73 (Run C across the three B1 cells to day 42, and Run D at $\alpha = 0.5$ and $\alpha = 0$ across all three B1 cells) are feasible without any C++ code changes using `build_r10/panSim` and without dropping any cell. With 4 concurrent GPU jobs (`PANSIM_JOBS=4`), Run C (3 cells × 12 replicates × 6 weeks) takes ~5 minutes and Run D (6 cells calibrated on `76001..76006` and run on `77001..77012` for 4 weeks) takes ~20–25 minutes, so the full round will be completed in full.

Below are five technical points and clarifications identified by inspecting `include/policies/infectionPolicies.h` and checking the existing B1 traces from Round 14 before running.

---

## 2. Five technical points on Note 73

### Point 1 (Run C): 6-week (`-w 6`, day 42) horizon and `trace.tsv` overwrite on reinfection
- In `panSim`, `-w 4` runs 28 days (`timestamp // 144` in `0..27`) and `-w 6` runs 42 days (`timestamp // 144` in `0..41`). Because the simulator steps forward causally, the first 28 days of each replicate in a `-w 6` run are step-by-step identical to the `-w 4` run of Round 14 (`r14_b1final_*`).
- **However**, `trace.tsv` (`writeInfectionTrace()` in `include/policies/infectionPolicies.h`, line 1089) is written at the **end** of the simulation from `realThis->agents->agentStats[agent]`, which stores a single struct per agent holding its **most recent** infection (`stat.infectedTimestamp`, `stat.infectorId`, `stat.infectedLocation`, with `stat.infectedCount` incremented on each episode). If an agent first infected on days `0..27` recovers, wanes back to susceptible, and gets **reinfected** on days `28..41`, its row in the week-6 `trace.tsv` is overwritten by the later episode (`infectedCount >= 2`).
- By contrast, `--episodeTrace <path>` (`writeEpisodes()`, line 924) streams every regular-location infection episode at the exact step it occurs, and `--eventGroupLog <path>` (`runGroupEvents()`, line 1310) streams every closed-group event infection to `<path>.infections` at the exact step it occurs.
- Furthermore, we already have the exact 4-week (`-w 4`) `trace.tsv` and `events.tsv.infections` for all 12 replicates of B1 in `superspreader/study/results/round14/cal/r14_b1final_{w1,w2b,w3b}/`.
- **How we handle this cleanly:**
  1. We run all three B1 cells to day 42 (`-w 6`) with `--infectionTrace`, `--episodeTrace`, `--eventGroupLog` (for `w3b`), and `--hviDump` (for `w2b`).
  2. For infections occurring on days `0..27`, we lock each agent's record to the Round-14 4-week `trace.tsv` (which has zero post-day-27 overwrite), add day-28 (`infection_day == 28`) infections from the 6-week run, and count `offspring_14d` and `offspring_total` up to day 42 using all infections across days `1..41` from the combined 4-week + 6-week infection stream (`episodes.tsv` + `events.tsv.infections` + 6-week `trace.tsv`).
  3. This guarantees that the per-replicate offspring histograms of the index cases (infected on days `1..10`, whose 14-day window ends on days `15..24 <= 27`) reproduce `69_b_replicate_histograms.csv` **100% identically** in every replicate and every bin. In `74_round15_results.md`, we also report the small number of index cases (`~0.1%–0.3%`) that differ if one reads the week-6 `trace.tsv` in isolation without locking days `0..27` to the week-4 `trace.tsv`.

### Point 2 (Run C): Columns of `74_c_infections_<world>_<block>.csv` and `< 2 MB` file splitting
- **Columns provided directly by `trace.tsv` / `episodes.tsv`:**
  - `agent_id` (`agent`), `infector_id` (`infector`, empty `""` when `infector == 4294967295` for day-0 seeds), `infection_day` (`timestamp // 144`), `place_type` (`locType`), `location_id` (`location`).
- **Columns constructed or joined from auxiliary files:**
  - `venue_day_id`: `f"{location_id}_{infection_day}"` (for non-seed infections; empty `""` for day-0 seeded infections).
  - `same_household_as_infector`: `1` if `infector_id != ""` and `home[agent_id] >= 0` and `home[agent_id] == home[infector_id]` (using the agent's home location of type `2` from `inputRealExample/agents2.json`), else `0`.
  - `event_flag`: `1` if the infection is recorded in `events.tsv.infections` (closed-group event in World 3b), else `0`.
  - `offspring_14d`: count of infections in the 6-week run (`infection_day <= 41`) whose `infector_id == agent_id` and whose `infection_day <= this_agent.infection_day + 14`.
  - `offspring_total`: count of all infections in the 6-week run (`infection_day <= 41`) whose `infector_id == agent_id`.
  - `agent_type`: `typeID` (`1..8`) from `inputRealExample/agents2.json` (the exact occupation/age-group type used in the top-1% profiles).
  - `agent_class_flag`: `1` or `0` from column 5 of `<run_dir>/hvi.csv` in World 2b; empty `""` in Worlds 1 and 3b as instructed.
- **File splitting (`<= 2 MB`):** Each cell has ~75,000–78,000 infections up to day 28 across 12 replicates (~4.5 MB per world). Splitting each world into **3 blocks of 4 replicates** (`reps01_04`, `reps05_08`, `reps09_12`) produces 9 files (`74_c_infections_<world>_reps01_04.csv`, etc.) of **~1.5 MB each**, all safely below the 2 MB limit.

### Point 3 (Run C): 14-day filter on children of index cases and the Lloyd-Smith 99th-percentile Poisson threshold
- **Children of index cases:** An index case (parent $p$, `1 <= infection_day <= 10`) occasionally (`< 0.8%` of secondary infections, when hospitalized) causes an infection more than 14 days after its own infection (`15 <= child_day - parent_day <= 24`). Under the standard study definition (`offspring_14d`), a parent's offspring are infections within 14 days (`child_day <= parent_day + 14`). We report all parent–child statistics both for **14-day children** (`child_day <= parent_day + 14`, where the number of children of each parent $p$ equals $p$'s `offspring_14d`) and for **all day-$\le 28$ children** (`child_day <= 28`), which agree closely.
- **Superspreader threshold (Run C item 2):** For a Poisson distribution with mean equal to the cell's mean index-case offspring $R$ (`1.407` in World 1, `1.573` in World 2b, `1.451` in World 3b), the 99th percentile $q_{0.99}(\text{Poisson}(R))$ is **`5`** in all three worlds ($\text{CDF}(4) = 0.978\text{–}0.985 < 0.99 < \text{CDF}(5) = 0.994\text{–}0.997$). Thus *"above the 99th percentile"* means **`offspring_14d > 5` (`>= 6`)**. (We also report `>= 5` beside `> 5` for completeness.)

### Point 4 (Run C Item 6 & Prediction C(d)): Generational distinction in the backward-tracing sibling identity
- Note 73 derives the moment-based backward-to-forward tracing yield ratio from the index-case offspring distribution $Z$ (mean $R = E[Z]$):
  $$\frac{1 + E[Z(Z-1)]/E[Z]}{E[Z]} = \frac{1}{R} + \frac{E[Z(Z-1)]}{R^2} = \frac{1}{R} + 1 + \frac{1}{k_{\text{mom}}},$$
  which gives **`5.854, 7.504, 8.263`** (`5.9, 7.5, 8.3`) for the B1 cells of Worlds 1, 2b, and 3b, and registers Prediction C(d): *"In all three worlds the mean sibling count plus one divided by the mean own offspring is within 5% of the moment-based ratio above (an identity up to eligibility and depletion; a failure means the export is wrong)."*
- A pre-run check on the Round-14 B1 traces reveals an important generational distinction between two ways of reading "sibling count":
  1. **Backward from the children $c$ of the index cases ($G_2 \to G_1$):** Each index case $p \in G_1$ (infected on days 1–10) has $Z_p = \text{offspring\_14d}(p)$ children, and each of those $Z_p$ children has $Z_p - 1$ siblings. Averaged over all children of index cases, $1 + \overline{\text{siblings}(c)} = 1 + \frac{\sum_p Z_p(Z_p - 1)}{\sum_p Z_p}$, so dividing by the index-case mean $R = \overline{Z_p}$ gives **`5.854, 7.504, 8.263`** — an **exact algebraic identity (`0.00%` difference)** with the moment-based formula! (Dividing instead by the children's own mean offspring $\overline{Z_c}$ gives the ratio adjusted only for depletion between $G_1$ and $G_2$.)
  2. **Backward from the days 1–10 index cases $i \in G_1$ themselves to *their* infectors $\text{inf}(i) \in G_0 \cup G_1$:** Most infectors of days 1–10 index cases are the **day-0 initial seeds ($G_0$)**! Because day-0 seeds are placed uniformly at random across the population (`~10%` in the risky-venue class in World 2b), whereas by days 1–10 infection has strongly selected for the risky-venue class (`~58%` of days 1–10 index cases in World 2b are class members!), the uniformly seeded day-0 cohort has a substantially lower offspring variance than the days 1–10 index-case cohort in World 2b. Consequently, $(1 + \overline{\text{siblings}(i)}) / \overline{Z_i}$ evaluated on days 1–10 index cases looking back to day-0 seeds is **`5.487` (`-6.3%` vs `5.854`) in World 1, `6.077` (`-19.0%` vs `7.504`) in World 2b, and `8.888` (`+7.6%` vs `8.263`) in World 3b**.
- This difference in (2) is a genuine physical difference between uniform day-0 seeding ($G_0$) and transmission-selected index cases ($G_1$), **not** an export error. We will report both (1) the child-of-index-case sibling ratio ($G_2 \to G_1$) and (2) the index-case-to-seed sibling ratio ($G_1 \to G_0$) in `74_c_replicate_summary.csv` and `74_round15_results.md`.

### Point 5 (Run D): How World 3b's closed-group event kernel treats $\alpha$ (`--densityExponent`) and how busiest-10% venue share is defined
- **Event kernel in C++ (`include/policies/infectionPolicies.h`, lines 1209–1211):**
  In `runGroupEvents`, the closed-group event hazard uses **both** the background coefficient `this->k` ($k_0$) and `densityExponent` ($\alpha$) applied to the sampled group size `group = min(30, present)`:
  $$\text{density}_{\text{event}} = \frac{\text{infectiousSum}}{\text{group}^\alpha}, \qquad p_{\text{event}} = 1 - \exp\!\left(-k_0 \cdot \frac{\text{infectiousSum}}{\text{group}^\alpha} \cdot \text{locInfectiousness} \cdot \text{eventFactor} \cdot \text{seasonality} \cdot 120\right).$$
  Because regular venues in the city reach occupancies $N \sim 100\text{–}1,000$ (so lowering $\alpha$ from $1$ to $0$ multiplies their hazard by $N^{1-\alpha} \sim 100\text{–}1,000$), whereas closed-group events are capped at $\text{group} \le 30$ (so lowering $\alpha$ to $0$ multiplies their hazard by at most $30$), recalibrating $k_0$ downward by `~100x` at $\alpha = 0$ to match day-28 cumulative infections reduces $k_0 \cdot \text{group}^{1-\alpha}$ inside closed-group events relative to large regular venues. As instructed, we keep the C++ code unchanged and report the resulting shift in `event_offspring_share` and `k_ml`.
- **Share of infections in the busiest 10% of venues (by infections):**
  Because `locations1.json` has `81,471` locations (`22,068` non-home locations) while a 4-week replicate has `~6,200` infections across at most `~2,500` distinct locations (`< 3.5%` of all locations in the city), the top 10% (`8,147`) of *all* city locations would trivially contain `100%` of infections in every cell. To provide the meaningful concentration measure, we compute and report three definitions side by side:
  1. **Primary (`top10pct_active_venues_share_rep_mean`):** Share of days 1–28 non-seed infections occurring in the busiest 10% of **infection-producing venues** (`loc` with $\ge 1$ infection in that replicate), averaged over replicates (at $\alpha = 1$: `42.3%` in World 1, `57.0%` in World 2b, `64.3%` in World 3b).
  2. **Pooled active venues (`top10pct_active_venues_share_pooled`):** Share of pooled days 1–28 infections in the busiest 10% of venues with $\ge 1$ infection across all 12 replicates (`59.3%`, `82.7%`, `75.8%` at $\alpha = 1$).
  3. **Non-home active venues (`top10pct_nonhome_active_venues_share_rep_mean`):** Share of days 1–28 non-home infections (`locType != 2`) in the busiest 10% of non-home venues with $\ge 1$ infection (`47.4%`, `53.3%`, `48.4%` at $\alpha = 1$).

---

## 3. Registered predictions (recorded verbatim before running)

### Run C predictions
- **C(a):** World 1: Pearson correlation of parent and child `offspring_14d` is between `-0.05` and `+0.05`, and the ratio of observed to expected superspreader pairs is between `0.7` and `1.4`.
- **C(b):** World 2b: Pearson correlation is at least `+0.03`, and the superspreader-pair ratio is above `1.2` and above that of World 1.
- **C(c):** World 3b: Pearson correlation is at least `0.02` above that of World 1.
- **C(d):** In all three worlds, the mean sibling count plus one divided by the mean own offspring is within `5%` of the moment-based ratio (`5.85, 7.50, 8.26`).
- **C(e):** The day-matched ratio of children's `offspring_14d` to the expectation is between `0.85` and `1.15` for children of parents with at most one offspring (`parent offspring_14d == 1`) in all three worlds.

### Run D predictions
- **D(a):** World 1 at $\alpha = 0$: likelihood $k$ (`k_ml`) between `0.15` and `0.23` (composition rule with Table 5.1b occupancy source predicts `~0.18`).
- **D(b):** World 2b at $\alpha = 0$: likelihood $k$ (`k_ml`) lower than at $\alpha = 1$ (`0.270`) by between `15%` and `45%` (i.e., between `0.149` and `0.230`).
- **D(c):** World 3b at $\alpha = 0$: likelihood $k$ (`k_ml`) within `20%` of its $\alpha = 1$ value (`0.248`, i.e., between `0.198` and `0.298`).
- **D(d):** At $\alpha = 0$, the largest-venue-day share of the ten largest clusters stays at `80%` or more in World 3b, and the same-household share of the ten largest clusters of World 1 stays above that of Worlds 2b and 3b.
- **D(e):** The share of infections in the busiest 10% of venues rises with falling $\alpha$ in every world, and at $\alpha = 0$ it exceeds `50%` in at least one world.
