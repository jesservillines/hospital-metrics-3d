from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.routes.auth import verify_token_dependency
from app.models.user import User, UserRole, RoleAccess
import logging
import os
import traceback

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join("app", "templates"))
logger = logging.getLogger(__name__)

def check_admin_access(token_data = Depends(verify_token_dependency), db: Session = Depends(get_db)):
    """Verify admin access."""
    try:
        logger.info(f"Checking admin access for token data: {token_data}")
        user = db.query(User).filter(User.username == token_data.username).first()
        if not user:
            logger.error(f"User not found: {token_data.username}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if user.role != UserRole.ADMIN:
            logger.error(f"Non-admin user attempted admin access: {user.username} (role: {user.role})")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        logger.info(f"Admin access granted for user: {user.username}")
        return user
    except Exception as e:
        logger.error(f"Error in check_admin_access: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def get_users(current_user: User = Depends(check_admin_access), db: Session = Depends(get_db)):
    """Get all users."""
    try:
        users = db.query(User).all()
        return [
            {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": str(user.role),
                "is_active": user.is_active,
                "last_login": user.last_login
            }
            for user in users
        ]
    except Exception as e:
        logger.exception("Error getting users")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/admin/users")
async def get_users_route(current_user: User = Depends(check_admin_access), db: Session = Depends(get_db)):
    return get_users(current_user, db)

@router.get("/admin/users/{user_id}")
async def get_user(
    user_id: str,
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Get user details."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": str(user.role),
            "is_active": user.is_active,
            "last_login": user.last_login
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting user details")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/admin/users/{user_id}")
async def update_user(
    user_id: str,
    user_data: dict,
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Update user details."""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # Don't allow changing admin status of the last admin
        if user.role == UserRole.ADMIN and user_data.get("role") != "ADMIN":
            admin_count = db.query(User).filter(User.role == UserRole.ADMIN).count()
            if admin_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot remove the last admin"
                )
        
        if "email" in user_data:
            user.email = user_data["email"]
        if "role" in user_data:
            user.role = UserRole[user_data["role"]]
        if "is_active" in user_data:
            user.is_active = user_data["is_active"]
            
        db.commit()
        return {"message": "User updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error updating user")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/admin/roles")
async def get_roles(current_user: User = Depends(check_admin_access), db: Session = Depends(get_db)):
    """Get all roles and their access levels."""
    try:
        roles = db.query(RoleAccess).all()
        return [
            {
                "id": str(role.id),
                "name": role.role_name,
                "access": {
                    "patient": role.patient_access,
                    "staff": role.staff_access,
                    "resource": role.resource_access
                }
            }
            for role in roles
        ]
    except Exception as e:
        logger.exception("Error getting roles")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/admin/roles")
async def create_role(
    role_data: dict,
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Create a new role."""
    try:
        # Check if role already exists
        if db.query(RoleAccess).filter(RoleAccess.role_name == role_data["name"]).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role already exists"
            )
            
        new_role = RoleAccess(
            role_name=role_data["name"],
            patient_access=role_data["access"]["patient"],
            staff_access=role_data["access"]["staff"],
            resource_access=role_data["access"]["resource"]
        )
        
        db.add(new_role)
        db.commit()
        
        return {"message": "Role created successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error creating role")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/admin/roles/{role_id}/access")
async def update_role_access(
    role_id: str,
    access_data: dict,
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Update role access levels."""
    try:
        role = db.query(RoleAccess).filter(RoleAccess.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
            
        # Don't allow modifying ADMIN role
        if role.role_name == "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify ADMIN role access"
            )
            
        data_type = access_data["data_type"]
        access = access_data["access"]
        
        if data_type == "patient":
            role.patient_access = access
        elif data_type == "staff":
            role.staff_access = access
        elif data_type == "resource":
            role.resource_access = access
            
        db.commit()
        return {"message": "Role access updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error updating role access")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/admin/roles/{role_id}")
async def delete_role(
    role_id: str,
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Delete a role."""
    try:
        role = db.query(RoleAccess).filter(RoleAccess.id == role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
            
        # Don't allow deleting ADMIN role
        if role.role_name == "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete ADMIN role"
            )
            
        # Check if any users are using this role
        if db.query(User).filter(User.role == role.role_name).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete role while users are assigned to it"
            )
            
        db.delete(role)
        db.commit()
        
        return {"message": "Role deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error deleting role")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/profile", response_class=HTMLResponse)
async def admin_profile(
    request: Request,
    current_user: User = Depends(check_admin_access),
    db: Session = Depends(get_db)
):
    """Render the admin profile page."""
    try:
        logger.info(f"Admin profile page request - Path: {request.url.path}")
        logger.info(f"Admin profile page request - User: {current_user.username}")
        logger.info(f"Admin profile page request - Headers: {dict(request.headers)}")
        
        try:
            # Get all roles for the dropdown
            roles = db.query(RoleAccess).all()
            logger.info(f"Found {len(roles)} roles")
            
            try:
                # Generate template response
                response = templates.TemplateResponse(
                    "profile/admin_profile.html",
                    {
                        "request": request,
                        "user": current_user,
                        "roles": roles,
                        "UserRole": UserRole
                    }
                )
                logger.info("Template response generated successfully")
                return response
            except Exception as template_error:
                logger.error(f"Template error: {str(template_error)}")
                logger.error(f"Template traceback: {traceback.format_exc()}")
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Error rendering template"}
                )
                
        except Exception as db_error:
            logger.error(f"Database error: {str(db_error)}")
            logger.error(f"Database traceback: {traceback.format_exc()}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Error accessing database"}
            )
            
    except HTTPException as he:
        logger.error(f"HTTP Exception in admin_profile: {str(he)}")
        logger.error(f"HTTP Exception traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=he.status_code,
            content={"detail": str(he.detail)}
        )
    except Exception as e:
        logger.error(f"Unexpected error in admin_profile: {str(e)}")
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"Internal server error: {str(e)}"}
        )
