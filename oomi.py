import requests
import re
from datetime import datetime, timezone
import pytz
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

class OomiClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.verificationtoken = None

    def login(self) -> None:
        """ Login to Oomi online service """

        login_url_1 = 'https://online.oomi.fi/eServices/Online/IndexNoAuth'
        login_url_2 = 'https://online.oomi.fi/eServices/Online/Login'
        response_1 = self.session.get(login_url_1)

        # get verification token from the noauth page
        verification_token_pattern = r'(?<=<input name="__RequestVerificationToken" type="hidden" value=")([\w-]+)(?=" />)'
        match = re.search(verification_token_pattern, response_1.text)
        if not match:
            logger.error("No verification token found")    
            raise ValueError("No verification token found")
        
        # Do the actual login
        verification_token = match.group(1)
        logger.info(f"login as {self.username}")
        login_response = self.session.post(
            login_url_2,
            data={
                "UserName": self.username,
                "Password": self.password,
                "__RequestVerificationToken": verification_token,
            }
        )
        
        if login_response.status_code != 200:
            logger.error("Login failed, status code: {login_response.status_code}")
            raise ValueError("Login failed")

        # Check if username is found from the response.text in format userName = "username";
        if f'userName = "{self.username}";' not in login_response.text:
            logger.error("Login failed, Username not found")
            raise ValueError("Login failed")
        logger.info("Login successful")
        self.verificationtoken = verification_token

    def get_consumption_data(self, meteringpoint: str, start_date: datetime = None, end_date: datetime = None) -> dict:
        """ 
        Get consumption/produciton data from Oomi online service.  

        Parameters:
        meteringpoint: str: the metering point code
        start_date: datetime: the start date of the data. If None, return all data
        end_date: datetime: the end date of the data. If None, return all data
        """

        if not self.verificationtoken:
            raise ValueError("Not logged in")

        logger.info(f"Getting data for meteringpoint {meteringpoint}")
        consumption_url = f"https://online.oomi.fi/Reporting/CustomerConsumption?meteringPointCode={meteringpoint}&showOldContracts=null"
        response = self.session.get(consumption_url)
        if response.status_code != 200:
            raise ValueError("Failed to get consumption data")
        
        # parse the data. This is a bit tricky, because the data is not in a nice format...
        # the actual data is in a javascript object in the html
        pattern_model = r'var model = ({.+});'
        match = re.search(pattern_model, response.text)
        if not match:
            raise ValueError("No data found")
        
        data = match.group(1)

        # there is a lot of stuff in the model, but we are only interested in the consumption data, which is the first Data-array
        pattern_data = r"Data\":\[(\[[\[\],\.\d]+\])\]"  
        match = re.search(pattern_data, data)
        if not match:
            raise ValueError("No data found")
        
        consumption_data = match.group(1)

        #write the data to a file
        with open("consumption_data_raw.txt", "w") as f:
            f.write(consumption_data)

        # the data is a stringin the format "[timestamp, consumption],[timestamp, consumption] ..."
        # timestamps are Europe/Helsinki timezone, but wrong by offset hours. 
        # we will convert it to a list of tuples

        pattern_measurements = r"\[(\d+),([\d.]+)\]"
        measurement_tuples = re.findall(pattern_measurements, consumption_data)

        # convert the timestamps to datetime objects
        tz_helsinki = pytz.timezone('Europe/Helsinki')
        measurements = [(datetime.fromtimestamp(int(ts) / 1000, tz=tz_helsinki), float(cons)) for ts, cons in measurement_tuples]

        # timetsamps are for some reason skewed by offset hours, so we need to fix that
        # this is a bit hacky, but it seem to be the way to get timestamps work
        measurements = [((ts - ts.utcoffset()).astimezone(pytz.utc), cons) for ts, cons in measurements]
        
        # filter the data based on the start and end dates
        if start_date:
            start_date = start_date.astimezone(tz_helsinki)
            measurements = [m for m in measurements if m[0] > start_date]

        if end_date:
            end_date = end_date.astimezone(tz_helsinki)
            measurements = [m for m in measurements if m[0] <= end_date]
        
        return measurements

def main():
    from dotenv import load_dotenv
    username = os.getenv("OOMI_USERNAME")
    password = os.getenv("OOMI_PASSWORD")
    meteringpoint_consumption = os.getenv("OOMI_METERINGPOINT_CONSUMPTION")
    meteringpoint_production = os.getenv("OOMI_METERINGPOINT_PRODUCTION")

    client = OomiClient(username, password)
    client.login()

    data_production = client.get_consumption_data(meteringpoint_production)
    df_prod = pd.DataFrame(data_production, columns=["timestamp", "production"])
    logger.info(f"Production data:\n{df_prod}")

    # get consumption data
    data_consumption = client.get_consumption_data(meteringpoint_consumption)
    df_cons = pd.DataFrame(data_consumption, columns=["timestamp", "consumption"])
    print(f"Consumption data:\n{df_cons}")


if __name__ == "__main__":
    main()








