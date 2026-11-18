"""HCW-kontaktkarantén nélkül: mit ad az ODE? (a témavezető kérése, a panSim --hcwQuarantineExemptFrom
forgatókönyveinek ODE-párja)

A kalibracio.py eredményeiből (kalibracio_kimenet/parameterek.json) indul, nem illeszt újra, kivéve
a (B) változat egyik esetét. Esetek:
  (A) panSim-illesztés:  alapeset | kontaktkarantén nélkül egész évben
  (B) valós illesztés:   alapeset | kontaktkarantén nélkül egész évben | 2021-03-25-től nincs
                         (a márciusi beesés "berendelés" hipotézise) | ugyanez, de 03-25-ig a beoltott
                         kontaktok is karanténba kerülnek | újraillesztve kappa = 0 mellett
Az ODE-ben a karantén (Q_h) csak a kiesést és a dolgozói arányt (DA) változtatja, a fertőzést nem:
a karanténba küldött, valójában fertőzött kontaktok kiszűrése nincs a modellben (lásd KALIBRACIO.md).

Futtatás: python karanten_kiserlet.py   (kimenet: kalibracio_kimenet/, bizalmas SZTE-adattal)
"""
import json

import numpy as np
import pandas as pd

import kalibracio as K

OFF_MARC = 183                    # 2021-03-25: a márciusi beesés előtti utolsó pont az SZTE-görbén


def load_params():
    d = json.loads((K.OUT / "parameterek.json").read_text(encoding="utf-8"))
    conv = lambda p: {k: (np.array(v) if isinstance(v, list) else v) for k, v in p.items()}  # noqa: E731
    return conv(d["A_panSim"]), conv(d["B_valos"])


def main():
    np.seterr(all="ignore")
    pA, pB = load_params()
    m = K.load_sim()
    day = m.index.values.astype(float)
    inp_A = K.make_inputs(day, m["alpha"].values, m["delta"].values, m["VAC"].values)
    x0_A = lambda p: K.initial_state(m["I0"].iloc[0], m["hosp"].iloc[0], m["R"].iloc[0] + m["R_h"].iloc[0],  # noqa: E731
                                     m["D1"].iloc[0])
    real = K.load_real()
    inp_B = K.make_inputs(day, m["alpha"].values, m["delta"].values, real["doses"].values,
                          hcw_doses_until=(94, 130))
    x0_B = lambda p: K.initial_state(p["I0"], real["hosp"].iloc[0], m["R"].iloc[0] + m["R_h"].iloc[0], 0.0,  # noqa: E731
                                     I_h0_pct=p["I_h0_pct"])
    sim = lambda p, inp, x0: K.simulate(p, inp, x0(p))  # noqa: E731

    oA = sim(pA, inp_A, x0_A)
    oA0 = sim({**pA, "kappa_off_day": 0}, inp_A, x0_A)
    oB = sim(pB, inp_B, x0_B)
    oB0 = sim({**pB, "kappa_off_day": 0}, inp_B, x0_B)
    oBm = sim({**pB, "kappa_off_day": OFF_MARC}, inp_B, x0_B)
    # Ha a valóságban a beoltott kontaktok is karanténba kerültek volna 03-25-ig, és akkor rendelték
    # be őket: ez a változat a beoltottak mentességét kikapcsolja 03-25-ig, utána nincs karantén.
    oBv = sim({**pB, "kappa_off_day": OFF_MARC, "vax_exempt_from_day": OFF_MARC}, inp_B, x0_B)

    # (B) újraillesztés karantén nélkül: el tudja-e magyarázni az SZTE-görbét csak a fertőzés?
    has_szte = "szte" in real
    if has_szte:
        base0 = {**pB, "kappa_comm": 0.0, "kappa_work": 0.0}
        free0 = [("rho_c", pB["rho_c"], 0.1, 3.0), ("beta_PH", pB["beta_PH"], 1e-4, 0.5),
                 ("c_test", pB["c_test"], 0.3, 1.0), ("I_h0_pct", pB["I_h0_pct"], 0.0, 15.0)]
        pB_re = K.fit([("SZTE", real["szte"].values, 1.0, "kieso_pct")], base0, free0, x0_B, inp_B,
                      fit_c=False, label="B újraillesztve, kappa = 0")
        oB_re = sim(pB_re, inp_B, x0_B)

    def sor(o, ref=None):
        r = dict(kum_HCW=round(float(o["cum_hcw"].iloc[-1])),
                 incidence_RR=round(float((o["cum_hcw"].iloc[-1]/K.N_h)/(o["cum_civ"].iloc[-1]/K.N_c)), 3),
                 hci_csucs_2=K.window_peak(o["hci_pct"], "2020-09-23", "2021-01-31"),
                 hci_csucs_3=K.window_peak(o["hci_pct"], "2021-02-01", "2021-06-30"),
                 kieso_csucs_2=K.window_peak(o["kieso_pct"], "2020-09-23", "2021-01-31"),
                 kieso_csucs_3=K.window_peak(o["kieso_pct"], "2021-02-01", "2021-06-30"),
                 min_dolgozo_pct=round(100*o["dolgozo_arany"].min(), 1))
        if has_szte:
            mt = K.metrics(o["kieso_pct"].values, real["szte"].values)
            r.update(SZTE_r=round(mt["r"], 3), SZTE_rmse=round(mt["rmse"], 2))
        return r

    tab = {"A alapeset": sor(oA), "A karantén nélkül": sor(oA0),
           "B alapeset": sor(oB), "B karantén nélkül": sor(oB0), "B 03-25-től nincs": sor(oBm),
           "B beoltott is karanténban 03-25-ig, utána nincs": sor(oBv)}
    if has_szte:
        tab["B újraillesztve, kappa = 0"] = sor(oB_re)
        tab["B újraillesztve, kappa = 0"].update(
            {k: round(float(pB_re[k]), 3) for k in ("rho_c", "beta_PH", "c_test", "I_h0_pct")})
    df = pd.DataFrame(tab).T
    print(df.to_string())
    df.to_csv(K.OUT / "karanten_kiserlet.csv")

    gray = dict(color="#888888", lw=1.2, ls="--")
    panels = [("(A) panSim-illesztés: HCI", "%",
               [("panSim alapeset HCI", m["HCI"].values, K.SIM), ("ODE (A) alapeset", oA["hci_pct"].values, K.ODE_A),
                ("ODE (A) kontaktkarantén nélkül", oA0["hci_pct"].values, gray)])]
    if has_szte:
        panels.append(("(B) valós illesztés: kieső dolgozók", "a dolgozók %-a",
                       [("SZTE (valós)", real["szte"].values, K.REAL),
                        ("ODE (B) alapeset", oB["kieso_pct"].values, K.ODE_B),
                        ("ODE (B) kontaktkarantén nélkül", oB0["kieso_pct"].values, gray),
                        ("ODE (B) 2021-03-25-től nincs karantén", oBm["kieso_pct"].values,
                         dict(color="#d62728", lw=1.2, ls=":")),
                        ("ODE (B) beoltott is karanténban 03-25-ig, utána nincs", oBv["kieso_pct"].values,
                         dict(color="#9467bd", lw=1.4)),
                        ("ODE (B) újraillesztve, kappa = 0", oB_re["kieso_pct"].values,
                         dict(color="#2ca02c", lw=1.4))]))
    K.plot(oA, panels, "HCW-kontaktkarantén nélkül", K.OUT / "karanten_kiserlet.png")
    print("Kimenet:", K.OUT)


if __name__ == "__main__":
    main()
