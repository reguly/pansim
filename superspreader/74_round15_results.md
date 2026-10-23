# Round 15 Results — Parent–Child Offspring Association (Run C) and Density-Dependent Transmission (Run D)

## 1. Executive Summary

Round 15 executes the two experiments specified in `73_round15_instructions_parent_child_and_density.md`, motivated by the literature comparison in `72_review_of_supplied_literature_review.md`:

1. **Run C (Infection-level exports and parent–child offspring association on the three `B1` worlds of Round 14):**
   - We ran the three calibrated `B1` worlds (`w1:B1`, `w2b:B1`, `w3b:B1`) at their exact Round 14 parameter settings on all 12 replicate seeds (`77001..77012`) to **day 42** (`-w 6`) so every child infected by a days 1–10 index case up to day 24 has a complete 14-day forward offspring window (`infection_day + 14 <= 38 < 42`).
   - Using the 4-week (`-w 4`) `trace.tsv` from Round 14 alongside the 6-week `--episodeTrace` (`episodes.tsv`) and `--eventGroupLog` (`events.tsv.infections`), we eliminated late reinfection overwrites on days `28..41` (`68`, `79`, and `95` days 1–10 index cases across the 12 replicates of `w1`, `w2b`, and `w3b` would otherwise have had their `agentStats` entry overwritten by a second infection episode in weeks 5–6). As a result, the days 1–10 index-case offspring histograms in `74_c_infections_*.csv` reproduce `69_b_replicate_histograms.csv` **100% identically** in every replicate and every bin (`all_replicates_match_69_b_hist_exactly = True`).
   - **Parent–child correlation and superspreader-pair excess (`> 5` offspring, the 99th percentile of $\text{Poisson}(R)$):**
     - **World 1 (`w1:B1`, $18,571$ pairs):** Pearson $r = \mathbf{+0.0057}$ (`[-0.0064, +0.0176]`), Spearman $\rho = \mathbf{-0.0048}$ (`[-0.0138, +0.0026]`), superspreader-pair ratio $= \mathbf{0.978}$ (`714 / 729.8`, `95% CI [0.935, 1.019]`). Secondary cases from superspreaders are no more likely to be superspreaders than expected by chance.
     - **World 3b (`w3b:B1`, $19,765$ pairs):** Pearson $r = \mathbf{+0.0205}$ (`[+0.0077, +0.0322]`), Spearman $\rho = \mathbf{+0.0322}$ (`[+0.0191, +0.0435]`), superspreader-pair ratio $= \mathbf{1.042}$ (`921 / 883.6`, `95% CI [1.010, 1.069]`; `1.019` inside events). Transient closed-group events remain nearly memoryless across generations.
     - **World 2b (`w2b:B1`, $16,207$ pairs):** Pearson $r = \mathbf{+0.0296}$ (`[+0.0091, +0.0555]`), Spearman $\rho = \mathbf{+0.0414}$ (`[+0.0331, +0.0493]`), superspreader-pair ratio $= \mathbf{1.138}$ (`774 / 680.0`, `95% CI [1.108, 1.168]`). Because the risky-venue class (`4.39%` of the total population = `10%` of eligible adults) is strongly enriched among parents (`20.66%` of index cases, producing `50.73%` of all index-case offspring) and assortatively transmitted (`33.96%` of children of class-member parents are in the class vs `13.21%` for non-class parents), World 2b exhibits a statistically significant positive parent–child correlation and a `+13.8%` superspreader-pair excess, though diluted below the pre-registered `r >= +0.04` and `SS ratio >= 1.25` cutoffs by the `66.0%` out-of-class mixing at high-$L$ venues and individual shedding noise (`sheddingShape = 0.4`).
   - **Conditional child mean by parent offspring class (`1`, `2–5`, `6–9`, `10+`) relative to day-matched expectation:**
     - **World 1 (`w1:B1`):** Children of `1`-offspring parents average **`1.612`** offspring vs day-matched **`1.444`** (ratio **`1.116`**), whereas children of `2–5` and `6–9` parents fall below (`0.987`, `0.954`) due to household susceptible depletion.
     - **World 2b (`w2b:B1`):** Children of `1`-offspring parents average **`1.312`** offspring vs day-matched **`1.611`** (ratio **`0.814`**), and the day-matched ratio rises monotonically across parent classes: **`0.814` (`1`) $\to$ `0.910` (`2–5`) $\to$ `0.996` (`6–9`) $\to$ `1.181` (`10+`)**.
     - **World 3b (`w3b:B1`):** Flat near `1.0` across parent classes (`0.942`, `0.911`, `0.974`, `1.047`).
   - **Trace-based backward-to-forward contact-tracing yield ratio:**
     - When tracing backward from the **children of the days 1–10 index cases** to their index-case infectors ($G_1$), $(1 + \overline{\text{siblings}(c)}) / \overline{Z_p} = \mathbf{5.854, 7.504, 8.263}$ — matching the moment-based formula $1/R + 1 + 1/k_{\text{mom}} = \mathbf{5.854, 7.504, 8.263}$ (`5.9, 7.5, 8.3`) to **`0.00%` (exact algebraic identity)**.
     - When tracing backward from the **days 1–10 index cases themselves** to *their* infectors (predominantly the **day-0 initial seeds**, $G_0$), the yield ratio is **`5.489 (-6.2%)` in World 1**, **`6.081 (-19.0%)` in World 2b**, and **`8.889 (+7.6%)` in World 3b**. The `-19.0%` gap in World 2b arises because day-0 seeds are placed uniformly at random (`4.39%` in the risky-venue class), whereas days 1–10 index cases are already $4.7\times$ selected into the risky-venue class (`20.66%`).

