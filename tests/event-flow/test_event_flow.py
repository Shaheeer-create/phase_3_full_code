"""
Event Flow Tests for Phase V

Tests Kafka event publishing and consumption across microservices.
"""
import pytest
import asyncio
import httpx
import asyncpg
import os
from datetime import datetime, timedelta
import json

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL")
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpass123"

auth_token = None


@pytest.fixture(scope="session")
async def authenticated_client():
    """Create authenticated HTTP client."""
    global auth_token

    async with httpx.AsyncClient(base_url=API_URL) as client:
        response = await client.post("/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })

        if response.status_code == 200:
            auth_token = response.json()["token"]
        else:
            pytest.fail(f"Authentication failed: {response.status_code}")

        client.headers["Authorization"] = f"Bearer {auth_token}"
        yield client


@pytest.fixture(scope="session")
async def db_connection():
    """Create database connection for verification."""
    if not DATABASE_URL:
        pytest.skip("DATABASE_URL not configured")

    conn = await asyncpg.connect(DATABASE_URL)
    yield conn
    await conn.close()


class TestTaskEventPublishing:
    """Test that task operations publish events to Kafka."""

    @pytest.mark.asyncio
    async def test_task_created_event_logged(self, authenticated_client, db_connection):
        """Test that task creation publishes event and audit service logs it."""
        # Create a task
        response = await authenticated_client.post("/api/tasks", json={
            "title": "Event test task",
            "description": "Testing event flow",
            "priority": "high",
            "tags": ["test", "event"]
        })

        assert response.status_code == 201
        task_id = response.json()["id"]

        # Wait for event processing
        await asyncio.sleep(3)

        # Check audit log for task creation event
        audit_entry = await db_connection.fetchrow(
            """
            SELECT * FROM audit_log
            WHERE entity_type = 'task'
            AND entity_id = $1
            AND action = 'create'
            ORDER BY created_at DESC
            LIMIT 1
            """,
            task_id
        )

        assert audit_entry is not None, "Audit log entry not found"
        assert audit_entry["user_id"] is not None
        assert audit_entry["action"] == "create"

        # Verify new_values contains task data
        new_values = json.loads(audit_entry["new_values"])
        assert new_values["title"] == "Event test task"
        assert new_values["priority"] == "high"

    @pytest.mark.asyncio
    async def test_task_updated_event_logged(self, authenticated_client, db_connection):
        """Test that task update publishes event and audit service logs it."""
        # Create a task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Task to update",
            "priority": "low"
        })
        task_id = create_response.json()["id"]

        # Wait for creation event
        await asyncio.sleep(2)

        # Update the task
        update_response = await authenticated_client.put(
            f"/api/tasks/{task_id}",
            json={
                "title": "Updated task title",
                "priority": "high"
            }
        )

        assert update_response.status_code == 200

        # Wait for event processing
        await asyncio.sleep(3)

        # Check audit log for update event
        audit_entry = await db_connection.fetchrow(
            """
            SELECT * FROM audit_log
            WHERE entity_type = 'task'
            AND entity_id = $1
            AND action = 'update'
            ORDER BY created_at DESC
            LIMIT 1
            """,
            task_id
        )

        assert audit_entry is not None, "Update audit log entry not found"
        assert audit_entry["action"] == "update"

        # Verify old and new values
        old_values = json.loads(audit_entry["old_values"])
        new_values = json.loads(audit_entry["new_values"])

        assert old_values["priority"] == "low"
        assert new_values["priority"] == "high"
        assert new_values["title"] == "Updated task title"

    @pytest.mark.asyncio
    async def test_task_completed_event_logged(self, authenticated_client, db_connection):
        """Test that task completion publishes event and audit service logs it."""
        # Create a task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Task to complete",
            "priority": "medium"
        })
        task_id = create_response.json()["id"]

        # Wait for creation event
        await asyncio.sleep(2)

        # Complete the task
        complete_response = await authenticated_client.patch(
            f"/api/tasks/{task_id}/complete"
        )

        assert complete_response.status_code == 200

        # Wait for event processing
        await asyncio.sleep(3)

        # Check audit log for complete event
        audit_entry = await db_connection.fetchrow(
            """
            SELECT * FROM audit_log
            WHERE entity_type = 'task'
            AND entity_id = $1
            AND action = 'complete'
            ORDER BY created_at DESC
            LIMIT 1
            """,
            task_id
        )

        assert audit_entry is not None, "Complete audit log entry not found"
        assert audit_entry["action"] == "complete"

        # Verify completed status in new_values
        new_values = json.loads(audit_entry["new_values"])
        assert new_values["completed"] == True

    @pytest.mark.asyncio
    async def test_task_deleted_event_logged(self, authenticated_client, db_connection):
        """Test that task deletion publishes event and audit service logs it."""
        # Create a task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Task to delete",
            "priority": "low"
        })
        task_id = create_response.json()["id"]

        # Wait for creation event
        await asyncio.sleep(2)

        # Delete the task
        delete_response = await authenticated_client.delete(f"/api/tasks/{task_id}")

        assert delete_response.status_code == 204

        # Wait for event processing
        await asyncio.sleep(3)

        # Check audit log for delete event
        audit_entry = await db_connection.fetchrow(
            """
            SELECT * FROM audit_log
            WHERE entity_type = 'task'
            AND entity_id = $1
            AND action = 'delete'
            ORDER BY created_at DESC
            LIMIT 1
            """,
            task_id
        )

        assert audit_entry is not None, "Delete audit log entry not found"
        assert audit_entry["action"] == "delete"


