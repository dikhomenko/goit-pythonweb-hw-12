from unittest.mock import patch, ANY, AsyncMock
from conftest import test_user
from app.helpers.email_sender.email import send_password_reset_email as actual_send_email

def test_register_user(client):
    new_user_data = {
        "username": "new_user",
        "email": "new_user@example.com",
        "password": "password123",
        "role": "user",
    }

    response = client.post("/api/auth/register", json=new_user_data)

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == new_user_data["username"]
    assert data["email"] == new_user_data["email"]
    assert "id" in data


def test_login_user(client):
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"],
    }

    response = client.post("/api/auth/login", data=login_data)

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"



@patch("app.dependencies.auth.jwt_manager.create_password_reset_token", return_value="mocked-token")
@patch("app.helpers.email_sender.email.send_password_reset_email")
@patch("fastapi.BackgroundTasks.add_task")
def test_request_password_reset(mock_add_task, mock_send_email, mock_create_token, client):
    # Arrange
    reset_request_data = {"email": test_user["email"]}

    # Act
    response = client.post("/api/auth/request-password-reset", json=reset_request_data)

    # Assert response
    assert response.status_code == 200
    assert response.json()["message"] == "Password reset email sent. Check your inbox."

    # Assert the task was scheduled with correct args
    mock_add_task.assert_called_once_with(
        actual_send_email,
        test_user["email"],
        ANY,  # base_url
        "mocked-token"
    )

@patch("app.services.auth.jwt_manager.JWTManager.create_password_reset_token")
@patch("app.services.auth.jwt_manager.JWTManager.validate_password_reset_token")
@patch("app.helpers.email_sender.email.send_password_reset_email", new_callable=AsyncMock)
def test_reset_password(mock_send_email, mock_validate_token, mock_create_token, client):
    mock_send_email.return_value = None
    mock_create_token.return_value = "valid_reset_token"
    mock_validate_token.return_value = test_user["email"]

    reset_password_data = {
        "token": "valid_reset_token",
        "new_password": "new_password123",
    }

    response = client.post("/api/auth/reset-password", data=reset_password_data)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Password reset successfully."


def test_reset_password_form(client):
    reset_token = "fake_reset_token"
    response = client.get(f"/api/auth/reset-password-form?token={reset_token}")

    assert response.status_code == 200, response.text
    assert "reset your password" in response.text.lower()
