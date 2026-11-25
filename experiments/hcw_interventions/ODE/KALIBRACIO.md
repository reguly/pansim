# A SIHDR_HCW ODE kalibrálása a panSim alapesetére és a valós adatokra

Szkript: `kalibracio.py`. Futtatás: `python kalibracio.py`, kb. 1 perc. A kimenet a
`kalibracio_kimenet/` mappába kerül: `parameterek.json`, `illeszkedes.csv` és két ábra.

A cél: ugyanaz az ODE adja vissza

- **(A)** a panSim alapeset 20 futásának átlagát populációs és HCW-szinten;
- **(B)** a valós adatokat:
  - populációs szinten a `korona_hun.xlsx` kórházi ápoltjait és halálozását, a panSim
    178 746 fős populációjára skálázva (×178 746 / 9,7 M);
  - HCW-szinten az SZTE „COVID miatt kieső dolgozók” görbéjét. Ezt Röst G. diájáról kézzel
    olvastuk le, ±0,3 százalékpont pontossággal. **Bizalmas**, ezért a git által figyelmen kívül
    hagyott `experiments/validation_1yr/data/hungarian_data/szte_kieso_digitalizalt.csv` fájlban van.

Az időablak a panSim alapesettel azonos: 2020-09-23-tól 364 nap. A populáció is a panSimé:
N_c = 168 610, N_h = 10 136.

## 1. Mi változott az ODE-ben

Az egyenletek a `SIHDR_HCW_v3.py` 5–6. pontjának egyenletei. A v3 egyetlen hullámot ír le, állandó
β-val, ezért négy bővítés kellett. Mind kikapcsolható. Kikapcsolva a szkript visszaadja a v3
eredményét: civil csúcs 25,03%, HCW-csúcs 15,48%, 7148 kumulált HCW-fertőzés. A v3 ugyanezekre
25,04%-ot, 15,52%-ot és 7145-öt ad. A kis eltérés a szigorúbb integrátor-tűrésből jön.

| Bővítés | Képlet | Honnan jön |
|---|---|---|
| Közösségi kontaktusszorzó | β → β·c(t)·v(t) a λ_c-ben és a λ_comm-ban. c(t) 3 hetente csomópontos, szakaszonként lineáris, simított | Illesztve. A zárásokat, az iskolákat és a kijárási tilalmat foglalja össze. A kórházi tagokra nem hat, mert a kórházakat nem zárták be |
| Variánsszorzó | v(t) = 1 + (1,85/0,98 − 1)·alfa% + (2,05/0,98 − 1)·delta%. Minden fertőzési tagra hat, a kórháziakra is | A panSim `--infectiousnessMultiplier` és a `MUT` oszlop variánsarányai |
| Oltás | S → R áram e_v·u(t − τ_v)·S/(S+R): a t napon a τ_v = 14 nappal korábban beadott adagok válnak hatásossá. A HCW-k kapják az első 0,9·N_h adagot | (A): a panSim `VAC` oszlopa, e_v = 0,77 (`protectionInfection`, 2 adag). (B): a valós első adagok skálázva; a HCW-k 2020-12-26 és 2021-01-31 között |
| Karanténban lévő, nem fertőzött HCW-k | Q_h = [κ_comm·N_h·I/N + κ_work·c_test·I_h]·(1 − beoltott HCW-arány). Q_h a kiesők része | A beoltottakat a panSim nem teszi kontaktkarantén alá: `movementPolicies.h:183-185`, `quarantineImmuneActive = false`. Ez nélkül a HCI 3. hulláma nem illeszthető |

**Összevont HCW-fertőzési paraméterek.** A v3 HCW-fertőzési erejében hét szorzó van (θ, σ_c, σ_w,
β_p, β_s, q_H, q_I_h), de ezek csak szorzatként hatnak, külön nem azonosíthatók. Ezért három,
külön értelmezhető és külső adattal összevethető paraméterbe vannak összevonva (`osszevont()`):

| Új paraméter | = a v3 szorzóiból | Jelentés |
|---|---|---|
| ρ_c | (1 − θ)·σ_c | a HCW-k közösségi fertőződése a civilekéhez képest (dimenzió nélküli) |
| β_PH | θ·σ_w·β_p·q_H | napi fertőződési ráta betegtől, ha minden kórházi ágyban COVID-beteg fekszik |
| β_HH | θ·σ_w·β_s·q_I_h | napi fertőződési ráta kollégától, ha minden kolléga fertőző és nem szűrték ki |

