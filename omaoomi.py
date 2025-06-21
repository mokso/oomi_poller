from playwright.async_api import async_playwright
import pandas as pd
import asyncio
import os
import logging


# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s : %(message)s',
)

logger = logging.getLogger(__name__)

CONS_FILE = 'data/consumption.xlsx'
PROD_FILE = 'data/production.xlsx'
LOGINPAGE = 'https://www.oma.oomi.fi/s/login/?language=fi'
# TODO: get credentials from env vars
USERNAME =  os.getenv("OOMI_USERNAME")
PASSWORD = os.getenv("OOMI_PASSWORD")

async def main():
    await get_oomi_data()


def get_consumption_data():
    if not os.path.exists(CONS_FILE):
        print(f"Consumption data file {CONS_FILE} does not exist.")
        return None
    df = pd.read_excel(CONS_FILE)
    # remove 'undefined' consumption rows
    df = df[df['consumption'] != 'undefined']
    # 'start' and 'end' columns are datetime strings in EET, convert them to datetime objects
    df['start'] = pd.to_datetime(df['start'], format='%d.%m.%Y %H:%M').dt.tz_localize('Europe/Helsinki')

    #rename columns to 'time' and 'value'
    df.rename(columns={'start': 'time', 'consumption': 'value'}, inplace=True)
    #drop all other columns
    df = df[['time', 'value']]

    return df

def get_production_data():
    if not os.path.exists(PROD_FILE):
        print(f"Production data file {PROD_FILE} does not exist.")
        return None
    
    df = pd.read_excel(PROD_FILE)
    # remove 'undefined' production rows
    df = df[df['production'] != 'undefined']
    # 'start' and 'end' columns are datetime strings in EET, convert them to datetime objects
    df['start'] = pd.to_datetime(df['start'], format='%d.%m.%Y %H:%M').dt.tz_localize('Europe/Helsinki')
    #rename columns to 'time' and 'value'
    df.rename(columns={'start': 'time', 'production': 'value'}, inplace=True)
    #drop all other columns
    df = df[['time', 'value']]

    return df

def get_spot_prices():
    if not os.path.exists(CONS_FILE):
        print(f"Consumption data file {CONS_FILE} does not exist.")
        return None
    df = pd.read_excel(CONS_FILE)
    # remove 'undefined' consumption rows
    df = df[df['consumption'] != 'undefined']
    # 'start' and 'end' columns are datetime strings in EET, convert them to datetime objects
    df['start'] = pd.to_datetime(df['start'], format='%d.%m.%Y %H:%M').dt.tz_localize('Europe/Helsinki')

    #rename columns to 'time' and 'value'
    df.rename(columns={'start': 'time', 'spotPrice': 'price'}, inplace=True)

    # ensure price is numeric, replacing commas with dots
    df['price'] = df['price'].astype(str).str.replace(',', '.').astype(float)

    #price is in cent/kWh, convert to euro/kWh
    df['price'] = df['price'] / 100.0

    #drop all other columns
    df = df[['time', 'price']]
    return df




async def get_oomi_data():
    if not os.path.exists('data'):
        logging.info(f"Creating data directory...")
        os.makedirs('data')

    # Start Playwright and open a browser
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        logging.info(f"Navigating to {LOGINPAGE}")
        await page.goto(LOGINPAGE)
        await page.get_by_role('textbox', name='*Sähköposti').click()
        await page.get_by_role('textbox', name='*Sähköposti').fill(USERNAME)
        await page.get_by_role('textbox', name='*Salasana').click()
        await page.get_by_role('textbox', name='*Salasana').fill(PASSWORD)
        logging.info(f"Logging ins as {USERNAME}")
        await page.get_by_role('button', name='Kirjaudu sisään').click()


        await page.get_by_role('menuitem', name='Kulutus').click()
        # add extra wait to ensure the page is fully loaded
        await asyncio.sleep(5)

        await page.wait_for_selector("text=Vuosi", state="visible")
        await page.get_by_text('Vuosi').click()

        logging.info("Downloading consumption data...")

        async with page.expect_download() as download_info:            
            await page.get_by_text('Lataa (.xls)').click()
        download_cons = await download_info.value

        # Save the file
        await download_cons.save_as(CONS_FILE)
        logger.info(f"Consumption data saved to {CONS_FILE}")

        # Navigate to production data
        await page.get_by_role('main').click()
        await page.get_by_role('menuitem', name='Enemmän').click()
        await page.get_by_role('menuitem', name='Tuotanto').click()

        # add extra wait to ensure the page is fully loaded
        await asyncio.sleep(5)

        await page.wait_for_selector("text=Vuosi", state="visible")
        await page.get_by_text('Vuosi').click()

        logging.info("Downloading production data...")
        async with page.expect_download() as download1_info:
            await page.get_by_text('Lataa (.xls)').click()
        download_prod = await download1_info.value

        # Save the file
        await download_prod.save_as(PROD_FILE)
        logger.info(f"Production data saved to {PROD_FILE}")

        # Close the browser
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())