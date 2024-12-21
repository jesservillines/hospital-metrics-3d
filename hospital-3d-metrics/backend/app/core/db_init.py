import os
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from ..database import engine, SessionLocal, init_db
from ..models import (
    MetricDefinition, Floor, Room, RoomMetric, FloorMetric,
    MetricCategory, Base
)
import logging

logger = logging.getLogger(__name__)

def create_tables():
    """Create all database tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def load_csv_data(db: Session):
    """Load initial data from CSV files"""
    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
    
    # Load floor metrics
    logger.info("Loading floor metrics data...")
    floor_metrics_path = os.path.join(data_dir, 'floor_metrics.csv')
    if os.path.exists(floor_metrics_path):
        df_floor = pd.read_csv(floor_metrics_path)
        
        # Create unique floors
        unique_floors = df_floor[['floor', 'floor_id']].drop_duplicates()
        for _, row in unique_floors.iterrows():
            floor = Floor(
                floor_id=row['floor_id'],
                name=row['floor'],
                building=row['floor'].split()[1],  # "East" or "West"
                level=int(row['floor'].split()[0])  # Floor number
            )
            db.add(floor)
        
        # Create metric definitions from floor metrics
        metric_defs = {}
        for _, row in df_floor.drop_duplicates('metric_name').iterrows():
            metric_def = MetricDefinition(
                name=row['metric_name'],
                display_name=row['metric_name'].replace('_', ' ').title(),
                category=row['metric_category'],
                data_type='numeric',
                aggregation_type='avg'
            )
            db.add(metric_def)
            db.flush()  # Get the ID
            metric_defs[row['metric_name']] = metric_def.id
        
        # Add floor metrics
        for _, row in df_floor.iterrows():
            floor_metric = FloorMetric(
                floor_id=row['floor_id'],
                metric_id=metric_defs[row['metric_name']],
                value=float(row['value']),
                timestamp=datetime.strptime(row['timestamp'], '%Y-%m-%d'),
                is_calculated=False
            )
            db.add(floor_metric)
    
    # Load room metrics
    logger.info("Loading room metrics data...")
    room_metrics_path = os.path.join(data_dir, 'room_metrics.csv')
    if os.path.exists(room_metrics_path):
        df_room = pd.read_csv(room_metrics_path)
        
        # Create rooms
        unique_rooms = df_room[['room_id', 'floor_id']].drop_duplicates()
        for _, row in unique_rooms.iterrows():
            room = Room(
                room_id=row['room_id'],
                floor_id=row['floor_id'],
                room_type='patient' if row['room_id'].startswith('P') else 'staff'
            )
            db.add(room)
        
        # Add room metrics
        for _, row in df_room.iterrows():
            # Check if metric definition exists, if not create it
            metric_name = row['metric_name']
            if metric_name not in metric_defs:
                metric_def = MetricDefinition(
                    name=metric_name,
                    display_name=metric_name.replace('_', ' ').title(),
                    category=row['metric_category'],
                    data_type='numeric',
                    aggregation_type='avg'
                )
                db.add(metric_def)
                db.flush()
                metric_defs[metric_name] = metric_def.id
            
            room_metric = RoomMetric(
                room_id=row['room_id'],
                metric_id=metric_defs[metric_name],
                value=float(row['value']),
                timestamp=datetime.strptime(row['timestamp'], '%Y-%m-%d')
            )
            db.add(room_metric)
    
    try:
        db.commit()
        logger.info("Data loaded successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error loading data: {str(e)}")
        raise

def init_database():
    """Initialize database and load initial data"""
    try:
        create_tables()
        db = SessionLocal()
        try:
            load_csv_data(db)
        finally:
            db.close()
        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_database()
