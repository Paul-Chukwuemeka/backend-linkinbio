from datetime import datetime, timedelta, timezone
from os import getenv

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


ALGORITHM = getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_secret_key() -> str:
    secret_key = getenv("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY is not set")
    return secret_key


def create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + expires_delta
    to_encode = {"sub": subject, "iat": now, "exp": expire, "type": token_type}
    return jwt.encode(to_encode, get_secret_key(), algorithm=ALGORITHM)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    return create_token(
        subject=subject,
        token_type="access",
        expires_delta=expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: str, expires_delta: timedelta | None = None) -> str:
    return create_token(
        subject=subject,
        token_type="refresh",
        expires_delta=expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc


def require_token_type(payload: dict, token_type: str) -> dict:
    if payload.get("type") != token_type:
        raise ValueError(f"Invalid token type: expected {token_type}")
    return payload


def decode_access_token(token: str) -> dict:
    return require_token_type(decode_token(token), "access")


def decode_refresh_token(token: str) -> dict:
    return require_token_type(decode_token(token), "refresh")
