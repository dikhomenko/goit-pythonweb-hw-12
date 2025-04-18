import pytest
from fastapi.testclient import TestClient
from app.main import app
from db.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.base import Base
from unittest.mock import MagicMock, patch

# Add the src directory to the Python path
import os
import sys

sys.path.insert(0, os.path.abspath("../../"))

# Configure SQLite in-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the `get_db` dependency to use the test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# Create the TestClient
client = TestClient(app)


# Create the database schema before running tests
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables after tests
    Base.metadata.drop_all(bind=engine)


# Mock the entire JWTManager class
@patch("app.services.auth.jwt_manager.JWTManager")
def test_create_contact(mock_jwt_manager):
    # Configure the mock to return a fake user
    mock_jwt_manager.return_value.get_current_user.return_value = MagicMock(
        id=1, email="testuser@example.com", confirmed=True
    )

    contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "birthday": "1990-01-01",
        "emails": [{"email": "john.doe@example.com"}],
        "phones": [{"phone": "1234567890"}],
        "additional_data": [{"key": "note", "value": "Test contact"}],
    }
    headers = {"Authorization": "Bearer test_token"}  # Mock header if required
    response = client.post("/api/contacts/", json=contact_data, headers=headers)
    print("Response status code:", response.status_code)
    print("Response body:", response.json())  # Debug the response body
    assert response.status_code == 201
    assert response.json()["first_name"] == "John"
    assert response.json()["last_name"] == "Doe"


# Test: Retrieve a list of contacts
def test_read_contacts():
    headers = {"Authorization": "Bearer test_token"}  # Mock header if required
    response = client.get("/api/contacts/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Test: Retrieve a specific contact by ID
def test_read_contact():
    contact_id = 1
    headers = {"Authorization": "Bearer test_token"}  # Mock header if required
    response = client.get(f"/api/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == contact_id


# Test: Update a contact
def test_update_contact():
    contact_id = 1
    updated_data = {
        "first_name": "Jane",
        "last_name": "Doe",
        "birthday": "1992-02-02",
        "emails": [{"email": "jane.doe@example.com"}],
        "phones": [{"phone": "0987654321"}],
        "additional_data": [{"key": "note", "value": "Updated contact"}],
    }
    headers = {"Authorization": "Bearer test_token"}  # Mock header if required
    response = client.put(
        f"/api/contacts/{contact_id}", json=updated_data, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Jane"
    assert response.json()["last_name"] == "Doe"


# Test: Delete a contact
def test_delete_contact():
    contact_id = 1
    headers = {"Authorization": "Bearer test_token"}  # Mock header if required
    response = client.delete(f"/api/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == contact_id


# Test: Search for contacts
def test_search_contacts():
    params = {
        "name": "John",
        "lastname": "Doe",
        "email": "john.doe@example.com",
    }
    headers = {"Authorization": "Bearer test_token"}  # Mock header if required
    response = client.get("/api/contacts/search/", params=params, headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# Test: Retrieve contacts with upcoming birthdays
def test_contacts_with_upcoming_birthdays():
    headers = {"Authorization": "Bearer test_token"}  # Mock header if required
    response = client.get("/api/contacts/birthdays/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
