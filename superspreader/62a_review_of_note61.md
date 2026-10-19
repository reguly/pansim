# 62a. Pre-Run Review of Note 60 and Note 61 (Round 12 Instructions)

## 1. Context & Verification of Note 60

Note 60 (`60_reading_of_59_round11_results.md`) and its accompanying tables (`60_ratio_sample_size.csv`, `60_thinning_fingerprints.csv`) establish three results from Round 11 (`59_*`):

1. **World 3b (`r67_M30` from Round 6) restores the third world** at target dispersion (`k_ml = 0.330`, `k_mom = 0.152`, `k_ml / k_mom = 2.177`, observed zero share `52.3%`, 80% share `18.1%`, `event_offspring_share = 61.7%`). However, it was run in Round 6 on seeds `68101..68112` rather than the common seeds `77001..77012` used for Worlds 1, 2a, and 2b.
2. **Closed-group event rate semantics discrepancy:** In `59_round11_results.md`, the prose stated that `--eventRate 0.1456` means *"14.6% of agents attend a closed group every day"*, whereas `59_r111_worlds.csv` recorded `events_total = 83,086` across 12 replicates × 28 days (`247.3` events/day). At a cap of `M = 30` attendees per event, `247.3 × 30 = 7,418` person-attendances/day is at most `4.15%` of the `178,746` agents/day.
3. **Why `k_ml / k_mom` differs across the three worlds:** World 3b (`2.18`) has a much higher ratio of likelihood $k$ to moment $k$ than World 1 (`1.12`) or World 2b (`1.44`) because closed-group events leave the body of the offspring distribution near-Poisson/moderate-NB (index cases who never attend an event while infectious have a low zero share of `52.3%`, `3.7` percentage points below the NB zero expectation `56.0%` at `k_ml = 0.330`) while adding a heavy upper tail (`max = 31`, `p99 = 14`, 80% share `18.1%`) that inflates sample variance and depresses `k_mom` (`0.152`) relative to `k_ml` (`0.330`).

---

## 2. Exact C++ Semantics of `--eventRate` (Pre-Run Inspection for R12-1 Item 2)

Before running any simulation, we inspected `include/locationList.h` (`updateDailyEvents`) and `include/policies/infectionPolicies.h` (`prepareGroupEvents` and `runGroupEvents`, lines 1118–1320):

- **`--eventRate 0.1456` is a daily Bernoulli probability per eligible venue, NOT per agent.**
  - At the start of each simulation day, `updateDailyEvents(day)` iterates over all locations whose type is in `--eventTypes 5,8` (type `5` = restaurant/cafe/bar, type `8` = long-stay shopping/service venue). In `locations1.json`, there are ~1,700 such venues (`1,700 × 0.1456 ≈ 247.3` venues selected per day).
  - In `prepareGroupEvents`, each selected venue is assigned a single uniform random `startStep` between 10:00 and 20:00 (`10 * stepsPerHour` to `20 * stepsPerHour`), and its venue-day `eventBoost` is reset to `1.0f` (so only the closed-group transmission channel acts).
  - At `startStep`, `runGroupEvents` inspects the `present` agents who are already at that venue at that exact time step under their normal daily movement schedule. If `present > 0`, it samples `group = min(eventGroupSize, present)` (`min(30, present)`) attendees uniformly without replacement from the `present` agents.
  - If `infectiousSum > 0` among those `group` attendees, each susceptible attendee in `group` faces a 2-hour (`120`-minute) closed-group infection probability:
    $$p_{\text{inf}} = 1 - \exp\!\left(-k_0 \cdot \frac{\text{infectiousSum}}{\text{group}^\alpha} \cdot \text{locInfectiousness} \cdot \text{eventFactor} \cdot \text{seasonality} \cdot 120\right).$$
  - Every selected venue-event (including those with `present == 0`) is logged as a row in `events.tsv` (`day, step, location_index, locType, present, group, infectious_in_group, ratio, exposed, infected`), and every resulting infection is logged to `events.tsv.infections` (`day, agent, location_index, infector`) as well as `trace.tsv`.
