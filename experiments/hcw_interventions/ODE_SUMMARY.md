# HCW-beavatkozások: összefoglaló az ODE-modellhez

Ez a fájl összegyűjti, milyen NPI-ket és beállításokat teszteltünk a panSim HCW-kísérletében, hogy
egy ODE-modell ugyanezeket reprodukálhassa. Források: `../../scripts/run_20_sims.sh`
(`PARAM_SET=validated`), `scenarios.yaml`, a closures JSON-fájlok (`../../inputConfigFiles/`),
`include/policies/closurePolicies.h`, `testingPolicies.h`, `movementPolicies.h`. Az eredmények a
`outputs/relative_risk_table.csv` és a `outputs/per_run.csv` fájlból valók.

Az ODE-modellhez a legfontosabb négy megkötés:

- Az alapeset maga is tartalmaz egy teljes, időzített NPI-menetrendet.
- A `closuresNone` ezt a menetrendet a variánsokkal együtt kapcsolja ki.
- A tesztelési kar csak a 0–258. napon számít.
- A kórházakat soha nem zárja munkahelyi karantén.

## 1. Közös beállítások (minden forgatókönyvben)

| Beállítás | Érték |
|---|---|
| Populáció | 178 746 ágens (Szeged, szintetikus), ebből **10 136 egészségügyi dolgozó (5,67%)**. Egészségügyi dolgozó = akinek a munkahelye kórház (12-es típus) vagy rendelő (14-es típus). A turisták nem kerülnek be a szimulációba. |
| Időtáv | 52 hét = 364 nap. **0. nap = 2020-09-23**, utolsó nap = 2021-09-21. |
| Ismétlés | 20 sztochasztikus futás forgatókönyvenként, rögzített seed nélkül |
| Paraméterkészlet | `PARAM_SET=validated`: `-k 0.00041` (fertőzési együttható), `--progression inputConfigFiles/progressions_Jun17_tune/transition_config.json`, `-A inputConfigFiles/agentTypes_3.json`, `--quarantinePolicy 3` |
| Variánsok fertőzőképessége | `--infectiousnessMultiplier 0.98,1.85,2.05,2.58,4.32,6.8,6.8` (sorrendben: vad típus, alfa, delta, BA.1, …) |
| Variánsok betegséglefolyása | `--diseaseProgressionScaling 0.94,1.03,1.40,0.72,0.57,0.463,0.45` |
| NPI-menetrend | `--closures inputConfigFiles/closureJun6_real_later3_delta_omicronBA2_earlier8.json` (lásd a 2. pontot) |

## 2. Az alapeset beépített NPI-menetrendje

Ez a menetrend minden forgatókönyvben fut, kivéve a `closuresNone` és a `closuresNone_hiTest`
futásokat. A kezdőnap a 0. naphoz képest értendő, a záró nap is bele van számolva. A
helyszíntípusok azonosítói a `inputConfigFiles/locationTypes.json` fájlból valók.

| NPI | Napok | Dátum | Pontos hatás |
|---|---|---|---|
| Nagy rendezvényhelyek (6-os típus) és idősotthonok (22-es típus) zárva | 0–48 | 2020-09-23 – 11-10 | A helyszín bezár, az ágensek nem mennek oda |
| Egyetemek (44-es típus) zárva | 49–341 | 2020-11-11 – 2021-08-30 | ugyanígy |
| Idősotthonok (22-es típus) zárva | 49–217 | 2020-11-11 – 2021-04-28 | ugyanígy |
| Nagy rendezvényhelyek (6-os típus) zárva | 49–240 | 2020-11-11 – 2021-05-21 | ugyanígy |
| Éttermek, kocsmák (5-ös típus) zárva | 49–211 | 2020-11-11 – 2021-04-22 | ugyanígy |
| Üzletek, ügyintézés, templom (7-es, 8-as, 9-es típus) zárva | 166–196 | 2021-03-08 – 04-07 | ugyanígy |
| Iskolai korhatár 14 év | 49–165 | 2020-11-11 – 2021-03-07 | A 14 évesek és idősebbek nem járnak iskolába |
| Iskolai korhatár 3 év (gyakorlatilag teljes iskolazár) | 166–207 | 2021-03-08 – 04-18 | ugyanígy |
| Iskolai korhatár 10 év | 208–227 | 2021-04-19 – 05-08 | Csak a 10 év alattiak járnak iskolába |
| Iskolai korhatár 3 év (nyári szünet) | 263–341 | 2021-06-13 – 08-30 | ugyanígy |
| Kijárási korlátozás 20:00–05:00 | 49–196 | 2020-11-11 – 2021-04-07 | Esti tevékenységek tiltva |
| Kijárási korlátozás 22:00–05:00 | 197–211 | 2021-04-08 – 04-22 | ugyanígy |
| Kijárási korlátozás 23:00–05:00 | 212–219 | 2021-04-23 – 04-30 | ugyanígy |
| Mozgáscsökkentés (`ReduceMovement` 0,0949) | 49–100 | 2020-11-11 – 2021-01-01 | Az ágensek 9,5%-a otthon marad |
| Ünnepi üzemmód (`HolidayMode`) | 92–95 | 2020-12-24 – 12-27 | Ünnepi napirend |
| Tesztelési arányok átállítása (`TestingProb`) | 259-től | 2021-06-09-től végig | A kórházi és rendelői dolgozók napi tesztelési valószínűsége 0,005-ről **0,5**-re nő. Visszaállítás nincs. |
| Alfa-variáns behozatala (`ExposeToMutation`, 1. variáns) | 132–137 | 2021-02-02 – 02-07 | Naponta a populáció 0,024%-a fertőződik meg a variánssal |
| Delta-variáns behozatala (`ExposeToMutation`, 2. variáns) | 316–321 | 2021-08-05 – 08-10 | Naponta 0,035% |

