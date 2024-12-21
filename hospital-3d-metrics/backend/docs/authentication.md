# Authentication System Documentation

## Overview

The authentication system provides a complete solution for user management, including registration, login, password reset, and session management. It integrates with the OAuth2 system to provide both traditional and OAuth2-based authentication.

## Features

- User registration with email verification
- Login with remember me functionality
- Password reset via email
- Session management
- Rate limiting for security
- OAuth2 integration
- Modern, responsive UI

## API Endpoints

### Registration

```http
POST /api/v1/auth/register
Content-Type: application/json

{
    "username": "string",
    "email": "user@example.com",
    "password": "string",
    "password_confirm": "string",
    "terms_accepted": true
}
```

**Response**:
- `200 OK`: Registration successful
- `400 Bad Request`: Invalid input or user already exists

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "string",
    "password": "string",
    "remember_me": false,
    "return_to": "string"
}
```

**Response**:
- `200 OK`: Login successful
- `401 Unauthorized`: Invalid credentials

### Password Reset Request

```http
POST /api/v1/auth/reset-password
Content-Type: application/json

{
    "email": "user@example.com"
}
```

**Response**:
- `200 OK`: Reset email sent (if email exists)

### Password Reset Confirmation

```http
POST /api/v1/auth/reset-password/{token}
Content-Type: application/json

{
    "token": "string",
    "password": "string",
    "password_confirm": "string"
}
```

**Response**:
- `200 OK`: Password reset successful
- `400 Bad Request`: Invalid token or password

### Logout

```http
GET /api/v1/auth/logout
```

**Response**:
- `302 Found`: Redirects to home page

## Security Features

### Password Requirements

- Minimum length: 12 characters
- Must contain at least one uppercase letter
- Must contain at least one number
- Must contain at least one special character

### Rate Limiting

- Login: 5 attempts per minute
- Registration: 3 attempts per minute
- Password reset: 3 attempts per minute

### Session Security

- Secure session cookies
- HTTP-only cookies for security
- CSRF protection
- Session timeout after inactivity

## Configuration

The authentication system uses the following environment variables:

```env
# JWT Settings
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# Email Settings
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=noreply@example.com

# Application Settings
SERVER_HOST=http://localhost:8000
PROJECT_NAME=Hospital Metrics 3D
```

## Database Models

### User Model

```python
class User(Base):
    id: UUID primary key
    username: str (unique)
    email: str (unique)
    hashed_password: str
    is_active: bool
    reset_token: Optional[str]
    reset_token_expires: Optional[datetime]
```

### OAuth2Token Model

```python
class OAuth2Token(Base):
    id: UUID primary key
    access_token: str
    refresh_token: Optional[str]
    token_type: str
    scope: str
    expires_at: datetime
    user_id: UUID (foreign key)
    revoked: bool
```

## Error Handling

The system provides detailed error messages for:
- Invalid credentials
- Username/email already taken
- Password requirements not met
- Invalid reset tokens
- Rate limit exceeded
- Server errors

## Frontend Integration

The system provides HTML templates using Jinja2:
- `base.html`: Base template with navigation
- `auth/login.html`: Login form
- `auth/register.html`: Registration form
- `auth/reset_password.html`: Password reset request form
- `auth/reset_password_confirm.html`: New password form

## Testing

See `tests/test_auth.py` for comprehensive tests covering:
- User registration
- Login functionality
- Password reset flow
- Rate limiting
- Session management
- Error handling

## Example Usage

### Registration

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "terms_accepted": True
    }
)
```

### Login

```python
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "username": "testuser",
        "password": "SecurePass123!",
        "remember_me": True
    }
)
```

## Best Practices

1. **Password Storage**
   - Passwords are hashed using bcrypt
   - Never store plain text passwords
   - Use strong password requirements

2. **Session Management**
   - Use secure, HTTP-only cookies
   - Implement proper session timeout
   - Revoke sessions on password change

3. **Security Headers**
   - Set appropriate security headers
   - Use HTTPS in production
   - Implement CSRF protection

4. **Rate Limiting**
   - Protect against brute force attacks
   - Limit registration attempts
   - Limit password reset attempts

5. **Error Handling**
   - Provide user-friendly error messages
   - Log security events
   - Don't expose sensitive information

## Troubleshooting

### Common Issues

1. **Login Failed**
   - Check username/password
   - Verify account is active
   - Check rate limit status

2. **Registration Failed**
   - Username/email might be taken
   - Password requirements not met
   - Rate limit exceeded

3. **Password Reset Issues**
   - Token might be expired
   - Email delivery problems
   - Invalid email address

### Debug Mode

Set `DEBUG=True` in development for detailed error messages.
