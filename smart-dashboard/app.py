#.    docker run -p 8080:5000 smart-dashboard
#.    http://127.0.0.1:8080
#.    docker build -t smart-dashboard .




# Flask  - do strony 
# render_template - do wczytania index.html i wstawienia  danych
from flask import Flask, render_template

#from energa_outages_api import EnergaOutagesClientSync


import json

import os


import requests # requests - do pobierania danych z internetu 

import subprocess



from datetime import datetime

# Tworzymy aplikację 
app = Flask(__name__)


@app.route('/') # jak glowne wejscie na strone to 
def index():
    



    # ----------    POGODA  POCZATEK   ----------


















    try:
        url_dane_pogody_meteo = "https://api.open-meteo.com/v1/forecast?latitude=54.341&longitude=18.362&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m&timezone=Europe%2FWarsaw" 
        dane_pogody_meteo = requests.get(url_dane_pogody_meteo, timeout=10).json()

        temperatura = round(dane_pogody_meteo["current"]["temperature_2m"])
        cisnienie = round(dane_pogody_meteo["current"]["surface_pressure"])
        godzina = dane_pogody_meteo["current"]["time"].split("T")[1]

    except:
        temperatura = "brak sieci"
        cisnienie = "brak sieci"
        godzina = "brak sieci"

   


    # dane_pogody_imgw = requests.get("https://danepubliczne.imgw.pl/api/data/synop/station/gdansk").json()


    # temperatura = round(float(dane_pogody_imgw["temperatura"]))
    # cisnienie = dane_pogody_imgw["cisnienie"]
    # wilgotnosc = round(float(dane_pogody_imgw["wilgotnosc_wzgledna"]))
    # wiatr = dane_pogody_imgw["predkosc_wiatru"]
    # godzina = dane_pogody_imgw["godzina_pomiaru"]





























    # ----------    POGODA    KONIEC     ----------




    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################




    # ----------    KALENDARZ    POCZATEK     ----------



    LISTA_KALENDARZY = [
        "https://p168-caldav.icloud.com/published/2/MTE3NzcwMzEzMzAxMTc3N9hV8n-S-_35QYxvu6MN0QABMHOtT3P_bPjFa_moqgmOclzTJQoe7STET0ADGMntt8B7Bbopo8D4aQZjnM782XQ",
        "https://p168-caldav.icloud.com/published/2/MTE3NzcwMzEzMzAxMTc3N9hV8n-S-_35QYxvu6MN0QCSQqfoFuhS9qvqwq3NQXOYK_1yLCJvA2M0UwfvV3jSc7ylMy0b3-RVvgpRNKOxXao",
        "https://p168-caldav.icloud.com/published/2/MTE3NzcwMzEzMzAxMTc3N9hV8n-S-_35QYxvu6MN0QBBzUBjhJ9IcSLzXZX4rs2L4nMjqCgnxsTY54VYGb5hsYADybFOEGz-Nc6RC4Vg5G0"
    ]



    wydarzenia_z_kalendarza = []    

    
    dzis_jest_data = datetime.now().strftime("%Y%m%d")

    for link in LISTA_KALENDARZY:
        try:
            tekst = requests.get(link, timeout=10).text
        except:
            continue

        ostatnia_zapisana_data = "" 


        for linia in tekst.splitlines(): # po kazdej lini 


            if linia.startswith("DTSTART"): # bierzemy date wydarzenia 
                    ostatnia_zapisana_data = linia.split(":")[1][:8] #RRRRMMDD                       

            
        
            if linia.startswith("SUMMARY:"):  # każde nazwa wydarzenia_z_kalendarza zaczyna się od słowa "SUMMARY:"
                nazwa = linia.replace("SUMMARY:", "") #wycianym ten napis
                
                if ostatnia_zapisana_data >= dzis_jest_data:
                
                    ladna_data = f"{ ostatnia_zapisana_data [6:8]}.{ ostatnia_zapisana_data [4:6]}" #ladniejsze formowanie daty
                    wydarzenia_z_kalendarza.append(f"{ladna_data} - {nazwa}")

    wydarzenia_z_kalendarza.sort()

    # jak mniej niz 4 wydarzenia dajemy myslnik
    while len(wydarzenia_z_kalendarza) < 4:
        wydarzenia_z_kalendarza.append("-")















    # ----------    KALENDARZ    KONIEC     ----------



    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################



    # ----------    POCIAGI  POCZATEK   ----------






    teraz = datetime.now()                                                
    plik = "odjazdy_zukowo.json"                                      

    try:                                                                  
        with open(plik, encoding="utf-8") as f:                            
            dane = json.load(f)                                            
    except:                                                                
        dane = {}                                                          

   
    if dane.get("data") != teraz.strftime("%Y%m%d"):
        subprocess.Popen(["python3", "wycinanie_rozkladu_pociagi.py"]) # uruchamiamy  skrypt na rozkald, popoen nie czeka na zaskonczenie
        try:                                                               
            with open(plik, encoding="utf-8") as f: # otwieramy plik jeszcze raz
                dane = json.load(f) # wczytujemy do zmiennej "dane"  nowo pobrane pociągi
        except:                                                            
            dane = {}                                                     

    pociagi = [] # tekst do wyswietlenia
    teraz_jest_godzina = teraz.strftime("%H:%M") # aktualna godzina 
    teraz_minuta = teraz.hour * 60 + teraz.minute # aktualna godzina w minutach od północy


    for p in dane.get("odjazdy", []):  # przechodzimy po kolei przez każdy pociąg z pliku 
        # Bierzemy tylko te pociągi gdzie godzina odjazdu jest >= teraz
        if p["godzina"] >= teraz_jest_godzina:                                     
            h, m = map(int, p["godzina"].split(":"))                       
            odjazd_minuta = h * 60 + m              

            if odjazd_minuta >= teraz_minuta:
                pociagi.append(f" {p['godzina']} -> {p['kierunek']} ({p['stacja']})")                         
            


        if len(pociagi) == 4:                                         
            break                                                      

    while len(pociagi) < 4:                                                
        pociagi.append("-")                                                




    # ----------    POCIAGI  KONIEC   ----------





    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################













    # ----------    PRAd  POCZATEK   ----------














