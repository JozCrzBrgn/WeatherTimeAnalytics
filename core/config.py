from functools import lru_cache

from .postgres import PostgresSettings
from .weather import WeatherSettings


class Settings:
    def __init__(self):
        self.weather = WeatherSettings()
        self.postgres = PostgresSettings()

@lru_cache
def get_settings() -> Settings:
    return Settings()
