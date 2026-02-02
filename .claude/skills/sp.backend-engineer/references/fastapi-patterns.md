# FastAPI Patterns

Comprehensive patterns for implementing FastAPI endpoints.

## Table of Contents
- Endpoint Basics
- Dependency Injection
- Response Models
- Error Handling
- Middleware
- Background Tasks

---

## Endpoint Basics

### Basic Endpoint

```python
from fastapi import FastAPI, status

app = FastAPI()

@app.get("/api/tasks")
async def list_tasks():
    return {"tasks": []}

@app.post("/api/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task_data: dict):
    return {"id": "123", **task_data}
```

### Path Parameters

```python
from uuid import UUID

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: UUID):
    return {"id": task_id, "title": "Task"}

@app.delete("/api/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: UUID):
    # Delete task
    return None
```

### Query Parameters

```python
from typing import Optional

@app.get("/api/tasks")
async def list_tasks(
    page: int = 1,
    page_size: int = 20,
    completed: Optional[bool] = None,
    search: Optional[str] = None
):
    return {"page": page, "page_size": page_size}
```

### Request Body

```python
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

@app.post("/api/tasks")
async def create_task(task: TaskCreate):
    return {"title": task.title}
```

---

## Dependency Injection

### Database Session

```python
from sqlmodel import Session
from fastapi import Depends

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/api/tasks")
async def list_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks
```

### Authentication

```python
from fastapi import Depends, HTTPException, status
from uuid import UUID

async def get_current_user_id(
    token: str = Depends(oauth2_scheme)
) -> UUID:
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user_id

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

### Pagination

```python
from fastapi import Query

class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100)
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size

@app.get("/api/tasks")
async def list_tasks(
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session)
):
    tasks = session.exec(
        select(Task)
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    return tasks
```

---

## Response Models

### Basic Response Model

```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class TaskResponse(BaseModel):
    id: UUID
    title: str
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

### List Response

```python
class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    page: int
    page_size: int

@app.get("/api/tasks", response_model=TaskListResponse)
async def list_tasks(
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session)
):
    tasks = session.exec(
        select(Task)
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()

    total = session.exec(select(func.count(Task.id))).one()

    return {
        "items": tasks,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size
    }
```

### Exclude Fields

```python
class TaskResponse(BaseModel):
    id: UUID
    title: str
    user_id: UUID

    class Config:
        from_attributes = True

@app.get("/api/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: UUID):
    # user_id will be included

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: UUID) -> TaskResponse:
    # Can exclude fields dynamically
    task = get_task_from_db(task_id)
    return TaskResponse.from_orm(task).dict(exclude={'user_id'})
```

---

## Error Handling

### HTTPException

```python
from fastapi import HTTPException, status

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: UUID, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task
```

### Custom Exception Handler

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class TaskNotFoundError(Exception):
    def __init__(self, task_id: UUID):
        self.task_id = task_id

@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "TASK_NOT_FOUND",
                "message": f"Task with ID {exc.task_id} not found"
            }
        }
    )
```

### Validation Error Handler

```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for error in exc.errors():
        field = '.'.join(str(loc) for loc in error['loc'][1:])
        errors[field] = error['msg']

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": errors
            }
        }
    )
```

---

## Middleware

### CORS Middleware

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Custom Middleware

```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Request ID Middleware

```python
import uuid

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

---

## Background Tasks

### Basic Background Task

```python
from fastapi import BackgroundTasks

def send_email(email: str, message: str):
    # Send email
    print(f"Sending email to {email}: {message}")

@app.post("/api/tasks")
async def create_task(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    # Create task
    new_task = Task(**task.dict())
    session.add(new_task)
    session.commit()

    # Send notification in background
    background_tasks.add_task(
        send_email,
        "user@example.com",
        f"Task '{new_task.title}' created"
    )

    return new_task
```

---

## Router Organization

### Separate Routers

```python
# app/routers/tasks.py
from fastapi import APIRouter

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.get("")
async def list_tasks():
    return []

@router.post("")
async def create_task():
    return {}

# app/main.py
from app.routers import tasks

app = FastAPI()
app.include_router(tasks.router)
```

---

## Best Practices

1. **Use dependency injection** for database sessions and auth
2. **Define response models** for type safety and documentation
3. **Handle errors consistently** with custom exception handlers
4. **Use routers** to organize endpoints
5. **Add middleware** for cross-cutting concerns
6. **Use background tasks** for async operations
7. **Document endpoints** with descriptions and examples
8. **Validate input** with Pydantic models
9. **Use status codes** correctly
10. **Test endpoints** thoroughly

---

## Complete Example

```python
from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from uuid import UUID
from typing import Optional

app = FastAPI(title="Task API", version="1.0.0")

# Dependency
def get_session():
    with Session(engine) as session:
        yield session

# Router
router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.get("", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    completed: Optional[bool] = None,
    session: Session = Depends(get_session),
    user_id: UUID = Depends(get_current_user_id)
):
    """List tasks with pagination and filtering."""
    query = select(Task).where(Task.user_id == user_id)

    if completed is not None:
        query = query.where(Task.completed == completed)

    total = len(session.exec(query).all())
    offset = (page - 1) * page_size
    tasks = session.exec(query.offset(offset).limit(page_size)).all()

    return {
        "items": tasks,
        "total": total,
        "page": page,
        "page_size": page_size
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
    """Get a single task."""
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    return task

app.include_router(router)
```