Így λ_h = ρ_c·β·c·v·I/N + β_PH·v·H/(H + P_0) + β_HH·v·(1 − c_test)·I_h/N_w. Az átparaméterezés
a modellt nem változtatja meg; a v3-ellenőrzés a v3 értékeiből számolt ρ_c, β_PH, β_HH-val fut.

### Az egyenletek

A `kalibracio.py` `rhs()` függvénye alapján. Két csoport van: civilek (c) és egészségügyi
dolgozók (h), mindkettőben S, I, H, D, R kompartmentekkel. Jelölések: N = N_c + N_h,
I = I_c + I_h, H = H_c + H_h. A képeket az `egyenletek_kepek.py` rajzolja az `egyenletek/`
mappába; ha egy képlet változik, ott kell átírni és újrafuttatni.

**A kompartmentek kapcsolata.** Folytonos nyíl: emberek áramlása, a nyílon a ráta. Szaggatott
nyíl: hatás, vagyis melyik kompartment melyik fertőzési erőt, a karantént vagy a dolgozói arányt
táplálja. Az ábrát a `kompartment_abra.py` rajzolja.

![Kompartment-diagram](egyenletek/kompartmentek.svg)

**Segédmennyiségek.** A karanténban lévő HCW-k száma (Q_h) algebrai, nem állapotváltozó. K a
kieső, N_w a dolgozó HCW-k száma, DA a dolgozói arány:

![Segédmennyiségek](egyenletek/segedmennyisegek.svg)

**Fertőzési erők:**

![Fertőzési erők](egyenletek/fertozesi_erok.svg)

**Oltás.** Az u_g(t) napi adag a fertőzésen még át nem esett (S + R) csoport között oszlik meg, és
az S-be jutó adagok e_v része hatásos:

![Oltás](egyenletek/oltas.svg)

**Civilek:**

![Civil kompartmentek](egyenletek/civilek.svg)

**Egészségügyi dolgozók:**

![HCW kompartmentek](egyenletek/hcw.svg)

**Kumulált számlálók.** Ezek nem hatnak vissza a dinamikára, csak a forrásbontáshoz kellenek:

![Kumulált számlálók](egyenletek/szamlalok.svg)

**Időfüggő bemenetek:**

- c(t): kontaktusszorzó, 21 naponkénti csomópontok között lineárisan interpolálva. Ez az
  illesztett érték.
- v(t): a variánsok fertőzőképességi szorzója (lent). α(t) és δ(t) a variánsok részaránya a
  panSim `MUT` kimenetéből.
- u_c(t), u_h(t): napi oltások a beadás napján; a hatásuk τ_v = 14 nappal később jelentkezik
  (panSim: az első adag után 1 hétig nincs védelem, 1–4 hét között fél védelem).
- f_vax,h(t): a beoltott HCW-k aránya, késleltetés nélkül. Ez adja a karanténmentességet.

![Variánsszorzó](egyenletek/variansszorzo.svg)

**Megfigyelt mennyiségek:**

![Megfigyelt mennyiségek](egyenletek/megfigyelt.svg)

**Megjegyzések:**

- A DA-val való osztás a v3-ból öröklődött. Ha DA < 1, vagyis kevesebb a dolgozó, akkor gyorsul a
  kórházi kiáramlás, a halálozási hányad pedig p_D/DA-ra nő. Ezért jelenik meg a halálozás
  kiáramlása DA²-tel osztva. Lásd a 6. pontot.
- A K-ban D_h is szerepel, tehát az elhunyt dolgozók tartósan kiesőként számítanak, a v3-mal
  egyezően.
- p_H,h = hpr · p_H,c, ahol hpr = 1 rögzített érték.

## 2. Melyik modellmennyiség melyik adatnak felel meg

| Adat | Definíció | ODE-megfelelő |
|---|---|---|
| panSim HCI | A fertőzött (**diagnosztizálatlan is**) VAGY karanténban lévő HCW-k %-a. Futásonként egészre csonkolják | (I_h + H_h + Q_h)/N_h. Az összevetésben max(x − 0,5; 0), a csonkolás miatt |
| panSim HCE | Új HCW-fertőzések naponta | λ_h·S_h |
| SZTE kieső | A COVID miatt nem dolgozók %-a a 3798 fős létszámból | (c_test·I_h + H_h + Q_h)/N_h, csak a **detektált** fertőzöttek |
| Kórházi ápoltak | panSim: I5_h + I6_h. Valós: „Kórházi ápoltak száma” | H_c + H_h |

## 3. Paraméterek

**Rögzített értékek a panSim alapján:**

- τ_I = 1/8, mint a v3-ban. A panSim E+I hossza 8–10 nap.
- LOS = 1/τ_H = 10 nap, mint a v3-ban és a panSim I5_h/I6_h állapotában. Szabadon hagyva 3 napra
  futott le: a p_H_c-vel együtt csak a szorzatuk azonosítható.