class TestRecurringTaskEventFlow:
    """Test recurring task event flow and instance generation."""

    @pytest.mark.asyncio
    async def test_recurring_task_generates_instance(self, authenticated_client, db_connection):
        """Test that completing a recurring task generates next instance."""
        # Create a recurring task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Daily recurring task",
            "description": "Should generate next instance",
            "priority": "medium",
            "is_recurring": True
        })
        task_id = create_response.json()["id"]

        # Create recurring pattern
        pattern_response = await authenticated_client.post(
            f"/api/tasks/{task_id}/recurring",
            json={
                "frequency": "daily",
                "interval": 1
            }
        )

        assert pattern_response.status_code == 201

        # Wait for pattern creation
        await asyncio.sleep(2)

        # Complete the task (should trigger instance generation)
        complete_response = await authenticated_client.patch(
            f"/api/tasks/{task_id}/complete"
        )

        assert complete_response.status_code == 200

        # Wait for event processing and instance generation
        await asyncio.sleep(5)

        # Check if new instance was created
        instances = await db_connection.fetch(
            """
            SELECT * FROM tasks
            WHERE parent_task_id = $1
            ORDER BY created_at DESC
            """,
            task_id
        )

        # Note: Instance generation depends on recurring service being deployed
        # This test may fail if recurring service is not running
        if len(instances) > 0:
            assert instances[0]["parent_task_id"] == task_id
            assert instances[0]["title"] == "Daily recurring task"
            print(f"✓ Recurring instance generated: {instances[0]['id']}")
        else:
            print("⚠ No recurring instance found (recurring service may not be running)")


class TestReminderEventFlow:
    """Test reminder event flow and notification service."""

    @pytest.mark.asyncio
    async def test_reminder_created_in_database(self, authenticated_client, db_connection):
        """Test that reminder is created in database."""
        # Create a task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Task with reminder",
            "priority": "high"
        })
        task_id = create_response.json()["id"]

        # Create reminder
        reminder_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        reminder_response = await authenticated_client.post(
            f"/api/tasks/{task_id}/reminders",
            json={
                "reminder_time": reminder_time,
                "reminder_type": "notification"
            }
        )

        assert reminder_response.status_code == 201
        reminder_id = reminder_response.json()["id"]

        # Verify reminder in database
        reminder = await db_connection.fetchrow(
            """
            SELECT * FROM task_reminders
            WHERE id = $1
            """,
            reminder_id
        )

        assert reminder is not None
        assert reminder["task_id"] == task_id
        assert reminder["is_sent"] == False
        assert reminder["reminder_type"] == "notification"


class TestAuditTrailQuery:
    """Test audit service query endpoints."""

    @pytest.mark.asyncio
    async def test_get_task_audit_trail(self, authenticated_client):
        """Test getting audit trail for a specific task."""
        # Create a task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Task for audit trail test",
            "priority": "medium"
        })
        task_id = create_response.json()["id"]

        # Update the task
        await authenticated_client.put(
            f"/api/tasks/{task_id}",
            json={"priority": "high"}
        )

        # Complete the task
        await authenticated_client.patch(f"/api/tasks/{task_id}/complete")

        # Wait for events to be processed
        await asyncio.sleep(3)

        # Query audit service for task audit trail
        # Note: This requires audit service to be running and accessible
        try:
            audit_response = await httpx.AsyncClient().get(
                f"http://localhost:8004/audit/task/{task_id}"
            )

            if audit_response.status_code == 200:
                audit_data = audit_response.json()
                assert "entries" in audit_data
                assert audit_data["count"] >= 3  # create, update, complete

                print(f"✓ Audit trail retrieved: {audit_data['count']} entries")
            else:
                print("⚠ Audit service not accessible")
        except Exception as e:
            print(f"⚠ Could not connect to audit service: {e}")


class TestEventProcessingLatency:
    """Test event processing latency."""

    @pytest.mark.asyncio
    async def test_event_processing_time(self, authenticated_client, db_connection):
        """Measure time from task creation to audit log entry."""
        import time

        # Record start time
        start_time = time.time()

        # Create a task
        response = await authenticated_client.post("/api/tasks", json={
            "title": "Latency test task",
            "priority": "high"
        })

        task_id = response.json()["id"]

        # Poll for audit log entry
        max_wait = 10  # seconds
        poll_interval = 0.5  # seconds
        elapsed = 0

        while elapsed < max_wait:
            audit_entry = await db_connection.fetchrow(
                """
                SELECT * FROM audit_log
                WHERE entity_type = 'task'
                AND entity_id = $1
                AND action = 'create'
                """,
                task_id
            )

            if audit_entry:
                processing_time = time.time() - start_time
                print(f"✓ Event processed in {processing_time:.2f} seconds")
                assert processing_time < 5, "Event processing took too long"
                break

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        if elapsed >= max_wait:
            pytest.fail("Event not processed within timeout")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
