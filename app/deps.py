from __future__ import annotations

import logging
import sqlite3
from typing import TYPE_CHECKING, Any

from httpx import AsyncClient
from picodi import ContextVarScope, Provide, SingletonScope, dependency, inject

from app.conf import Settings, parse_settings
from app.data_access.user import SqliteUserRepository
from app.data_access.weather import OpenMeteoGeocoderClient, OpenMeteoWeatherClient

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Generator

    from app.user import IUserRepository
    from app.weather import IGeocoderClient, IWeatherClient

logger = logging.getLogger(__name__)


class FastApiScope(ContextVarScope):
    pass


@dependency(scope_class=SingletonScope)
def get_settings() -> Settings:
    return parse_settings()


def get_option(getter: Callable[[Settings], Any], /) -> Callable[[], Any]:
    @inject
    def get_option_inner(settings: Settings = Provide(get_settings)) -> Any:
        return getter(settings)

    return get_option_inner


@dependency(scope_class=FastApiScope)
def get_sqlite_connection() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect("db.sqlite", check_same_thread=False)
    logger.info("Connected to SQLite database. ID: %s", id(conn))
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
