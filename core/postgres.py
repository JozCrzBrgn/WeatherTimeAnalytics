from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class PostgresSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="PG_",
        extra="ignore",
    )

    host: str
    port: int
    port_localhost: str = Field(alias="PG_PORT_LOCALHOST")
    dbname: str
    user: str
    password: str
