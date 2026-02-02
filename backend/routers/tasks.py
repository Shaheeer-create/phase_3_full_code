"""
Task CRUD endpoints with user isolation.

CRITICAL SECURITY: All endpoints filter by user_id from JWT.
Users can only access their own tasks.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Optional
from datetime import datetime

from database import get_session
from dependencies import get_current_user_id
from models import Task


router = APIRouter(prefix="/api/tasks", tags=["tasks"])


# Pydantic models for request/response
from pydantic import BaseModel


class TaskCreate(BaseModel):
    """Request model for creating a task."""
    title: str
    description: Optional[str] = None


class TaskUpdate(BaseModel):
    """Request model for updating a task."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskResponse(BaseModel):
    """Response model for task data."""
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    status: str = Query("all", regex="^(all|pending|completed)$"),
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    List all tasks for the authenticated user.

    SECURITY: Filters by user_id from JWT - users only see their own tasks.

    Args:
        status: Filter by completion status (all, pending, completed)
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

    # Order by creation date (newest first)
    query = query.order_by(Task.created_at.desc())

    result = await session.execute(query)
    tasks = result.scalars().all()

    return tasks


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new task for the authenticated user.

    SECURITY: Automatically assigns user_id from JWT.

    Args:
        task_data: Task creation data
        session: Database session
        user_id: Authenticated user ID from JWT

    Returns:
        Created task
    """
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        completed=False
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


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

    return task


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

    # Update fields if provided
    if task_data.title is not None:
        task.title = task_data.title
    if task_data.description is not None:
        task.description = task_data.description
    if task_data.completed is not None:
        task.completed = task_data.completed

    # Update timestamp
    task.updated_at = datetime.utcnow()

    session.add(task)
    await session.commit()
    await session.refresh(task)

    return task


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

    return task


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

    await session.delete(task)
    await session.commit()

    return None
