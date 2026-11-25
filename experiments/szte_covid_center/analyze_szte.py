"""SZTE COVID-centre test (README.md): the chosen workplaces' HCW absence against the SZTE curve.

For every scenario in results/ (20 runs x 364 days):
  - absence of the focus HCWs (FHCW), two definitions as in hci_split.py:
      pos = (FHCWH + FHCWD) / FHCW, all = pos + (FHCWQI + FHCWQN) / FHCW
  - the same for every other HCW (all HCW minus the focus group), as a control
  - wave-2 peak, the Sept-Oct plateau, cumulative wave-2 infections per 100 staff, and the RMSE
    against the SZTE curve on its own dates (wave 2 and wave 3)

Outputs (outputs/ is git-ignored, the SZTE curve is confidential):
  outputs/szte_summary.csv, outputs/szte_daily.csv, outputs/szte_absence.png

Run from anywhere:  python analyze_szte.py
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

RESULTS = here / "results"
OUT = here / "outputs"
SZTE_CSV = here.parent / "validation_1yr/data/hungarian_data/szte_kieso_digitalizalt.csv"
START = pd.Timestamp("2020-09-23")  # panSim day 0
N_HCW = metrics.HEALTHCARE_WORKER_COUNT
WAVE2 = ("2020-09-23", "2021-01-31")
WAVE3 = ("2021-02-01", "2021-06-30")
PLATEAU = ("2020-09-29", "2020-10-27")  # SZTE: 3-4 % before the November rise
ORDER = ["baseline_szte", "covidCenter", "covidCenterMild", "covidCenterKoranyi",
         "baseline_focusJEK", "covidCenter_focusJEK"]


def main():
    OUT.mkdir(exist_ok=True)
    df = load.load_all(RESULTS)
    df["date"] = START + pd.to_timedelta(df["day"], "D")
    f_pos, f_q = df["FHCWH"] + df["FHCWD"], df["FHCWQI"] + df["FHCWQN"]
    o_pos = df["HCWH"] + df["HCWD"] - f_pos
    o_q = df["HCWQI"] + df["HCWQN"] - f_q
    n_other = N_HCW - df["FHCW"]
    df["focus_pos"] = 100 * f_pos / df["FHCW"]
    df["focus_all"] = 100 * (f_pos + f_q) / df["FHCW"]
    df["other_pos"] = 100 * o_pos / n_other
    df["other_all"] = 100 * (o_pos + o_q) / n_other

    szte = pd.read_csv(SZTE_CSV, comment="#", parse_dates=["datum"]).set_index("datum")["kieso_szazalek"]
    cols = ["focus_pos", "focus_all", "other_pos", "other_all"]
    g = df.groupby(["scenario", "date"])[cols]
    daily = pd.concat({"mean": g.mean(), "q05": g.quantile(0.05), "q95": g.quantile(0.95)}, axis=1)
    daily.to_csv(OUT / "szte_daily.csv")

    rows = []
    scenarios = [s for s in ORDER if s in set(df["scenario"])]
    for s in scenarios:
        d = df[df["scenario"] == s]
        m = daily["mean"].loc[s]
        w2 = m.loc[WAVE2[0]:WAVE2[1]]
        row = {"scenario": s, "FHCW": int(d["FHCW"].iloc[0])}
        for c in ("focus_all", "focus_pos", "other_all"):
            row[f"{c}_peak2"] = round(w2[c].max(), 2)
            row[f"{c}_peak2_date"] = str(w2[c].idxmax().date())
            row[f"{c}_plateau"] = round(m.loc[PLATEAU[0]:PLATEAU[1], c].mean(), 2)
        # per-run peak spread of the main metric
        pk = d[(d["date"] >= WAVE2[0]) & (d["date"] <= WAVE2[1])].groupby("run")["focus_all"].max()
        row["focus_all_peak2_q05"], row["focus_all_peak2_q95"] = (round(pk.quantile(q), 2) for q in (0.05, 0.95))
        # cumulative wave-2 infections per 100 staff: focus vs the other HCWs
        w2d = d[(d["date"] >= WAVE2[0]) & (d["date"] <= WAVE2[1])].groupby("run")[["FHCE", "HCE"]].sum().mean()
        row["inf100_focus_w2"] = round(100 * w2d["FHCE"] / row["FHCW"], 1)
        row["inf100_other_w2"] = round(100 * (w2d["HCE"] - w2d["FHCE"]) / (N_HCW - row["FHCW"]), 1)
        for name, (a, b) in {"w2": WAVE2, "w3": WAVE3}.items():
            obs = szte.loc[a:b]
            sim = m["focus_all"].reindex(obs.index)
            row[f"rmse_{name}"] = round(float(np.sqrt(((sim - obs) ** 2).mean())), 2)
        rows.append(row)
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "szte_summary.csv", index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 50):
        print(summary.T.to_string())
    print(f"\nSZTE: peak {szte.loc[WAVE2[0]:WAVE2[1]].max()} % on "
          f"{szte.loc[WAVE2[0]:WAVE2[1]].idxmax().date()}, plateau {szte.loc[PLATEAU[0]:PLATEAU[1]].mean():.2f} %")

    plot(daily, szte, scenarios)


def plot(daily, szte, scenarios):
    panels = [("Teljes klinikai központ (17 kórház, 6811 fő)", ["baseline_szte", "covidCenter", "covidCenterMild",
                                                                "covidCenterKoranyi"]),
              ("A JEK dolgozói (1802 fő)", ["baseline_focusJEK", "covidCenter_focusJEK"])]
    colours = {"baseline_szte": "#7f7f7f", "covidCenter": "#c0392b", "covidCenterMild": "#8e44ad",
               "covidCenterKoranyi": "#e67e22", "baseline_focusJEK": "#7f7f7f", "covidCenter_focusJEK": "#c0392b"}
    labels = {"baseline_szte": "átirányítás nélkül", "covidCenter": "súlyos betegek a JEK-be",
              "covidCenterMild": "+ enyhe esetek is", "covidCenterKoranyi": "JEK + Korányi",
              "baseline_focusJEK": "átirányítás nélkül", "covidCenter_focusJEK": "súlyos betegek a JEK-be"}
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, (title, ss) in zip(axes, panels):
        for s in [x for x in ss if x in scenarios]:
            m, lo, hi = (daily[k].loc[s]["focus_all"].loc[:"2021-06-30"] for k in ("mean", "q05", "q95"))
            ax.plot(m.index, m, color=colours[s], lw=1.6, label=labels[s])
            ax.fill_between(m.index, lo, hi, color=colours[s], alpha=0.12, lw=0)
        ax.plot(szte.loc[:"2021-06-30"].index, szte.loc[:"2021-06-30"], color="black", lw=2, marker="o", ms=3,
                label="SZTE (valós)")
        ax.set_title(title)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        ax.grid(alpha=0.3)
        ax.legend(fontsize=9)
    axes[0].set_ylabel("kieső dolgozók (%), pozitív + kontaktkaranténban")
    fig.suptitle("SZTE COVID-központ teszt: kiesés a kiválasztott dolgozói körben (átlag, 5-95% sáv, 20 futás)")
    fig.tight_layout()
    fig.savefig(OUT / "szte_absence.png", dpi=150)


if __name__ == "__main__":
    main()
