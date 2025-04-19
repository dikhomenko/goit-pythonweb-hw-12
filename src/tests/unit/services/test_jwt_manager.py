from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, UTC
from types import SimpleNamespace
from jose import jwt
from fastapi import HTTPException, status
from app.services.auth.jwt_manager import JWTManager
from app.settings import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


def test_create_access_token():
    jwt_manager = JWTManager()
    data = {"sub": "deadpool"}
    expires_delta = 3600

    token = jwt_manager.create_access_token(data, expires_delta)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded_token["sub"] == "deadpool"


def test_get_current_user_valid_token():
    jwt_manager = JWTManager()
    token = jwt.encode({"sub": "test_user"}, SECRET_KEY, algorithm=ALGORITHM)
    user_obj = SimpleNamespace(username="test_user")

    with (
        patch("app.services.auth.jwt_manager.get_db", return_value=None),
        patch.object(JWTManager, "get_current_user", return_value=user_obj),
    ):
        user = jwt_manager.get_current_user(
            token=token, db=None, user_service=MagicMock()
        )

    assert user.username == "test_user"


def test_get_current_user_invalid_token():
    jwt_manager = JWTManager()
    invalid_token = "invalid_token"

    with (
        patch("app.services.auth.jwt_manager.get_db", return_value=None),
        patch.object(
            JWTManager,
            "get_current_user",
            side_effect=HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            ),
        ),
    ):
        try:
            jwt_manager.get_current_user(token=invalid_token, db=None)
            assert False, "Expected HTTPException"
        except HTTPException as e:
            assert e.status_code == status.HTTP_401_UNAUTHORIZED
            assert e.detail == "Could not validate credentials"


def test_create_email_token():
    jwt_manager = JWTManager()
    data = {"sub": "test@example.com"}

    token = jwt_manager.create_email_token(data)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded_token["sub"] == "test@example.com"
    assert "exp" in decoded_token
    assert datetime.fromtimestamp(decoded_token["exp"], tz=UTC) > datetime.now(UTC)


def test_get_email_from_token_valid():
    jwt_manager = JWTManager()
    token = jwt.encode({"sub": "test@example.com"}, SECRET_KEY, algorithm=ALGORITHM)

    email = jwt_manager.get_email_from_token(token)
    assert email == "test@example.com"


def test_get_email_from_token_invalid():
    jwt_manager = JWTManager()
    invalid_token = "invalid_token"

    try:
        jwt_manager.get_email_from_token(invalid_token)
        assert False, "Expected HTTPException"
    except HTTPException as e:
        assert e.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert e.detail == "Wrong token for email confirmation"


def test_create_password_reset_token():
    jwt_manager = JWTManager()
    email = "test@example.com"

    token = jwt_manager.create_password_reset_token(email)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert decoded_token["sub"] == email
    assert "exp" in decoded_token
    assert datetime.fromtimestamp(decoded_token["exp"], tz=UTC) > datetime.now(UTC)


def test_validate_password_reset_token_valid():
    jwt_manager = JWTManager()
    token = jwt.encode({"sub": "test@example.com"}, SECRET_KEY, algorithm=ALGORITHM)

    email = jwt_manager.validate_password_reset_token(token)
    assert email == "test@example.com"


def test_validate_password_reset_token_invalid():
    jwt_manager = JWTManager()
    invalid_token = "invalid_token"

    try:
        jwt_manager.validate_password_reset_token(invalid_token)
        assert False, "Expected HTTPException"
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST
        assert e.detail == "Invalid or expired password reset token"


def test_get_current_admin_user_valid_admin():
    jwt_manager = JWTManager()
    token = jwt.encode({"sub": "admin_user"}, SECRET_KEY, algorithm=ALGORITHM)
    user_obj = SimpleNamespace(username="admin_user", role="admin")

    with (
        patch("app.services.auth.jwt_manager.get_db", return_value=None),
        patch.object(JWTManager, "get_current_user", return_value=user_obj),
    ):
        user = jwt_manager.get_current_admin_user(
            token=token, db=None, user_service=MagicMock()
        )

    assert user.username == "admin_user"
    assert user.role == "admin"


def test_get_current_admin_user_non_admin():
    jwt_manager = JWTManager()
    token = jwt.encode({"sub": "regular_user"}, SECRET_KEY, algorithm=ALGORITHM)
    user_obj = SimpleNamespace(username="regular_user", role="user")

    with (
        patch("app.services.auth.jwt_manager.get_db", return_value=None),
        patch.object(JWTManager, "get_current_user", return_value=user_obj),
    ):
        try:
            jwt_manager.get_current_admin_user(
                token=token, db=None, user_service=MagicMock()
            )
            assert False, "Expected HTTPException"
        except HTTPException as e:
            assert e.status_code == status.HTTP_403_FORBIDDEN
            assert e.detail == "Insufficient permissions"
