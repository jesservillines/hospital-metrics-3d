from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base

class MetricDefinition(Base):
    __tablename__ = "metric_definitions"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    unit = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    floor_metrics = relationship("FloorMetric", back_populates="definition")

class RoomMetric(Base):
    """Model for room metrics data"""
    __tablename__ = "room_metrics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    floor_id = Column(String, nullable=False)
    room_id = Column(String, nullable=False)
    metric_name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    metric_category = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=True, default=datetime.utcnow)

    def __repr__(self):
        return f"<RoomMetric(floor_id='{self.floor_id}', room_id='{self.room_id}', metric_name='{self.metric_name}', value={self.value}, category='{self.metric_category}')>"

class FloorMetric(Base):
    __tablename__ = "floor_metrics"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    floor_id = Column(String, index=True)
    metric_name = Column(String)
    value = Column(Float)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metric_category = Column(String)
    meta_data = Column(JSON, nullable=True)

    # Optional relationship to metric definition
    metric_id = Column(Integer, ForeignKey("metric_definitions.id"), nullable=True)
    definition = relationship("MetricDefinition", back_populates="floor_metrics")
