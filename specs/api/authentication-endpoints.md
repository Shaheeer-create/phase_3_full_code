# Authentication API Endpoints

## Overview

Authentication endpoints for user registration, login, and profile management using JWT tokens.

## Base URL

```
http://localhost:8000/api/auth
```

---

## Endpoints

### 1. Register User

**POST** `/api/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

**Validation Rules:**
- `email`: Required, valid email format, unique
- `password`: Required, minimum 8 characters
- `name`: Required, 1-100 characters

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2026-02-01T10:00:00Z"
  }
}
```

**Error Responses:**

**409 Conflict** - Email already registered
```json
{
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "An account with this email already exists"
  }
}
```

**422 Unprocessable Entity** - Validation failed
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "email": "Invalid email format",
      "password": "Password must be at least 8 characters"
    }
  }
}
```

---

### 2. Login

**POST** `/api/auth/login`

Authenticate user and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Error Responses:**

**401 Unauthorized** - Invalid credentials
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

---

### 3. Get Current User

**GET** `/api/auth/me`

Get currently authenticated user's profile.

**Headers:**
```
Authorization: Bearer <token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-02-01T10:00:00Z",
  "updated_at": "2026-02-01T10:00:00Z"
}
```

**Error Responses:**

**401 Unauthorized** - Missing or invalid token
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```

---

## Authentication Flow

```
1. Register/Login
   User → POST /api/auth/register or /api/auth/login
   ↓
   Server validates credentials
   ↓
   Server generates JWT token
   ↓
   Server returns token + user data

2. Authenticated Requests
   User → GET /api/tasks (with Authorization header)
   ↓
   Server verifies JWT token
   ↓
   Server extracts user_id from token
   ↓
   Server returns user's data only
```

---

## JWT Token Structure

**Payload:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "exp": 1738411200,
  "iat": 1738324800
}
```

**Expiration:** 24 hours

**Algorithm:** HS256

---

## Security Considerations

1. **Password Storage**
   - Passwords hashed with bcrypt
   - Never store plain text passwords
   - Minimum 8 characters required

2. **Token Security**
   - JWT tokens signed with secret key
   - Tokens expire after 24 hours
   - Store tokens securely on client (httpOnly cookies or localStorage)

3. **Rate Limiting**
   - Login: 5 attempts per minute per IP
   - Register: 3 attempts per minute per IP

4. **HTTPS Required**
   - All authentication endpoints require HTTPS in production
   - Tokens transmitted over secure connection only
