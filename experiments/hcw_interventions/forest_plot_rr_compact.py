"""Compact version of forest_plot_rr.py --all: same data and content (forest plot, ratio and CI
column, colour legend, scenario key), laid out as a wide, short figure (7 x ~4 in) so that fonts stay readable
without rescaling. Include it with \\includegraphics[width=\\linewidth]{forest_plot_rr_all_compact.pdf}.
The figure title is left to the LaTeX caption.

Reads outputs/uncertainty_ci.csv (run uncertainty.py first).
Usage: python forest_plot_rr_compact.py [--width INCHES] [--no-key | --key-below] [--final-width IN] [--body-pt PT] [out_dir]
--no-key drops the scenario key from the image (it is written to forest_plot_rr_all_scenarios.tex
by forest_plot_rr.py --all) so the text can be larger on a short figure.
"""
import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

here = Path(__file__).parent
argv = sys.argv[1:]
W = 7.0
if "--width" in argv:
    k = argv.index("--width")
    W = float(argv[k + 1])
    del argv[k:k + 2]
def opt(name, default):
    """--name VALUE -> float, removed from argv."""
    if name in argv:
        k = argv.index(name)
        v = float(argv[k + 1])
        del argv[k:k + 2]
        return v
    return default


FINAL_WIDTH = opt("--final-width", 6.3)   # width (in) the figure is shown at in the paper, e.g. 	extwidth
BODY_PT = opt("--body-pt", 10.0)          # body font size of the paper; the description is sized to match it
no_key = "--no-key" in argv
key_below = "--key-below" in argv   # stacked layout: plot, legend, scenario key, caption
argv = [a for a in argv if a not in ("--no-key", "--key-below")]
out = Path(argv[0]) if argv else here / "outputs"

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
NUMBER = {name: k + 1 for k, name in enumerate(LABELS)}
PROTECT, HARM, NEUTRAL, BASE, POINT = "#2e9e4f", "#d62728", "#8a8f98", "#4a4f57", "#1a1a1a"
DOT = "#2a78d6"   # baseline-mean line
ARROW_LESS, ARROW_MORE = "#2e9e4f", "#d62728"   # direction arrows: green = lower risk, red = higher risk

S = 1.25   # text/spacing scale relative to the 7-inch design
FONT_BUMP = 1.5   # pt added to every font in the figure (the description keeps its own size)
FS, FS_SMALL = 7.5 * S + FONT_BUMP, 7 * S + FONT_BUMP
plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "Times", "Liberation Serif", "DejaVu Serif"],
                     "mathtext.fontset": "stix", "font.size": FS, "axes.edgecolor": "0.4", "axes.linewidth": 0.6})

ci = pd.read_csv(out / "uncertainty_ci.csv")
d = ci[ci.metric == "incidence_RR"].set_index("scenario")
bl = d.loc["baseline"]
eff = d.loc[list(LABELS) + ["baseline"], ["mean", "mean_ci95_lo", "mean_ci95_hi"]].sort_values("mean")
n = len(eff)


def colour(lo, hi):
    """Compare the CI with 1 (HCWs and the rest of the population equally affected)."""
    return PROTECT if hi < 1 else HARM if lo > 1 else NEUTRAL


# Layout in inches: plot panel on the left; legend and scenario key stacked in a panel on the right.
ROW_H, TOP, XAXIS_H = 0.175 * S, 0.32 * S, 0.5 * S
LEFT_IN, VALUE_COL = 0.5 * S, 1.12 * S
PLOT_W = 3.6 * S                      # width of the plot panel incl. row labels and ratio column
PX = PLOT_W + 0.2                 # left edge of the right panel
KEY_LINE = 0.125 * S
KEY_FS = FS_SMALL            # font of the scenario key (larger in the side-by-side layout)
key = [("Baseline", "Actual policies, calibrated to real data from Szeged")] + [
    (f"S{NUMBER[s]}", LABELS[s]) for s in sorted(LABELS, key=NUMBER.get)]
ID_W = 0.42 * S
wrap_chars = int((W - PX - 0.05 - ID_W) / (0.039 * S))
key = [(sid, textwrap.wrap(desc, wrap_chars)) for sid, desc in key]
stacked = no_key or key_below
_mf = plt.figure()
_mr = _mf.canvas.get_renderer()


def text_w(t, fs, weight="normal"):
    """Rendered width of t in inches."""
    tt = _mf.text(0, 0, t, fontsize=fs, fontweight=weight)
    w = tt.get_window_extent(_mr).width / _mf.dpi
    tt.remove()
    return w


