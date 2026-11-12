"""A SIHDR_HCW_v3 ODE-modell kalibrálása
  (A) a panSim alapesetéhez (results/baseline, 20 futás átlaga), és
  (B) a valós adatokhoz (korona_hun.xlsx: kórházi ápoltak és halálozás; SZTE: kieső dolgozók).

Az egyenletek a SIHDR_HCW_v3.py egyenletei (5-6. pont). Négy bővítést kapott, ezek kikapcsolva
(c = 1, v = 1, nincs oltás, kappa = 0) pontosan a v3-at adják (lásd ellenorzes_v3()):
  1) c(t): a közösségi kontaktusok időfüggő szorzója (zárások, iskolák, kijárási tilalom).
     Csak a közösségi fertőzési erőkre hat; a kórházi tagokra nem (a kórházakat nem zárták be).
  2) v(t): variánsszorzó (alfa 1,85/0,98, delta 2,05/0,98, a panSim infectiousnessMultiplier-e),
     a panSim MUT oszlopában lévő variánsarányokkal súlyozva. Minden fertőzési erőre hat.
  3) Oltás: a napi oltásszám e_v hatékonysággal S -> R áramot ad, 14 nap késleltetéssel.
     A HCW-k kapják az első 0,9*N_h adagot (panSim: --immunizationOrder, 90%-os szint).
  4) Karanténban lévő, nem fertőzött HCW-k (Q_h), algebrai megfigyelt mennyiség:
       Q_h = [kappa_comm*N_h*I/N        (háztartási/közösségi kontaktus miatti karantén)
              + kappa_work*c_test*I_h]  (munkahelyi kontaktus miatti karantén)
             * (1 - beoltott HCW-k aránya)
     A Q_h is kiesik a munkából (a Kieso_dolgozok_szama része). A panSim-ben a kórházat és a
     rendelőt soha nem zárja munkahelyi karantén, ezért az (A) kalibrációban kappa_work = 0.
     A beoltottakat a panSim nem teszi kontaktkarantén alá (movementPolicies.h, quarantineAgent:
     quarantineImmuneActive = false), ezért a szorzó (1 - beoltottak aránya), az első adagtól.

Megfigyelt mennyiségek:
  panSim HCI  = a fertőzött VAGY karanténban lévő HCW-k %-a  ~  (I_h + H_h + Q_h)/N_h,
                futásonként egészre csonkolva (ezért az összevetésben max(x - 0,5; 0))
  panSim HCE  = új HCW-fertőzések naponta             ~  lambda_h*S_h
  SZTE kieső  = COVID miatt nem dolgozók %-a            ~  (c_test*I_h + H_h + Q_h)/N_h
  kórházi ápoltak                                      ~  H_c + H_h

Futtatás: python kalibracio.py   (kimenet: ODE/kalibracio_kimenet/)
A valós SZTE-adat bizalmas, a git által figyelmen kívül hagyott
experiments/validation_1yr/data/hungarian_data/ mappából olvassuk; ha nincs meg, a (B) kihagyja.
"""
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE.parent))
from hcw.load import load_scenario  # noqa: E402

OUT = HERE / "kalibracio_kimenet"
SZTE_CSV = REPO / "experiments/validation_1yr/data/hungarian_data/szte_kieso_digitalizalt.csv"

START = pd.Timestamp("2020-09-23")     # a panSim 0. napja
T = 363                                # a panSim alapeset utolsó napja (364 nap, 52 hét)
N_ALL = 178746                         # panSim (agents1.json) teljes populáció
N_h = 10136                            # ebből egészségügyi dolgozó (12-es és 14-es munkahely)
N_c = N_ALL - N_h
HUNGARY_POPULATION = 9_700_000         # mint a validation_1yr-ben
SZTE_UNTIL = pd.Timestamp("2021-06-10")  # utána a görbe 0 nov. közepéig: hiányzó adat, nem valós 0

# Változatlanul a v3-ból átvett értékek (ahol nem kalibrálunk)
V3 = dict(beta=1/3, omega=1/180, tau_I=1/8, p_D=0.3, tau_H_c=1/10, tau_H_h=1/10, p_H_c=0.25,
          p_H_h=0.1, theta=0.5, sigma_c=0.7, sigma_w=0.3, beta_p=1/3, beta_s=1/3, q_H=0.7,
          q_I_h=0.1, c_test=0.7, P_0=5e4, kappa_comm=0.0, kappa_work=0.0, e_v=0.0)

