%% SIHDR járványmodell civilekre és egészségügyi dolgozókra (HCW)
% =========================================================================
% Kompartmentek (mindkét csoportra, _c = civil, _h = egészségügyi dolgozó):
%   S - fogékony
%   I - fertőző (nem kórházban)
%   H - kórházban ápolt
%   D - elhunyt
%   R - felgyógyult (az immunitás omega rátával csökken -> vissza S-be)
%
% Fő modellezési gondolatok:
%   1) A HCW-k fertőzési ereje két "univerzumból" áll, az ébrenléti idő
%      theta, illetve (1-theta) arányában:
%        - közösség: a teljes populációval normalizálva, a HCW-k
%          fogékonysága sigma_c (< 1: óvatosabbak a hétköznapokban)
%        - kórház: (a) beteg -> HCW kontaktus, a COVID-os betegek
%          arányával (H / (H + P_0)) normalizálva,
%                   (b) HCW -> HCW kontaktus, a ténylegesen dolgozók
%          számával normalizálva
%   2) A kieső dolgozók (detektált fertőzöttek + kórházban lévők + elhunytak)
%      csökkentik a munkaerőt, ami rontja a kórházi ellátást: a kórházi
%      kimenet (gyógyulás/halál) lassul a Dolgozok_aranya-val arányosan.
%
% Megjegyzés: a fájl UTF-8 kódolású (ékezetes kommentek miatt).
% =========================================================================

clear; clc; close all;

%% 1. Szimbolikus állapotváltozók
% A "real" feltevés egyszerűsíti a szimbolikus kifejezéseket.
syms S_c I_c H_c D_c R_c real
syms S_h I_h H_h D_h R_h real

xc = [S_c I_c H_c D_c R_c];     % civilek kompartmentjei
xh = [S_h I_h H_h D_h R_h];     % HCW-k kompartmentjei
x  = [xc xh].';                 % teljes állapotvektor (10x1 oszlop)

%% 2. Szimbolikus paraméterek
% Közös paraméterek
syms beta omega tau_I p_D                 % beta: kontaktrátából eredő fertőzési ráta
                                          % (megj.: felülírja a beta() beépített függvényt)
% Csoportspecifikus paraméterek
syms tau_H_c tau_H_h p_H_c p_H_h          % kórházi tartózkodás ill. kórházba kerülés valószínűsége
% Populációméretek
syms N_c N_h
% HCW-specifikus paraméterek
syms theta        % munkahelyi időarány az ébrenlétből (0.5 = fele)
syms sigma_c      % HCW fogékonysága a közösségben (régi beta_rel_h)
syms sigma_w      % HCW fogékonysága a munkahelyen (védőfelszerelés hatása; 1 = védtelen)
syms beta_p       % HCW-beteg kontaktusból eredő fertőzési ráta
syms beta_s       % HCW-HCW kontaktusból eredő fertőzési ráta
syms q_H          % kórházi betegek relatív fertőzőképessége
syms q_I_h        % fertőző HCW relatív fertőzőképessége a munkahelyen
syms c_test       % a fertőző HCW-k detektált (és otthon maradó) hányada
syms P_0          % nem-COVID-os betegek száma a kórházakban

% Összegzett mennyiségek
I = I_c + I_h;            % összes közösségi fertőző
H = H_c + H_h;            % összes kórházban ápolt
N = N_c + N_h;            % teljes populáció

%% 3. Kieső és dolgozó HCW-k
% Nem dolgozik: a detektált fertőzöttek (otthon izolálnak), a kórházban
% ápolt, valamint az elhunyt dolgozók.
Kieso_dolgozok_szama = c_test*I_h + H_h + D_h;

% Ténylegesen munkában lévő dolgozók száma és aránya
N_w             = N_h - Kieso_dolgozok_szama;
Dolgozok_aranya = N_w / N_h;

%% 4. Fertőzési erők
% --- Civilek: tisztán közösségi fertőzés, a teljes populációval normalizálva
lambda_c = beta*I/N;

% --- HCW-k: három komponens
% (a) közösségi tag: sigma_c-vel csökkentett fogékonyság
lambda_comm  = sigma_c*beta*I/N;

% (b) kórházi beteg -> HCW: a HCW adott számú beteggel találkozik, amelyek
%     közül H/(H+P_0) a COVID-os. A kórházi dolgozók H_h tagjai is betegként
%     szerepelnek a H-ban (a dolgozói létszámból is kiesnek, lásd 3. pont).
lambda_pat   = sigma_w*beta_p*q_H*H/(H + P_0);

