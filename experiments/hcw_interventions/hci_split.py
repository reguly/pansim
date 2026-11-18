"""HCI split for the quarantine question: results_hci_split/<scenario>/all_runs.tsv ->
outputs/hci_split/{hci_split_summary.csv, hci_split_stacked.png, hci_split_absence.png}

panSim's HCI (% of HCWs infected OR quarantined) mixes people who are off work with people who
are still working, so it cannot be compared with a hospital's absent-staff curve directly. The
five split columns (src/runtime/simulationOrchestration.cpp) are mutually exclusive counts that
sum to the HCI count:
  HCWH  hospitalized                            - absent
  HCWD  diagnosed and isolating                 - absent (except under --quarantinePolicy 0,
                                                  where diagnosed agents are not isolated)
  HCWQI contact-quarantined, infected            - absent if contacts are quarantined
  HCWQN contact-quarantined, not infected        - absent if contacts are quarantined
  HCWU  infected, undetected, still working      - not absent
Two absence definitions bracket the unknown definition of the SZTE curve: positives only
(HCWH + HCWD) and positives plus contact quarantine (+ HCWQI + HCWQN).

If the git-ignored SZTE curve (NDA) and the ODE calibration output exist, they are overlaid on the
absence panel; outputs/ is git-ignored, so the figures never reach the repo.

Usage: python hci_split.py [results_dir] [out_dir]
Defaults: results_hci_split/, outputs/hci_split/ (relative to this file).
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
results_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else here / "results_hci_split"
out = Path(sys.argv[2]) if len(sys.argv) > 2 else here / "outputs" / "hci_split"
out.mkdir(parents=True, exist_ok=True)

START = pd.Timestamp("2020-09-23")          # panSim day 0 (--startDate 267)
N_H = metrics.HEALTHCARE_WORKER_COUNT
SPLIT = ["HCWH", "HCWD", "HCWQI", "HCWQN", "HCWU"]
LABELS = {"HCWH": "hospitalized", "HCWD": "diagnosed, isolating",
          "HCWQI": "contact-quarantined, infected", "HCWQN": "contact-quarantined, not infected",
          "HCWU": "infected, undetected, working"}
COLOURS = {"HCWH": "#8c1d18", "HCWD": "#e8710a", "HCWQI": "#6a3d9a", "HCWQN": "#b9a3d6",
           "HCWU": "#9e9e9e"}
ORDER = ["baseline", "hcwNoQuarantine", "hcwNoQuarantineMar21", "quarantine0"]
SCEN_COLOURS = {"baseline": "#222222", "hcwNoQuarantine": "#2a78d6",
                "hcwNoQuarantineMar21": "#1a9e77", "quarantine0": "#d62728"}
WAVES = {"wave2": ("2020-09-23", "2021-01-31"), "wave3": ("2021-02-01", "2021-06-30")}
SZTE_UNTIL = pd.Timestamp("2021-06-10")  # after this the digitized curve is 0 = missing data, not real 0
SZTE_CSV = here.parents[1] / "experiments/validation_1yr/data/hungarian_data/szte_kieso_digitalizalt.csv"
ODE_PARAMS = here / "ODE/kalibracio_kimenet/parameterek.json"

df = load.load_all(results_dir)
missing = [c for c in SPLIT if c not in df.columns]
if missing:
    sys.exit(f"{results_dir}: no HCI split columns {missing} - re-run with a panSim built at 5fce584 or later")
scenarios = [s for s in ORDER if s in set(df["scenario"])] + sorted(set(df["scenario"]) - set(ORDER))

# The split must reproduce HCI exactly (HCI = integer-truncated % of the summed count).
ok = (df[SPLIT].sum(axis=1) * 100 // N_H == df["HCI"])
print(f"HCI consistency: {ok.mean():.1%} of {len(df)} rows match")


def absence(d: pd.DataFrame, scenario: str, with_contacts: bool) -> pd.Series:
    """Absent HCW count per row. Under quarantine0 diagnosed agents are not isolated, so only the
    hospitalized are absent (and there is no contact quarantine to add)."""
    if scenario == "quarantine0":
        return d["HCWH"].astype(float)
    a = d["HCWH"] + d["HCWD"]
    if with_contacts:
        a = a + d["HCWQI"] + d["HCWQN"]
    return a.astype(float)


for name, d in df.groupby("scenario"):
    df.loc[d.index, "absent_pos"] = absence(d, name, False)
    df.loc[d.index, "absent_all"] = absence(d, name, True)

mean = df.groupby(["scenario", "day"])[SPLIT + ["absent_pos", "absent_all", "HCE"]].mean()
dates = lambda idx: START + pd.to_timedelta(np.asarray(idx), "D")  # noqa: E731


def window_peak(s: pd.Series, a: str, b: str):
    s = pd.Series(s.to_numpy(), index=dates(s.index))[a:b]
    if s.empty:
        return np.nan, ""
    return round(float(s.max()), 2), str(s.idxmax().date())


def mean_ci(x: pd.Series):
    x = x.dropna()
    m = x.mean()
    if len(x) < 2:
        return m, np.nan, np.nan
    h = stats.t.ppf(0.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
    return m, m - h, m + h


# ---------- summary table ----------
runs = metrics.per_run(df)
per_run_extra = df.groupby(["scenario", "run"]).agg(
    absent_pos_days=("absent_pos", "sum"), absent_all_days=("absent_all", "sum")).reset_index()
runs = runs.merge(per_run_extra, on=["scenario", "run"])
base_inf = runs.loc[runs.scenario == "baseline", "hcw_infections"].mean()
sig = metrics.mann_whitney_vs_baseline(runs, "hcw_infections").set_index("scenario")

rows = []
for scen in scenarios:
    r = runs[runs.scenario == scen]
    m = mean.loc[scen]
    inf, lo, hi = mean_ci(r["hcw_infections"])
    row = {"scenario": scen, "runs": len(r), "days": int(r["n_days"].median()),
           "hcw_infections": round(inf, 1), "hcw_infections_ci95": f"{lo:.0f}-{hi:.0f}",
           "ratio_vs_baseline": round(inf / base_inf, 3) if base_inf else np.nan,
           "p_vs_baseline": sig["p_value"].get(scen, np.nan),
           "incidence_RR": round(r["incidence_RR"].mean(), 3),
           "absent_person_days_positives": round(r["absent_pos_days"].mean()),
           "absent_person_days_with_contacts": round(r["absent_all_days"].mean())}
    for w, (a, b) in WAVES.items():
        for col, lab in [("absent_pos", "positives"), ("absent_all", "with_contacts")]:
            pk, day = window_peak(100 * m[col] / N_H, a, b)
            row[f"peak_absent_pct_{lab}_{w}"] = pk
            row[f"peak_date_{lab}_{w}"] = day
    # composition of the HCI count on the day it peaks in wave 2 (share of each category)
    hci_count = m[SPLIT].sum(axis=1)
    w2 = hci_count[dates(hci_count.index) <= pd.Timestamp(WAVES["wave2"][1])]
    if not w2.empty and w2.max() > 0:
        peak_day = w2.idxmax()
        for c in SPLIT:
            row[f"share_at_wave2_peak_{c}"] = round(float(m.loc[peak_day, c] / hci_count[peak_day]), 3)
    rows.append(row)
summary = pd.DataFrame(rows)
summary.to_csv(out / "hci_split_summary.csv", index=False)
print(summary.T.to_string(header=False))

# ---------- figure 1: stacked composition per scenario ----------
fig, axes = plt.subplots(len(scenarios), 1, figsize=(10, 2.6 * len(scenarios)), sharex=True, sharey=True,
                         layout="constrained")
axes = np.atleast_1d(axes)
for ax, scen in zip(axes, scenarios):
    m = mean.loc[scen]
    ax.stackplot(dates(m.index), *[100 * m[c] / N_H for c in SPLIT], colors=[COLOURS[c] for c in SPLIT],
                 labels=[LABELS[c] for c in SPLIT], linewidth=0)
    ax.set_title(scen + (" (diagnosed HCWs are not isolated here)" if scen == "quarantine0" else ""),
                 loc="left", fontsize=11)
    ax.set_ylabel("% of HCWs")
    ax.grid(axis="y", color="0.9")
    ax.spines[["top", "right"]].set_visible(False)
axes[0].legend(loc="upper right", fontsize=8.5, frameon=False, reverse=True)
axes[-1].xaxis.set_major_formatter(mdates.ConciseDateFormatter(axes[-1].xaxis.get_major_locator()))
fig.suptitle("HCWs counted in HCI, by status (mean of runs)", x=0.01, ha="left", fontsize=13)
fig.savefig(out / "hci_split_stacked.png", dpi=150)
plt.close(fig)

# ---------- figure 2: absence vs the SZTE curve, and HCW incidence ----------
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 9), sharex=True, layout="constrained")
mb = mean.loc["baseline"] if "baseline" in scenarios else None
if mb is not None:
    ax1.plot(dates(mb.index), 100 * mb["absent_pos"] / N_H, color="#e8710a", lw=2, label="panSim: positives only")
    ax1.plot(dates(mb.index), 100 * mb["absent_all"] / N_H, color="#6a3d9a", lw=2,
             label="panSim: positives + contact quarantine")
    ax1.fill_between(dates(mb.index), 100 * mb["absent_pos"] / N_H, 100 * mb["absent_all"] / N_H,
                     color="#b9a3d6", alpha=0.3, lw=0)
if SZTE_CSV.exists():
    szte = pd.read_csv(SZTE_CSV, comment="#", parse_dates=["datum"])
    szte = szte[szte["datum"] <= SZTE_UNTIL]
    ax1.plot(szte["datum"], szte["kieso_szazalek"], color="#222222", lw=2, label="SZTE absent staff (real)")
if ODE_PARAMS.exists():
    sys.path.insert(0, str(here / "ODE"))
    import karanten_kiserlet as KK  # noqa: E402
    import kalibracio as K  # noqa: E402
    _, pB = KK.load_params()
    m_sim, real = K.load_sim(), K.load_real()
    day = m_sim.index.values.astype(float)
    inp_B = K.make_inputs(day, m_sim["alpha"].values, m_sim["delta"].values, real["doses"].values,
                          hcw_doses_until=(94, 130))
    oB = K.simulate(pB, inp_B, K.initial_state(pB["I0"], real["hosp"].iloc[0],
                                               m_sim["R"].iloc[0] + m_sim["R_h"].iloc[0], 0.0, I_h0_pct=pB["I_h0_pct"]))
    ax1.plot(dates(oB.index), oB["kieso_pct"], color="#1a9e77", lw=1.5, ls="--", label="ODE (B), fitted to SZTE")
ax1.set_title("Baseline: absent HCWs under two definitions", loc="left", fontsize=11)
ax1.set_ylabel("% of HCWs")

for scen in scenarios:
    m = mean.loc[scen]
    lab = scen + (" (hospitalized only: no isolation)" if scen == "quarantine0" else "")
    ax2.plot(dates(m.index), 100 * m["absent_all"] / N_H, color=SCEN_COLOURS.get(scen), lw=1.8, label=lab)
    ax3.plot(dates(m.index), m["HCE"].rolling(7, center=True, min_periods=1).mean(),
             color=SCEN_COLOURS.get(scen), lw=1.8, label=scen)
ax2.set_title("Absent HCWs (positives + contact quarantine), by scenario", loc="left", fontsize=11)
ax2.set_ylabel("% of HCWs")
ax3.set_title("New HCW infections per day (7-day mean)", loc="left", fontsize=11)
ax3.set_ylabel("HCWs/day")
for ax in (ax1, ax2, ax3):
    ax.legend(fontsize=8.5, frameon=False, loc="upper right")
    ax.grid(axis="y", color="0.9")
    ax.spines[["top", "right"]].set_visible(False)
ax3.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax3.xaxis.get_major_locator()))
fig.savefig(out / "hci_split_absence.png", dpi=150)
plt.close(fig)
print("Output:", out)