A fájlban lévő maszkszabály (`Masks` 1,25) és karanténszabály-váltás (`QuarantinePolicy` 1) csak
az 530. napon indulna, vagyis **a vizsgált évben nem aktív**. A többi variáns behozatala is a 364.
nap után van. Az emlékeztető oltások a compiled defaultok szerint a 315. naptól (2021-08-04) futnak
(`--boosterStart 315`).

## 3. Tesztelés, karantén és oltás az alapesetben

**Tesztelés** (`testingPolicies.h`):

- Minden ágens naponta ennyi valószínűséggel teszteltet. A tagok összeadódnak:
  - véletlen tesztelés: 0,00005
  - ha a háztartásban valakit az elmúlt 24 órában diagnosztizáltak: +0,01
  - ha a munkahelyén diagnosztizáltak valakit: +0,0005
  - ha az iskolájában: +0,0005; ha az osztálytermében: +3 × 0,0005
  - **ha kórházban vagy rendelőben dolgozik: +0,005**
  - ha idősotthonban dolgozik: +0,05
- Ez a hat érték a `--testingProbabilities` sorrendje: véletlen, háztartás, munkahely, iskola,
  kórház, idősotthon.
- Két teszt között legalább 5 nap telik el (`--testingRepeatDelay 5`).
- A teszt PCR (`--testingMethod PCR`). Az érzékenysége a fertőzés állapotától függ (a progressziós
  konfigurációból jön).

**Karantén (3-as szint, `movementPolicies.h`):**

- Diagnózis után 10 napig (`--quarantineLength 10`) karanténban van:
  - maga a diagnosztizált ágens,
  - a teljes háztartása,
  - a munkahelye vagy az osztályterme.
- **Kórházat és rendelőt soha nem zár be.** A munkahelyi karanténlépés csak a 4-es típusú
  munkahelyekre és az osztálytermekre hat (lásd `README.md`, „Why `prevalence_RR` and
  `incidence_RR` disagree”).

**Oltás:**

- Kezdete a 96. nap (2020-12-27, `--immunizationStart 96`). A heti oltásszám a
  `inputConfigFiles/vaccPerWeek.txt` fájlból jön (kb. 61%-os átoltottságra skálázva).
- Prioritási sorrend (`--immunizationOrder 1,2,3,4,5,6,0,0,7,8`), az első helyen az egészségügyi
  dolgozók: egészségügyi dolgozók, idősotthon, 60 év felett, 18–60 év alapbetegséggel,
  kulcsmunkakörök, 18 év felett, (60 év felett alapbetegséggel: kihagyva), (pedagógusok:
  kihagyva), 12–18 év, 5–12 év.
- Átoltottsági szintek kategóriánként (`--vaccinationGroupLevel`):
  `0.9,0.85,0.9,0.82,0.8,0.75,0.8,0.67,0.4,0.2`. Az egészségügyi dolgozóknál ez **90%**.

## 4. A tesztelt forgatókönyvek

Mindegyik az alapesettől egyetlen beállításban vagy kapcsolóban tér el, kivéve a kombinációkat.
Mutatók:

- **incidencia-RR** = (az egészségügyi dolgozók napi új fertőzései / 10 136) osztva (a többiek
  napi új fertőzései / 168 610).
- **HCW-fertőzések** = az egészségügyi dolgozók összes új fertőzése egy év alatt (20 futás
  mediánja).

