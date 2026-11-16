import csv, io, json, re, zipfile                  
from datetime import datetime                        
import requests                                      

STRONA = "https://mobilitydatabase.org/feeds/gtfs/mdb-2087"  # adres strony 
STACJE = {"18051": "Żukowo Zachodnie", "257551": "Żukowo"}

teraz = datetime.now()                                
dzisiaj = teraz.strftime("%Y%m%d")                    # dzisiejsza data format GTFS
dni = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]  # nazwy kolumn z calendar w kolejności 0-6
dzien = dni[teraz.weekday()]                          # weekdayzwraca 0 poniedzialek 6 niedziela

try:                                                 
    html = requests.get(STRONA, timeout=150).text      #bierzemy strone jako tekst HTML
    link = re.search(r'https://files\.mobilitydatabase\.org/mdb-2087/[^"]+\.zip', html).group(0)  #  link do ZIP
    zip_data = requests.get(link, timeout=200).content # ściągam ZIP 
    z = zipfile.ZipFile(io.BytesIO(zip_data))         # zip w ram

    def czytaj(nazwa):                             
        try:                                          
            with z.open(nazwa) as f:                  # otwieram plik o "nazwie" w zip
                return list(csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig")))  #każdy wiersz jako {nazwa_kolumny: wartość} + usuwamy smieci na poczatku
        except KeyError:                              
            return []                                

    aktywne = set()                                   
    for r in czytaj("calendar_dates.txt"):           
        if r.get("date") == dzisiaj and r.get("exception_type") == "1":
            aktywne.add(r["service_id"])

    kierunki = {}                                     
    for r in czytaj("trips.txt"):                     #  każdy kurs z trips
        if r["service_id"] in aktywne:                # jeśli kurs jest aktywny
            kierunki[r["trip_id"]] = r["trip_headsign"]  #zapisujemy  trip_id -> kierunek 

    odjazdy = set()                                   
    for r in czytaj("stop_times.txt"):                # wszystkie odjazdy 
        if r["trip_id"] not in kierunki:              # jeśli nie z dzisiejszego rozkładu
            continue                                  # pomijamy
        if r["stop_id"] not in STACJE:                # jjak inna stacja
            continue                                  # pomijamy
        godzina = r["departure_time"][:5]             # godzina w normalnej formie
        kierunek = kierunki[r["trip_id"]]             # dokąd
        stacja = STACJE[r["stop_id"]]                 # nazwa stacji w normalnej formie
        odjazdy.add((godzina, kierunek, stacja))      # dodajęmy krotke

    odjazdy = sorted(odjazdy)                         # sortowanie


    lista = []                                        
    for g, k, s in odjazdy:                           # dla każdej krotki z posortowanych odjazdów
        lista.append({"godzina": g, "kierunek": k, "stacja": s})  # słownik z 3 polami

    with open("odjazdy_zukowo.json", "w", encoding="utf-8") as f:  
        json.dump({"data": dzisiaj, "odjazdy": lista}, f, ensure_ascii=False, indent=2)  

    print("OK,", len(odjazdy), "pociągów")            # log

except Exception as e:                                # jak blad
    print("Nie udało się odświeżyć", e)             