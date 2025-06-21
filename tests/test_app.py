import os
import pytest
from unittest import mock
import app

@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    monkeypatch.setenv("OOMI_USERNAME", "user")
    monkeypatch.setenv("OOMI_PASSWORD", "pass")
    monkeypatch.setenv("POSTGRES_SERVER", "localhost")
    monkeypatch.setenv("POSTGRES_USER", "postgres")
    monkeypatch.setenv("POSTGRES_PASSWORD", "pw")
    monkeypatch.setenv("POSTGRES_DB", "db")


def test_check_config_all_present():
    assert app.check_config() is True


def test_check_config_missing(monkeypatch):
    monkeypatch.delenv("OOMI_USERNAME", raising=False)
    assert app.check_config() is False


def test_run_syncs_success(monkeypatch):
    # Patch all data functions and db methods
    monkeypatch.setattr(app, "get_oomi_data", mock.AsyncMock())
    monkeypatch.setattr(app, "get_consumption_data", mock.Mock(return_value=[{"time": "2025-01-01T00:00:00+02:00", "value": 2.0}]))
    monkeypatch.setattr(app, "get_production_data", mock.Mock(return_value=[{"time": "2025-01-01T00:00:00+02:00", "value": 1.0}]))
    monkeypatch.setattr(app, "get_spot_prices", mock.Mock(return_value=[{"time": "2025-01-01T00:00:00+02:00", "price": 0.12}]))
    db_mock = mock.Mock()
    monkeypatch.setattr(app, "db", db_mock)
    # Should not raise
    import asyncio
    asyncio.run(app.run_syncs())
    assert db_mock.upsert_consumptions.called
    assert db_mock.upsert_productions.called
    assert db_mock.upsert_spotprices.called


def test_run_syncs_handles_none(monkeypatch):
    monkeypatch.setattr(app, "get_oomi_data", mock.AsyncMock())
    monkeypatch.setattr(app, "get_consumption_data", mock.Mock(return_value=None))
    monkeypatch.setattr(app, "get_production_data", mock.Mock(return_value=None))
    monkeypatch.setattr(app, "get_spot_prices", mock.Mock(return_value=None))
    db_mock = mock.Mock()
    monkeypatch.setattr(app, "db", db_mock)
    import asyncio
    asyncio.run(app.run_syncs())
    assert not db_mock.upsert_consumptions.called
    assert not db_mock.upsert_productions.called
    assert not db_mock.upsert_spotprices.called
