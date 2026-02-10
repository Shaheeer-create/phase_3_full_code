"""
Task CRUD endpoints with user isolation.

CRITICAL SECURITY: All endpoints filter by user_id from JWT.
Users can only access their own tasks.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, or_, and_
from typing import Optional, List
from datetime import datetime

from database import get_session
from dependencies import get_current_user_id
from models import Task, TaskTag, TaskReminder, RecurringPattern
from services.event_publisher import event_publisher


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


# Pydantic models for request/response
from pydantic import BaseModel


class TaskCreate(BaseModel):
    """Request model for creating a task."""
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"  # low, medium, high
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    is_recurring: Optional[bool] = False


class TaskUpdate(BaseModel):
    """Request model for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    """Response model for task data."""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    due_date: Optional[datetime]
    is_recurring: bool
    parent_task_id: Optional[int]
    recurrence_instance_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[str]] = None

    class Config:
        from_attributes = True


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    status: str = Query("all", regex="^(all|pending|completed)$"),
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    List all tasks for the authenticated user.

    SECURITY: Filters by user_id from JWT - users only see their own tasks.

    Args:
        status: Filter by completion status (all, pending, completed)
        priority: Filter by priority (low, medium, high)
        session: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        List of tasks owned by the user
    """
    # Base query: ALWAYS filter by user_id
    query = select(Task).where(Task.user_id == user_id)

    # Apply status filter
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    # Apply priority filter
    if priority:
        query = query.where(Task.priority == priority)

    # Order by creation date (newest first)
    query = query.order_by(Task.created_at.desc())

    result = await session.execute(query)
    tasks = result.scalars().all()

    # Fetch tags for each task
    tasks_with_tags = []
    for task in tasks:
        task_dict = task.dict()

        # Get tags
        tags_result = await session.execute(
            select(TaskTag).where(TaskTag.task_id == task.id)
        )
        tags = [tag.tag_name for tag in tags_result.scalars().all()]
        task_dict['tags'] = tags

        tasks_with_tags.append(TaskResponse(**task_dict))

    return tasks_with_tags


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    request: Request,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new task for the authenticated user.

    SECURITY: Automatically assigns user_id from JWT.

    Args:
        task_data: Task creation data
        request: FastAPI request object (for IP/user-agent)
        session: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        Created task
    """
    # Validate priority
    if task_data.priority not in ["low", "medium", "high"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Priority must be one of: low, medium, high"
        )

    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False,
        priority=task_data.priority,
        due_date=task_data.due_date,
        is_recurring=task_data.is_recurring or False
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Add tags if provided
    tags = []
    if task_data.tags:
        for tag_name in task_data.tags:
            tag = TaskTag(task_id=task.id, tag_name=tag_name.strip().lower())
            session.add(tag)
            tags.append(tag_name.strip().lower())
        await session.commit()

    # Publish event to Kafka
    await event_publisher.publish_task_event(
        event_type="task.created",
        task_id=task.id,
        user_id=user_id,
        task_data={
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "is_recurring": task.is_recurring,
            "completed": task.completed,
            "tags": tags
        }
    )

    # Prepare response
    task_dict = task.dict()
    task_dict['tags'] = tags

    return TaskResponse(**task_dict)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get a specific task by ID.

    SECURITY: Verifies task ownership - returns 404 if not found OR not owned.

    Args:
        task_id: Task ID
        session: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        Task details

    Raises:
        404: Task not found or not owned by user
    """
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Get tags
    tags_result = await session.execute(
        select(TaskTag).where(TaskTag.task_id == task.id)
    )
    tags = [tag.tag_name for tag in tags_result.scalars().all()]

    task_dict = task.dict()
    task_dict['tags'] = tags

    return TaskResponse(**task_dict)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update a task.

    SECURITY: Verifies task ownership before update.

    Args:
        task_id: Task ID
        task_data: Updated task data
        session: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        Updated task

    Raises:
        404: Task not found or not owned by user
    """
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Store old values for audit
    old_values = {
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "priority": task.priority,
        "due_date": task.due_date.isoformat() if task.due_date else None
    }

    # Update fields if provided
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed
    if task_data.priority is not None:
        if task_data.priority not in ["low", "medium", "high"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Priority must be one of: low, medium, high"
            )
        task.priority = task_data.priority
    if task_data.due_date is not None:
        task.due_date = task_data.due_date

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Get tags
    tags_result = await session.execute(
        select(TaskTag).where(TaskTag.task_id == task.id)
    )
    tags = [tag.tag_name for tag in tags_result.scalars().all()]

    # Publish event to Kafka
    await event_publisher.publish_task_event(
        event_type="task.updated",
        task_id=task.id,
        user_id=user_id,
        task_data={
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "is_recurring": task.is_recurring,
            "completed": task.completed,
            "tags": tags,
            "old_values": old_values
        }
    )

    task_dict = task.dict()
    task_dict['tags'] = tags

    return TaskResponse(**task_dict)


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Toggle task completion status.

    SECURITY: Verifies task ownership before update.

    Args:
        task_id: Task ID
        session: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        Updated task

    Raises:
        404: Task not found or not owned by user
    """
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle completion
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    # Get tags
    tags_result = await session.execute(
        select(TaskTag).where(TaskTag.task_id == task.id)
    )
    tags = [tag.tag_name for tag in tags_result.scalars().all()]

    # Publish event to Kafka
    event_type = "task.completed" if task.completed else "task.uncompleted"
    await event_publisher.publish_task_event(
        event_type=event_type,
        task_id=task.id,
        user_id=user_id,
        task_data={
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "is_recurring": task.is_recurring,
            "completed": task.completed,
            "tags": tags
        }
    )

    # If task is recurring and completed, publish recurring event
    if task.completed and task.is_recurring:
        # Get recurring pattern
        pattern_result = await session.execute(
            select(RecurringPattern).where(
                RecurringPattern.task_id == task.id,
                RecurringPattern.is_active == True
            )
        )
        pattern = pattern_result.scalar_one_or_none()

        if pattern:
            await event_publisher.publish_recurring_event(
                parent_task_id=task.id,
                user_id=user_id,
                recurring_pattern={
                    "frequency": pattern.frequency,
                    "interval": pattern.interval,
                    "days_of_week": pattern.days_of_week,
                    "day_of_month": pattern.day_of_month,
                    "month_of_year": pattern.month_of_year
                },
                next_occurrence_date=datetime.utcnow().isoformat()
            )

    task_dict = task.dict()
    task_dict['tags'] = tags

    return TaskResponse(**task_dict)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Delete a task.

    SECURITY: Verifies task ownership before deletion.

    Args:
        task_id: Task ID
        session: Database session
        user_id: Authenticated user ID from JWT

    Raises:
        404: Task not found or not owned by user
    """
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Get tags before deletion
    tags_result = await session.execute(
        select(TaskTag).where(TaskTag.task_id == task.id)
    )
    tags = [tag.tag_name for tag in tags_result.scalars().all()]

    # Publish event to Kafka before deletion
    await event_publisher.publish_task_event(
        event_type="task.deleted",
        task_id=task.id,
        user_id=user_id,
        task_data={
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "is_recurring": task.is_recurring,
            "completed": task.completed,
            "tags": tags
        }
    )

    await session.delete(task)
    await session.commit()

    return None