% (c) kórházi HCW -> HCW: a nem detektált fertőző dolgozók, q_I_h relatív
%     fertőzőképességgel, a munkában lévő létszámmal normalizálva.
lambda_staff = sigma_w*beta_s*q_I_h*(1-c_test)*I_h/N_w;

% A HCW eredő fertőzési ereje: időarányosan súlyozva
lambda_h = (1-theta)*lambda_comm + theta*(lambda_pat + lambda_staff);

%% 5. Civilek dinamikája
dS_c = -lambda_c*S_c + omega*R_c;
dI_c =  lambda_c*S_c - tau_I*I_c;
dH_c = p_H_c*tau_I*I_c - tau_H_c*H_c/Dolgozok_aranya;
dD_c = p_D*tau_H_c*H_c/Dolgozok_aranya^2;
dR_c = (1-p_H_c)*tau_I*I_c + (1-p_D/Dolgozok_aranya)*tau_H_c*H_c/Dolgozok_aranya - omega*R_c;

% Ellenőrzés: a civilek száma nem változhat.
Megmaradasi_torveny_c = simplify(dS_c + dI_c + dH_c + dD_c + dR_c);
disp('Civilek megmaradási törvénye (0 kell legyen):'); disp(Megmaradasi_torveny_c)

%% 6. HCW-k dinamikája
dS_h = -lambda_h*S_h + omega*R_h;
dI_h =  lambda_h*S_h - tau_I*I_h;
dH_h = p_H_h*tau_I*I_h - tau_H_h*H_h/Dolgozok_aranya;
dD_h = p_D*tau_H_h*H_h/Dolgozok_aranya^2;
dR_h = (1-p_H_h)*tau_I*I_h + (1-p_D/Dolgozok_aranya)*tau_H_h*H_h/Dolgozok_aranya - omega*R_h;

% Ellenőrzés: a HCW-k száma nem változhat.
Megmaradasi_torveny_h = simplify(dS_h + dI_h + dH_h + dD_h + dR_h);
disp('HCW megmaradási törvénye (0 kell legyen):'); disp(Megmaradasi_torveny_h)

%% 7. Teljes ODE-rendszer
f = [dS_c; dI_c; dH_c; dD_c; dR_c; dS_h; dI_h; dH_h; dD_h; dR_h];

% Az alábbi két sor sorrendje fontos: a Dolgozok_aranya, N_w stb. szimbolikus
% kifejezések, ezért a numerikus értékeket a subs() hozza be a workspace-ből.

%% 8. Numerikus paraméterek (HELYŐRZŐ ÉRTÉKEK, kalibrálandók!)
% --- Közös
beta    = 1/3;       % fertőzési ráta [1/nap]  (R0 = beta/tau_I = 8/3)
omega   = 1/180;     % immunitás elvesztésének rátája [1/nap]
tau_I   = 1/8;       % fertőző időszak átlagos hossza 8 nap
p_D     = 0.3;       % (?) kórházban elhalálozás valószínűsége

% --- Csoportspecifikus
tau_H_c = 1/10;      % civilek kórházi tartózkodása ~10 nap
tau_H_h = 1/10;      % HCW-k kórházi tartózkodása ~10 nap
p_H_c   = 0.25;      % (?) civilek kórházba kerülési valószínűsége
p_H_h   = 0.1;       % (?) HCW-k kórházba kerülési valószínűsége

% Csak Szegedre:
N_h = 10100;
N_c = 180000 - N_h;

% --- HCW-specifikus
theta   = 0.5;       % ébrenlét fele a munkahelyen
sigma_c = 0.7;       % <1: óvatosabbak a közösségben
sigma_w = 0.3;       % PPE hatása a munkahelyen (1 = védtelen) <-------------------(NAGYON LEVITTEM)
beta_p  = beta;      % kiinduló feltevés: a beteg-kontaktus ráta = közösségi
beta_s  = beta;      % kiinduló feltevés: a kolléga-kontaktus ráta = közösségi
q_H     = 0.7;       % betegek relatív fertőzőképessége (szigetelés esetén < 1) <--(NAGYON LEVITTEM)
q_I_h   = 0.1;       % fertőző HCW relatív fertőzőképessége munkahelyen
c_test  = 0.7;       % detektált fertőző HCW-k aránya
P_0     = 5e4;       % nem-COVID-os betegek száma (ágyszám alapján becsülendő)

% Kórházi ágykapacitás (csak az ábrán jelenik meg, a modellben nincs kapacitáskorlát)
agyak_szama = 1000;

%% 9. Az ODE-függvény létrehozása
f   = subs(f);                       % paraméterek behelyettesítése
t   = sym('t');
f_ode = matlabFunction(f, 'vars', {t, x});

