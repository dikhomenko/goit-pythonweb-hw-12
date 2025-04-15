from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request,
    BackgroundTasks,
    Form,
)
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from app.routers.auth import schemas
from db.database import get_db
from app.services.auth.jwt_manager import Hash
from app.services.user.user_service import UserService
from app.helpers.email_sender.email import send_email, send_password_reset_email
from app.routers.auth.schemas import UserResponse
from app.services.auth.jwt_manager import JWTManager
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

hash_handler = Hash()

router = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(
    directory=str(
        Path(__file__).parent.parent.parent / "helpers/email_sender/templates"
    )
)


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register_user(
    body: schemas.UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(UserService),
):
    """
    Register a new user.

    Args:
        body (schemas.UserModel): The user registration data.
        background_tasks (BackgroundTasks): Background tasks for sending emails.
        request (Request): The HTTP request object.
        db (Session): The database session.
        user_service (UserService): The user service for interacting with the database.

    Returns:
        UserResponse: The registered user's data.
    """
    jwt_manager = JWTManager()

    # Check if the email is already registered
    email_user = user_service.get_user_by_email(db, body.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    # Check if the username is already taken
    username_user = user_service.get_user_by_username(db, body.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists",
        )

    # Create a new user
    new_user = user_service.create_user(
        db,
        username=body.username,
        hashed_password=hash_handler.get_password_hash(body.password),
        email=body.email,
    )

    # Send confirmation email
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url, jwt_manager
    )
    return new_user


@router.post(
    "/login", response_model=schemas.TokenModel, status_code=status.HTTP_200_OK
)
def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    user_service: UserService = Depends(UserService),
    jwt_manager: JWTManager = Depends(JWTManager),
):
    """
    Authenticate a user and generate an access token.

    Args:
        body (OAuth2PasswordRequestForm): The login credentials (username and password).
        db (Session): The database session.
        user_service (UserService): The user service for interacting with the database.
        jwt_manager (JWTManager): The JWT manager for generating the access token.

    Returns:
        schemas.TokenModel: The access token and its type.

    Raises:
        HTTPException: If the username is invalid.
        HTTPException: If the password is incorrect.
        HTTPException: If the user's email is not confirmed.
    """
    # Fetch the user by username
    user = user_service.get_user_by_username(db, body.username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username"
        )

    # Verify the password
    if not hash_handler.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )

    # Check if the email is confirmed
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not confirmed",
        )

    # Generate JWT
    access_token = jwt_manager.create_access_token(data={"sub": user.username})
    return schemas.TokenModel(access_token=access_token, token_type="bearer")


@router.post("/request-password-reset", status_code=status.HTTP_200_OK)
def request_password_reset(
    body: schemas.RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(UserService),
    jwt_manager: JWTManager = Depends(JWTManager),
):
    """
    Handle a password reset request.

    Args:
        body (schemas.RequestEmail): The email address of the user requesting the reset.
        background_tasks (BackgroundTasks): Background tasks for sending the reset email.
        request (Request): The HTTP request object.
        db (Session): The database session.
        user_service (UserService): The user service for interacting with the database.
        jwt_manager (JWTManager): The JWT manager for generating the reset token.

    Returns:
        dict: A success message indicating the reset email was sent.
    """
    user = user_service.get_user_by_email(db, body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Generate password reset token
    token = jwt_manager.create_password_reset_token(user.email)

    # Send password reset email
    background_tasks.add_task(
        send_password_reset_email, user.email, request.base_url, token
    )
    return {"message": "Password reset email sent. Check your inbox."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    token: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db),
    user_service: UserService = Depends(UserService),
    jwt_manager: JWTManager = Depends(JWTManager),
):
    """
    Reset the user's password.

    Args:
        token (str): The password reset token.
        new_password (str): The new password provided by the user.
        db (Session): The database session.
        user_service (UserService): The user service for interacting with the database.
        jwt_manager (JWTManager): The JWT manager for validating tokens.

    Returns:
        dict: A success message.
    """
    # Validate the token and extract the email
    email = jwt_manager.validate_password_reset_token(token)

    # Get the user by email
    user = user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update the user's password
    hashed_password = Hash().get_password_hash(new_password)
    user_service.update_password(db, email, hashed_password)

    return {"message": "Password reset successfully."}


@router.get("/reset-password-form", response_class=HTMLResponse)
def reset_password_form(token: str, request: Request):
    """
    Serve the password reset form.

    Args:
        token (str): The password reset token.
        request (Request): The HTTP request object.

    Returns:
        HTMLResponse: The password reset form HTML.
    """
    return templates.TemplateResponse(
        "reset_password_form.html", {"request": request, "token": token}
    )
