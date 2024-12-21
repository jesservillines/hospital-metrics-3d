# backend/app/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

Base = declarative_base()

class MetricCategory(enum.Enum):
    PATIENT = "patient"
    STAFF = "staff"
    # Extensible for future categories

class MetricDefinition(Base):
    __tablename__ = 'metric_definitions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    category = Column(Enum(MetricCategory), nullable=False)
    data_type = Column(String, nullable=False)  # 'numeric' or 'string'
    description = Column(String)
    units = Column(String)
    aggregation_type = Column(String)  # 'avg', 'sum', 'latest', etc.

    # Relationships
    room_metrics = relationship("RoomMetric", back_populates="metric")
    floor_metrics = relationship("FloorMetric", back_populates="metric")

class Floor(Base):
    __tablename__ = 'floors'
    
    id = Column(Integer, primary_key=True)
    floor_id = Column(String, unique=True, nullable=False)  # e.g., "1_east"
    name = Column(String, nullable=False)  # e.g., "1 East"
    building = Column(String, nullable=False)  # "East" or "West"
    level = Column(Integer, nullable=False)  # 1, 2, 3, 4

    # Relationships
    rooms = relationship("Room", back_populates="floor")
    metrics = relationship("FloorMetric", back_populates="floor")

class Room(Base):
    __tablename__ = 'rooms'
    
    id = Column(Integer, primary_key=True)
    room_id = Column(String, unique=True, nullable=False)  # e.g., "227A"
    floor_id = Column(String, ForeignKey('floors.floor_id'), nullable=False)
    room_type = Column(String, nullable=False)  # e.g., "patient", "therapy", "office"
    
    # Relationships
    floor = relationship("Floor", back_populates="rooms")
    metrics = relationship("RoomMetric", back_populates="room")

class RoomMetric(Base):
    __tablename__ = 'room_metrics'
    
    id = Column(Integer, primary_key=True)
    room_id = Column(String, ForeignKey('rooms.room_id'), nullable=False)
    metric_id = Column(Integer, ForeignKey('metric_definitions.id'), nullable=False)
    value = Column(Float)
    timestamp = Column(DateTime, nullable=False)
    is_calculated = Column(Boolean, default=False)
    
    # Relationships
    room = relationship("Room", back_populates="metrics")
    metric = relationship("MetricDefinition", back_populates="room_metrics")

class FloorMetric(Base):
    __tablename__ = 'floor_metrics'
    
    id = Column(Integer, primary_key=True)
    floor_id = Column(String, ForeignKey('floors.floor_id'), nullable=False)
    metric_id = Column(Integer, ForeignKey('metric_definitions.id'), nullable=False)
    value = Column(Float)
    timestamp = Column(DateTime, nullable=False)
    is_calculated = Column(Boolean, default=False)
    
    # Relationships
    floor = relationship("Floor", back_populates="metrics")
    metric = relationship("MetricDefinition", back_populates="floor_metrics")

class UserRole(enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime)

class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'
    
    id = Column(Integer, primary_key=True)
    token = Column(String(255), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked = Column(Boolean, default=False)
    
    # Relationship
    user = relationship("User", backref="refresh_tokens")