# ============================================================================
# Phase V: Advanced Features Endpoints
# ============================================================================


@router.get("/search", response_model=list[TaskResponse])
async def search_tasks(
    q: Optional[str] = Query(None, description="Search query"),
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    due_before: Optional[datetime] = Query(None),
    due_after: Optional[datetime] = Query(None),
    status: str = Query("all", regex="^(all|pending|completed)$"),
    sort_by: str = Query("created_at", regex="^(created_at|due_date|priority)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Advanced search for tasks with multiple filters.

    SECURITY: Filters by user_id from JWT.

    Args:
        q: Search query (searches title and description)
        priority: Filter by priority
        tags: Comma-separated list of tags
        due_before: Filter tasks due before this date
        due_after: Filter tasks due after this date
        status: Filter by completion status
        sort_by: Sort field (created_at, due_date, priority)
        sort_order: Sort order (asc, desc)
        session: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        List of matching tasks
    """
    # Base query: ALWAYS filter by user_id
    query = select(Task).where(Task.user_id == user_id)

    # Apply text search
    if q:
        search_term = f"%{q}%"
        query = query.where(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term)
            )
        )

    # Apply priority filter
    if priority:
        query = query.where(Task.priority == priority)

    # Apply status filter
    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    # Apply due date filters
    if due_before:
        query = query.where(Task.due_date <= due_before)
    if due_after:
        query = query.where(Task.due_date >= due_after)

    # Apply sorting
    if sort_by == "created_at":
        sort_column = Task.created_at
    elif sort_by == "due_date":
        sort_column = Task.due_date
    elif sort_by == "priority":
        # Custom priority sorting: high > medium > low
        priority_order = {"high": 1, "medium": 2, "low": 3}
        sort_column = Task.priority
    else:
        sort_column = Task.created_at

    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    result = await session.execute(query)
    tasks = result.scalars().all()

    # Filter by tags if provided
    if tags:
        tag_list = [tag.strip().lower() for tag in tags.split(",")]
        filtered_tasks = []

        for task in tasks:
            tags_result = await session.execute(
                select(TaskTag).where(TaskTag.task_id == task.id)
            )
            task_tags = [tag.tag_name for tag in tags_result.scalars().all()]

            # Check if task has any of the requested tags
            if any(tag in task_tags for tag in tag_list):
                task_dict = task.dict()
                task_dict['tags'] = task_tags
                filtered_tasks.append(TaskResponse(**task_dict))

        return filtered_tasks

    # Get tags for all tasks
    tasks_with_tags = []
    for task in tasks:
        tags_result = await session.execute(
            select(TaskTag).where(TaskTag.task_id == task.id)
        )
        task_tags = [tag.tag_name for tag in tags_result.scalars().all()]

        task_dict = task.dict()
        task_dict['tags'] = task_tags
        tasks_with_tags.append(TaskResponse(**task_dict))

    return tasks_with_tags

# ============================================================================
# Additional Advanced Endpoints for Phase V
# These should be appended to tasks.py
# ============================================================================


class TagsRequest(BaseModel):
    """Request model for adding tags to a task."""
    tags: List[str]


@router.post("/{task_id}/tags", response_model=TaskResponse)
async def add_task_tags(
    task_id: int,
    tags_data: TagsRequest,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Add tags to a task.

    SECURITY: Verifies task ownership before adding tags.

    Args:
        task_id: Task ID
        tags_data: Tags to add
        session: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        Updated task with tags

    Raises:
        404: Task not found or not owned by user
    """
    # Verify task ownership
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Add new tags (avoid duplicates)
    existing_tags_result = await session.execute(
        select(TaskTag).where(TaskTag.task_id == task_id)
    )
    existing_tags = {tag.tag_name for tag in existing_tags_result.scalars().all()}

    new_tags = []
    for tag_name in tags_data.tags:
        tag_name_clean = tag_name.strip().lower()
        if tag_name_clean and tag_name_clean not in existing_tags:
            tag = TaskTag(task_id=task_id, tag_name=tag_name_clean)
            session.add(tag)
            new_tags.append(tag_name_clean)
            existing_tags.add(tag_name_clean)

    await session.commit()

    # Get all tags
    all_tags = list(existing_tags)

    task_dict = task.dict()
    task_dict['tags'] = all_tags

    return TaskResponse(**task_dict)


class ReminderRequest(BaseModel):
    """Request model for creating a reminder."""
    reminder_time: datetime
    reminder_type: str = "notification"  # notification, email, both


class ReminderResponse(BaseModel):
    """Response model for reminder data."""
    id: int
    task_id: int
    user_id: str
    reminder_time: datetime
    reminder_type: str
    is_sent: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/{task_id}/reminders", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED)
async def create_reminder(
    task_id: int,
    reminder_data: ReminderRequest,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a reminder for a task.

    SECURITY: Verifies task ownership before creating reminder.

    Args:
        task_id: Task ID
        reminder_data: Reminder configuration
        session: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        Created reminder

    Raises:
        404: Task not found or not owned by user
        422: Invalid reminder type or time in the past
    """
    # Verify task ownership
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Validate reminder type
    if reminder_data.reminder_type not in ["notification", "email", "both"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Reminder type must be one of: notification, email, both"
        )

    # Validate reminder time is in the future
    if reminder_data.reminder_time <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Reminder time must be in the future"
        )

    # Create reminder
    reminder = TaskReminder(
        task_id=task_id,
        user_id=user_id,
        reminder_time=reminder_data.reminder_time,
        reminder_type=reminder_data.reminder_type,
        is_sent=False
    )

    session.add(reminder)
    await session.commit()
    await session.refresh(reminder)

    return reminder


class RecurringPatternRequest(BaseModel):
    """Request model for creating a recurring pattern."""
    frequency: str  # daily, weekly, monthly, yearly
    interval: int = 1
    days_of_week: Optional[str] = None  # JSON array: [0,1,2,3,4,5,6]
    day_of_month: Optional[int] = None
    month_of_year: Optional[int] = None
    end_date: Optional[datetime] = None


class RecurringPatternResponse(BaseModel):
    """Response model for recurring pattern data."""
    id: int
    task_id: int
    frequency: str
    interval: int
    days_of_week: Optional[str]
    day_of_month: Optional[int]
    month_of_year: Optional[int]
    end_date: Optional[datetime]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/{task_id}/recurring", response_model=RecurringPatternResponse, status_code=status.HTTP_201_CREATED)
async def create_recurring_pattern(
    task_id: int,
    pattern_data: RecurringPatternRequest,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Set up a recurring pattern for a task.

    SECURITY: Verifies task ownership before creating pattern.

    Args:
        task_id: Task ID
        pattern_data: Recurring pattern configuration
        session: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        Created recurring pattern

    Raises:
        404: Task not found or not owned by user
        422: Invalid frequency or configuration
    """
    # Verify task ownership
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Validate frequency
    if pattern_data.frequency not in ["daily", "weekly", "monthly", "yearly"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Frequency must be one of: daily, weekly, monthly, yearly"
        )

    # Validate interval
    if pattern_data.interval < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Interval must be at least 1"
        )

    # Mark task as recurring
    task.is_recurring = True
    session.add(task)

    # Create recurring pattern
    pattern = RecurringPattern(
        task_id=task_id,
        frequency=pattern_data.frequency,
        interval=pattern_data.interval,
        days_of_week=pattern_data.days_of_week,
        day_of_month=pattern_data.day_of_month,
        month_of_year=pattern_data.month_of_year,
        end_date=pattern_data.end_date,
        is_active=True
    )

    session.add(pattern)
    await session.commit()
    await session.refresh(pattern)

    return pattern


@router.get("/{task_id}/instances", response_model=list[TaskResponse])
async def get_recurring_instances(
    task_id: int,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all instances of a recurring task (parent + children).

    SECURITY: Verifies task ownership.

    Args:
        task_id: Parent task ID
        session: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        List of task instances (parent + all generated instances)

    Raises:
        404: Task not found or not owned by user
    """
    # Verify task ownership
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    parent_task = result.scalar_one_or_none()

    if not parent_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Get all instances (parent + children)
    instances_result = await session.execute(
        select(Task).where(
            or_(
                Task.id == task_id,
                Task.parent_task_id == task_id
            ),
            Task.user_id == user_id
        ).order_by(Task.recurrence_instance_date.asc())
    )
    instances = instances_result.scalars().all()

    # Get tags for each instance
    instances_with_tags = []
    for instance in instances:
        tags_result = await session.execute(
            select(TaskTag).where(TaskTag.task_id == instance.id)
        )
        tags = [tag.tag_name for tag in tags_result.scalars().all()]

        instance_dict = instance.dict()
        instance_dict['tags'] = tags
        instances_with_tags.append(TaskResponse(**instance_dict))

    return instances_with_tags
