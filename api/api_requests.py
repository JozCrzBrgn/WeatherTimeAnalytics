from core.config import cnf


def build_weather_url(city: str) -> str:
    return f"{cnf.weather.base_url}?access_key={cnf.weather.api_key}&query={city}"
