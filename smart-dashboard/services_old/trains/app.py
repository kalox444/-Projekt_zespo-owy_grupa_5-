import csv
import io
import json
import os
import re
import threading
import time
import zipfile
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from flask import Flask, jsonify

app = Flask(__name__)

TZ = ZoneInfo("Europe/Warsaw")
STRONA = "https://mobilitydatabase.org/feeds/gtfs/mdb-2087"
STACJE = {"18051": "Żukowo Zachodnie", "257551": "Żukowo"}
DATA_FILE = "/data/odjazdy_zukowo.json"
lock = threading.Lock()


def aktualizuj_rozklad():
    teraz = datetime.now(TZ)
    dzisiaj = teraz.strftime("%Y%m%d")
    try:
        html = requests.get(STRONA, timeout=60).text
        match = re.search(r'https://files\.mobilitydatabase\.org/mdb-2087/[^"]+\.zip', html)
        if not match:
            return
        zip_data = requests.get(match.group(0), timeout=120).content
        z = zipfile.ZipFile(io.BytesIO(zip_data))

        def czytaj(nazwa):
            try:
                with z.open(nazwa) as f:
                    return list(csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig")))
            except KeyError:
                return []

        aktywne = {
            r["service_id"]
            for r in czytaj("calendar_dates.txt")
            if r.get("date") == dzisiaj and r.get("exception_type") == "1"
        }

        kierunki = {
            r["trip_id"]: r["trip_headsign"]
            for r in czytaj("trips.txt")
            if r["service_id"] in aktywne
        }

        odjazdy = set()
        for r in czytaj("stop_times.txt"):
            if r["trip_id"] in kierunki and r["stop_id"] in STACJE:
                odjazdy.add((r["departure_time"][:5], kierunki[r["trip_id"]], STACJE[r["stop_id"]]))

        lista = [
            {"godzina": g, "kierunek": k, "stacja": s}
            for g, k, s in sorted(odjazdy)
        ]

        with lock:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({"data": dzisiaj, "odjazdy": lista}, f, ensure_ascii=False)
    except Exception as e:
        print("Błąd aktualizacji GTFS:", e)


def worker_w_tle():
    while True:
        teraz = datetime.now(TZ).strftime("%Y%m%d")
        aktualna_data = ""
        if os.path.exists(DATA_FILE):
            try:
                with lock, open(DATA_FILE, encoding="utf-8") as f:
                    aktualna_data = json.load(f).get("data", "")
            except Exception:
                pass
        if aktualna_data != teraz:
            aktualizuj_rozklad()
        time.sleep(900)


threading.Thread(target=worker_w_tle, daemon=True).start()


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/trains")
def get_trains():
    teraz = datetime.now(TZ)
    teraz_minuta = teraz.hour * 60 + teraz.minute

    try:
        with lock, open(DATA_FILE, encoding="utf-8") as f:
            dane = json.load(f)
    except Exception:
        return jsonify({"items": ["Pobieranie rozkładu GTFS w tle...", "-", "-", "-"]}), 200

    pociagi = []
    for p in dane.get("odjazdy", []):
        try:
            h, m = map(int, p["godzina"].split(":"))
            if h * 60 + m >= teraz_minuta:
                pociagi.append(f"{p['godzina']} -> {p['kierunek']} ({p['stacja']})")
            if len(pociagi) == 4:
                break
        except ValueError:
            continue

    while len(pociagi) < 4:
        pociagi.append("-")

    return jsonify({"items": pociagi}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
