"""
Recurring Task Service - Phase V Microservice

Generates next task instances for recurring tasks when they are completed.
Consumes recurring events from Kafka via Dapr Pub/Sub.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import logging
import os
import httpx
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Recurring Task Service", version="1.0.0")


# ============================================================================
# Date Calculation Logic
# ============================================================================

def calculate_next_occurrence(
    current_date: datetime,
    frequency: str,
    interval: int,
    days_of_week: Optional[str] = None,
    day_of_month: Optional[int] = None,
    month_of_year: Optional[int] = None
) -> datetime:
    """
    Calculate the next occurrence date for a recurring task.

    Args:
        current_date: Current date/time
        frequency: daily, weekly, monthly, yearly
        interval: Every N days/weeks/months/years
        days_of_week: JSON array of weekdays [0-6] for weekly recurrence
        day_of_month: Day of month (1-31) for monthly recurrence
        month_of_year: Month (1-12) for yearly recurrence

    Returns:
        Next occurrence datetime
    """
    if frequency == "daily":
        return current_date + timedelta(days=interval)

    elif frequency == "weekly":
        # Add interval weeks
        next_date = current_date + timedelta(weeks=interval)

        # If specific days of week are specified, find the next matching day
        if days_of_week:
            try:
                target_days = json.loads(days_of_week)
                current_weekday = next_date.weekday()

                # Find next matching weekday
                for i in range(7):
                    check_date = next_date + timedelta(days=i)
                    # Convert Monday=0 to Sunday=0 format
                    check_weekday = (check_date.weekday() + 1) % 7
                    if check_weekday in target_days:
                        return check_date
            except:
                pass

        return next_date

    elif frequency == "monthly":
        # Add interval months
        month = current_date.month + interval
        year = current_date.year

        while month > 12:
            month -= 12
            year += 1

        # Use specified day of month or current day
        day = day_of_month if day_of_month else current_date.day

        # Handle invalid days (e.g., Feb 31)
        while True:
            try:
                return datetime(year, month, day, current_date.hour, current_date.minute)
            except ValueError:
                day -= 1
                if day < 1:
                    day = 1
                    break

    elif frequency == "yearly":
        # Add interval years
        year = current_date.year + interval
        month = month_of_year if month_of_year else current_date.month
        day = day_of_month if day_of_month else current_date.day

        # Handle leap year edge cases
        try:
            return datetime(year, month, day, current_date.hour, current_date.minute)
        except ValueError:
            # If invalid (e.g., Feb 29 on non-leap year), use Feb 28
            return datetime(year, month, 28, current_date.hour, current_date.minute)

    return current_date + timedelta(days=1)  # Fallback


# ============================================================================
# Task Creation via Backend API
# ============================================================================

async def create_task_instance(
    parent_task_id: int,
    user_id: str,
    title: str,
    description: Optional[str],
    priority: str,
    due_date: Optional[datetime],
    tags: list,
    next_occurrence: datetime
) -> bool:
    """
    Create a new task instance via the backend API.

    Args:
        parent_task_id: ID of the parent recurring task
        user_id: User ID
        title: Task title
        description: Task description
        priority: Task priority
        due_date: Original due date
        tags: Task tags
        next_occurrence: Date for this instance

    Returns:
        True if task created successfully, False otherwise
    """
    backend_url = os.getenv("BACKEND_URL", "http://backend:8000")

    # Calculate new due date based on next occurrence
    new_due_date = None
    if due_date:
        time_diff = due_date - datetime.utcnow()
        new_due_date = next_occurrence + time_diff

    task_data = {
        "title": title,
        "description": description,
        "priority": priority,
        "due_date": new_due_date.isoformat() if new_due_date else None,
        "tags": tags,
        "is_recurring": False,
        "parent_task_id": parent_task_id,
        "recurrence_instance_date": next_occurrence.isoformat()
    }

    try:
        async with httpx.AsyncClient() as client:
            # Note: In production, we'd need to generate a service token
            # For now, we'll call an internal endpoint that doesn't require auth
            response = await client.post(
                f"{backend_url}/api/internal/tasks",
                json=task_data,
                headers={"X-User-ID": user_id},
                timeout=10.0
            )

            if response.status_code == 201:
                logger.info(f"Created recurring task instance for parent {parent_task_id}")
                return True
            else:
                logger.error(f"Failed to create task instance: {response.status_code} - {response.text}")
                return False

    except Exception as e:
        logger.error(f"Error creating task instance: {e}")
        return False


# ============================================================================
# Dapr Subscription Endpoint
# ============================================================================

class RecurringEvent(BaseModel):
    """Recurring event schema from Kafka."""
    event_type: str
    parent_task_id: int
    user_id: str
    recurring_pattern: dict
    next_occurrence_date: str
    timestamp: str


@app.post("/recurring-events")
async def handle_recurring_event(event: dict):
    """
    Handle recurring task events from Kafka via Dapr.

    This endpoint is called by Dapr when a message arrives on the recurring-events topic.
    """
    try:
        # Extract event data
        data = event.get("data", {})

        parent_task_id = data.get("parent_task_id")
        user_id = data.get("user_id")
        pattern = data.get("recurring_pattern", {})
        task_data = data.get("task_data", {})

        logger.info(f"Processing recurring event for task {parent_task_id}")

        # Calculate next occurrence
        frequency = pattern.get("frequency")
        interval = pattern.get("interval", 1)
        days_of_week = pattern.get("days_of_week")
        day_of_month = pattern.get("day_of_month")
        month_of_year = pattern.get("month_of_year")

        current_date = datetime.utcnow()
        next_occurrence = calculate_next_occurrence(
            current_date=current_date,
            frequency=frequency,
            interval=interval,
            days_of_week=days_of_week,
            day_of_month=day_of_month,
            month_of_year=month_of_year
        )

        logger.info(f"Next occurrence calculated: {next_occurrence.isoformat()}")

        # Create new task instance
        title = task_data.get("title", "Recurring Task")
        description = task_data.get("description")
        priority = task_data.get("priority", "medium")
        due_date_str = task_data.get("due_date")
        due_date = datetime.fromisoformat(due_date_str) if due_date_str else None
        tags = task_data.get("tags", [])

        success = await create_task_instance(
            parent_task_id=parent_task_id,
            user_id=user_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tags,
            next_occurrence=next_occurrence
        )

        return {
            "status": "processed" if success else "failed",
            "parent_task_id": parent_task_id,
            "next_occurrence": next_occurrence.isoformat()
        }

    except Exception as e:
        logger.error(f"Error processing recurring event: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================================
# Dapr Subscription Configuration
# ============================================================================

@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Tells Dapr which topics this service subscribes to.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "recurring-events",
            "route": "/recurring-events"
        }
    ]


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "recurring-service",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Recurring Task Service",
        "version": "1.0.0",
        "description": "Generates next task instances for recurring tasks"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
