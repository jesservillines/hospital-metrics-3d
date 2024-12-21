import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import Base, get_db, engine
from app.models.metrics import FloorMetric, RoomMetric
from app.models.user import User
from app.core.security import create_access_token
from datetime import datetime, timedelta, timezone

client = TestClient(app)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(db: Session):
    # Delete any existing user with the same email
    existing_user = db.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        db.delete(existing_user)
        db.commit()

    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LedYQNB8UHUHzh" # test123
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def token(test_user: User):
    return create_access_token(
        data={"sub": test_user.email},
        scopes=["metrics:read"],
        expires_delta=timedelta(minutes=30)
    )

@pytest.fixture
def authorized_client(token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_metrics(db: Session):
    floor_metrics = [
        FloorMetric(
            floor_id="1E",
            metric_name="patient_satisfaction",
            value=85.5,
            metric_category="Patient Metrics",
            timestamp=datetime.now(timezone.utc)
        ),
        FloorMetric(
            floor_id="2W",
            metric_name="staff_satisfaction",
            value=92.3,
            metric_category="Staff Metrics",
            timestamp=datetime.now(timezone.utc)
        )
    ]
    room_metrics = [
        RoomMetric(
            floor_id="1E",
            room_id="101",
            metric_name="fall_risk",
            value=15.2,
            metric_category="Patient Metrics",
            timestamp=datetime.now(timezone.utc)
        ),
        RoomMetric(
            floor_id="2W",
            room_id="201",
            metric_name="nurse_response_time",
            value=3.5,
            metric_category="Staff Metrics",
            timestamp=datetime.now(timezone.utc)
        )
    ]
    
    for metric in floor_metrics + room_metrics:
        db.add(metric)
    db.commit()
    
    return {"floor_metrics": floor_metrics, "room_metrics": room_metrics}

def test_get_floor_metrics(authorized_client, test_metrics):
    response = authorized_client.get("/api/v1/metrics/floors")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["floor_id"] == "1E"
    assert data[0]["metric_name"] == "patient_satisfaction"
    assert data[1]["floor_id"] == "2W"
    assert data[1]["metric_name"] == "staff_satisfaction"

def test_get_floor_metrics_by_category(authorized_client, test_metrics):
    response = authorized_client.get("/api/v1/metrics/floors?category=Patient+Metrics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["metric_category"] == "Patient Metrics"

def test_get_specific_floor_metrics(authorized_client, test_metrics):
    response = authorized_client.get("/api/v1/metrics/floors/1E")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["floor_id"] == "1E"
    assert data[0]["metric_name"] == "patient_satisfaction"

def test_get_room_metrics(authorized_client, test_metrics):
    response = authorized_client.get("/api/v1/metrics/rooms")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["room_id"] == "101"
    assert data[0]["metric_name"] == "fall_risk"
    assert data[1]["room_id"] == "201"
    assert data[1]["metric_name"] == "nurse_response_time"

def test_get_floor_room_metrics(authorized_client, test_metrics):
    response = authorized_client.get("/api/v1/metrics/floors/1E/rooms")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["floor_id"] == "1E"
    assert data[0]["room_id"] == "101"
    assert data[0]["metric_name"] == "fall_risk"

def test_get_specific_room_metrics(authorized_client, test_metrics):
    response = authorized_client.get("/api/v1/metrics/floors/1E/rooms/101")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["floor_id"] == "1E"
    assert data[0]["room_id"] == "101"
    assert data[0]["metric_name"] == "fall_risk"

def test_unauthorized_access(client):
    response = client.get("/api/v1/metrics/floors")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
