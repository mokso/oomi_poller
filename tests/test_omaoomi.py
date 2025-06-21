import os
import pandas as pd
import pytest
from unittest import mock
from omaoomi import get_consumption_data, get_production_data, get_spot_prices, CONS_FILE, PROD_FILE

@pytest.fixture
def fake_consumption_xlsx(tmp_path):
    df = pd.DataFrame({
        'start': ['01.01.2025 00:00', '01.01.2025 01:00'],
        'end': ['01.01.2025 01:00', '01.01.2025 02:00'],
        'consumption': ['2,65', '3,14'],
        'spotPrice': ['12,34', '56,78']
    })
    file = tmp_path / "consumption.xlsx"
    df.to_excel(file, index=False)
    return file

@pytest.fixture
def fake_production_xlsx(tmp_path):
    df = pd.DataFrame({
        'start': ['01.01.2025 00:00', '01.01.2025 01:00'],
        'end': ['01.01.2025 01:00', '01.01.2025 02:00'],
        'production': ['1,23', 'undefined']
    })
    file = tmp_path / "production.xlsx"
    df.to_excel(file, index=False)
    return file

def test_get_consumption_data_returns_dataframe(fake_consumption_xlsx, monkeypatch):
    monkeypatch.setattr("omaoomi.CONS_FILE", str(fake_consumption_xlsx))
    df = get_consumption_data()
    assert isinstance(df, pd.DataFrame)
    assert "time" in df.columns
    assert "value" in df.columns
    assert df["value"].iloc[0] == '2,65' or df["value"].iloc[0] == 2.65  # Depending on conversion

def test_get_consumption_data_handles_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr("omaoomi.CONS_FILE", str(tmp_path / "doesnotexist.xlsx"))
    assert get_consumption_data() is None

def test_get_production_data_returns_dataframe(fake_production_xlsx, monkeypatch):
    monkeypatch.setattr("omaoomi.PROD_FILE", str(fake_production_xlsx))
    df = get_production_data()
    assert isinstance(df, pd.DataFrame)
    assert "time" in df.columns
    assert "value" in df.columns
    # Only one row should remain (the 'undefined' row is dropped)
    assert len(df) == 1

def test_get_production_data_handles_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr("omaoomi.PROD_FILE", str(tmp_path / "doesnotexist.xlsx"))
    assert get_production_data() is None

def test_get_spot_prices_returns_dataframe(fake_consumption_xlsx, monkeypatch):
    monkeypatch.setattr("omaoomi.CONS_FILE", str(fake_consumption_xlsx))
    df = get_spot_prices()
    assert isinstance(df, pd.DataFrame)
    assert "time" in df.columns
    assert "price" in df.columns
    # Check price conversion: 12,34 -> 0.1234
    assert abs(df["price"].iloc[0] - 0.1234) < 1e-6

def test_get_spot_prices_handles_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr("omaoomi.CONS_FILE", str(tmp_path / "doesnotexist.xlsx"))
    assert get_spot_prices() is None