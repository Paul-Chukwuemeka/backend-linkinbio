from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
import uuid

from lib.auth import get_current_user
from lib.database import get_db
from models.user_model import User
from models.card_model import Card
from schemas.profile import CurrentUserProfile, ProfileUpdate, UserProfilePublic
from schemas.cards import CardPublicList,CurrentCardUpdate
from routes.cards import get_card_by_id
from lib.s3 import upload_file_to_r2

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=CurrentUserProfile)
def get_my_profile(current_user: User = Depends(get_current_user)) -> CurrentUserProfile:
    return CurrentUserProfile.model_validate(current_user)


@router.post("/upload-avatar", response_model=CurrentUserProfile)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CurrentUserProfile:
    if not str(file.content_type).startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large (max 5MB)",
        )

    ext = os.path.splitext(str(file.filename))[1]
    if not ext:
        if file.content_type == "image/jpeg": ext = ".jpg"
        elif file.content_type == "image/png": ext = ".png"
        elif file.content_type == "image/gif": ext = ".gif"
        elif file.content_type == "image/webp": ext = ".webp"
        else: ext = ".bin"

    filename = f"avatars/{uuid.uuid4()}{ext}"

    try:
        file.file.seek(0)
        upload_file_to_r2(file.file, filename, file.content_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not upload to R2: {str(e)}",
        )

    r2_public_url = os.getenv("R2_PUBLIC_URL")
    if r2_public_url:
        avatar_url = f"{r2_public_url.rstrip('/')}/{filename.lstrip('/')}"
    else:
        avatar_url = f"/{filename}"
    
    current_user.avatar_url = avatar_url

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update profile",
        )

    db.refresh(current_user)
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



@router.get("/{username}", response_model=CardPublicList )
def get_profile(username: str, response: Response, db: Session = Depends(get_db)) -> CardPublicList:
    user = db.query(User).filter(func.lower(User.username) == username.lower()).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    currentCard = user.current_card
    current = get_card_by_id(currentCard,db)
    
    response.headers["Cache-Control"] = "public, max-age=60"
    
    return CardPublicList.model_validate(current)


@router.patch("/current" ,response_model=CurrentUserProfile)
def set_current_card(body: CurrentCardUpdate,current_user: User = Depends(get_current_user),db:Session = Depends(get_db)) -> CurrentUserProfile:
    card_id = body.card_id
    card = (
        db.query(Card)
        .filter(Card.id == card_id, Card.user_id == current_user.id)
        .first()
    )
    if not card:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found")
    current_user.current_card = card_id
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