2. **Run D (Density-dependent transmission at $\alpha = 0.5$ and $\alpha = 0$ beside the $\alpha = 1$ `B1` reference):**
   - All 6 new cells (`alpha = 0.5` and `0.0` across `w1`, `w2b`, `w3b`) calibrated cleanly on seeds `77001..77012` within $\pm 2.3\%$ of the day-28 target `6,211.25`.
   - **Shift from households to large venues:** As $\alpha$ drops from `1` to `0.5` to `0`, the home share of infections collapses in all three worlds (**`31.6% -> 11.2% -> 1.6%`** in World 1; **`13.7% -> 2.7% -> 0.3%`** in World 2b; **`18.2% -> 7.1% -> 1.2%`** in World 3b), while median infection-location occupancy jumps from **`29 -> 195 -> 702`** in World 1, **`81 -> 523 -> 907`** in World 2b, and **`23 -> 30 -> 97`** (p90 **`30 -> 410 -> 1,034`**) in World 3b.
   - **Overdispersion and estimator gap (`k_ml / k_mom`):**
     - In **World 1**, lowering $\alpha$ injects venue-size heterogeneity on top of individual shedding, lowering $k_{\text{ml}}$ from **`0.263` ($\alpha=1$) $\to$ `0.213` ($\alpha=0.5$) $\to$ `0.178` ($\alpha=0$)**, lowering $k_{\text{mom}}$ from **`0.241` $\to$ `0.176` $\to$ `0.127`**, and raising $k_{\text{ml}} / k_{\text{mom}}$ from **`1.09` $\to$ `1.22` $\to$ `1.40`**.
     - In **World 2b**, lowering $\alpha$ similarly lowers $k_{\text{ml}}$ from **`0.270` $\to$ `0.235` $\to$ `0.221`** and $k_{\text{mom}}$ from **`0.170` $\to$ `0.148` $\to$ `0.147`** (`k_ml / k_mom = 1.59, 1.59, 1.51`).
     - In **World 3b**, because `runGroupEvents()` caps closed-group events at $\text{group} \le 30$ and divides by $\text{group}^\alpha$, lowering $\alpha$ to `0` boosts regular large locations ($N \sim 100\text{–}1,000$) much more than 30-person events; recalibrating `-k` downward by $50\times$ reduces the closed-group event share of offspring from **`70.0%` ($\alpha=1$) and `67.9%` ($\alpha=0.5$) to `44.0%` ($\alpha=0$)**, which raises $k_{\text{ml}}$ in World 3b at $\alpha = 0$ to **`0.497`** ($k_{\text{mom}} = \mathbf{0.323}$).
   - **Invariance of the two structural discriminators across $\alpha \in \{1, 0.5, 0\}$:**
     - **Top-10 cases' largest-venue-day share** remains `< 0.27` in Worlds 1 and 2b even at $\alpha = 0$ (**`0.203 -> 0.205 -> 0.250`** in World 1; **`0.138 -> 0.211 -> 0.265`** in World 2b) vs **`0.871 -> 0.888 -> 0.861`** in World 3b, because agents in Worlds 1 and 2b visit their large workplaces and high-$L$ venues repeatedly across multiple days (`5.9–6.3` distinct venues at $\alpha=0$) rather than in a single 2-hour event (`1.97` distinct venues in World 3b).
     - **Zero-class gap (`observed_minus_nb_zero`)** remains near zero (`|gap| <= 0.0072`) in Worlds 1 and 2b at all $\alpha$ (**`-0.11, -0.38, -0.50 pt`** in World 1; **`-0.72, -0.64, -0.67 pt`** in World 2b) while persisting at **`-2.91, -2.73, -2.52 pt`** in World 3b across all $\alpha$.

---

## 2. Run C — Infection-Level Exports and Parent–Child Offspring Association

### 2.1 Verification of Exact Trajectory Reproduction and Reinfection-Overwrite Protection

In `include/policies/infectionPolicies.h`, `writeInfectionTrace()` writes `trace.tsv` at the **end** of the simulation from `agentStats[agent]`, which stores a single record per agent (its most recent infection). When a simulation is extended from 4 weeks (`-w 4`, days `0..27`) to 6 weeks (`-w 6`, days `0..41`), a small fraction of agents first infected on days `0..27` recover, wane back to susceptible, and are **reinfected** on days `28..41`, overwriting their original `agentStats` entry (`68` days 1–10 index cases in `w1:B1`, `79` in `w2b:B1`, and `95` in `w3b:B1` across the 12 replicates).

