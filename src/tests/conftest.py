from unittest.mock import MagicMock, patch
import logging
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from db.models import Base, User
from db.database import get_db
from app.services.auth.jwt_manager import Hash, JWTManager
from app.settings import settings
from jose import jwt
from db.models.user import UserRole
from app.dependencies.auth import jwt_manager


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Use a file-based SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create a single shared connection
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Create a session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

test_user = {
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "12345678",
}


def get_mock_admin_user():
    """
    Returns a MagicMock representing an authenticated admin user.
    """
    user = MagicMock()
    user.id = 1
    user.username = test_user["username"]
    user.email = test_user["email"]
    user.confirmed = True
    user.role = UserRole.admin.value
    return user


def init_models():
    logger.debug("Initializing database schema...")
    # Create tables
    with engine.begin() as conn:
        logger.debug("Dropping all tables...")
        Base.metadata.drop_all(bind=conn)
        logger.debug("Creating all tables...")
        Base.metadata.create_all(bind=conn)

    # Add test user
    logger.debug("Adding test user to the database...")
    with TestingSessionLocal() as session:
        hash_password = Hash().get_password_hash(test_user["password"])
        current_user = User(
            username=test_user["username"],
            email=test_user["email"],
            password=hash_password,
            confirmed=True,
            avatar="<https://twitter.com/gravatar>",
        )
        session.add(current_user)
        session.commit()
        logger.debug("Test user added: %s", current_user)


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    logger.debug("Calling init_models_wrap fixture...")
    # Ensure the database schema is initialized before the tests
    init_models()
    yield
    # Clean up the database file after the tests
    logger.debug("Disposing of the database engine...")
    engine.dispose()
    if os.path.exists("./test.db"):
        os.remove("./test.db")
        logger.debug("Test database file removed.")


@pytest.fixture(scope="module")
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Override the exact callable used in the route
    app.dependency_overrides[jwt_manager.get_current_admin_user] = get_mock_admin_user

    yield TestClient(app)

    # Clean up after tests
    app.dependency_overrides.clear()


@pytest.fixture()
def get_token():
    logger.debug("Generating a fake token...")
    jwt_manager_mock = MagicMock()
    jwt_manager_mock.create_access_token.return_value = jwt.encode(
        {"sub": test_user["username"]},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    JWTManager.create_access_token = jwt_manager_mock.create_access_token

    token = JWTManager().create_access_token(data={"sub": test_user["username"]})
    logger.debug("Fake token generated: %s", token)
    return token
