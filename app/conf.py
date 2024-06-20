from typing import Any, Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class SqliteDatabaseSettings(BaseModel):
    db_name: str = "db.sqlite"
    create_db: bool = False


class RedisDatabaseSettings(BaseModel):
    url: str = "redis://redis:6379/0"


class DatabaseSettings(BaseModel):
    type: Literal["sqlite", "redis"] = "sqlite"
    settings: SqliteDatabaseSettings | RedisDatabaseSettings = SqliteDatabaseSettings()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore", env_nested_delimiter="__", env_ignore_empty=True
    )

    database: DatabaseSettings = DatabaseSettings()


def parse_settings(**kwargs: Any) -> Settings:
    return Settings(**kwargs)