def wrap_w(text, fs, width):
    """Greedy word wrap to a measured width in inches."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if cur and text_w(trial, fs) > width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    return lines + [cur]


LEGEND_LABELS = ["CI below 1: HCWs less affected", "CI above 1: HCWs more affected",
                 "CI includes 1: equal risk", "Baseline: actual policies, calibrated to real data",
                 "Diamond: mean of 20 runs; bar: 95% CI", "Dashed line: equal risk, ratio of 1"]
if not stacked:
    # plot + legend + figure description on the left, scenario key (slightly larger font) on the right
    KEY_FS = FS_SMALL * 1.15
    KEY_LINE = 1.15 * KEY_FS / 72   # line pitch follows the key font
    ID_W = text_w("Baseline", KEY_FS, "bold") + 0.12
    RIGHT_W = 3.5
    W = PX + RIGHT_W + 0.05
    key = [(sid, wrap_w(" ".join(t), KEY_FS, RIGHT_W - ID_W - 0.05)) for sid, t in key]
if key_below:   # tighter vertical spacing, the key is the long part
    ROW_H, XAXIS_H, KEY_LINE = 0.155 * S, 0.42 * S, 0.108 * S
if stacked:
    W = 6.0
    PLOT_W = W - 0.1
    PX = 0.1
    wrap_chars = int((W - 0.15 - ID_W) / (0.039 * S))
    key = [(sid, textwrap.wrap(desc, wrap_chars)) for sid, desc in [(k, ' '.join(t)) for k, t in key]]
    if no_key:
        key = []
CAPTION = "Vulnerability of healthcare workers (HCWs) relative to the rest of the population under each intervention scenario."
KEY_H = 0.3 * S + KEY_LINE * sum(len(t) for _, t in key) + (0.012 if key_below else 0.012) * S * len(key)
LEGEND_H = 0.1 + 1.39 * FS_SMALL / 72 * 7
ax_h = ROW_H * (n + 0.9)
LEG_BELOW = 0.1 + 0.135 * S * 3 + (0.02 if key_below else 0.1)   # no-key mode: legend in two columns under the plot
cap_lines = textwrap.wrap(CAPTION, int((W - 0.1) / (0.045 * S))) if stacked else []
CAP_FS = BODY_PT * W / FINAL_WIDTH   # appears at BODY_PT once the figure is scaled to FINAL_WIDTH
side_cap = [] if stacked else wrap_w("Figure 1. " + CAPTION, CAP_FS, W - 0.1)
LEG_Y = TOP + ax_h + XAXIS_H + 0.05                  # side layout: legend under the plot,
CAP_Y = max(LEG_Y + LEGEND_H, 0.05 + KEY_H) + 0.12   # full-width figure description under both columns
left_bottom = CAP_Y + 1.4 * CAP_FS / 72 * len(side_cap) + 0.05
CAP_H = (0.12 + 0.17 * S * len(cap_lines)) if stacked else 0
KEY_BLOCK = KEY_H if key and stacked else 0
H = TOP + ax_h + XAXIS_H + LEG_BELOW + KEY_BLOCK + CAP_H if stacked else max(left_bottom, 0.1 + KEY_H)

fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([LEFT_IN / W, (H - TOP - ax_h) / H, (PLOT_W - LEFT_IN - VALUE_COL) / W, ax_h / H])
ax.axvline(1, color="0.35", lw=0.6, ls="--", zorder=0)
ax.vlines(bl["mean"], -0.7, n - 0.6, color=DOT, lw=1.1, ls=":", zorder=0)   # baseline mean, stops below the arrows
for i, (scen, r) in enumerate(eff.iterrows()):
    lo, hi = r.mean_ci95_lo, r.mean_ci95_hi
    c = DOT if scen == "baseline" else colour(lo, hi)
    ax.hlines(i, lo, hi, color=c, lw=1.8 * S, zorder=2)
    ax.vlines([lo, hi], i - 0.18, i + 0.18, color=c, lw=1.4 * S, zorder=2)
    ax.plot(r["mean"], i, "D", color=POINT, ms=2.3 * S, zorder=3)
    ax.annotate(f"{r['mean']:.2f}  [{lo:.2f}, {hi:.2f}]", xy=(1, i), xycoords=("axes fraction", "data"),
                xytext=(5, 0), textcoords="offset points", va="center", ha="left", fontsize=FS)
ax.annotate("ratio [95% CI]", xy=(1, n + 0.05), xycoords=("axes fraction", "data"), xytext=(5, 0),
            textcoords="offset points", va="center", ha="left", fontsize=FS, fontweight="bold")

ax.set_yticks(range(n))
ax.set_yticklabels(["Baseline" if s == "baseline" else f"S{NUMBER[s]}" for s in eff.index], fontsize=FS, fontweight="bold")
ax.set_xlim(0.6, 2.0)
ax.set_xticks([0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0])
ax.set_xticklabels(["0.6", "0.8", "1.0", "1.2", "1.4", "1.6", "1.8", "2.0"])
ax.minorticks_off()
ax.spines[["top", "right", "left"]].set_visible(False)
ax.tick_params(axis="y", length=0, pad=2)
ax.tick_params(axis="x", length=2, width=0.6, pad=2)
ax.set_xlabel("HCW / rest-of-population incidence ratio\n(1 means equal risk)", fontsize=FS, labelpad=2)
ax.set_ylim(-0.7, n + 0.2)
ytop = n - 0.15
ax.annotate("", xy=(0.65, ytop), xytext=(0.96, ytop), arrowprops=dict(arrowstyle="->", color=ARROW_LESS, lw=0.9, mutation_scale=6))
ax.annotate("", xy=(1.95, ytop), xytext=(1.04, ytop), arrowprops=dict(arrowstyle="->", color=ARROW_MORE, lw=0.9, mutation_scale=6))
ax.text(0.98, ytop + 0.35, "HCWs less affected", ha="right", fontsize=FS_SMALL, color="black")
ax.text(1.03, ytop + 0.35, "HCWs more affected", ha="left", fontsize=FS_SMALL, color="black")

handles = [
    Line2D([], [], marker="o", ms=3, color=PROTECT, lw=1.8, label="CI below 1: HCWs less affected"),
    Line2D([], [], marker="o", ms=3, color=HARM, lw=1.8, label="CI above 1: HCWs more affected"),
    Line2D([], [], marker="o", ms=3, color=NEUTRAL, lw=1.8, label="CI includes 1: equal risk"),
    Line2D([], [], marker="o", ms=3, color=DOT, lw=1.8, label="Baseline: actual policies, calibrated to real data"),
    Line2D([], [], marker="D", ms=2.3, color=POINT, lw=0, label="Diamond: mean of 20 runs; bar: 95% CI"),
    Line2D([], [], color="0.35", lw=0.6, ls="--", label="Dashed line: equal risk, ratio of 1"),
    Line2D([], [], color=DOT, lw=1.1, ls=":", label=f"Dotted line: baseline mean ({bl['mean']:.2f})"),
]
if stacked:
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=FS_SMALL, handlelength=1.8,
               labelspacing=0.3, columnspacing=1.0, borderaxespad=0, bbox_to_anchor=(0.5, (CAP_H + KEY_BLOCK + 0.02) / H))
else:
    fig.legend(handles=handles, loc="upper left", ncol=1, frameon=False, fontsize=FS_SMALL, handlelength=1.8,
               labelspacing=0.3, borderaxespad=0, bbox_to_anchor=(0.02 / W, 1 - LEG_Y / H))

# Scenario key, below the legend
y0 = TOP + ax_h + XAXIS_H + LEG_BELOW if stacked else 0.05
if key:
  fig.text(PX / W, 1 - (y0 + 0.02) / H, "Scenarios", fontsize=FS + 0.5, fontweight="bold", va="top")
  fig.add_artist(plt.Line2D([PX / W, 0.995], [1 - (y0 + 0.2 * S) / H] * 2, color="0.5", lw=0.5))
y = y0 + 0.25 * S
for sid, lines in key:
    fig.text(PX / W, 1 - y / H, sid, fontsize=KEY_FS, fontweight="bold", va="top")
    for ln in lines:
        fig.text((PX + ID_W) / W, 1 - y / H, ln, fontsize=KEY_FS, va="top")
        y += KEY_LINE
    y += (0.012 if key_below else 0.012) * S

for k, ln in enumerate(cap_lines):
    fig.text(0.01, (CAP_H - 0.08 - 0.17 * S * k) / H, (r"$\mathbf{Figure\ 1.}$ " if k == 0 else "") + ln,
             fontsize=FS_SMALL, va="top", ha="left")

# Side-by-side layout: full-width figure description under the plot/legend and the key
for k, ln in enumerate(side_cap):
    y = CAP_Y + 1.4 * CAP_FS / 72 * k
    if k == 0:
        ln = r"$\mathbf{Figure\ 1.}$" + ln[len("Figure 1."):]
    fig.text(0.01, 1 - y / H, ln, fontsize=CAP_FS, va="top", ha="left")

name = "forest_plot_rr_all_compact" + ("_nokey" if no_key else "_keybelow" if key_below else "")
fig.savefig(out / f"{name}.pdf", bbox_inches="tight", pad_inches=0.03)
fig.savefig(out / f"{name}.png", dpi=300, bbox_inches="tight", pad_inches=0.03)
print(f"-> {out / name}.png/.pdf ({W:.1f} x {H:.1f} in, {n} rows)")