- p_H_h = p_H_c. A panSim a HCW-k kórházi felvételét nem írja ki külön.
- P_0 = 609. Ez a panSim nem-COVID kórházi betegeinek átlaga (`H` oszlop). A v3-ban 50 000 volt,
  ami Szegedre két nagyságrenddel sok.
- ω = 1/1000, a v3-ban 1/180. A panSim fertőzés utáni védettsége 85%, és hetente 0,3%-kal csökken.
  Az 1/180-as ráta fél év alatt a gyógyultak felét visszaküldené S-be.
- β_HH = 0,005 / nap, a v3 értékeiből (θ = 0,5, σ_w = 0,3, β_s = 1/3, q_I_h = 0,1). A panSim-ben
  a kollégától eredő fertőzés kicsi, az adat nem határozza meg.
- τ_v = 14 nap, az oltás hatásának késése (lásd fent).

**Illesztett értékek:**

| Paraméter | (A) panSim | (B) valós | Megjegyzés |
|---|---|---|---|
| p_H_c | 0,047 | 0,047 (az A-ból) | A panSim kórházi ápolt / új fertőzés aránya is kb. 5%. A (B)-ben nem azonosítható, mert szabadon hagyva a populáció 80%-a fertőződne meg |
| p_D | 0,21 | 0,19 | A panSim I6_h állapotában 19% hal meg |
| ρ_c | 1,47 | 1,66 | A HCW-k közösségi fertőződése a civilekének 1,5–1,7-szerese (v3: 0,35) |
| β_PH | 0,0050 / nap | 0,0052 / nap | Beteg → HCW. 600 nem-COVID és 150 COVID-beteg mellett kb. 0,1% / nap egy fogékony HCW-re (v3: 0,035) |
| c_test | 0,35 (rögzített) | **0,90** (felső korlát) | (A): a panSim-ben a pozitív tesztek és az új fertőzések aránya kb. 0,33 |
| κ_comm | 2,07 | 2,35 | Ennyi nem fertőzött, karanténban lévő HCW jut a populációs prevalencia arányában |
| κ_work | 0 (panSim-szabály) | **0,62** | Egy detektált HCW-re ennyi munkahelyi kontaktkarantén jut |
| c(t) | 0,46 → 0,34 → 0,39 → 0,05 | 0,69 → 0,35 → 0,41 → 0,05 | Nyáron a prevalencia kb. 0, ott a c(t)-t az adat nem határozza meg, ezért az alsó korlátra fut |
| HCW kezdeti fertőzöttség | a populáció arányában | 0,37% | |

## 4. Illeszkedés

| Cél | r | RMSE | Megfigyelt csúcs | ODE-csúcs |
|---|---|---|---|---|
| (A) kórházi ápoltak | 0,985 | 10,7 fő | 210 | 200 |
| (A) új civil fertőzések | 0,987 | 23 fő/nap | 431 | 469 |
| (A) HCE | 0,997 | 0,87 fő/nap | 32,0 | 31,9 |
| (A) HCI | 0,989 | 0,23 százalékpont | 4,8% | 4,85% |
| (A) kumulált halálozás | 1,000 | 3,7 fő | 554 | 553 |
| (B) kórházi ápoltak (valós) | 0,988 | 10,4 fő | 231 | 199 |
| (B) kumulált halálozás (valós) | 0,994 | 39 fő | 542 | 557 |
| (B) SZTE kiesők | 0,961 | 0,79 százalékpont | 10,0% | 8,9% |
| *referencia: panSim HCI vs. SZTE* | *0,904* | *2,07 százalékpont* | *10,0%* | *4,8%* |

Összesített eredmények egy évre:

| | panSim | ODE (A) | ODE (B) |
|---|---|---|---|
| incidencia-RR (HCW / nem HCW) | 1,37 | 1,45 | 1,50 |
| kumulált HCW-fertőzés | 4333 | 4362 | 4834 |
| ebből közösségből / betegtől / kollégától | – | 70 / 28 / 2% | 75 / 25 / 0,3% |
| HCI-csúcs, 2. hullám (2020 ősz) | 4,8% (csonkolt) | 5,35% (csonkolás nélkül) | 9,3% |
| kieső-csúcs, 2. hullám | – | 3,8% | 8,9% (SZTE: 10,0%) |
| kieső-csúcs, 3. hullám | – | 1,2% | 2,4% (SZTE: 3,2%) |

## 5. A karanténnal kapcsolatos zavar

Négy különböző dolog keveredik össze.

