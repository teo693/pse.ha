## Instalacja
1. Przejdź do "Ustawienia" -> "Dodatki" -> "Dodaj repozytorium"
2. Wklej: `https://github.com/teo693/pse.ha`
3. Kliknij "PSE Energy Status" w liście dodatków
4. Kliknij "INSTALUJ"
5. Włącz dodatek

## Opis znaczników
* 0 - ZALECANE UŻYTKOWANIE 
* 1 - NORMALNE UŻYTKOWANIE
* 2 - ZALECANE OSZCZĘDZANIE
* 3 - WYMAGANE OGRANICZANIE

## Użycie w automatyzacjach
```yaml
automation:
  - alias: "PSE Oszczędzanie"
    trigger:
      - platform: state
        entity_id: sensor.pse_energy_status
    condition:
      - condition: numeric_state
        entity_id: sensor.pse_energy_status
        above: 1
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.moje_urzadzenie
```
