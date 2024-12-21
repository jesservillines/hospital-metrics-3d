# Hospital Metrics 3D Backend

This is the backend service for the Hospital Metrics 3D visualization system. It provides data management, authentication, and API endpoints for hospital metrics visualization.

## Project Structure

```
backend/
├── app/
│   ├── core/           # Core functionality (auth, security, middleware)
│   ├── models/         # Database models
│   ├── routes/         # API endpoints
│   ├── schemas/        # Pydantic models for request/response
│   └── templates/      # HTML templates for auth pages
├── tests/             # Test suite
├── alembic/           # Database migrations
└── requirements.txt   # Python dependencies
```

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hospital_metrics
DB_USER=postgres
DB_PASSWORD=your_password
SECRET_KEY=your-secret-key
```

4. Initialize the database:
```bash
alembic upgrade head
```

## Running the Backend

1. Start the development server:
```bash
uvicorn app.main:app --reload --port 8000
```

2. The backend will be available at:
- API: http://localhost:8000/api/v1
- Documentation: http://localhost:8000/api/v1/docs
- OpenAPI Spec: http://localhost:8000/api/v1/openapi.json

## Connecting to Frontend

1. The backend serves the frontend at the root URL (http://localhost:8000)

2. Configure CORS in `app/core/middleware.py`:
```python
origins = [
    "http://localhost:3000",  # React development server
    "http://localhost:8000",  # Backend server
]
```

3. Frontend API calls should be directed to `http://localhost:8000/api/v1/*`

## Authentication Flow

1. **Registration**:
   - POST `/api/v1/auth/register`
   - Required fields: username, email, password
   - Returns user details on success

2. **Login**:
   - POST `/api/v1/auth/login`
   - Required fields: username/email, password
   - Optional: remember_me (for refresh token)
   - Returns access token and optional refresh token

3. **Password Reset**:
   - POST `/api/v1/auth/reset-password` (request reset)
   - POST `/api/v1/auth/reset-password-confirm` (with reset token)

4. **Token Management**:
   - Access tokens expire after 30 minutes
   - Refresh tokens (if requested) expire after 7 days
   - Blacklisted tokens are tracked for security

5. **Rate Limiting**:
   - Auth endpoints: 5 attempts per 15 minutes
   - Standard endpoints: 200 requests per 15 minutes

## Running Tests

1. Set up test environment:
```bash
export TESTING=true  # On Windows: set TESTING=true
```

2. Run all tests:
```bash
pytest
```

3. Run specific test files:
```bash
pytest tests/test_auth.py -v
```

4. Run with coverage:
```bash
pytest --cov=app tests/
```

## Security Features

- Password hashing with bcrypt
- JWT tokens with expiration
- Token blacklisting for logout
- Rate limiting on sensitive endpoints
- HTTPS redirect in production
- CORS protection
- Session management

## Development Status

✅ Authentication system complete
✅ User management implemented
✅ Token handling and security
✅ Test suite with high coverage
🔄 Metrics API endpoints in progress
🔄 3D visualization data endpoints pending
