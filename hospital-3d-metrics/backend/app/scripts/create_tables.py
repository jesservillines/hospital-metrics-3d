import sys
import os
import pandas as pd
from datetime import datetime
from sqlalchemy import inspect, text

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database import engine, Base, get_db
from app.models.metrics import FloorMetric, RoomMetric, MetricDefinition
from app.core.config import settings

def recreate_tables():
    """Drop and recreate all tables."""
    with engine.begin() as conn:
        # Drop all tables and their dependencies
        conn.execute(text("""
            DROP TABLE IF EXISTS floor_metrics CASCADE;
            DROP TABLE IF EXISTS room_metrics CASCADE;
            DROP TABLE IF EXISTS metric_definitions CASCADE;
        """))
        print("Dropped all tables.")
        
        # Create metric_definitions table
        conn.execute(text("""
            CREATE TABLE metric_definitions (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description VARCHAR(500),
                unit VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        print("Created metric_definitions table.")
        
        # Create floor_metrics table
        conn.execute(text("""
            CREATE TABLE floor_metrics (
                id SERIAL PRIMARY KEY,
                floor VARCHAR,
                floor_id VARCHAR,
                metric_name VARCHAR,
                value FLOAT,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                metric_category VARCHAR,
                meta_data JSON,
                metric_id INTEGER REFERENCES metric_definitions(id)
            );
            CREATE INDEX ix_floor_metrics_floor ON floor_metrics (floor);
            CREATE INDEX ix_floor_metrics_floor_id ON floor_metrics (floor_id);
        """))
        print("Created floor_metrics table.")
        
        # Create room_metrics table
        conn.execute(text("""
            CREATE TABLE room_metrics (
                id SERIAL PRIMARY KEY,
                room_id VARCHAR,
                floor VARCHAR,
                floor_id VARCHAR,
                metric_name VARCHAR,
                value FLOAT,
                timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                metric_category VARCHAR,
                meta_data JSON,
                metric_id INTEGER REFERENCES metric_definitions(id)
            );
            CREATE INDEX ix_room_metrics_room_id ON room_metrics (room_id);
            CREATE INDEX ix_room_metrics_floor ON room_metrics (floor);
            CREATE INDEX ix_room_metrics_floor_id ON room_metrics (floor_id);
        """))
        print("Created room_metrics table.")

def import_metrics():
    """Import metrics from CSV files."""
    db = next(get_db())
    try:
        # Import floor metrics
        floor_df = pd.read_csv("data/floor_metrics.csv")
        # Clean column names
        floor_df.columns = floor_df.columns.str.strip()
        for _, row in floor_df.iterrows():
            metric = FloorMetric(
                floor=row["floor"],
                floor_id=row["floor_id"],
                metric_name=row["metric_name"],
                value=row["value"],
                timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d"),
                metric_category=row["metric_category"]
            )
            db.add(metric)
        
        # Import room metrics
        room_df = pd.read_csv("data/room_metrics.csv")
        # Clean column names
        room_df.columns = room_df.columns.str.strip()
        for _, row in room_df.iterrows():
            metric = RoomMetric(
                room_id=row["room_id"],
                floor=row["floor"],
                floor_id=row["floor_id"],
                metric_name=row["metric_name"],
                value=row["value"],
                timestamp=datetime.strptime(row["timestamp"], "%Y-%m-%d"),
                metric_category=row["metric_category"]
            )
            db.add(metric)
        
        db.commit()
        print("Imported metrics data successfully.")
        
    except Exception as e:
        db.rollback()
        print(f"Error importing metrics: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Recreating tables...")
    recreate_tables()
    print("Importing metrics...")
    import_metrics()
    print("Done.")
