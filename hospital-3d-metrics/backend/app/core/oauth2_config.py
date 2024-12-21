from datetime import timedelta
from typing import Optional, Dict, Any
from pydantic import BaseModel
import os

class OAuth2Settings(BaseModel):
    """OAuth2 configuration settings."""
    
    # Token settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"  # Changed to HS256 for testing
    
    # Client settings
    CLIENTS_REQUIRE_APPROVAL: bool = True
    
    # Scope settings
    DEFAULT_SCOPES: list[str] = [
        "metrics:read",      # Read access to metrics
        "metrics:write",     # Write access to metrics
        "profile:read",      # Read access to user profile
        "offline_access"     # Ability to use refresh tokens
    ]
    
    # OpenID Connect settings
    OIDC_ENABLED: bool = True
    OIDC_SCOPES: list[str] = [
        "openid",
        "profile",
        "email"
    ]
    
    # Authorization Code flow settings
    AUTH_CODE_EXPIRE_MINUTES: int = 10
    
    # Consent settings
    CONSENT_EXPIRE_DAYS: int = 365  # How long user consent is valid
    
    # Security settings
    REQUIRE_PKCE: bool = True  # Require PKCE for Authorization Code flow
    ROTATE_REFRESH_TOKENS: bool = True  # Issue new refresh token with access token
    
    # Rate limiting settings
    RATE_LIMIT_TOKEN_ENDPOINT: tuple[int, str] = (100, "1 minute")  # 100 requests per minute
    RATE_LIMIT_AUTH_ENDPOINT: tuple[int, str] = (20, "1 minute")   # 20 requests per minute
    
    class Config:
        env_prefix = "OAUTH2_"  # Environment variables should be prefixed with OAUTH2_
        env_file = ".env" if os.path.exists(".env") else None

oauth2_settings = OAuth2Settings()
