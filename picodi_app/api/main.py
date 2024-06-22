from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import picodi
from fastapi import APIRouter, FastAPI, Request, Response
from picodi import ContextVarScope

from picodi_app.api.routes import users, weather

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
    )
    app.include_router(create_api_router())
    app.middleware("http")(manage_request_scoped_deps)
    return app


# Picodi Note:
#   This middleware is used to manage request-scoped dependencies.
#   It initializes and closes dependencies on each request.
#   This is needed for properly closing connections, releasing resources, etc.
#   It also allows to inject async dependencies in sync functions.
#   In this example, we use `ContextVarScope` to manage request-scoped dependencies.
#   But you can use any other scope that fits your needs.
async def manage_request_scoped_deps(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    await picodi.init_dependencies(scope_class=ContextVarScope)
    response = await call_next(request)
    await picodi.shutdown_dependencies(scope_class=ContextVarScope)
    return response


# uvicorn --factory picodi_app.api.main:create_app --host=0.0.0.0 --port=8000 --reload
