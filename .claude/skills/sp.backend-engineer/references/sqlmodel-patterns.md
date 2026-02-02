# SQLModel Patterns

Comprehensive patterns for defining database models with SQLModel.

## Table of Contents
- SQLModel Basics
- Table Models
- Relationships
- Indexes and Constraints
- Migrations
- Query Patterns

---

## SQLModel Basics

### What is SQLModel?

SQLModel combines SQLAlchemy and Pydantic:
- **SQLAlchemy**: Database ORM
- **Pydantic**: Data validation

**Benefits:**
- Single model definition for DB and API
- Type hints and validation
- Editor support and autocomplete
- Less boilerplate code

### Installation

```bash
pip install sqlmodel
pip install psycopg2-binary  # PostgreSQL driver
```

---

## Table Models

### Basic Table Model

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class Task(SQLModel, table=True):
    __tablename__ = "tasks"  # Optional, defaults to lowercase class name

    # Primary key
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Required fields
    title: str = Field(max_length=100, index=True)

    # Optional fields
    description: Optional[str] = Field(default=None, max_length=500)

    # Fields with defaults
    priority: str = Field(default="medium")
    completed: bool = Field(default=False, index=True)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Field Types

```python
from sqlmodel import Field, Column
from sqlalchemy import JSON, Text
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

class Example(SQLModel, table=True):
    # String types
    short_text: str = Field(max_length=100)
    long_text: str = Field(sa_column=Column(Text))

    # Numeric types
    integer: int
    float_num: float
    decimal_num: Decimal = Field(max_digits=10, decimal_places=2)

    # Boolean
    is_active: bool = Field(default=True)

    # Date/Time
    created_date: date
    created_datetime: datetime
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # UUID
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # JSON
    metadata: dict = Field(default_factory=dict, sa_column=Column(JSON))
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Enum (as string)
    status: str = Field(default="pending")  # pending, active, completed

    # Optional fields
    optional_field: Optional[str] = Field(default=None)
```

### Indexes

```python
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Single column index
    title: str = Field(max_length=100, index=True)

    # Composite index (in table args)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    completed: bool = Field(default=False, index=True)

    class Config:
        # Composite indexes
        indexes = [
            {"fields": ["user_id", "completed"]},
            {"fields": ["user_id", "created_at"]},
        ]
```

### Constraints

```python
from sqlmodel import Field

class Task(SQLModel, table=True):
    # Unique constraint
    slug: str = Field(unique=True, index=True)

    # Not null (default for non-Optional fields)
    title: str  # NOT NULL

    # Nullable
    description: Optional[str] = None  # NULL allowed

    # Check constraint (via SQLAlchemy)
    priority: str = Field(
        sa_column=Column(
            String,
            CheckConstraint("priority IN ('low', 'medium', 'high')")
        )
    )

    # Default value
    status: str = Field(default="pending")

    # Foreign key with cascade
    user_id: UUID = Field(
        foreign_key="users.id",
        ondelete="CASCADE"
    )
```

---

## Relationships

### One-to-Many

```python
from sqlmodel import Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)

    # Relationship
    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str

    # Foreign key
    user_id: UUID = Field(foreign_key="users.id", index=True)

    # Relationship
    user: Optional[User] = Relationship(back_populates="tasks")

# Usage
user = session.get(User, user_id)
tasks = user.tasks  # Lazy loaded

task = session.get(Task, task_id)
owner = task.user  # Lazy loaded
```

### Many-to-Many

```python
from sqlmodel import Relationship

# Link table
class TaskTag(SQLModel, table=True):
    __tablename__ = "task_tags"

    task_id: UUID = Field(foreign_key="tasks.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tags.id", primary_key=True)

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str

    # Many-to-many relationship
    tags: List["Tag"] = Relationship(
        back_populates="tasks",
        link_model=TaskTag
    )

class Tag(SQLModel, table=True):
    __tablename__ = "tags"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True)

    # Many-to-many relationship
    tasks: List[Task] = Relationship(
        back_populates="tags",
        link_model=TaskTag
    )

# Usage
task = session.get(Task, task_id)
tags = task.tags  # List of Tag objects

tag = session.get(Tag, tag_id)
tasks = tag.tasks  # List of Task objects
```

### Self-Referential

```python
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str

    # Parent task (optional)
    parent_id: Optional[UUID] = Field(default=None, foreign_key="tasks.id")

    # Relationships
    parent: Optional["Task"] = Relationship(
        back_populates="subtasks",
        sa_relationship_kwargs={"remote_side": "Task.id"}
    )
    subtasks: List["Task"] = Relationship(back_populates="parent")

# Usage
parent_task = session.get(Task, parent_id)
subtasks = parent_task.subtasks

subtask = session.get(Task, subtask_id)
parent = subtask.parent
```

---

## Query Patterns

### Basic Queries

```python
from sqlmodel import Session, select

# Get by primary key
task = session.get(Task, task_id)

# Get all
statement = select(Task)
tasks = session.exec(statement).all()

# Filter
statement = select(Task).where(Task.completed == False)
active_tasks = session.exec(statement).all()

# Multiple filters
statement = select(Task).where(
    Task.user_id == user_id,
    Task.completed == False
)
user_active_tasks = session.exec(statement).all()

# Order by
statement = select(Task).order_by(Task.created_at.desc())
recent_tasks = session.exec(statement).all()

# Limit and offset
statement = select(Task).offset(20).limit(10)
page_2_tasks = session.exec(statement).all()
```

