

# Flask  - do strony 
# render_template - do wczytania index.html i wstawienia  danych
from flask import Flask, render_template



import json

import os


import requests # requests - do pobierania danych z internetu 

import subprocess



from datetime import datetime

# Tworzymy aplikację 
app = Flask(__name__)

LINK_KALENDARZ = "https://p168-caldav.icloud.com/published/2/MTE3NzcwMzEzMzAxMTc3N9hV8n-S-_35QYxvu6MN0QABMHOtT3P_bPjFa_moqgmOclzTJQoe7STET0ADGMntt8B7Bbopo8D4aQZjnM782XQ"

@app.route('/') # jak glowne wejscie na strone to 
def index():
    



    # ----------    POGODA  POCZATEK   ----------


















    try:
        url_dane_pogody_meteo = "https://api.open-meteo.com/v1/forecast?latitude=54.341&longitude=18.362&current=temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m&timezone=Europe%2FWarsaw" 
        dane_pogody_meteo = requests.get(url_dane_pogody_meteo).json()

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



















    tekst_kalendarza = requests.get(LINK_KALENDARZ).text # bierzmy kalendarze jako tekst 
    wydarzenia_z_kalendarza = []
    dzis_jest_data = datetime.now().strftime("%Y%m%d")

    ostatnia_zapisana_data = ""

    
    for linia in tekst_kalendarza.splitlines(): # po kazdej lini 


        if linia.startswith("DTSTART"): # bierzemy date wydarzenia 
                ostatnia_zapisana_data = linia.split(":")[1][:8] #RRRRMMDD                       

        
       
        if linia.startswith("SUMMARY:"):  # każde nazwa wydarzenia_z_kalendarza zaczyna się od słowa "SUMMARY:"
            nazwa = linia.replace("SUMMARY:", "") #wycianym ten napis
            print("Z KALENDARZA:", ostatnia_zapisana_data, nazwa)

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

   
    if dane.get("data") != teraz.strftime("%Y%m%d"):  # czy plik ma dzisiejszą datę
        subprocess.run(["python3", "wycinanie_rozkladu_pociagi.py"]) # uruchamiamy  skrypt na rozkald
        try:                                                               
            with open(plik, encoding="utf-8") as f: # otwieramy plik jeszcze raz
                dane = json.load(f) # wczytujemy do zmiennej "dane"  nowo pobrane pociągi
        except:                                                            
            dane = {}                                                     

    pociagi = [] # tekst do wyswietlenia
    teraz_jest_godzina = teraz.strftime("%H:%M") # aktualna godzina 
    teraz_min = teraz.hour * 60 + teraz.minute # aktualna godzina w minutach od północy


    for p in dane.get("odjazdy", []):  # przechodzimy po kolei przez każdy pociąg z pliku 
        # Bierzemy tylko te pociągi gdzie godzina odjazdu jest >= teraz
        if p["godzina"] >= teraz_jest_godzina:                                     
            h, m = map(int, p["godzina"].split(":"))                       
            odjazd_min = h * 60 + m                                        
            
            pociagi.append(f" {p['godzina']} -> {p['kierunek']} ({p['stacja']})")


        if len(pociagi) == 4:                                         
            break                                                      

    while len(pociagi) < 4:                                                
        pociagi.append("-")                                                




    # ----------    POCIAGI  KONIEC   ----------




















    # ----------    POCIAGI  KONIEC   ----------




    return render_template('index.html', temp=temperatura, cisnienie=cisnienie, godzina=godzina, kalendarz=wydarzenia_z_kalendarza, pociagi=pociagi)

if __name__ == '__main__': #Uruchamiamy serwer lokalny na porcie 500
    app.run(debug=True, port=5000)