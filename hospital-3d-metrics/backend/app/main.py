from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .core.middleware import setup_middleware
from .database import engine, Base
from .routes import api_router
from .core.security import verify_token_dependency
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hospital Metrics 3D",
    description="3D visualization of hospital metrics",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# Setup middleware
setup_middleware(app)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Set up templates
templates = Jinja2Templates(directory=os.path.join("app", "templates"))

@app.get("/")
async def home(request: Request):
    """Home page."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/auth/login")
async def auth_login_redirect():
    """Redirect /auth/login to /api/v1/auth/login."""
    return RedirectResponse(url="/api/v1/auth/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@app.get("/login")
async def login_redirect():
    """Redirect /login to /api/v1/auth/login."""
    return RedirectResponse(url="/api/v1/auth/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@app.get("/register")
async def register_redirect():
    """Redirect /register to /api/v1/auth/register."""
    return RedirectResponse(url="/api/v1/auth/register", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

@app.get("/profile")
async def profile_redirect():
    """Redirect /profile to /api/v1/profile."""
    return RedirectResponse(url="/api/v1/profile", status_code=status.HTTP_307_TEMPORARY_REDIRECT)

# Include routers
app.include_router(api_router, prefix="/api/v1")