### Advanced Queries

```python
from sqlmodel import or_, and_, func

# OR condition
statement = select(Task).where(
    or_(
        Task.priority == "high",
        Task.due_date < datetime.utcnow()
    )
)

# AND condition (explicit)
statement = select(Task).where(
    and_(
        Task.user_id == user_id,
        Task.completed == False
    )
)

# LIKE
statement = select(Task).where(Task.title.like("%documentation%"))

# IN
statement = select(Task).where(Task.priority.in_(["high", "medium"]))

# Count
statement = select(func.count(Task.id)).where(Task.user_id == user_id)
count = session.exec(statement).one()

# Aggregate
statement = select(
    Task.priority,
    func.count(Task.id)
).group_by(Task.priority)
results = session.exec(statement).all()
```

### Joins

```python
# Explicit join
statement = select(Task, User).join(User)
results = session.exec(statement).all()

for task, user in results:
    print(f"{task.title} by {user.email}")

# Join with filter
statement = select(Task).join(User).where(User.email == "user@example.com")
tasks = session.exec(statement).all()

# Left join
statement = select(Task).join(User, isouter=True)
```

---

## CRUD Operations

### Create

```python
# Single record
task = Task(
    title="New task",
    description="Task description",
    user_id=user_id
)
session.add(task)
session.commit()
session.refresh(task)  # Get generated ID and defaults

# Multiple records
tasks = [
    Task(title="Task 1", user_id=user_id),
    Task(title="Task 2", user_id=user_id),
]
session.add_all(tasks)
session.commit()
```

### Read

```python
# By ID
task = session.get(Task, task_id)

# First match
statement = select(Task).where(Task.title == "Specific task")
task = session.exec(statement).first()

# All matches
statement = select(Task).where(Task.user_id == user_id)
tasks = session.exec(statement).all()

# One (raises if not exactly one)
statement = select(Task).where(Task.id == task_id)
task = session.exec(statement).one()
```

### Update

```python
# Get and update
task = session.get(Task, task_id)
if task:
    task.title = "Updated title"
    task.completed = True
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)

# Bulk update
statement = (
    update(Task)
    .where(Task.user_id == user_id)
    .values(completed=True)
)
session.exec(statement)
session.commit()
```

### Delete

```python
# Get and delete
task = session.get(Task, task_id)
if task:
    session.delete(task)
    session.commit()

# Bulk delete
statement = delete(Task).where(Task.completed == True)
session.exec(statement)
session.commit()
```

---

## Best Practices

### 1. Use Type Hints

```python
from typing import Optional, List
from uuid import UUID

class Task(SQLModel, table=True):
    id: UUID  # Type hint
    title: str
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
```

### 2. Add Indexes

```python
class Task(SQLModel, table=True):
    user_id: UUID = Field(foreign_key="users.id", index=True)
    completed: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

### 3. Use Timestamps

```python
class Task(SQLModel, table=True):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def update(self):
        self.updated_at = datetime.utcnow()
```

### 4. Validate Data

```python
from pydantic import validator

class Task(SQLModel, table=True):
    priority: str = Field(default="medium")

    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError('Invalid priority')
        return v
```

### 5. Use Soft Deletes

```python
class Task(SQLModel, table=True):
    deleted_at: Optional[datetime] = Field(default=None)

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()

# Query only non-deleted
statement = select(Task).where(Task.deleted_at.is_(None))
```

### 6. Separate Read/Write Models

```python
# Table model (for database)
class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    user_id: UUID

# Read model (for API responses)
class TaskRead(SQLModel):
    id: UUID
    title: str
    user_id: UUID

# Create model (for API requests)
class TaskCreate(SQLModel):
    title: str
```

---

## Common Patterns

### Pagination

```python
def paginate(
    session: Session,
    model: type[SQLModel],
    page: int = 1,
    page_size: int = 20
):
    offset = (page - 1) * page_size
    statement = select(model).offset(offset).limit(page_size)
    items = session.exec(statement).all()

    count_statement = select(func.count(model.id))
    total = session.exec(count_statement).one()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
```

### Filtering

```python
def filter_tasks(
    session: Session,
    user_id: UUID,
    completed: Optional[bool] = None,
    priority: Optional[str] = None
):
    statement = select(Task).where(Task.user_id == user_id)

    if completed is not None:
        statement = statement.where(Task.completed == completed)

    if priority:
        statement = statement.where(Task.priority == priority)

    return session.exec(statement).all()
```

### Soft Delete

```python
class SoftDeleteMixin:
    deleted_at: Optional[datetime] = Field(default=None)

    def soft_delete(self):
        self.deleted_at = datetime.utcnow()

    @classmethod
    def active_only(cls, statement):
        return statement.where(cls.deleted_at.is_(None))

class Task(SQLModel, SoftDeleteMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str

# Usage
statement = Task.active_only(select(Task))
active_tasks = session.exec(statement).all()
```

---

## Summary

**Key Points:**
1. Use SQLModel for combined ORM and validation
2. Define table models with `table=True`
3. Use type hints for all fields
4. Add indexes for frequently queried fields
5. Use relationships for related data
6. Separate read/write models for API
7. Implement soft deletes when needed
8. Use timestamps for audit trails
9. Validate data with Pydantic validators
10. Follow consistent naming conventions
