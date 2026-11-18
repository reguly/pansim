%% SIHDR járványmodell civilekre és egészségügyi dolgozókra (HCW) - a panSim alapesetére kalibrálva
% =========================================================================
% Ez a szkript a SIHDR_HCW_v3.m modelljét futtatja a panSim ágensalapú modell alapesetére
% (Szeged, 2020-09-23-tól 364 nap, 20 futás átlaga) illesztett paraméterekkel ("A" illesztés).
% Az illesztést a kalibracio.py végezte (Python, scipy least_squares); itt csak a kapott
% értékek szerepelnek, a szkript illesztést nem végez.
%
% A v3-mal ellentétben nem használ szimbolikus számítást: az egyenletek a fájl végén lévő
% jobb_oldal() függvényben vannak, ugyanabban a sorrendben és jelöléssel, mint a v3-ban.
% Így az alap MATLAB-bal is fut, a Symbolic Math Toolbox nem kell.
%
% Kompartmentek (mindkét csoportra, _c = civil, _h = egészségügyi dolgozó):
%   S - fogékony
%   I - fertőző (nem kórházban)
%   H - kórházban ápolt
%   D - elhunyt
%   R - védett (gyógyult vagy beoltott; a védettség omega rátával csökken -> vissza S-be)
%
% Ami a v3-hoz képest változott (a v3 egyenletei egyébként változatlanok):
%   1) c(t): a közösségi kontaktusok időfüggő szorzója. A zárásokat, iskolabezárásokat,
%      kijárási tilalmat (és minden mást, amit a modell külön nem ír le, pl. szezonalitás)
%      foglalja össze. 21 naponként egy illesztett csomópont, köztük lineáris.
%      Csak a közösségi fertőzési erőkre hat, a kórházi tagokra nem.
%   2) v(t): a variánsok fertőzőképességi szorzója, a panSim variánsarányaiból
%      (alfa 1,85/0,98-szoros, delta 2,05/0,98-szoros, mint a panSim-ben). Minden
%      fertőzési erőre hat.
%   3) Oltás: S -> R áram. A t napon a tau_v = 14 nappal korábban beadott adagok e_v része
%      válik hatásossá. A HCW-k kapják az első 0,9*N_h adagot (mint a panSim-ben).
%   4) Karanténban lévő, nem fertőzött HCW-k (Q_h): kiesnek a munkából. A beoltott HCW-k
%      mentesek a kontaktkarantén alól (mint a panSim-ben).
%   5) A v3 HCW-fertőzési szorzói (theta, sigma_c, sigma_w, beta_p, beta_s, q_H, q_I_h) csak
%      szorzatként hatnak, ezért három, külön értelmezhető paraméterbe vannak összevonva:
%        rho_c   = (1-theta)*sigma_c          HCW közösségi fertőződése a civilekéhez képest
%        beta_PH = theta*sigma_w*beta_p*q_H   napi fertőződés betegtől, ha minden ágy COVID-os
%        beta_HH = theta*sigma_w*beta_s*q_I_h napi fertőződés kollégától, ha mind fertőző
%   6) Négy számláló (C_civ, C_comm, C_pat, C_staff) összesíti a fertőzéseket forrás szerint.
%      Ezek a dinamikára nem hatnak.
%
% Futtatás: ugyanebben a mappában legyen a SIHDR_HCW_A_bemenetek.csv fájl. Ebben vannak a
% panSim alapeset napi bemenetei (variánsarányok, oltások) és az összevetéshez használt
% panSim-görbék (20 futás átlaga).
%
% Várt eredmény (a Python-implementációval egyezően): kórházi csúcs ~200 fő, kumulált
% HCW-fertőzés ~4360 (70 % közösségből, 28 % betegtől, 2 % kollégától), HCW / civil
% incidencia-arány ~1,45, HCI-csúcs ~5,35 %, kumulált halálozás a 0. naptól ~553 fő.
%
% Megjegyzés: a fájl UTF-8 kódolású (ékezetes kommentek miatt).
% =========================================================================

clear; clc; close all;

%% 1. Numerikus paraméterek - az "A" illesztés eredménye (panSim alapeset)
% Jelölés: [illesztett] = kalibracio.py illesztette; [panSim] = a panSim beállításaiból
% rögzített; [v3] = a SIHDR_HCW_v3.m értéke változatlanul.

