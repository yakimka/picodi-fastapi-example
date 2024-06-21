import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from picodi_app.api.main import create_app


@pytest.fixture()
def fastapi_app() -> FastAPI:
    return create_app()


@pytest.fixture()
def api_client(fastapi_app) -> TestClient:
    return TestClient(fastapi_app, base_url="http://testserver/api")
