"""SZTE COVID-centre test: all HCWs (10 136) in the new runs against the earlier baseline batch.

The earlier baseline is hcw_interventions/results_hci_split/baseline (20 runs, no redirection, no --hcwFocus).
baseline_szte differs from it only in the extra FHCW output columns, so the two should agree within run-to-run
noise; this is the consistency check. The redirection scenarios then show what pooling the COVID patients does
to the whole HCW population (hospitals and clinics together).

Panels: daily new HCW infections (HCE, 7-day mean), HCW absence (positive + contact quarantine, % of all HCWs),
and the yearly HCW infections relative to the earlier baseline with a bootstrap 95 % CI.

Outputs (outputs/ is git-ignored):  outputs/szte_vs_baseline.png, outputs/szte_vs_baseline.csv,
outputs/szte_vs_baseline_weekly.csv
Run from anywhere:  python compare_baseline.py
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here.parent / "hcw_interventions"))
from hcw import load, metrics  # noqa: E402

OLD = here.parent / "hcw_interventions/results_hci_split/baseline"
RESULTS = here / "results"
OUT = here / "outputs"
START = pd.Timestamp("2020-09-23")  # panSim day 0
N_HCW = metrics.HEALTHCARE_WORKER_COUNT
N_BOOT = 2000
SERIES = {  # name -> (label, colour)
    "korabbi_baseline": ("korábbi baseline (results_hci_split)", "#000000"),
    "baseline_szte": ("új baseline (átirányítás nélkül)", "#7f7f7f"),
    "covidCenter": ("súlyos betegek a JEK-be", "#c0392b"),
    "covidCenterMild": ("+ enyhe esetek is", "#8e44ad"),
    "covidCenterKoranyi": ("JEK + Korányi", "#e67e22"),
}
rng = np.random.default_rng(0)


def load_runs():
    old = load.load_scenario(OLD)
    old.insert(0, "scenario", "korabbi_baseline")
    new = load.load_all(RESULTS)
    df = pd.concat([old, new[new["scenario"].isin(SERIES)]], ignore_index=True)
    df["date"] = START + pd.to_timedelta(df["day"], "D")
    df["absence"] = 100 * (df["HCWH"] + df["HCWD"] + df["HCWQI"] + df["HCWQN"]) / N_HCW
    # 7-day centred mean per run, so the band is the spread of smoothed runs
    df["HCE7"] = df.groupby(["scenario", "run"])["HCE"].transform(
        lambda s: s.rolling(7, center=True, min_periods=1).mean())
    return df


def ratio_ci(x, y):
    bx = x[rng.integers(0, len(x), (N_BOOT, len(x)))].mean(axis=1)
    by = y[rng.integers(0, len(y), (N_BOOT, len(y)))].mean(axis=1)
    return x.mean() / y.mean(), *np.percentile(bx / by, [2.5, 97.5])


def main():
    OUT.mkdir(exist_ok=True)
    df = load_runs()
    names = [s for s in SERIES if s in set(df["scenario"])]
    yearly = df.groupby(["scenario", "run"])["HCE"].sum()
    ref = yearly.loc["korabbi_baseline"].to_numpy(float)
    rows = []
    for s in names:
        x = yearly.loc[s].to_numpy(float)
        r, lo, hi = ratio_ci(x, ref)
        d = df[df["scenario"] == s].groupby("date")["absence"].mean()
        w2 = d.loc["2020-09-23":"2021-01-31"]
        rows.append({"scenario": s, "runs": len(x), "hcw_inf_year": round(x.mean()), "ratio": round(r, 3),
                     "ratio_lo": round(lo, 3), "ratio_hi": round(hi, 3),
                     "absence_peak2": round(w2.max(), 2), "absence_peak2_date": str(w2.idxmax().date())})
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "szte_vs_baseline.csv", index=False)
    print(summary.to_string(index=False))

    g = df.groupby(["scenario", "date"])
    daily = pd.concat({"mean": g[["HCE7", "absence"]].mean(), "q05": g[["HCE7", "absence"]].quantile(0.05),
                       "q95": g[["HCE7", "absence"]].quantile(0.95)}, axis=1)
    weekly = (df.groupby(["scenario", "run", pd.Grouper(key="date", freq="W-SUN")])
                .agg(HCE=("HCE", "sum"), absence=("absence", "mean"))
                .groupby(["scenario", "date"]).mean().round(2))
    weekly.to_csv(OUT / "szte_vs_baseline_weekly.csv")
    plot(daily, summary, names)


def plot(daily, summary, names):
    fig = plt.figure(figsize=(15, 9))
    gs = fig.add_gridspec(2, 2, width_ratios=[2.2, 1])
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[:, 1])]
    for ax, col, ylab in [(axes[0], "HCE7", "új HCW-fertőzés / nap (7 napos átlag)"),
                          (axes[1], "absence", "kieső HCW (%), pozitív + kontaktkarantén")]:
        for s in names:
            lab, c = SERIES[s]
            m, lo, hi = (daily[k].loc[s][col] for k in ("mean", "q05", "q95"))
            lw = 2.2 if s == "korabbi_baseline" else 1.4
            ax.plot(m.index, m, color=c, lw=lw, label=lab, ls="--" if s == "korabbi_baseline" else "-")
            if s in ("korabbi_baseline", "covidCenter"):
                ax.fill_between(m.index, lo, hi, color=c, alpha=0.10, lw=0)
        ax.set_ylabel(ylab)
        ax.grid(alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    axes[0].legend(fontsize=9)
    axes[0].set_title(f"Összes egészségügyi dolgozó ({N_HCW} fő: kórházak és rendelők)")

    ax = axes[2]
    t = summary.set_index("scenario").loc[names]
    y = np.arange(len(names))[::-1]
    ax.errorbar(t["ratio"], y, xerr=[t["ratio"] - t["ratio_lo"], t["ratio_hi"] - t["ratio"]], fmt="o",
                color="black", ecolor="grey", capsize=4)
    for yi, s in zip(y, names):
        ax.scatter(t.loc[s, "ratio"], yi, color=SERIES[s][1], zorder=3, s=50)
        ax.annotate(f"{t.loc[s, 'ratio']:.3f}  ({t.loc[s, 'hcw_inf_year']} fő)", (t.loc[s, "ratio_hi"], yi),
                    xytext=(6, 0), textcoords="offset points", va="center", fontsize=9)
    ax.axvline(1, color="black", lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([SERIES[s][0] for s in names], fontsize=9)
    ax.set_xlabel("éves HCW-fertőzés a korábbi baseline arányában (95% CI)")
    ax.set_xlim(0.75, 1.15)
    ax.grid(alpha=0.3, axis="x")
    fig.suptitle("COVID-kórházas teszt vs. korábbi baseline: összes HCW (átlag, 5–95% sáv, 20-20 futás)")
    fig.tight_layout()
    fig.savefig(OUT / "szte_vs_baseline.png", dpi=150)


if __name__ == "__main__":
    main()
