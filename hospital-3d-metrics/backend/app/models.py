# backend/app/models.py
from pydantic import BaseModel
from typing import Dict, List, Optional


class MetricData(BaseModel):
    floor: str
    metric_name: str
    value: float
    timestamp: str


class FloorMetrics(BaseModel):
    floor: str
    metrics: Dict[str, float]


class MetricFilter(BaseModel):
    metric_name: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None