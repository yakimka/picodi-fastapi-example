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
    kwargs_nested = _build_dict_from_nested_kwargs(kwargs)
    return Settings(**kwargs_nested)


def _build_dict_from_nested_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    """
    Convert nested kwargs to nested dict
    Example:
        path__to__nested__settings=False
        ->
        {"path": {"to": {"nested": {"settings": False}}}}
    """
    result: dict[str, Any] = {}

    for key, value in kwargs.items():
        parts = key.split("__")
        current_level = result

        for part in parts[:-1]:
            current_level.setdefault(part, {})
            current_level = current_level[part]

        current_level[parts[-1]] = value

    return result
