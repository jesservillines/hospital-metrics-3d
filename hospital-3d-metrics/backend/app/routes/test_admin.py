from fastapi import APIRouter, Depends, HTTPException
from .test_auth import get_current_user

router = APIRouter()

@router.get("/status")
async def get_admin_status(current_user = Depends(get_current_user)):
    """Simple admin status endpoint for testing."""
    return {"status": "ok", "user": current_user}
