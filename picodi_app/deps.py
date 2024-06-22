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


# Picodi Note:
#   We use `SingletonScope` to create a single instance of the Settings object.
@dependency(scope_class=SingletonScope)
def get_settings() -> Settings:
    return parse_settings()


# Picodi Note:
#   We use `get_option` to get a specific option from the settings object.
#   In `getter` argument we pass a lambda function that extracts the desired option.
#   Mypy will check if the option is present in the settings object
#   and will raise an error if it's not.
#   Example: `get_option(lambda s: s.database.type)` will return the database type.
#
#   Also in this example you can see that `inject` decorator
#   can be used in closures as well.
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


# Picodi Note:
#   Thanks to `SingletonScope` we can use sqlite connection
#   even with ":memory:" database.
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


# Picodi Note:
#   Note that `get_open_meteo_http_client` is an async dependency, but we inject it
#   into a sync `get_weather_client` dependency.
#   It can be done because we use `SingletonScope` and `init_dependencies` function
#   to initialize dependencies on app startup (see `picodi_app.api.main.lifespan`).
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
