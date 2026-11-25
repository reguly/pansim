"""A panSim kórházai (12-es helyszíntípus): kapacitás, koordináta (EOV és WGS84), a hozzájuk rendelt
lakosok és az ott dolgozó egészségügyi dolgozók száma.

A HCW-definíció ugyanaz, mint a panSim flagHealthcareWorkers()-ében
(src/runtime/simulationOrchestration.cpp): van "work" (typeID 4) bejegyzése, és az a helyszín
valójában 12-es (kórház) vagy 14-es (rendelő) típusú. A turisták (agent typeID 9) nem kerülnek be
a szimulációba (--disableTourists alapértéke 1), ezért itt is kimaradnak.

A koordináták EOV-ban vannak ([X északi, Y keleti], HD72/EOV, EPSG:23700). Az átváltás saját
képlettel történik (pyproj nélkül); a HD72 -> WGS84 dátumeltolást nem végzi el, ez kb. 50-100 m
hiba, ami az épületek azonosításához elég.

Futtatás:
    python hospital_census.py <agents1.json> <locations0.json> [kimenet.csv]
"""
import collections
import csv
import json
import sys
from math import asin, atan, cos, degrees, exp, pi, radians, sin, sqrt, tan

# EOV (Hungarian oblique Mercator, GRS67 ellipszoid)
E = sqrt(0.006694605329)
R, K0, N, K = 6379743.001, 0.99993, 1.000719704936, 1.003110007693
PHI0_SPHERE = radians(47 + 6/60)
LAM0 = radians(19 + 2/60 + 54.8584/3600)


def eov_to_latlon(x_north, y_east):
    x, y = x_north - 200000, y_east - 650000
    ps = 2*atan(exp(x/(R*K0))) - pi/2
    ls = y/(R*K0)
    p1 = asin(cos(PHI0_SPHERE)*sin(ps) + sin(PHI0_SPHERE)*cos(ps)*cos(ls))
    l1 = asin(cos(ps)*sin(ls)/cos(p1))
    phi = p1
    for _ in range(20):
        phi = 2*atan((tan(pi/4 + p1/2)/K * ((1 + E*sin(phi))/(1 - E*sin(phi)))**(N*E/2))**(1/N)) - pi/2
    return degrees(phi), degrees(LAM0 + l1/N)


def main(agents_path, locations_path, out_csv=None):
    places = json.load(open(locations_path, encoding="utf-8"))["places"]
    loc = {p["ID"]: p for p in places}
    people = [a for a in json.load(open(agents_path, encoding="utf-8"))["people"] if a["typeID"] != 9]

    residents, staff = collections.Counter(), collections.Counter()
    per_agent = collections.Counter()
    for a in people:
        hs = [l["locID"] for l in a["locations"] if l["typeID"] != 4 and loc.get(l["locID"], {}).get("type") == 12]
        per_agent[len(hs)] += 1
        residents.update(hs)
        work = {l["locID"] for l in a["locations"]
                if l["typeID"] == 4 and loc.get(l["locID"], {}).get("type") in (12, 14)}
        staff.update(work)

    rows = []
    for p in places:
        if p["type"] != 12:
            continue
        lat, lon = eov_to_latlon(*p["coordinates"])
        rows.append(dict(ID=p["ID"], capacity=p.get("capacity"), eov_x=p["coordinates"][0],
                         eov_y=p["coordinates"][1], lat=round(lat, 5), lon=round(lon, 5),
                         residents=residents[p["ID"]], hcw=staff[p["ID"]]))
    print(f"agents (no tourists): {len(people)}; hospital entries per agent: {dict(per_agent)}")
    print(f"HCW total: {sum(1 for a in people if any(l['typeID'] == 4 and loc.get(l['locID'], {}).get('type') in (12, 14) for l in a['locations']))}"
          f" (hospitals: {sum(r['hcw'] for r in rows)}, clinics: {sum(v for k, v in staff.items() if loc[k]['type'] == 14)})")
    print(f"{'ID':<14}{'cap':>5}{'lat':>10}{'lon':>10}{'residents':>11}{'HCW':>6}")
    for r in rows:
        print(f"{r['ID']:<14}{r['capacity']:>5}{r['lat']:>10.5f}{r['lon']:>10.5f}{r['residents']:>11}{r['hcw']:>6}")
    if out_csv:
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)


if __name__ == "__main__":
    main(*sys.argv[1:4])
