import pytest
from fastapi import status
from app.models.user import User
from app.core.security import get_password_hash
from datetime import datetime, timedelta

@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("TestPass123!"),
        is_active=True,
        is_verified=True,
        created_at=datetime.now(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_user_with_reset_token(db, test_user):
    """Create a test user with reset token."""
    test_user.reset_token = "test-reset-token"
    test_user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()
    db.refresh(test_user)
    return test_user

def test_register_success(client, db):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
            "terms_accepted": True,
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data

    # Verify user in database
    user = db.query(User).filter(User.email == "newuser@example.com").first()
    assert user is not None
    assert user.username == "newuser"
    assert user.is_active
    assert not user.is_verified

def test_register_duplicate_email(client, test_user):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "another",
            "email": "test@example.com",  # Same as test_user
            "password": "TestPass123!",
            "password_confirm": "TestPass123!",
            "terms_accepted": True,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]

def test_login_success(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "test@example.com",
            "password": "TestPass123!",
            "remember_me": False,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_form_success(client, test_user):
    """Test login with form data."""
    form_data = {
        "username": "testuser",  # Use username instead of email
        "password": "TestPass123!",
        "grant_type": "password"
    }
    response = client.post(
        "/api/v1/auth/login",
        data=form_data,  # Use data= for form data
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print("Login response:", response.status_code, response.text)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "wrong@example.com",
            "password": "WrongPass123!",
            "remember_me": False,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid credentials" in response.json()["detail"]

def test_request_password_reset(client, test_user):
    response = client.post(
        "/api/v1/auth/request-password-reset",
        json={"email": "test@example.com"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "Password reset email sent" in response.json()["message"]

def test_reset_password(client, test_user_with_reset_token, db):
    print("\n=== Password Reset Test ===")
    print(f"Initial user password hash: {test_user_with_reset_token.hashed_password}")
    
    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "test-reset-token",
            "new_password": "NewTestPass123!",
            "password_confirm": "NewTestPass123!",
        },
    )
    print(f"Reset Response: {response.status_code} {response.text}")
    assert response.status_code == status.HTTP_200_OK
    assert "Password reset successful" in response.json()["message"]

    # Verify password was updated
    db.expire_all()  # Expire all objects in the session
    user = db.query(User).filter(User.id == test_user_with_reset_token.id).first()
    print(f"Updated user password hash: {user.hashed_password}")
    
    # Try verifying the password
    verification_result = user.verify_password("NewTestPass123!")
    print(f"Password verification result: {verification_result}")
    print(f"Using password: NewTestPass123!")
    
    assert verification_result, "Password verification failed"

    # Try logging in with new password
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": user.email,
            "password": "NewTestPass123!",
            "remember_me": False,
        },
    )
    print("Login response:", login_response.status_code, login_response.text)
    assert login_response.status_code == status.HTTP_200_OK

def test_reset_password_invalid_token(client):
    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": "invalid-token",
            "new_password": "NewTestPass123!",
            "password_confirm": "NewTestPass123!",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid or expired reset token" in response.json()["detail"]

def test_logout(client, test_user):
    # First login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "test@example.com",
            "password": "TestPass123!",
            "remember_me": False,
        },
    )
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()["access_token"]

    # Then logout
    logout_response = client.post(
        "/api/v1/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert logout_response.status_code == status.HTTP_200_OK
    assert "Logged out successfully" in logout_response.json()["message"]

    # Verify can't access protected endpoint
    protected_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert protected_response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_rate_limit():
    """Test rate limiting on login endpoint."""
    # This test is handled by the NoLimitLimiter in test mode
    pass

def test_session_data(client, test_user):
    # First login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "test@example.com",
            "password": "TestPass123!",
            "remember_me": False,
        },
    )
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()["access_token"]

    # Test accessing protected endpoint
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["username"] == "testuser"

def test_session_expiry(client, test_user):
    # First login
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "test@example.com",
            "password": "TestPass123!",
            "remember_me": False,
        },
    )
    assert login_response.status_code == status.HTTP_200_OK
    token = login_response.json()["access_token"]

    # Test accessing protected endpoint with expired token
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNjM5NTIwMDAwfQ.7B6p2xzO5H0CBr1oC0C3jqvDv8Ng5wKfDm9v6Jh5HA0"
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    print("Response with expired token:", response.status_code, response.text)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Could not validate credentials" in response.json()["detail"]
