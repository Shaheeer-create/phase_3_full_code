# Error Handling

Comprehensive guide to designing error responses and handling errors in REST APIs.

## Table of Contents
- Error Response Format
- HTTP Status Codes
- Error Codes
- Validation Errors
- Error Messages
- Best Practices

---

## Error Response Format

### Standard Error Structure

Use a consistent error format across all endpoints:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}  // Optional, for additional context
  }
}
```

### Components

**code**: Machine-readable error identifier
- UPPER_SNAKE_CASE format
- Unique across application
- Used by clients for error handling

**message**: Human-readable description
- Clear and actionable
- Suitable for displaying to users
- Localized if supporting multiple languages

**details**: Additional context (optional)
- Field-level validation errors
- Stack traces (development only)
- Request ID for debugging
- Timestamp

---

## HTTP Status Codes

### Success Codes (2xx)

**200 OK**
```
GET /api/tasks/123
200 OK
{ "id": "123", "title": "Task" }
```
Use for: Successful GET, PUT, PATCH

**201 Created**
```
POST /api/tasks
201 Created
Location: /api/tasks/456
{ "id": "456", "title": "New Task" }
```
Use for: Successful POST (resource created)

**204 No Content**
```
DELETE /api/tasks/123
204 No Content
```
Use for: Successful DELETE (no response body)

### Client Error Codes (4xx)

**400 Bad Request**
```json
POST /api/tasks
400 Bad Request
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Request body is not valid JSON"
  }
}
```
Use for:
- Malformed JSON
- Invalid request format
- Missing required headers

**401 Unauthorized**
```json
GET /api/tasks
401 Unauthorized
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}
```
Use for:
- Missing authentication token
- Invalid authentication token
- Expired token

**403 Forbidden**
```json
DELETE /api/tasks/123
403 Forbidden
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You don't have permission to delete this task"
  }
}
```
Use for:
- Valid authentication, insufficient permissions
- User trying to access another user's resource
- Action not allowed for user role

**404 Not Found**
```json
GET /api/tasks/999
404 Not Found
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found"
  }
}
```
Use for:
- Resource doesn't exist
- Endpoint doesn't exist

**409 Conflict**
```json
POST /api/tasks
409 Conflict
{
  "error": {
    "code": "DUPLICATE_TASK",
    "message": "A task with this title already exists"
  }
}
```
Use for:
- Duplicate resource
- Conflicting state (e.g., deleting completed task)
- Concurrent modification conflict

**422 Unprocessable Entity**
```json
POST /api/tasks
422 Unprocessable Entity
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "title": "Title is required",
      "due_date": "Due date must be in the future"
    }
  }
}
```
Use for:
- Valid JSON, but failed business validation
- Field-level validation errors
- Semantic errors

**429 Too Many Requests**
```json
POST /api/tasks
429 Too Many Requests
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests. Please try again in 60 seconds.",
    "details": {
      "retry_after": 60
    }
  }
}
```
Use for:
- Rate limit exceeded
- Too many requests from IP/user

### Server Error Codes (5xx)

**500 Internal Server Error**
```json
GET /api/tasks
500 Internal Server Error
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "details": {
      "request_id": "abc-123-def"
    }
  }
}
```
Use for:
- Unexpected server errors
- Unhandled exceptions
- Database connection failures

**502 Bad Gateway**
```json
GET /api/tasks
502 Bad Gateway
{
  "error": {
    "code": "BAD_GATEWAY",
    "message": "Upstream service unavailable"
  }
}
```
Use for:
- Proxy/gateway errors
- Upstream service failures

**503 Service Unavailable**
```json
GET /api/tasks
503 Service Unavailable
{
  "error": {
    "code": "SERVICE_UNAVAILABLE",
    "message": "Service temporarily unavailable. Please try again later.",
    "details": {
      "retry_after": 300
    }
  }
}
```
Use for:
- Maintenance mode
- Service overload
- Temporary outages

---

## Error Codes

### Naming Convention

Use UPPER_SNAKE_CASE and be descriptive:

```
VALIDATION_ERROR
NOT_FOUND
UNAUTHORIZED
FORBIDDEN
DUPLICATE_RESOURCE
INVALID_INPUT
RATE_LIMIT_EXCEEDED
INTERNAL_ERROR
```

### Common Error Codes

**Authentication/Authorization:**
```
UNAUTHORIZED          - Missing or invalid token
FORBIDDEN             - Insufficient permissions
TOKEN_EXPIRED         - Auth token expired
INVALID_CREDENTIALS   - Wrong username/password
```

**Validation:**
```
VALIDATION_ERROR      - General validation failure
REQUIRED_FIELD        - Required field missing
INVALID_FORMAT        - Field format invalid
INVALID_VALUE         - Field value invalid
```

**Resource:**
```
NOT_FOUND             - Resource doesn't exist
DUPLICATE_RESOURCE    - Resource already exists
CONFLICT              - Resource state conflict
```

**Rate Limiting:**
```
RATE_LIMIT_EXCEEDED   - Too many requests
QUOTA_EXCEEDED        - Usage quota exceeded
```

**Server:**
```
INTERNAL_ERROR        - Unexpected server error
SERVICE_UNAVAILABLE   - Service temporarily down
BAD_GATEWAY           - Upstream service error
```

---

## Validation Errors

### Field-Level Errors

```json
POST /api/tasks
422 Unprocessable Entity
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "title": "Title is required and must be between 1-100 characters",
      "priority": "Priority must be one of: low, medium, high",
      "due_date": "Due date must be in the future"
    }
  }
}
```

### Multiple Errors

Return all validation errors at once:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Multiple validation errors",
    "details": {
      "title": "Title is required",
      "description": "Description exceeds maximum length of 500 characters",
      "due_date": "Due date must be in ISO 8601 format"
    }
  }
}
```

