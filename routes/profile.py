from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from lib.auth import get_current_user
from lib.database import get_db
from models.userModel import User
from schemas.profile import CurrentUserProfile, ProfileUpdate, UserProfilePublic

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=CurrentUserProfile)
def get_my_profile(current_user: User = Depends(get_current_user)) -> CurrentUserProfile:
    return CurrentUserProfile.model_validate(current_user)


@router.patch("/me", response_model=CurrentUserProfile)
def update_my_profile(
    payload: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CurrentUserProfile:
    if payload.username is not None:
        username = payload.username.strip()
        if not username:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Username cannot be empty",
            )
        current_user.username = username

    if payload.fullname is not None:
        fullname = payload.fullname.strip()
        if not fullname:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Full name cannot be empty",
            )
        current_user.fullname = fullname

    if "bio" in payload.model_fields_set:
        bio = (payload.bio or "").strip()
        current_user.bio = bio or None

    if "avatar_url" in payload.model_fields_set:
        avatar_url = (payload.avatar_url or "").strip()
        current_user.avatar_url = avatar_url or None

    if "theme" in payload.model_fields_set:
        theme = (payload.theme or "").strip()
        current_user.theme = theme or "default"

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already in use",
        )

    db.refresh(current_user)
    return CurrentUserProfile.model_validate(current_user)


@router.get("/{username}", response_model=UserProfilePublic)
def get_profile(username: str, db: Session = Depends(get_db)) -> UserProfilePublic:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserProfilePublic.model_validate(user)