% --- Közös
p.beta    = 1/3;          % [v3]      alap fertőzési ráta [1/nap]; a tényleges ráta beta*c(t)*v(t)
p.omega   = 1/1000;       % [panSim]  védettség elvesztése [1/nap] (v3: 1/180). A panSim-ben a
                          %           fertőzés utáni védettség 85 %, hetente csak 0,3 %-kal csökken.
p.tau_I   = 1/8;          % [v3]      fertőző időszak átlagos hossza 8 nap
p.p_D     = 0.211639;     % [illesztett] kórházban elhalálozás valószínűsége (v3: 0,3)

% --- Csoportspecifikus
p.tau_H_c = 1/10;         % [panSim]  kórházi tartózkodás 10 nap (panSim I5_h/I6_h; = v3)
p.tau_H_h = 1/10;         % [panSim]  ugyanez HCW-kre
p.p_H_c   = 0.0467006;    % [illesztett] civilek kórházba kerülési valószínűsége (v3: 0,25)
p.p_H_h   = p.p_H_c;      % [panSim]  a panSim nem különbözteti meg a HCW-k kórházba kerülését (v3: 0,1)

% A panSim populációja (agents1.json): 178 746 fő, ebből 10 136 egészségügyi dolgozó
% (kórházi és rendelői munkahely).
p.N_h = 10136;
p.N_c = 178746 - p.N_h;

% --- HCW-specifikus (összevont paraméterek)
p.rho_c   = 1.47455;      % [illesztett] a HCW-k közösségi fertőződése a civilekének 1,47-szerese
                          %           (v3: (1-theta)*sigma_c = 0,5*0,7 = 0,35)
p.beta_PH = 0.00499235;   % [illesztett] beteg -> HCW [1/nap]. 150 COVID- és 609 egyéb beteg mellett
                          %           egy fogékony HCW napi fertőződési esélye kb. 0,1 %
                          %           (v3: theta*sigma_w*beta_p*q_H = 0,035)
p.beta_HH = 0.005;        % [v3]      HCW -> HCW [1/nap] (theta*sigma_w*beta_s*q_I_h = 0,5*0,3*(1/3)*0,1)
p.c_test  = 0.35;         % [panSim]  a panSim-ben a pozitív tesztek / új fertőzések aránya kb. 0,33 (v3: 0,7)
p.P_0     = 609.361;      % [panSim]  a panSim nem-COVID kórházi betegeinek átlaga (v3: 50 000)

% --- Karantén és oltás
p.kappa_comm = 2.06593;   % [illesztett] közösségi kontaktkarantén (a panSim HCI-jéből)
p.kappa_work = 0;         % [panSim]  a panSim a kórházat nem zárja munkahelyi karanténba
p.e_v     = 0.77;         % [panSim]  oltás hatékonysága fertőzés ellen (protectionInfection, 2 adag)
p.tau_v   = 14;           % [panSim]  az oltás hatásának késése [nap]: a panSim-ben az első adag után
                          %           1 hétig nincs védelem, 1-4 hét között fél védelem

%% 2. A kontaktusszorzó, c(t) [illesztett]
% 21 naponként egy csomópont (0., 21., ..., 378. nap), köztük lineáris interpoláció.
c_csomopont_nap = (0:21:378).';
c_csomopont     = [0.464482 0.483233 0.461728 0.380751 0.341885 0.351118 0.387430 ...
                   0.391417 0.322654 0.257951 0.216686 0.178405 0.147712 0.122734 ...
                   0.102247 0.0853534 0.0713582 0.0597171 0.05].';
% Ősszel 0,46-0,48; a 2020. novemberi korlátozások után 0,34-0,35; februárban 0,39;
% tavasztól folyamatosan csökken. A nyári értékeket az adat alig határozza meg (kevés eset,
% a modellben nincs behurcolás), ezért ott a c(t) az alsó korlátra (0,05) fut.

%% 3. Időfüggő bemenetek a panSim alapesetből
% SIHDR_HCW_A_bemenetek.csv oszlopai (napi értékek, 20 futás átlaga):
%   nap, alfa_arany, delta_arany   - a variánsok aránya a fertőzöttek között (panSim MUT)
%   oltas_napi                     - napi oltásszám (panSim VAC)
%   panSim_*                       - összevetéshez: kórházi ápoltak, új civil fertőzések,
%                                    új HCW-fertőzések (HCE), HCI (%), kumulált halálozás
adat = readtable('SIHDR_HCW_A_bemenetek.csv');
nap  = adat.nap;

