from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.oauth2_config import oauth2_settings
from app.database import get_db
from app.models.user import User
from app.models.oauth2 import OAuth2Token
from app.schemas.auth import (
    UserLogin,
    UserRegistration,
    PasswordReset,
    PasswordResetConfirm,
    UserResponse,
)
from app.core.templates import templates
from app.core.security import limiter
from app.core.email import send_reset_password_email
import secrets

router = APIRouter(tags=["authentication"])

@router.get("/login")
async def login_page(
    request: Request,
    return_to: Optional[str] = None,
):
    """Render login page."""
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
            "return_to": return_to,
        },
    )

@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Handle login form submission."""
    try:
        # Authenticate user
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled",
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": user.username},
            scopes=form_data.scopes if hasattr(form_data, 'scopes') else ["profile:read"],
        )

        # Create refresh token if remember_me is True
        refresh_token = None
        remember_me = getattr(form_data, 'remember_me', 'false').lower() == 'true'
        
        if remember_me:
            refresh_token, expires_at = create_refresh_token(
                data={"sub": user.username},
                scopes=["profile:read"],
            )

            # Store refresh token
            db_token = OAuth2Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                scope="profile:read",
                user_id=user.id,
                expires_at=expires_at,
            )
            db.add(db_token)
            db.commit()

        # Set session cookie
        request.session["user_id"] = user.id
        
        # Set remember me cookie if requested
        if remember_me and refresh_token:
            response.set_cookie(
                "refresh_token",
                refresh_token,
                max_age=60 * 60 * 24 * 30,  # 30 days
                httponly=True,
                secure=True,
                samesite="lax",
            )

        # Return token response for API clients
        return JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer",
            },
            media_type="application/json",
        )
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise

@router.get("/register")
async def register_page(request: Request):
    """Render registration page."""
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request},
    )

@router.post("/register")
@limiter.limit("3/minute")
async def register(
    request: Request,
    form_data: UserRegistration,
    db: Session = Depends(get_db),
):
    """Handle registration form submission."""
    
    # Check if username exists
    if db.query(User).filter(User.username == form_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email exists
    if db.query(User).filter(User.email == form_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = User(
        username=form_data.username,
        email=form_data.email,
        hashed_password=get_password_hash(form_data.password),
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed",
        )

    # Log user in
    request.session["user_id"] = user.id

    return RedirectResponse(
        url="/",
        status_code=status.HTTP_302_FOUND,
    )

@router.get("/logout")
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """Handle logout."""
    
    # Clear session
    request.session.clear()
    
    # Clear remember me cookie
    response.delete_cookie("refresh_token")
    
    # Revoke refresh tokens
    if user_id := request.session.get("user_id"):
        db.query(OAuth2Token).filter(
            OAuth2Token.user_id == user_id,
            OAuth2Token.revoked == False,
        ).update({"revoked": True})
        db.commit()

    return RedirectResponse(
        url="/",
        status_code=status.HTTP_302_FOUND,
    )

@router.get("/reset-password")
async def reset_password_page(request: Request):
    """Render password reset request page."""
    return templates.TemplateResponse(
        "auth/reset_password.html",
        {"request": request},
    )

@router.post("/reset-password")
@limiter.limit("3/minute")
async def reset_password(
    request: Request,
    form_data: PasswordReset,
    db: Session = Depends(get_db),
):
    """Handle password reset request."""
    
    user = db.query(User).filter(User.email == form_data.email).first()
    if user:
        # Generate reset token
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()

        # Send reset email
        await send_reset_password_email(user.email, token)

    # Always return success to prevent email enumeration
    return {"message": "If an account exists with this email, you will receive reset instructions"}

@router.get("/reset-password/{token}")
async def reset_password_confirm_page(
    request: Request,
    token: str,
    db: Session = Depends(get_db),
):
    """Render password reset confirmation page."""
    
    user = db.query(User).filter(
        User.reset_token == token,
        User.reset_token_expires > datetime.utcnow(),
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    return templates.TemplateResponse(
        "auth/reset_password_confirm.html",
        {
            "request": request,
            "token": token,
        },
    )

@router.post("/reset-password/{token}")
@limiter.limit("3/minute")
async def reset_password_confirm(
    request: Request,
    token: str,
    form_data: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    """Handle password reset confirmation."""
    
    user = db.query(User).filter(
        User.reset_token == token,
        User.reset_token_expires > datetime.utcnow(),
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Update password
    user.hashed_password = get_password_hash(form_data.password)
    user.reset_token = None
    user.reset_token_expires = None
    
    # Revoke all refresh tokens
    db.query(OAuth2Token).filter(
        OAuth2Token.user_id == user.id,
        OAuth2Token.revoked == False,
    ).update({"revoked": True})
    
    db.commit()

    return RedirectResponse(
        url="/login",
        status_code=status.HTTP_302_FOUND,
    )
