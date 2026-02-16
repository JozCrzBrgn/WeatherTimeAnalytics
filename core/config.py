from .weather import WeatherSettings
from .postgres import PostgresSettings


class Settings:
    weather = WeatherSettings()
    postgres = PostgresSettings()


cnf = Settings()
