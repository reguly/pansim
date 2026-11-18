"""A kalibracio.py ODE-jének kompartment-diagramja: egyenletek/kompartmentek.svg (és .png).
Folytonos nyíl: emberek áramlása. Szaggatott nyíl: hatás (fertőzési erő, kiesés, dolgozói arány).
Futtatás: python kompartment_abra.py"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

plt.rcParams.update({"mathtext.fontset": "dejavusans", "svg.fonttype": "path", "font.size": 11})
KI = Path(__file__).with_name("egyenletek")

SZIN = {"S": "#dbe9f6", "I": "#f8d9c4", "H": "#f3c6c6", "D": "#d9d9d9", "R": "#d5ecd4",
        "seged": "#efeaf7", "Q": "#fff2cc"}
SZEGELY = "#444444"
FEKETE = "#222222"
HATAS = "#7a5fa8"
W, H = 1.6, 1.0

# Kompartmentek: név -> (x, y, felirat, típus). A HCW-sor tükrözött: R alul van.
CSUCS = {
    "S_c": (0, 8, "$S_c$\nfogékony", "S"),
    "I_c": (3.6, 8, "$I_c$\nfertőzött", "I"),
    "H_c": (7.2, 8, "$H_c$\nkórházban", "H"),
    "D_c": (10.8, 8, "$D_c$\nelhunyt", "D"),
    "R_c": (5.4, 10.9, "$R_c$\nvédett", "R"),
    "S_h": (0, 0, "$S_h$\nfogékony", "S"),
    "I_h": (3.6, 0, "$I_h$\nfertőzött", "I"),
    "H_h": (7.2, 0, "$H_h$\nkórházban", "H"),
    "D_h": (10.8, 0, "$D_h$\nelhunyt", "D"),
    "R_h": (5.4, -2.9, "$R_h$\nvédett", "R"),
}


def doboz(ax, x, y, szoveg, szin, w=W, h=H, fs=11, vastag=1.4):
    ax.add_patch(FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0,rounding_size=0.15",
                                fc=szin, ec=SZEGELY, lw=vastag, zorder=3))
    ax.text(x, y, szoveg, ha="center", va="center", fontsize=fs, zorder=4, linespacing=1.35)


def felirat(ax, x, y, t, hatas=False, fs=9.5, ha="center"):
    ax.text(x, y, t, ha=ha, va="center", fontsize=fs, color=HATAS if hatas else FEKETE, zorder=5,
            bbox=dict(fc="white", ec="none", pad=0.8, alpha=0.95))


def nyil(ax, *pontok, hatas=False, rad=0.0):
    """Nyíl a pontokon át (töröttvonal); a hegy az utolsó szakaszon van."""
    szin = HATAS if hatas else FEKETE
    lw = 1.1 if hatas else 1.6
    ls = (0, (4, 3)) if hatas else "-"
    for a, b in zip(pontok[:-2], pontok[1:-1]):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=szin, lw=lw, linestyle=ls, zorder=2,
                solid_capstyle="butt")
    ax.add_patch(FancyArrowPatch(pontok[-2], pontok[-1], arrowstyle="-|>", mutation_scale=14, lw=lw,
                                 color=szin, linestyle=ls, connectionstyle=f"arc3,rad={rad}",
                                 shrinkA=0, shrinkB=0, zorder=2))


def oldal(n, o, d=0.0):
    """A doboz egy oldalának pontja: 'l', 'r', 't', 'b'; d eltolás az oldal mentén."""
    x, y = CSUCS[n][:2]
    return {"l": (x - W/2, y + d), "r": (x + W/2, y + d), "t": (x + d, y + H/2), "b": (x + d, y - H/2)}[o]


def csoport(ax, g):
    S, I, Hk, D, R = (f"{k}_{g}" for k in "SIHDR")
    fel = g == "c"
    sz = 1 if fel else -1                  # tükrözés a HCW-sorhoz
    v, rv = ("t", "b") if fel else ("b", "t")
    yrow = CSUCS[S][1]

    nyil(ax, oldal(S, "r"), oldal(I, "l"))
    felirat(ax, 1.8, yrow + 0.28*sz, r"$\lambda_c$" if fel else r"$\lambda_h$", fs=12)
    nyil(ax, oldal(I, "r"), oldal(Hk, "l"))
    felirat(ax, 5.4, yrow + 0.28*sz, rf"$p_{{H,{g}}}\,\tau_I$")
    nyil(ax, oldal(Hk, "r"), oldal(D, "l"))
    felirat(ax, 9.0, yrow + 0.28*sz, r"$p_D\,\tau_H\,/\,DA^2$")

    # I -> R és H -> R
    nyil(ax, oldal(I, v), oldal(R, rv, -0.45))
    felirat(ax, 3.55, yrow + 1.45*sz, rf"$(1-p_{{H,{g}}})\,\tau_I$", ha="right")
    nyil(ax, oldal(Hk, v), oldal(R, rv, 0.45))
    felirat(ax, 7.25, yrow + 1.45*sz, r"$(1-p_D/DA)\,\tau_H\,/\,DA$", ha="left")

    # S -> R oltás és R -> S immunitásvesztés, derékszögű vezetéssel
    xs = CSUCS[S][0]
    yr = CSUCS[R][1]
    nyil(ax, oldal(S, v, 0.3), (xs + 0.3, yr + 0.18*sz), oldal(R, "l", 0.18*sz))
    felirat(ax, 2.6, yr + 0.45*sz, rf"oltás  $V_{g}$, $\tau_v$ késéssel")
    nyil(ax, oldal(R, "l", -0.18*sz), (xs - 0.3, yr - 0.18*sz), oldal(S, v, -0.3))
    felirat(ax, 2.6, yr - 0.45*sz, r"immunitásvesztés  $\omega$")


def main():
    fig, ax = plt.subplots(figsize=(15, 11.5))
    ax.set_xlim(-2.2, 17.8)
    ax.set_ylim(-4.4, 12.6)
    ax.set_aspect("equal")
    ax.axis("off")

    for y0, cim, ty in [(6.85, "Civilek   ($N_c$ = 168 610)", 12.25),
                        (-4.05, "Egészségügyi dolgozók   ($N_h$ = 10 136)", -3.75)]:
        ax.add_patch(FancyBboxPatch((-1.3, y0), 13.1, 5.7, boxstyle="round,pad=0,rounding_size=0.3",
                                    fc="#fafafa", ec="#bbbbbb", lw=0.8, zorder=0))
        ax.text(-1.05, ty, cim, fontsize=12.5, fontweight="bold", va="center", color="#333333")

    for n, (x, y, t, k) in CSUCS.items():
        doboz(ax, x, y, t, SZIN[k])
    csoport(ax, "c")
    csoport(ax, "h")

    # ---- fertőzési nyomások a két sor között ----
    kx, ky = 1.6, 5.2       # közösségi
    bx, by = 7.2, 4.3       # betegek
    cx, cy = 5.95, 2.0      # kollégák
    lx, ly = 1.3, 2.3       # lambda_h összegző
    doboz(ax, kx, ky, "közösségi nyomás\n$I/N$,   $I = I_c + I_h$", SZIN["seged"], w=2.6, h=1.0, fs=9.5,
          vastag=1.0)
    doboz(ax, bx, by, "betegnyomás\n$H/(H+P_0)$,  $H = H_c+H_h$", SZIN["seged"], w=3.3, h=1.0, fs=9.5,
          vastag=1.0)
    doboz(ax, cx, cy, "kollégák\n" r"$(1-c_{test})\,I_h\,/\,N_w$", SZIN["seged"], w=2.4, h=1.0, fs=9.5,
          vastag=1.0)
    doboz(ax, lx, ly, "$\\lambda_h$  HCW-fertőzési erő\n"
          r"$\lambda_{comm} + \lambda_{pat} + \lambda_{staff}$",
          SZIN["seged"], w=3.1, h=1.0, fs=8.5, vastag=1.0)

    # források
    nyil(ax, oldal("I_c", "b", -0.3), (kx + 0.9, ky + 0.5), hatas=True)
    nyil(ax, oldal("I_h", "t", -0.45), (kx + 1.0, ky - 0.5), hatas=True)
    nyil(ax, oldal("H_c", "b"), (bx, by + 0.5), hatas=True)
    nyil(ax, oldal("H_h", "t"), (bx, by - 0.5), hatas=True)
    nyil(ax, oldal("I_h", "t", 0.45), (cx - 0.6, cy - 0.5), hatas=True)
    # hova hatnak
    nyil(ax, (kx - 0.4, ky + 0.5), (kx - 0.4, 8.0), hatas=True)
    felirat(ax, kx - 0.45, 6.45, r"$\lambda_c = \beta\,c(t)\,v(t)\,I/N$", hatas=True, ha="right")
    nyil(ax, (kx - 0.4, ky - 0.5), (kx - 0.4, ly + 0.5), hatas=True)
    felirat(ax, kx - 0.45, 3.75, r"$\lambda_{comm} = \rho_c\,\beta\,c\,v\,I/N$", hatas=True, ha="right")
    nyil(ax, (bx - 1.45, by - 0.2), (lx + 1.55, ly + 0.35), hatas=True)
    felirat(ax, 4.3, 3.65, r"$\lambda_{pat} \propto \beta_{PH}\,v$", hatas=True)
    nyil(ax, (cx - 1.2, cy + 0.1), (lx + 1.55, cy + 0.1), hatas=True)
    felirat(ax, 3.8, 1.72, r"$\lambda_{staff} \propto \beta_{HH}\,v$", hatas=True, fs=8.5)
    nyil(ax, (lx, ly - 0.5), (lx, 0.03), hatas=True)

    # ---- karantén és dolgozói arány a jobb oldalon ----
    qx, qy = 15.3, -1.3
    dx, dy = 15.3, 4.6
    doboz(ax, qx, qy, "$Q_h$: karanténban lévő,\nnem fertőzött HCW-k\n"
          r"$[\kappa_{comm}N_h\,I/N + \kappa_{work}\,c_{test}I_h]$" "\n" r"$\times\,(1-f_{vax,h}(t))$",
          SZIN["Q"], w=4.4, h=2.0, fs=9.5)
    doboz(ax, dx, dy, "dolgozói arány   $DA = N_w/N_h$\n"
          r"$N_w = N_h - (c_{test}I_h + H_h + D_h + Q_h)$" "\n"
          "lassítja/gyorsítja a kórházi kiáramlást,\n$N_w$ a kollégák nevezője",
          SZIN["seged"], w=4.6, h=1.9, fs=9.5)
    nyil(ax, (qx, qy + 1.0), (dx, dy - 0.95), hatas=True)
    felirat(ax, qx + 0.15, 1.65, "kiesik", hatas=True, ha="left")
    nyil(ax, oldal("D_h", "r", 0.25), (12.4, 0.25), (dx - 2.3, dy - 0.6), hatas=True)
    felirat(ax, 12.55, 1.0, r"$c_{test}I_h,\ H_h,\ D_h$", hatas=True, ha="left")
    nyil(ax, (dx - 2.3, dy + 0.55), (9.0, 7.97), hatas=True)
    nyil(ax, (dx - 2.3, dy - 0.2), (9.0, 0.03), hatas=True)
    felirat(ax, 11.55, 6.2, r"$\tau_H/DA$", hatas=True)
    felirat(ax, 10.25, 1.55, r"$\tau_H/DA$", hatas=True)

    # ---- jelmagyarázat ----
    jx, jy = 12.4, 11.9
    ax.add_patch(FancyArrowPatch((jx, jy), (jx + 0.9, jy), arrowstyle="-|>", mutation_scale=14, lw=1.6,
                                 color=FEKETE))
    ax.text(jx + 1.1, jy, "emberek áramlása (ráta a nyílon)", va="center", fontsize=9.5)
    ax.add_patch(FancyArrowPatch((jx, jy - 0.55), (jx + 0.9, jy - 0.55), arrowstyle="-|>",
                                 mutation_scale=14, lw=1.1, color=HATAS, linestyle=(0, (4, 3))))
    ax.text(jx + 1.1, jy - 0.55, "hatás (fertőzési erő, kiesés)", va="center", fontsize=9.5)
    ax.text(jx, jy - 1.05, "c(t): illesztett kontaktusszorzó (21 naponként)\n"
            "v(t): variánsszorzó (alfa, delta)\n"
            "$f_{vax,h}(t)$: beoltott HCW-k aránya\n"
            r"$\tau_H = \tau_{H,c} = \tau_{H,h},\ \ p_{H,h} = p_{H,c}$",
            va="top", fontsize=9, color="#444444", linespacing=1.5)

    KI.mkdir(exist_ok=True)
    for kit in ("svg", "png"):
        fig.savefig(KI / f"kompartmentek.{kit}", bbox_inches="tight", dpi=110, facecolor="white")
    plt.close(fig)
    print(KI / "kompartmentek.svg")


if __name__ == "__main__":
    main()
