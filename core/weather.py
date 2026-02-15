from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WeatherSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )

    base_url: str = Field(
        default="http://api.weatherstack.com/current",
        alias="BASE_WEATHER_URL",
    )
    api_key: str = Field(alias="WEATHER_API_KEY")
