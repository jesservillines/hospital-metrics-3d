from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import pandas as pd
import logging
from app.database import get_db
from app.models.metrics import FloorMetric, RoomMetric
from app.models.user import User
from app.core.security import verify_token_dependency, get_current_user
from app.schemas.metrics import (
    FloorMetricCreate,
    FloorMetricResponse,
    RoomMetricCreate,
    RoomMetricResponse
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/floors", response_model=List[FloorMetricResponse])
async def get_floor_metrics(
    metric_name: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all floor metrics."""
    try:
        logger.info("Fetching all floor metrics")
        logger.debug(f"User: {current_user.email}, Metric: {metric_name}, Category: {category}")
        
        query = db.query(FloorMetric)
        
        if metric_name:
            query = query.filter(FloorMetric.metric_name == metric_name)
        if category:
            query = query.filter(FloorMetric.metric_category == category)
            
        metrics = query.all()
        logger.info(f"Found {len(metrics)} floor metrics")
        if not metrics:
            # Return empty list instead of 404 for better frontend handling
            return []
        return metrics
    except Exception as e:
        logger.error(f"Error fetching floor metrics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching floor metrics: {str(e)}"
        )

@router.get("/floors/{floor_id}", response_model=List[FloorMetricResponse])
async def get_specific_floor_metrics(
    floor_id: str,
    metric_name: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get metrics for a specific floor."""
    try:
        logger.info(f"Fetching metrics for floor {floor_id}")
        logger.debug(f"User: {current_user.email}, Metric: {metric_name}, Category: {category}")
        
        query = db.query(FloorMetric).filter(FloorMetric.floor_id == floor_id)
        logger.debug(f"SQL Query: {str(query)}")
        
        if metric_name:
            query = query.filter(FloorMetric.metric_name == metric_name)
        if category:
            query = query.filter(FloorMetric.metric_category == category)
            
        metrics = query.all()
        logger.info(f"Found {len(metrics)} metrics for floor {floor_id}")
        logger.debug(f"Metrics: {[{k: v for k, v in m.__dict__.items() if not k.startswith('_')} for m in metrics]}")
        
        if not metrics:
            logger.info(f"No metrics found for floor {floor_id}")
            return []
            
        return metrics
    except Exception as e:
        logger.error(f"Error fetching floor metrics: {str(e)}", exc_info=True)
        logger.error(f"Floor ID: {floor_id}, User: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching floor metrics: {str(e)}"
        )

@router.get("/rooms", response_model=List[RoomMetricResponse])
async def get_room_metrics(
    metric_name: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all room metrics."""
    try:
        logger.info("Fetching all room metrics")
        logger.debug(f"User: {current_user.email}, Metric: {metric_name}, Category: {category}")
        
        query = db.query(RoomMetric)
        
        if metric_name:
            query = query.filter(RoomMetric.metric_name == metric_name)
        if category:
            query = query.filter(RoomMetric.metric_category == category)
            
        metrics = query.all()
        logger.info(f"Found {len(metrics)} room metrics")
        if not metrics:
            return []
        return metrics
    except Exception as e:
        logger.error(f"Error fetching room metrics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching room metrics: {str(e)}"
        )

@router.get("/floors/{floor_id}/rooms", response_model=List[RoomMetricResponse])
async def get_floor_room_metrics(
    floor_id: str,
    metric_name: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get room metrics for a specific floor."""
    try:
        logger.info(f"Fetching room metrics for floor {floor_id}")
        logger.debug(f"User: {current_user.email}, Metric: {metric_name}, Category: {category}")
        
        # Build and execute the query
        query = db.query(RoomMetric).filter(RoomMetric.floor_id == floor_id)
        if metric_name:
            query = query.filter(RoomMetric.metric_name == metric_name)
        if category:
            # Convert frontend category to backend format (e.g., 'Patient Metrics' -> 'patient')
            backend_category = category.lower().replace(' metrics', '')
            query = query.filter(RoomMetric.metric_category == backend_category)
            
        logger.debug(f"SQL Query: {query.statement.compile(compile_kwargs={'literal_binds': True})}")
        
        # Execute query and log results
        metrics = query.all()
        logger.info(f"Found {len(metrics)} metrics for floor {floor_id}")
        
        # Transform metrics to match frontend expectations
        transformed_metrics = []
        for metric in metrics:
            # Map backend categories to frontend categories
            category = metric.metric_category
            if category == 'patient':
                frontend_category = 'Patient Metrics'
            elif category == 'staff':
                frontend_category = 'Staff Metrics'
            elif category == 'room':
                frontend_category = 'Room Metrics'
            else:
                frontend_category = f"{category.title()} Metrics"
                
            transformed_metric = RoomMetricResponse(
                floor_id=metric.floor_id,
                room_id=metric.room_id,
                metric_name=metric.metric_name,
                value=float(metric.value),
                metric_category=frontend_category,
                timestamp=metric.timestamp,
                metric_type='room'
            )
            logger.debug(f"Transformed metric: {transformed_metric}")
            transformed_metrics.append(transformed_metric)
            
        if not transformed_metrics:
            logger.warning(f"No metrics found for floor {floor_id}")
            return []
            
        return transformed_metrics
    except Exception as e:
        logger.error(f"Error fetching room metrics: {str(e)}", exc_info=True)
        logger.error(f"Floor ID: {floor_id}, User: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching room metrics: {str(e)}"
        )

@router.get("/floors/{floor_id}/rooms/{room_id}", response_model=List[RoomMetricResponse])
async def get_specific_room_metrics(
    floor_id: str,
    room_id: str,
    metric_name: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get metrics for a specific room."""
    try:
        logger.info(f"Fetching metrics for room {room_id} on floor {floor_id}")
        logger.debug(f"User: {current_user.email}, Metric: {metric_name}, Category: {category}")
        
        query = db.query(RoomMetric).filter(
            RoomMetric.floor_id == floor_id,
            RoomMetric.room_id == room_id
        )
        
        if metric_name:
            query = query.filter(RoomMetric.metric_name == metric_name)
        if category:
            query = query.filter(RoomMetric.metric_category == category)
            
        metrics = query.all()
        logger.info(f"Found {len(metrics)} metrics for room {room_id} on floor {floor_id}")
        if not metrics:
            return []
        return metrics
    except Exception as e:
        logger.error(f"Error fetching room metrics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching room metrics: {str(e)}"
        )

@router.post("/import/floor-metrics")
async def import_floor_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import floor metrics from CSV file."""
    try:
        logger.info("Importing floor metrics from CSV file")
        logger.debug(f"User: {current_user.email}")
        
        if not current_user.is_superuser:
            logger.error("Unauthorized access attempt")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to import metrics"
            )
            
        df = pd.read_csv('app/data/floor_metrics.csv')
        for _, row in df.iterrows():
            metric = FloorMetric(
                floor_id=row['floor_id'],
                metric_name=row['metric_name'],
                value=row['value'],
                metric_category=row['metric_category'],
                timestamp=datetime.strptime(row['timestamp'], '%Y-%m-%d')
            )
            db.add(metric)
        db.commit()
        logger.info("Floor metrics imported successfully")
        return {"message": "Floor metrics imported successfully"}
    except Exception as e:
        logger.error(f"Error importing floor metrics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing floor metrics: {str(e)}"
        )

@router.post("/import/room-metrics")
async def import_room_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Import room metrics from CSV file."""
    try:
        logger.info("Importing room metrics from CSV file")
        logger.debug(f"User: {current_user.email}")
        
        if not current_user.is_superuser:
            logger.error("Unauthorized access attempt")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to import metrics"
            )
            
        df = pd.read_csv('app/data/room_metrics.csv')
        for _, row in df.iterrows():
            metric = RoomMetric(
                floor_id=row['floor_id'],
                room_id=row['room_id'],
                metric_name=row['metric_name'],
                value=row['value'],
                metric_category=row['metric_category'],
                timestamp=datetime.now()
            )
            db.add(metric)
        db.commit()
        logger.info("Room metrics imported successfully")
        return {"message": "Room metrics imported successfully"}
    except Exception as e:
        logger.error(f"Error importing room metrics: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing room metrics: {str(e)}"
        )

@router.post("/floor-metrics", response_model=FloorMetricResponse)
async def create_floor_metric(
    metric: FloorMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new floor metric."""
    try:
        logger.info("Creating new floor metric")
        logger.debug(f"User: {current_user.email}, Metric: {metric.dict()}")
        
        if not current_user.is_superuser:
            logger.error("Unauthorized access attempt")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create metrics"
            )
            
        db_metric = FloorMetric(**metric.dict())
        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)
        logger.info("Floor metric created successfully")
        return db_metric
    except Exception as e:
        logger.error(f"Error creating floor metric: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating floor metric: {str(e)}"
        )

@router.post("/room-metrics", response_model=RoomMetricResponse)
async def create_room_metric(
    metric: RoomMetricCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new room metric."""
    try:
        logger.info("Creating new room metric")
        logger.debug(f"User: {current_user.email}, Metric: {metric.dict()}")
        
        if not current_user.is_superuser:
            logger.error("Unauthorized access attempt")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create metrics"
            )
            
        db_metric = RoomMetric(**metric.dict())
        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)
        logger.info("Room metric created successfully")
        return db_metric
    except Exception as e:
        logger.error(f"Error creating room metric: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating room metric: {str(e)}"
        )
