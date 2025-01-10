import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
from datetime import timezone as tz

from app.main import app
from app.models.metrics import RoomMetric
from app.models.user import User
from app.core.security import create_access_token

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def test_db(db):
    """Create test room metrics"""
    # Clean up any existing data
    db.query(RoomMetric).delete()
    db.query(User).delete()
    db.commit()
    
    # Create test room metrics
    test_metrics = [
        RoomMetric(
            floor_id="3_west",
            room_id="301",
            metric_name="room_occupancy",
            value=80.0,
            metric_category="room",
            timestamp=datetime.now(tz.utc)
        ),
        RoomMetric(
            floor_id="3_west",
            room_id="302",
            metric_name="patient_satisfaction",
            value=85.0,
            metric_category="patient",
            timestamp=datetime.now(tz.utc)
        ),
        RoomMetric(
            floor_id="3_west",
            room_id="303",
            metric_name="staff_efficiency",
            value=90.0,
            metric_category="staff",
            timestamp=datetime.now(tz.utc)
        )
    ]
    
    for metric in test_metrics:
        db.add(metric)
    db.commit()
    
    yield db
    
    # Cleanup
    db.query(RoomMetric).delete()
    db.query(User).delete()
    db.commit()

@pytest.fixture
def test_user(test_db):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="test_password_hash",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    return user

@pytest.fixture
def auth_headers(test_user):
    access_token = create_access_token(
        data={"sub": test_user.username},  # Use username instead of email
        scopes=["user"]  # Add required scopes parameter
    )
    return {"Authorization": f"Bearer {access_token}"}

def test_get_floor_room_metrics_success(test_client, test_db, auth_headers):
    """Test successful retrieval of room metrics for a floor"""
    response = test_client.get("/api/v1/metrics/floors/3_west/rooms", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        metric = data[0]
        assert all(key in metric for key in ['floor_id', 'room_id', 'metric_name', 'value', 'metric_category', 'metric_type'])
        assert metric['metric_type'] == 'room'
        assert metric['metric_category'].endswith('Metrics')
        assert isinstance(metric['value'], (int, float))

def test_get_floor_room_metrics_with_category(test_client, test_db, auth_headers):
    """Test filtering room metrics by category"""
    response = test_client.get(
        "/api/v1/metrics/floors/3_west/rooms?category=Patient%20Metrics",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert all(metric['metric_category'] == 'Patient Metrics' for metric in data)

def test_get_floor_room_metrics_with_metric_name(test_client, test_db, auth_headers):
    """Test filtering room metrics by metric name"""
    response = test_client.get(
        "/api/v1/metrics/floors/3_west/rooms?metric_name=room_temperature",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert all(metric['metric_name'] == 'room_temperature' for metric in data)

def test_get_floor_room_metrics_empty_floor(test_client, test_db, auth_headers):
    """Test handling of floor with no metrics"""
    response = test_client.get("/api/v1/metrics/floors/nonexistent_floor/rooms", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []

def test_get_floor_room_metrics_unauthorized(test_client, test_db):
    """Test unauthorized access"""
    response = test_client.get("/api/v1/metrics/floors/3_west/rooms")
    assert response.status_code == 401
    assert "detail" in response.json()

def test_get_floor_room_metrics_db_error(test_client, test_db, auth_headers, monkeypatch):
    """Test handling of database errors"""
    original_query = Session.query
    
    def mock_query(*args, **kwargs):
        # Only mock RoomMetric queries
        if len(args) > 1 and args[1] == RoomMetric:
            raise Exception("Database error")
        return original_query(*args, **kwargs)
    
    monkeypatch.setattr(Session, "query", mock_query)
    response = test_client.get("/api/v1/metrics/floors/3_west/rooms", headers=auth_headers)
    assert response.status_code == 500
    assert "error" in response.json()["detail"].lower()
