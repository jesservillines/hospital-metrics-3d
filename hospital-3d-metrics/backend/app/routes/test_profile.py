from fastapi import APIRouter, Depends
from .test_auth import get_current_user

router = APIRouter()

@router.get("/me")
async def get_my_profile(current_user = Depends(get_current_user)):
    """Simple profile endpoint for testing."""
    return {"profile": current_user}