- **Conclusion on the Note 59 prose error:** The file `59_r111_worlds.csv` (`events_total = 83,086`, or `247.3` events/day/replicate) is exact. The prose in `59_round11_results.md` ("14.6% of agents attend a closed group every day") mistakenly described the per-venue daily probability (`0.1456` of type-5/8 venues) as a per-agent daily probability.
- **Note on agent-level attendance tracking:** Because `events.tsv` logs `present` and `group` per event rather than the IDs of uninfected attendees, the exact number of daily person-attendances is $\sum \text{group}$ (`~1.0%–2.5%` of the `178,746` population per day, depending on how many selected venues have fewer than 30 people present at `startStep`). Since an agent can only be in one venue at a given step and events occur once per selected venue per day, daily unique attendees are bounded tightly by $\sum \text{group}$, and weekly unique share is reported alongside exact person-attendances per day and per week.

---

## 3. Experimental Design & Pre-Run Choices for Round 12

### R12-1: Paired World 3b on Common Seeds `77001..77012` + Event Semantics Audit
1. **Binary & Parameters:** Use `build_r10/panSim` (which includes all closed-group event flags) with the exact Round-6 `r67_M30` configuration:
   - `--eventRate 0.1456 --eventFactor 3000 --eventTypes 5,8 --eventGroupSize 30 --eventDurationHours 2`
   - Pass `--eventGroupLog <run_dir>/events.tsv` on every replicate so both `events.tsv` and `events.tsv.infections` are recorded.
   - Calibrate baseline `-k` (starting from the Round-6 value `0.0001422`) on the 12 common seeds `77001..77012` over 28 days so mean cumulative day-28 infections are within 3% of `6,211.25`.
2. **Deliverables for R12-1:**
   - `62_r121_worlds_paired.csv`, `62_r121_worlds_paired_offspring.csv`, `62_r121_clusters.csv`: Full comparison of the 4 paired arms (`world1_het_sh0.32`, `world2a_env_L30_sh0.70`, `world2b_env_L10_sh0.58`, and `world3b_events_M30_rate0.146_paired`) on seeds `77001..77012`, alongside the Round-6 `world3b_events_M30_rate0.146_r6` (`68101..68112`) for continuity.
   - `62_r121_event_semantics.csv`: Exact audit of `events.tsv` and `events.tsv.infections` across both `world3b` seed sets (eligible venues by type, total events/day, non-empty events/day, distribution of `present` and `group`, person-attendances/day and share of the `178,746` population per day and per week, events with `infectious_in_group > 0`, infections per active event, and share of all infections and index-case offspring occurring in events).

### R12-2: Under-Detection Thinning (`p = 1.0, 0.6, 0.3`) on Paired Traces
We will thin the existing paired traces on seeds `77001..77012` for **World 1** (`r10_w1_sh0.32`), **World 2b** (`r11_w2_L10_sh0.58`), and **World 3b** (`r12_w3b_M30_rate0.1456`), plus **World 2a** (`r11_w2_L30_sh0.70`) for completeness, without re-running the simulator.

To ensure transparency and avoid ambiguity, we specify the exact thinning mechanics before running:
- **Deterministic RNG seeding per replicate and rate:** For each replicate $r \in \{0,\dots,11\}$ and detection rate $p \in \{0.6, 0.3\}$, we use a fixed reproducible RNG (`np.random.default_rng(910000 + rep_idx * 100 + int(round(p * 100)))`).
- **Agent-level detection mask $D(a) \in \{0, 1\}$:**
  1. **Random per-infection detection (`random`):** Each infected agent $a$ in `trace.tsv` is independently detected with probability $p$ ($D(a) \sim \text{Bernoulli}(p)$).
  2. **Household-clustered detection (`household`):** Each household ID $h$ is independently selected with probability $p$ ($D_{\text{hh}}(h) \sim \text{Bernoulli}(p)$). Every agent $a$ belonging to household $h = \text{home}[a]$ has $D(a) = D_{\text{hh}}(\text{home}[a])$.
