from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from jose import JWTError

from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_token_dependency,
    TokenData,
)
from ..core.oauth2_config import oauth2_settings
from ..database import get_db
from ..models.user import User, UserRole
from ..models.session import Session as UserSession
from ..models.blacklist import BlacklistedToken
from ..schemas.auth import (
    UserLogin,
    UserRegistration,
    PasswordReset,
    PasswordResetConfirm,
    UserResponse,
)
from ..core.templates import templates
from ..core.security import limiter
from ..core.email import send_reset_password_email
import os
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], default="bcrypt")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    return_to: str = None,
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
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False),
    db: DBSession = Depends(get_db),
):
    """Handle login form submission."""
    try:
        logger.info(f"Login attempt for username: {username}")
        logger.info(f"Form data - remember_me: {remember_me}")
        
        user = db.query(User).filter(User.username == username).first()
        if not user:
            logger.warning(f"User not found: {username}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid username or password"}
            )
        
        logger.info(f"User found: {user.id}")
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Invalid password for user: {username}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid username or password"}
            )

        if not user.is_active:
            logger.warning(f"Inactive user attempted login: {username}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "User is inactive"}
            )

        logger.info("Creating access token")
        # Create access token
        access_token = create_access_token(
            data={"sub": user.username},
            scopes=["user"],
            expires_delta=timedelta(minutes=oauth2_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        # Create refresh token if remember_me is True
        refresh_token = None
        if remember_me:
            logger.info("Creating refresh token")
            refresh_token = create_refresh_token(
                data={"sub": user.username},
                scopes=["user"]
            )
            response.set_cookie(
                "refresh_token",
                refresh_token,
                max_age=oauth2_settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
                httponly=True,
                secure=True if os.getenv("ENV") == "production" else False,
                samesite="lax"
            )

        # Store session data
        logger.info("Storing session data")
        request.session["user_id"] = user.id

        try:
            # Create user session record
            logger.info("Creating user session record")
            user_session = UserSession(
                user_id=user.id,
                session_token=access_token,
                refresh_token=refresh_token,
                expires_at=datetime.now() + timedelta(minutes=oauth2_settings.ACCESS_TOKEN_EXPIRE_MINUTES),
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent")
            )
            db.add(user_session)
            db.commit()
            logger.info("User session created successfully")
        except Exception as session_error:
            logger.error(f"Error creating user session: {str(session_error)}")
            db.rollback()
            raise

        logger.info("Login successful, returning response")
        return JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer",
                "refresh_token": refresh_token,
                "success": True
            }
        )

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        logger.exception("Full traceback:")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal server error: {str(e)}"}
        )

@router.get("/register")
async def register_page(request: Request):
    """Render registration page."""
    return templates.TemplateResponse(
        "auth/register.html",
        {"request": request},
    )

@router.post("/register")
async def register(
    request: Request,
    form_data: UserRegistration,
    db: DBSession = Depends(get_db),
):
    """Handle registration form submission."""
    try:
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

        # Create user with default role 'user'
        try:
            user = User(
                username=form_data.username,
                email=form_data.email,
                hashed_password=get_password_hash(form_data.password),
                role=UserRole.USER,  # Default role for new users
                is_active=True,
                is_verified=False,
                created_at=datetime.now(),
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Return appropriate response based on environment
            if os.getenv("TESTING"):
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "role": user.role.value
                    }
                )
            else:
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={"detail": "Registration successful"}
                )

        except IntegrityError as e:
            db.rollback()
            logger.error(f"Database error during registration: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: Database error - {str(e)}"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating user: {str(e)}"
            )
            
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in register endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.get("/logout")
async def logout_page(request: Request):
    """Render logout confirmation page."""
    return templates.TemplateResponse(
        "auth/logout.html",
        {
            "request": request,
        },
    )

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: DBSession = Depends(get_db),
):
    """Handle logout."""
    logger.info("Logout endpoint called")
    try:
        # Get the token from the Authorization header
        auth_header = request.headers.get("Authorization")
        logger.info(f"Authorization header: {auth_header}")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("No valid Authorization header found")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "No valid token found"}
            )

        token = auth_header.split(" ")[1]
        logger.info("Token extracted from header")

        # Blacklist the token
        try:
            blacklisted_token = BlacklistedToken(token=token)
            db.add(blacklisted_token)
            db.commit()
            logger.info("Token blacklisted successfully")
        except Exception as e:
            logger.error(f"Error blacklisting token: {str(e)}")
            db.rollback()

        # Clear session
        request.session.clear()
        logger.info("Session cleared")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"detail": "Successfully logged out"}
        )

    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        logger.exception("Full traceback:")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal server error: {str(e)}"}
        )

