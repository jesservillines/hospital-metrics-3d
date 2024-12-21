from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os
import sys
import ssl
from urllib.parse import quote_plus

def create_db_url(host, port, user, password, db_name, ssl_mode='require'):
    """Create database URL with proper escaping and SSL configuration."""
    escaped_password = quote_plus(password)
    return f"postgresql://{user}:{escaped_password}@{host}:{port}/{db_name}?sslmode={ssl_mode}"

def test_db_connection(db_url):
    """Test database connection with the provided credentials."""
    try:
        # Create engine with SSL configuration
        engine = create_engine(
            db_url,
            connect_args={
                'sslmode': 'require',
                'ssl': {
                    'cert_reqs': ssl.CERT_REQUIRED,
                    'ca_certs': os.getenv('SSL_CERT_FILE', None)
                }
            } if 'sslmode=require' in db_url else {}
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"Successfully connected to PostgreSQL: {version}")
        return True
    except SQLAlchemyError as e:
        print(f"Error connecting to database: {str(e)}")
        return False

def main():
    # Database configuration
    config = {
        'DB_HOST': os.getenv('DB_HOST', 'localhost'),
        'DB_PORT': os.getenv('DB_PORT', '5432'),
        'DB_USER': os.getenv('DB_USER', 'hospital_metrics_y1e8wgay'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD', '0CM%D#ZKyHcX6#PgoY3wo9!S5lEQZI0Y'),
        'DB_NAME': os.getenv('DB_NAME', 'hospital_metrics_prod_0900f37a'),
        'SSL_MODE': os.getenv('DB_SSL_MODE', 'require')
    }
    
    # Create database URL
    db_url = create_db_url(
        config['DB_HOST'],
        config['DB_PORT'],
        config['DB_USER'],
        config['DB_PASSWORD'],
        config['DB_NAME'],
        config['SSL_MODE']
    )
    
    print("\nTesting database connection...")
    if test_db_connection(db_url):
        print("\nDatabase connection successful!")
        print("\nAdd these settings to your .env.production file:")
        print("----------------------------------------")
        print(f"DB_HOST={config['DB_HOST']}")
        print(f"DB_PORT={config['DB_PORT']}")
        print(f"DB_USER={config['DB_USER']}")
        print(f"DB_PASSWORD={config['DB_PASSWORD']}")
        print(f"DB_NAME={config['DB_NAME']}")
        print(f"DB_SSL_MODE={config['SSL_MODE']}")
        print("\nOr use the complete DATABASE_URL:")
        print("----------------------------------------")
        print(f"DATABASE_URL={db_url}")
    else:
        print("\nFailed to connect to database. Please check your credentials and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
