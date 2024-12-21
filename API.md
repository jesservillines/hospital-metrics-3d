# Hospital 3D Metrics API Documentation

## Authentication

### Register User
- **Endpoint**: `POST /api/v1/auth/register`
- **Description**: Register a new user
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "confirm_password": "string"
  }
  ```
- **Response**:
  ```json
  {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "is_active": true,
    "created_at": "datetime"
  }
  ```

### Login
- **Endpoint**: `POST /api/v1/auth/login`
- **Description**: Login and receive JWT token
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string",
    "remember_me": false
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer"
  }
  ```

### Get Current User
- **Endpoint**: `GET /api/v1/auth/me`
- **Description**: Get current user info
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "role": "string",
    "is_active": true,
    "is_verified": true,
    "created_at": "datetime",
    "last_login": "datetime"
  }
  ```

### Logout
- **Endpoint**: `POST /api/v1/auth/logout`
- **Description**: Logout and blacklist token
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `204 No Content`

### Reset Password Request
- **Endpoint**: `POST /api/v1/auth/reset-password`
- **Description**: Request password reset
- **Request Body**:
  ```json
  {
    "email": "string"
  }
  ```
- **Response**: `200 OK`

### Reset Password Confirm
- **Endpoint**: `POST /api/v1/auth/reset-password-confirm`
- **Description**: Confirm password reset
- **Request Body**:
  ```json
  {
    "token": "string",
    "new_password": "string",
    "confirm_password": "string"
  }
  ```
- **Response**: `200 OK`

## Profile Management

### Get User Profile
- **Endpoint**: `GET /api/v1/profile`
- **Description**: Get user profile
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "role": "string",
    "is_active": true,
    "is_verified": true,
    "created_at": "datetime",
    "last_login": "datetime"
  }
  ```

### Update User Profile
- **Endpoint**: `POST /api/v1/profile/update`
- **Description**: Update user profile
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "email": "string",
    "current_password": "string",
    "new_password": "string"
  }
  ```
- **Response**: `200 OK`

### Get User Activity
- **Endpoint**: `GET /api/v1/profile/activity`
- **Description**: Get user activity history
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "sessions": [
      {
        "id": "uuid",
        "ip_address": "string",
        "user_agent": "string",
        "created_at": "datetime",
        "last_active": "datetime"
      }
    ]
  }
  ```

## Admin Management

### Get Admin Profile
- **Endpoint**: `GET /api/v1/admin/profile`
- **Description**: Get admin profile
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "role": "ADMIN",
    "is_active": true,
    "is_verified": true,
    "created_at": "datetime",
    "last_login": "datetime",
    "roles": [
      {
        "id": "uuid",
        "name": "string",
        "permissions": ["string"]
      }
    ]
  }
  ```

### List Users
- **Endpoint**: `GET /api/v1/admin/users`
- **Description**: List all users
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  [
    {
      "id": "uuid",
      "username": "string",
      "email": "string",
      "role": "string",
      "is_active": true,
      "last_login": "datetime"
    }
  ]
  ```

### Get User Details
- **Endpoint**: `GET /api/v1/admin/users/{user_id}`
- **Description**: Get specific user
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "id": "uuid",
    "username": "string",
    "email": "string",
    "role": "string",
    "is_active": true,
    "is_verified": true,
    "created_at": "datetime",
    "last_login": "datetime"
  }
  ```

### Update User
- **Endpoint**: `PUT /api/v1/admin/users/{user_id}`
- **Description**: Update user
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "email": "string",
    "role": "string",
    "is_active": true
  }
  ```
- **Response**: `200 OK`

### List Roles
- **Endpoint**: `GET /api/v1/admin/roles`
- **Description**: List all roles
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  [
    {
      "id": "uuid",
      "name": "string",
      "permissions": ["string"]
    }
  ]
  ```

### Create Role
- **Endpoint**: `POST /api/v1/admin/roles`
- **Description**: Create new role
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "name": "string",
    "permissions": ["string"]
  }
  ```
- **Response**:
  ```json
  {
    "id": "uuid",
    "name": "string",
    "permissions": ["string"]
  }
  ```

### Update Role Access
- **Endpoint**: `PUT /api/v1/admin/roles/{role_id}`
- **Description**: Update role access
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "permissions": ["string"]
  }
  ```
- **Response**: `200 OK`

## Metrics Management

### Get All Metrics
- **Endpoint**: `GET /api/v1/metrics`
- **Description**: Get all metrics
- **Headers**: `Authorization: Bearer <token>`
- **Query Parameters**:
  - `category`: Filter by category
  - `start_date`: Filter by start date
  - `end_date`: Filter by end date
- **Response**:
  ```json
  [
    {
      "id": "uuid",
      "name": "string",
      "category": "string",
      "value": "number",
      "unit": "string",
      "timestamp": "datetime"
    }
  ]
  ```

### Get Metric Details
- **Endpoint**: `GET /api/v1/metrics/{metric_id}`
- **Description**: Get specific metric
- **Headers**: `Authorization: Bearer <token>`
- **Response**:
  ```json
  {
    "id": "uuid",
    "name": "string",
    "category": "string",
    "value": "number",
    "unit": "string",
    "timestamp": "datetime",
    "metadata": {
      "source": "string",
      "confidence": "number"
    }
  }
  ```

### Create Metric
- **Endpoint**: `POST /api/v1/metrics`
- **Description**: Create new metric
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "name": "string",
    "category": "string",
    "value": "number",
    "unit": "string",
    "metadata": {
      "source": "string",
      "confidence": "number"
    }
  }
  ```
- **Response**:
  ```json
  {
    "id": "uuid",
    "name": "string",
    "category": "string",
    "value": "number",
    "unit": "string",
    "timestamp": "datetime",
    "metadata": {
      "source": "string",
      "confidence": "number"
    }
  }
  ```

### Update Metric
- **Endpoint**: `PUT /api/v1/metrics/{metric_id}`
- **Description**: Update metric
- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "value": "number",
    "metadata": {
      "source": "string",
      "confidence": "number"
    }
  }
  ```
- **Response**: `200 OK`

### Delete Metric
- **Endpoint**: `DELETE /api/v1/metrics/{metric_id}`
- **Description**: Delete metric
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `204 No Content`

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid authentication credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```
