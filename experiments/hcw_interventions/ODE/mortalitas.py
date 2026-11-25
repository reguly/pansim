"""COVID-halálozás hullámonként: valós adat (korona_hun.xlsx, a panSim populációjára skálázva),
panSim alapeset (20 futás) és az ODE két illesztése ((A) panSim-re, (B) valós adatra).

Az ODE-paraméterek a kalibracio.py kimenetéből jönnek (A_teljes_pontossag.json, ill.
parameterek.json "B_valos"), újraillesztés nincs. A panSim ugyanaz az alapeset-köteg, amelyre az
(A) illesztés készült (results/baseline).

Futtatás: python mortalitas.py   (kimenet: kalibracio_kimenet/mortalitas/)
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import kalibracio as K  # noqa: E402

OUT = K.OUT / "mortalitas"
HULLAMOK = [("2. hullám", "2020-09-23", "2021-01-31"),     # ugyanazok a határok, mint a kalibracio.py-ban
            ("3. hullám", "2021-02-01", "2021-06-30"),
            ("nyár (4. hullám eleje)", "2021-07-01", "2021-09-21")]


def parameterek(kulcs):
    d = json.loads((K.OUT / "parameterek.json").read_text(encoding="utf-8"))[kulcs]
    if kulcs == "A_panSim" and (K.OUT / "A_teljes_pontossag.json").exists():
        d = json.loads((K.OUT / "A_teljes_pontossag.json").read_text())
    return {k: (np.array(v) if isinstance(v, list) else v) for k, v in d.items()}


def main():
    np.seterr(all="ignore")
    OUT.mkdir(parents=True, exist_ok=True)
    m = K.load_sim()
    day = m.index.values.astype(float)
    datum = K.START + pd.to_timedelta(m.index, "D")

    # panSim: futásonkénti kumulált halálozás
    df = K.load_scenario(K.REPO / "experiments/hcw_interventions/results/baseline")
    futas = df.pivot_table(index="day", columns="run", values="D1")
    futas = futas - futas.iloc[0]

    # ODE (A)
    pA = parameterek("A_panSim")
    inpA = K.make_inputs(day, m["alpha"].values, m["delta"].values, m["VAC"].values)
    oA = K.simulate(pA, inpA, K.initial_state(m["I0"].iloc[0], m["hosp"].iloc[0],
                                               m["R"].iloc[0] + m["R_h"].iloc[0], m["D1"].iloc[0]))
    # ODE (B)
    real = K.load_real()
    pB = parameterek("B_valos")
    inpB = K.make_inputs(day, m["alpha"].values, m["delta"].values, real["doses"].values, hcw_doses_until=(94, 130))
    oB = K.simulate(pB, inpB, K.initial_state(pB["I0"], real["hosp"].iloc[0], m["R"].iloc[0] + m["R_h"].iloc[0],
                                               0.0, I_h0_pct=pB["I_h0_pct"]))

    kum = pd.DataFrame({
        "valos": real["deaths"].values,
        "panSim": futas.mean(axis=1).values,
        "ODE_A": (oA["deaths"] - oA["deaths"].iloc[0]).values[:len(day)],
        "ODE_B": (oB["deaths"] - oB["deaths"].iloc[0]).values[:len(day)],
    }, index=datum)

    # hullámonkénti összesítés
    sorok = []
    for nev, a, b in HULLAMOK:
        a0 = pd.Timestamp(a) - pd.Timedelta(days=1)
        a0 = max(a0, kum.index[0])
        b = min(pd.Timestamp(b), kum.index[-1])
        d = kum.loc[b] - kum.loc[a0]
        fut = futas.iloc[(kum.index.get_loc(b))] - futas.iloc[kum.index.get_loc(a0)]
        sor = {"hullam": nev, "kezdet": a, "veg": b.date().isoformat()}
        for k in kum:
            sor[k] = round(float(d[k]), 1)
        sor["panSim_min"], sor["panSim_max"] = round(float(fut.min()), 1), round(float(fut.max()), 1)
        heti = kum.loc[a0:b].diff().resample("W-SUN").sum()
        for k in kum:
            sor[f"{k}_csucs_heti"] = round(float(heti[k].max()), 1)
            sor[f"{k}_csucs_het"] = heti[k].idxmax().date().isoformat()
        sorok.append(sor)
    ossz = {"hullam": "teljes év", "kezdet": HULLAMOK[0][1], "veg": kum.index[-1].date().isoformat()}
    for k in kum:
        ossz[k] = round(float(kum[k].iloc[-1]), 1)
    ossz["panSim_min"], ossz["panSim_max"] = round(float(futas.iloc[-1].min()), 1), round(float(futas.iloc[-1].max()), 1)
    sorok.append(ossz)
    tab = pd.DataFrame(sorok)
    tab.to_csv(OUT / "mortalitas_hullamok.csv", index=False)
    print(tab.to_string(index=False))

    # heti halálozás (hétfőtől vasárnapig) és a panSim futások szórása
    heti = kum.diff().fillna(kum.iloc[0]).resample("W-SUN").sum()
    heti_fut = futas.diff().fillna(0).set_axis(datum).resample("W-SUN").sum()
    heti["panSim_p5"] = heti_fut.quantile(0.05, axis=1)
    heti["panSim_p95"] = heti_fut.quantile(0.95, axis=1)
    heti.round(2).to_csv(OUT / "mortalitas_heti.csv", index_label="het_vege")

    fig, ax = plt.subplots(figsize=(11, 4.5), layout="constrained")
    ax.fill_between(heti.index, heti["panSim_p5"], heti["panSim_p95"], color="0.6", alpha=0.3, lw=0,
                    label="panSim, 20 futás 5–95%")
    ax.plot(heti.index, heti["valos"], color="black", lw=2, label="valós (skálázva)")
    ax.plot(heti.index, heti["panSim"], color="0.4", lw=1.6, label="panSim átlag")
    ax.plot(heti.index, heti["ODE_A"], color="#e8710a", lw=1.6, ls="--", label="ODE (A)")
    ax.plot(heti.index, heti["ODE_B"], color="#2a78d6", lw=1.6, ls="--", label="ODE (B)")
    for _, a, b in HULLAMOK[1:]:
        ax.axvline(pd.Timestamp(a), color="0.8", lw=1)
    ax.set_ylabel("halálozás / hét (fő)")
    ax.legend(frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(OUT / "mortalitas_heti.png", dpi=140)
    print("Kimenet:", OUT)


if __name__ == "__main__":
    main()
