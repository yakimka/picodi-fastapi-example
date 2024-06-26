from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import anyio
import picodi
from fastapi import APIRouter, FastAPI
from picodi.integrations.fastapi import RequestScopeMiddleware
from starlette.middleware import Middleware

from picodi_app.api.routes import users, weather
from picodi_app.utils import monitor_thread_limiter

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

logging.basicConfig(level=logging.INFO)


# Picodi Note:
#   The lifespan context manager is used to initialize dependencies on app startup and
#   close them on app shutdown.
#   This is needed for properly closing connections, releasing resources, etc.
#   But more importantly, it allows to inject async dependencies in sync functions,
#   this can be done if async dependency are scoped with `SingletonScope` or similar.
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await picodi.init_dependencies()
    try:
        yield
    finally:
        await picodi.shutdown_dependencies()


def create_api_router() -> APIRouter:
    router = APIRouter()
    api_router = APIRouter(prefix="/api")
    api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
    api_router.include_router(users.router, prefix="/users", tags=["users"])
    router.include_router(api_router)
    return router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Weather App",
        description="Example Weather App API with Picodi and FastAPI",
        lifespan=lifespan,
        # Picodi Note:
        #   The RequestScopeMiddleware is used to manage a scopes for each request.
        middleware=[Middleware(RequestScopeMiddleware)],
    )
    app.include_router(create_api_router())
    return app


# uvicorn --factory picodi_app.api.main:create_app --host=0.0.0.0 --port=8000 --reload


if __name__ == "__main__":
    # Code under this `if` is for my testing purposes only
    import uvicorn

    config = uvicorn.Config(app="picodi_app.api.main:create_app", factory=True)
    server = uvicorn.Server(config)

    async def main() -> None:
        async with anyio.create_task_group() as tg:
            tg.start_soon(monitor_thread_limiter)
            await server.serve()

    anyio.run(main)
