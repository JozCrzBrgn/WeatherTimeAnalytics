import logging
import random
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

import requests

from core.config import get_settings

cnf = get_settings()

CITY_REGEX = re.compile(r"^[A-Za-zÀ-ÿ\s\-]+$")
WEATHER_DESCRIPTIONS = [
    "Sunny",
    "Partly cloudy",
    "Cloudy",
    "Rain",
    "Light rain",
    "Heavy rain",
    "Thunderstorm",
    "Snow",
    "Fog",
    "Overcast",
]


def build_weather_url(city: str) -> str:
    """
    Get the url from the api weather

    Args:
        city (str): City from which the request is made.

    Returns:
        str: Url from the api weather.
    """

    if not city or not city.strip():
        raise ValueError("City cannot be empty")

    if not CITY_REGEX.match(city):
        raise ValueError("City contains invalid characters")

    return f"{cnf.weather.base_url}?access_key={cnf.weather.api_key}&query={city}"


def fetch_data(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch weather data from the API.

    Args:
        url (str): Weather API endpoint.
        timeout (int): Request timeout in seconds.

    Returns:
        Dict[str, Any]: Parsed JSON response.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        logging.info(
            "Weather API response received",
            extra={"url": url, "status_code": response.status_code},
        )

        return response.json()

    except requests.exceptions.RequestException:
        logging.error("Error calling Weather API", exc_info=True, extra={"url": url})
        raise


def mock_fetch_data(city: str = "New York", days_offset: int = 0) -> Dict[str, Any]:
    """
    Generate mock weather data.

    Args:
        city (str): City name.
        days_offset (int): Days relative to today.
                            0 = today
                            1 = tomorrow
                            -1 = yesterday

    Returns:
        Dict[str, Any]: Mock weather response.
    """
    try:
        if not city or not city.strip():
            raise ValueError("City cannot be empty")

        if not CITY_REGEX.match(city):
            raise ValueError("City contains invalid characters")

        if not isinstance(days_offset, int):
            raise TypeError("days_offset must be an integer")

        now_utc = datetime.now(timezone.utc)

        # Aplicamos offset de días
        base_date = now_utc + timedelta(days=days_offset)

        # Offset de zona horaria aleatorio
        utc_offset = "-5.0"
        offset_hours = float(utc_offset)

        local_time = base_date + timedelta(hours=offset_hours)

        sunrise_time = local_time.replace(hour=6, minute=50)
        sunset_time = local_time.replace(hour=17, minute=31)

        moon_phases = [
            "New Moon",
            "Waxing Crescent",
            "First Quarter",
            "Waxing Gibbous",
            "Full Moon",
            "Waning Gibbous",
            "Last Quarter",
            "Waning Crescent",
        ]

        weather_descriptions = [
            "Sunny",
            "Cloudy",
            "Partly cloudy",
            "Rain",
            "Thunderstorm",
            "Snow",
        ]

        data = {
            "request": {
                "type": "City",
                "query": f"{city}, United States of America",
                "language": "en",
                "unit": "m",
            },
            "location": {
                "name": city,
                "country": "United States of America",
                "region": "New York",
                "lat": "40.714",
                "lon": "-74.006",
                "timezone_id": "America/New_York",
                "localtime": local_time.strftime("%Y-%m-%d %H:%M"),
                "localtime_epoch": int(local_time.timestamp()),
                "utc_offset": utc_offset,
            },
            "current": {
                "observation_time": local_time.strftime("%I:%M %p"),
                "temperature": random.randint(-15, 45),
                "weather_code": random.randint(100, 900),
                "weather_icons": [
                    "https://cdn.worldweatheronline.com/images/wsymbols01_png_64/wsymbol_0004_black_low_cloud.png"
                ],
                "weather_descriptions": [random.choice(weather_descriptions)], # nosec B311 - safe for mock data
                "astro": {
                    "sunrise": sunrise_time.strftime("%I:%M %p"),
                    "sunset": sunset_time.strftime("%I:%M %p"),
                    "moonrise": sunrise_time.strftime("%I:%M %p"),
                    "moonset": sunset_time.strftime("%I:%M %p"),
                    "moon_phase": random.choice(moon_phases), # nosec B311 - safe for mock data
                    "moon_illumination": random.randint(0, 100), # nosec B311 - safe for mock data
                },
                "air_quality": {
                    "co": f"{round(random.uniform(200, 400), 2)}",
                    "no2": f"{round(random.uniform(10, 80), 2)}",
                    "o3": f"{round(random.uniform(10, 100), 2)}",
                    "so2": f"{round(random.uniform(1, 10), 2)}",
                    "pm2_5": f"{round(random.uniform(5, 50), 2)}",
                    "pm10": f"{round(random.uniform(5, 80), 2)}",
                    "us-epa-index": str(random.randint(1, 5)), # nosec B311 - safe for mock data
                    "gb-defra-index": str(random.randint(1, 5)), # nosec B311 - safe for mock data
                },
                "wind_speed": random.randint(0, 80),
                "wind_degree": random.randint(0, 360),
                "wind_dir": random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"]),
                "pressure": random.randint(980, 1050),
                "precip": round(random.uniform(0, 20), 1),
                "humidity": random.randint(10, 100),
                "cloudcover": random.randint(0, 100),
                "feelslike": random.randint(-20, 50),
                "uv_index": random.randint(0, 11),
                "visibility": random.randint(1, 20),
                "is_day": "yes" if 6 <= local_time.hour < 18 else "no",
            },
        }

        logging.info(
            "Mock weather data generated",
            extra={"city": city, "days_offset": days_offset},
        )

        return data

    except Exception:
        logging.error("Error generating mock weather data", exc_info=True)
        raise
