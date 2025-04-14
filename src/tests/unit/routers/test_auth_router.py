import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.routers.auth.schemas import UserModel, TokenModel

client = TestClient(app)


def test_register_user_missing_fields():
    """Test registering a user with missing required fields."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            # Missing email and password
        },
    )
    assert response.status_code == 422  # Unprocessable Entity


def test_register_user_invalid_email_format():
    """Test registering a user with an invalid email format."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "invalid-email",
            "password": "securepassword",
        },
    )
    assert response.status_code == 422  # Unprocessable Entity


def test_login_user_missing_fields():
    """Test logging in with missing required fields."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            # Missing password
        },
    )
    assert response.status_code == 422  # Unprocessable Entity


def test_login_user_invalid_token():
    """Test accessing a protected route with an invalid token."""
    response = client.get(
        "/api/protected-route",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


@pytest.mark.parametrize(
    "username, email, password",
    [
        ("user1", "user1@example.com", "password1"),
        ("user2", "user2@example.com", "password2"),
    ],
)
def test_register_user_parametrized(username, email, password):
    """Test registering multiple users with parameterized data."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == username
    assert data["email"] == email


def test_login_user_expired_token():
    """Test logging in with an expired token."""
    expired_token = "expired_token_example"
    with patch(
        "app.services.auth.jwt_manager.JWTManager.decode_access_token"
    ) as mock_decode:
        mock_decode.side_effect = ValueError("Token has expired")

        response = client.get(
            "/api/protected-route",
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Token has expired"
        mock_decode.assert_called_once_with(expired_token)


def test_register_user():
    """Test registering a new user."""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword",
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"


def test_register_user_duplicate_email():
    """Test registering a user with a duplicate email."""
    user_data = {
        "username": "anotheruser",
        "email": "testuser@example.com",  # Duplicate email
        "password": "securepassword",
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 409  # Conflict


def test_login_user_success():
    """Test logging in with valid credentials."""
    user_data = {
        "username": "testuser",
        "password": "securepassword",
    }
    response = client.post("/api/auth/login", data=user_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_user_invalid_credentials():
    """Test logging in with invalid credentials."""
    user_data = {
        "username": "testuser",
        "password": "wrongpassword",
    }
    response = client.post("/api/auth/login", data=user_data)
    assert response.status_code == 401  # Unauthorized


def test_login_user_nonexistent_email():
    """Test logging in with a nonexistent email."""
    user_data = {
        "username": "nonexistentuser",
        "password": "password",
    }
    response = client.post("/api/auth/login", data=user_data)
    assert response.status_code == 401  # Unauthorized


def test_refresh_token_success():
    """Test refreshing a valid token."""
    with patch(
        "app.services.auth.jwt_manager.JWTManager.create_access_token"
    ) as mock_create_token:
        mock_create_token.return_value = "new_access_token"

        response = client.post(
            "/api/auth/refresh", headers={"Authorization": "Bearer valid_token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "new_access_token"
        mock_create_token.assert_called_once()


def test_refresh_token_invalid_user():
    """Test refreshing a token for an invalid user."""
    response = client.post(
        "/api/auth/refresh", headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401  # Unauthorized
