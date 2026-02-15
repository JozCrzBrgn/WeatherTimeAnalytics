from api.api_requests import build_weather_url
from core.config import cnf


def test_build_weather_url2(monkeypatch):
    monkeypatch.setattr(cnf.weather, "api_key", "TESTKEY123")

    monkeypatch.setattr(cnf.weather, "base_url", "http://test.com")

    url = build_weather_url("Paris")

    assert url == "http://test.com?access_key=TESTKEY123&query=Paris"
