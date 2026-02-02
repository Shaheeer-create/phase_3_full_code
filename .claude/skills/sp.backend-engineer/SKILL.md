---
name: sp.backend-engineer
description: Implement FastAPI endpoints with SQLModel, database operations, and authentication. Use when the user needs to: (1) Implement REST API endpoints, (2) Create database models with SQLModel, (3) Implement CRUD operations, (4) Add authentication and authorization, (5) Handle request validation, (6) Implement user data isolation, or (7) Add error handling and logging. Should be run after API contracts are designed.
---

# Backend Engineer

Implement production-ready FastAPI endpoints with SQLModel, database operations, authentication, and comprehensive error handling.

## Workflow

### 1. Gather Context

Read existing specifications and design:
- `specs/api/<feature>-endpoints.md` - API contracts (REQUIRED)
- `specs/database/schema.md` - Database models
- `specs/architecture.md` - Tech stack, auth strategy, database config
- `specs/features/<feature>.md` - Feature requirements
- Project CLAUDE.md - Backend conventions and standards

Extract:
- API endpoints to implement
- Request/response schemas
- Database models and relationships
- Authentication requirements
- Validation rules
- User isolation requirements

### 2. Setup Project Structure

Organize backend code following FastAPI best practices.

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── dependencies.py      # Dependency injection
│   ├── models/              # SQLModel models
│   │   ├── __init__.py
│   │   ├── task.py
│   │   └── user.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── task.py
│   │   └── user.py
│   ├── routers/             # API routers
│   │   ├── __init__.py
│   │   ├── tasks.py
│   │   └── auth.py
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── task_service.py
│   │   └── auth_service.py
│   └── utils/               # Utilities
│       ├── __init__.py
│       ├── auth.py
│       └── errors.py
├── tests/
├── requirements.txt
└── .env.example
```

### 3. Create Database Models

Define SQLModel models for database tables. See [references/sqlmodel-patterns.md](references/sqlmodel-patterns.md) for detailed patterns.

```python
# app/models/task.py
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    priority: str = Field(default="medium")  # low, medium, high
    completed: bool = Field(default=False, index=True)
    due_date: Optional[datetime] = Field(default=None)
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Foreign key
    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Relationship
    user: Optional["User"] = Relationship(back_populates="tasks")
```

### 4. Create Request/Response Schemas

Define Pydantic schemas for API validation. See [references/pydantic-validation.md](references/pydantic-validation.md) for validation patterns.

```python
# app/schemas/task.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from uuid import UUID

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: str = Field(default="medium")
    due_date: Optional[datetime] = None
    tags: list[str] = Field(default_factory=list)

    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError('Priority must be low, medium, or high')
        return v

    @validator('due_date')
    def validate_due_date(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    tags: Optional[list[str]] = None

class TaskResponse(TaskBase):
    id: UUID
    completed: bool
    created_at: datetime
    updated_at: datetime
    user_id: UUID

    class Config:
        from_attributes = True
```

### 5. Implement Authentication

Setup JWT authentication and user isolation. See [references/auth-patterns.md](references/auth-patterns.md) for comprehensive auth patterns.

```python
# app/utils/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

security = HTTPBearer()

SECRET_KEY = "your-secret-key"  # Load from env
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthCredentials = Depends(security)) -> UUID:
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return UUID(user_id)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# Dependency for protected routes
async def get_current_user_id(
    user_id: UUID = Depends(verify_token)
) -> UUID:
    return user_id
```

### 6. Implement API Endpoints

Create FastAPI routers with CRUD operations. See [references/fastapi-patterns.md](references/fastapi-patterns.md) for endpoint patterns.

```python
# app/routers/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from uuid import UUID
from typing import List

from app.database import get_session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.utils.auth import get_current_user_id

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.get("", response_model=dict)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    completed: Optional[bool] = None,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """List tasks with pagination and filtering."""
    # Build query with user isolation
    query = select(Task).where(Task.user_id == user_id)

    # Apply filters
    if completed is not None:
        query = query.where(Task.completed == completed)

    # Get total count
    total = len(session.exec(query).all())

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    tasks = session.exec(query).all()

    return {
        "items": tasks,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "has_previous": page > 1,
            "has_next": offset + page_size < total
        }
    }

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Create a new task."""
    task = Task(**task_data.dict(), user_id=user_id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Get a single task by ID."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # User isolation check
    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task"
        )

    return task

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Update a task."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to update this task"
        )

    # Update only provided fields
    update_data = task_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """Delete a task."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this task"
        )

    session.delete(task)
    session.commit()
