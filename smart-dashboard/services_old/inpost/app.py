import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)
LOCKER_CODE = os.getenv("LOCKER_CODE", "ZUK03M")

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/api/inpost")
def get_inpost():
    url = f"https://api-pl-points.easypack24.net/v1/points/{LOCKER_CODE}/air-sensors"
    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code != 200:
            return jsonify({"items": ["Brak czujników dla tego paczkomatu"]}), 200

        values = resp.json().get("current", {}).get("values", [])
        temp, wilg, cisn, pm25, pm10 = "-", "-", "-", "-", "-"

        for item in values:
            name, val = item.get("name"), item.get("value")
            if val is None:
                continue
            if name == "TEMPERATURE":
                temp = round(float(val), 1)
            elif name == "HUMIDITY":
                wilg = round(float(val), 1)
            elif name == "PRESSURE":
                cisn = int(round(float(val), 0))
            elif name == "PM25":
                pm25 = round(float(val), 1)
            elif name == "PM10":
                pm10 = round(float(val), 1)

        if temp != "-":
            items = [
                f"Temp: {temp}°C | Wilg: {wilg}%",
                f"Ciśnienie: {cisn} hPa",
                f"PM2.5: {pm25} µg/m³",
                f"PM10: {pm10} µg/m³"
            ]
        else:
            items = ["Paczkomat online (brak czujników)"]

        return jsonify({"items": items}), 200
    except Exception:
        return jsonify({"items": ["Brak danych"]}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
