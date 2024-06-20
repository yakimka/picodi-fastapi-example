from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasic
from pydantic import BaseModel

from app.api.fastapi_deps import get_current_user
from app.user import User

router = APIRouter()
security = HTTPBasic()


class UserResp(BaseModel):
    id: str
    nickname: str


@router.get("/whoami")
def whoami(current_user: User = Depends(get_current_user)) -> UserResp:
    return UserResp(id=current_user.id, nickname=current_user.nickname)