1. **A HCI nem kiesés.** A panSim HCI-je minden fertőzött HCW-t számol, a diagnosztizálatlanokat
   is, pedig ők dolgoznak. A karanténban lévőket is számolja. Az SZTE görbéje csak azokat
   számolja, akik ténylegesen nem dolgoztak. A panSim-paraméterekkel az ODE kieső görbéje (3,8%)
   ezért alacsonyabb, mint a HCI (5,35%).
2. **A panSim kórházat nem karanténoz.** A munkahelyi kontaktkarantén csak a 4-es típusú
   munkahelyekre és az osztálytermekre hat, a 12-es (kórház) és a 14-es (rendelő) típusra nem.
   A panSim HCW-karanténja tehát csak háztartási eredetű. Valójában az osztályokon kitört
   járványok után a kollégákat is hazaküldték. Ezt az ODE (B) κ_work = 0,61-gyel pótolja.
3. **A beoltottak mentesek.** A panSim a beoltott vagy korábban diagnosztizált ágenst nem teszi
   kontaktkarantén alá. A HCW-k 90%-a 2021 februárjára be volt oltva, ezért a 3. hullámban a HCW-k
   karanténja kb. 0. Ez a valóságban is így volt, a védettségi igazolvány mentesített. Ezért
   esik a kiesők száma a 3. hullámban jóval jobban, mint a populációs prevalencia.
4. **A panSim populációs karanténja kb. 8-szor akkora, mint a hatósági.** 2020 novemberében a
   panSim a lakosság 4%-át tartja karanténban; ennek 85%-a nem fertőzött kontakt (`Q` − `QT`).
   A `korona_hun.xlsx` „Hatósági házi karantén” oszlopa a csúcson 0,5%-ot mutat. A
   3-as karanténszint ugyanis minden diagnózisnál a teljes háztartást, a munkahelyet és az
   osztálytermet is karanténba küldi, 10 napra. A hatósági szám valószínűleg csak a
   rendőrségileg ellenőrzött házi karantént tartalmazza, a pozitívakat nem.

**Következmény:** a panSim HCI-je és az SZTE kiesőgörbéje között a kétszeres eltérés nem
feltétlenül jelent kétszer annyi fertőzést. Az ODE (B) a panSim-mel közel azonos számú
HCW-fertőzéssel (4834 vs. 4333) adja vissza a 10%-os csúcsot. Ehhez két dolog kell:

- a fertőzött HCW-k 90%-át kiszűrik és hazaküldik (c_test = 0,9; a panSim-ben kb. 0,35);
- munkahelyi kontaktkarantén.

**Ez a megoldás nem egyértelmű.** Ugyanezt a görbét több fertőzés és kevesebb karantén is
megmagyarázná. A (B) azt a megoldást választja, amelyik a panSim HCW-paramétereihez a
legközelebb van (ρ_c és β_PH gyenge priorral az (A) értékei felé húzva). A c_test a felső
korláton áll. Hogy melyik magyarázat igaz, azt az SZTE-adat definíciója döntené el: benne van-e
a karantén, és szét lehet-e bontani pozitívakra és kontaktokra.

## 6. Ismert korlátok

- **A 2021. augusztusi kis delta-hullám hiányzik.** A panSim-ben ezt a behurcolás
  (`ExposeToMutation`) indítja el. Az ODE-ben nincs behurcolási tag, és a nyári c(t) az alsó
  korlátra fut.
- **Az SZTE 2020. szept–okt. 3–4%-os platóját az ODE nem adja vissza.** Ekkor a populációs
  prevalencia még alacsony volt. A plató helyi kórházi gócra vagy a definícióban lévő
  karanténra utal.
- **A 2. hullám kórházi csúcsa ellaposodik** az ODE-ben (130 vs. 150 az (A)-ban). Ennek oka az
  exponenciális tartózkodási idő, a panSim-ben az idők közel rögzítettek. Egy E kompartment vagy
  Erlang-lépcsők segítene.
- **A Q_h algebrai mennyiség:** a karanténban lévő S_h-t a modell továbbra is fertőzhetőnek
  tekinti a munkahelyén.
- **A Dolgozok_aranya hatása gyorsítja a kórházi kiáramlást**, nem lassítja: a kifejezés
  τ_H·H/DA, ahol DA < 1, és a halálozási arány p_D/DA nő. A v3 fejléc-kommentje „lassul”-t ír,
  ez ellentmond a képletnek. A kalibrációban a DA ≥ 0,91, így a hatás kicsi.
- Az SZTE (3798 fő, egy klinikai központ) és a panSim (10 136 HCW, a 12-es és 14-es munkahelyek)
  HCW-fogalma eltér.