% A HCW fertőzési erő komponenseinek függvénye (utólagos elemzéshez)
lam_parts = subs([(1-theta)*lambda_comm; ...
                  theta*lambda_pat;      ...
                  theta*lambda_staff]);
lam_fun   = matlabFunction(lam_parts, 'vars', {x});

% Dolgozók arányának függvénye (utólagos elemzéshez)
Nw_fun = matlabFunction(subs(Dolgozok_aranya), 'vars', {x});

%% 10. Kezdeti feltételek
I_c_0 = 10;          % kezdetben ennyi fertőzött civil
I_h_0 = 0;           % kezdetben nincs fertőzött HCW

x0 = [ N_c - I_c_0     % S_c
       I_c_0           % I_c
       0               % H_c
       0               % D_c
       0               % R_c
       N_h - I_h_0     % S_h
       I_h_0           % I_h
       0               % H_h
       0               % D_h
       0 ];            % R_h

%% 11. Szimuláció
T = round(4/12*365);                          % kb. 4 hónap (122 nap)
[tt, xx] = ode45(f_ode, [0 T], x0);
datum = tt + datetime(2022,1,1);

%% 12. Utólagos számítások
nt = numel(tt);
lam = zeros(nt, 3);                          % [közösségi, beteg->HCW, HCW->HCW]
dolg_arany = zeros(nt, 1);
for k = 1:nt
    lam(k,:)      = lam_fun(xx(k,:).').';
    dolg_arany(k) = Nw_fun(xx(k,:).');
end
lam_ossz = sum(lam, 2);

% Kumulált fertőzések a HCW-knél, útvonal szerint (újrafertőzéssel együtt)
S_h_t   = xx(:,6);
fert_ut = trapz(tt, lam .* S_h_t);           % 1x3 vektor
fert_ossz = sum(fert_ut);

H_ossz = xx(:,3) + xx(:,8);

fprintf('\n=== Eredmények ===\n');
fprintf('Civil fertőzöttek csúcsa: %.2f %% (%s)\n', ...
    100*max(xx(:,2))/N_c, string(datum(find(xx(:,2)==max(xx(:,2)),1))));
fprintf('HCW fertőzöttek csúcsa:   %.2f %% (%s)\n', ...
    100*max(xx(:,7))/N_h, string(datum(find(xx(:,7)==max(xx(:,7)),1))));
fprintf('Kumulált HCW-fertőzések:  %.0f (a dolgozók %.1f %%-a)\n', fert_ossz, 100*fert_ossz/N_h);
fprintf('  - közösségből:          %.1f %%\n', 100*fert_ut(1)/fert_ossz);
fprintf('  - betegektől:           %.1f %%\n', 100*fert_ut(2)/fert_ossz);
fprintf('  - kollégáktól:          %.1f %%\n', 100*fert_ut(3)/fert_ossz);
fprintf('Kórházban ápoltak csúcsa: %.0f (ágyszám: %.0f)\n', max(H_ossz), agyak_szama);
fprintf('Legkisebb dolgozói arány: %.1f %%\n', 100*min(dolg_arany));

%% 13. Ábrák
figure('Name','SIHDR HCW modell','Position',[100 100 1000 750]);
tl = tiledlayout(2,2,'TileSpacing','compact','Padding','compact');

% (1) Fertőzöttek aránya a csoportjukon belül
nexttile
plot(datum, xx(:,2)/N_c, datum, xx(:,7)/N_h, 'LineWidth', 2)
legend('Civilek','HCW-k','Location','best')
title('Fertőzöttek aránya (I / N)'); ylabel('arány'); grid on

% (2) HCW fertőzési erő komponensei
nexttile
area(datum, lam, 'LineStyle','none')
legend('Közösség','Beteg \rightarrow HCW','HCW \rightarrow HCW','Location','best')
title('HCW fertőzési erő komponensei (\lambda_h)'); ylabel('1/nap'); grid on

% (3) Kórházban ápoltak vs. ágykapacitás
nexttile
plot(datum, H_ossz, 'LineWidth', 2); hold on
yline(agyak_szama, '--r', 'Ágykapacitás', 'LineWidth', 1.5);
title('Kórházban ápoltak (H_c + H_h)'); ylabel('fő'); grid on

% (4) Dolgozói arány
nexttile
plot(datum, dolg_arany, 'LineWidth', 2)
ylim([0 1.05])
title('Munkában lévő HCW-k aránya'); ylabel('arány'); grid on

title(tl, 'SIHDR modell civilekkel és egészségügyi dolgozókkal');