% Variánsszorzó (a panSim fertőzőképességi szorzói, a vad típus 0,98-hoz viszonyítva)
v_napi = 1 + (1.85/0.98 - 1)*adat.alfa_arany + (2.05/0.98 - 1)*adat.delta_arany;

% Oltások: az első 0,9*N_h adag a HCW-ké, a többi a civileké
oltas      = adat.oltas_napi;
u_h        = diff([0; min(cumsum(oltas), 0.9*p.N_h)]);
u_c        = max(oltas - u_h, 0);
beoltott_h = min(cumsum(u_h)/p.N_h, 1);  % a beoltott HCW-k aránya (az első adagtól mentesek a karantén alól)

bem = struct('nap', nap, 'v', v_napi, 'u_c', u_c, 'u_h', u_h, 'beoltott_h', beoltott_h, ...
             'c_nap', c_csomopont_nap, 'c', c_csomopont, 'tau_v', p.tau_v);

%% 4. Kezdeti feltételek (a panSim alapeset 0. napja, 2020-09-23)
% A kezdeti fertőzöttek (E+I1..I4 = 372) a létszám arányában oszlanak meg a két csoport között;
% a kórházban ápoltak, gyógyultak és elhunytak a civilekhez kerülnek.
I_0 = 372.15;   H_0 = 9.9;   R_0 = 248.9;   D_0 = 1.15;
arany_h = p.N_h/(p.N_c + p.N_h);

x0 = [ p.N_c - I_0*(1-arany_h) - H_0 - R_0 - D_0   % S_c
       I_0*(1-arany_h)                             % I_c
       H_0                                         % H_c
       D_0                                         % D_c
       R_0                                         % R_c
       p.N_h - I_0*arany_h                         % S_h
       I_0*arany_h                                 % I_h
       0                                           % H_h
       0                                           % D_h
       0                                           % R_h
       0; 0; 0; 0 ];                               % számlálók: C_civ, C_comm, C_pat, C_staff

%% 5. Ellenőrzés: megmaradási törvény
% A két csoport létszáma nem változhat: a kompartmentek deriváltjainak összege 0 (az oltás
% S -> R áram, nem változtat a létszámon). Egy tetszőleges időpontban ellenőrizzük.
dx_proba = jobb_oldal(100, x0, p, bem);
fprintf('Civilek megmaradási törvénye (0 kell legyen): %.2e\n', sum(dx_proba(1:5)));
fprintf('HCW megmaradási törvénye (0 kell legyen):     %.2e\n', sum(dx_proba(6:10)));

%% 6. Szimuláció
T = 363;                                          % 364 nap, mint a panSim alapeset
opciok = odeset('RelTol', 1e-6, 'AbsTol', 1e-6, 'MaxStep', 1);
[tt, xx] = ode45(@(t, y) jobb_oldal(t, y, p, bem), 0:T, x0, opciok);
datum = datetime(2020, 9, 23) + days(tt);

