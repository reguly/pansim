"""A panSim (ABM) forgatókönyveinek ODE-párja: minden forgatókönyvet a beavatkozásnak megfelelő
ODE-paraméterváltozással futtat, és a HCW-fertőzésekre gyakorolt hatást összeveti az ABM-mel.

Az ODE-paraméterek az "A" illesztésből jönnek (kalibracio.py), és NEM illesztjük őket a
forgatókönyvre: a HCW-eredmény mindenhol előrejelzés. Forgatókönyvenként:
  - a napi oltások a forgatókönyv saját panSim-futásából jönnek (pl. a noVacc-ban nincs oltás);
  - a variánsszorzó, v(t) a köteg baseline-jából jön: a panSim MUT oszlopa a variánsok aránya a
    fertőzöttek KÖZÖTT, tehát a járvány eredménye (pl. erősebb tesztelésnél korábban nő az alfa
    aránya), nem bemenet. Saját v(t) csak ott, ahol a forgatókönyvben nincs variáns-behozatal
    (closuresNone: noRules.json);
  - a beavatkozás paramétere a lenti KAROK szerint változik;
  - a populációs beavatkozásoknál (korlátozások, populációs karantén) a c(t) kontaktusszorzót
    újraillesztjük, de CSAK a populációs görbékre (kórházi ápoltak, új civil fertőzések,
    halálozás). Ezek a beavatkozások az ODE-ben nem jelennek meg külön tagként, a c(t)-be
    olvadnak; a HCW-eredmény így is előrejelzés marad.

Beavatkozás -> ODE (a forgatókönyv nevének "_"-sal elválasztott részei; a kombinációk ezek
egymás utáni alkalmazása):
  hcwPPE                  beta_PH, beta_HH x 0,3 (HospitalPPE paramétere: kórházban és rendelőben a
                          fertőzőképesség 70 %-kal kisebb)
  hiTest, hcwDailyTest    c_test a panSim HCI-bontásából mérve (a kiszűrt fertőzött HCW-k aránya),
                          a 259. nap előtt és után külön (lásd c_test_meres())
  noVaccHCW               a HCW-k nem kapnak adagot, az adagok a civilekhez mennek
  noVacc                  nincs oltás (a panSim-futás bemenete)
  hcwNoQuarantine(Mar21)  nincs HCW-kontaktkarantén (Q_h = 0) a 0. (ill. 183.) naptól
  longQuarantine          kappa_comm x 21/10 (a karantén 10 helyett 21 napig tart); c(t) újraillesztve
  quarantine0             kappa = 0, c_test = 0 (a diagnosztizált HCW sem marad otthon);
                          c(t) újraillesztve
  closuresNone, closuresOnlyNone   c(t) újraillesztve

A forgatókönyveket a saját kötegük baseline-jához hasonlítjuk (results_hci_split/, ha ott megvan,
különben results/): két baseline-köteg között ~3 % eltérés volt (stochasticity.py).

Futtatás: python forgatokonyvek.py   (kimenet: kalibracio_kimenet/forgatokonyvek/)
"""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import kalibracio as K  # noqa: E402

KOTEGEK = [K.HERE.parent / "results_hci_split", K.HERE.parent / "results"]   # előbb az újabb köteg
OUT = K.OUT / "forgatokonyvek"
TESZT_VALTAS = 259        # a lezárási fájl TestingProb szabálya: ettől a naptól 0,5 a kórházi tesztelés
PPE = 0.3                 # ..._hospitalPPE.json: HospitalPPE parameter
KARANTEN_HOSSZ = 21/10    # longQuarantine: --quarantineLength 21 (alap: 10)
SPLIT = ["HCWH", "HCWD", "HCWQI", "HCWQN", "HCWU"]
N_BOOT = 2000
rng = np.random.default_rng(0)


