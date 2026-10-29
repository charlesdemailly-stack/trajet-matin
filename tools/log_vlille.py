#!/usr/bin/env python3
"""Relève le stock de vélos de quelques stations V'Lille et l'ajoute à un CSV (une ligne par station et par relevé)."""
import csv, json, sys, time, urllib.request
from datetime import datetime, timezone

STATIONS = {"184": "Rue du Parc", "181": "Marie Marrant", "115": "De Gaulle", "98": "Place du Marché", "99": "La Madeleine Mairie", "96": "Romarin"}
URL = "https://media.ilevia.fr/opendata/station_status.json"
out = sys.argv[1]

def fetch():
    last = None
    for _ in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "trajet-matin-logger"}), timeout=20) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            last = e; time.sleep(3)
    raise last

j = fetch()
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
rows = []
for s in j["data"]["stations"]:
    if s["station_id"] in STATIONS:
        rows.append([now, s["station_id"], s.get("num_bikes_available"), s.get("num_docks_available"), int(bool(s.get("is_renting"))), int(bool(s.get("is_installed"))), s.get("last_reported"), j.get("last_updated")])
new = False
try:
    open(out).close()
except FileNotFoundError:
    new = True
with open(out, "a", newline="") as f:
    w = csv.writer(f)
    if new:
        w.writerow(["ts_utc", "station_id", "bikes", "docks", "renting", "installed", "last_reported", "feed_updated"])
    w.writerows(rows)
print(f"{len(rows)} lignes ajoutées")
