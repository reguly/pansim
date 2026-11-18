"""A KALIBRACIO.md egyenleteit SVG-képként rajzolja ki az egyenletek/ mappába, hogy LaTeX-támogatás
nélküli Markdown-előnézetben is látszódjanak. Futtatás: python egyenletek_kepek.py"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update({"mathtext.fontset": "cm", "svg.fonttype": "path"})
KI = Path(__file__).with_name("egyenletek")

# Minden blokk sorok listája: (bal oldal, jobb oldal). A sorok az egyenlőségjelnél igazodnak.
# A "T:" kezdetű bal oldal sima szöveg (a mathtext betűkészletében nincs ő).
BLOKKOK = {
    "segedmennyisegek": [
        (r"Q_h", r"\left(\kappa_{comm}\,N_h\,\dfrac{I}{N} + \kappa_{work}\,c_{test}\,I_h\right)\left(1 - f_{vax,h}(t)\right)"),
        (r"K", r"c_{test}\,I_h + H_h + D_h + Q_h"),
        (r"N_w", r"N_h - K"),
        (r"DA", r"\dfrac{N_w}{N_h}"),
    ],
    "fertozesi_erok": [
        (r"b(t)", r"\beta\,v(t)\,c(t)"),
        (r"\lambda_c", r"b\,\dfrac{I}{N}"),
        (r"\lambda_{comm}", r"\rho_c\,b\,\dfrac{I}{N}"),
        (r"\lambda_{pat}", r"\beta_{PH}\,v\,\dfrac{H}{H+P_0}"),
        (r"\lambda_{staff}", r"\beta_{HH}\,v\,(1-c_{test})\,\dfrac{I_h}{N_w}"),
        (r"\lambda_h", r"\lambda_{comm} + \lambda_{pat} + \lambda_{staff}"),
    ],
    "oltas": [
        (r"V_g(t)", r"e_v\,u_g(t-\tau_v)\,\dfrac{S_g}{\max(S_g+R_g,\ 1)},\qquad g \in \{c, h\}"),
    ],
    "civilek": [
        (r"\dot S_c", r"-\lambda_c S_c + \omega R_c - V_c"),
        (r"\dot I_c", r"\lambda_c S_c - \tau_I I_c"),
        (r"\dot H_c", r"p_{H,c}\,\tau_I I_c - \dfrac{\tau_{H,c}}{DA}\,H_c"),
        (r"\dot D_c", r"p_D\,\dfrac{\tau_{H,c}}{DA^2}\,H_c"),
        (r"\dot R_c", r"(1-p_{H,c})\,\tau_I I_c + \left(1-\dfrac{p_D}{DA}\right)\dfrac{\tau_{H,c}}{DA}\,H_c - \omega R_c + V_c"),
    ],
    "hcw": [
        (r"\dot S_h", r"-\lambda_h S_h + \omega R_h - V_h"),
        (r"\dot I_h", r"\lambda_h S_h - \tau_I I_h"),
        (r"\dot H_h", r"p_{H,h}\,\tau_I I_h - \dfrac{\tau_{H,h}}{DA}\,H_h"),
        (r"\dot D_h", r"p_D\,\dfrac{\tau_{H,h}}{DA^2}\,H_h"),
        (r"\dot R_h", r"(1-p_{H,h})\,\tau_I I_h + \left(1-\dfrac{p_D}{DA}\right)\dfrac{\tau_{H,h}}{DA}\,H_h - \omega R_h + V_h"),
    ],
    "szamlalok": [
        (r"\dot C_{civ}", r"\lambda_c S_c"),
        (r"\dot C_{comm}", r"\lambda_{comm} S_h"),
        (r"\dot C_{pat}", r"\lambda_{pat} S_h"),
        (r"\dot C_{staff}", r"\lambda_{staff} S_h"),
        (r"\dot C_{reinf}", r"\omega\,(R_c + R_h)"),
    ],
    "variansszorzo": [
        (r"v(t)", r"1 + \left(\dfrac{1{,}85}{0{,}98} - 1\right)\alpha(t) + \left(\dfrac{2{,}05}{0{,}98} - 1\right)\delta(t)"),
    ],
    "megfigyelt": [
        ("T:HCI [%]", r"\dfrac{I_h + H_h + Q_h}{N_h}"),
        ("T:kieső [%]", r"\dfrac{c_{test}\,I_h + H_h + Q_h}{N_h}"),
        ("T:kórházi ápolt", r"H_c + H_h"),
        ("T:halott", r"D_c + D_h"),
    ],
}

SOR = 0.75      # sormagasság hüvelykben (a törtek miatt bő)
MERET = 15


def rajzol(nev, sorok):
    fig = plt.figure(figsize=(9, SOR*len(sorok) + 0.1))
    fig.patch.set_facecolor("white")
    for i, (bal, jobb) in enumerate(sorok):
        y = 1 - (i + 0.5)/len(sorok)
        bal = bal[2:] if bal.startswith("T:") else f"${bal}$"
        fig.text(0.16, y, bal, ha="right", va="center", fontsize=MERET, family="serif")
        fig.text(0.17, y, "$=$", ha="left", va="center", fontsize=MERET)
        fig.text(0.21, y, f"${jobb}$", ha="left", va="center", fontsize=MERET)
    fig.savefig(KI / f"{nev}.svg", bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    KI.mkdir(exist_ok=True)
    for nev, sorok in BLOKKOK.items():
        rajzol(nev, sorok)
        print(KI / f"{nev}.svg")