```

### 7. Implement Error Handling

Add global exception handlers and error responses.

```python
# app/main.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

app = FastAPI(title="Task Management API", version="1.0.0")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for error in exc.errors():
        field = error["loc"][-1]
        errors[field] = error["msg"]

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": errors
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )
```

### 8. Setup Database Connection

Configure database connection and session management.

```python
# app/database.py
from sqlmodel import create_engine, Session, SQLModel
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
```

### 9. Create Output Files

Generate backend implementation files:

**Models**: `app/models/<resource>.py`
- SQLModel table definitions
- Relationships
- Indexes

**Schemas**: `app/schemas/<resource>.py`
- Request schemas (Create, Update)
- Response schemas
- Validation rules

**Routers**: `app/routers/<resource>.py`
- API endpoint implementations
- CRUD operations
- User isolation
- Error handling

**Services**: `app/services/<resource>_service.py` (optional)
- Business logic
- Complex operations
- Reusable functions

**Utils**: `app/utils/`
- Authentication helpers
- Error handlers
- Common utilities

**Configuration**: `app/config.py`
- Environment variables
- Settings management

**Main App**: `app/main.py`
- FastAPI app initialization
- Router registration
- Middleware setup
- Exception handlers

### 10. Integration with Workflow

**Before running this skill**:
- API contracts designed (`/sp.api-designer` completed)
- Database schema defined
- Authentication strategy documented

**After running this skill**:
- Backend endpoints ready for testing
- Run tests to verify implementation
- Deploy to staging environment

**PHR Creation**:
- Create PHR in `history/prompts/<feature-name>/`
- Stage: `green` (implementation work)
- Include links to created backend files

**ADR Suggestions**:
Suggest ADR for significant backend decisions:
- Database connection pooling strategy
- Caching approach
- Background task processing
- File storage solution

Example: "📋 Architectural decision detected: Using connection pooling with pool_pre_ping for database reliability. Document reasoning? Run `/sp.adr database-connection-pooling`"

## Usage Examples

Basic usage:
```
/sp.backend-engineer task-crud
```

Specific feature:
```
/sp.backend-engineer authentication
```

With tests:
```
/sp.backend-engineer task-crud --with-tests
```

## Success Criteria

- [ ] Database models created with SQLModel
- [ ] Request/response schemas defined with Pydantic
- [ ] All CRUD endpoints implemented
- [ ] Authentication and authorization working
- [ ] User data isolation enforced
- [ ] Request validation implemented
- [ ] Error handling comprehensive
- [ ] Database queries optimized
- [ ] Logging configured
- [ ] PHR created
- [ ] ADR suggested for significant decisions

## Implementation Checklist

**Database**:
- [ ] SQLModel models defined
- [ ] Relationships configured
- [ ] Indexes added for performance
- [ ] Migrations created (if using Alembic)

**API Endpoints**:
- [ ] All CRUD operations implemented
- [ ] Pagination working
- [ ] Filtering and sorting working
- [ ] Request validation working
- [ ] Response schemas correct

**Authentication**:
- [ ] JWT token generation
- [ ] Token verification
- [ ] Protected routes
- [ ] User isolation enforced

**Error Handling**:
- [ ] Validation errors (422)
- [ ] Not found errors (404)
- [ ] Authorization errors (403)
- [ ] Server errors (500)
- [ ] Consistent error format

**Testing**:
- [ ] Unit tests for services
- [ ] Integration tests for endpoints
- [ ] Authentication tests
- [ ] Error case tests

## References

- [SQLModel Patterns](references/sqlmodel-patterns.md) - Database models and relationships
- [Pydantic Validation](references/pydantic-validation.md) - Request validation patterns
- [FastAPI Patterns](references/fastapi-patterns.md) - Endpoint implementation patterns
- [Auth Patterns](references/auth-patterns.md) - JWT authentication and authorization
