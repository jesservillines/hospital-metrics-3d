import os
import sys
from sqlalchemy_utils import database_exists, create_database, drop_database
from sqlalchemy import create_engine, text
from pathlib import Path
import csv

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import settings
from app.database import DatabaseConfig

def reset_database():
    """Reset the database by dropping and recreating it."""
    config = DatabaseConfig()
    
    # Construct database URL
    if config.db_type == 'postgresql':
        db_url = f'postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database}'
    else:
        raise ValueError(f"Unsupported database type: {config.db_type}")

    print(f"Checking database {config.database}...")
    
    # Drop database if it exists
    if database_exists(db_url):
        print(f"Dropping existing database {config.database}...")
        drop_database(db_url)
    
    # Create new database
    print(f"Creating new database {config.database}...")
    create_database(db_url)
    
    # Run migrations
    print("Running database migrations...")
    os.system("alembic upgrade head")
    
    # Create admin user
    print("Creating admin user...")
    os.system("python create_admin.py admin admin@example.com admin123")
    
    # Import seed data
    print("Importing seed data...")
    engine = create_engine(db_url)
    
    # Import floor metrics
    with engine.connect() as conn:
        print("Importing floor metrics...")
        with open('data/floor_metrics.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Get metric category from the row or default to 'unknown'
                metric_category = row.get('metric_category', 'unknown')
                floor_id = row.get('floor_id', row['floor'].lower().replace(' ', '_'))
                
                conn.execute(
                    text("""
                    INSERT INTO floor_metrics (floor_name, metric_name, value, timestamp, metric_category, floor_id)
                    VALUES (:floor, :metric_name, :value, :timestamp, :metric_category, :floor_id)
                    """),
                    {
                        'floor': row['floor'],
                        'metric_name': row['metric_name'],
                        'value': float(row['value']),
                        'timestamp': row['timestamp'],
                        'metric_category': metric_category,
                        'floor_id': floor_id
                    }
                )
        
        print("Importing room metrics...")
        with open('data/room_metrics.csv', 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Get metric category from the row or default to 'unknown'
                metric_category = row.get('metric_category', 'unknown')
                floor_id = row.get('floor_id', '')
                room_id = row.get('room_id', '')
                
                conn.execute(
                    text("""
                    INSERT INTO room_metrics (floor_id, room_id, metric_name, value, timestamp, metric_category)
                    VALUES (:floor_id, :room_id, :metric_name, :value, :timestamp, :metric_category)
                    """),
                    {
                        'floor_id': floor_id,
                        'room_id': room_id,
                        'metric_name': row['metric_name'],
                        'value': float(row['value']),
                        'timestamp': row['timestamp'],
                        'metric_category': metric_category
                    }
                )
        
        conn.commit()

if __name__ == "__main__":
    reset_database()
