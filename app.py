import json
import time
import requests
from db import PostgresDB 
from datetime import datetime
import pytz
from omaoomi import get_production_data, get_consumption_data, get_spot_prices, get_oomi_data
import logging
import pandas as pd
import os
import schedule
import asyncio

# schedule to run every 6 hours
INTERVAL_SHOURS = 6
OOMI_USERNAME = os.getenv("OOMI_USERNAME")
OOMI_PASSWORD = os.getenv("OOMI_PASSWORD")

#init logger
# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s : %(message)s',
)

logger = logging.getLogger(__name__)

db = PostgresDB()

async def run_syncs() -> None:
    try:
        logger.info("Running syncs")
        # process_oomi_data()
        # process_spot_data()

        # scrape data from oma.oomi.fi
        await get_oomi_data()
        data_consumption = get_consumption_data()
        if data_consumption is not None:
            db.upsert_consumptions(data_consumption)
        else:
            logger.info("No new consumption data from oma.oomi.fi")

        data_production = get_production_data()
        if data_production is not None:
            db.upsert_productions(data_production)
        else:
            logger.info("No new production data from oma.oomi.fi")

        # get today's spot prices
        spot_prices = get_spot_prices() 
        if spot_prices is not None:
            db.upsert_spotprices(spot_prices)
        else:
            logger.info("No new spot prices from oma.oomi.fi")

        logger.info(f"Syncs done, sleeping for {INTERVAL_SHOURS} hours") 
    except Exception as e:
        logger.error(f"Error running syncs: {e}")


def check_config() -> bool:
    required_vars = [
        "OOMI_USERNAME", 
        "OOMI_PASSWORD", 
        "POSTGRES_SERVER",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB"
        ]
    config_ok = True
    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"Missing configuration: {var}")
            config_ok = False
    return config_ok

if not check_config():
    logger.error("Missing configuration. Exiting.")
    exit(1)


logger.info(f'Configuring to run datasyncs every {INTERVAL_SHOURS} hour') 
schedule.every(INTERVAL_SHOURS).hours.do(lambda: asyncio.run(run_syncs()))
asyncio.run(run_syncs())
while True:
    schedule.run_pending()
    time.sleep(1)

