from fastapi import APIRouter, Depends

from lib.auth import get_current_user
from models.userModel import User

router = APIRouter(prefix="/protected", tags=["protected"])


@router.get("/ping")
def protected_ping(current_user: User = Depends(get_current_user)) -> dict:
    return {"message": "pong", "user_id": str(current_user.id)}