%% 7. Utólagos számítások
nt   = numel(tt);
lam  = zeros(nt, 3);                              % [közösségi, beteg->HCW, HCW->HCW]
Qh   = zeros(nt, 1);
dolg_arany = zeros(nt, 1);
for k = 1:nt
    [~, lam(k, :), Qh(k), dolg_arany(k)] = jobb_oldal(tt(k), xx(k, :).', p, bem);
end

N_h = p.N_h;  N_c = p.N_c;
H_ossz   = xx(:, 3) + xx(:, 8);                   % kórházban ápoltak
halott   = xx(:, 4) + xx(:, 9) - x0(4);           % kumulált halálozás a 0. naptól
HCI      = 100*(xx(:, 7) + xx(:, 8) + Qh)/N_h;    % panSim HCI megfelelője: fertőzött VAGY karanténban
kieso    = 100*(p.c_test*xx(:, 7) + xx(:, 8) + Qh)/N_h;  % ténylegesen kieső dolgozók
fert_ut  = xx(end, 12:14);                        % kumulált HCW-fertőzés útvonalanként
fert_ossz = sum(fert_ut);
fert_civ  = xx(end, 11);
uj_civil  = [NaN; diff(xx(:, 11))];               % napi új civil fertőzések
uj_hcw    = [NaN; diff(sum(xx(:, 12:14), 2))];    % napi új HCW-fertőzések
RR        = (fert_ossz/N_h)/(fert_civ/N_c);       % HCW / civil incidencia-arány

[~, i_h]  = max(H_ossz);
[~, i_q]  = max(HCI);
fprintf('\n=== Eredmények (A illesztés, panSim alapeset) ===\n');
fprintf('Kórházban ápoltak csúcsa:  %.0f fő (%s)\n', H_ossz(i_h), string(datum(i_h)));
fprintf('Kumulált civil fertőzés:   %.0f (a civilek %.1f %%-a)\n', fert_civ, 100*fert_civ/N_c);
fprintf('Kumulált HCW-fertőzés:     %.0f (a dolgozók %.1f %%-a)\n', fert_ossz, 100*fert_ossz/N_h);
fprintf('  - közösségből:           %.1f %%\n', 100*fert_ut(1)/fert_ossz);
fprintf('  - betegektől:            %.1f %%\n', 100*fert_ut(2)/fert_ossz);
fprintf('  - kollégáktól:           %.1f %%\n', 100*fert_ut(3)/fert_ossz);
fprintf('HCW / civil incidencia-RR: %.2f\n', RR);
fprintf('HCI csúcsa:                %.2f %% (%s)\n', HCI(i_q), string(datum(i_q)));
fprintf('Kieső dolgozók csúcsa:     %.2f %%\n', max(kieso));
fprintf('Kumulált halálozás:        %.0f fő\n', halott(end));
fprintf('Legkisebb dolgozói arány:  %.1f %%\n', 100*min(dolg_arany));

% Összevetés a panSim alapesettel (korreláció; a napi zajos sorok 7 napos átlaggal)
panSim_HCE   = movmean(adat.panSim_HCE, 7);
panSim_civil = movmean(adat.panSim_uj_civil, 7);
HCI_csonkolt = max(HCI - 0.5, 0);                 % a panSim HCI-je futásonként egészre csonkolt
fprintf('\nIlleszkedés a panSim-hez (korreláció):\n');
fprintf('  kórházi ápoltak:  r = %.3f\n', korrelacio(H_ossz, adat.panSim_korhazi_apolt));
fprintf('  új civil fert.:   r = %.3f\n', korrelacio(uj_civil, panSim_civil));
fprintf('  új HCW-fert.:     r = %.3f\n', korrelacio(uj_hcw, panSim_HCE));
fprintf('  HCI:              r = %.3f\n', korrelacio(HCI_csonkolt, adat.panSim_HCI));
fprintf('  kum. halálozás:   r = %.3f\n', korrelacio(halott, adat.panSim_halott_kum));

%% 8. Ábrák - a modell belső működése (mint a v3-ban)
figure('Name', 'SIHDR HCW modell - A illesztés', 'Position', [100 100 1000 750]);
tl = tiledlayout(2, 2, 'TileSpacing', 'compact', 'Padding', 'compact');

% (1) Fertőzöttek aránya a csoportjukon belül
nexttile
plot(datum, xx(:, 2)/N_c, datum, xx(:, 7)/N_h, 'LineWidth', 2)
legend('Civilek', 'HCW-k', 'Location', 'best')
title('Fertőzöttek aránya (I / N)'); ylabel('arány'); grid on

% (2) HCW fertőzési erő komponensei
nexttile
area(datum, lam, 'LineStyle', 'none')
legend('Közösség', 'Beteg \rightarrow HCW', 'HCW \rightarrow HCW', 'Location', 'best')
title('HCW fertőzési erő komponensei (\lambda_h)'); ylabel('1/nap'); grid on

% (3) HCW-k állapota: fertőzött vagy karanténban (HCI) és ténylegesen kieső
nexttile
plot(datum, HCI, datum, kieso, datum, 100*Qh/N_h, 'LineWidth', 2)
legend('HCI: fertőzött vagy karanténban', 'Kieső (detektált + kórház + karantén)', ...
       'Karanténban, nem fertőzött (Q_h)', 'Location', 'best')
title('Egészségügyi dolgozók'); ylabel('a dolgozók %-a'); grid on

% (4) Dolgozói arány
nexttile
plot(datum, dolg_arany, 'LineWidth', 2)
ylim([0.9 1.005])
title('Munkában lévő HCW-k aránya'); ylabel('arány'); grid on

title(tl, 'SIHDR modell civilekkel és egészségügyi dolgozókkal - a panSim alapesetére kalibrálva');

%% 9. Ábrák - összevetés a panSim alapesettel
szin_panSim = [0.16 0.47 0.84];
szin_ODE    = [0.91 0.44 0.04];

figure('Name', 'Összevetés a panSim-mel', 'Position', [150 50 1100 850]);
tl2 = tiledlayout(3, 2, 'TileSpacing', 'compact', 'Padding', 'compact');

nexttile
plot(datum, adat.panSim_korhazi_apolt, 'Color', szin_panSim, 'LineWidth', 2); hold on
plot(datum, H_ossz, '--', 'Color', szin_ODE, 'LineWidth', 2)
legend('panSim', 'ODE', 'Location', 'best')
title('Kórházban ápoltak (H_c + H_h)'); ylabel('fő'); grid on

nexttile
plot(datum, panSim_civil, 'Color', szin_panSim, 'LineWidth', 2); hold on
plot(datum, uj_civil, '--', 'Color', szin_ODE, 'LineWidth', 2)
legend('panSim (7 napos átlag)', 'ODE', 'Location', 'best')
title('Új fertőzések, nem HCW'); ylabel('fő/nap'); grid on

nexttile
plot(datum, panSim_HCE, 'Color', szin_panSim, 'LineWidth', 2); hold on
plot(datum, uj_hcw, '--', 'Color', szin_ODE, 'LineWidth', 2)
legend('panSim (7 napos átlag)', 'ODE', 'Location', 'best')
title('Új HCW-fertőzések (HCE)'); ylabel('fő/nap'); grid on

nexttile
plot(datum, adat.panSim_HCI, 'Color', szin_panSim, 'LineWidth', 2); hold on
plot(datum, HCI_csonkolt, '--', 'Color', szin_ODE, 'LineWidth', 2)
plot(datum, HCI, ':', 'Color', szin_ODE, 'LineWidth', 1)
legend('panSim HCI', 'ODE, csonkolva', 'ODE, csonkolás nélkül', 'Location', 'best')
title('HCI: fertőzött vagy karanténban lévő HCW-k'); ylabel('%'); grid on

nexttile
plot(datum, adat.panSim_halott_kum, 'Color', szin_panSim, 'LineWidth', 2); hold on
plot(datum, halott, '--', 'Color', szin_ODE, 'LineWidth', 2)
legend('panSim', 'ODE', 'Location', 'best')
title('Kumulált COVID-halálozás a 0. naptól'); ylabel('fő'); grid on

nexttile
c_napi = interp1(c_csomopont_nap, c_csomopont, tt);
yyaxis left
plot(datum, c_napi, 'LineWidth', 2); ylabel('c(t)')
yyaxis right
plot(datum, v_napi(1:nt), 'LineWidth', 2); ylabel('v(t)')
title('Kontaktusszorzó c(t) (illesztett) és variánsszorzó v(t)'); grid on

title(tl2, 'ODE (A illesztés) és a panSim alapeset (20 futás átlaga)');

%% A modell egyenletei
function [dx, lam, Q_h, Dolgozok_aranya] = jobb_oldal(t, x, p, bem)
% Az ODE jobb oldala a t időpontban. A jelölések a SIHDR_HCW_v3.m-éi.
% Kimenet: dx a 14 derivált (10 kompartment + 4 számláló); utólagos elemzéshez a HCW
% fertőzési erő komponensei, a karanténban lévő HCW-k száma és a dolgozói arány.

    % Állapotváltozók
    % (x(4) = D_c a jobb oldalon nem szerepel; az elhunyt HCW-k, D_h viszont kiesnek a munkából)
    S_c = x(1);  I_c = x(2);  H_c = x(3);                R_c = x(5);
    S_h = x(6);  I_h = x(7);  H_h = x(8);  D_h = x(9);  R_h = x(10);

    % Időfüggő bemenetek: kontaktusszorzó, variánsszorzó, tau_v nappal korábbi adagok,
    % a még nem beoltott (karanténba küldhető) HCW-k aránya
    [c, v, uc, uh, mentes] = bemenetek(t, bem);

    % Összegzett mennyiségek
    I = I_c + I_h;                   % összes közösségi fertőző
    H = H_c + H_h;                   % összes kórházban ápolt
    N = p.N_c + p.N_h;               % teljes populáció

    % --- Kieső és dolgozó HCW-k
    % Karanténban lévő, nem fertőzött HCW-k (algebrai mennyiség, nem állapotváltozó):
    %   háztartási/közösségi kontaktus miatt a populációs prevalencia (I/N) arányában,
    %   munkahelyi kontaktus miatt a detektált fertőzött kollégák arányában (a panSim-ben 0)
    Q_h = (p.kappa_comm*p.N_h*I/N + p.kappa_work*p.c_test*I_h)*mentes;
    % Nem dolgozik: a detektált fertőzöttek, a kórházban ápolt és az elhunyt dolgozók,
    % valamint a karanténban lévők
    Kieso_dolgozok_szama = p.c_test*I_h + H_h + D_h + Q_h;
    N_w             = p.N_h - Kieso_dolgozok_szama;   % ténylegesen munkában lévők
    Dolgozok_aranya = N_w/p.N_h;

    % --- Fertőzési erők
    b = p.beta*v*c;                  % közösségi fertőzési ráta: kontaktusok (c) és variánsok (v)
    lambda_c     = b*I/N;            % civilek: tisztán közösségi fertőzés
    lambda_comm  = p.rho_c*b*I/N;    % HCW (a) közösség: a civilekéhez képest rho_c-szeres
    lambda_pat   = p.beta_PH*v*H/(H + p.P_0);             % HCW (b) beteg -> HCW
    lambda_staff = p.beta_HH*v*(1 - p.c_test)*I_h/N_w;    % HCW (c) HCW -> HCW, nem detektált fertőzők
    lambda_h     = lambda_comm + lambda_pat + lambda_staff;

    % --- Oltás: a tau_v nappal korábban beadott adagok a még nem fertőzött (S + R) csoport
    % között oszlanak meg; az S-be jutó adagok e_v része kerül R-be
    V_c = p.e_v*uc*S_c/(S_c + R_c);
    V_h = p.e_v*uh*S_h/(S_h + R_h);

    % --- Civilek dinamikája
    dS_c = -lambda_c*S_c + p.omega*R_c - V_c;
    dI_c =  lambda_c*S_c - p.tau_I*I_c;
    dH_c = p.p_H_c*p.tau_I*I_c - p.tau_H_c*H_c/Dolgozok_aranya;
    dD_c = p.p_D*p.tau_H_c*H_c/Dolgozok_aranya^2;
    dR_c = (1-p.p_H_c)*p.tau_I*I_c + (1-p.p_D/Dolgozok_aranya)*p.tau_H_c*H_c/Dolgozok_aranya ...
           - p.omega*R_c + V_c;

    % --- HCW-k dinamikája
    dS_h = -lambda_h*S_h + p.omega*R_h - V_h;
    dI_h =  lambda_h*S_h - p.tau_I*I_h;
    dH_h = p.p_H_h*p.tau_I*I_h - p.tau_H_h*H_h/Dolgozok_aranya;
    dD_h = p.p_D*p.tau_H_h*H_h/Dolgozok_aranya^2;
    dR_h = (1-p.p_H_h)*p.tau_I*I_h + (1-p.p_D/Dolgozok_aranya)*p.tau_H_h*H_h/Dolgozok_aranya ...
           - p.omega*R_h + V_h;

    % --- Kumulált fertőzések: civil; HCW közösségből / betegtől / kollégától
    dx = [dS_c; dI_c; dH_c; dD_c; dR_c; dS_h; dI_h; dH_h; dD_h; dR_h; ...
          lambda_c*S_c; lambda_comm*S_h; lambda_pat*S_h; lambda_staff*S_h];
    lam = [lambda_comm, lambda_pat, lambda_staff];
end

%% Segédfüggvények
function [c, v, uc, uh, mentes] = bemenetek(t, bem)
% Az időfüggő bemenetek a t időpontban (lineáris interpolációval a napi értékek között).
    t  = min(max(t, bem.nap(1)), bem.nap(end));
    c  = interp1(bem.c_nap, bem.c, t);
    v  = interp1(bem.nap, bem.v, t);
    ts = t - bem.tau_v;                    % az oltás tau_v nap késéssel hat
    if ts < 0
        uc = 0; uh = 0;
    else
        uc = interp1(bem.nap, bem.u_c, ts);
        uh = interp1(bem.nap, bem.u_h, ts);
    end
    mentes = 1 - interp1(bem.nap, bem.beoltott_h, t);
end

function r = korrelacio(a, b)
% Pearson-korreláció, a hiányzó (NaN) értékek kihagyásával.
    ok = ~isnan(a) & ~isnan(b);
    cc = corrcoef(a(ok), b(ok));
    r  = cc(1, 2);
end
