# Hospital 3D Metrics - Technical Documentation

## System Architecture

### Overview
The Hospital 3D Metrics system is a full-stack application that provides 3D visualization of hospital metrics. It consists of:
1. Frontend: React + Three.js application for 3D visualization
2. Backend: FastAPI application providing REST API endpoints
3. Database: PostgreSQL for data persistence

## Frontend Architecture

### Technology Stack
- React 18+ with TypeScript
- Three.js with React Three Fiber
- Tailwind CSS for styling
- ShadcnUI for UI components
- Vite for build tooling

### Directory Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── Building.tsx           # 3D building component
│   │   ├── Bridge.tsx            # Bridge between buildings
│   │   ├── Garden.tsx            # Garden area component
│   │   ├── HospitalView.tsx      # Main 3D view container
│   │   ├── Controls.tsx          # UI controls panel
│   │   ├── MetricsPanel.tsx      # Metrics display panel
│   │   ├── FloorDetail.tsx       # Floor detail view
│   │   ├── FloorLayout.tsx       # Floor layout component
│   │   ├── PatientRoomDetail.tsx # Patient room component
│   │   ├── RoomDetail.tsx        # Generic room component
│   │   └── Environment.tsx       # 3D environment settings
│   ├── hooks/
│   │   ├── useMetrics.ts         # Metrics data hook
│   │   ├── useAuth.ts            # Authentication hook
│   │   └── useFloorData.ts       # Floor data management
│   ├── services/
│   │   ├── api.ts                # API client
│   │   ├── roomDataService.ts    # Room data service
│   │   └── metricsService.ts     # Metrics data service
│   ├── types/
│   │   ├── metrics.ts            # Metric type definitions
│   │   └── rooms.ts              # Room type definitions
│   └── utils/
│       ├── colorScales.ts        # Color mapping utilities
│       └── constants.ts          # Global constants
```

### Key Components

#### HospitalView
- Main container for 3D visualization
- Manages camera controls and scene setup
- Handles building selection and floor highlighting
- Coordinates with metrics panel for data display

#### Building
- Renders individual hospital buildings
- Manages floor geometry and materials
- Handles hover and click interactions
- Implements heat map visualization

#### FloorDetail
- Shows detailed view of selected floor
- Renders room layouts and patient areas
- Displays room-specific metrics
- Handles room selection and highlighting

### Frontend Next Steps

1. **Performance Optimization**
   - [ ] Implement level-of-detail (LOD) system
   - [ ] Add geometry instancing for repeated elements
   - [ ] Optimize texture loading and management
   - [ ] Add object pooling for dynamic elements

2. **UI Improvements**
   - [ ] Add advanced filtering options
   - [ ] Implement comparison view
   - [ ] Add timeline controls for historical data
   - [ ] Improve accessibility features

3. **Visualization Enhancements**
   - [ ] Add smooth transitions between views
   - [ ] Implement room occupancy visualization
   - [ ] Add patient flow visualization
   - [ ] Improve heat map gradients

4. **Data Management**
   - [ ] Implement client-side caching
   - [ ] Add offline support
   - [ ] Improve error handling
   - [ ] Add real-time updates via WebSocket

## Backend Architecture

### Technology Stack
- FastAPI
- SQLAlchemy ORM
- Pydantic for validation
- PostgreSQL database
- JWT for authentication

### Directory Structure
```
backend/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   ├── security.py        # Security utilities
│   │   └── middleware.py      # Middleware setup
│   ├── models/
│   │   ├── user.py           # User model
│   │   ├── metrics.py        # Metrics models
│   │   └── token.py          # Token model
│   ├── routes/
│   │   ├── auth.py           # Authentication routes
│   │   ├── metrics.py        # Metrics routes
│   │   └── users.py          # User management
│   ├── schemas/
│   │   ├── user.py           # User schemas
│   │   └── metrics.py        # Metrics schemas
│   └── services/
│       ├── auth.py           # Auth service
│       └── metrics.py        # Metrics service
├── tests/
│   ├── test_auth.py          # Auth tests
│   └── test_metrics.py       # Metrics tests
└── alembic/                  # Database migrations
```

### Key Components

#### Authentication System
- JWT-based authentication
- Token blacklisting
- Role-based access control
- Password hashing with bcrypt
- Refresh token rotation

#### Metrics System
- Floor-level metrics
- Room-level metrics
- Historical data tracking
- Metric aggregation
- Data validation

### Backend Next Steps

1. **Code Quality**
   - [ ] Update datetime handling to use timezone-aware objects
   - [ ] Update Pydantic schemas to V2 syntax
   - [ ] Improve error handling and logging
   - [ ] Add comprehensive input validation

2. **Performance**
   - [ ] Implement query optimization
   - [ ] Add response caching
   - [ ] Optimize database indexes
   - [ ] Add connection pooling

3. **Features**
   - [ ] Add metric aggregation endpoints
   - [ ] Implement WebSocket support
   - [ ] Add bulk operations
   - [ ] Implement rate limiting

4. **Testing**
   - [ ] Increase test coverage
   - [ ] Add integration tests
   - [ ] Add load tests
   - [ ] Improve test fixtures

## Database Architecture

### Technology Stack
- PostgreSQL as the primary database
- SQLAlchemy ORM for database interactions
- Alembic for database migrations
- JSON data type support for flexible metadata storage

### Core Schema

#### Metrics Tables
```sql
-- Metric Definitions
CREATE TABLE metric_definitions (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    unit VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Room Metrics
CREATE TABLE room_metrics (
    id INTEGER PRIMARY KEY,
    room_id VARCHAR,
    floor VARCHAR,
    floor_id VARCHAR,
    metric_name VARCHAR,
    value FLOAT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metric_category VARCHAR,
    meta_data JSON,
    metric_id INTEGER REFERENCES metric_definitions(id)
);

-- Floor Metrics
CREATE TABLE floor_metrics (
    id INTEGER PRIMARY KEY,
    floor VARCHAR,
    floor_id VARCHAR,
    metric_name VARCHAR,
    value FLOAT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metric_category VARCHAR,
    meta_data JSON,
    metric_id INTEGER REFERENCES metric_definitions(id)
);
```

#### Authentication Tables
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR UNIQUE,
    email VARCHAR UNIQUE,
    hashed_password VARCHAR,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE roles (
    id INTEGER PRIMARY KEY,
    name VARCHAR UNIQUE,
    permissions JSON
);

CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(id),
    role_id INTEGER REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE blacklisted_tokens (
    id INTEGER PRIMARY KEY,
    token VARCHAR UNIQUE,
    blacklisted_at TIMESTAMP DEFAULT NOW()
);
```

### Key Features

1. **Metric Tracking**
   - Hierarchical structure with floor and room-level metrics
   - Flexible metadata storage using JSON columns
   - Temporal data tracking with timestamps
   - Metric categorization and unit management

2. **Authentication & Authorization**
   - Role-based access control
   - Token blacklisting for security
   - User-role many-to-many relationship
   - Password hashing and verification

3. **Performance Optimizations**
   - Indexed columns for frequent queries
   - Timestamp with timezone support
   - Efficient relationship mappings
   - Prepared statement support

### Database Next Steps

1. **Schema Optimization**
   - [ ] Add partitioning for metrics tables
   - [ ] Implement materialized views for common queries
   - [ ] Add composite indexes for frequent query patterns
   - [ ] Set up table archival strategy

2. **Data Management**
   - [ ] Implement data retention policies
   - [ ] Add metric validation constraints
   - [ ] Set up automated backups
   - [ ] Create data pruning procedures

3. **Performance Monitoring**
   - [ ] Set up query performance monitoring
   - [ ] Implement connection pooling
   - [ ] Add database health checks
   - [ ] Create performance dashboards

## Security Architecture

### Authentication & Authorization
- JWT-based authentication with secure token management
- Role-based access control (RBAC) system
- Token blacklisting for secure logout
- Refresh token rotation for enhanced security
- Password strength enforcement with bcrypt hashing

### Environment Configuration
```plaintext
backend/
├── .env                    # Development environment
├── .env.production        # Production environment
├── .env.example          # Template for environment setup
└── scripts/
    ├── generate_secret_key.py    # Secure key generation
    └── generate_db_credentials.py # Database credential generation
```

### Security Features
1. **CORS Configuration**
   - Environment-specific allowed origins
   - Strict method and header controls
   - Credentials support for authenticated requests
   - Preflight caching for performance

2. **Database Security**
   - SSL/TLS encrypted connections
   - Connection pooling with health checks
   - Statement timeout limits
   - User-specific privileges
   - Read-only user for reporting

3. **API Security**
   - Rate limiting per endpoint
   - Request validation middleware
   - Secure session handling
   - HTTPS redirection in production

### Production Security Measures
1. **Environment Variables**
   - Secure credential generation
   - Environment-specific configurations
   - Sensitive data protection

2. **Database Access**
   - Limited connection pools
   - Connection timeouts
   - SSL enforcement
   - Schema-level permissions

3. **Session Security**
   - Secure cookie settings
   - HTTP-only flags
   - SameSite policy
   - CSRF protection

### Security Next Steps

1. **Authentication Enhancements**
   - [ ] Implement MFA support
   - [ ] Add OAuth2 provider integration
   - [ ] Enhance password policies
   - [ ] Add login attempt tracking

2. **Monitoring & Logging**
   - [ ] Set up security audit logging
   - [ ] Implement intrusion detection
   - [ ] Add automated vulnerability scanning
   - [ ] Configure error monitoring

3. **Infrastructure Security**
   - [ ] Set up WAF rules
   - [ ] Implement DDoS protection
   - [ ] Configure network security groups
   - [ ] Set up automated backups

4. **Compliance & Documentation**
   - [ ] Create security documentation
   - [ ] Implement audit trails
   - [ ] Add compliance reporting
   - [ ] Create incident response plan

## Configuration Management

### Environment Configuration
```plaintext
# API Configuration
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws

# Authentication
VITE_AUTH_STORAGE_KEY=hospital_metrics_auth
VITE_TOKEN_REFRESH_INTERVAL=600000

# Feature Flags
VITE_ENABLE_WEBSOCKET=true
VITE_ENABLE_3D_EFFECTS=true
VITE_ENABLE_ANIMATIONS=true

# Performance
VITE_MAX_FLOOR_INSTANCES=100
VITE_GEOMETRY_DETAIL_LEVEL=high
VITE_ENABLE_SHADOWS=true
```

### Database Configuration
```python
# Database connection settings
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hospital_metrics
DB_USER=<generated_secure_username>
DB_PASSWORD=<generated_secure_password>
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# Security settings
DB_SSL_MODE=require
ENABLE_HTTPS_REDIRECT=true
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Strict
```

### Configuration Next Steps

1. **Environment Management**
   - [ ] Add configuration validation
   - [ ] Implement secrets rotation
   - [ ] Add configuration versioning
   - [ ] Create deployment profiles

2. **Monitoring**
   - [ ] Add configuration auditing
   - [ ] Implement change tracking
   - [ ] Set up alerts for changes
   - [ ] Create configuration backups

3. **Documentation**
   - [ ] Document all configuration options
   - [ ] Create setup guides
   - [ ] Add troubleshooting guides
   - [ ] Create migration guides

## API Integration

### Data Flow Examples

#### Frontend Data Fetching
```typescript
// hooks/useMetrics.ts
export const useMetrics = () => {
  const { data: session } = useSession();
  const [metrics, setMetrics] = useState<DetailedMetrics>({
    floorMetrics: [],
    roomMetrics: []
  });

  const fetchMetricsForFloor = useCallback(async (floor: string) => {
    if (!session?.accessToken) return [];
    
    try {
      const response = await fetchFloorMetricsApi(floor, session.accessToken);
      return response.map(transformApiMetric);
    } catch (err) {
      handleApiError(err);
      return [];
    }
  }, [session]);

  // Usage in component
  useEffect(() => {
    if (selectedFloor) {
      fetchMetricsForFloor(selectedFloor)
        .then(metrics => setCurrentMetrics(metrics));
    }
  }, [selectedFloor, fetchMetricsForFloor]);
};

// components/FloorDetail.tsx
const FloorDetail: React.FC<FloorDetailProps> = ({ floor, metrics }) => {
  return (
    <group>
      {metrics.map(metric => (
        <HeatMapVisualization
          key={metric.id}
          value={metric.value}
          position={calculatePosition(metric)}
        />
      ))}
    </group>
  );
};
```

#### Data Models and Schemas
```python
# Backend: app/schemas/metrics.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FloorMetricBase(BaseModel):
    floor: str
    floor_id: str
    metric_name: str
    value: float
    metric_category: str
    timestamp: Optional[datetime] = None

class FloorMetricResponse(FloorMetricBase):
    id: int
    
    class Config:
        from_attributes = True  # Updated from orm_mode in Pydantic v2

# Frontend: types/metrics.ts
interface Metric {
  floor: string;
  room?: string;
  metric_name: string;
  value: number;
  timestamp: string;
  metric_type: string;
}
```

### Authentication Flow

#### Backend Implementation
```python
# routes/auth.py
from fastapi import APIRouter, Depends, HTTPException
from app.core.security import create_access_token
from app.models.user import User

router = APIRouter()

@router.post("/login")
async def login(
    credentials: UserCredentials,
    db: Session = Depends(get_db)
):
    user = authenticate_user(credentials.username, credentials.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user.email, "roles": user.roles}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# middleware/auth.py
async def verify_token_dependency(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = get_user_by_email(db, payload["sub"])
        if not user:
            raise HTTPException(status_code=401)
        return user
    except JWTError:
        raise HTTPException(status_code=401)
```

#### Frontend Authentication
```typescript
// services/api.ts
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// hooks/useAuth.ts
export const useAuth = () => {
  const { data: session } = useSession();
  
  const login = async (credentials: LoginCredentials) => {
    const { data } = await api.post('/auth/login', credentials);
    await signIn('credentials', {
      token: data.access_token,
      callbackUrl: '/'
    });
  };
};
```

### Role-Based Access Control
```python
# models/user.py
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    USER = "user"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    roles = Column(ARRAY(String), default=["user"])

# routes/metrics.py
@router.post("/metrics/admin")
async def create_metric(
    metric: MetricCreate,
    current_user: User = Depends(verify_token_dependency)
):
    if UserRole.ADMIN not in current_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Only admins can create metrics"
        )
    return await create_new_metric(metric)
```

## System Data Flow

### High-Level Architecture
```mermaid
graph TD
    subgraph Frontend
        UI[User Interface]
        R3F[React Three Fiber]
        HC[Hooks & Components]
        AS[API Service]
    end
    
    subgraph Backend
        API[FastAPI Server]
        Auth[Authentication]
        Met[Metrics Service]
        DB[(PostgreSQL)]
    end
    
    UI --> R3F
    R3F --> HC
    HC --> AS
    AS --> API
    API --> Auth
    API --> Met
    Met --> DB
    Auth --> DB
```

### Request Flow Example
```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as Auth Service
    participant M as Metrics API
    participant D as Database

    U->>F: Select Floor
    F->>A: Validate Token
    A-->>F: Token Valid
    F->>M: GET /api/v1/metrics/floors/{id}
    M->>D: Query Floor Metrics
    D-->>M: Return Metrics Data
    M-->>F: JSON Response
    F->>U: Update 3D Visualization
```

## API Examples

### Floor Metrics

#### Request
```http
GET /api/v1/metrics/floors/1W
Authorization: Bearer <token>
```

#### Response
```json
[
  {
    "id": 1,
    "floor": "1W",
    "floor_id": "1W",
    "metric_name": "patient_satisfaction",
    "value": 85.5,
    "metric_category": "Patient Metrics",
    "timestamp": "2024-12-20T14:26:36-07:00"
  },
  {
    "id": 2,
    "floor": "1W",
    "floor_id": "1W",
    "metric_name": "staff_retention",
    "value": 92.3,
    "metric_category": "Staff Metrics",
    "timestamp": "2024-12-20T14:26:36-07:00"
  }
]
```

### Room Metrics

#### Request
```http
GET /api/v1/metrics/floors/1W/rooms/101
Authorization: Bearer <token>
```

#### Response
```json
[
  {
    "id": 1,
    "room_id": "101",
    "floor": "1W",
    "floor_id": "1W",
    "metric_name": "equipment_utilization",
    "value": 78.9,
    "metric_category": "Room Metrics",
    "timestamp": "2024-12-20T14:26:36-07:00"
  }
]
```

## Troubleshooting Guide

### Common Issues

#### 1. Authentication Issues
```
Problem: 401 Unauthorized errors
Check:
- Token expiration in browser console
- Token presence in request headers
- Backend JWT_SECRET environment variable
Files to check:
- frontend/src/services/api.ts
- backend/app/core/security.py
```

#### 2. CORS Issues
```
Problem: API requests blocked by CORS
Solution:
1. Ensure backend CORS settings match frontend origin:
   ```python
   # backend/app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:3000"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
2. Check frontend API URL configuration:
   ```typescript
   // frontend/.env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
```

#### 3. Database Issues
```
Problem: Database connection errors
Check:
1. Database URL format:
   postgresql://user:password@localhost:5432/dbname

2. Run migrations:
   ```bash
   cd backend
   alembic upgrade head
   ```

3. Check connection in Python:
   ```python
   # backend/check_db.py
   from app.database import engine
   try:
       with engine.connect() as conn:
           result = conn.execute("SELECT 1")
           print("Database connection successful")
   except Exception as e:
       print(f"Database connection failed: {e}")
   ```
```

### For AI Assistants

#### Key Directories for Common Tasks

1. Adding New Metrics
```
- Backend Schema: backend/app/schemas/metrics.py
- Backend Model: backend/app/models/metrics.py
- Frontend Type: frontend/src/types/metrics.ts
- API Route: backend/app/routes/metrics.py
```

2. Modifying Visualization
```
- Main View: frontend/src/components/HospitalView.tsx
- Building Component: frontend/src/components/Building.tsx
- Floor Component: frontend/src/components/FloorDetail.tsx
```

3. Authentication Changes
```
- Backend Auth: backend/app/core/security.py
- Frontend Auth: frontend/src/hooks/useAuth.ts
- Auth Routes: backend/app/routes/auth.py
```

#### Common Error Locations

1. API Errors
```
- Check route implementation: backend/app/routes/
- Check error middleware: backend/app/core/middleware.py
- Check API service: frontend/src/services/api.ts
```

2. Visualization Errors
```
- Check scene setup: frontend/src/components/HospitalView.tsx
- Check geometry: frontend/src/components/Building.tsx
- Check material properties: frontend/src/utils/materials.ts
```

3. Data Flow Errors
```
- Check API response format: backend/app/schemas/
- Check data transformation: frontend/src/services/
- Check state management: frontend/src/hooks/
```

## Deployment Configuration

### Docker Setup
```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend Dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
CMD ["npm", "start"]

# docker-compose.yml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/hospital_metrics
    depends_on:
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=hospital_metrics
```

### CI/CD Pipeline
```yaml
# .github/workflows/main.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Run Backend Tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest
          
      - name: Setup Node
        uses: actions/setup-node@v2
        with:
          node-version: '16'
          
      - name: Run Frontend Tests
        run: |
          cd frontend
          npm install
          npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Production
        run: |
          # Add deployment steps here
```

## Performance Optimization

### Frontend Optimization
```typescript
// Geometric Instancing Example
const RoomInstances: React.FC<{ rooms: Room[] }> = ({ rooms }) => {
  const geometry = useMemo(() => new BoxGeometry(1, 1, 1), []);
  const material = useMemo(() => new MeshStandardMaterial(), []);
  
  return (
    <instancedMesh
      args={[geometry, material, rooms.length]}
      count={rooms.length}
    >
      {rooms.map((room, i) => (
        <RoomInstance
          key={room.id}
          index={i}
          position={room.position}
        />
      ))}
    </instancedMesh>
  );
};

// Memoization Example
const MetricsDisplay = React.memo(({ metrics }: MetricsDisplayProps) => {
  return (
    <div>
      {metrics.map(metric => (
        <MetricItem key={metric.id} {...metric} />
      ))}
    </div>
  );
});
```

### Backend Query Optimization
```python
# Optimized SQLAlchemy Query
from sqlalchemy import func
from sqlalchemy.orm import joinedload

async def get_floor_metrics(floor_id: str, db: Session):
    return (
        db.query(FloorMetric)
        .options(
            joinedload(FloorMetric.definition),
            joinedload(FloorMetric.rooms)
        )
        .filter(FloorMetric.floor_id == floor_id)
        .filter(FloorMetric.timestamp >= func.now() - timedelta(days=7))
        .order_by(FloorMetric.timestamp.desc())
    ).all()

# Index Creation
from alembic import op

def upgrade():
    op.create_index(
        'idx_floor_metrics_floor_timestamp',
        'floor_metrics',
        ['floor_id', 'timestamp'],
        postgresql_using='btree'
    )
```

## Security Considerations

### Authentication
- JWT tokens with short expiry
- Secure token storage
- CSRF protection
- Rate limiting on auth endpoints

### Data Protection
- Input validation
- SQL injection prevention
- XSS protection
- CORS configuration

### API Security
- HTTPS only
- API versioning
- Request validation
- Response sanitization

## Development Guidelines

### Code Style
- TypeScript for frontend
- Python type hints
- ESLint configuration
- Black for Python formatting

### Testing
- Jest for frontend
- Pytest for backend
- E2E tests with Cypress
- CI/CD pipeline

### Documentation
- OpenAPI/Swagger
- TSDoc for TypeScript
- Python docstrings
- Architecture diagrams

## Deployment

### Frontend
- Static file hosting
- CDN integration
- Environment configuration
- Build optimization

### Backend
- Docker containerization
- Database migrations
- Environment variables
- Logging setup

## Monitoring

### Metrics
- API response times
- Error rates
- User activity
- System resources

### Alerts
- Service availability
- Error thresholds
- Performance degradation
- Security events
