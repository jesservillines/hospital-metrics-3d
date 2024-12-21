from fastapi import Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import time
import os

# Rate limiting configuration
limiter = Limiter(key_func=get_remote_address)

# Standard rate limit: 200 requests per 15 minutes
@limiter.limit("200/15minutes")
async def standard_rate_limit(request: Request):
    return True

# Authentication rate limit: 5 attempts per 15 minutes in production, 100 in testing
@limiter.limit("100/15minutes" if os.getenv("TESTING") else "5/15minutes")
async def auth_rate_limit(request: Request):
    return True

class RequestValidationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        """Validate requests and apply rate limiting.
        
        - Adds request timestamp
        - Validates content type for POST/PUT requests
        - Applies rate limiting based on endpoint:
          * Auth endpoints: 5/15min
          * Standard endpoints: 200/15min
        - Skips validation and rate limiting in test mode
        """
        # Add request timestamp
        request.state.start_time = time.time()
        
        # Skip rate limiting and validation for tests
        if os.getenv("TESTING"):
            return await call_next(request)
        
        path = request.url.path

        # Skip content type check for form submissions
        form_endpoints = ["/api/v1/auth/login", "/api/v1/auth/register"]
        if request.method == "POST" and path in form_endpoints:
            return await call_next(request)

        # Validate content type for POST/PUT requests
        if request.method in ["POST", "PUT"] and "json" not in request.headers.get("content-type", "").lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content-Type must be application/json"
            )
        
        # Apply rate limiting based on endpoint
        try:
            if path.startswith("/api/v1/auth"):
                # Stricter rate limiting for auth endpoints
                await auth_rate_limit(request)
            else:
                # Standard rate limiting for other endpoints
                await standard_rate_limit(request)
        except RateLimitExceeded as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e)
            )
            
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

def setup_middleware(app):
    """Configure middleware for the application.
    
    Sets up:
    - CORS with allowed origins
    - HTTPS redirect (production only)
    - Request validation and rate limiting
    - Session handling
    """
    # Session middleware (must be first)
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv("SECRET_KEY", "your-secret-key-for-dev"),
        max_age=60 * 60 * 24 * 7,  # 7 days
    )
    
    # CORS middleware
    allowed_origins = [
        "http://localhost:3000",  # Development frontend
        "http://localhost:5173",  # Vite dev server
    ]
    
    # Add production origin if defined
    if os.getenv("FRONTEND_URL"):
        allowed_origins.append(os.getenv("FRONTEND_URL"))
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type",
            "Authorization",
            "Accept",
            "Origin",
            "X-Requested-With",
        ],
        expose_headers=["Content-Length"],
        max_age=600,  # Cache preflight requests for 10 minutes
    )
    
    # HTTPS redirect only in production
    if os.getenv("ENV") == "production":
        app.add_middleware(HTTPSRedirectMiddleware)
    
    # Custom request validation and rate limiting
    app.add_middleware(RequestValidationMiddleware)
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)