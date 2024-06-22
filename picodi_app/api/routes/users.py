from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasic
from pydantic import BaseModel

from picodi_app.api.fastapi_deps import get_current_user_or_raise_error
from picodi_app.user import User

router = APIRouter()
security = HTTPBasic()


class UserResp(BaseModel):
    id: str
    email: str


@router.get(
    "/whoami",
    description="Get current user. Requires authentication (Basic Auth).",
)
def whoami(current_user: User = Depends(get_current_user_or_raise_error)) -> UserResp:
    return UserResp(id=current_user.id, email=current_user.email)
