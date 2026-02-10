"""
Audit Service - Phase V Microservice

Logs all task operations to the audit_log table for compliance and tracking.
Consumes all task events from Kafka via Dapr Pub/Sub.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import logging
import os
import asyncpg
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Audit Service", version="1.0.0")

# Database connection pool
db_pool = None


# ============================================================================
# Database Connection
# ============================================================================

async def get_db_pool():
    """Get or create database connection pool."""
    global db_pool
    if db_pool is None:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL not configured")
            return None

        try:
            db_pool = await asyncpg.create_pool(
                database_url,
                min_size=2,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            return None

    return db_pool


async def log_audit_entry(
    user_id: str,
    entity_type: str,
    entity_id: int,
    action: str,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> bool:
    """
    Log an audit entry to the database.

    Args:
        user_id: User ID who performed the action
        entity_type: Type of entity (task, conversation, etc.)
        entity_id: ID of the entity
        action: Action performed (create, update, delete, complete, uncomplete)
        old_values: Previous values (for updates)
        new_values: New values
        ip_address: IP address of the request
        user_agent: User agent string

    Returns:
        True if logged successfully, False otherwise
    """
    pool = await get_db_pool()
    if not pool:
        return False

    try:
        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO audit_log (
                    user_id, entity_type, entity_id, action,
                    old_values, new_values, ip_address, user_agent, created_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                user_id,
                entity_type,
                entity_id,
                action,
                json.dumps(old_values) if old_values else None,
                json.dumps(new_values) if new_values else None,
                ip_address,
                user_agent,
                datetime.utcnow()
            )

        logger.info(f"Audit log created: {action} on {entity_type} {entity_id} by {user_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to log audit entry: {e}")
        return False


# ============================================================================
# Dapr Subscription Endpoint
# ============================================================================

class TaskEvent(BaseModel):
    """Task event schema from Kafka."""
    event_type: str
    task_id: int
    user_id: str
    task_data: dict
    timestamp: str


@app.post("/task-events")
async def handle_task_event(event: dict):
    """
    Handle task events from Kafka via Dapr.

    This endpoint is called by Dapr when a message arrives on the task-events topic.
    Logs all task operations to the audit_log table.
    """
    try:
        # Extract event data
        data = event.get("data", {})

        event_type = data.get("event_type")
        task_id = data.get("task_id")
        user_id = data.get("user_id")
        task_data = data.get("task_data", {})

        logger.info(f"Processing task event: {event_type} for task {task_id}")

        # Map event type to action
        action_map = {
            "task.created": "create",
            "task.updated": "update",
            "task.deleted": "delete",
            "task.completed": "complete",
            "task.uncompleted": "uncomplete"
        }

        action = action_map.get(event_type, "unknown")

        # Extract old and new values
        old_values = task_data.get("old_values")
        new_values = {
            "title": task_data.get("title"),
            "description": task_data.get("description"),
            "priority": task_data.get("priority"),
            "due_date": task_data.get("due_date"),
            "completed": task_data.get("completed"),
            "tags": task_data.get("tags")
        }

        # Log to audit table
        success = await log_audit_entry(
            user_id=user_id,
            entity_type="task",
            entity_id=task_id,
            action=action,
            old_values=old_values,
            new_values=new_values,
            ip_address=None,  # Not available from Kafka events
            user_agent=None
        )

        return {
            "status": "processed" if success else "failed",
            "event_type": event_type,
            "task_id": task_id
        }

    except Exception as e:
        logger.error(f"Error processing task event: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================================
# Audit Query Endpoints
# ============================================================================

@app.get("/audit/{entity_type}/{entity_id}")
async def get_audit_trail(entity_type: str, entity_id: int, limit: int = 50):
    """
    Get audit trail for a specific entity.

    Args:
        entity_type: Type of entity (task, conversation, etc.)
        entity_id: ID of the entity
        limit: Maximum number of entries to return

    Returns:
        List of audit log entries
    """
    pool = await get_db_pool()
    if not pool:
        return {"error": "Database not available"}

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, user_id, entity_type, entity_id, action,
                       old_values, new_values, ip_address, user_agent, created_at
                FROM audit_log
                WHERE entity_type = $1 AND entity_id = $2
                ORDER BY created_at DESC
                LIMIT $3
                """,
                entity_type,
                entity_id,
                limit
            )

        audit_entries = []
        for row in rows:
            audit_entries.append({
                "id": row["id"],
                "user_id": row["user_id"],
                "entity_type": row["entity_type"],
                "entity_id": row["entity_id"],
                "action": row["action"],
                "old_values": json.loads(row["old_values"]) if row["old_values"] else None,
                "new_values": json.loads(row["new_values"]) if row["new_values"] else None,
                "ip_address": row["ip_address"],
                "user_agent": row["user_agent"],
                "created_at": row["created_at"].isoformat()
            })

        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "count": len(audit_entries),
            "entries": audit_entries
        }

    except Exception as e:
        logger.error(f"Error fetching audit trail: {e}")
        return {"error": str(e)}


@app.get("/audit/user/{user_id}")
async def get_user_audit_trail(user_id: str, limit: int = 100):
    """
    Get audit trail for a specific user.

    Args:
        user_id: User ID
        limit: Maximum number of entries to return

    Returns:
        List of audit log entries for the user
    """
    pool = await get_db_pool()
    if not pool:
        return {"error": "Database not available"}

    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, user_id, entity_type, entity_id, action,
                       old_values, new_values, ip_address, user_agent, created_at
                FROM audit_log
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2
                """,
                user_id,
                limit
            )

        audit_entries = []
        for row in rows:
            audit_entries.append({
                "id": row["id"],
                "user_id": row["user_id"],
                "entity_type": row["entity_type"],
                "entity_id": row["entity_id"],
                "action": row["action"],
                "old_values": json.loads(row["old_values"]) if row["old_values"] else None,
                "new_values": json.loads(row["new_values"]) if row["new_values"] else None,
                "ip_address": row["ip_address"],
                "user_agent": row["user_agent"],
                "created_at": row["created_at"].isoformat()
            })

        return {
            "user_id": user_id,
            "count": len(audit_entries),
            "entries": audit_entries
        }

    except Exception as e:
        logger.error(f"Error fetching user audit trail: {e}")
        return {"error": str(e)}


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
            "topic": "task-events",
            "route": "/task-events"
        }
    ]


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint."""
    pool = await get_db_pool()
    db_status = "connected" if pool else "disconnected"

    return {
        "status": "healthy",
        "service": "audit-service",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Audit Service",
        "version": "1.0.0",
        "description": "Logs all task operations for compliance and tracking"
    }


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize database connection pool on startup."""
    await get_db_pool()


@app.on_event("shutdown")
async def shutdown():
    """Close database connection pool on shutdown."""
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("Database connection pool closed")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
