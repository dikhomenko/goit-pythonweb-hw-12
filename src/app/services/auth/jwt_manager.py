from datetime import datetime, timedelta, UTC
from typing import Optional
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.settings import settings
from db.database import get_db
from app.services.user.user_service import UserService
from fastapi.security import OAuth2PasswordBearer
from app.settings import settings
from db.models.user import User, UserRole
import redis
from redis_lru import RedisLRU

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
JWT_EXPIRATION_SECONDS = settings.JWT_EXPIRATION_SECONDS

# Initialize Redis connection
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
)
cache = RedisLRU(redis_client)


class Hash:
    """
    Utility class for hashing and verifying passwords.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.OAUTH2_SCHEME)


class JWTManager:
    """
    Manager class for handling JWT creation and validation.
    """

    def __init__(self):
        pass

    def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Create an access token with optional expiration time.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(UTC) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @cache
    def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
        user_service: UserService = Depends(UserService),  # Resolve dependency here
    ):
        """
        Retrieve the current authenticated user from the token.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = user_service.get_user_by_username(db, username)
        if user is None:
            raise credentials_exception
        return user

    def get_current_admin_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
        user_service: UserService = Depends(UserService),
    ):
        """
        Retrieve the current authenticated admin user from the token.
        """
        # Call get_current_user explicitly
        current_user = self.get_current_user(
            token=token, db=db, user_service=user_service
        )

        if current_user.role != UserRole.admin.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    def create_email_token(self, data: dict):
        """
        Create a token for email confirmation.
        """
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(days=7)
        to_encode.update({"iat": datetime.now(UTC), "exp": expire})
        token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return token

    def get_email_from_token(self, token: str):
        """
        Extract the email from an email confirmation token.
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email = payload.get("sub")
            return email
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Wrong token for email confirmation",
            )

    def create_password_reset_token(self, email: str):
        """
        Generate a password reset token.
        """
        to_encode = {"sub": email, "iat": datetime.now(UTC)}
        expire = datetime.now(UTC) + timedelta(hours=1)  # Token valid for 1 hour
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def validate_password_reset_token(self, token: str):
        """
        Validate the password reset token and extract the email.
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("sub")  # Return the email
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token",
            )
