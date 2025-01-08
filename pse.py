import requests
from datetime import datetime
import json

def pobierz_ceny_ogr():
    url = "https://api.raporty.pse.pl/api/pdgsz"
    
    dzis = datetime.now().strftime("%Y-%m-%d")
    
    # Nagłówki zgodne ze standardami API
    headers = {
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        dane = response.json()
        print(f"Pobrano dane dla dnia: {dzis}")
        print(json.dumps(dane, indent=2, ensure_ascii=False))
        
        # Opcjonalnie zapisz dane do pliku
        with open('ceny_ogr.json', 'w', encoding='utf-8') as f:
            json.dump(dane, f, ensure_ascii=False, indent=2)
        
        return dane
        
    except requests.exceptions.RequestException as e:
        print(f"Wystąpił błąd podczas pobierania danych: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Szczegóły odpowiedzi: {e.response.text}")
        return None

if __name__ == "__main__":
    print("Rozpoczynam pobieranie danych OGR-D1...")
    pobierz_ceny_ogr()
