from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.routes.auth import get_current_user
from app.models.user import User, UserRole
import numpy as np
from datetime import datetime, timedelta
import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join("app", "templates"))

@router.get("/visualization", response_class=HTMLResponse)
async def visualization_page(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Render the 3D visualization page."""
    return templates.TemplateResponse(
        "visualization.html",
        {"request": request, "user": current_user}
    )

@router.get("/api/v1/metrics/{data_source}")
async def get_metrics(
    data_source: str,
    time_range: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get metrics data for visualization."""
    try:
        # Role-based access control
        if data_source == "patients":
            if current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to access patient data"
                )
        elif data_source == "staff":
            if current_user.role not in [UserRole.ADMIN]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to access staff data"
                )
        
        # Example data generation - replace with actual database queries
        x = np.linspace(0, 10, 20)
        y = np.linspace(0, 10, 20)
        X, Y = np.meshgrid(x, y)
        
        if data_source == "patients":
            Z = np.sin(np.sqrt(X**2 + Y**2))
        elif data_source == "staff":
            Z = np.cos(np.sqrt(X**2 + Y**2))
        else:
            Z = np.exp(-(X**2 + Y**2)/10)
            
        return {
            "x": x.tolist(),
            "y": y.tolist(),
            "z": Z.flatten().tolist(),
            "values": Z.tolist(),
            "access_level": str(current_user.role)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