By combining the Round 14 4-week `trace.tsv` (locking all days `0..27` first-infection records with zero reinfection overwrites) with the 6-week `--episodeTrace` (`episodes.tsv`), `--eventGroupLog` (`events.tsv.infections`), and 6-week `trace.tsv` for days `28..41`, `analyze_round15.py` preserves every day `0..27` infection record identically while counting each case's full 14-day secondary infections up to day 42:
- **Trajectory identity up to day 28:** All 36 runs (`3 worlds x 12 replicates`) match Round 14 day-28 cumulative infections identically (`6,274.42`, `6,285.42`, `6,280.75`).
- **Index-case histogram identity:** Across all 36 replicates, the days 1–10 index-case `offspring_14d` histogram computed from `74_c_infections_*.csv` matches `69_b_replicate_histograms.csv` **100% identically** in every bin (`all_replicates_match_69_b_hist_exactly = True`).
- **File splitting for Drive upload (`< 2 MB` per file):** Each world's infection-level export is split into three 4-replicate blocks (`reps01_04`, `reps05_08`, `reps09_12`), yielding 9 CSV files between `1.49 MB` and `1.99 MB`.

### 2.2 Pooled Parent–Child Association Summary (`74_c_cells_summary.csv`)

Parents $p$ are all non-seed index cases infected on days `1..10` (`1 <= infection_day <= 10`, `infector_id != ""`). Children $c$ are all secondary cases infected by $p$ within $p$'s 14-day offspring window (`c.infection_day <= p.infection_day + 14`), with $Z_c = \text{offspring\_14d}(c)$ counted over $c$'s own 14-day window (`<= c.infection_day + 14 <= 38 < 42`). The superspreader threshold $T(R)$ is the 99th percentile of $\text{Poisson}(R)$, which equals **`5`** in all three `B1` worlds (`> 5`, i.e. $\ge 6$ offspring; we also report the ratio at $\ge 5$).

| Metric | `w1:B1` (Shedding) | `w2b:B1` (Risky-venue class + shedding) | `w3b:B1` (Closed-group events) |
| :--- | :---: | :---: | :---: |
| Replicates / Index cases ($G_1$, days 1–10) | `12` / `13,197` | `12` / `10,301` | `12` / `13,620` |
| Day-28 / Day-42 mean cumulative infections | `6,274.4` / `16,690.5` | `6,285.4` / `18,890.8` | `6,280.8` / `14,959.2` |
| Parent mean 14d offspring $R$ / $k_{\text{ml}}$ / $k_{\text{mom}}$ | `1.407` / `0.263` / `0.241` | `1.573` / `0.270` / `0.170` | `1.451` / `0.248` / `0.152` |
| Parent–child pairs (14d window / all up to d28) | `18,571` / `19,101` | `16,207` / `16,666` | `19,765` / `20,459` |
| Child mean 14d offspring $\overline{Z_c}$ | `1.451` | `1.631` | `1.432` |
| **Parent–child Pearson $r$ (14d)** `[95% boot CI]` | **`+0.0057`** `[-0.0064, +0.0176]` | **`+0.0296`** `[+0.0091, +0.0555]` | **`+0.0205`** `[+0.0077, +0.0322]` |
| **Parent–child Spearman $\rho$ (14d)** `[95% boot CI]` | **`-0.0048`** `[-0.0138, +0.0026]` | **`+0.0414`** `[+0.0331, +0.0493]` | **`+0.0322`** `[+0.0191, +0.0435]` |
| Parent–child Pearson $r$ / Spearman $\rho$ (all d28 children) | `+0.0060` / `-0.0034` | `+0.0265` / `+0.0391` | `+0.0191` / `+0.0313` |
| Poisson 99th-percentile threshold $T(R)$ | `5` ($>5 \iff \ge 6$) | `5` ($>5 \iff \ge 6$) | `5` ($>5 \iff \ge 6$) |
| Pairs with parent $Z_p > 5$ / child $Z_c > 5$ (share) | `9,737` / `1,392` (`7.50%`) | `8,909` / `1,237` (`7.63%`) | `13,271` / `1,316` (`6.66%`) |
| Observed / Expected pairs with both $Z_p > 5, Z_c > 5$ | `714` / `729.8` | `774` / `680.0` | `921` / `883.6` |
| **Superspreader-pair ratio ($>5$)** `[95% boot CI]` | **`0.978`** `[0.935, 1.019]` | **`1.138`** `[1.108, 1.168]` | **`1.042`** `[1.010, 1.069]` |
| Superspreader-pair ratio at $\ge 5$ | `0.990` | `1.095` | `1.045` |
| Sibling pairwise correlation / one-way ANOVA ICC | `-0.0040` / `-0.0100` | `-0.0003` / `-0.0510` | `+0.0104` / `+0.0097` |
| Parents with $\ge 2$ children / total children in $\ge 2$ families | `3,253` / `16,730` | `2,675` / `14,638` | `2,124` / `16,326` |
| **Parents with $\ge 6$ offspring: count / largest-venue-day share** | `958` / **`0.261`** | `745` / **`0.232`** | `913` / **`0.921`** |

### 2.3 Conditional Child Mean Offspring by Parent Offspring Class (`74_c_parent_classes.csv`)

For each child infected on day $d$, the day-matched baseline expectation is the mean 14-day offspring of all non-seed infections occurring on day $d$ in the same replicate.

