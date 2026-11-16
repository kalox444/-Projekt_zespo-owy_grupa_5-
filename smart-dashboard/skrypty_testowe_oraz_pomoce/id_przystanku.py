import io
import zipfile
import csv
import requests
import re

STRONA = "https://mobilitydatabase.org/feeds/gtfs/mdb-2087"
html = requests.get(STRONA, timeout=15).text
link = re.search(r'https://files\.mobilitydatabase\.org/mdb-2087/[^"]+\.zip', html).group(0)
z = zipfile.ZipFile(io.BytesIO(requests.get(link).content))

with z.open("stops.txt") as f:
    for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig")):
        if "żukowo" in r.get("stop_name", "").lower():
            print(f"ID: {r['stop_id']} -> Nazwa: {r['stop_name']}")