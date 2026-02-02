# Authentication Patterns

Comprehensive patterns for implementing JWT authentication and authorization in FastAPI.

## Table of Contents
- JWT Basics
- Token Generation
- Token Verification
- Protected Routes
- User Isolation
- Refresh Tokens
- Password Hashing

---

## JWT Basics

### What is JWT?

JSON Web Token (JWT) is a compact, URL-safe token format for securely transmitting information between parties.

**Structure:**
```
header.payload.signature
```

**Example:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzIiwiZXhwIjoxNjQwOTk1MjAwfQ.signature
```

**Payload:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "exp": 1640995200
}
```

### Installation

```bash
pip install python-jose[cryptography]
pip install passlib[bcrypt]
pip install python-multipart
```

---

## Token Generation

### Basic Token Creation

```python
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

SECRET_KEY = "your-secret-key-here"  # Load from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Usage
token = create_access_token(
    data={"user_id": str(user.id), "email": user.email}
)
```

### With Custom Claims

```python
def create_access_token(
    user_id: UUID,
    email: str,
    roles: list[str] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    payload = {
        "user_id": str(user_id),
        "email": email,
        "roles": roles or [],
        "iat": datetime.utcnow(),  # Issued at
        "exp": datetime.utcnow() + (expires_delta or timedelta(hours=24))
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

---

## Token Verification

### Basic Verification

```python
from jose import JWTError, jwt
from fastapi import HTTPException, status

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### With Expiration Check

```python
from datetime import datetime

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Check expiration
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has no expiration"
            )

        if datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )

        return payload

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

---

## Protected Routes

### Bearer Token Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from uuid import UUID

security = HTTPBearer()

def get_current_user_id(
    credentials: HTTPAuthCredentials = Depends(security)
) -> UUID:
    """Extract and verify user ID from JWT token."""
    payload = verify_token(credentials.credentials)

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    return UUID(user_id)

# Usage in endpoint
@app.get("/api/tasks")
async def list_tasks(
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
    return tasks
```

### Get Full User

```python
from sqlmodel import Session, select

def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """Get current user from token."""
    payload = verify_token(credentials.credentials)
    user_id = UUID(payload.get("user_id"))

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user

# Usage
@app.get("/api/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user
```

---

## User Isolation

### Query Filtering

```python
@app.get("/api/tasks")
async def list_tasks(
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    # ALWAYS filter by user_id
    tasks = session.exec(
        select(Task).where(Task.user_id == user_id)
    ).all()
    return tasks
```

### Resource Access Check

```python
@app.get("/api/tasks/{task_id}")
async def get_task(
    task_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Check ownership
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task"
        )

    return task
```

### Reusable Access Check

```python
def verify_task_access(
    task_id: UUID,
    user_id: UUID,
    session: Session
) -> Task:
    """Verify user has access to task."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return task

# Usage
@app.patch("/api/tasks/{task_id}")
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    user_id: UUID = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    task = verify_task_access(task_id, user_id, session)
    # Update task
    return task
```

---

## Login Endpoint

### Basic Login

```python
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    session: Session = Depends(get_session)
):
    # Find user
    user = session.exec(
        select(User).where(User.email == credentials.email)
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create token
    access_token = create_access_token(
        data={"user_id": str(user.id), "email": user.email}
    )

    return {"access_token": access_token, "token_type": "bearer"}
```

---

## Registration Endpoint

### Basic Registration

```python
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str

@app.post("/api/auth/register", response_model=LoginResponse)
async def register(
    user_data: RegisterRequest,
    session: Session = Depends(get_session)
):
    # Check if user exists
    existing_user = session.exec(
        select(User).where(User.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    # Create token
    access_token = create_access_token(
        data={"user_id": str(user.id), "email": user.email}
    )

    return {"access_token": access_token, "token_type": "bearer"}
```

---

## Password Hashing

### Using Passlib

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)
```

---

## Refresh Tokens

### Token Pair

```python
def create_token_pair(user_id: UUID, email: str) -> dict:
    """Create access and refresh tokens."""
    access_token = create_access_token(
        data={"user_id": str(user_id), "email": email, "type": "access"},
        expires_delta=timedelta(minutes=15)
    )

    refresh_token = create_access_token(
        data={"user_id": str(user_id), "email": email, "type": "refresh"},
        expires_delta=timedelta(days=7)
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
```

### Refresh Endpoint

```python
class RefreshRequest(BaseModel):
    refresh_token: str

@app.post("/api/auth/refresh")
async def refresh_token(request: RefreshRequest):
    try:
        payload = jwt.decode(
            request.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        # Verify it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )

        # Create new access token
        user_id = payload.get("user_id")
        email = payload.get("email")

        new_access_token = create_access_token(
            data={"user_id": user_id, "email": email, "type": "access"},
            expires_delta=timedelta(minutes=15)
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
```

---

## Role-Based Access Control

### With Roles

```python
def require_role(required_role: str):
    """Dependency to check user role."""
    def role_checker(
        credentials: HTTPAuthCredentials = Depends(security)
    ) -> UUID:
        payload = verify_token(credentials.credentials)

        roles = payload.get("roles", [])
        if required_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )

        return UUID(payload.get("user_id"))

    return role_checker

# Usage
@app.delete("/api/users/{user_id}")
async def delete_user(
    user_id: UUID,
    admin_id: UUID = Depends(require_role("admin"))
):
    # Only admins can delete users
    pass
```

---

## Best Practices

### 1. Use Environment Variables

```python
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    class Config:
        env_file = ".env"

settings = Settings()
```

### 2. Secure Secret Key

```python
# Generate secure secret key
import secrets
secret_key = secrets.token_urlsafe(32)

# Store in .env file
# SECRET_KEY=your-generated-secret-key
```

### 3. Use HTTPS

Always use HTTPS in production to prevent token interception.

### 4. Short Token Expiration

```python
# Short-lived access tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# Long-lived refresh tokens
REFRESH_TOKEN_EXPIRE_DAYS = 7
```

### 5. Validate Token Claims

```python
def verify_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    # Validate required claims
    required_claims = ["user_id", "email", "exp"]
    for claim in required_claims:
        if claim not in payload:
            raise HTTPException(
                status_code=401,
                detail=f"Missing required claim: {claim}"
            )

    return payload
```

### 6. Rate Limit Login

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginRequest):
    # Login logic
    pass
```

---

## Complete Example

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from uuid import UUID
from pydantic import BaseModel, EmailStr

app = FastAPI()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

# Token functions
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Password functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# Dependencies
def get_current_user_id(
    credentials: HTTPAuthCredentials = Depends(security)
) -> UUID:
    payload = verify_token(credentials.credentials)
    return UUID(payload["user_id"])

# Endpoints
@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    user = get_user_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": str(user.id), "email": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/api/tasks")
async def list_tasks(user_id: UUID = Depends(get_current_user_id)):
    return get_user_tasks(user_id)
```

---

## Summary

**Key Points:**
1. Use JWT for stateless authentication
2. Hash passwords with bcrypt
3. Implement user isolation in all queries
4. Use short-lived access tokens
5. Implement refresh tokens for better UX
6. Validate all token claims
7. Use HTTPS in production
8. Rate limit authentication endpoints
9. Store secrets in environment variables
10. Test authentication thoroughly
