# SZTE COVID-központ teszt

**Kérdés:** visszaadja-e a panSim az SZTE kieső dolgozóinak görbéjét (2. hullám: 10%-os csúcs nov. 9-én,
3–4%-os szept.–okt. plató), ha a COVID-betegeket – a valósághoz hasonlóan – a kijelölt COVID-épületekben
látják el, és nem egyenletesen a város összes kórházában?

**Miért:** a panSim-ben jelenleg minden lakosnak egy véletlenszerűen kiosztott kórháza van (17 kórház, egyenként
kb. 10 500 lakos), így a súlyos COVID-betegek egyenletesen oszlanak el. A fertőzési kockázat egy helyszínen a
jelenlévők közti fertőzöttek arányától függ (`include/policies/infectionPolicies.h`), tehát a betegek
összevonása az ott dolgozók kitettségét erősen növeli.

## Az SZTE COVID-ellátása (a felhasználó jegyzetei alapján)

- **Kálvária sgt. 57. (Járványügyi Ellátó Központ, JEK):** légúti ambulancia, fekvőbeteg-ellátás és az
  intenzív terápia COVID részlege. Ez volt a fő COVID-épület.
- **Korányi fasor 8. (1–2. emelet):** a JEK fekvőbeteg-ellátásához kapcsolódott.
- **Temesvári krt. 35–37.:** a Gyermekgyógyászati Klinika COVID részlege.
- **ELI-ALPS csarnokok:** 118 ágyas tartalék kórház (2020 tavasz), a panSim helyszínei között nincs.
- A súlyos állapotú betegeket a régióból is Szegedre irányították, az enyhébbeket más intézmények látták el.
- A dolgozói adat (3798 fő) pontos köre nem ismert; feltevés: a teljes klinikai központot fedi.

## Helyszínek a panSim bemenetében

`hospital_census.py` → `hospitals.csv`. A 17 kórház (6811 dolgozó) koordinátái EOV-ban vannak, a szkript
WGS84-re váltja őket. Az azonosítás a koordinátákon alapul, **térképen ellenőrizendő**:

| épület | panSim helyszín(ek) | dolgozók | koordináta |
|---|---|---|---|
| JEK, Kálvária sgt. 57. (valószínű) | `28565_1491`, `178777_1503`, `221632_1504`, `221633_1505` (egy ponton) | 1802 | 46.25424, 20.12696 |
| Korányi fasor 8. (valószínű) | `64118_1496` | 420 | 46.24781, 20.15173 |
| Temesvári krt. 35–37., Újszeged (valószínű) | `148295_1686` (kis kórház) | 35 | 46.24327, 20.17001 |
| belvárosi klinikák | a többi 10 nagy és 1 kis kórház | 4554 | 46.243–46.252, 20.143–20.152 |

A rendelők (14-es típus, 95 db, 3325 dolgozó) nem részei a viszonyítási körnek.

## Új panSim-kapcsolók (alapértelmezésben kikapcsolva, a működés változatlan)

| kapcsoló | hatás | kód |
|---|---|---|
| `--covidHospitals id1,id2,...` | a súlyos COVID-betegek (WBState S) ezekben a kórházakban vannak a saját kórházuk helyett (több helyszín esetén egyenletesen elosztva); a nem COVID-os kórházi ápolás nem változik | `movementPolicies.h`, `RealMovement::movement()` és `initCovidHospitals()` |
| `--covidHospitalsMild 1` | az enyhe esetek (WBState M) kórházi látogatásai is ide mennek | ugyanott |
| `--hcwFocus id1,...` vagy `hospital` | a megadott munkahelyek HCW-ire külön oszlopok: `FHCW` (létszám), `FHCE` (napi új fertőzés), `FHCWH`, `FHCWD`, `FHCWQI`, `FHCWQN`, `FHCWU` (mint a HCI-bontás) | `simulationOrchestration.cpp`, `flagFocusWorkers()` és a statisztika vége |

Az SZTE-vel összevethető kiesés: `(FHCWH + FHCWD + FHCWQI + FHCWQN) / FHCW`.

## Futtatás

```bash
# a repó gyökeréből; előbb rövid próba
RESULTS_ROOT=experiments/szte_covid_center/results_smoke N_RUNS=2 WEEKS=2 \
SCENARIOS_FILE=experiments/szte_covid_center/scenarios.yaml ./experiments/hcw_interventions/run_scenarios.sh
# teljes köteg (6 forgatókönyv x 20 futás x 52 hét, kb. 8 óra) Slurm-jobként
sbatch experiments/szte_covid_center/run_szte.sbatch
```

A `run_szte.sbatch` a korábbi `hci_split.sbatch` mintájára készült (`cpu` partíció, 16 szál, 12 óra,
`~/PanSim/pansim`). Ha a job időkorlát miatt leáll, újra beküldhető: a már kész forgatókönyveket
(van `all_runs.tsv`) átugorja. A napló a beküldés könyvtárában: `szte_covid_<jobid>.log`.

## Füstteszt (helyben, WSL/OMP, egy-egy 10 hetes futás)

Viszonyítási kör: a JEK négy helyszínének 1802 dolgozója.

| | JEK-dolgozók fertőzései (FHCE) | többi HCW | JEK-kiesés a 10. héten |
|---|---|---|---|
| átirányítás nélkül | 176 | 1123 | 2,7% |
| `--covidHospitals` = JEK | 287 | 876 | 3,4% |

Egyetlen futás, csak a működés ellenőrzése. A kapcsolók nélküli futás kimenete formailag változatlan.

## Korlátok

- Egy kórház egyetlen keveredési tér: a JEK minden dolgozója egyformán ki van téve a COVID-betegeknek.
- A régióból érkező betegek hiányoznak (a panSim-ben csak szegedi lakosok vannak). Következő lépés lehet egy
  vonzáskörzet-szorzó a COVID-kórház betegeinek fertőzési súlyára.
- A gyermekek nem kerülnek külön a Temesvári körúti részlegre.
- A helyszínek azonosítása a koordinátákon alapul.