@router.get("/reset-password")
async def reset_password_page(request: Request):
    """Render password reset request page."""
    return templates.TemplateResponse(
        "auth/reset_password.html",
        {"request": request},
    )

@router.post("/request-password-reset")
async def reset_password(
    request: Request,
    form_data: PasswordReset,
    db: DBSession = Depends(get_db),
):
    """Handle password reset request.
    
    Generates a reset token and sends it via email.
    In test mode, email sending is disabled.
    """
    user = db.query(User).filter(User.email == form_data.email).first()
    if user:
        # Generate reset token
        token = create_access_token(
            data={"sub": user.username, "type": "reset"},
            scopes=["auth:reset-password"]
        )
        user.reset_token = token
        user.reset_token_expires = datetime.now() + timedelta(hours=1)
        db.commit()
        
        # Send reset email
        if not os.getenv("TESTING"):  # Skip email sending in tests
            await send_reset_password_email(user.email, token)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Password reset email sent"}
    )

@router.post("/reset-password")
async def reset_password_confirm(
    request: Request,
    form_data: PasswordResetConfirm,
    db: DBSession = Depends(get_db),
):
    """Handle password reset confirmation.
    
    - Verifies the reset token
    - Updates the password using the User model's set_password method
    - Clears the reset token
    - Returns 200 on success
    """
    try:
        # Verify token
        user = db.query(User).filter(User.reset_token == form_data.token).first()
        if os.getenv("TESTING"):
            print(f"Reset password request for token: {form_data.token}")
            print(f"Found user: {user.username if user else None}")
            if user:
                print(f"Token expiry: {user.reset_token_expires}")
                print(f"Current time: {datetime.now()}")

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )
        
        if not user.reset_token_expires:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )
        
        if user.reset_token_expires < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )
        
        # Get a fresh instance of the user
        user = db.query(User).filter(User.id == user.id).first()
        if os.getenv("TESTING"):
            print(f"\n=== Password Reset Handler ===")
            print(f"Current password hash: {user.hashed_password}")
        
        # Set the new password using the model's method
        user.set_password(form_data.new_password)
        if os.getenv("TESTING"):
            print(f"New password hash after set_password: {user.hashed_password}")
        
        # Clear reset token
        user.reset_token = None
        user.reset_token_expires = None
        user.last_password_change = datetime.now()
        
        # Commit changes
        db.commit()
        db.refresh(user)
        
        if os.getenv("TESTING"):
            print(f"Final password hash after commit: {user.hashed_password}")
            # Verify the password was set correctly
            verify_result = user.verify_password(form_data.new_password)
            print(f"Password verification result: {verify_result}")
            print(f"Using password: {form_data.new_password}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Password reset successful"}
        )
    except HTTPException:
        raise
    except Exception as e:
        if os.getenv("TESTING"):
            print(f"Unexpected error in reset_password_confirm: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )

@router.get("/me")
async def get_current_user(
    request: Request,
    token_data: TokenData = Depends(verify_token_dependency),
    db: DBSession = Depends(get_db),
):
    """Get current user profile."""
    try:
        if not token_data:
            logger.error("No token data provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )
            
        if not token_data.username:
            logger.error("Token data missing username")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token data",
            )

        logger.info(f"Getting current user profile for: {token_data.username}")
        user = db.query(User).filter(User.username == token_data.username).first()
        if not user:
            logger.error(f"User not found: {token_data.username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
            
        if not user.is_active:
            logger.error(f"Inactive user attempted access: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is inactive",
            )
            
        # Check if token is blacklisted
        blacklisted = db.query(BlacklistedToken).filter(
            BlacklistedToken.token == request.headers.get("Authorization", "").replace("Bearer ", "")
        ).first()
        if blacklisted:
            logger.error(f"Blacklisted token used for user: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )
            
        logger.info(f"User found: {user.username}, Role: {user.role}")
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value if user.role else None,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "last_login": user.last_login,
        }
        
    except HTTPException as he:
        logger.error(f"HTTP Exception in get_current_user: {str(he)}")
        logger.error(f"Request headers: {dict(request.headers)}")
        raise
    except Exception as e:
        logger.exception("Unexpected error in get_current_user")
        logger.error(f"Request headers: {dict(request.headers)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )