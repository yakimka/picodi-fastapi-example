import logging
from collections.abc import Callable

import picodi
from fastapi import Depends, FastAPI, Request, Response
from fastapi.security import HTTPBasic
from pydantic import BaseModel

from app.api.fastapi_deps import get_current_user
from app.deps import FastApiScope
from app.user import User

logging.basicConfig(level=logging.INFO)

app = FastAPI()
security = HTTPBasic()


@app.middleware("http")
async def shutdown_dependencies_middleware(
    request: Request, call_next: Callable
) -> Response:
    await picodi.init_dependencies(FastApiScope)
    response = await call_next(request)
    await picodi.shutdown_dependencies(FastApiScope)
    return response


@app.get("/")
def read_root() -> dict:
    return {"Hello": "World"}


class UserResp(BaseModel):
    id: str
    nickname: str


@app.get("/whoami")
def whoami(current_user: User = Depends(get_current_user)) -> UserResp:
    return UserResp(id=current_user.id, nickname=current_user.nickname)


# uvicorn app.api.main:app --reload