KNOT_STEP = 21                                   # c(t) csomópontjai 3 hetente
KNOTS = np.arange(0, T + KNOT_STEP, KNOT_STEP, dtype=float)


# %% 1. A modell jobb oldala (a v3 5-6. pontja + bővítések)
def rhs(t, x, p, inp):
    S_c, I_c, H_c, D_c, R_c, S_h, I_h, H_h, D_h, R_h = x[:10]
    c = np.interp(t, KNOTS, p["c_knots"]) if "c_knots" in p else 1.0
    v = np.interp(t, inp["day"], inp["v"]) if inp else 1.0
    u_c = np.interp(t, inp["day"], inp["u_c"]) if inp else 0.0
    u_h = np.interp(t, inp["day"], inp["u_h"]) if inp else 0.0
    nem_mentes = 1 - np.interp(t, inp["day"], inp["vax_h_frac"]) if inp else 1.0

    I = I_c + I_h
    H = H_c + H_h
    N = N_c + N_h
    Q_h = (p["kappa_comm"]*N_h*I/N + p["kappa_work"]*p["c_test"]*I_h)*nem_mentes
    if t < p.get("vax_exempt_from_day", 0):          # eddig a beoltottak is karanténba kerülnek
        nem_mentes = 1.0
        Q_h = p["kappa_comm"]*N_h*I/N + p["kappa_work"]*p["c_test"]*I_h
    Q_h *= t < p.get("kappa_off_day", np.inf)        # ettől a naptól nincs HCW-kontaktkarantén
    Kieso_dolgozok_szama = p["c_test"]*I_h + H_h + D_h + Q_h
    N_w = N_h - Kieso_dolgozok_szama
    DA = N_w / N_h                                   # Dolgozok_aranya

    b = p["beta"]*v*c
    lambda_c = b*I/N
    lambda_comm = p["sigma_c"]*b*I/N
    lambda_pat = p["sigma_w"]*p["beta_p"]*v*p["q_H"]*H/(H + p["P_0"])
    lambda_staff = p["sigma_w"]*p["beta_s"]*v*p["q_I_h"]*(1-p["c_test"])*I_h/N_w
    parts = np.array([(1-p["theta"])*lambda_comm, p["theta"]*lambda_pat, p["theta"]*lambda_staff])
    lambda_h = parts.sum()

    # oltás: a nem fertőzött (S+R) csoport kapja az adagokat, az S-beliek e_v része lesz immunis
    vac_c = p["e_v"]*u_c*S_c/max(S_c + R_c, 1.0)
    vac_h = p["e_v"]*u_h*S_h/max(S_h + R_h, 1.0)

    tI, om, pD = p["tau_I"], p["omega"], p["p_D"]
    dS_c = -lambda_c*S_c + om*R_c - vac_c
    dI_c = lambda_c*S_c - tI*I_c
    dH_c = p["p_H_c"]*tI*I_c - p["tau_H_c"]*H_c/DA
    dD_c = pD*p["tau_H_c"]*H_c/DA**2
    dR_c = (1-p["p_H_c"])*tI*I_c + (1-pD/DA)*p["tau_H_c"]*H_c/DA - om*R_c + vac_c

    dS_h = -lambda_h*S_h + om*R_h - vac_h
    dI_h = lambda_h*S_h - tI*I_h
    dH_h = p["p_H_h"]*tI*I_h - p["tau_H_h"]*H_h/DA
    dD_h = pD*p["tau_H_h"]*H_h/DA**2
    dR_h = (1-p["p_H_h"])*tI*I_h + (1-pD/DA)*p["tau_H_h"]*H_h/DA - om*R_h + vac_h

    # kumulált számlálók: civil fertőzések, HCW-fertőzések útvonalanként, visszafertőződhetők
    cum = [lambda_c*S_c, *(parts*S_h), om*(R_c + R_h)]
    return np.array([dS_c, dI_c, dH_c, dD_c, dR_c, dS_h, dI_h, dH_h, dD_h, dR_h, *cum])


