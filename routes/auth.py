import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from lib.auth import get_current_user
from lib.database import get_db
from lib.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from models.userModel import User
from models.cardModel import Card
from schemas.auth import (
    AuthResponse,
    LoginRequest,
    RefreshTokenRequest,
    SignupRequest,
    UserPublic,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def build_auth_response(user: User) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(subject=str(user.id)),
        refresh_token=create_refresh_token(subject=str(user.id)),
        user=user,
    )


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> AuthResponse:
    existing = (
        db.query(User)
        .filter((User.username == payload.username) | (User.email == payload.email))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already in use",
        )

    user = User(
        username=payload.username,
        email=payload.email,
        fullname=payload.fullname,
        password=hash_password(payload.password),
    )
    db.add(user)
    try:
        db.flush()
        card = Card(user_id=user.id)
        db.add(card)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already in use",
        )

    db.refresh(user)
    return build_auth_response(user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return build_auth_response(user)


@router.post("/refresh", response_model=AuthResponse)
def refresh_tokens(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> AuthResponse:
    try:
        token_payload = decode_refresh_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    subject = token_payload.get("sub")
    try:
        user_id = uuid.UUID(str(subject))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return build_auth_response(user)


@router.get("/me", response_model=UserPublic)
def read_me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return current_user