# def sprawdz_prad_energa():
#     try:
#         with EnergaOutagesClientSync() as client:
#             aktywne = client.check_location(lat=54.341, lon=18.362, margin_m=500)
#             if aktywne:
#                 return f" {aktywne.shutdown.message[:60]}..."
            
#             planowane = client.check_location_planned(lat=54.341, lon=18.362, margin_m=500, window_hours=168)
#             if planowane:
#                 najblizsze = planowane[0]
#                 start = najblizsze.shutdown.start_date.strftime("%d.%m %H:%M")
#                 return f" Planowane wyłączenie: {start}"
                
#         return "Brak planowanych wyłączeń prądu"
#     except Exception as e:
#         return "Brak danych o sieci"



    wylaczenia = []

    

    try:
        url_energa = "https://energa-operator.pl/__system/api/document/EXTERNAL_DOCUMENT-305647"
        odpowiedz = requests.get(url_energa, timeout=10).json()
        
        payload = odpowiedz.get("document", {}).get("payload", {})
        if isinstance(payload, list):
            lista_wylaczen = payload  
        else:
            lista_wylaczen = payload.get("outages", payload.get("shutdowns", payload.get("data", [])))
        
        for w in lista_wylaczen:
            wiadomosc = w.get("message", "")
            
            if "Żukowo" in wiadomosc or "Żukowie" in wiadomosc:
                data_od = w.get("startDate", "")[:10] 
                
                if data_od:
                    ladna_data = f"{data_od[8:10]}.{data_od[5:7]}" # DD.MM
                    krotka_wiadomosc = (wiadomosc[:50] + '...') if len(wiadomosc) > 50 else wiadomosc
                    wylaczenia.append(f"{ladna_data}: {krotka_wiadomosc}")

    except Exception as e:
        print("Błąd wyłączeń prądu:", e)

    if not wylaczenia:
        wylaczenia.append("Brak planowanych wyłączeń")

    # Dopełniamy do 4 elementów
    while len(wylaczenia) < 4:
        wylaczenia.append("-")















    # ----------    WYŁĄCZENIA PRĄDU  KONIEC     ----------







    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################
    ###############################################























    
    # ----------    POGODA Z PACZKOMATU  POCZĄTEK   ----------
    
    
    inpost_pogoda = ["Brak danych"]
    inpost_kod = "ZUK03M"  
    
    try:
        url_inpost = f"https://api-pl-points.easypack24.net/v1/points/{inpost_kod}/air-sensors"
        odpowiedz = requests.get(url_inpost, timeout=10)
        
        if odpowiedz.status_code == 200:
            dane_json = odpowiedz.json()
            values = dane_json.get("current", {}).get("values", [])
            
            temp, wilg, cisn, pm25, pm10 = "-", "-", "-", "-", "-"
            
            for item in values:
                name = item.get("name")
                val = item.get("value")
                
                if val is not None:
                    val_z = round(float(val), 1)
                else:
                    continue
                    
                if name == "TEMPERATURE":
                    temp = val_z
                elif name == "HUMIDITY":
                    wilg = val_z
                elif name == "PRESSURE":
                    cisn = int(round(float(val), 0))
                elif name == "PM25":
                    pm25 = val_z
                elif name == "PM10":
                    pm10 = val_z
                    
            if temp != "-":
                # Przygotowujemy ładną listę linii do wyświetlenia w kafelku
                inpost_pogoda = [
                    f"Temp: {temp}°C | Wilg: {wilg}%",
                    f"Ciśnienie: {cisn} hPa",
                    f"PM2.5: {pm25} µg/m³",
                    f"PM10: {pm10} µg/m³"
                ]
            else:
                inpost_pogoda = ["Paczkomat online (brak czujników)"]
        else:
            inpost_pogoda = ["Brak czujników dla tego paczkomatu"]
            
    except Exception as e:
        print("Błąd pogody z paczkomatu:", e)
        inpost_pogoda = ["Brak danych"]

















    # ----------    POGODA Z PACZKOMATU  KONIEC   ----------











    return render_template('index.html', temp=temperatura, cisnienie=cisnienie, godzina=godzina, kalendarz=wydarzenia_z_kalendarza, pociagi=pociagi, wylaczenia=wylaczenia, inpost_pogoda=inpost_pogoda, inpost_kod=inpost_kod)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)