def simulate(p, inp, x0, T_end=T, t_eval=None):
    """Illesztéshez fix lépésű RK4 (dt = 1/4 nap): a célfüggvény így sima a paraméterekben, a
    véges differenciás Jacobi-mátrix nem zajos. Ha t_eval adott, adaptív RK45 (solve_ivp)."""
    y0 = np.concatenate([x0, np.zeros(5)])
    if t_eval is not None:
        sol = solve_ivp(rhs, (0, T_end), y0, args=(p, inp), method="RK45", rtol=1e-6, atol=1e-6,
                        t_eval=t_eval, max_step=1.0)
        if not sol.success:
            raise RuntimeError(sol.message)
        return observe(sol.t, sol.y.T, p, inp)
    sub = 4
    dt = 1/sub
    y = y0.copy()
    out = [y0]
    for k in range(T_end*sub):
        t0 = k*dt
        k1 = rhs(t0, y, p, inp)
        k2 = rhs(t0 + dt/2, y + dt/2*k1, p, inp)
        k3 = rhs(t0 + dt/2, y + dt/2*k2, p, inp)
        k4 = rhs(t0 + dt, y + dt*k3, p, inp)
        y = y + dt/6*(k1 + 2*k2 + 2*k3 + k4)
        if (k + 1) % sub == 0:
            out.append(y)
    y = np.array(out)
    if not np.all(np.isfinite(y)):
        raise RuntimeError("nem véges megoldás")
    return observe(np.arange(T_end + 1, dtype=float), y, p, inp)


def observe(tt, y, p, inp=None):
    S_c, I_c, H_c, D_c, R_c, S_h, I_h, H_h, D_h, R_h = y[:, :10].T
    I = I_c + I_h
    nem_mentes = 1 - np.interp(tt, inp["day"], inp["vax_h_frac"]) if inp else 1.0
    Q_h = (p["kappa_comm"]*N_h*I/N_ALL + p["kappa_work"]*p["c_test"]*I_h)*nem_mentes
    nem_mentes = np.where(tt < p.get("vax_exempt_from_day", 0), 1.0, nem_mentes)
    Q_h = (p["kappa_comm"]*N_h*I/N_ALL + p["kappa_work"]*p["c_test"]*I_h)*nem_mentes
    Q_h = Q_h*(tt < p.get("kappa_off_day", np.inf))
    o = pd.DataFrame(index=pd.Index(tt, name="day"))
    o["civil_prev_pct"] = 100*I_c/N_c
    o["hcw_prev_pct"] = 100*(I_h + H_h)/N_h
    o["I_h_pct"] = 100*I_h/N_h
    o["hosp"] = H_c + H_h
    o["deaths"] = D_c + D_h
    o["Q_h"] = Q_h
    o["hci_pct"] = 100*(I_h + H_h + Q_h)/N_h                     # panSim HCI megfelelője
    o["kieso_pct"] = 100*(p["c_test"]*I_h + H_h + Q_h)/N_h       # SZTE kieső megfelelője
    o["dolgozo_arany"] = 1 - (p["c_test"]*I_h + H_h + D_h + Q_h)/N_h
    o["cum_civ"], o["cum_comm"], o["cum_pat"], o["cum_staff"], o["cum_reinf"] = y[:, 10:].T
    o["cum_hcw"] = o[["cum_comm", "cum_pat", "cum_staff"]].sum(axis=1)
    o["new_civ"] = o["cum_civ"].diff()
    o["new_hcw"] = o["cum_hcw"].diff()
    return o


# %% 2. Ellenőrzés: bővítések nélkül a v3 eredményeit kell adnia
def ellenorzes_v3():
    p = dict(V3)
    x0 = np.array([180000 - 10100 - 10, 10, 0, 0, 0, 10100, 0, 0, 0, 0], dtype=float)
    global N_c, N_h, N_ALL
    saved = N_c, N_h, N_ALL
    N_h, N_c, N_ALL = 10100, 180000 - 10100, 180000
    try:
        o = simulate(p, None, x0, T_end=round(4/12*365), t_eval=np.linspace(0, 122, 4881))
    finally:
        N_c, N_h, N_ALL = saved
    return o["civil_prev_pct"].max(), o["I_h_pct"].max(), o["cum_hcw"].iloc[-1]


