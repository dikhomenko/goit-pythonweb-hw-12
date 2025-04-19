from unittest.mock import MagicMock
from app.services.user.user_service import UserService


def test_get_user_by_username():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.get_user_by_username.return_value = {"id": 1, "username": "test_user"}
    user_service = UserService(users_repository=mock_repository)

    # Act
    result = user_service.get_user_by_username(None, "test_user")

    # Assert
    assert result["username"] == "test_user"
    mock_repository.get_user_by_username.assert_called_once_with(None, "test_user")


def test_get_user_by_email():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.get_user_by_email.return_value = {"id": 1, "email": "test@example.com"}
    user_service = UserService(users_repository=mock_repository)

    # Act
    result = user_service.get_user_by_email(None, "test@example.com")

    # Assert
    assert result["email"] == "test@example.com"
    mock_repository.get_user_by_email.assert_called_once_with(None, "test@example.com")


def test_get_user_by_id():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.get_user_by_id.return_value = {"id": 1, "username": "test_user"}
    user_service = UserService(users_repository=mock_repository)

    # Act
    result = user_service.get_user_by_id(None, 1)

    # Assert
    assert result["id"] == 1
    mock_repository.get_user_by_id.assert_called_once_with(None, 1)


def test_create_user():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.create_user.return_value = {"id": 1, "username": "new_user"}
    user_service = UserService(users_repository=mock_repository)

    # Act
    result = user_service.create_user(None, "new_user", "hashed_password", "new_user@example.com")

    # Assert
    assert result["username"] == "new_user"
    mock_repository.create_user.assert_called_once_with(None, "new_user", "hashed_password", "new_user@example.com")


def test_confirmed_email():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.confirmed_email.return_value = True
    user_service = UserService(users_repository=mock_repository)

    # Act
    result = user_service.confirmed_email(None, "test@example.com")

    # Assert
    assert result is True
    mock_repository.confirmed_email.assert_called_once_with(None, "test@example.com")


def test_update_avatar_url():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.update_avatar_url.return_value = {"email": "test@example.com", "avatar_url": "http://example.com/avatar.jpg"}
    user_service = UserService(users_repository=mock_repository)

    # Act
    result = user_service.update_avatar_url(None, "test@example.com", "http://example.com/avatar.jpg")

    # Assert
    assert result["avatar_url"] == "http://example.com/avatar.jpg"
    mock_repository.update_avatar_url.assert_called_once_with(None, "test@example.com", "http://example.com/avatar.jpg")


def test_update_password():
    # Arrange
    mock_repository = MagicMock()
    mock_repository.update_password.return_value = True
    user_service = UserService(users_repository=mock_repository)

    # Act
    result = user_service.update_password(None, "test@example.com", "new_password")

    # Assert
    assert result is True
    mock_repository.update_password.assert_called_once_with(None, "test@example.com", "new_password")