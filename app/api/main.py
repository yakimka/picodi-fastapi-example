from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import picodi
from fastapi import APIRouter, FastAPI

from app.api.routes import users, weather

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

logging.basicConfig(level=logging.INFO)


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
    return app


# uvicorn --factory app.api.main:create_app --host=0.0.0.0 --port=8000 --reload
