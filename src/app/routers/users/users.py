from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
    status,
    BackgroundTasks,
    # UploadFile,
    File,
)

from fastapi import UploadFile
from app.services.user.user_service import UserService
from app.services.file_services.upload_service import UploadFileService
from app.routers.users import schemas
from app.helpers.api.rate_limiter import limiter
from sqlalchemy.orm import Session
from db.database import get_db
from fastapi_mail import ConnectionConfig
from app.settings import settings
from app.routers.users.schemas import RequestEmail, EmailSchema
from app.helpers.email_sender.email import send_email
from app.services.auth.jwt_manager import JWTManager
from db.models.user import User


router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    "/me",
    response_model=schemas.UserResponse,
    description="No more than 5 requests per minute",
)
@limiter.limit("5/minute")
def me(
    request: Request,
    current_user: schemas.UserResponse = Depends(JWTManager().get_current_user),
):
    """
    Retrieve the current authenticated user's details.

    Args:
        request (Request): The HTTP request object.
        current_user (schemas.UserResponse): The currently authenticated user.

    Returns:
        schemas.UserResponse: The details of the current user.
    """
    return current_user


@router.get("/confirmed_email/{token}")
def confirmed_email(
    token: str,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(UserService),
    jwt_manager: JWTManager = Depends(JWTManager),
):
    """
    Confirm a user's email using a token.

    Args:
        token (str): The email confirmation token.
        db (Session): The database session.
        user_service (UserService): The user service for interacting with the database.
        jwt_manager (JWTManager): The JWT manager for validating the token.

    Returns:
        dict: A success message if the email is confirmed.

    Raises:
        HTTPException: If the token is invalid or the user is not found.
    """
    email = jwt_manager.get_email_from_token(token)
    user = user_service.get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "You have already confirmed your email"}
    user_service.confirmed_email(db, email)
    return {"message": "Email confirmed successfully"}


@router.post("/request_email")
def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    user_service: UserService = Depends(UserService),
):
    """
    Request an email confirmation for a user.

    Args:
        body (RequestEmail): The email address of the user requesting confirmation.
        background_tasks (BackgroundTasks): Background tasks for sending the confirmation email.
        request (Request): The HTTP request object.
        db (Session): The database session.
        user_service (UserService): The user service for interacting with the database.

    Returns:
        dict: A success message indicating the confirmation email was sent.
    """
    jwt_manager = JWTManager()
    user = user_service.get_user_by_email(db, body.email)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url, jwt_manager
        )
    return {"message": "Check your email for confirmation"}


@router.patch("/avatar", response_model=schemas.UserResponse)
def update_avatar_user(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    upload_service: UploadFileService = Depends(UploadFileService),
    user_service: UserService = Depends(UserService),
    current_user: User = Depends(JWTManager().get_current_admin_user),
    # current_user: User = Depends(get_current_admin_user)
):
    """
    Update the avatar for the current user.

    Args:
        file (UploadFile): The uploaded avatar file.
        db (Session): The database session.
        upload_service (UploadFileService): The service for handling file uploads.
        user_service (UserService): The user service for interacting with the database.
        current_user (User): The currently authenticated admin user.

    Returns:
        schemas.UserResponse: The updated user with the new avatar URL.

    Raises:
        HTTPException: If the file upload or database update fails.
    """
    avatar_url = upload_service.upload_file(file, current_user.username)
    updated_user = user_service.update_avatar_url(db, current_user.email, avatar_url)
    return updated_user