# %% 1. Beolvasás
def beolvas(d):
    """Egy panSim-forgatókönyv: napi átlagok (bemenetek, populációs görbék, HCI-bontás) és a
    futásonkénti összesítések."""
    df = K.load_scenario(d)
    mut = df["MUT"].astype(str).str.split(",", expand=True).astype(float)
    df["alpha"], df["delta"] = mut[0]/100, mut[1]/100
    df["hosp"] = df["I5_h"] + df["I6_h"]
    df["I0"] = df[["E", "I1", "I2", "I3", "I4"]].sum(axis=1)
    cols = ["hosp", "NI", "HCE", "HCI", "VAC", "alpha", "delta", "D1", "I0", "R", "R_h"]
    cols += [c for c in SPLIT if c in df]
    m = df.groupby("day")[cols].mean()
    m["new_civ"] = m["NI"] - m["HCE"]
    futas = df.groupby("run").agg(hcw=("HCE", "sum"), osszes=("NI", "sum"))
    futas["civ"] = futas["osszes"] - futas["hcw"]
    return m, futas


def c_test_meres(m, a, b, min_fertozott=20):
    """A kiszűrt (diagnosztizált) HCW-k aránya a nem kórházi fertőzött HCW-k között, az [a, b)
    napokon: HCWD / (HCWD + HCWQI + HCWU), a napi átlagokat összegezve. Csak azok a napok
    számítanak, amelyeken legalább min_fertozott fertőzött HCW van (különben zaj)."""
    if "HCWD" not in m:
        return None
    s = m.loc[(m.index >= a) & (m.index < b)]
    nevezo = s["HCWD"] + s["HCWQI"] + s["HCWU"]
    ok = nevezo >= min_fertozott
    return float(s["HCWD"][ok].sum()/nevezo[ok].sum()) if ok.any() else None


# %% 2. Paraméterek és bemenetek
def a_parameterek():
    """Az "A" illesztés teljes pontossággal (ha a kalibracio.py futtatása után elmentettük),
    különben a parameterek.json kerekített értékei."""
    f = K.OUT / "A_teljes_pontossag.json"
    d = json.loads(f.read_text()) if f.exists() else \
        json.loads((K.OUT / "parameterek.json").read_text(encoding="utf-8"))["A_panSim"]
    return {k: (np.array(v) if isinstance(v, list) else v) for k, v in d.items()}


def bemenetek(m, m_var, hcw_olt=True):
    """Oltások az m (a forgatókönyv), variánsarányok az m_var (rendszerint a baseline) futásból."""
    day = m.index.values.astype(float)
    inp = K.make_inputs(day, m_var["alpha"].values, m_var["delta"].values, m["VAC"].values)
    if not hcw_olt:                      # noVaccHCW: a HCW-k kimaradnak, minden adag a civileké
        inp["u_c"] = np.clip(m["VAC"].values, 0, None)
        inp["u_h"] = np.zeros_like(day)
        inp["vax_h_frac"] = np.zeros_like(day)
    return inp


def kezdeti(m):
    return K.initial_state(m["I0"].iloc[0], m["hosp"].iloc[0], m["R"].iloc[0] + m["R_h"].iloc[0], m["D1"].iloc[0])


def karok(nev):
    """A forgatókönyv neve -> a beavatkozási karok listája (a "_"-sal elválasztott részek)."""
    return [] if nev == "baseline" else nev.split("_")


def beallit(nev, pA, meresek):
    """A forgatókönyv ODE-paraméterei, a bemenet-beállítás és az, hogy kell-e c(t)-t illeszteni."""
    p = dict(pA)
    hcw_olt, illeszt, megj = True, False, []
    for kar in karok(nev):
        if kar == "hcwPPE":
            p["beta_PH"] *= PPE
            p["beta_HH"] *= PPE
        elif kar in ("hiTest", "hcwDailyTest"):
            r = meresek.get(kar)
            if r is None:
                megj.append(f"{kar}: c_test nincs mérve, alapérték")
                continue
            c1, c2 = min(pA["c_test"]*r[0], 0.99), min(pA["c_test"]*r[1], 0.99)
            p["c_test_ido"] = (TESZT_VALTAS, c1, c2)
            megj.append(f"c_test {c1:.2f} / {c2:.2f} (a {TESZT_VALTAS}. nap előtt / után)")
        elif kar == "noVaccHCW":
            hcw_olt = False
        elif kar == "noVacc":
            pass                          # a panSim-futás VAC oszlopa 0
        elif kar == "hcwNoQuarantine":
            p["kappa_off_day"] = 0
        elif kar == "hcwNoQuarantineMar21":
            p["kappa_off_day"] = 183
        elif kar == "longQuarantine":
            p["kappa_comm"] *= KARANTEN_HOSSZ
            illeszt = True
        elif kar == "quarantine0":
            p["kappa_comm"] = p["kappa_work"] = 0.0
            p["c_test"] = 0.0
            p.pop("c_test_ido", None)
            illeszt = True
        elif kar in ("closuresNone", "closuresOnlyNone"):
            illeszt = True
        else:
            raise ValueError(f"ismeretlen beavatkozás: {kar} ({nev})")
    if "quarantine0" in karok(nev) and "c_test_ido" in p:   # a diagnózis itt nem jár otthon maradással
        p.pop("c_test_ido")
    return p, hcw_olt, illeszt, megj


