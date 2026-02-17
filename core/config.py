from .postgres import PostgresSettings
from .weather import WeatherSettings


class Settings:
    weather = WeatherSettings()
    postgres = PostgresSettings()


cnf = Settings()
