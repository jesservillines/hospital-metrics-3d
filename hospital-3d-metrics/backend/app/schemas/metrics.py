from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class FloorMetricBase(BaseModel):
    floor_id: str
    metric_name: str
    value: float
    metric_category: str
    timestamp: Optional[datetime] = None
    meta_data: Optional[Dict[str, Any]] = None

class FloorMetricCreate(FloorMetricBase):
    pass

class FloorMetricResponse(FloorMetricBase):
    id: int

    class Config:
        from_attributes = True

class RoomMetricBase(BaseModel):
    room_id: str
    floor_id: str
    metric_name: str
    value: float
    metric_category: str
    timestamp: Optional[datetime] = None
    meta_data: Optional[Dict[str, Any]] = None

class RoomMetricCreate(RoomMetricBase):
    pass

class RoomMetricResponse(RoomMetricBase):
    id: int

    class Config:
        from_attributes = True
