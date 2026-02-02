"""
Task management tools for Gemini function calling.
These functions are executed when the AI agent calls task-related tools.
"""
from typing import Dict, Any, List, Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import Task
from datetime import datetime


async def execute_tool(
    tool_name: str,
    tool_args: Dict[str, Any],
    user_id: str,
    session: AsyncSession
) -> Dict[str, Any]:
    """
    Execute a tool function based on the tool name.

    Args:
        tool_name: Name of the tool to execute
        tool_args: Arguments for the tool
        user_id: Current user ID for data isolation
        session: Database session

    Returns:
        Dict with tool execution result
    """
    if tool_name == "create_task":
        return await create_task_tool(
            user_id=user_id,
            session=session,
            title=tool_args.get("title"),
            description=tool_args.get("description")
        )
    elif tool_name == "list_tasks":
        return await list_tasks_tool(
            user_id=user_id,
            session=session,
            status=tool_args.get("status", "all")
        )
    elif tool_name == "update_task":
        return await update_task_tool(
            user_id=user_id,
            session=session,
            task_id=tool_args.get("task_id"),
            title=tool_args.get("title"),
            description=tool_args.get("description"),
            completed=tool_args.get("completed")
        )
    elif tool_name == "delete_task":
        return await delete_task_tool(
            user_id=user_id,
            session=session,
            task_id=tool_args.get("task_id")
        )
    else:
        return {"error": f"Unknown tool: {tool_name}"}


async def create_task_tool(
    user_id: str,
    session: AsyncSession,
    title: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new task for the user.

    Args:
        user_id: User ID from JWT
        session: Database session
        title: Task title
        description: Optional task description

    Returns:
        Dict with created task data
    """
    try:
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            },
            "message": f"Task '{title}' created successfully with ID {task.id}"
        }
    except Exception as e:
        await session.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create task"
        }


async def list_tasks_tool(
    user_id: str,
    session: AsyncSession,
    status: str = "all"
) -> Dict[str, Any]:
    """
    List user's tasks, optionally filtered by status.

    Args:
        user_id: User ID from JWT
        session: Database session
        status: Filter by 'all', 'pending', or 'completed'

    Returns:
        Dict with list of tasks
    """
    try:
        # Build query with user isolation
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

        task_list = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            }
            for task in tasks
        ]

        return {
            "success": True,
            "tasks": task_list,
            "count": len(task_list),
            "message": f"Found {len(task_list)} {status} task(s)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to list tasks"
        }


async def update_task_tool(
    user_id: str,
    session: AsyncSession,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None
) -> Dict[str, Any]:
    """
    Update an existing task.

    Args:
        user_id: User ID from JWT
        session: Database session
        task_id: ID of task to update
        title: New title (optional)
        description: New description (optional)
        completed: New completion status (optional)

    Returns:
        Dict with updated task data
    """
    try:
        # Fetch task with user isolation
        query = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        result = await session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            return {
                "success": False,
                "error": "Task not found or access denied",
                "message": f"Task with ID {task_id} not found"
            }

        # Update fields if provided
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if completed is not None:
            task.completed = completed

        task.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(task)

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            },
            "message": f"Task {task_id} updated successfully"
        }
    except Exception as e:
        await session.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to update task"
        }


async def delete_task_tool(
    user_id: str,
    session: AsyncSession,
    task_id: int
) -> Dict[str, Any]:
    """
    Delete a task permanently.

    Args:
        user_id: User ID from JWT
        session: Database session
        task_id: ID of task to delete

    Returns:
        Dict with deletion result
    """
    try:
        # Fetch task with user isolation
        query = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        result = await session.execute(query)
        task = result.scalar_one_or_none()

        if not task:
            return {
                "success": False,
                "error": "Task not found or access denied",
                "message": f"Task with ID {task_id} not found"
            }

        task_title = task.title
        await session.delete(task)
        await session.commit()

        return {
            "success": True,
            "message": f"Task '{task_title}' (ID {task_id}) deleted successfully"
        }
    except Exception as e:
        await session.rollback()
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to delete task"
        }
