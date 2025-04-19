import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.user import User
from app.repositories.users.users import UsersRepository
from db.models.base import Base  # Import the Base to include all models

# Set up an in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def test_db():
    """Fixture to set up and tear down the test database."""
    Base.metadata.create_all(bind=engine)  # Create all tables
    db = TestingSessionLocal()  # Create a new session
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)  # Drop all tables after tests


@pytest.fixture
def users_repository():
    """Fixture to provide an instance of UsersRepository."""
    return UsersRepository()


@pytest.fixture
def test_user(test_db):
    """Fixture to create a test user."""
    user = User(
        username="deadpool",
        email="deadpool@example.com",
        password="hashed_password",
        confirmed=False,
        avatar=None,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


def test_get_user_by_username(test_db, users_repository, test_user):
    """Test retrieving a user by username."""
    user = users_repository.get_user_by_username(test_db, test_user.username)
    assert user is not None
    assert user.username == test_user.username


def test_get_user_by_email(test_db, users_repository, test_user):
    """Test retrieving a user by email."""
    user = users_repository.get_user_by_email(test_db, test_user.email)
    assert user is not None
    assert user.email == test_user.email


def test_get_user_by_id(test_db, users_repository, test_user):
    """Test retrieving a user by ID."""
    user = users_repository.get_user_by_id(test_db, test_user.id)
    assert user is not None
    assert user.id == test_user.id


def test_create_user(test_db, users_repository):
    """Test creating a new user."""
    new_user = users_repository.create_user(
        test_db,
        username="new_user",
        hashed_password="hashed_password",
        email="new_user@example.com",
    )
    assert new_user is not None
    assert new_user.username == "new_user"
    assert new_user.email == "new_user@example.com"


def test_confirmed_email(test_db, users_repository, test_user):
    """Test confirming a user's email."""
    users_repository.confirmed_email(test_db, test_user.email)
    user = users_repository.get_user_by_email(test_db, test_user.email)
    assert user.confirmed is True


def test_update_avatar_url(test_db, users_repository, test_user):
    """Test updating a user's avatar URL."""
    new_avatar_url = "https://example.com/avatar.jpg"
    updated_user = users_repository.update_avatar_url(
        test_db, test_user.email, new_avatar_url
    )
    assert updated_user.avatar == new_avatar_url


def test_update_password(test_db, users_repository, test_user):
    """Test updating a user's password."""
    new_password = "new_hashed_password"
    updated_user = users_repository.update_password(
        test_db, test_user.email, new_password
    )
    assert updated_user.password == new_password
