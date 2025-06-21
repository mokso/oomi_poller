import os
import pytest
import pandas as pd
from unittest import mock
from db import PostgresDB
from datetime import datetime

@pytest.fixture
def db():
    # Patch create_engine to avoid real DB connection
    with mock.patch('db.create_engine') as mock_engine:
        db = PostgresDB()
        db.engine = mock.Mock()
        yield db

def test_get_latest_consumption_date_returns_datetime(db):
    # Mock pd.read_sql_query to return a DataFrame with a datetime
    latest_dt = datetime(2025, 1, 1, 0, 0, tzinfo=pd.Timestamp('2025-01-01T00:00:00+02:00').tz)
    dt = pd.Timestamp(latest_dt)
    df = pd.DataFrame({'latest_time': [dt]})
    with mock.patch('db.pd.read_sql_query', return_value=df):
        result = db.get_latest_consumption_date()
        assert result == dt.to_pydatetime()  # Ensure it returns a datetime object
        assert result == latest_dt  # Check the value is correct


def test_upsert_consumptions_calls_execute(db):
    data = [
        {'time': '2025-01-01T00:00:00+02:00', 'value': '2,65'},
        {'time': '2025-01-01T01:00:00+02:00', 'value': '3,14'}
    ]
    # Patch SQLAlchemy Table and insert
    with mock.patch('db.MetaData') as mock_metadata, \
         mock.patch('db.Table') as mock_table, \
         mock.patch('db.insert') as mock_insert:
        mock_table.return_value = mock.Mock()
        mock_insert.return_value = mock.Mock(on_conflict_do_update=mock.Mock(return_value=mock.Mock()))
        db.engine.begin = mock.Mock(return_value=mock.MagicMock(__enter__=lambda s: s, __exit__=mock.Mock(), execute=mock.Mock()))
        db.upsert_consumptions(data)
        # If no exception, test passes

def test_get_latest_production_date_returns_datetime(db):
    latest_dt = datetime(2025, 1, 1, 0, 0, tzinfo=pd.Timestamp('2025-01-01T00:00:00+02:00').tz)
    dt = pd.Timestamp(latest_dt)
    df = pd.DataFrame({'latest_time': [dt]})
    with mock.patch('db.pd.read_sql_query', return_value=df):
        result = db.get_latest_production_date()
        assert result == dt.to_pydatetime()  # Ensure it returns a datetime object
        assert result == latest_dt  # Check the value is correct

def test_upsert_productions_calls_execute(db):
    data = [
        {'time': '2025-01-01T00:00:00+02:00', 'value': '1,23'},
        {'time': '2025-01-01T01:00:00+02:00', 'value': '2,34'}
    ]
    with mock.patch('db.MetaData') as mock_metadata, \
         mock.patch('db.Table') as mock_table, \
         mock.patch('db.insert') as mock_insert:
        mock_table.return_value = mock.Mock()
        mock_insert.return_value = mock.Mock(on_conflict_do_update=mock.Mock(return_value=mock.Mock()))
        db.engine.begin = mock.Mock(return_value=mock.MagicMock(__enter__=lambda s: s, __exit__=mock.Mock(), execute=mock.Mock()))
        db.upsert_productions(data)

def test_get_latest_spotprices_returns_value(db):
    dt = pd.Timestamp('2025-01-01T00:00:00+02:00')
    df = pd.DataFrame({'latest_time': [dt]})
    with mock.patch('db.pd.read_sql_query', return_value=df):
        result = db.get_latest_spotprices()
        assert result == dt

def test_upsert_spotprices_calls_execute(db):
    data = [
        {'time': '2025-01-01T00:00:00+02:00', 'price': '12,34'},
        {'time': '2025-01-01T01:00:00+02:00', 'price': '56,78'}
    ]
    with mock.patch('db.MetaData') as mock_metadata, \
         mock.patch('db.Table') as mock_table, \
         mock.patch('db.insert') as mock_insert:
        mock_table.return_value = mock.Mock()
        mock_insert.return_value = mock.Mock(on_conflict_do_update=mock.Mock(return_value=mock.Mock()))
        db.engine.begin = mock.Mock(return_value=mock.MagicMock(__enter__=lambda s: s, __exit__=mock.Mock(), execute=mock.Mock()))
        db.upsert_spotprices(data)
