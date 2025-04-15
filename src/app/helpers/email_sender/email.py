from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from app.settings import settings
from app.services.auth.jwt_manager import JWTManager
from fastapi import Depends


conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(
    email: EmailStr, username: str, host: str, jwt_manager: JWTManager
):
        """
    Send an email confirmation link to the user.

    Args:
        email (EmailStr): The recipient's email address.
        username (str): The username of the recipient.
        host (str): The base URL of the application.
        jwt_manager (JWTManager): The JWT manager for generating the email token.

    Raises:
        Exception: If the email fails to send.
    """
    try:
        # Use JWTManager to create the email token
        token_verification = jwt_manager.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        # Send the email
        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        raise Exception(f"Failed to send email to {email}. Please try again later.")


async def send_password_reset_email(email: EmailStr, host: str, token: str):
    """
    Send a password reset email to the user.

    Args:
        email (EmailStr): The recipient's email address.
        host (str): The base URL of the application.
        token (str): The password reset token.

    Raises:
        Exception: If the email fails to send.
    """
    try:
        message = MessageSchema(
            subject="Password Reset Request for Your Account",
            recipients=[email],
            template_body={"host": host, "token": token},
            subtype=MessageType.html,
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        raise Exception(
            f"Failed to send password reset email to {email}. Please try again later."
        )
