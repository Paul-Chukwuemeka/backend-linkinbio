from functools import lru_cache
from os import getenv

from dotenv import load_dotenv

load_dotenv()

DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]


def _normalize_origin(origin: str) -> str:
    return origin.strip().rstrip("/")


def _parse_cors_origins(raw_value: str | None) -> list[str]:
    if not raw_value:
        return DEFAULT_CORS_ORIGINS.copy()

    origins = [
        _normalize_origin(origin)
        for origin in raw_value.split(",")
        if origin.strip()
    ]

    return origins or DEFAULT_CORS_ORIGINS.copy()


@lru_cache
def get_cors_origins() -> list[str]:
    return _parse_cors_origins(getenv("CORS_ORIGINS"))
