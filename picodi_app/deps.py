from __future__ import annotations

import logging
import sqlite3
from typing import TYPE_CHECKING, Any

from httpx import AsyncClient
from picodi import Registry, SingletonScope, inject, registry
from picodi.helpers import resolve
from picodi.integrations.fastapi import Provide, RequestScope
from redis import asyncio as aioredis

from picodi_app.conf import (
    RedisDatabaseSettings,
    Settings,
    SqliteDatabaseSettings,
    parse_settings,
)
from picodi_app.data_access.sqlite import create_tables
from picodi_app.data_access.user import RedisUserRepository, SqliteUserRepository
from picodi_app.data_access.weather import (
    OpenMeteoGeocoderClient,
    OpenMeteoWeatherClient,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable, Generator  # noqa: TC004

    from picodi_app.user import IUserRepository
    from picodi_app.weather import IGeocoderClient, IWeatherClient

logger = logging.getLogger(__name__)


cli_registry = Registry()


# Picodi Note:
#   We use `SingletonScope` to create a single instance of the Settings object.
@registry.set_scope(scope_class=SingletonScope)
@cli_registry.set_scope(scope_class=SingletonScope)
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
@registry.set_scope(scope_class=SingletonScope)
@cli_registry.set_scope(scope_class=SingletonScope)
@inject
def get_sqlite_connection(
    db_settings: SqliteDatabaseSettings = Provide(
        get_option(lambda s: s.database.settings)
    ),
) -> Generator[sqlite3.Connection, None, None]:
    if not isinstance(db_settings, SqliteDatabaseSettings):
        raise ValueError("Invalid database settings")
    conn = sqlite3.connect(db_settings.db_name, check_same_thread=False)
    logger.info(
        "Connected to SQLite database. ID: %s. Must be closed on app shutdown", id(conn)
    )
    if db_settings.create_db:
        create_tables(conn)
        logger.info("Created tables in SQLite database")
    try:
        yield conn
    finally:
        conn.close()
        logger.info("Closed SQLite connection. ID: %s", id(conn))


@inject
def get_sqlite_user_repository(
    conn: sqlite3.Connection = Provide(get_sqlite_connection),
) -> SqliteUserRepository:
    logger.info(
        "Creating SqliteUserRepository instance with connection ID: %s", id(conn)
    )
    return SqliteUserRepository(conn)


@registry.set_scope(scope_class=SingletonScope)
@cli_registry.set_scope(scope_class=SingletonScope)
@inject
async def get_redis_client(
    db_settings: RedisDatabaseSettings = Provide(
        get_option(lambda s: s.database.settings)
    ),
) -> AsyncGenerator[aioredis.Redis, None]:
    if not isinstance(db_settings, RedisDatabaseSettings):
        raise ValueError("Invalid database settings")

    redis = aioredis.from_url(db_settings.url, decode_responses=True)  # type: ignore
    async with redis as conn:
        logger.info(
            "Connected to Redis database. ID: %s. Must be closed on app shutdown",
            id(conn),
        )
        yield conn
        logger.info("Closed Redis connection. ID: %s", id(conn))


# Picodi Note:
#   Note that `get_redis_client` is an async dependency, but we inject it
#   into a sync `get_redis_user_repository` dependency.
#   It can be done because we use `SingletonScope` and `init_dependencies` function
#   to initialize dependencies on app startup (see `picodi_app.api.main.lifespan`).
@inject
def get_redis_user_repository(
    redis: aioredis.Redis = Provide(get_redis_client),
) -> RedisUserRepository:
    logger.info(
        "Creating RedisUserRepository instance with connection ID: %s", id(redis)
    )
    return RedisUserRepository(redis)


@inject
def get_user_repository(
    db_type: str = Provide(get_option(lambda s: s.database.type)),
) -> Generator[IUserRepository, None, None]:
    # Picodi Note:
    #   Tricky part here is that we want to inject only one of the repositories - either
    #   SqliteUserRepository or RedisUserRepository.
    if db_type == "sqlite":
        with resolve(get_sqlite_user_repository) as repo:
            yield repo
    elif db_type == "redis":
        with resolve(get_redis_user_repository) as repo:
            yield repo
    else:
        raise ValueError(f"Unsupported database type: {db_type}")


# Picodi Note:
#   We use `RequestScope` to create http client for open-meteo service.
#   That means that even if will be created multiple repositories or services
#   that depend on `get_open_meteo_http_client` they will share the same instance
#   of the http client (across one request).
#
#   In real project we would use `httpx.AsyncClient` with connection pooling
#   and reuse the same instance of the client across multiple requests.
@registry.set_scope(scope_class=RequestScope)
@cli_registry.set_scope(scope_class=RequestScope)
async def get_open_meteo_http_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(timeout=5) as client:
        logger.info(
            "Creating new httpx.AsyncClient. ID: %s. Must be closed on end of request",
            id(client),
        )
        yield client
        logger.info("Closing httpx.AsyncClient instance. ID: %s", id(client))


@inject
async def get_weather_client(
    http_client: AsyncClient = Provide(get_open_meteo_http_client),
) -> IWeatherClient:
    logger.info(
        "Creating OpenMeteoWeatherClient instance with http client ID: %s",
        id(http_client),
    )
    return OpenMeteoWeatherClient(http_client=http_client)


@inject
async def get_geocoder_client(
    http_client: AsyncClient = Provide(get_open_meteo_http_client),
) -> IGeocoderClient:
    logger.info(
        "Creating OpenMeteoGeocoderClient instance with http client ID: %s",
        id(http_client),
    )
    return OpenMeteoGeocoderClient(http_client=http_client)


# Picodi Note:
#   We can use `init_dependencies` function to initialize dependencies on app startup.
#   In this example we use it to initialize database connection and redis client
#   on app startup depending on the database type from settings.
#   In most cases we don't need setup like this, but it's good to know that
#   we can use it if needed.
@inject
def dependencies_for_init(
    db_type: str = Provide(get_option(lambda s: s.database.type)),
) -> list[Callable]:
    if db_type == "redis":
        return [get_redis_client]

    return []


registry.add_for_init(dependencies_for_init)
cli_registry.add_for_init(dependencies_for_init)
