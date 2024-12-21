from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from urllib.parse import quote_plus
import os
from contextlib import contextmanager
from typing import Generator
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create declarative base
Base = declarative_base()

class DatabaseConfig:
    """Database configuration handling both PostgreSQL and SQL Server"""
    def __init__(self):
        self.db_type = os.getenv('DB_TYPE', 'postgresql')  # or 'mssql'
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')  # PostgreSQL default port
        self.database = os.getenv('DB_NAME', 'hospital_metrics')
        self.username = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', '')
        
        # Connection pool settings
        self.pool_size = int(os.getenv('DB_POOL_SIZE', '5'))
        self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', '10'))
        self.pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', '30'))
        
        # Validate database type
        if self.db_type not in ['postgresql', 'mssql']:
            raise ValueError("DB_TYPE must be either 'postgresql' or 'mssql'")
        
        # Log configuration (without password)
        logger.info(f"Database config: type={self.db_type}, host={self.host}, "
                   f"port={self.port}, database={self.database}, user={self.username}")
        logger.info(f"Password length: {len(self.password)}")

    def get_connection_string(self) -> str:
        """Construct database URL based on database type"""
        if not self.password:
            logger.error("No database password provided")
            
        if self.db_type == 'postgresql':
            url = (
                f'postgresql://{self.username}:{quote_plus(self.password)}'
                f'@{self.host}:{self.port}/{self.database}'
            )
            logger.info(f"Connection URL (without password): "
                       f"postgresql://{self.username}:***@{self.host}:{self.port}/{self.database}")
            return url
        else:
            url = (
                f'mssql+pyodbc://{self.username}:{quote_plus(self.password)}'
                f'@{self.host}:{self.port}/{self.database}'
                f'?driver=ODBC+Driver+17+for+SQL+Server'
            )
            logger.info(f"Connection URL (without password): "
                       f"mssql+pyodbc://{self.username}:***@{self.host}:{self.port}/{self.database}")
            return url

def get_engine(config: DatabaseConfig = None):
    """Create SQLAlchemy engine with connection pooling"""
    if config is None:
        config = DatabaseConfig()
        
    return create_engine(
        config.get_connection_string(),
        poolclass=QueuePool,
        pool_size=config.pool_size,
        max_overflow=config.max_overflow,
        pool_timeout=config.pool_timeout,
        pool_pre_ping=True,  # Enable connection health checks
    )

# Create engine instance
engine = get_engine()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """Database session context manager"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def check_db_connection():
    """Test database connection"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False
    finally:
        db.close()