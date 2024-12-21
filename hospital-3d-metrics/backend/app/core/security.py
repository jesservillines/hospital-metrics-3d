from datetime import datetime, timedelta, timezone
from typing import Optional, List
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, constr
import os
from fastapi.security import OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer
from fastapi import Depends, HTTPException, status, Request
import re
from slowapi import Limiter
from slowapi.util import get_remote_address
from authlib.oauth2 import OAuth2Error
from .oauth2_config import oauth2_settings
import secrets
import base64
import logging
from starlette.config import Config
from ..database import get_db
from ..models.blacklisted_token import BlacklistedToken  # Update import statement
from ..models.user import User  # Import here to avoid circular imports
from .password import verify_password, get_password_hash, verify_password_strength

# Load environment variables
config = Config(".env" if os.path.exists(".env") else None)

# Security configurations
SECRET_KEY = config("SECRET_KEY", default="your-secret-key-for-development")
ALGORITHM = oauth2_settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = oauth2_settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = oauth2_settings.REFRESH_TOKEN_EXPIRE_DAYS

# Rate limiting
if os.getenv("TESTING"):
    # Disable rate limiting in test environment
    class NoLimitLimiter:
        def limit(self, key_func):
            def decorator(func):
                async def wrapped(*args, **kwargs):
                    return await func(*args, **kwargs)
                return wrapped
            return decorator
        
        def __call__(self, *args, **kwargs):
            return self.limit(lambda: "test")
    limiter = NoLimitLimiter()
else:
    limiter = Limiter(key_func=get_remote_address, config_filename=".env" if os.path.exists(".env") else None)

# OAuth2 schemes
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scopes={
        "metrics:read": "Read access to metrics",
        "metrics:write": "Write access to metrics",
        "profile:read": "Read access to user profile",
        "offline_access": "Ability to use refresh tokens"
    }
)

oauth2_code_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="/api/v1/auth/authorize",
    tokenUrl="/api/v1/auth/login"
)

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None
    expires_in: int
    scope: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []
    client_id: Optional[str] = None
    exp: Optional[datetime] = None

class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    password: str
    role: Optional[str] = "viewer"

logger = logging.getLogger(__name__)

def create_access_token(
    data: dict,
    scopes: List[str],
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "scope": " ".join(scopes),
        "token_type": "access_token"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(
    data: dict,
    scopes: List[str]
) -> tuple[str, datetime]:
    to_encode = data.copy()
    expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp": expire,
        "scope": " ".join(scopes),
        "token_type": "refresh_token"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire

def verify_token(token: str, db) -> TokenData:
    """Verify a JWT token.
    
    Performs the following checks:
    1. Verifies token signature using SECRET_KEY
    2. Validates token expiration
    3. Checks if token is blacklisted
    
    Returns TokenData containing username, expiry, scope, and token type.
    Raises HTTPException with 401 status if validation fails.
    """
    try:
        logger.debug(f"Verifying token: {token[:10]}...")
        
        # First verify token signature and expiry
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_signature": True},
        )
        logger.debug(f"Token payload: {payload}")
        
        username: str = payload.get("sub")
        if not username:
            logger.error("Token missing 'sub' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check token expiration
        exp = payload.get("exp")
        if not exp:
            logger.error("Token missing 'exp' claim")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
        if datetime.now(timezone.utc) >= exp_datetime:
            logger.error(f"Token expired at {exp_datetime}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if token is blacklisted
        blacklisted = db.query(BlacklistedToken).filter(
            BlacklistedToken.token == token
        ).first()
        
        if blacklisted:
            logger.error("Token is blacklisted")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token_data = TokenData(
            username=username,
            exp=exp_datetime,
            scope=payload.get("scope", ""),
            token_type=payload.get("token_type", ""),
        )
        logger.debug(f"Token verified successfully for user: {username}")
        
        return token_data
    except JWTError as e:
        logger.error(f"JWT verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def verify_token_dependency(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db)
) -> TokenData:
    """Verify a JWT token. This is a FastAPI dependency.
    
    Use this as a dependency to protect routes that require authentication.
    Returns TokenData if token is valid, raises HTTPException if not.
    """
    return verify_token(token, db)

async def get_current_user(
    token_data: TokenData = Depends(verify_token_dependency),
    db = Depends(get_db)
):
    """Get the current authenticated user."""
    
    if not token_data.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.username == token_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def generate_authorization_code() -> str:
    """Generate a secure authorization code."""
    return secrets.token_urlsafe(32)

def verify_client_secret(client_secret: str, hashed_secret: str) -> bool:
    """Verify a client secret against its hash."""
    return verify_password(client_secret, hashed_secret)

def hash_client_secret(client_secret: str) -> str:
    """Hash a client secret."""
    return get_password_hash(client_secret)

def generate_client_credentials() -> tuple[str, str]:
    """Generate a new client ID and secret."""
    client_id = secrets.token_urlsafe(32)
    client_secret = secrets.token_urlsafe(32)
    return client_id, client_secret

def verify_pkce_challenge(code_verifier: str, code_challenge: str, method: str = "S256") -> bool:
    """Verify PKCE code challenge."""
    if method == "S256":
        import hashlib
        code_challenge_computed = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")
        return code_verifier == code_challenge_computed
    elif method == "plain":
        return code_verifier == code_challenge
    else:
        raise OAuth2Error("Unsupported PKCE transform method")