# %% 3. Bemenetek: panSim alapeset
def load_sim():
    df = load_scenario(REPO / "experiments/hcw_interventions/results/baseline")
    mut = df["MUT"].str.split(",", expand=True).astype(float)
    df["alpha"], df["delta"] = mut[0]/100, mut[1]/100
    df["hosp"] = df["I5_h"] + df["I6_h"]
    df["I0"] = df[["E", "I1", "I2", "I3", "I4"]].sum(axis=1)
    cols = ["hosp", "NI", "HCE", "HCI", "VAC", "alpha", "delta", "D1", "I0", "R", "R_h", "H"]
    m = df.groupby("day")[cols].mean()
    m["new_civ"] = m["NI"] - m["HCE"]
    return m


def make_inputs(day, alpha, delta, doses, hcw_doses_until=None):
    """Variánsszorzó és csoportonkénti napi oltásszám. A HCW-k kapják az első 0,9*N_h adagot,
    vagy (valós eset) hcw_doses_until napig egyenletesen."""
    v = 1 + (1.85/0.98 - 1)*alpha + (2.05/0.98 - 1)*delta
    doses = np.asarray(doses, dtype=float)
    if hcw_doses_until is None:
        cum = np.cumsum(doses)
        u_h = np.diff(np.minimum(cum, 0.9*N_h), prepend=0.0)
    else:
        a, b = hcw_doses_until
        u_h = np.where((day >= a) & (day < b), 0.9*N_h/(b - a), 0.0)
    u_c = np.clip(doses - u_h, 0, None)
    lag = 14                                       # védettség kialakulása
    shift = lambda s: np.concatenate([np.zeros(lag), s[:-lag]])  # noqa: E731
    return dict(day=np.asarray(day, dtype=float), v=np.asarray(v), u_c=shift(u_c), u_h=shift(u_h),
                vax_h_frac=np.minimum(np.cumsum(u_h)/N_h, 1.0))


# %% 4. Bemenetek: valós adatok
def load_real():
    k = pd.read_excel(REPO / "korona_hun.xlsx", sheet_name="koronahun", header=0)
    k = k.iloc[:, [0, 3, 19, 32]]
    k.columns = ["date", "deaths_cum", "hosp", "vacc1_cum"]
    k["date"] = pd.to_datetime(k["date"], errors="coerce")
    k = k.dropna(subset=["date"]).drop_duplicates("date").set_index("date").apply(pd.to_numeric, errors="coerce")
    idx = pd.date_range(START, periods=T + 1)
    k = k.reindex(idx).interpolate(limit_area="inside")
    scale = N_ALL / HUNGARY_POPULATION
    r = pd.DataFrame(index=pd.RangeIndex(T + 1, name="day"))
    r["hosp"] = k["hosp"].values*scale
    r["deaths"] = (k["deaths_cum"].values - k["deaths_cum"].iloc[0])*scale
    r["doses"] = np.diff(k["vacc1_cum"].fillna(0).values, prepend=0.0).clip(0)*scale
    if SZTE_CSV.exists():
        s = pd.read_csv(SZTE_CSV, comment="#", parse_dates=["datum"]).set_index("datum")["kieso_szazalek"]
        s = s[s.index <= SZTE_UNTIL]
        s = s.reindex(pd.date_range(s.index[0], s.index[-1])).interpolate()
        r["szte"] = s.reindex(idx).values
    return r


# %% 5. Kalibráció
def pack(p_fit, names, base, nk):
    p = dict(base)
    if nk:
        p["c_knots"] = np.exp(p_fit[:nk])
    for n, val in zip(names, p_fit[nk:]):
        p[n] = val
    if "LOS" in p:
        p["tau_H_c"] = p["tau_H_h"] = 1/p["LOS"]
    if "hpr" in p:
        p["p_H_h"] = p["hpr"]*p["p_H_c"]
    return p


def initial_state(I0, H0, R0, D0, I_h0_pct=None):
    """A kezdeti fertőzöttek a létszám arányában oszlanak meg; I_h0_pct megadásával a HCW-k kezdeti
    fertőzöttsége (a HCW-k %-ában) a civilektől függetlenül állítható."""
    sh = N_h/N_ALL
    I_h0 = I0*sh if I_h0_pct is None else I_h0_pct/100*N_h
    return np.array([N_c - I0*(1-sh) - H0 - R0 - D0, I0*(1-sh), H0, D0, R0,
                     N_h - I_h0, I_h0, 0, 0, 0], dtype=float)