| Forgatókönyv | panSim-kapcsoló | Pontos jelentés | Inc.-RR | HCW-fertőzések |
|---|---|---|---|---|
| `baseline` | – | A fenti beállítások | **1,38** | 4302 |
| `quarantine0` | `--quarantinePolicy 0` | Nincs karantén: a diagnosztizált ágens és a kontaktjai is járnak tovább | 1,47 | 6669 |
| `longQuarantine` | `--quarantineLength 21` | A karantén 10 helyett 21 nap | 1,35 (nem szignifikáns) | 4053 |
| `closuresNone` | `--closures inputConfigFiles/noRules.json` | **Az egész 2. pontbeli menetrend kikapcsolva**: zárások, iskolai korhatár, kijárási korlátozás, mozgáscsökkentés, a 259. napi tesztelésemelés **és a variánsok behozatala is**. Az egész év a vad típussal fut. | 1,38 (nem szignifikáns) | 4923 |
| `noVacc` | `--immunizationsPerWeek 0` | Senkit nem oltanak | 1,78 | 7000 |
| `noVaccHCW` | `--immunizationOrder 0,2,3,4,5,6,0,0,7,8` | Csak az egészségügyi dolgozók kategóriája marad ki az oltásból. Az ő adagjaik a többi kategóriához kerülnek, mindenki más oltási ütemterve változatlan. | 1,82 | 6092 |
| `hiTest` | `--testingProbabilities 0.00005,0.01,0.0005,0.0005,0.5,0.05` | A kórházi és rendelői dolgozók napi tesztelési valószínűsége 0,005 helyett 0,5. **Csak a 0–258. napon tér el az alapesettől**, mert a 259. naptól az alapeset is 0,5-öt használ. | 1,09 | 3056 |
| `hcwDailyTest` | `--testingProbabilities 0.00005,0.01,0.0005,0.0005,0.95,0.05 --testingRepeatDelay 1` | Napi tesztelés: 0,95 valószínűség, és naponta újra lehet tesztelni (az alapeset 5 napos szünete helyett) | 1,00 | 2640 |
| `hcwPPE` | `--closures inputConfigFiles/closureJun6_real_later3_delta_omicronBA2_earlier8_hospitalPPE.json` (új C++-szabály) | `HospitalPPE` 0,3 a 0. naptól végig: **a kórházakban és rendelőkben a fertőzőképesség ×0,3** (70%-os csökkentés). A többi helyszín és a teljes menetrend változatlan. A kórházban és rendelőben tartózkodó betegekre is hat, nem csak a dolgozókra. | **0,71** | 1946 |
| `noVaccHCW_hiTest` | `noVaccHCW` + `hiTest` | Kombináció | 1,52 | 4264 |
| `closuresNone_hiTest` | `closuresNone` + `hiTest` | Kombináció. A tesztelés itt az egész évben eltér, de a variánsok is hiányoznak. | 1,13 | 3363 |
| `quarantine0_noVaccHCW` | `quarantine0` + `noVaccHCW` | Kombináció | 1,62 | 7565 |
| `quarantine0_hiTest` | `quarantine0` + `hiTest` | Kombináció | 1,48 | 6665 |

A `closuresNone` és a `longQuarantine` kivételével minden RR-eltérés szignifikáns (Mann–Whitney-próba,
BH-FDR korrekció, q < 0,05; `outputs/significance.csv`).

## 5. Mire figyeljen az ODE-modell

1. **Az alapeset NPI-menetrendje időfüggő.** Az ODE-ben ez egy darabonként állandó kontakt-szorzóként
   jelenik meg (a zárások, az iskolai korhatár, a kijárási korlátozás, a mozgáscsökkentés hatása).
   Ezt egyszer illeszteni kell a panSim alapesetéhez, mielőtt bármelyik forgatókönyvet összevetjük.
2. **A `closuresNone` két dolgot kapcsol ki egyszerre:** a menetrendet és a variánsokat. Ezért csak
   úgy reprodukálható, ha az ODE-ben a variáns-kompartmenteket is kivesszük. Ha a cél egy tiszta
   zárási hatás, egy olyan closures-fájl kell, ami a variánsok behozatalát megtartja. Ilyen még nincs.
3. **A tesztelés eltávolítási rátaként modellezhető:** az egészségügyi dolgozókra kb.
   p_teszt × érzékenység per nap, a 259. naptól lépcsővel. Az 5 napos tesztelési szünet a `hiTest`-ben
   a ténylegesen elérhető ráta felső korlátját kb. 1/5 per napra teszi. A `hcwDailyTest` ezt a
   korlátot oldja fel.
4. **A karantén aszimmetrikus:** az egészségügyi dolgozókat csak a háztartási és a saját diagnózis
   miatti karantén érinti, a munkahelyi nem. Az ODE-ben a többi lakosra erősebb karanténhatást kell
   tenni.
5. **A PPE a munkahelyi fertőzési tagot szorozza:** β_kórház × 0,3. Ehhez az ODE-ben külön kórházi
   kontakttag kell, ami a betegeken keresztül a többi lakosra is visszahat.
6. **Melyik mutatóhoz illesszünk:** az incidencia-RR-hez (pontos számlálás). A prevalencia-RR-hez és
   a HCI-hoz ne, mert a HCI egészre csonkolt százalék, ráadásul „fertőzött vagy karanténban”
   definíciójú.
