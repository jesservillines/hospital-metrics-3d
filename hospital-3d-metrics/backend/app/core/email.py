from typing import Optional
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.core.config import settings

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL or "noreply@example.com",  # Provide a default
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_SERVER=settings.SMTP_HOST or "localhost",  # Provide a default
    MAIL_FROM_NAME=settings.PROJECT_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

async def send_email(
    email_to: str,
    subject_template: str,
    html_template: str,
    environment: Optional[dict] = None,
) -> None:
    """Send an email."""
    
    if environment is None:
        environment = {}
        
    message = MessageSchema(
        subject=subject_template,
        recipients=[email_to],
        body=html_template,
        subtype="html",
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_reset_password_email(email_to: EmailStr, token: str) -> None:
    """Send a password reset email."""
    
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery"
    
    # Generate the reset URL
    reset_url = f"{settings.SERVER_HOST}/api/v1/auth/reset-password/{token}"
    
    # Create the email content
    html_template = f"""
        <p>Hi,</p>
        <p>You have requested to reset your password for {project_name}.</p>
        <p>Click the link below to reset your password:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>If you did not request a password reset, please ignore this email.</p>
        <p>This link will expire in 1 hour.</p>
        <p>Best regards,<br>{project_name} Team</p>
    """
    
    await send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=html_template,
    )
