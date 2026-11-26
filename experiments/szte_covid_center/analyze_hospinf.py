"""SZTE COVID-centre test, round 2 (hospInf, README.md): higher infectiousness of hospitalised COVID patients.

Compares, for the hospital-patient infectiousness 0.1 (the validated value), 0.3, 0.5, 0.7 and 1.0:
  - the HCW absence of the measured group (FHCW, positive + contact quarantine) against the SZTE curve:
    wave-2 peak (mean curve, and the 5-95 % range of per-run peaks), Sept-Oct plateau, RMSE on the SZTE dates;
  - the city epidemic, which the change also touches (non-COVID inpatients get infected too): COVID deaths per
    wave and the peak of hospitalised COVID patients, against the scaled real data (kalibracio.load_real) and
    against the 0.1 runs.

Outputs (outputs/ is git-ignored, the SZTE curve is confidential):
  outputs/hospinf_summary.csv, outputs/hospinf.png
Run from anywhere:  python analyze_hospinf.py
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
sys.path.insert(0, str(here.parent / "hcw_interventions/ODE"))
from hcw import load  # noqa: E402
import kalibracio as K  # noqa: E402

RESULTS = here / "results"
OUT = here / "outputs"
SZTE_CSV = here.parent / "validation_1yr/data/hungarian_data/szte_kieso_digitalizalt.csv"
START = pd.Timestamp("2020-09-23")  # panSim day 0
WAVES = {"w2": ("2020-09-23", "2021-01-31"), "w3": ("2021-02-01", "2021-06-30")}
PLATEAU = ("2020-09-29", "2020-10-27")
# scenario -> (infectiousness of I5_h/I6_h, redirected to the JEK, measured group)
SCEN = {
    "baseline_szte": (0.1, False, "központ"),
    "covidCenter": (0.1, True, "központ"),
    "covidCenter_hospInf03": (0.3, True, "központ"),
    "covidCenter_hospInf05": (0.5, True, "központ"),
    "covidCenter_hospInf07": (0.7, True, "központ"),
    "covidCenter_hospInf10": (1.0, True, "központ"),
    "baseline_hospInf10": (1.0, False, "központ"),
    "covidCenter_focusJEK": (0.1, True, "JEK"),
    "covidCenter_focusJEK_hospInf10": (1.0, True, "JEK"),
}


def main():
    OUT.mkdir(exist_ok=True)
    df = load.load_all(RESULTS)
    df = df[df["scenario"].isin(SCEN)].copy()
    df["date"] = START + pd.to_timedelta(df["day"], "D")
    df["absence"] = 100 * (df["FHCWH"] + df["FHCWD"] + df["FHCWQI"] + df["FHCWQN"]) / df["FHCW"]
    df["hosp"] = df["I5_h"] + df["I6_h"]
    szte = pd.read_csv(SZTE_CSV, comment="#", parse_dates=["datum"]).set_index("datum")["kieso_szazalek"]
    real = K.load_real()
    real.index = START + pd.to_timedelta(np.arange(len(real)), "D")

    names = [s for s in SCEN if s in set(df["scenario"])]
    mean = df.groupby(["scenario", "date"])[["absence", "hosp", "D1"]].mean()
    rows = []
    for s in names:
        inf, redirected, group = SCEN[s]
        d, m = df[df["scenario"] == s], mean.loc[s]
        w2 = m.loc[WAVES["w2"][0]:WAVES["w2"][1], "absence"]
        pk = d[(d["date"] >= WAVES["w2"][0]) & (d["date"] <= WAVES["w2"][1])].groupby("run")["absence"].max()
        row = {"scenario": s, "hosp_infectious": inf, "redirected": redirected, "group": group,
               "FHCW": int(d["FHCW"].iloc[0]), "peak2": round(w2.max(), 2), "peak2_date": str(w2.idxmax().date()),
               "peak2_q05": round(pk.quantile(0.05), 2), "peak2_q95": round(pk.quantile(0.95), 2),
               "plateau": round(m.loc[PLATEAU[0]:PLATEAU[1], "absence"].mean(), 2)}
        for w, (a, b) in WAVES.items():
            obs = szte.loc[a:b]
            row[f"rmse_{w}"] = round(float(np.sqrt(((m["absence"].reindex(obs.index) - obs) ** 2).mean())), 2)
            a0 = max(pd.Timestamp(a) - pd.Timedelta(days=1), m.index[0])
            row[f"deaths_{w}"] = round(float(m.loc[b, "D1"] - m.loc[a0, "D1"]), 1)
            row[f"deaths_{w}_real"] = round(float(real.loc[b, "deaths"] - real.loc[a0, "deaths"]), 1)
        row["hosp_peak"] = round(float(m["hosp"].max()), 1)
        row["hosp_peak_real"] = round(float(real["hosp"].max()), 1)
        row["new_inf_year"] = round(float(d.groupby("run")["NI"].sum().mean()))
        rows.append(row)
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "hospinf_summary.csv", index=False)
    with pd.option_context("display.width", 250, "display.max_columns", 50):
        print(summary.T.to_string())
    print(f"\nSZTE: peak {szte.loc[WAVES['w2'][0]:WAVES['w2'][1]].max()} %, "
          f"plateau {szte.loc[PLATEAU[0]:PLATEAU[1]].mean():.2f} %")
    plot(mean, summary, szte, names)


def plot(mean, summary, szte, names):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.2), gridspec_kw={"width_ratios": [2, 1.2, 1.2]})
    shades = {0.1: 0.3, 0.3: 0.45, 0.5: 0.6, 0.7: 0.8, 1.0: 1.0}

    ax = axes[0]
    for s in [n for n in names if SCEN[n][2] == "központ"]:
        inf, redirected, _ = SCEN[s]
        m = mean.loc[s, "absence"].loc[:"2021-06-30"]
        ax.plot(m.index, m, color="#c0392b" if redirected else "#7f7f7f", alpha=shades[inf], lw=1.8,
                ls="-" if redirected else "--",
                label=f"{'JEK-be irányítva' if redirected else 'átirányítás nélkül'}, fertőzőképesség {inf:g}")
    ax.plot(szte.loc[:"2021-06-30"].index, szte.loc[:"2021-06-30"], color="black", lw=2, marker="o", ms=3,
            label="SZTE (valós)")
    ax.set_title("Kiesés a klinikai központban (17 kórház, 6811 fő)")
    ax.set_ylabel("kieső dolgozók (%), pozitív + kontaktkarantén")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)

    ax = axes[1]
    t = summary.set_index("scenario")
    for (redirected, group), (c, mk, lab) in {(True, "központ"): ("#c0392b", "o", "központ, JEK-be irányítva"),
                                              (False, "központ"): ("#7f7f7f", "s", "központ, átirányítás nélkül"),
                                              (True, "JEK"): ("#2c3e50", "^", "JEK dolgozói, irányítva")}.items():
        sub = t[(t["redirected"] == redirected) & (t["group"] == group)].sort_values("hosp_infectious")
        if sub.empty:
            continue
        # point = peak of the mean curve; bar = 5-95 % of per-run peaks (runs peak at different dates, so the
        # mean curve's peak can sit below the bar)
        ax.plot(sub["hosp_infectious"], sub["peak2"], color=c, marker=mk, label=lab)
        ax.vlines(sub["hosp_infectious"], sub["peak2_q05"], sub["peak2_q95"], color=c, alpha=0.5, lw=3)
    ax.axhline(szte.loc[WAVES["w2"][0]:WAVES["w2"][1]].max(), color="black", ls=":", label="SZTE csúcs")
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("kórházi COVID-betegek fertőzőképessége (I5_h, I6_h)")
    ax.set_ylabel("kiesés 2. hullámbeli csúcsa (%), futásonkénti 5–95%")
    ax.set_title("Csúcs a fertőzőképesség függvényében")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)

    ax = axes[2]
    sub = t[t["group"] == "központ"]
    x = np.arange(len(sub))
    for i, (w, lab) in enumerate([("w2", "2. hullám"), ("w3", "3. hullám")]):
        ax.bar(x + (i - 0.5) * 0.38, sub[f"deaths_{w}"] / sub[f"deaths_{w}_real"], 0.38, label=lab,
               color=["#5d6d7e", "#aab7b8"][i])
    ax.axhline(1, color="black", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{'irányítva' if r else 'nincs'}\n{i:g}" for r, i in zip(sub["redirected"],
                                                                                 sub["hosp_infectious"])],
                       fontsize=8)
    ax.set_ylabel("COVID-halálozás / valós (skálázott)")
    ax.set_title("Városi halálozás hullámonként")
    ax.grid(alpha=0.3, axis="y")
    ax.legend(fontsize=8)
    fig.suptitle("A kórházi COVID-betegek fertőzőképességének emelése (20 futás forgatókönyvenként)")
    fig.tight_layout()
    fig.savefig(OUT / "hospinf.png", dpi=150)


if __name__ == "__main__":
    main()
