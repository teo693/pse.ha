# main.py
import asyncio
import aiohttp
import json
import logging
import os
import sys
from datetime import datetime
from threading import Thread

logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

SUPERVISOR_TOKEN = os.environ.get('SUPERVISOR_TOKEN')
API_URL = "https://api.raporty.pse.pl/api/pdgsz"

async def get_pse_status():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"{API_URL}?$filter=doba eq '{today}'"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                current_hour = datetime.now().strftime("%H:00")
                
                for item in data.get('value', []):
                    if item.get('udtczas', '').startswith(current_hour):
                        return item.get('znacznik', -1)
    return -1

async def update_ha_sensor(status):
    headers = {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "Content-Type": "application/json",
    }
    
    sensor_data = {
        "state": status,
        "attributes": {
            "status_description": {
                0: "ZALECANE UŻYTKOWANIE",
                1: "NORMALNE UŻYTKOWANIE",
                2: "ZALECANE OSZCZĘDZANIE",
                3: "WYMAGANE OGRANICZANIE"
            }.get(status, "NIEZNANY STATUS")
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://supervisor/core/api/states/sensor.pse_energy_status",
            headers=headers,
            json=sensor_data
        ) as response:
            if response.status != 201:
                _LOGGER.error("Failed to update HA sensor: %s", await response.text())

async def main_loop():
    while True:
        try:
            with open('/data/options.json') as options_file:
                options = json.load(options_file)
            scan_interval = options.get('scan_interval', 300)
            
            status = await get_pse_status()
            if status != -1:
                await update_ha_sensor(status)
            
            await asyncio.sleep(scan_interval)
        except Exception as e:
            _LOGGER.error("Error in main loop: %s", str(e))
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        sys.exit(0)
