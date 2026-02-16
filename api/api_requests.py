import logging
from typing import Any, Dict

import requests

from core.config import cnf


def build_weather_url(city: str) -> str:
    """
    Get the url from the api weather

    Args:
        city (str): City from which the request is made.

    Returns:
        str: Url from the api weather.
    """
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
