from functools import lru_cache
from os import getenv

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

load_dotenv()

Base = declarative_base()


@lru_cache
def get_database_url() -> str:
    database_url = getenv("CONNECTION_STRING")
    if not database_url:
        raise RuntimeError("CONNECTION_STRING is not set")
    return str(database_url)


@lru_cache
def get_engine() -> Engine:
    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
    )


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(
        autoflush=False,
        autocommit=False,
        bind=get_engine(),
    )


def get_db():
    db = get_session_factory()()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