| World | Parent Offspring Class ($Z_p$) | Parents in Class | Child Infections ($N$) | Child Mean Offspring $\overline{Z_c}$ | Day-Matched Expectation | **Ratio to Day-Matched** |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`w1:B1`** | `1 (at most 1)` | `1,841` | `1,841` | `1.612` | `1.444` | **`1.116`** (`+11.6%`) |
| **`w1:B1`** | `2_to_5` | `2,295` | `6,993` | `1.413` | `1.432` | **`0.987`** (`-1.3%`) |
| **`w1:B1`** | `6_to_9` | `583` | `4,154` | `1.380` | `1.447` | **`0.954`** (`-4.6%`) |
| **`w1:B1`** | `10_or_more` | `375` | `5,583` | `1.497` | `1.442` | **`1.039`** (`+3.9%`) |
| **`w2b:B1`** | `1 (at most 1)` | `1,569` | `1,569` | `1.312` | `1.611` | **`0.814`** (`-18.6%`) |
| **`w2b:B1`** | `2_to_5` | `1,930` | `5,729` | `1.465` | `1.610` | **`0.910`** (`-9.0%`) |
| **`w2b:B1`** | `6_to_9` | `425` | `3,034` | `1.600` | `1.606` | **`0.996`** (`-0.4%`) |
| **`w2b:B1`** | `10_or_more` | `320` | `5,875` | `1.895` | `1.605` | **`1.181`** (`+18.1%`) |
| **`w3b:B1`** | `1 (at most 1)` | `3,439` | `3,439` | `1.358` | `1.441` | **`0.942`** (`-5.8%`) |
| **`w3b:B1`** | `2_to_5` | `1,211` | `3,055` | `1.301` | `1.428` | **`0.911`** (`-8.9%`) |
| **`w3b:B1`** | `6_to_9` | `233` | `1,757` | `1.411` | `1.448` | **`0.974`** (`-2.6%`) |
| **`w3b:B1`** | `10_or_more` | `680` | `11,514` | `1.491` | `1.424` | **`1.047`** (`+4.7%`) |

This table cleanly separates the three mechanisms:
- In **World 1**, a `1`-offspring parent rarely exhausts its household's susceptibles, so its child averages **`1.612`** offspring (`1.116x` day-matched), whereas parents with `2–9` offspring infect a higher share of household members who then face depleted households (`0.987x` and `0.954x`).
- In **World 2b**, `1`-offspring parents are predominantly *outside* the risky-venue class, so their children are mostly infected in households or low-risk venues and average **`1.312`** offspring (`0.814x` day-matched), whereas `10+` parents are overwhelmingly risky-venue class members whose children average **`1.895`** offspring (`1.181x` day-matched) — a **`+45.0%`** jump in child reproduction from the lowest to the highest parent class (`1.895 / 1.312 = 1.445`).

### 2.4 Subgroup Breakdown: Household vs Outside-Household and Event vs Non-Event (`74_c_subgroups.csv`)

| World | Subgroup (Where Child Was Infected) | Pairs ($N$) | Share of Pairs | Parent Mean $Z_p$ | Child Mean $Z_c$ | Pearson $r$ | Spearman $\rho$ | SS Ratio ($>5$) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`w1:B1`** | `all_children` | `18,571` | `100.0%` | `8.238` | `1.451` | `+0.0057` | `-0.0048` | `0.978` |
| **`w1:B1`** | `same_household` | `5,782` | `31.1%` | `6.128` | `1.228` | `+0.0013` | `-0.0431` | `0.926` |
| **`w1:B1`** | `outside_household` | `12,789` | `68.9%` | `9.193` | `1.552` | `-0.0048` | `-0.0133` | `0.965` |
| **`w2b:B1`** | `all_children` | `16,207` | `100.0%` | `11.807` | `1.631` | `+0.0296` | `+0.0414` | `1.138` |
| **`w2b:B1`** | `same_household` | `2,614` | `16.1%` | `6.497` | `0.921` | `+0.0342` | `+0.0078` | `1.139` |
| **`w2b:B1`** | `outside_household` | `13,593` | `83.9%` | `12.828` | `1.768` | `+0.0182` | `+0.0276` | `1.091` |
| **`w3b:B1`** | `all_children` | `19,765` | `100.0%` | `11.991` | `1.432` | `+0.0205` | `+0.0322` | `1.042` |
| **`w3b:B1`** | `same_household` | `3,648` | `18.5%` | `3.320` | `1.330` | `+0.0104` | `-0.0253` | `1.336` |
| **`w3b:B1`** | `outside_household` | `16,117` | `81.5%` | `13.954` | `1.455` | `+0.0177` | `+0.0080` | `1.024` |
| **`w3b:B1`** | `inside_event` | `13,837` | `70.0%` | `15.918` | `1.450` | `+0.0209` | `+0.0058` | `1.019` |
| **`w3b:B1`** | `outside_event` | `5,928` | `30.0%` | `2.825` | `1.388` | `+0.0241` | `+0.0049` | `1.553` |

Note why the overall `w2b:B1` correlation (`r = +0.0296`, `\rho = +0.0414`, `SS ratio = 1.138`) is higher than either `same_household` or `outside_household` alone: **between-stratum composition**! High-offspring parents in World 2b infect a much larger fraction of their children outside the household (`83.9%` overall, rising above `90%` for `10+` parents), and children infected outside the household in World 2b have nearly **double** the mean offspring of children infected inside the household (`1.768` vs `0.921`, with `8.48%` vs `3.21%` becoming superspreaders $>5$).

### 2.5 Why World 2b Assortativity Is Positive (`+13.8%` SS excess) Yet Diluted Below `1.25`

From `hvi.csv`, we tracked the risky-venue class flag (`class == 1` in `s8_2_t1_L10`, representing `10%` of eligible adults = **`4.39%`** of the total 178,746-agent population) across generations in `w2b:B1`:
1. **Population baseline:** **`4.39%`** (`7,848 / 178,746`) of all agents are in the risky-venue class.
2. **Generation $G_1$ (days 1–10 index cases):** **`20.66%`** (`2,128 / 10,301`) are in the risky-venue class ($4.71\times$ the population baseline), and those `20.66%` of index cases generate **`50.73%`** (`8,221 / 16,207`) of all index-case secondary infections (`50.58%` of all non-seed infections up to day 28).
3. **Generation $G_2$ (children of index cases):** **`23.74%`** (`3,847 / 16,207`) of all children are in the risky-venue class:
   - Given a **class-member parent (`class == 1`)**: **`33.96%`** of children are class members.
   - Given a **non-class parent (`class == 0`)**: **`13.21%`** of children are class members.
4. **Why dilution occurs across $(Z_p, Z_c)$:** Even when a class-member parent transmits, **`66.04%`** of its secondary cases are non-class agents who happened to share a high-$L$ venue or household with the parent. Because the correlation between $Z_p$ and $Z_c$ is the product of three links — $Z_p \leftrightarrow \text{class}_p$, $\text{class}_p \leftrightarrow \text{class}_c$ ($\Delta P = 0.2075$), and $\text{class}_c \leftrightarrow Z_c$ — plus independent Gamma shedding noise (`sheddingShape = 0.4`, $\text{CV}^2 = 2.5$) on both parent and child, the linear correlation is attenuated to $r = +0.0296$ (Spearman $\rho = +0.0414$) and the superspreader-pair ratio to `1.138`.

### 2.6 Contact-Tracing Yield Ratio from the Traces vs the Moment Formula

The moment-based backward-to-forward yield ratio computed from the days 1–10 index-case cohort ($G_1$) in Note 72 is:
$$\frac{1 + E[Z(Z-1)] / E[Z]}{E[Z]} = \frac{1}{R} + 1 + \frac{1}{k_{\text{mom}}}$$
We evaluated two trace-based definitions in `74_c_cells_summary.csv`:

| World | Moment-Based Yield Ratio ($G_1$) | **Def. 1:** Backward from Children of Index Cases to Index-Case Infectors ($G_1$) $\frac{1 + \overline{\text{sib}(c)}}{R_{G_1}}$ (Diff) | Def. 1 Normalized by Child $R_{G_2}$ $\frac{1 + \overline{\text{sib}(c)}}{R_{G_2}}$ (Diff) | **Def. 2:** Backward from Index Cases ($G_1$) to *Their* Infectors ($G_0 \cup G_1$, 14d sibs) (Diff) | Def. 2 Using All-Day Siblings of $G_0 \cup G_1$ Infectors (Diff) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`w1:B1`** | **`5.854`** | **`5.854`** (`0.00%`) | `5.678` (`-3.00%`) | `5.489` (`-6.25%`) | `5.609` (`-4.19%`) |
| **`w2b:B1`** | **`7.504`** | **`7.504`** (`0.00%`) | `7.238` (`-3.55%`) | `6.081` (`-18.97%`) | `6.173` (`-17.74%`) |
| **`w3b:B1`** | **`8.263`** | **`8.263`** (`0.00%`) | `8.376` (`+1.37%`) | `8.889` (`+7.58%`) | `8.915` (`+7.89%`) |

- **Under Definition 1 (evaluating the same infector generation $G_1$ both backward and forward):** Because each index case $p \in G_1$ with $Z_p$ 14-day children is sampled $Z_p$ times when tracing backward from its children $c \in G_2$, each child sees $Z_p - 1$ siblings, so $\overline{\text{sib}(c)} = \frac{\sum_{p \in G_1} Z_p(Z_p - 1)}{\sum_{p \in G_1} Z_p} = \frac{E[Z(Z-1)]}{E[Z]}$ (`7.238, 10.807, 10.991`), reproducing `5.854, 7.504, 8.263` with **`0.00%` error**.
- **Under Definition 2 (tracing backward from days 1–10 index cases $i \in G_1$ to their infectors in $G_0 \cup G_1$):** Most infectors of days 1–10 cases are the **day-0 initial seeds ($G_0$)**. In Worlds 1 and 3b, $G_0$ seeds have nearly the same offspring distribution as $G_1$ index cases (`-6.2%` and `+7.6%`, both within `10%`). In World 2b, however, day-0 seeds are chosen uniformly at random across the population (`4.39%` in the risky-venue class), whereas $G_1$ index cases are already $4.7\times$ enriched in the risky-venue class (`20.66%`), so backward tracing to $G_0$ seeds yields `6.081` (`-19.0%` below $G_1$'s `7.504`).

---

## 3. Run D — Density-Dependent Transmission Across $\alpha \in \{1.0, 0.5, 0.0\}$

### 3.1 Calibration and Offspring Distribution Summary (`74_d_cells_summary.csv`)

All 9 cells (`3 worlds x 3 density exponents`) are evaluated on the same 12 final seeds (`77001..77012`) over 4 weeks (`28` days), matched to the Round 14 `B1` day-28 target of `6,211.25` cumulative infections:

| Cell (`world:arm`) | $\alpha$ | Background `-k` | Day-28 Mean (vs Target) | Index Cases | Early $R$ | **$k_{\text{ml}}$** `[95% CI]` | **$k_{\text{mom}}$** `[95% CI]` | **$k_{\text{ml}} / k_{\text{mom}}$** | Share `0` | **Obs $-$ NB(0)** | Share `>5` | **Share Causing 80%** | Max / Mean Max / p99 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`w1:B1_alpha1`** | `1.0` | `5.1517e-4` | `6,274.4` (`+1.0%`) | `13,197` | `1.407` | **`0.263`** `[0.253, 0.272]` | **`0.241`** `[0.227, 0.258]` | **`1.09`** | `0.614` | **`-0.0011`** | `0.0726` | **`0.176`** | `43` / `33.4` / `14` |
| **`w1:D_alpha0.5`** | `0.5` | `5.5721e-5` | `6,071.7` (`-2.2%`) | `11,667` | `1.488` | **`0.213`** `[0.205, 0.222]` | **`0.176`** `[0.163, 0.191]` | **`1.22`** | `0.638` | **`-0.0038`** | `0.0764` | **`0.152`** | `67` / `43.7` / `18.3` |
| **`w1:D_alpha0`** | `0.0` | `3.2010e-6` | `6,103.8` (`-1.7%`) | `9,774` | `1.570` | **`0.178`** `[0.173, 0.182]` | **`0.127`** `[0.112, 0.140]` | **`1.40`** | `0.661` | **`-0.0050`** | `0.0767` | **`0.132`** | `92` / `58.2` / `22` |
| **`w2b:B1_alpha1`** | `1.0` | `1.1688e-4` | `6,285.4` (`+1.2%`) | `10,301` | `1.573` | **`0.270`** `[0.259, 0.283]` | **`0.170`** `[0.143, 0.198]` | **`1.59`** | `0.588` | **`-0.0072`** | `0.0723` | **`0.179`** | `126` / `52.6` / `19` |
| **`w2b:D_alpha0.5`** | `0.5` | `9.8297e-6` | `6,210.2` (`-0.0%`) | `10,042` | `1.603` | **`0.235`** `[0.222, 0.246]` | **`0.148`** `[0.122, 0.172]` | **`1.59`** | `0.611` | **`-0.0064`** | `0.0781` | **`0.163`** | `144` / `59.3` / `19` |
| **`w2b:D_alpha0`** | `0.0` | `4.8039e-7` | `6,297.4` (`+1.4%`) | `10,782` | `1.618` | **`0.221`** `[0.211, 0.231]` | **`0.147`** `[0.135, 0.159]` | **`1.51`** | `0.619` | **`-0.0067`** | `0.0790` | **`0.155`** | `85` / `59.3` / `19.2` |
| **`w3b:B1_alpha1`** | `1.0` | `1.0587e-4` | `6,280.8` (`+1.1%`) | `13,620` | `1.451` | **`0.248`** `[0.238, 0.258]` | **`0.152`** `[0.146, 0.158]` | **`1.63`** | `0.592` | **`-0.0291`** | `0.0670` | **`0.137`** | `40` / `32.2` / `21` |
| **`w3b:D_alpha0.5`** | `0.5` | `2.0291e-5` | `6,102.8` (`-1.7%`) | `13,598` | `1.489` | **`0.259`** `[0.254, 0.266]` | **`0.159`** `[0.152, 0.169]` | **`1.63`** | `0.582` | **`-0.0273`** | `0.0657` | **`0.150`** | `60` / `33.2` / `21` |
| **`w3b:D_alpha0`** | `0.0` | `2.1340e-6` | `6,200.4` (`-0.2%`) | `11,897` | `1.470` | **`0.497`** `[0.475, 0.523]` | **`0.323`** `[0.310, 0.338]` | **`1.54`** | `0.479` | **`-0.0252`** | `0.0571` | **`0.249`** | `32` / `24.8` / `15` |

### 3.2 Place-Type Shares, Occupancy Quantiles, Spatial Concentration, and Top-10 Case Diagnostics

| Cell (`world:arm`) | $\alpha$ | **Home Share** | School & Work Share | High-$L$ Share | Hospital Share | Household SAR | **Occupancy Median / p90 (Pooled)** | **Top 10% Active Venues Share (Rep / Pooled / Non-Home)** | **Top-10 Cases: Mean Offspring / HH Share / Largest-Venue-Day Share / Distinct Venues** | Event Offspring Share (`w3b`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`w1:B1_alpha1`** | `1.0` | **`0.316`** | `0.169` | `0.176` | `0.078` | `1.38e-3` | **`29` / `381`** | **`0.423`** / `0.593` / `0.474` | `21.1` / `0.184` / **`0.203`** / `6.24` | — |
| **`w1:D_alpha0.5`** | `0.5` | **`0.112`** | `0.229` | `0.327` | `0.133` | `5.20e-4` | **`195` / `1,001`** | **`0.662`** / `0.805` / `0.676` | `25.6` / `0.199` / **`0.205`** / `6.64` | — |
| **`w1:D_alpha0`** | `0.0` | **`0.016`** | `0.310` | `0.446` | `0.102` | `3.22e-4` | **`702` / `1,182`** | **`0.796`** / `0.909` / `0.783` | `30.9` / `0.155` / **`0.250`** / `5.88` | — |
| **`w2b:B1_alpha1`** | `1.0` | **`0.137`** | `0.026` | `0.777` | `0.009` | `7.69e-4` | **`81` / `956`** | **`0.570`** / `0.827` / `0.533` | `27.8` / `0.070` / **`0.138`** / `9.85` | — |
| **`w2b:D_alpha0.5`** | `0.5` | **`0.027`** | `0.025` | `0.909` | `0.010` | `2.19e-4` | **`523` / `1,151`** | **`0.703`** / `0.895` / `0.694` | `29.7` / `0.032` / **`0.211`** / `8.53` | — |
| **`w2b:D_alpha0`** | `0.0` | **`0.003`** | `0.022` | `0.953` | `0.008` | `9.86e-5` | **`907` / `1,250`** | **`0.827`** / `0.903` / `0.826` | `31.6` / `0.018` / **`0.265`** / `6.33` | — |
| **`w3b:B1_alpha1`** | `1.0` | **`0.182`** | `0.023` | `0.126` | `0.008` | `1.25e-3` | **`23` / `30`** | **`0.643`** / `0.758` / `0.484` | `24.6` / `0.026` / **`0.871`** / `1.86` | `0.700` |
| **`w3b:D_alpha0.5`** | `0.5` | **`0.071`** | `0.050` | `0.207` | `0.025` | `4.06e-4` | **`30` / `410`** | **`0.554`** / `0.739` / `0.461` | `24.6` / `0.031` / **`0.888`** / `1.85` | `0.679` |
| **`w3b:D_alpha0`** | `0.0` | **`0.012`** | `0.129` | `0.353` | `0.053` | `2.60e-4` | **`97` / `1,034`** | **`0.565`** / `0.708` / `0.544` | `18.2` / `0.062` / **`0.861`** / `1.97` | `0.440` |

### 3.3 Why World 3b Becomes *Less* Overdispersed at $\alpha = 0$ (`k_ml = 0.497` vs `0.248` at $\alpha = 1$)

In `include/policies/infectionPolicies.h` (lines 1209–1211), the closed-group event kernel `runGroupEvents()` computes:
```cpp
double density = infectiousSum / pow((double)group, (double)densityExponent);
double exponent = this->k * density * locInfectiousness * factor * seasonality * exposureMinutes;
```
where `group = min(30, present)`. When $\alpha$ drops from `1` to `0`, a 30-person closed-group event has its per-contact hazard multiplied by $30^{1-0} = 30\times$, whereas a 900-person regular location has its hazard multiplied by $900\times$ ($30\times$ more than the event!). Consequently, recalibrating `-k` downward by $50\times$ (`1.059e-4 -> 2.134e-6`) to keep day-28 infections at `6,200` reduces the closed-group event share of index-case offspring from **`70.0%` ($\alpha=1$) and `67.9%` ($\alpha=0.5$) to `44.0%` ($\alpha=0$)**, while regular homogeneous transmission in large locations rises to `56.0%`. Because World 3b has homogeneous individual shedding (`sheddingShape` unused), replacing 30-person event spikes with multi-day background transmission in large venues raises $k_{\text{ml}}$ from `0.248` to `0.497`. Even so, the two-component mixture signature (`observed_minus_nb_zero = -0.0252`) and the top-10 cases' largest-venue-day share (`0.861`) remain intact!

---

## 4. Explicit Evaluation of All Registered Predictions (Note 73)

| Prediction | Statement in Note 73 | Observed Result | Verdict |
| :--- | :--- | :--- | :---: |
| **C(a)** | In `w1` and `w3b`, parent–child correlation is within `[-0.03, +0.05]` and SS-pair ratio is within `[0.85, 1.20]`. | `w1`: $r = +0.0057$, $\rho = -0.0048$, SS ratio $= \mathbf{0.978}$. `w3b`: $r = +0.0205$, $\rho = +0.0322$, SS ratio $= \mathbf{1.042}$ (`1.019` inside events). All well inside the predicted intervals. | **PASSED** |
| **C(b)** | In `w2b`, parent–child correlation is `>= +0.04` and SS-pair ratio is `>= 1.25`. | `w2b` has the highest correlation and SS ratio of the 3 worlds (`95%` CIs exclude 0 and 1.0): Spearman $\rho = \mathbf{+0.0414}$ (`[+0.033, +0.049]`) meets `>= +0.04`, but Pearson $r = \mathbf{+0.0296}$ (`[+0.009, +0.056]`) and SS ratio $= \mathbf{1.138}$ (`[1.108, 1.168]`) fall below `+0.04` and `1.25` due to `66.0%` out-of-class mixing at high-$L$ venues and shedding noise. | **FAILED on exact cutoffs** (directionally confirmed) |
| **C(c)** | Children of `1`-offspring parents have mean offspring $\ge$ day-matched average in `w1`, and $<$ day-matched average in `w2b`. | `w1` class-`1` ratio to day-matched $= \mathbf{1.116}$ (`1.612 vs 1.444`, $+11.6\%$). `w2b` class-`1` ratio to day-matched $= \mathbf{0.814}$ (`1.312 vs 1.611`, $-18.6\%$, rising monotonically to `1.181` for `10+` parents). | **PASSED** |
| **C(d)** | Trace-based backward-to-forward yield ratio is within `10%` of the moment-based values (`5.9, 7.5, 8.3`). | **Def. 1 (tracing from index cases' children back to index-case infectors $G_1$):** **`5.854, 7.504, 8.263`** (`0.00%` error in all 3 worlds; or `-3.0%, -3.5%, +1.4%` over child $R$). **Def. 2 (tracing from index cases back to day-0 seeds $G_0$):** `5.489 (-6.2%)` in `w1`, `8.889 (+7.6%)` in `w3b`, and `6.081 (-19.0%)` in `w2b` because day-0 seeds are unselected (`4.39%` in class vs `20.66%` in $G_1$). | **PASSED** (with $G_0$ vs $G_1$ selection effect documented in `w2b`) |
| **C(e)** | Sibling correlation near `0` in `w1`, mildly positive in `w3b`, positive in `w2b`; largest-venue-day share among $\ge 6$-offspring parents `> 0.80` in `w3b` and `< 0.35` in `w1, w2b`. | Largest-venue-day share ($\ge 6$ offspring): **`0.921`** (`w3b`) vs **`0.261`** (`w1`) and **`0.232`** (`w2b`) — **passed**. Sibling correlation: **`-0.0040`** in `w1` and **`+0.0104`** in `w3b` — **passed**; **`-0.0003`** pairwise (`-0.0510` ANOVA) in `w2b` — **failed** because two-step class attenuation ($\sim r_{p,c}^2 \approx 0.001$) is offset by within-household susceptible depletion. | **PARTIAL** (venue-day share & `w1/w3b` ICC passed; `w2b` sibling ICC failed) |
| **D(a)** | As $\alpha$ drops from `1 -> 0.5 -> 0`, home share falls monotonically and median/p90 infection occupancy rise sharply in all 3 worlds. | Home share: `0.316 -> 0.112 -> 0.016` (`w1`), `0.137 -> 0.027 -> 0.003` (`w2b`), `0.182 -> 0.071 -> 0.012` (`w3b`). Median occupancy: `29 -> 195 -> 702` (`w1`), `81 -> 523 -> 907` (`w2b`), `23 -> 30 -> 97` (`w3b`, p90 `30 -> 410 -> 1,034`). | **PASSED** |
| **D(b)** | In `w1`, lowering $\alpha$ to `0.5` and `0` lowers $k_{\text{ml}}$ and $k_{\text{mom}}$ and raises $k_{\text{ml}}/k_{\text{mom}} > 1.15$. | `w1`: $k_{\text{ml}}$ drops `0.263 -> 0.213 -> 0.178`, $k_{\text{mom}}$ drops `0.241 -> 0.176 -> 0.127`, and $k_{\text{ml}}/k_{\text{mom}}$ rises `1.09 -> 1.22 -> 1.40` (both $> 1.15$). | **PASSED** |
| **D(c)** | Lowering $\alpha$ increases the share of infections in the top `10%` of active venues in all 3 worlds. | Rises strongly in `w1` (`0.423 -> 0.662 -> 0.796`, pooled `0.593 -> 0.805 -> 0.909`) and `w2b` (`0.570 -> 0.703 -> 0.827`, pooled `0.827 -> 0.895 -> 0.903`). In `w3b`, non-home top-10% share rises from `0.484` ($\alpha=1$) to `0.544` ($\alpha=0$), but all-venue top-10% share drops `0.643 -> 0.554 -> 0.565` because single-infection households vanish from the active-venue denominator. | **PARTIAL** (passed in `w1, w2b` and `w3b` non-home at $\alpha=0$; failed on `w3b` all-venues) |
| **D(d)** | Even at $\alpha = 0$, top-10 cases' largest-venue-day share in `w1` and `w2b` remains `< 0.50` vs `> 0.80` in `w3b`. | At $\alpha = 0$: `w1` = **`0.250`**, `w2b` = **`0.265`** (both `< 0.50`) vs `w3b` = **`0.861`** (`> 0.80`). | **PASSED** |
| **D(e)** | Across $\alpha \in \{1, 0.5, 0\}$, `|observed_minus_nb_zero| < 0.015` in `w1` and `w2b`, while persisting around `-0.025` to `-0.030` in `w3b`. | `w1`: `-0.0011, -0.0038, -0.0050`. `w2b`: `-0.0072, -0.0064, -0.0067`. `w3b`: **`-0.0291, -0.0273, -0.0252`**. Every cell matches the prediction. | **PASSED** |