- **How detected index cases and their detected offspring are constructed:**
  - In the full trace (`p = 1.0`), the cohort of early index cases is $I_0 = \{i : 1 \le \text{day}(i) \le 10, \text{infector}(i) \ge 0\}$, and the offspring set of $i \in I_0$ is $O_0(i) = \{a : \text{infector}(a) = i\}$.
  - Under **agent-level detection** (`random` and `household`), an index case $i \in I_0$ enters the observed index cohort iff $D(i) = 1$, and each of its secondary cases $a \in O_0(i)$ is observed as an offspring of $i$ iff $D(a) = 1$. (Note: for `random`, since $D(i)$ and $D(a)$ for $a \in O_0(i)$ are independent $\text{Bernoulli}(p)$ draws, the marginal distribution of observed offspring per detected index case is identical to binomial thinning $Y_i^{\text{obs}} \sim \text{Binomial}(Y_i, p)$ on a random fraction $p$ of index cases.)
  - **Pre-run mathematical check on Prediction (b) for `household` detection:**
    Note 61's Prediction (b) states: *"with household-clustered detection, the same-household share of detected infectees falls in worlds 1 and 3b and the ratio of likelihood to moment k is at least 0.1 lower than under random detection of the same overall rate (because whole households vanish)"*.
    We flag a crucial conditioning distinction **before** running:
    - Under **agent-consistent household detection** (where an index case $i$ is observed iff its household $\text{home}[i]$ is detected, and an infectee $a$ is observed iff $\text{home}[a]$ is detected), conditioning on the index case $i$ being detected means $\text{home}[i]$ is **already detected with probability 1**! Consequently, **100%** of $i$'s same-household infectees ($\text{home}[a] = \text{home}[i]$) are detected, whereas only a fraction **$p$** of $i$'s outside-household infectees ($\text{home}[a] \ne \text{home}[i]$) are detected. That conditioning **increases** (rather than decreases) the same-household share among detected offspring of detected index cases, from $s_{\text{hh}}$ to $\frac{s_{\text{hh}}}{s_{\text{hh}} + p(1 - s_{\text{hh}})}$.
    - Conversely, if "household-clustered detection of infectees" means that **entire households of infectees vanish with probability $1-p$ independently of whether the index case was detected** (i.e., all index cases $i \in I_0$ are conditioned on as known index cases, or the index case is detected via e.g. workplace/index testing while secondary follow-up misses whole households with probability $1-p$, including the index case's own household with probability $1-p$), then whole household clusters of size 2–4 are wiped out to 0 with probability $1-p$ or kept intact with probability $p$. Even there, the expected count of surviving same-household infectees is $p \cdot Y_{i,\text{hh}}$ and of outside-household infectees is $p \cdot Y_{i,\text{out}}$, so the unconditional share of same-household infectees has the same numerator/denominator scaling $p$, *except* within the **top-10 largest detected clusters** where keeping or losing a whole household changes which clusters enter the top 10!
    - Because this distinction is central to evaluating Prediction (b) fairly, we will compute and report **both** variants of household-clustered detection in `62_r122_thinning.csv`:
      1. **`household_coupled` (index + infectee share the same household mask $D_{\text{hh}}$):** Index case $i$ is detected iff $D_{\text{hh}}(\text{home}[i]) = 1$, and infectee $a$ is detected iff $D_{\text{hh}}(\text{home}[a]) = 1$.
      2. **`household_infectee` (infectees thinned by household mask $D_{\text{hh}}$ independent of index detection):** Index cases are sampled at rate $p$, and infectees are detected iff their household $D_{\text{hh}}(\text{home}[a]) = 1$ (drawn independently of the index case's own detection).

---

## 4. Registered Pre-Run Predictions (from Note 61)

We register the three predictions from Note 61 verbatim to test against the Round 12 tables:
- **Prediction (a):** Under random 60% and 30% detection, `k_ml` and `k_mom` stay within `15%` of their un-thinned values in all three worlds, while the observed zero share rises from `~52%–68%` to `~75%–85%` (matching the negative-binomial expectation at the thinned mean $p \cdot R_0$).
- **Prediction (b):** With household-clustered detection, the same-household share of detected infectees falls in Worlds 1 and 3b and the ratio `k_ml / k_mom` is at least `0.1` lower than under random detection of the same overall rate (because whole households vanish).
- **Prediction (c):** Even at `30%` detection under either scheme, the two observable metrics — (i) observed zero share minus NB zero expectation at `k_ml`, and (ii) largest-venue-day share of the top-10 detected clusters — still correctly separate all three worlds in the same order as at `100%` detection:
  - Zero gap: `world 3b < world 2b < world 1`
  - Largest-venue-day share: `world 1 < world 3b < world 2b`
