# Pydantic Validation Patterns

Comprehensive patterns for request validation with Pydantic in FastAPI.

## Table of Contents
- Pydantic Basics
- Field Validation
- Model Validators
- Custom Validators
- Nested Models
- Error Handling

---

## Pydantic Basics

### Basic Model

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None
    tags: list[str] = []
```

### Field Constraints

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    # String constraints
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    # Numeric constraints
    priority_score: int = Field(ge=1, le=10)  # 1 <= x <= 10
    estimated_hours: float = Field(gt=0, le=100)  # 0 < x <= 100

    # List constraints
    tags: list[str] = Field(default_factory=list, max_items=10)

    # Pattern matching
    slug: str = Field(pattern=r'^[a-z0-9-]+$')
```

---

## Field Validation

### Required vs Optional

```python
class TaskCreate(BaseModel):
    # Required (no default)
    title: str

    # Optional with None default
    description: Optional[str] = None

    # Optional with value default
    priority: str = "medium"

    # Optional with factory default
    tags: list[str] = Field(default_factory=list)
```

### Enum Validation

```python
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskCreate(BaseModel):
    priority: Priority = Priority.MEDIUM

# Usage
task = TaskCreate(title="Task", priority="high")  # Validates
task = TaskCreate(title="Task", priority="invalid")  # ValidationError
```

### Date/Time Validation

```python
from datetime import datetime, date
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    due_date: Optional[datetime] = None
    start_date: Optional[date] = None

    @validator('due_date')
    def due_date_must_be_future(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Due date must be in the future')
        return v

    @validator('start_date')
    def start_date_not_too_far(cls, v):
        if v and (v - date.today()).days > 365:
            raise ValueError('Start date cannot be more than 1 year in future')
        return v
```

### Email Validation

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr  # Validates email format
    name: str
```

### URL Validation

```python
from pydantic import BaseModel, HttpUrl

class TaskCreate(BaseModel):
    title: str
    reference_url: Optional[HttpUrl] = None  # Validates URL format
```

---

## Model Validators

### Field Validator

```python
from pydantic import BaseModel, validator

class TaskCreate(BaseModel):
    title: str
    priority: str

    @validator('priority')
    def validate_priority(cls, v):
        allowed = ['low', 'medium', 'high']
        if v not in allowed:
            raise ValueError(f'Priority must be one of: {", ".join(allowed)}')
        return v

    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

### Multiple Field Validator

```python
from pydantic import BaseModel, validator

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

    @validator('title', 'description')
    def strip_whitespace(cls, v):
        if v:
            return v.strip()
        return v
```

### Root Validator

```python
from pydantic import BaseModel, root_validator
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    @root_validator
    def check_dates(cls, values):
        start = values.get('start_date')
        due = values.get('due_date')

        if start and due and start > due:
            raise ValueError('Start date must be before due date')

        return values
```

### Pre and Post Validators

```python
from pydantic import BaseModel, validator

class TaskCreate(BaseModel):
    title: str
    tags: list[str] = []

    @validator('title', pre=True)
    def convert_title_to_string(cls, v):
        # Runs before type validation
        if isinstance(v, int):
            return str(v)
        return v

    @validator('tags', pre=False)
    def normalize_tags(cls, v):
        # Runs after type validation
        return [tag.lower().strip() for tag in v]
```

---

## Custom Validators

### Reusable Validators

```python
from pydantic import BaseModel, validator

def validate_not_empty(v: str) -> str:
    if not v or not v.strip():
        raise ValueError('Field cannot be empty')
    return v.strip()

def validate_max_length(max_len: int):
    def validator_func(v: str) -> str:
        if len(v) > max_len:
            raise ValueError(f'Field must be at most {max_len} characters')
        return v
    return validator_func

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

    _validate_title = validator('title', allow_reuse=True)(validate_not_empty)
    _validate_desc = validator('description', allow_reuse=True)(validate_max_length(500))
```

### Custom Field Types

```python
from pydantic import BaseModel
from typing import Any

class Priority:
    def __init__(self, value: str):
        allowed = ['low', 'medium', 'high']
        if value not in allowed:
            raise ValueError(f'Priority must be one of: {", ".join(allowed)}')
        self.value = value

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, cls):
            return v
        return cls(v)

    def __repr__(self):
        return f'Priority({self.value})'

class TaskCreate(BaseModel):
    title: str
    priority: Priority

    class Config:
        arbitrary_types_allowed = True
```

---

## Nested Models

