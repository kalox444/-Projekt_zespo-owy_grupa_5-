import requests
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/energa")
def get_energa():
    wylaczenia = []
    try:
        url = "https://energa-operator.pl/__system/api/document/EXTERNAL_DOCUMENT-305647"
        odpowiedz = requests.get(url, timeout=10).json()
        payload = odpowiedz.get("document", {}).get("payload", {})

        if isinstance(payload, list):
            lista = payload
        else:
            lista = payload.get("outages", payload.get("shutdowns", payload.get("data", [])))

        for w in lista:
            wiadomosc = w.get("message", "")
            if "Żukowo" in wiadomosc or "Żukowie" in wiadomosc:
                data_od = w.get("startDate", "")[:10]
                if data_od:
                    ladna_data = f"{data_od[8:10]}.{data_od[5:7]}"
                    krotka = (wiadomosc[:50] + "...") if len(wiadomosc) > 50 else wiadomosc
                    wylaczenia.append(f"{ladna_data}: {krotka}")
    except Exception:
        wylaczenia.append("Błąd połączenia z Energa")

    if not wylaczenia:
        wylaczenia.append("Brak planowanych wyłączeń")

    while len(wylaczenia) < 4:
        wylaczenia.append("-")

    return jsonify({"items": wylaczenia[:4]}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
