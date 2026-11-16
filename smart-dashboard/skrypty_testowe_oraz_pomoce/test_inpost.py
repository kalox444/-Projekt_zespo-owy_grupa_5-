import requests
import time

kody = [
    "ZUK01N", "ZUK04M", "ZUK02A", "ZUK03M", "ZUK02N", 
    "ZUK01M", "ZUK02BAPP", "ZUK02M", "BORV01M", "ZUK01A", 
    "BOK01B", "GNZ01M", "ZUK01APP", "MWQ01M", "PPW01M", 
    "NIP01M", "PEP01A", "PZY02M", "PZY03M", "CZPL01BAPP", 
    "BRVO01BAPP", "BAN02BAPP", "BVO01M", "PZY01BAPP", "LXZ01B"
]

dziala = []

print(f"Sprawdzam {len(kody)} paczkomatów...\n")

for kod in kody:
    url = f"https://api-pl-points.easypack24.net/v1/points/{kod}/air-sensors"
    
    try:
        odp = requests.get(url, timeout=5)
        
        if odp.status_code == 200:
            dane = odp.json()
            if dane.get("current") and dane.get("current").get("values"):
                print(f" {kod:12} | DZIAŁA (są dane z czujników)")
                dziala.append(kod)
            else:
                print(f" {kod:12} | Odpowiada, ale brak danych (czujnik nie raportuje)")
        elif odp.status_code == 404:
            print(f" {kod:12} | Błąd 404 (brak czujnika lub API wyłączone)")
        else:
            print(f" {kod:12} | Status: {odp.status_code}")
            
    except Exception as e:
        print(f" {kod:12} | Błąd połączenia: {e}")
    
    time.sleep(0.3)

print("\n--- PODSUMOWANIE ---")
if dziala:
    print("Paczkomaty, które zwróciły dane:")
    for d in dziala:
        print(f"- {d}")
else:
    print("Niestety, żaden paczkomat z listy nie zwrócił danych. API InPost Air jest definitywnie wyłączone.")