from passlib.context import CryptContext
import re

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def verify_password_strength(password: str) -> bool:
    """
    Verify password meets complexity requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 12:
        return False
    
    if not re.search(r"[A-Z]", password):
        return False
    
    if not re.search(r"\d", password):
        return False
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    
    return True
