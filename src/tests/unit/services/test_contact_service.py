from unittest.mock import MagicMock
from app.services.contacts.contact_service import ContactService


def test_get_contact():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.get_contact.return_value = {"id": 1, "name": "John Doe"}
    contact_service = ContactService(contacts_repository=mock_repository)

    # Act
    result = contact_service.get_contact(None, 1, 1)

    # Assert
    assert result["id"] == 1
    mock_repository.get_contact.assert_called_once_with(None, 1, 1)


def test_get_contacts():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.get_contacts.return_value = [
        {"id": 1, "name": "John Doe"},
        {"id": 2, "name": "Jane Doe"},
    ]
    contact_service = ContactService(contacts_repository=mock_repository)

    # Act
    result = contact_service.get_contacts(None, 1, skip=0, limit=10)

    # Assert
    assert len(result) == 2
    mock_repository.get_contacts.assert_called_once_with(None, 1, 0, 10)


def test_create_contact():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.create_contact.return_value = {"id": 1, "name": "John Doe"}
    contact_service = ContactService(contacts_repository=mock_repository)

    # Act
    result = contact_service.create_contact(None, {"name": "John Doe"}, 1)

    # Assert
    assert result["name"] == "John Doe"
    mock_repository.create_contact.assert_called_once_with(None, {"name": "John Doe"}, 1)


def test_update_contact():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.update_contact.return_value = {"id": 1, "name": "John Updated"}
    contact_service = ContactService(contacts_repository=mock_repository)

    # Act
    result = contact_service.update_contact(None, 1, {"name": "John Updated"}, 1)

    # Assert
    assert result["name"] == "John Updated"
    mock_repository.update_contact.assert_called_once_with(None, 1, {"name": "John Updated"}, 1)


def test_delete_contact():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.delete_contact.return_value = {"id": 1, "name": "John Doe"}
    contact_service = ContactService(contacts_repository=mock_repository)

    # Act
    result = contact_service.delete_contact(None, 1, 1)

    # Assert
    assert result["id"] == 1
    mock_repository.delete_contact.assert_called_once_with(None, 1, 1)


def test_get_contact_by_name_lastname_email():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.get_contact_by_name_lastname_email.return_value = [
        {"id": 1, "name": "John Doe", "email": "john@example.com"}
    ]
    contact_service = ContactService(contacts_repository=mock_repository)

    # Act
    result = contact_service.get_contact_by_name_lastname_email(
        None, 1, name="John", lastname=None, email="john@example.com"
    )

    # Assert
    assert len(result) == 1
    assert result[0]["email"] == "john@example.com"
    mock_repository.get_contact_by_name_lastname_email.assert_called_once_with(
        None, 1, "John", None, "john@example.com"
    )


def test_get_contacts_with_upcoming_birthdays():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.get_contacts_with_upcoming_birthdays.return_value = [
        {"id": 1, "name": "John Doe", "birthday": "1990-01-01"}
    ]
    contact_service = ContactService(contacts_repository=mock_repository)

    # Act
    result = contact_service.get_contacts_with_upcoming_birthdays(None, 1)

    # Assert
    assert len(result) == 1
    assert result[0]["birthday"] == "1990-01-01"
    mock_repository.get_contacts_with_upcoming_birthdays.assert_called_once_with(None, 1)