def nrm(a):
    return np.nanmax(np.abs(a))


def fit(targets, base, free, x0_fun, inp, priors=None, smooth=0.5, label="", c_init=None, fit_c=True,
        c_prior=None):
    """Súlyozott legkisebb négyzetes illesztés. fit_c=False: a c(t) csomópontjai a base["c_knots"]
    értéken rögzítettek, csak a `free` paramétereket illesztjük."""
    nk = len(KNOTS) if fit_c else 0
    names = [f[0] for f in free]
    c0 = np.log(c_init) if c_init is not None else np.full(nk, np.log(0.5))
    p0 = np.concatenate([c0[:nk], [f[1] for f in free]])
    lo = np.concatenate([np.full(nk, np.log(0.05)), [f[2] for f in free]])
    hi = np.concatenate([np.full(nk, np.log(3.0)), [f[3] for f in free]])

    def resid(z):
        p = pack(z, names, base, nk)
        try:
            o = simulate(p, inp, x0_fun(p))
        except (RuntimeError, ValueError, FloatingPointError):
            return np.full(n_res, 1e3)
        r = []
        for col, obs, w, tr in targets:
            mod = tr(o) if callable(tr) else o[tr].values
            ok = ~np.isnan(obs) & ~np.isnan(mod)
            r.append(w*(mod[ok] - obs[ok])/nrm(obs[ok])/np.sqrt(ok.sum()))
        if nk:
            r.append(smooth*np.diff(z[:nk], 2)/np.sqrt(nk))      # c(t) simasága
        if c_prior is not None:                                  # gyenge húzás egy referencia c(t) felé
            r.append(0.02*(z[:nk] - np.log(c_prior))/np.sqrt(nk))
        for n, (mu, sd) in (priors or {}).items():
            r.append(np.atleast_1d((np.log(p[n]) - np.log(mu))/sd*0.05))
        return np.concatenate(r)

    n_res = len(resid(p0))
    sol = least_squares(resid, p0, bounds=(lo, hi), x_scale="jac", diff_step=1e-3, max_nfev=300,
                        xtol=1e-9, ftol=1e-9, gtol=1e-9)
    p = pack(sol.x, names, base, nk)
    print(f"[{label}] cost={sol.cost:.4g}, nfev={sol.nfev}, status={sol.status}")
    return p


def metrics(mod, obs):
    ok = ~np.isnan(obs) & ~np.isnan(mod)
    m, o = mod[ok], obs[ok]
    return dict(r=float(np.corrcoef(m, o)[0, 1]), rmse=float(np.sqrt(np.mean((m - o)**2))),
                peak_obs=float(o.max()), peak_mod=float(m.max()))


def window_peak(series, a, b):
    s = pd.Series(np.asarray(series), index=START + pd.to_timedelta(np.arange(len(series)), "D"))[a:b]
    return round(float(s.max()), 2), str(s.idxmax().date())


# %% 6. Ábrák
def plot(o, panels, title, path):
    dates = START + pd.to_timedelta(o.index, "D")
    fig, axs = plt.subplots(len(panels), 1, figsize=(10, 2.6*len(panels)), sharex=True,
                            layout="constrained")
    for ax, (ttl, ylab, series) in zip(np.atleast_1d(axs), panels):
        for lab, y, style in series:
            ax.plot(dates[:len(y)], y, label=lab, **style)
        ax.set_title(ttl, loc="left", fontsize=10)
        ax.set_ylabel(ylab)
        ax.grid(axis="y", color="#e6e6e6")
        for s in ["top", "right"]:
            ax.spines[s].set_visible(False)
        ax.legend(fontsize=8, frameon=False, loc="best")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y.%m"))
    fig.suptitle(title, x=0.01, ha="left", fontsize=11)
    fig.savefig(path, dpi=150)
    plt.close(fig)


SIM = dict(color="#2a78d6", lw=2)
REAL = dict(color="#222222", lw=2)
ODE_A = dict(color="#e8710a", lw=2, ls="--")
ODE_B = dict(color="#1a9e77", lw=2, ls="--")


