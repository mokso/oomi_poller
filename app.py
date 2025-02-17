import json
import time
import requests
from db import PostgresDB 
from datetime import datetime
import pytz
from oomi import OomiClient
import logging
import pandas as pd
import os
import schedule

# schedule to run every 6 hours
INTERVAL_SHOURS = 6
OOMI_USERNAME = os.getenv("OOMI_USERNAME")
OOMI_PASSWORD = os.getenv("OOMI_PASSWORD")
OOMI_METERINGPOINT_CONSUMPTION = os.getenv("OOMI_METERINGPOINT_CONSUMPTION")
OOMI_METERINGPOINT_PRODUCTION = os.getenv("OOMI_METERINGPOINT_PRODUCTION")

#init logger
# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s : %(message)s',
)

logger = logging.getLogger(__name__)


db = PostgresDB()
oomi = OomiClient(OOMI_USERNAME, OOMI_PASSWORD)

def process_oomi_data() -> None:
    """Process Oomi data and insert to database"""
    oomi.login()

    # get new consumption data
    latest_date_consumption = db.get_latest_consumption_date()
    logger.info(f"Latest consumption date: {latest_date_consumption}")
    data_consumption = oomi.get_consumption_data(OOMI_METERINGPOINT_CONSUMPTION, start_date=latest_date_consumption)
    if data_consumption:
        db.upsert_consumptions(data_consumption)
    else:
        logger.info("No new consumption data")

    # get new production data
    latest_date_production = db.get_latest_production_date()
    data_production = oomi.get_consumption_data(OOMI_METERINGPOINT_PRODUCTION, start_date=latest_date_production)
    if data_production:
        db.upsert_productions(data_production)
    else:
        logger.info("No new production data")


def get_today_spotprices() -> list:
    """Get today's spot prices from spot-hinta.fi API
    
    Returns:
        list: A list of dicts with the data (datetime, price)
    """

    url = "https://api.spot-hinta.fi/Today"
    response = requests.get(url)
    data = json.loads(response.text)
    data = [{"time": datetime.fromisoformat(item["DateTime"]), "price": item["PriceWithTax"]} for item in data]
    return data

def process_spot_data() -> None:
    """ Process spot data and insert to database """
    try:
        latest_spot = db.get_latest_spotprices()
        logger.info(f'Latest spot price in db: {latest_spot}')
    except Exception as e:
        logger.error(f"Error getting latest spot price: {e}")
        latest_spot = None

    if latest_spot and latest_spot > datetime.now(pytz.utc):
        logger.info("No new spot prices")
        return

    today_spot_prices = get_today_spotprices() 
    db.upsert_spotprices(today_spot_prices)


def run_syncs() -> None:
    try:
        logger.info("Running syncs")
        process_oomi_data()
        process_spot_data()
        logger.info(f"Syncs done, sleeping for {INTERVAL_SHOURS} hours") 
    except Exception as e:
        logger.error(f"Error running syncs: {e}")


def check_config() -> bool:
    required_vars = [
        "OOMI_USERNAME", 
        "OOMI_PASSWORD", 
        "OOMI_METERINGPOINT_CONSUMPTION", 
        "OOMI_METERINGPOINT_PRODUCTION",
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
schedule.every(INTERVAL_SHOURS).hours.do(run_syncs)
run_syncs()
while True:
    schedule.run_pending()
    time.sleep(1)

