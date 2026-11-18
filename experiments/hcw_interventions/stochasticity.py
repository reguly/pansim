"""Run-to-run (stochastic) variability of panSim: how much do the 20 unseeded runs of a scenario differ?

Complements uncertainty.py (bootstrap CIs of the HCW metrics' means) with:
  stochasticity_per_run.csv      per scenario x metric: mean, SD, CV, min, max, 5-95% range of the
                                 per-run values, for population AND HCW outcomes
  stochasticity_effects.csv      each scenario's effect on HCW infections vs baseline, in units of
                                 the run-to-run SD (Cohen's d), and the smallest effect 20 runs can
                                 detect (two-sided 5%, 80% power)
  stochasticity_replication.csv  two independent baseline batches (results/ and
                                 results_hci_split/, same command, no seeds): do they agree?
  stochasticity_baseline.png     baseline: every run as a thin line + mean, and the daily CV

Usage: python stochasticity.py [results_dir] [second_baseline_dir] [out_dir]
Defaults: results/, results_hci_split/baseline/, outputs/stochasticity/ (relative to this file).
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from hcw import load, metrics  # noqa: E402

here = Path(__file__).parent
results_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else here / "results"
second_baseline = Path(sys.argv[2]) if len(sys.argv) > 2 else here / "results_hci_split" / "baseline"
out = Path(sys.argv[3]) if len(sys.argv) > 3 else here / "outputs" / "stochasticity"
out.mkdir(parents=True, exist_ok=True)

START = pd.Timestamp("2020-09-23")
WAVE2_END = 131                         # 2021-02-01: wave 2 = days 0-130, wave 3 = days 131-
LABELS = {"total_infections": "total infections", "hcw_infections": "HCW infections",
          "deaths": "COVID deaths", "peak_hosp_wave2": "hospital peak, wave 2",
          "peak_hosp_wave3": "hospital peak, wave 3", "peak_day_wave2": "day of hospital peak, wave 2",
          "peak_hci": "HCI peak (%)", "incidence_RR": "HCW incidence RR"}


def add_derived(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["hosp"] = df["I5_h"] + df["I6_h"]
    return df


def per_run_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (scenario, run). Per-run scalars, not daily values: days within a run are
    autocorrelated, runs are independent."""
    rows = []
    for (scen, run), d in df.groupby(["scenario", "run"]):
        d = d.sort_values("day")
        w2, w3 = d[d.day < WAVE2_END], d[d.day >= WAVE2_END]
        rows.append({"scenario": scen, "run": run,
                     "total_infections": d["NI"].sum(), "hcw_infections": d["HCE"].sum(),
                     "deaths": d["D1"].iloc[-1] - d["D1"].iloc[0],
                     "peak_hosp_wave2": w2["hosp"].max(), "peak_hosp_wave3": w3["hosp"].max(),
                     "peak_day_wave2": int(w2.loc[w2["hosp"].idxmax(), "day"]),
                     "peak_hci": d["HCI"].max()})
    out_ = pd.DataFrame(rows)
    rr = metrics.per_run(df)[["scenario", "run", "incidence_RR"]]
    return out_.merge(rr, on=["scenario", "run"])


df = add_derived(load.load_all(results_dir))
runs = per_run_metrics(df)
cols = list(LABELS)

# ---------- 1. spread of per-run values ----------
summ = []
for scen, r in runs.groupby("scenario"):
    for c in cols:
        x = r[c].astype(float)
        summ.append({"scenario": scen, "metric": c, "n_runs": len(x), "mean": x.mean(), "sd": x.std(ddof=1),
                     "cv_pct": 100 * x.std(ddof=1) / x.mean(), "min": x.min(), "max": x.max(),
                     "q05": x.quantile(0.05), "q95": x.quantile(0.95),
                     "range_pct_of_mean": 100 * (x.max() - x.min()) / x.mean()})
summ = pd.DataFrame(summ)
summ.round(3).to_csv(out / "stochasticity_per_run.csv", index=False)
print("Baseline, per-run spread (20 runs):")
print(summ[summ.scenario == "baseline"].set_index("metric")[["mean", "sd", "cv_pct", "min", "max"]].round(2).to_string())
print("\nCV (%) of each metric across scenarios - median and range:")
cv = summ.pivot(index="metric", columns="scenario", values="cv_pct")
print(pd.DataFrame({"median": cv.median(axis=1), "min": cv.min(axis=1), "max": cv.max(axis=1)}).round(2).to_string())