def c_illesztes(nev, p, m, inp, x0):
    """A c(t) újraillesztése a forgatókönyv populációs görbéire (a HCW-paraméterek rögzítettek)."""
    sm = lambda s: s.rolling(7, center=True, min_periods=1).mean().values  # noqa: E731
    celok = [("hosp", m["hosp"].values, 1.0, "hosp"),
             ("new_civ", sm(m["new_civ"]), 1.0, "new_civ"),
             ("deaths", (m["D1"] - m["D1"].iloc[0]).values, 0.5,
              lambda o: o["deaths"].values - o["deaths"].iloc[0])]
    return K.fit(celok, p, [], lambda _: x0, inp, c_init=p["c_knots"], c_prior=p["c_knots"],
                 label=f"c(t): {nev}")


# %% 3. Összevetés
def arany_ci(x, y):
    """Az átlagok aránya (x / y) és bootstrap 95 % CI-je (futások független húzásként)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    bx = x[rng.integers(0, len(x), (N_BOOT, len(x)))].mean(axis=1)
    by = y[rng.integers(0, len(y), (N_BOOT, len(y)))].mean(axis=1)
    return x.mean()/y.mean(), *np.percentile(bx/by, [2.5, 97.5])


def main():
    np.seterr(all="ignore")
    OUT.mkdir(parents=True, exist_ok=True)
    pA = a_parameterek()

    # forgatókönyvek kötegenként; ha egy név több kötegben is megvan, az elsőt (újabbat) használjuk
    kotegek, latott = {}, set()
    for gy in KOTEGEK:
        if not (gy / "baseline" / "all_runs.tsv").exists():
            continue
        nevek = sorted(d.name for d in gy.iterdir() if (d / "all_runs.tsv").exists())
        kotegek[gy] = [n for n in nevek if n == "baseline" or n not in latott]
        latott.update(kotegek[gy])

    # c_test-mérések: a forgatókönyv / a saját baseline-ja, a 259. nap előtt és után
    meresek = {}
    for gy, nevek in kotegek.items():
        m_b, _ = beolvas(gy / "baseline")
        for kar in ("hiTest", "hcwDailyTest"):
            if kar in nevek and kar not in meresek:
                m_s, _ = beolvas(gy / kar)
                r = []
                for a, b in [(0, TESZT_VALTAS), (TESZT_VALTAS, 10_000)]:
                    s, bb = c_test_meres(m_s, a, b), c_test_meres(m_b, a, b)
                    r.append(s/bb if s and bb else None)
                if r[0] is not None:
                    meresek[kar] = (r[0], r[1] if r[1] is not None else r[0])
    print("c_test mérés (forgatókönyv / baseline, a 259. nap előtt és után):", meresek)

    sorok, idosorok = [], {}
    for gy, nevek in kotegek.items():
        m_b, f_b = beolvas(gy / "baseline")
        o_b = K.simulate(pA, bemenetek(m_b, m_b), kezdeti(m_b))
        for nev in nevek:
            m, f = beolvas(gy / nev)
            try:
                p, hcw_olt, illeszt, megj = beallit(nev, pA, meresek)
            except ValueError as e:
                print("kihagyva:", e)
                continue
            van_varians = m[["alpha", "delta"]].to_numpy().max() > 0
            inp, x0 = bemenetek(m, m_b if van_varians else m, hcw_olt), kezdeti(m)
            if illeszt:
                p = c_illesztes(nev, p, m, inp, x0)
            o = K.simulate(p, inp, x0)
            arany, lo, hi = arany_ci(f["hcw"], f_b["hcw"])
            rr_abm = ((f["hcw"]/K.N_h)/(f["civ"]/K.N_c)).mean()
            tot = o["cum_hcw"].iloc[-1]
            sorok.append({
                "forgatokonyv": nev, "koteg": gy.name, "c_ujraillesztve": illeszt,
                "ABM_HCW_fertozes": round(f["hcw"].mean()), "ABM_arany": round(arany, 3),
                "ABM_arany_ci": f"{lo:.3f}-{hi:.3f}", "ODE_HCW_fertozes": round(tot),
                "ODE_arany": round(tot/o_b["cum_hcw"].iloc[-1], 3),
                "ABM_RR": round(rr_abm, 3), "ODE_RR": round((tot/K.N_h)/(o["cum_civ"].iloc[-1]/K.N_c), 3),
                "ODE_kozosseg_pct": round(100*o["cum_comm"].iloc[-1]/tot, 1),
                "ODE_beteg_pct": round(100*o["cum_pat"].iloc[-1]/tot, 1),
                "ODE_kollega_pct": round(100*o["cum_staff"].iloc[-1]/tot, 1),
                "ODE_kieso_csucs_pct": round(o["kieso_pct"].max(), 2),
                "megjegyzes": "; ".join(megj)})
            idosorok[nev] = (m, o)
    tab = pd.DataFrame(sorok)
    tab.to_csv(OUT / "forgatokonyvek.csv", index=False)
    print(tab.drop(columns=["megjegyzes"]).to_string(index=False))

    # ---------- 1. ábra: hatás a HCW-fertőzésekre, ABM vs. ODE ----------
    t = tab[tab.forgatokonyv != "baseline"].sort_values("ABM_arany")
    fig, ax = plt.subplots(figsize=(9, 0.42*len(t) + 1.6), layout="constrained")
    y = np.arange(len(t))
    ci = t["ABM_arany_ci"].str.split("-", expand=True).astype(float)
    ax.hlines(y, ci[0], ci[1], color="#222222", lw=2)
    ax.plot(t["ABM_arany"], y, "o", color="#222222", ms=6, label="ABM (panSim), 20 futás, 95 % CI")
    ax.plot(t["ODE_arany"], y, "D", color="#e8710a", ms=6, label="ODE (A paraméterek, előrejelzés)")
    ax.axvline(1, color="0.5", ls="--", lw=1)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{n}{' *' if c else ''}" for n, c in zip(t.forgatokonyv, t.c_ujraillesztve)])
    ax.set_xscale("log")
    ax.set_xticks([0.4, 0.5, 0.7, 1, 1.4, 2])
    ax.set_xticklabels(["0,4", "0,5", "0,7", "1", "1,4", "2"])
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.set_xlabel("HCW-fertőzések egy év alatt, a saját baseline arányában")
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    ax.set_title("A beavatkozások hatása: ABM és ODE   (* c(t) a populációs görbékre újraillesztve)",
                 loc="left", fontsize=11)
    ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(OUT / "forgatokonyvek_hatas.png", dpi=150)
    plt.close(fig)

    # ---------- 2. ábra: új HCW-fertőzések időben, forgatókönyvenként ----------
    nevek = list(idosorok)
    ncol = 3
    fig, axs = plt.subplots(int(np.ceil(len(nevek)/ncol)), ncol, figsize=(13, 2.4*np.ceil(len(nevek)/ncol)),
                            sharex=True, layout="constrained")
    for ax, nev in zip(axs.flat, nevek):
        m, o = idosorok[nev]
        datum = K.START + pd.to_timedelta(m.index, "D")
        ax.plot(datum, m["HCE"].rolling(7, center=True, min_periods=1).mean(), color="#2a78d6", lw=1.6,
                label="ABM (7 napos átlag)")
        ax.plot(K.START + pd.to_timedelta(o.index, "D"), o["new_hcw"], "--", color="#e8710a", lw=1.6, label="ODE")
        ax.set_title(nev, loc="left", fontsize=10)
        ax.grid(axis="y", color="0.9")
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axs.flat[len(nevek):]:
        ax.axis("off")
    axs.flat[0].legend(frameon=False, fontsize=8)
    for ax in axs[-1]:
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    fig.suptitle("Új HCW-fertőzések naponta: ABM és ODE", x=0.01, ha="left", fontsize=12)
    fig.savefig(OUT / "forgatokonyvek_hce.png", dpi=130)
    plt.close(fig)
    print("Kimenet:", OUT)


if __name__ == "__main__":
    main()
