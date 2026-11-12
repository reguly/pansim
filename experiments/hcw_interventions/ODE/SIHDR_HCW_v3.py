 """SIHDR járványmodell civilekre és egészségügyi dolgozókra (HCW)

A SIHDR_HCW_v3.m Python-fordítása (sympy + scipy + matplotlib). Az összefüggések, a paraméterek
és a kommentek megegyeznek a MATLAB-változattal; a MATLAB-specifikus lépések megfelelői:
    syms / subs / simplify / matlabFunction  ->  sympy.symbols / .subs / sympy.simplify / sympy.lambdify
    ode45                                    ->  scipy.integrate.solve_ivp(method="RK45"), ugyanaz a
                                                 Dormand-Prince módszer, az ode45 alapértelmezett
                                                 tűréseivel (RelTol 1e-3, AbsTol 1e-6) és kimeneti
                                                 sűrítésével (Refine = 4, lásd ode45_refined())
    trapz                                    ->  numpy.trapezoid
    tiledlayout / area / yline               ->  plt.subplots / stackplot / axhline

=========================================================================
Kompartmentek (mindkét csoportra, _c = civil, _h = egészségügyi dolgozó):
  S - fogékony
  I - fertőző (nem kórházban)
  H - kórházban ápolt
  D - elhunyt
  R - felgyógyult (az immunitás omega rátával csökken -> vissza S-be)

Fő modellezési gondolatok:
  1) A HCW-k fertőzési ereje két "univerzumból" áll, az ébrenléti idő
     theta, illetve (1-theta) arányában:
       - közösség: a teljes populációval normalizálva, a HCW-k
         fogékonysága sigma_c (< 1: óvatosabbak a hétköznapokban)
       - kórház: (a) beteg -> HCW kontaktus, a COVID-os betegek
         arányával (H / (H + P_0)) normalizálva,
                  (b) HCW -> HCW kontaktus, a ténylegesen dolgozók
         számával normalizálva
  2) A kieső dolgozók (detektált fertőzöttek + kórházban lévők + elhunytak)
     csökkentik a munkaerőt, ami rontja a kórházi ellátást: a kórházi
     kimenet (gyógyulás/halál) lassul a Dolgozok_aranya-val arányosan.

Megjegyzés: a fájl UTF-8 kódolású (ékezetes kommentek miatt).
=========================================================================
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sympy as sp
from scipy.integrate import solve_ivp

plt.close("all")

# %% 1. Szimbolikus állapotváltozók
# A "real" feltevés egyszerűsíti a szimbolikus kifejezéseket.
S_c, I_c, H_c, D_c, R_c = sp.symbols("S_c I_c H_c D_c R_c", real=True)
S_h, I_h, H_h, D_h, R_h = sp.symbols("S_h I_h H_h D_h R_h", real=True)

xc = [S_c, I_c, H_c, D_c, R_c]     # civilek kompartmentjei
xh = [S_h, I_h, H_h, D_h, R_h]     # HCW-k kompartmentjei
x = xc + xh                        # teljes állapotvektor (10 elem)

# %% 2. Szimbolikus paraméterek
# Közös paraméterek
beta, omega, tau_I, p_D = sp.symbols("beta omega tau_I p_D")  # beta: kontaktrátából eredő fertőzési ráta
                                                               # (a MATLAB-változatban felülírja a beta() beépített függvényt)
# Csoportspecifikus paraméterek
tau_H_c, tau_H_h, p_H_c, p_H_h = sp.symbols("tau_H_c tau_H_h p_H_c p_H_h")  # kórházi tartózkodás ill. kórházba kerülés valószínűsége
# Populációméretek
N_c, N_h = sp.symbols("N_c N_h")
# HCW-specifikus paraméterek
theta = sp.Symbol("theta")        # munkahelyi időarány az ébrenlétből (0.5 = fele)
sigma_c = sp.Symbol("sigma_c")    # HCW fogékonysága a közösségben (régi beta_rel_h)
sigma_w = sp.Symbol("sigma_w")    # HCW fogékonysága a munkahelyen (védőfelszerelés hatása; 1 = védtelen)
beta_p = sp.Symbol("beta_p")      # HCW-beteg kontaktusból eredő fertőzési ráta
beta_s = sp.Symbol("beta_s")      # HCW-HCW kontaktusból eredő fertőzési ráta
q_H = sp.Symbol("q_H")            # kórházi betegek relatív fertőzőképessége
q_I_h = sp.Symbol("q_I_h")        # fertőző HCW relatív fertőzőképessége a munkahelyen
c_test = sp.Symbol("c_test")      # a fertőző HCW-k detektált (és otthon maradó) hányada
P_0 = sp.Symbol("P_0")            # nem-COVID-os betegek száma a kórházakban

# Összegzett mennyiségek
I = I_c + I_h            # összes közösségi fertőző
H = H_c + H_h            # összes kórházban ápolt
N = N_c + N_h            # teljes populáció

# %% 3. Kieső és dolgozó HCW-k
# Nem dolgozik: a detektált fertőzöttek (otthon izolálnak), a kórházban
# ápolt, valamint az elhunyt dolgozók.
Kieso_dolgozok_szama = c_test*I_h + H_h + D_h

# Ténylegesen munkában lévő dolgozók száma és aránya
N_w = N_h - Kieso_dolgozok_szama
Dolgozok_aranya = N_w / N_h

# %% 4. Fertőzési erők
# --- Civilek: tisztán közösségi fertőzés, a teljes populációval normalizálva
lambda_c = beta*I/N

# --- HCW-k: három komponens
# (a) közösségi tag: sigma_c-vel csökkentett fogékonyság
lambda_comm = sigma_c*beta*I/N

# (b) kórházi beteg -> HCW: a HCW adott számú beteggel találkozik, amelyek
#     közül H/(H+P_0) a COVID-os. A kórházi dolgozók H_h tagjai is betegként
#     szerepelnek a H-ban (a dolgozói létszámból is kiesnek, lásd 3. pont).
lambda_pat = sigma_w*beta_p*q_H*H/(H + P_0)

# (c) kórházi HCW -> HCW: a nem detektált fertőző dolgozók, q_I_h relatív
#     fertőzőképességgel, a munkában lévő létszámmal normalizálva.
lambda_staff = sigma_w*beta_s*q_I_h*(1-c_test)*I_h/N_w

# A HCW eredő fertőzési ereje: időarányosan súlyozva
lambda_h = (1-theta)*lambda_comm + theta*(lambda_pat + lambda_staff)

# %% 5. Civilek dinamikája
dS_c = -lambda_c*S_c + omega*R_c
dI_c = lambda_c*S_c - tau_I*I_c
dH_c = p_H_c*tau_I*I_c - tau_H_c*H_c/Dolgozok_aranya
dD_c = p_D*tau_H_c*H_c/Dolgozok_aranya**2
dR_c = (1-p_H_c)*tau_I*I_c + (1-p_D/Dolgozok_aranya)*tau_H_c*H_c/Dolgozok_aranya - omega*R_c

# Ellenőrzés: a civilek száma nem változhat.
Megmaradasi_torveny_c = sp.simplify(dS_c + dI_c + dH_c + dD_c + dR_c)
print("Civilek megmaradási törvénye (0 kell legyen):")
print(Megmaradasi_torveny_c)

# %% 6. HCW-k dinamikája
dS_h = -lambda_h*S_h + omega*R_h
dI_h = lambda_h*S_h - tau_I*I_h
dH_h = p_H_h*tau_I*I_h - tau_H_h*H_h/Dolgozok_aranya
dD_h = p_D*tau_H_h*H_h/Dolgozok_aranya**2
dR_h = (1-p_H_h)*tau_I*I_h + (1-p_D/Dolgozok_aranya)*tau_H_h*H_h/Dolgozok_aranya - omega*R_h

# Ellenőrzés: a HCW-k száma nem változhat.
Megmaradasi_torveny_h = sp.simplify(dS_h + dI_h + dH_h + dD_h + dR_h)
print("HCW megmaradási törvénye (0 kell legyen):")
print(Megmaradasi_torveny_h)

# %% 7. Teljes ODE-rendszer
f = sp.Matrix([dS_c, dI_c, dH_c, dD_c, dR_c, dS_h, dI_h, dH_h, dD_h, dR_h])

# A MATLAB-változatban a Dolgozok_aranya, N_w stb. szimbolikus kifejezések, és a numerikus
# értékeket a subs() hozza be a workspace-ből. Itt a numerikus értékek a `num` szótárba
# kerülnek (szimbólum -> érték), és a 9. pontban a .subs(num) helyettesíti be őket.

# %% 8. Numerikus paraméterek (HELYŐRZŐ ÉRTÉKEK, kalibrálandók!)
num = {}
# --- Közös
num[beta] = 1/3         # fertőzési ráta [1/nap]  (R0 = beta/tau_I = 8/3)
num[omega] = 1/180      # immunitás elvesztésének rátája [1/nap]
num[tau_I] = 1/8        # fertőző időszak átlagos hossza 8 nap
num[p_D] = 0.3          # (?) kórházban elhalálozás valószínűsége

# --- Csoportspecifikus
num[tau_H_c] = 1/10     # civilek kórházi tartózkodása ~10 nap
num[tau_H_h] = 1/10     # HCW-k kórházi tartózkodása ~10 nap
num[p_H_c] = 0.25       # (?) civilek kórházba kerülési valószínűsége
num[p_H_h] = 0.1        # (?) HCW-k kórházba kerülési valószínűsége

# Csak Szegedre:
num[N_h] = 10100
num[N_c] = 180000 - num[N_h]

# --- HCW-specifikus
num[theta] = 0.5        # ébrenlét fele a munkahelyen
num[sigma_c] = 0.7      # <1: óvatosabbak a közösségben
num[sigma_w] = 0.3      # PPE hatása a munkahelyen (1 = védtelen) <-------------------(NAGYON LEVITTEM)
num[beta_p] = num[beta] # kiinduló feltevés: a beteg-kontaktus ráta = közösségi
num[beta_s] = num[beta] # kiinduló feltevés: a kolléga-kontaktus ráta = közösségi
num[q_H] = 0.7          # betegek relatív fertőzőképessége (szigetelés esetén < 1) <--(NAGYON LEVITTEM)
num[q_I_h] = 0.1        # fertőző HCW relatív fertőzőképessége munkahelyen
num[c_test] = 0.7       # detektált fertőző HCW-k aránya
num[P_0] = 5e4          # nem-COVID-os betegek száma (ágyszám alapján becsülendő)

# Kórházi ágykapacitás (csak az ábrán jelenik meg, a modellben nincs kapacitáskorlát)
agyak_szama = 1998

# %% 9. Az ODE-függvény létrehozása 
f = f.subs(num)                      # paraméterek behelyettesítése
t = sp.Symbol("t")
_f_lam = sp.lambdify([t, x], f, modules="numpy", cse=True)


def f_ode(t_, x_):
    return np.asarray(_f_lam(t_, x_), dtype=float).ravel()


# A HCW fertőzési erő komponenseinek függvénye (utólagos elemzéshez)
lam_parts = sp.Matrix([(1-theta)*lambda_comm,
                       theta*lambda_pat,
                       theta*lambda_staff]).subs(num)
_lam_lam = sp.lambdify([x], lam_parts, modules="numpy", cse=True)


def lam_fun(x_):
    return np.asarray(_lam_lam(x_), dtype=float).ravel()


# Dolgozók arányának függvénye (utólagos elemzéshez)
_Nw_lam = sp.lambdify([x], Dolgozok_aranya.subs(num), modules="numpy")


def Nw_fun(x_):
    return float(_Nw_lam(x_))


# %% 10. Kezdeti feltételek
I_c_0 = 10          # kezdetben ennyi fertőzött civil
I_h_0 = 0           # kezdetben nincs fertőzött HCW

x0 = np.array([num[N_c] - I_c_0,     # S_c
               I_c_0,                # I_c
               0,                    # H_c
               0,                    # D_c
               0,                    # R_c
               num[N_h] - I_h_0,     # S_h
               I_h_0,                # I_h
               0,                    # H_h
               0,                    # D_h
               0], dtype=float)      # R_h


# %% 11. Szimuláció
def ode45_refined(fun, t_span, y0, refine=4, rtol=1e-3, atol=1e-6):
    """Az ode45 kimenetének megfelelője: a lépéspontok közé (refine-1) interpolált pontot is
    visszaad (az ode45 alapértelmezett Refine értéke 4), az ode45 alapértelmezett tűréseivel."""
    sol = solve_ivp(fun, t_span, y0, method="RK45", rtol=rtol, atol=atol, dense_output=True)
    if not sol.success:
        raise RuntimeError(sol.message)
    steps = sol.t
    frac = np.arange(1, refine) / refine
    inner = (steps[:-1, None] + frac[None, :] * np.diff(steps)[:, None])
    tt = np.concatenate([np.column_stack([steps[:-1, None], inner]).ravel(), steps[-1:]])
    return tt, sol.sol(tt).T


T = round(4/12*365)                          # kb. 4 hónap (122 nap)
tt, xx = ode45_refined(f_ode, (0, T), x0)
datum = pd.Timestamp(2022, 1, 1) + pd.to_timedelta(tt, unit="D")

# %% 12. Utólagos számítások
nt = tt.size
lam = np.zeros((nt, 3))                      # [közösségi, beteg->HCW, HCW->HCW]
dolg_arany = np.zeros(nt)
for k in range(nt):
    lam[k, :] = lam_fun(xx[k, :])
    dolg_arany[k] = Nw_fun(xx[k, :])
lam_ossz = lam.sum(axis=1)

# Kumulált fertőzések a HCW-knél, útvonal szerint (újrafertőzéssel együtt)
S_h_t = xx[:, 5]
fert_ut = np.trapezoid(lam * S_h_t[:, None], tt, axis=0)   # 3 elemű vektor
fert_ossz = fert_ut.sum()

H_ossz = xx[:, 2] + xx[:, 7]


def _datum_str(i):
    return datum[i].strftime("%d-%b-%Y %H:%M:%S")


print("\n=== Eredmények ===")
print(f"Civil fertőzöttek csúcsa: {100*xx[:, 1].max()/num[N_c]:.2f} % ({_datum_str(np.argmax(xx[:, 1]))})")
print(f"HCW fertőzöttek csúcsa:   {100*xx[:, 6].max()/num[N_h]:.2f} % ({_datum_str(np.argmax(xx[:, 6]))})")
print(f"Kumulált HCW-fertőzések:  {fert_ossz:.0f} (a dolgozók {100*fert_ossz/num[N_h]:.1f} %-a)")
print(f"  - közösségből:          {100*fert_ut[0]/fert_ossz:.1f} %")
print(f"  - betegektől:           {100*fert_ut[1]/fert_ossz:.1f} %")
print(f"  - kollégáktól:          {100*fert_ut[2]/fert_ossz:.1f} %")
print(f"Kórházban ápoltak csúcsa: {H_ossz.max():.0f} (ágyszám: {agyak_szama:.0f})")
print(f"Legkisebb dolgozói arány: {100*dolg_arany.min():.1f} %")

# %% 13. Ábrák
fig, axs = plt.subplots(2, 2, figsize=(10, 7.5), layout="constrained", num="SIHDR HCW modell")

# (1) Fertőzöttek aránya a csoportjukon belül
ax = axs[0, 0]
ax.plot(datum, xx[:, 1]/num[N_c], datum, xx[:, 6]/num[N_h], linewidth=2)
ax.legend(["Civilek", "HCW-k"], loc="best")
ax.set_title("Fertőzöttek aránya (I / N)"); ax.set_ylabel("arány"); ax.grid(True)

# (2) HCW fertőzési erő komponensei
ax = axs[0, 1]
ax.stackplot(datum, lam.T, linewidth=0,
             labels=["Közösség", r"Beteg $\rightarrow$ HCW", r"HCW $\rightarrow$ HCW"])
ax.legend(loc="best")
ax.set_title(r"HCW fertőzési erő komponensei ($\lambda_h$)"); ax.set_ylabel("1/nap"); ax.grid(True)

# (3) Kórházban ápoltak vs. ágykapacitás
ax = axs[1, 0]
ax.plot(datum, H_ossz, linewidth=2)
ax.axhline(agyak_szama, color="r", linestyle="--", linewidth=1.5)
ax.text(1, agyak_szama, "Ágykapacitás", color="r", ha="right", va="bottom",
        transform=ax.get_yaxis_transform())
ax.set_title("Kórházban ápoltak ($H_c + H_h$)"); ax.set_ylabel("fő"); ax.grid(True)

# (4) Dolgozói arány
ax = axs[1, 1]
ax.plot(datum, dolg_arany, linewidth=2)
ax.set_ylim(0, 1.05)
ax.set_title("Munkában lévő HCW-k aránya"); ax.set_ylabel("arány"); ax.grid(True)

for ax in axs.flat:
    ax.tick_params(axis="x", labelrotation=30)

fig.suptitle("SIHDR modell civilekkel és egészségügyi dolgozókkal")
plt.show()
