from __future__ import annotations

import logging
import sqlite3
from typing import TYPE_CHECKING, Any

from httpx import AsyncClient
from picodi import Provide, SingletonScope, dependency, inject

from picodi_app.conf import Settings, SqliteDatabaseSettings, parse_settings
from picodi_app.data_access.sqlite import create_tables
from picodi_app.data_access.user import SqliteUserRepository
from picodi_app.data_access.weather import (
    OpenMeteoGeocoderClient,
    OpenMeteoWeatherClient,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Generator  # noqa: TC004

    from picodi_app.user import IUserRepository
    from picodi_app.weather import IGeocoderClient, IWeatherClient

logger = logging.getLogger(__name__)


@dependency(scope_class=SingletonScope)
def get_settings() -> Settings:
    return parse_settings()


def get_option(
    getter: Callable[[Settings], Any], default: Any = ...
) -> Callable[[], Any]:
    @inject
    def get_option_inner(settings: Settings = Provide(get_settings)) -> Any:
        try:
            return getter(settings)
        except LookupError:
            if default is not ...:
                return default
            raise

    return get_option_inner


@dependency(scope_class=SingletonScope)
@inject
def get_sqlite_connection(
    db_settings: SqliteDatabaseSettings = Provide(
        get_option(lambda s: s.database.settings)
    ),
) -> Generator[sqlite3.Connection, None, None]:
    if not isinstance(db_settings, SqliteDatabaseSettings):
        raise ValueError("Invalid database settings")
    conn = sqlite3.connect(db_settings.db_name, check_same_thread=False)
    logger.info("Connected to SQLite database. ID: %s", id(conn))
    if db_settings.create_db:
        create_tables(conn)
        logger.info("Created tables in SQLite database")
    try:
        yield conn
    finally:
        conn.close()
        logger.info("Closed SQLite connection. ID: %s", id(conn))


@inject
def get_user_repository(
    conn: sqlite3.Connection = Provide(get_sqlite_connection),
) -> IUserRepository:
    logger.info(
        "Creating SqliteUserRepository instance with connection ID: %s", id(conn)
    )
    return SqliteUserRepository(conn)


@dependency(scope_class=SingletonScope)
async def get_open_meteo_http_client() -> AsyncGenerator[AsyncClient, None]:
    logger.info("Creating new httpx.AsyncClient instance")
    async with AsyncClient() as client:
        yield client
    logger.info("Closing httpx.AsyncClient instance")


@inject
def get_weather_client(
    http_client: AsyncClient = Provide(get_open_meteo_http_client),
) -> IWeatherClient:
    return OpenMeteoWeatherClient(http_client=http_client)


@inject
def get_geocoder_client(
    http_client: AsyncClient = Provide(get_open_meteo_http_client),
) -> IGeocoderClient:
    return OpenMeteoGeocoderClient(http_client=http_client)
