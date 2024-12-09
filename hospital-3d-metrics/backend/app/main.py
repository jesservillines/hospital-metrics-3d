from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routes import router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hospital Metrics API")

# Configure CORS with more detailed settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default port
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Add middleware to log requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request path: {request.url.path}")
    response = await call_next(request)
    return response

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hospital Metrics API. Use /api/v1/ endpoints for data access."}