# backend/app/models.py
from pydantic import BaseModel, field_validator
from typing import Dict, List, Optional
import pandas as pd

class MetricData(BaseModel):
    floor: str
    room: Optional[str] = None  # Make room explicitly optional
    metric_name: str
    value: float
    timestamp: str
    metric_type: str  # 'floor' or 'room'

    @field_validator('room')
    def validate_room(cls, v):
        # Convert nan to None for optional room field
        if isinstance(v, float) and pd.isna(v):  # Using pandas isna for nan check
            return None
        return v

class FloorMetrics(BaseModel):
    floor: str
    floor_metrics: Dict[str, float]
    room_metrics: Dict[str, Dict[str, float]]

class MetricFilter(BaseModel):
    metric_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    metric_type: Optional[str] = None