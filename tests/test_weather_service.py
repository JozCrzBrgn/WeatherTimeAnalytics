import random

import pytest
import requests
from freezegun import freeze_time

from api.api_requests import build_weather_url, fetch_data, mock_fetch_data
from core.config import cnf


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


# * ----------------------------- *#
# * ------ mock_fetch_data ------ *#
# * ----------------------------- *#


def test_mock_fetch_data_structure():
    """
    Dictionary structure
    """
    data = mock_fetch_data("CDMX")
    assert "request" in data
    assert "location" in data
    assert "current" in data


def test_city_is_used():
    """
    Respect the city
    """
    city = "Monterrey"
    data = mock_fetch_data(city)
    assert data["request"]["query"] == city
    assert data["location"]["name"] == city


@freeze_time("2026-02-13 12:00:00")
def test_days_offset():
    """
    Change the date using days_offset
    """
    data_today = mock_fetch_data("CDMX", 0)
    data_tomorrow = mock_fetch_data("CDMX", 1)
    assert data_today["location"]["localtime"] != data_tomorrow["location"]["localtime"]


def test_temperature_range():
    """
    validate that the values ​​are within range
    """
    data = mock_fetch_data()

    temperature = data["current"]["temperature"]
    weather_code = data["current"]["weather_code"]
    wind_speed = data["current"]["wind_speed"]
    wind_degree = data["current"]["wind_degree"]
    pressure = data["current"]["pressure"]
    precip = data["current"]["precip"]
    humidity = data["current"]["humidity"]
    cloudcover = data["current"]["cloudcover"]
    feelslike = data["current"]["feelslike"]
    uv_index = data["current"]["uv_index"]
    visibility = data["current"]["visibility"]

    assert -15 <= temperature <= 45
    assert 100 <= weather_code <= 900
    assert 0 <= wind_speed <= 80
    assert 0 <= wind_degree <= 360
    assert 980 <= pressure <= 1050
    assert 0 <= precip <= 20
    assert 10 <= humidity <= 100
    assert 0 <= cloudcover <= 100
    assert -20 <= feelslike <= 50
    assert 0 <= uv_index <= 11
    assert 1 <= visibility <= 20


def test_deterministic_output():
    """
    Deterministic Test
    """
    random.seed(42)
    data1 = mock_fetch_data()

    random.seed(42)
    data2 = mock_fetch_data()

    assert data1["current"]["temperature"] == data2["current"]["temperature"]
    assert data1["current"]["weather_code"] == data2["current"]["weather_code"]
    assert data1["current"]["wind_speed"] == data2["current"]["wind_speed"]
    assert data1["current"]["wind_degree"] == data2["current"]["wind_degree"]
    assert data1["current"]["pressure"] == data2["current"]["pressure"]
    assert data1["current"]["precip"] == data2["current"]["precip"]
    assert data1["current"]["humidity"] == data2["current"]["humidity"]
    assert data1["current"]["cloudcover"] == data2["current"]["cloudcover"]
    assert data1["current"]["feelslike"] == data2["current"]["feelslike"]
    assert data1["current"]["uv_index"] == data2["current"]["uv_index"]
    assert data1["current"]["visibility"] == data2["current"]["visibility"]


def test_negative_days_offset():
    """
    Validate that it does not explode with negative values
    """
    data = mock_fetch_data("CDMX", days_offset=-1)
    assert "location" in data
    assert data["request"]["query"] == "CDMX"


def test_large_days_offset():
    """
    Detect potential overflow or format problems
    """
    data = mock_fetch_data("CDMX", days_offset=365)
    assert "localtime" in data["location"]


def test_days_offset_zero_is_valid():
    """
    days_offset zero is valid
    """
    data = mock_fetch_data("CDMX", 0)
    assert data["request"]["query"] == "CDMX"


def test_days_offset_wrong_type():
    """
    days_offset wrong type
    """
    with pytest.raises(TypeError):
        mock_fetch_data("CDMX", "mañana")


def test_city_empty():
    """
    Empty city
    """
    with pytest.raises(ValueError):
        mock_fetch_data("", 0)


def test_city_with_emoji():
    """
    City with emoji
    """
    with pytest.raises(ValueError):
        mock_fetch_data("São Paulo 🏙️", 0)


def test_city_with_number():
    """
    City with numbers
    """
    with pytest.raises(ValueError):
        mock_fetch_data("Paris123", 0)


def test_city_valid_with_accent():
    """
    City with accent
    """
    data = mock_fetch_data("São Paulo", 0)
    assert data["location"]["name"] == "São Paulo"
