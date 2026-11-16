import logging # bibliotek do logow/bledow
import requests #biblioteka do zapytan http                                      
from flask import Flask # flask serwer,           
from flask import jsonify #  jsonify zeby json -> na slownik pythona  i potem znowu spakowc slownik -> json   
app = Flask(__name__)  #tworzymy aplikacje flask                          
logging.basicConfig(level=logging.INFO)   # ustawienie zeby widziec WSZYSTKIE poziomy bledow w terminalu

@app.route("/api/weather") #tutaj wystawiamy lokalnie jsona juz przetworzonego - endpoint
def get_weather():                                    # Funkcja, która uruchomi się, gdy ktoś wejdzie na ten adres
    url = "https://api.open-meteo.com/v1/forecast?latitude=54.341&longitude=18.362&current=temperature_2m,surface_pressure&timezone=Europe%2FWarsaw" # Zapisuje długi adres do API pogodowego w zmiennej
    try:                                              # Zaczyna blok "spróbuj" (jeśli coś w środku się zepsuje, przejdziemy do "except")
        r = requests.get(url, timeout=8)              # Wysyła zapytanie do serwera pogodowego, czeka maksymalnie 8 sekund
        r.raise_for_status()                          # Błąd HTTP = wyjątek (jeśli serwer odpowie np. 404 lub 500, wywala błąd)
        c = r.json()["current"]                       # Zmienia odpowiedź z serwera na słownik i wyciąga tylko sekcję "current"
        return jsonify({                              # Zwraca dane do użytkownika jako JSON
            "temp": round(c["temperature_2m"]),       # Wyciąga temperaturę i zaokrągla do pełnej liczby (np. 3.4 -> 3)
            "cisnienie": round(c["surface_pressure"]),# Wyciąga ciśnienie i zaokrągla do pełnej liczby
            "godzina": c["time"].split("T")[1],       # Bierze czas (np. "2026-11-16T12:00"), dzieli na "T" i bierze godzinę ("12:00")
        })                                            # Zamyka słownik i jsonify
    except Exception:                                 # Jeśli cokolwiek w "try" się wysypie (brak neta, błąd danych)
        app.logger.exception("Pogoda: nie udało się pobrać danych")  # Zapisuje pełny, szczegółowy błąd do logów w konsoli
        return jsonify({"temp": None, "cisnienie": None, "godzina": None}), 502 # Zwraca pusty JSON (None) i kod błędu 502 (Bad Gateway)