import pytest
import requests

from api.api_requests import build_weather_url, fetch_data
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
