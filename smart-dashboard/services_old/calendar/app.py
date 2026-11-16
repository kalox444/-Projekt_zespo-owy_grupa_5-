import os
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
from flask import Flask, jsonify

app = Flask(__name__)
TZ = ZoneInfo("Europe/Warsaw")


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/calendar")
def get_calendar():
    raw_urls = os.getenv("CALENDAR_URLS", "")
    linki = [u.strip() for u in raw_urls.split(",") if u.strip()]

    wydarzenia = []
    dzis = datetime.now(TZ).strftime("%Y%m%d")

    for link in linki:
        try:
            tekst = requests.get(link, timeout=10).text
        except Exception:
            continue

        ostatnia_data = ""
        for linia in tekst.splitlines():
            if linia.startswith("DTSTART"):
                ostatnia_data = linia.split(":")[1][:8]
            elif linia.startswith("SUMMARY:"):
                nazwa = linia.replace("SUMMARY:", "")
                if ostatnia_data >= dzis:
                    ladna_data = f"{ostatnia_data[6:8]}.{ostatnia_data[4:6]}"
                    wydarzenia.append(f"{ladna_data} - {nazwa}")

    wydarzenia.sort()
    while len(wydarzenia) < 4:
        wydarzenia.append("-")

    return jsonify({"items": wydarzenia[:4]}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
