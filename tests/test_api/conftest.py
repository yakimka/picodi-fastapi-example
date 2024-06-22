import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from picodi_app.api.main import create_app


@pytest.fixture()
def fastapi_app() -> FastAPI:
    return create_app()


@pytest.fixture()
async def api_client(fastapi_app) -> AsyncClient:
    async with AsyncClient(app=fastapi_app, base_url="http://test/api") as client:
        yield client