### Basic Nesting

```python
from pydantic import BaseModel
from typing import Optional

class Address(BaseModel):
    street: str
    city: str
    country: str
    postal_code: str

class User(BaseModel):
    name: str
    email: str
    address: Optional[Address] = None

# Usage
user = User(
    name="John",
    email="john@example.com",
    address={
        "street": "123 Main St",
        "city": "New York",
        "country": "USA",
        "postal_code": "10001"
    }
)
```

### List of Models

```python
class Subtask(BaseModel):
    title: str
    completed: bool = False

class TaskCreate(BaseModel):
    title: str
    subtasks: list[Subtask] = []

# Usage
task = TaskCreate(
    title="Main task",
    subtasks=[
        {"title": "Subtask 1"},
        {"title": "Subtask 2", "completed": True}
    ]
)
```

### Recursive Models

```python
from __future__ import annotations
from pydantic import BaseModel
from typing import Optional

class Task(BaseModel):
    title: str
    parent: Optional[Task] = None
    subtasks: list[Task] = []

Task.update_forward_refs()
```

---

## Error Handling

### Validation Errors

```python
from pydantic import BaseModel, ValidationError

class TaskCreate(BaseModel):
    title: str
    priority: str

try:
    task = TaskCreate(title="", priority="invalid")
except ValidationError as e:
    print(e.json())
    # {
    #   "title": ["ensure this value has at least 1 characters"],
    #   "priority": ["value is not a valid enumeration member"]
    # }
```

### Custom Error Messages

```python
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    priority: str

    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError('Priority must be low, medium, or high')
        return v

    class Config:
        # Custom error messages
        error_msg_templates = {
            'value_error.missing': 'This field is required',
            'value_error.str.min_length': 'Must be at least {limit_value} characters',
        }
```

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    errors = {}
    for error in exc.errors():
        field = '.'.join(str(loc) for loc in error['loc'][1:])
        errors[field] = error['msg']

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
```

---

## Advanced Patterns

### Conditional Validation

```python
from pydantic import BaseModel, root_validator

class TaskCreate(BaseModel):
    title: str
    has_deadline: bool = False
    due_date: Optional[datetime] = None

    @root_validator
    def check_deadline(cls, values):
        has_deadline = values.get('has_deadline')
        due_date = values.get('due_date')

        if has_deadline and not due_date:
            raise ValueError('Due date is required when has_deadline is true')

        if not has_deadline and due_date:
            raise ValueError('Due date should not be set when has_deadline is false')

        return values
```

### Dynamic Defaults

```python
from pydantic import BaseModel, Field
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    tags: list[str] = Field(default_factory=list)
```

### Alias Fields

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str
    priority_level: str = Field(alias='priority')

    class Config:
        allow_population_by_field_name = True

# Usage
task = TaskCreate(title="Task", priority="high")  # Works
task = TaskCreate(title="Task", priority_level="high")  # Also works
```

### Exclude Fields

```python
from pydantic import BaseModel

class Task(BaseModel):
    id: str
    title: str
    password: str

    class Config:
        fields = {
            'password': {'exclude': True}  # Never include in output
        }

# Or dynamically
task_dict = task.dict(exclude={'password'})
task_json = task.json(exclude={'password'})
```

---

## Best Practices

### 1. Use Type Hints

```python
from typing import Optional, List
from datetime import datetime

class TaskCreate(BaseModel):
    title: str
    tags: List[str]
    due_date: Optional[datetime]
```

### 2. Provide Defaults

```python
class TaskCreate(BaseModel):
    title: str
    priority: str = "medium"
    completed: bool = False
    tags: list[str] = Field(default_factory=list)
```

### 3. Add Descriptions

```python
class TaskCreate(BaseModel):
    title: str = Field(..., description="Task title (1-100 characters)")
    priority: str = Field(
        default="medium",
        description="Task priority: low, medium, or high"
    )
```

### 4. Use Validators

```python
class TaskCreate(BaseModel):
    title: str

    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
```

### 5. Separate Models

```python
# Create model (for POST requests)
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None

# Update model (for PATCH requests)
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# Response model (for API responses)
class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True
```

---

## Summary

**Key Points:**
1. Use Pydantic for request validation
2. Define clear field constraints
3. Use validators for complex validation
4. Provide helpful error messages
5. Separate create/update/response models
6. Use type hints everywhere
7. Provide sensible defaults
8. Document fields with descriptions
9. Handle validation errors gracefully
10. Test validation thoroughly
