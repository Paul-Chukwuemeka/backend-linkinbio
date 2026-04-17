import os
# Force testing DB immediately before app is imported
os.environ["CONNECTION_STRING"] = "sqlite:///test.db"
os.environ["SECRET_KEY"] = "testing_secret_key"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import main
from lib.database import Base, get_db

# Create a test engine and sessionmaker
SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Setup test database
    Base.metadata.create_all(bind=engine)
    yield
    # Teardown test database
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test.db"):
        os.remove("test.db")

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Apply the override
main.app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    # TestClient doesn't require uvicorn
    with TestClient(main.app) as c:
        yield c
