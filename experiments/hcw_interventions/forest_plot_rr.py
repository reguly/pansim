"""Forest plot of the HCW vulnerability under each scenario: incidence ratio of healthcare workers
vs the rest of the population (per-capita daily new infections, mean over the 20 runs of the
per-run ratio; 95% bootstrap CI of that mean). The baseline (real-world policies) is one row;
1 means HCWs and everyone else are equally affected. Reads outputs/uncertainty_ci.csv
(run uncertainty.py first).

Colour compares each scenario's CI with 1: entirely below 1 (HCWs less affected than the rest of
the population), entirely above 1 (more affected), or including 1 (equal risk). A dotted line marks
the baseline mean so the scenarios can also be read against it.

Usage: python forest_plot_rr.py [--all] [--no-table] [out_dir]
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

here = Path(__file__).parent
args = [a for a in sys.argv[1:] if not a.startswith("--")]
no_table = "--no-table" in sys.argv
show_all = "--all" in sys.argv
out = Path(args[0]) if args else here / "outputs"

LABELS = {
    "hcwPPE": "Hospital PPE: 70% lower infectiousness in hospitals and clinics",
    "hcwDailyTest": "Hospital staff 95% test chance per day, retest after 1 day, until day 258",
    "hiTest": "Hospital staff test chance 50% per day instead of 0.5%, until day 258",
    "longQuarantine": "Quarantine after diagnosis lasts 21 days instead of 10",
    "closuresNone": "All closure rules removed (also no new variants; hospital testing stays low)",
    "noVaccHCW": "HCWs vaccinated as general adults, no longer first",
    "quarantine0": "No quarantine of diagnosed cases, households or workplaces",
    "noVacc": "No vaccination programme: no doses given",
    "closuresNone_hiTest": "No closure rules, hospital staff test chance 50% per day all year",
    "noVaccHCW_hiTest": "HCWs vaccinated as general adults + hospital test chance 50%, to day 258",
    "quarantine0_hiTest": "No quarantine + hospital staff test chance 50% per day, to day 258",
    "quarantine0_noVaccHCW": "No quarantine + HCWs vaccinated as general adults",
}
NUMBER = {name: k + 1 for k, name in enumerate(list(LABELS))}
SINGLE = ["hcwPPE", "hcwDailyTest", "hiTest", "longQuarantine", "closuresNone",
          "noVaccHCW", "quarantine0", "noVacc"]

# Diverging pair from the key-metrics palette + neutral grey for "not distinguishable".
PROTECT, HARM, NEUTRAL = "#2e9e4f", "#d62728", "#8a8f98"
DOT = "#2a78d6"   # baseline-mean line
ARROW_LESS, ARROW_MORE = "#2e9e4f", "#d62728"   # direction arrows: green = lower risk, red = higher risk
BASE = "#4a4f57"  # baseline reference row

ci = pd.read_csv(out / "uncertainty_ci.csv")
d = ci[ci.metric == "incidence_RR"].set_index("scenario")
bl = d.loc["baseline"]
names = (list(LABELS) if show_all else SINGLE) + ["baseline"]
eff = d.loc[names, ["mean", "mean_ci95_lo", "mean_ci95_hi"]].rename(
    columns={"mean": "ratio", "mean_ci95_lo": "ratio_ci95_lo", "mean_ci95_hi": "ratio_ci95_hi"})
eff = eff.sort_values("ratio")
LABELS["baseline"] = "Actual policies, calibrated to real data from Szeged"


def colour(lo, hi):
    """Compare the CI with 1 (HCWs and the rest of the population equally affected)."""
    return PROTECT if hi < 1 else HARM if lo > 1 else NEUTRAL


POINT = "#1a1a1a"


def draw(a, x, y, lo, hi, c):
    """CI as a coloured bar with end caps; the mean is a small dark point on top of it."""
    a.hlines(y, lo, hi, color=c, lw=3, zorder=2)
    a.vlines([lo, hi], y - 0.12, y + 0.12, color=c, lw=2.5, zorder=2)
    a.plot(x, y, "D", color=POINT, ms=3.5, zorder=3)


plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Times", "Liberation Serif", "DejaVu Serif"],
                     "mathtext.fontset": "stix", "font.size": 13, "axes.edgecolor": "0.4"})
n = len(eff)
# Layout in inches so row spacing stays fixed regardless of the number of scenarios.
TABLE_ROW = 0.27
TABLE_H = 0.0 if no_table else 0.6 + TABLE_ROW * n   # scenario key under the legend
LEGEND_H, XAXIS_H = 1.1, 0.95
W, TOP, ROW_H = 7.5, 0.7, 0.31
BOTTOM = TABLE_H + LEGEND_H + XAXIS_H
axB_h = ROW_H * (n + 1.2)
H = TOP + axB_h + BOTTOM
VALUE_COL = 1.75  # inches reserved right of the axes for the ratio and CI column
LEFT, RIGHT = 0.12, 1 - VALUE_COL / W
fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([LEFT, BOTTOM / H, RIGHT - LEFT, axB_h / H])

ax.axvline(1, color="0.35", lw=1, ls="--", zorder=0)   # reference: equal risk
ax.vlines(bl["mean"], -0.7, n - 0.4, color=DOT, lw=1.4, ls=":", zorder=0)   # baseline mean, stops below the arrows
# Scenario effect on total HCW infections vs baseline
for i, (scen, r) in enumerate(eff.iterrows()):
    c = DOT if scen == "baseline" else colour(r.ratio_ci95_lo, r.ratio_ci95_hi)
    draw(ax, r.ratio, i, r.ratio_ci95_lo, r.ratio_ci95_hi, c)
    txt = f"{r.ratio:.2f}  [{r.ratio_ci95_lo:.2f}, {r.ratio_ci95_hi:.2f}]"
    ax.annotate(txt, xy=(1, i), xycoords=("axes fraction", "data"), xytext=(12, 0),
                textcoords="offset points", va="center", ha="left", fontsize=12.5)
ax.annotate("ratio [95% CI]", xy=(1, n + 0.1), xycoords=("axes fraction", "data"), xytext=(12, 0),
            textcoords="offset points", va="center", ha="left", fontsize=12.5, fontweight="bold")
# One-line row labels: bold scenario id, then the description. Ids are fixed per scenario (order of
# LABELS: single changes first, then the combinations) so the text can refer to them.
def row_label(scen):
    return r"$\mathbf{Baseline}$" if scen == "baseline" else rf"$\mathbf{{S{NUMBER[scen]}}}$"


ax.set_yticks(range(n)); ax.set_yticklabels([row_label(sc) for sc in eff.index], fontsize=13)
ax.set_xlabel("HCW / rest of population incidence ratio; 1 means equal risk")

ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0)
ax.set_xlim(0.6, 2.0)
ax.set_xticks([0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0])
ax.set_xticklabels(["0.6", "0.8", "1.0", "1.2", "1.4", "1.6", "1.8", "2.0"])
ax.minorticks_off()
ytop = n + 0.05
ax.annotate("", xy=(0.65, ytop), xytext=(0.96, ytop), arrowprops=dict(arrowstyle="->", color=ARROW_LESS))
ax.annotate("", xy=(1.95, ytop), xytext=(1.04, ytop), arrowprops=dict(arrowstyle="->", color=ARROW_MORE))
ax.text(0.98, ytop + 0.3, "HCWs less affected", ha="right", fontsize=11.5, color="black")
ax.text(1.03, ytop + 0.3, "HCWs more affected", ha="left", fontsize=11.5, color="black")
ax.set_ylim(-0.7, n + 0.55)
fig.canvas.draw()
_r = fig.canvas.get_renderer()
_w = max(t.get_window_extent(_r).width for t in ax.get_yticklabels()) / fig.dpi
LEFT = min(0.7, (_w + 0.3) / W)
ax.set_position([LEFT, BOTTOM / H, RIGHT - LEFT, axB_h / H])

from matplotlib.lines import Line2D
from matplotlib.patches import Patch
legend_items = [
    Line2D([], [], marker="o", color=PROTECT, lw=2.5, label="CI below 1: HCWs less affected"),
    Line2D([], [], marker="o", color=HARM, lw=2.5, label="CI above 1: HCWs more affected"),
]
if any(colour(r.ratio_ci95_lo, r.ratio_ci95_hi) == NEUTRAL for sc, r in eff.iterrows() if sc != "baseline"):
    legend_items.append(Line2D([], [], marker="o", color=NEUTRAL, lw=2.5, label="CI includes 1: equal risk"))
legend_items.append(Line2D([], [], marker="o", color=DOT, lw=2.5, label="Baseline: actual policies, calibrated to real data"))
legend_items.append(Line2D([], [], marker="D", color=POINT, ms=4, lw=0, label="Diamond: mean of 20 runs; bar: 95% CI"))
legend_items.append(Line2D([], [], color="0.35", lw=1, ls="--", label="Dashed line: equal risk, ratio of 1"))
legend_items.append(Line2D([], [], color=DOT, lw=1.4, ls=":", label=f"Dotted line: baseline mean ({bl['mean']:.2f})"))
fig.legend(handles=legend_items, loc="lower center", ncol=2, frameon=False, fontsize=11.5, columnspacing=1.2, handlelength=1.8,
           bbox_to_anchor=(0.5, TABLE_H / H))

# Scenario key at the bottom: id, description (also written as LaTeX for the paper).
key = [("baseline", "Baseline", LABELS["baseline"])] + [
    (sc, f"S{NUMBER[sc]}", LABELS[sc]) for sc in sorted((x for x in eff.index if x != "baseline"), key=NUMBER.get)]
if not no_table:
  fig.text(0.015, (TABLE_H - 0.12) / H, "Scenarios", fontsize=13.5, fontweight="bold", va="top")
  for k, (_, sid, desc) in enumerate(key):
      y = (TABLE_H - 0.12 - 0.34 - TABLE_ROW * k) / H
      fig.text(0.015, y, sid, fontsize=12.5, fontweight="bold", va="top")
      fig.text(0.015 + 0.95 / W, y, desc, fontsize=12.5, va="top")
  fig.add_artist(plt.Line2D([0.015, 0.985], [(TABLE_H - 0.12 - 0.3) / H] * 2, color="0.5", lw=0.8))
tex = ["\\begin{tabular}{@{}ll@{}}", "\\hline", "ID & Scenario \\\\ \\hline"]
tex += [f"{sid} & {desc.replace('%', chr(92) + '%')} \\\\" for _, sid, desc in key]
tex += ["\\hline", "\\end{tabular}"]
(out / ("forest_plot_rr_all_scenarios.tex" if show_all else "forest_plot_rr_scenarios.tex")).write_text("\n".join(tex) + "\n")
fig.suptitle("Healthcare worker vulnerability under each scenario", fontsize=15, fontweight="bold", x=0.015, ha="left", y=1 - 0.12 / H)
name = ("forest_plot_rr_all" if show_all else "forest_plot_rr") + ("_notable" if no_table else "")
fig.savefig(out / f"{name}.png", dpi=200)
fig.savefig(out / f"{name}.pdf")
print(f"-> {out / name}.png/.pdf ({n} scenarios)")