### Nested Field Errors

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "assignee.email": "Invalid email format",
      "subtasks[0].title": "Subtask title is required",
      "subtasks[2].due_date": "Due date must be in the future"
    }
  }
}
```

---

## Error Messages

### Writing Good Error Messages

**Bad:**
```
"Error"
"Invalid input"
"Something went wrong"
"Error 500"
```

**Good:**
```
"Title is required and must be between 1-100 characters"
"Email format is invalid. Expected: user@example.com"
"Due date must be in the future"
"Authentication token has expired. Please log in again."
```

### Guidelines

1. **Be specific**: Explain exactly what's wrong
2. **Be actionable**: Tell user how to fix it
3. **Be user-friendly**: Avoid technical jargon
4. **Be consistent**: Use same terminology across errors
5. **Don't expose internals**: Hide implementation details

### Examples by Category

**Authentication:**
```
✅ "Authentication required. Please provide a valid token."
❌ "401 Unauthorized"

✅ "Your session has expired. Please log in again."
❌ "Token validation failed"
```

**Validation:**
```
✅ "Title must be between 1-100 characters. Current length: 150"
❌ "Invalid title"

✅ "Email format is invalid. Expected format: user@example.com"
❌ "Bad email"
```

**Not Found:**
```
✅ "Task with ID '123' not found"
❌ "Not found"

✅ "The requested resource does not exist"
❌ "404"
```

**Permissions:**
```
✅ "You don't have permission to delete this task"
❌ "Forbidden"

✅ "Only task owners can mark tasks as complete"
❌ "Access denied"
```

---

## Best Practices

### 1. Use Appropriate Status Codes

```python
# Good
if not task:
    return JSONResponse(
        status_code=404,
        content={"error": {"code": "NOT_FOUND", "message": "Task not found"}}
    )

# Bad
if not task:
    return JSONResponse(
        status_code=200,
        content={"error": "Task not found"}
    )
```

### 2. Be Consistent

Use the same error format everywhere:

```python
# Define standard error response
class ErrorResponse(BaseModel):
    error: ErrorDetail

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None

# Use consistently
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Validation failed",
                details=exc.errors()
            )
        ).dict()
    )
```

### 3. Don't Leak Sensitive Information

```python
# Good
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred",
    "details": {
      "request_id": "abc-123"
    }
  }
}

# Bad (in production)
{
  "error": {
    "code": "DATABASE_ERROR",
    "message": "Connection to database 'prod_db' at 10.0.1.5:5432 failed",
    "details": {
      "stack_trace": "...",
      "sql_query": "SELECT * FROM users WHERE password = ..."
    }
  }
}
```

### 4. Log Errors Properly

```python
import logging

logger = logging.getLogger(__name__)

try:
    result = process_task(task_id)
except Exception as e:
    # Log full error details
    logger.error(
        f"Failed to process task {task_id}",
        exc_info=True,
        extra={"task_id": task_id, "user_id": user_id}
    )

    # Return sanitized error to client
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"request_id": request_id}
            }
        }
    )
```

### 5. Include Request ID

```python
import uuid

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        logger.error(f"Request {request_id} failed", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"request_id": request_id}
                }
            }
        )
```

### 6. Handle Validation Errors

```python
from pydantic import BaseModel, validator

class CreateTaskRequest(BaseModel):
    title: str
    due_date: Optional[datetime] = None

    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        if len(v) > 100:
            raise ValueError('Title must be less than 100 characters')
        return v

    @validator('due_date')
    def due_date_in_future(cls, v):
        if v and v < datetime.now():
            raise ValueError('Due date must be in the future')
        return v

@app.post("/api/tasks")
async def create_task(request: CreateTaskRequest):
    # Pydantic automatically validates and returns 422 with details
    pass
```

### 7. Provide Retry Information

```python
@app.get("/api/tasks")
async def list_tasks():
    if rate_limit_exceeded():
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "details": {
                        "retry_after": 60,  # seconds
                        "limit": 100,
                        "remaining": 0,
                        "reset_at": "2026-02-01T11:00:00Z"
                    }
                }
            },
            headers={"Retry-After": "60"}
        )
```

---

## Complete Example

```python
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

# Error response models
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None

class ErrorResponse(BaseModel):
    error: ErrorDetail

# Global exception handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message="Validation failed",
                details={err["loc"][-1]: err["msg"] for err in exc.errors()}
            )
        ).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=ErrorDetail(
                code=exc.detail.get("code", "HTTP_ERROR"),
                message=exc.detail.get("message", str(exc.detail))
            )
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"Unhandled exception in request {request_id}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred",
                details={"request_id": request_id}
            )
        ).dict()
    )

# Endpoint example
@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    task = get_task_from_db(task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "NOT_FOUND",
                "message": f"Task with ID '{task_id}' not found"
            }
        )

    if not user_has_access(task):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "You don't have permission to access this task"
            }
        )

    return task
```

---

## Summary

**Key Principles:**
1. Use appropriate HTTP status codes
2. Consistent error response format
3. Machine-readable error codes
4. Human-readable error messages
5. Field-level validation details
6. Don't leak sensitive information
7. Log errors with context
8. Include request IDs for debugging
9. Provide actionable error messages
10. Handle all error types gracefully