def to_json(p):
    return {k: (np.round(v, 4).tolist() if isinstance(v, np.ndarray) else round(float(v), 5))
            for k, v in p.items()}


def main():
    OUT.mkdir(exist_ok=True)
    np.seterr(all="ignore")

    c_peak, h_peak, cum_h = ellenorzes_v3()
    print(f"v3-ellenőrzés: civil csúcs {c_peak:.2f} %, HCW csúcs {h_peak:.2f} %, kumulált HCW {cum_h:.0f}"
          "  (v3: 25,04 % / 15,52 % / 7145)")

    m = load_sim()
    day = m.index.values.astype(float)
    inp_A = make_inputs(day, m["alpha"].values, m["delta"].values, m["VAC"].values)

    # Közös, a panSim-ből vett (nem illesztett) értékek
    base = dict(V3)
    base.update(
        omega=1/1000,       # panSim: fertőzés utáni védettség 85 %, heti 0,3 % csökkenés -> lassú
        P_0=float(m["H"].iloc[14:].mean()),   # nem-COVID kórházi betegek (panSim H oszlop)
        e_v=0.77,           # panSim protectionInfection, 2 adag, hasonló törzs
        c_test=0.35,        # panSim: pozitív tesztek / új fertőzések ~ 0,33 a 2. hullámban
        kappa_work=0.0,     # panSim: kórházat nem zár be munkahelyi karantén
        hpr=1.0,            # p_H_h = p_H_c: a panSim nem írja ki külön a HCW-k kórházi felvételét
        LOS=10.0,           # panSim progresszió: I5_h/I6_h átlagos hossza 10 nap (= v3 tau_H = 1/10).
    )                       # Szabadon hagyva 3 napra futna le (a p_H_c-vel csak a szorzatuk azonosítható)
    base["tau_H_c"] = base["tau_H_h"] = 1/base["LOS"]
    x0_A = lambda p: initial_state(m["I0"].iloc[0], m["hosp"].iloc[0], m["R"].iloc[0] + m["R_h"].iloc[0],  # noqa: E731
                                   m["D1"].iloc[0])

    # ---------- (A) panSim alapeset ----------
    hci_obs = lambda o: np.maximum(o["hci_pct"].values - 0.5, 0)  # noqa: E731  (HCI egészre csonkolt)
    sm = lambda s: s.rolling(7, center=True, min_periods=1).mean().values  # noqa: E731
    tA = [("hosp", m["hosp"].values, 1.0, "hosp"),
          ("new_civ", sm(m["new_civ"]), 1.0, "new_civ"),
          ("HCE", sm(m["HCE"]), 1.5, "new_hcw"),
          ("HCI", m["HCI"].values, 1.0, hci_obs),
          ("deaths", (m["D1"] - m["D1"].iloc[0]).values, 0.5, lambda o: o["deaths"].values - o["deaths"].iloc[0])]
    freeA = [("p_H_c", 0.05, 0.005, 0.3), ("p_D", 0.3, 0.05, 0.6),
             ("sigma_c", 2.0, 0.2, 4.0), ("beta_p", 1/3, 1e-3, 5.0), ("kappa_comm", 0.5, 0.0, 5.0)]
    pA = fit(tA, base, freeA, x0_A, inp_A, label="A: panSim")
    oA = simulate(pA, inp_A, x0_A(pA))

    # ---------- (B) valós adatok ----------
    real = load_real()
    inp_B = make_inputs(day, m["alpha"].values, m["delta"].values, real["doses"].values,
                        hcw_doses_until=(94, 130))   # HCW-oltás: 2020-12-26 .. 2021-01-31
    x0_B = lambda p: initial_state(p["I0"], real["hosp"].iloc[0], m["R"].iloc[0] + m["R_h"].iloc[0], 0.0,  # noqa: E731
                                   I_h0_pct=p["I_h0_pct"])
    # (B1) populáció: c(t), kórházi és halálozási paraméterek a valós kórházi ápoltakra és halálozásra
    baseB = dict(pA)
    baseB.update(I_h0_pct=100*m["I0"].iloc[0]/N_ALL)
    tB1 = [("hosp", real["hosp"].values, 1.0, "hosp"),
           ("deaths", real["deaths"].values, 0.5, lambda o: o["deaths"].values - o["deaths"].iloc[0])]
    # p_H_c és LOS az (A)-ból: a valós adatban csak kórházi ápolt és halott van, a fertőzések száma
    # nem azonosítható (szabadon hagyva a p_H_c lecsökken, és a populáció 80%-a megfertőződik).
    freeB1 = [("p_D", pA["p_D"], 0.05, 0.6), ("I0", m["I0"].iloc[0], 50, 5000)]
    pB = fit(tB1, baseB, freeB1, x0_B, inp_B, c_init=pA["c_knots"], c_prior=pA["c_knots"],
             label="B1: valós populáció")
    # (B2) HCW: rögzített populációs rész mellett a HCW-paraméterek az SZTE kieső görbéjére
    has_szte = "szte" in real
    if has_szte:
        tB2 = [("SZTE", real["szte"].values, 1.0, "kieso_pct")]
        freeB2 = [("sigma_c", pA["sigma_c"], 0.2, 4.0), ("beta_p", max(pA["beta_p"], 2e-3), 1e-3, 5.0),
                  ("kappa_comm", max(pA["kappa_comm"], 0.05), 0.0, 10.0), ("kappa_work", 1.0, 0.0, 20.0),
                  ("c_test", 0.5, 0.3, 0.9), ("I_h0_pct", 3.0, 0.0, 15.0)]
        pB = fit(tB2, pB, freeB2, x0_B, inp_B, fit_c=False,
                 priors={"sigma_c": (pA["sigma_c"], 1.0), "beta_p": (max(pA["beta_p"], 0.05), 1.0)},
                 label="B2: SZTE kieső dolgozók")
    oB = simulate(pB, inp_B, x0_B(pB))

    # ---------- Összevetés, mérőszámok ----------
    rr = lambda o: (o["cum_hcw"].iloc[-1]/N_h)/(o["cum_civ"].iloc[-1]/N_c)  # noqa: E731
    rows = {
        "A_kórházi_ápoltak": metrics(oA["hosp"].values, m["hosp"].values),
        "A_új_civil_fertőzés": metrics(oA["new_civ"].values, sm(m["new_civ"])),
        "A_HCE": metrics(oA["new_hcw"].values, sm(m["HCE"])),
        "A_HCI": metrics(hci_obs(oA), m["HCI"].values),
        "A_halálozás_kum": metrics(oA["deaths"].values - oA["deaths"].iloc[0], (m["D1"] - m["D1"].iloc[0]).values),
        "B_kórházi_ápoltak": metrics(oB["hosp"].values, real["hosp"].values),
        "B_halálozás_kum": metrics(oB["deaths"].values - oB["deaths"].iloc[0], real["deaths"].values),
        "B_kórházi_vs_panSim": metrics(m["hosp"].values, real["hosp"].values),
    }
    if has_szte:
        rows["B_SZTE_kieső"] = metrics(oB["kieso_pct"].values, real["szte"].values)
        rows["panSim_HCI_vs_SZTE"] = metrics(m["HCI"].values, real["szte"].values)
        rows["A_ODE_kieső_vs_SZTE"] = metrics(oA["kieso_pct"].values, real["szte"].values)
    met = pd.DataFrame(rows).T.round(3)
    print(met.to_string())
    met.to_csv(OUT / "illeszkedes.csv")

    summary = {}
    for lab, o in [("A_panSim", oA), ("B_valos", oB)]:
        tot = o["cum_hcw"].iloc[-1]
        summary[lab] = dict(
            incidence_RR=round(float(rr(o)), 3),
            kum_HCW_fertozes=round(float(tot)), kum_civil_fertozes=round(float(o["cum_civ"].iloc[-1])),
            kozossegbol_pct=round(100*o["cum_comm"].iloc[-1]/tot, 1),
            betegektol_pct=round(100*o["cum_pat"].iloc[-1]/tot, 1),
            kollegaktol_pct=round(100*o["cum_staff"].iloc[-1]/tot, 1),
            visszafertozodhetove_valt=round(float(o["cum_reinf"].iloc[-1])),
            min_dolgozo_arany_pct=round(100*o["dolgozo_arany"].min(), 1),
            hci_csucs_2hullam=window_peak(o["hci_pct"], "2020-09-23", "2021-01-31"),
            hci_csucs_3hullam=window_peak(o["hci_pct"], "2021-02-01", "2021-06-30"),
            kieso_csucs_2hullam=window_peak(o["kieso_pct"], "2020-09-23", "2021-01-31"),
            kieso_csucs_3hullam=window_peak(o["kieso_pct"], "2021-02-01", "2021-06-30"))
    sim_tot = m["HCE"].sum()
    summary["panSim_alapeset"] = dict(
        incidence_RR=round(float((sim_tot/N_h)/(m["new_civ"].sum()/N_c)), 3), kum_HCW_fertozes=round(float(sim_tot)),
        kum_civil_fertozes=round(float(m["new_civ"].sum())),
        hci_csucs_2hullam=window_peak(m["HCI"], "2020-09-23", "2021-01-31"),
        hci_csucs_3hullam=window_peak(m["HCI"], "2021-02-01", "2021-06-30"))
    if has_szte:
        summary["SZTE"] = dict(kieso_csucs_2hullam=window_peak(real["szte"].fillna(0), "2020-09-23", "2021-01-31"),
                               kieso_csucs_3hullam=window_peak(real["szte"].fillna(0), "2021-02-01", "2021-06-30"))
    print(json.dumps(summary, indent=1, ensure_ascii=False))
    (OUT / "parameterek.json").write_text(json.dumps(
        {"A_panSim": to_json(pA), "B_valos": to_json(pB), "osszegzes": summary,
         "c_csomopontok_napjai": KNOTS.tolist()}, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---------- Ábrák ----------
    plot(oA, [
        ("Kórházi ápoltak (H_c + H_h)", "fő", [("panSim", m["hosp"].values, SIM), ("ODE (A)", oA["hosp"].values, ODE_A)]),
        ("Új fertőzések, nem HCW", "fő/nap", [("panSim (7 napos átlag)", sm(m["new_civ"]), SIM),
                                               ("ODE (A)", oA["new_civ"].values, ODE_A)]),
        ("Új HCW-fertőzések (HCE)", "fő/nap", [("panSim (7 napos átlag)", sm(m["HCE"]), SIM),
                                                ("ODE (A)", oA["new_hcw"].values, ODE_A)]),
        ("HCI: fertőzött vagy karanténban lévő HCW-k", "%", [("panSim HCI", m["HCI"].values, SIM),
                                                             ("ODE (A), csonkolva", hci_obs(oA), ODE_A),
                                                             ("ODE (A), csonkolás nélkül", oA["hci_pct"].values,
                                                              dict(color="#e8710a", lw=1, ls=":"))]),
    ], "(A) ODE a panSim alapesetére illesztve", OUT / "A_panSim_illesztes.png")

    panels = [
        ("Kórházi ápoltak, a panSim populációjára skálázva", "fő",
         [("valós (korona_hun.xlsx)", real["hosp"].values, REAL), ("panSim", m["hosp"].values, SIM),
          ("ODE (B)", oB["hosp"].values, ODE_B)]),
        ("Kumulált COVID-halálozás a 0. naptól", "fő",
         [("valós", real["deaths"].values, REAL), ("panSim", (m["D1"] - m["D1"].iloc[0]).values, SIM),
          ("ODE (B)", (oB["deaths"] - oB["deaths"].iloc[0]).values, ODE_B)]),
    ]
    if has_szte:
        panels.append(("Kieső egészségügyi dolgozók", "a dolgozók %-a",
                       [("SZTE (valós)", real["szte"].values, REAL), ("panSim HCI", m["HCI"].values, SIM),
                        ("ODE (A) kieső", oA["kieso_pct"].values, ODE_A), ("ODE (B) kieső", oB["kieso_pct"].values, ODE_B)]))
    panels.append(("A közösségi kontaktusok szorzója, c(t)", "",
                   [("ODE (A)", np.interp(oA.index, KNOTS, pA["c_knots"]), ODE_A),
                    ("ODE (B)", np.interp(oB.index, KNOTS, pB["c_knots"]), ODE_B)]))
    plot(oB, panels, "(B) ODE a valós adatokra illesztve", OUT / "B_valos_illesztes.png")
    print("Kimenet:", OUT)


if __name__ == "__main__":
    main()
