#!/usr/bin/env python3
"""Relève (une fois par heure) l'air et la surface du sol à La Madeleine, pour juger si la température du sol aide à prévoir le verglas.
Deux lignes par relevé : la valeur de l'heure en cours (lead_h = 0) et la prévision à +12 h (lead_h = 12)."""
import csv, json, sys, urllib.request
from datetime import datetime, timedelta, timezone

OUT = sys.argv[1]
LAT, LON = 50.65, 3.07
URL = ("https://api.open-meteo.com/v1/forecast?latitude=%s&longitude=%s&timezone=UTC&past_days=1&forecast_days=2"
       "&hourly=temperature_2m,soil_temperature_0cm,precipitation,rain,snowfall,weather_code,relative_humidity_2m" % (LAT, LON))
FIELDS = ["temperature_2m", "soil_temperature_0cm", "precipitation", "rain", "snowfall", "weather_code", "relative_humidity_2m"]
now = datetime.now(timezone.utc)

try:
    rows = list(csv.reader(open(OUT)))
    if len(rows) > 1:
        last = datetime.strptime(rows[-1][0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if now - last < timedelta(minutes=55):
            print("relevé météo déjà fait il y a moins de 55 min"); sys.exit(0)
    new = False
except FileNotFoundError:
    new = True

with urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "trajet-matin-logger"}), timeout=30) as r:
    h = json.load(r)["hourly"]
idx = {t: i for i, t in enumerate(h["time"])}
ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
out = []
for lead in (0, 12):
    v = (now + timedelta(hours=lead)).replace(minute=0, second=0, microsecond=0)
    k = idx.get(v.strftime("%Y-%m-%dT%H:%M"))
    if k is None:
        continue
    out.append([ts, v.strftime("%Y-%m-%dT%H:%M:%SZ"), lead] + [h[f][k] for f in FIELDS])
with open(OUT, "a", newline="") as f:
    w = csv.writer(f)
    if new:
        w.writerow(["ts_utc", "valid_utc", "lead_h"] + FIELDS)
    w.writerows(out)
print(f"{len(out)} lignes météo ajoutées")
