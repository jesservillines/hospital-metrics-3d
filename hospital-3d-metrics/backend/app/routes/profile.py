from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.routes.auth import get_current_user, verify_token_dependency
from app.models.user import User, UserRole
from app.core.password import get_password_hash
import logging
import os
import traceback

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join("app", "templates"))
logger = logging.getLogger(__name__)

@router.get("/", response_class=HTMLResponse)
@router.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    token_data = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Render the profile page based on user role."""
    try:
        logger.info(f"Profile page request - Token data: {token_data}")
        logger.info(f"Request path: {request.url.path}")
        logger.info(f"Request headers: {dict(request.headers)}")

        if not token_data:
            logger.error("No token data provided")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"}
            )
        
        if not token_data.username:
            logger.error("Token data missing username")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid token data"}
            )
        
        # Get user from database
        user = db.query(User).filter(User.username == token_data.username).first()
        if not user:
            logger.error(f"User not found for username: {token_data.username}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "User not found"}
            )
            
        logger.info(f"User found: {user.username}, Role: {user.role}")
        
        # Verify user is active
        if not user.is_active:
            logger.error(f"Inactive user attempted to access profile: {user.username}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "User account is inactive"}
            )
        
        # Select template based on role
        template_name = "profile/user_profile.html"  # Default to user profile
        if user.role == UserRole.ADMIN:
            logger.info(f"Redirecting admin user to admin profile")
            return RedirectResponse(url="/api/v1/admin/profile", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
            
        logger.info(f"Using template: {template_name}")
        
        try:
            response = templates.TemplateResponse(
                template_name,
                {
                    "request": request,
                    "user": user,
                    "UserRole": UserRole
                }
            )
            logger.info(f"Template response generated successfully")
            return response
        except Exception as template_error:
            logger.error(f"Template error: {str(template_error)}")
            logger.error(f"Template traceback: {traceback.format_exc()}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Error rendering template"}
            )
        
    except HTTPException as he:
        logger.error(f"HTTP Exception in profile_page: {str(he)}")
        logger.error(f"HTTP Exception traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=he.status_code,
            content={"detail": str(he.detail)}
        )
    except Exception as e:
        logger.exception("Unexpected error in profile_page")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal server error: {str(e)}"}
        )

@router.post("/update")
@router.post("/profile/update")
async def update_profile(
    request: Request,
    email: str = Form(...),
    current_password: str = Form(None),
    new_password: str = Form(None),
    token_data = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Update user profile."""
    try:
        logger.info(f"Profile update request - Token data: {token_data}")
        logger.info(f"Request path: {request.url.path}")
        logger.info(f"Form data: email={email}, has_current_password={bool(current_password)}, has_new_password={bool(new_password)}")
        
        # Get user from database
        user = db.query(User).filter(User.username == token_data.username).first()
        if not user:
            logger.error(f"User not found for username: {token_data.username}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "User not found"}
            )

        # Verify current password if changing password
        if new_password:
            logger.info("Password change requested")
            if not user.verify_password(current_password):
                logger.warning(f"Invalid current password for user: {user.username}")
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"detail": "Current password is incorrect"}
                )
            user.hashed_password = get_password_hash(new_password)
            logger.info("Password updated successfully")

        user.email = email
        db.commit()
        logger.info(f"Profile updated successfully for user: {user.username}")

        return RedirectResponse(
            url="/profile",
            status_code=status.HTTP_302_FOUND
        )
    except HTTPException as he:
        logger.error(f"HTTP Exception in update_profile: {str(he)}")
        logger.error(f"HTTP Exception traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=he.status_code,
            content={"detail": str(he.detail)}
        )
    except Exception as e:
        logger.exception("Error updating profile")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)}
        )

@router.get("/activity")
@router.get("/profile/activity")
async def get_user_activity(
    request: Request,
    token_data = Depends(verify_token_dependency),
    db: Session = Depends(get_db)
):
    """Get user activity history."""
    try:
        logger.info(f"Activity request - Token data: {token_data}")
        logger.info(f"Request path: {request.url.path}")
        
        # Get user from database
        user = db.query(User).filter(User.username == token_data.username).first()
        if not user:
            logger.error(f"User not found for username: {token_data.username}")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"detail": "User not found"}
            )

        # Get user sessions
        sessions = []  # TODO: Implement session tracking
        logger.info(f"Retrieved {len(sessions)} sessions for user: {user.username}")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"sessions": sessions}
        )
    except HTTPException as he:
        logger.error(f"HTTP Exception in get_user_activity: {str(he)}")
        logger.error(f"HTTP Exception traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=he.status_code,
            content={"detail": str(he.detail)}
        )
    except Exception as e:
        logger.exception("Error getting user activity")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)}
        )