# ---------- 2. effects in units of noise ----------
base = runs[runs.scenario == "baseline"]["hcw_infections"]
n = len(base)
mde_sd = (stats.norm.ppf(0.975) + stats.norm.ppf(0.8)) * np.sqrt(2 / n)   # in SD units, 80% power
eff = []
for scen, r in runs.groupby("scenario"):
    if scen == "baseline":
        continue
    x = r["hcw_infections"]
    pooled = np.sqrt((x.var(ddof=1) + base.var(ddof=1)) / 2)
    eff.append({"scenario": scen, "mean_diff": x.mean() - base.mean(),
                "diff_pct": 100 * (x.mean() / base.mean() - 1), "cohens_d": (x.mean() - base.mean()) / pooled,
                "p_welch": stats.ttest_ind(x, base, equal_var=False).pvalue})
eff = pd.DataFrame(eff).sort_values("diff_pct")
eff.round(4).to_csv(out / "stochasticity_effects.csv", index=False)
print(f"\nSmallest detectable effect on HCW infections with {n} vs {n} runs (5%, 80% power): "
      f"{mde_sd:.2f} SD = {100 * mde_sd * base.std(ddof=1) / base.mean():.1f}% of the baseline mean")
print(eff.round(3).to_string(index=False))

# ---------- 3. replication: two independent baseline batches ----------
if (second_baseline / "all_runs.tsv").exists():
    df2 = add_derived(load.load_scenario(second_baseline))
    df2.insert(0, "scenario", "baseline_rerun")
    runs2 = per_run_metrics(df2)
    rep = []
    for c in cols:
        a, b = base_all = runs[runs.scenario == "baseline"][c].astype(float), runs2[c].astype(float)
        rep.append({"metric": c, "batch1_mean": a.mean(), "batch2_mean": b.mean(),
                    "diff_pct": 100 * (b.mean() / a.mean() - 1), "batch1_sd": a.std(ddof=1), "batch2_sd": b.std(ddof=1),
                    "p_welch": stats.ttest_ind(a, b, equal_var=False).pvalue,
                    "p_levene_sd": stats.levene(a, b).pvalue})
    rep = pd.DataFrame(rep)
    rep.round(4).to_csv(out / "stochasticity_replication.csv", index=False)
    print("\nReplication (results/baseline vs results_hci_split/baseline):")
    print(rep.round(3).to_string(index=False))

# ---------- 4. figure: baseline runs over time + daily CV ----------
b = df[df.scenario == "baseline"].copy()
b["NI7"] = b.groupby("run")["NI"].transform(lambda s: s.rolling(7, center=True, min_periods=1).mean())
b["HCE7"] = b.groupby("run")["HCE"].transform(lambda s: s.rolling(7, center=True, min_periods=1).mean())
panels = [("hosp", "COVID patients in hospital"), ("NI7", "new infections per day (7-day mean)"),
          ("HCE7", "new HCW infections per day (7-day mean)"), ("HCI", "HCI: HCWs infected or quarantined (%)")]
fig, axes = plt.subplots(len(panels) + 1, 1, figsize=(10, 12), sharex=True, layout="constrained")
dates = lambda d: START + pd.to_timedelta(np.asarray(d), "D")  # noqa: E731
for ax, (col, title) in zip(axes, panels):
    for _, d in b.groupby("run"):
        ax.plot(dates(d["day"]), d[col], color="#9e9e9e", lw=0.6, alpha=0.7)
    m = b.groupby("day")[col].mean()
    ax.plot(dates(m.index), m, color="#2a78d6", lw=2, label="mean of 20 runs")
    ax.set_title(title, loc="left", fontsize=11)
    ax.grid(axis="y", color="0.9")
    ax.spines[["top", "right"]].set_visible(False)
axes[0].legend(frameon=False, loc="upper right")
ax = axes[-1]
for col, title, colour in [("hosp", "hospital", "#222222"), ("NI7", "new infections", "#2a78d6"),
                           ("HCE7", "new HCW infections", "#e8710a")]:
    g = b.groupby("day")[col]
    ok = g.mean() >= (5 if col != "hosp" else 10)        # CV is meaningless near zero
    ax.plot(dates(g.mean().index), (100 * g.std() / g.mean()).where(ok), color=colour, lw=1.6, label=title)
ax.set_title("Run-to-run CV of the daily value (%, days with enough cases)", loc="left", fontsize=11)
ax.legend(frameon=False, loc="upper right")
ax.grid(axis="y", color="0.9")
ax.spines[["top", "right"]].set_visible(False)
ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
fig.suptitle("panSim baseline: 20 unseeded runs", x=0.01, ha="left", fontsize=13)
fig.savefig(out / "stochasticity_baseline.png", dpi=150)
print("Output:", out)
