import asyncio
import aiohttp
import json
import logging
import os
from datetime import datetime, timedelta

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_URL = "https://api.raporty.pse.pl/api/pdgsz"
HA_API_URL = "http://supervisor/core/api/states/sensor.pse_energy_status"

async def get_pse_status():
    try:
        # Pobieramy dane dla wczoraj i dziś, aby mieć pewność że coś znajdziemy
        dates = [
            (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y-%m-%d")
        ]
        
        for today in dates:
            url = f"{API_URL}?$filter=doba eq '{today}'"
            logger.info(f"Fetching data from PSE API for date: {today}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    logger.info(f"PSE API response status: {response.status}")
                    if response.status == 200:
                        data = await response.json()
                        if not data.get('value'):
                            continue
                            
                        current_hour = datetime.now().strftime("%H:00")
                        logger.info(f"Looking for data for hour: {current_hour}")
                        
                        for item in data.get('value', []):
                            if item.get('udtczas', '').startswith(current_hour):
                                status = item.get('znacznik', -1)
                                logger.info(f"Found status: {status}")
                                return status
                        
                        # Jeśli nie znaleziono dla aktualnej godziny, weź ostatni dostępny
                        if data.get('value'):
                            last_item = data['value'][-1]
                            status = last_item.get('znacznik', -1)
                            logger.info(f"Using last available status: {status}")
                            return status
    except Exception as e:
        logger.error(f"Error in get_pse_status: {str(e)}")
    return -1

async def update_ha_sensor(status):
    try:
        # Próbujemy pobrać token z różnych możliwych lokalizacji
        token = os.environ.get('SUPERVISOR_TOKEN')
        if not token:
            try:
                with open('/data/auth.txt', 'r') as f:
                    token = f.read().strip()
            except:
                try:
                    with open('/var/run/secrets/supervisor_token', 'r') as f:
                        token = f.read().strip()
                except:
                    pass
        
        if not token:
            logger.error("No supervisor token found in any location")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        status_descriptions = {
            0: "ZALECANE UŻYTKOWANIE",
            1: "NORMALNE UŻYTKOWANIE",
            2: "ZALECANE OSZCZĘDZANIE",
            3: "WYMAGANE OGRANICZANIE",
            -1: "BRAK DANYCH"
        }

        sensor_data = {
            "state": str(status),
            "attributes": {
                "friendly_name": "PSE Energy Status",
                "status_description": status_descriptions.get(status, "NIEZNANY STATUS"),
                "icon": "mdi:transmission-tower"
            }
        }

        logger.info(f"Updating HA sensor with data: {sensor_data}")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                HA_API_URL,
                headers=headers,
                json=sensor_data
            ) as response:
                if response.status == 201:
                    logger.info("Successfully updated HA sensor")
                else:
                    text = await response.text()
                    logger.error(f"Failed to update HA sensor. Status: {response.status}, Response: {text}")
    except Exception as e:
        logger.error(f"Error in update_ha_sensor: {str(e)}")

async def main():
    logger.info("Starting PSE Energy Status addon")
    while True:
        try:
            with open('/data/options.json') as options_file:
                options = json.load(options_file)
                scan_interval = int(options.get('scan_interval', 300))
                logger.info(f"Scan interval set to {scan_interval} seconds")
            
            status = await get_pse_status()
            logger.info(f"Got PSE status: {status}")
            await update_ha_sensor(status)
            
            logger.info(f"Waiting {scan_interval} seconds before next update")
            await asyncio.sleep(scan_interval)
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        logger.info("Initializing PSE Energy Status addon")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Addon stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
