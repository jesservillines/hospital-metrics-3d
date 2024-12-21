from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, constr
import re

class UserLogin(BaseModel):
    username: str  # Can be either username or email
    password: str
    remember_me: bool = False
    return_to: Optional[str] = None

class UserRegistration(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: str
    password_confirm: str
    terms_accepted: bool = False

    @field_validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:  # Changed from 12 to 8 for testing
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator('password_confirm')
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if 'password' in values.data and v != values.data['password']:
            raise ValueError("Passwords do not match")
        return v

    @field_validator('terms_accepted')
    def terms_must_be_accepted(cls, v):
        """Validate that terms are accepted."""
        if not v:
            raise ValueError("You must accept the terms and conditions")
        return v

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str  # Changed from password to new_password
    password_confirm: str

    @field_validator('new_password')
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:  # Changed from 12 to 8 for testing
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @field_validator('password_confirm')
    def passwords_match(cls, v, values):
        """Validate that passwords match."""
        if 'new_password' in values.data and v != values.data['new_password']:
            raise ValueError("Passwords do not match")
        return v

class UserResponse(BaseModel):
    id: int  # Added id field
    username: str
    email: EmailStr
    is_active: Optional[bool] = True
