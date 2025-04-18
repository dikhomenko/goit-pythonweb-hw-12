from unittest.mock import patch
from conftest import test_user


def test_get_me(client, get_token):
    # Use the token provided by the `get_token` fixture
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    # Send GET request to the `/api/users/me` endpoint
    response = client.get("/api/users/me", headers=headers)

    # Assert the response status code
    assert response.status_code == 200, response.text

    # Assert the response data
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "avatar" in data


@patch("app.services.file_services.upload_service.UploadFileService.upload_file")
def test_update_avatar_user(mock_upload_file, client, get_token):
    # Mock the file upload service
    fake_url = "<http://example.com/avatar.jpg>"
    mock_upload_file.return_value = fake_url

    # Use the token provided by the `get_token` fixture
    headers = {"Authorization": f"Bearer {get_token}"}

    # File to be sent
    file_data = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}

    # Send PATCH request to the `/api/users/avatar` endpoint
    response = client.patch("/api/users/avatar", headers=headers, files=file_data)

    # Assert the response status code
    assert response.status_code == 200, response.text

    # Assert the response data
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert data["avatar"] == fake_url

    # Assert that the `upload_file` function was called once
    mock_upload_file.assert_called_once()
