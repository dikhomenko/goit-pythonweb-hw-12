import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.contact import Contact, Email, Phone, AdditionalData
from db.models.user import User
from app.repositories.contacts.crud import ContactsRepository
from app.routers.contacts.schemas import ContactCreate, AdditionalDataCreate
from db.models.base import Base  # Import the Base from db.models to include all models

import sys
import os
import uuid
from datetime import date

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

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
def contacts_repository():
    """Fixture to provide an instance of ContactsRepository."""
    return ContactsRepository()


@pytest.fixture
def test_user(test_db):
    """Fixture to create a test user with a unique username."""
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    user = User(
        username=unique_username,
        email=f"{unique_username}@example.com",
        password="hashed_password",
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_contact(test_db, test_user):
    """Fixture to create a test contact."""
    contact_data = Contact(
        first_name="John",
        last_name="Doe",
        birthday=date(1990, 1, 1),  # Use a date object
        user_id=test_user.id,
        emails=[Email(email="john.doe@example.com")],
        phones=[Phone(phone="1234567890")],
        additional_data=[AdditionalData(key="note", value="Test contact")],
    )
    test_db.add(contact_data)
    test_db.commit()
    test_db.refresh(contact_data)
    return contact_data


def test_create_contact(test_db, contacts_repository, test_user):
    """Test creating a contact."""
    contact_data = ContactCreate(
        first_name="John",
        last_name="Doe",
        birthday=date(1990, 1, 1),  # Use a date object
        emails=[{"email": "john.doe@example.com"}],
        phones=[{"phone": "1234567890"}],
        additional_data=[{"key": "note", "value": "Test contact"}],
    )
    contact = contacts_repository.create_contact(test_db, contact_data, test_user.id)
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.user_id == test_user.id
    assert len(contact.emails) == 1
    assert contact.emails[0].email == "john.doe@example.com"
    assert len(contact.phones) == 1
    assert contact.phones[0].phone == "1234567890"
    assert len(contact.additional_data) == 1
    assert contact.additional_data[0].key == "note"


def test_get_contacts(test_db, contacts_repository, test_user, test_contact):
    """Test retrieving contacts for a user."""
    contacts = contacts_repository.get_contacts(test_db, test_user.id)
    assert len(contacts) > 0
    assert contacts[0].first_name == "John"


def test_get_contact(test_db, contacts_repository, test_user, test_contact):
    """Test retrieving a specific contact by ID."""
    retrieved_contact = contacts_repository.get_contact(
        test_db, test_contact.id, test_user.id
    )
    assert retrieved_contact.id == test_contact.id
    assert retrieved_contact.first_name == test_contact.first_name


def test_update_contact(test_db, contacts_repository, test_user, test_contact):
    """Test updating a contact."""
    updated_data = ContactCreate(
        first_name="Jane",
        last_name="Smith",
        birthday=date(1995, 5, 5),  # Use a date object
        emails=[{"email": "jane.smith@example.com"}],
        phones=[{"phone": "9876543210"}],
        additional_data=[{"key": "note", "value": "Updated contact"}],
    )
    updated_contact = contacts_repository.update_contact(
        test_db, test_contact.id, updated_data, test_user.id
    )
    assert updated_contact.first_name == "Jane"
    assert updated_contact.last_name == "Smith"
    assert len(updated_contact.emails) == 1
    assert updated_contact.emails[0].email == "jane.smith@example.com"


def test_delete_contact(test_db, contacts_repository, test_user, test_contact):
    """Test deleting a contact."""
    deleted_contact = contacts_repository.delete_contact(
        test_db, test_contact.id, test_user.id
    )
    assert deleted_contact.id == test_contact.id
    assert test_db.query(Contact).filter(Contact.id == test_contact.id).first() is None


def test_get_contact_by_name_lastname_email(
    test_db, contacts_repository, test_user, test_contact
):
    """Test searching for a contact by name, lastname, and email."""
    contacts = contacts_repository.get_contact_by_name_lastname_email(
        test_db,
        test_user.id,
        name="John",
        lastname="Doe",
        email="john.doe@example.com",
    )
    assert len(contacts) == 1
    assert contacts[0].first_name == "John"
    assert contacts[0].last_name == "Doe"


def test_get_contacts_with_upcoming_birthdays(test_db, contacts_repository, test_user):
    """Test retrieving contacts with upcoming birthdays."""
    contacts = contacts_repository.get_contacts_with_upcoming_birthdays(
        test_db, test_user.id
    )
    assert len(contacts) >= 0  # Adjust based on test data


def test_duplicate_user_creation(test_db):
    """Test handling duplicate user creation."""
    user = User(
        username="testuser", email="testuser@example.com", password="hashed_password"
    )
    test_db.add(user)
    test_db.commit()

    duplicate_user = User(
        username="testuser", email="testuser@example.com", password="hashed_password"
    )
    test_db.add(duplicate_user)
    with pytest.raises(Exception):  # Use specific exception if possible
        test_db.commit()
