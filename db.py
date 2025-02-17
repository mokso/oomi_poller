import os
import time
import pandas as pd
from sqlalchemy import MetaData, Table, create_engine
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
import logging

logger = logging.getLogger(name=__name__)

class PostgresDB:
    def __init__(self):
        self.host = os.getenv('POSTGRES_SERVER')
        self.user = os.getenv('POSTGRES_USER')
        self.password = os.getenv('POSTGRES_PASSWORD')
        self.database = os.getenv('POSTGRES_DB')

        logger.info(f"Connecting to database [{self.database}] at [{self.host}] as [{self.user}]")

        # SQLAlchemy connection string
        self.engine = create_engine(f'postgresql://{self.user}:{self.password}@{self.host}/{self.database}')

    def get_latest_consumption_date(self) -> datetime:
        """Fetch the latest timestamp from the `energy_consumption` table."""

        query = 'SELECT MAX("time") AS latest_time FROM energy_consumption'
        logger.debug(f"Executing query: {query}")
        df = pd.read_sql_query(query, self.engine)
        return df['latest_time'].iloc[0].to_pydatetime() 
    

    def upsert_consumptions(self, data) -> None:
        """
        Insert consumption data to database

        Args:
            data (list): List of dicts with consumption data (time, value)
        """

        df = pd.DataFrame(data, columns=["time", "value"])

        # ensure we have only one record per timestamp
        df = df.groupby("time").agg("sum").reset_index()

        
        # Load table metadata
        metadata = MetaData()
        metadata.reflect(bind=self.engine)  # Reflect existing database schema
        energy_consumption_table = Table("energy_consumption", metadata, autoload_with=self.engine)

        logger.info(f"Inserting {len(df)} consumption records")
        timestart = time.time()
        # Prepare UPSERT (Insert or Update)
        with self.engine.begin() as conn:
            stmt = insert(energy_consumption_table).values(df.to_dict(orient="records"))
            stmt = stmt.on_conflict_do_update(
                index_elements=["time"],  # Conflict on 'time' column (Primary Key)
                set_={"value": stmt.excluded.value}  # Update 'value' if time already exists
            )
            conn.execute(stmt)

        timeend = time.time()
        logger.info(f"Inserting {len(df)} consumption records took {timeend - timestart} seconds")


    def get_latest_production_date(self) -> datetime:
        """Fetch the latest timestamp from the `energy_production` table."""
        query = 'SELECT MAX("time") AS latest_time FROM energy_production'
        logger.debug(f"Executing query: {query}")
        df = pd.read_sql_query(query, self.engine)
        return df['latest_time'].iloc[0].to_pydatetime() 

    def upsert_productions(self, data) -> None:
        """
        Insert production data to database
        
        Args:
            data (list): List of dicts with production data (time, value)
        """
        df = pd.DataFrame(data, columns=["time", "value"])

        # ensure we have only one record per timestamp
        df = df.groupby("time").agg("sum").reset_index()

        # Load table metadata
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        energy_production_table = Table("energy_production", metadata, autoload_with=self.engine)

        logger.info(f"Inserting {len(df)} production records")
        timestart = time.time()
        # Prepare UPSERT (Insert or Update)
        with self.engine.begin() as conn:
            stmt = insert(energy_production_table).values(df.to_dict(orient="records"))
            stmt = stmt.on_conflict_do_update(
                index_elements=["time"],  # Conflict on 'time' column (Primary Key)
                set_={"value": stmt.excluded.value}  # Update 'value' if time already exists
            )
            conn.execute(stmt)

        timeend = time.time()
        logger.info(f"Inserting {len(df)} production records took {timeend - timestart} seconds")


    def get_latest_spotprices(self):
        """
        Get latest spot prices from databse

        Returns:
            datetime: Latest spot price time
        
        """
        query = 'SELECT max("time") AS latest_time FROM energy_spot_price'
        logger.debug(f"Executing query: {query}")
        df = pd.read_sql_query(query, self.engine)
        return df['latest_time'].iloc[0]  # Returns None if empty


    def upsert_spotprices(self, data):
        """
        Insert spot prices to database

        Args:
            data (list): List of dicts with spot price data

        Returns:
            None
        """
  
        df = pd.DataFrame(data, columns=["time", "price"])

        # ensure we have only one record per timestamp
        df = df.groupby("time").agg("max").reset_index()

        # Load table metadata
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        energy_spot_price_table = Table("energy_spot_price", metadata, autoload_with=self.engine)

        logger.info(f"Inserting {len(df)} spot price records")
        timestart = time.time()
        # Prepare UPSERT (Insert or Update)

        with self.engine.begin() as conn:
            stmt = insert(energy_spot_price_table).values(df.to_dict(orient="records"))
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["time"],  # Conflict on 'time' column (Primary Key)
            )
            conn.execute(stmt)

        timeend = time.time()
        logger.info(f"Inserting {len(df)} spot price records took {timeend - timestart} seconds")


if __name__ == "__main__":
    from dotenv import load_dotenv
    db = PostgresDB()
    
    latest_date = db.get_latest_consumption_date()
    print(f"Latest consumption date: {latest_date}")
