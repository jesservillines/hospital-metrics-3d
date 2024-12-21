from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
import ssl
from urllib.parse import quote_plus
import logging

logger = logging.getLogger(__name__)

def get_database_url():
    """
    Construct database URL from environment variables with proper escaping.
    Supports both individual credential vars and full DATABASE_URL.
    """
    if os.getenv("DATABASE_URL"):
        return os.getenv("DATABASE_URL")
    
    db_params = {
        "user": os.getenv("DB_USER", "postgres"),
        "password": quote_plus(os.getenv("DB_PASSWORD", "")),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "database": os.getenv("DB_NAME", "hospital_metrics"),
    }
    
    ssl_mode = os.getenv("DB_SSL_MODE", "prefer")
    return f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}?sslmode={ssl_mode}"

def create_db_engine():
    """
    Create SQLAlchemy engine with proper configuration based on environment.
    """
    database_url = get_database_url()
    
    # Base connection arguments
    connect_args = {
        "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "10")),
        "application_name": "hospital_metrics_app",
    }
    
    # Add SSL configuration if required
    if os.getenv("DB_SSL_MODE") in ["require", "verify-full"]:
        ssl_context = ssl.create_default_context()
        if os.getenv("DB_SSL_CA"):
            ssl_context.load_verify_locations(os.getenv("DB_SSL_CA"))
        connect_args["ssl_context"] = ssl_context
    
    # Create engine with connection pooling
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
        pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
        pool_pre_ping=True,  # Enable connection health checks
        connect_args=connect_args,
    )
    
    return engine

def get_db_session():
    """
    Create a database session factory.
    """
    engine = create_db_engine()
    SessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )
    return SessionLocal

def verify_db_connection():
    """
    Verify database connection and configuration.
    """
    try:
        engine = create_db_engine()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection verified successfully")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

# Create session factory
SessionLocal = get_db_session()
