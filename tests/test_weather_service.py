from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
import requests

import api
from api.api_requests import build_weather_url, fetch_data
from core.config import get_settings

cnf = get_settings()


class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        pass

# * ------------------------------- *#
# * ------ build_weather_url ------ *#
# * ------------------------------- *#
def test_build_weather_url(monkeypatch):
    monkeypatch.setattr(cnf.weather, "api_key", "TESTKEY123")
    monkeypatch.setattr(cnf.weather, "base_url", "http://test.com")
    url = build_weather_url("Paris")
    assert url == "http://test.com?access_key=TESTKEY123&query=Paris"


# * ------------------------ *#
# * ------ fetch_data ------ *#
# * ------------------------ *#
def test_fetch_data_success(monkeypatch):
    """
    Successful test case
    """

    def mock_get(*args, **kwargs):
        return MockResponse({"temp": 25})

    monkeypatch.setattr("api.api_requests.requests.get", mock_get)
    result = fetch_data("http://fake-url.com")
    assert result == {"temp": 25}


def test_fetch_data_http_error(monkeypatch):
    """
    HTTP test error
    """

    class MockResponse:
        def raise_for_status(self):
            raise requests.exceptions.HTTPError("404 Error")

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr("api.api_requests.requests.get", mock_get)
    with pytest.raises(requests.exceptions.HTTPError):
        fetch_data("http://fake-url.com")


def test_fetch_data_timeout(monkeypatch):
    """
    Timeout test
    """

    def mock_get(*args, **kwargs):
        raise requests.exceptions.Timeout("Timeout")

    monkeypatch.setattr("api.api_requests.requests.get", mock_get)
    with pytest.raises(requests.exceptions.Timeout):
        fetch_data("http://fake-url.com")


# * ------------------ *#
# * ------ main ------ *#
# * ------------------ *#
@patch("api.insert_data.insert_weather_records")
@patch("api.insert_data.create_table")
@patch("api.insert_data.connect_to_db")
@patch("api.insert_data.mock_fetch_data")
def test_main_success(mock_fetch, mock_connect, mock_create, mock_insert):
    """
    Successful test case
    """
    mock_fetch.return_value = {"data": "fake"}
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    context = {
        "logical_date": datetime(2026, 2, 13, 12, tzinfo=timezone.utc)
    }

    api.insert_data.main(**context)

    mock_fetch.assert_called_once()
    mock_connect.assert_called_once()
    mock_create.assert_called_once_with(mock_conn)
    mock_insert.assert_called_once_with(mock_conn, {"data": "fake"})
    mock_conn.close.assert_called_once()


@patch("api.insert_data.insert_weather_records")
@patch("api.insert_data.create_table")
@patch("api.insert_data.connect_to_db")
@patch("api.insert_data.mock_fetch_data")
def test_main_closes_connection_on_error(mock_fetch, mock_connect, mock_create, mock_insert):
    """
    Fail test case
    """
    mock_fetch.return_value = {"data": "fake"}
    mock_conn = MagicMock()
    mock_connect.return_value = mock_conn

    mock_insert.side_effect = Exception("Insert failed")

    context = {
        "logical_date": datetime(2026, 2, 13, 12, tzinfo=timezone.utc)
    }

    with pytest.raises(Exception):
        api.insert_data.main(**context)

    mock_conn.close.assert_called_once()


@patch("api.insert_data.connect_to_db")
def test_main_no_connection_no_close(mock_connect):
    """
    If the connection fails, do not attempt to close.
    """
    mock_connect.side_effect = Exception("DB down")

    context = {
        "logical_date": datetime(2026, 2, 13, 12, tzinfo=timezone.utc)
    }

    with pytest.raises(Exception, match="DB down"):
        api.insert_data.main(**context)