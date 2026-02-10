"""
Integration Tests for Phase V Backend API

Tests all new endpoints with database integration.
"""
import pytest
import asyncio
import httpx
import os
from datetime import datetime, timedelta

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpass123"

# Global token storage
auth_token = None


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def authenticated_client():
    """Create authenticated HTTP client."""
    global auth_token

    async with httpx.AsyncClient(base_url=API_URL) as client:
        # Login to get token
        response = await client.post("/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })

        if response.status_code == 200:
            auth_token = response.json()["token"]
        else:
            pytest.fail(f"Authentication failed: {response.status_code}")

        # Set default headers
        client.headers["Authorization"] = f"Bearer {auth_token}"
        yield client


class TestTaskCRUD:
    """Test basic task CRUD operations with Phase V fields."""

    @pytest.mark.asyncio
    async def test_create_task_with_priority(self, authenticated_client):
        """Test creating a task with priority."""
        response = await authenticated_client.post("/api/tasks", json={
            "title": "High priority task",
            "description": "This is urgent",
            "priority": "high"
        })

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "High priority task"
        assert data["priority"] == "high"
        assert data["completed"] == False

        # Store task ID for cleanup
        return data["id"]

    @pytest.mark.asyncio
    async def test_create_task_with_due_date(self, authenticated_client):
        """Test creating a task with due date."""
        due_date = (datetime.utcnow() + timedelta(days=7)).isoformat()

        response = await authenticated_client.post("/api/tasks", json={
            "title": "Task with due date",
            "priority": "medium",
            "due_date": due_date
        })

        assert response.status_code == 201
        data = response.json()
        assert data["due_date"] is not None
        assert data["priority"] == "medium"

    @pytest.mark.asyncio
    async def test_create_task_with_tags(self, authenticated_client):
        """Test creating a task with tags."""
        response = await authenticated_client.post("/api/tasks", json={
            "title": "Task with tags",
            "priority": "low",
            "tags": ["work", "urgent", "backend"]
        })

        assert response.status_code == 201
        data = response.json()
        assert "tags" in data
        assert len(data["tags"]) == 3
        assert "work" in data["tags"]
        assert "urgent" in data["tags"]
        assert "backend" in data["tags"]

    @pytest.mark.asyncio
    async def test_create_recurring_task(self, authenticated_client):
        """Test creating a recurring task."""
        response = await authenticated_client.post("/api/tasks", json={
            "title": "Daily standup",
            "priority": "medium",
            "is_recurring": True
        })

        assert response.status_code == 201
        data = response.json()
        assert data["is_recurring"] == True


class TestAdvancedSearch:
    """Test advanced search functionality."""

    @pytest.mark.asyncio
    async def test_search_by_priority(self, authenticated_client):
        """Test searching tasks by priority."""
        response = await authenticated_client.get("/api/tasks/search?priority=high")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # All returned tasks should have high priority
        for task in data:
            assert task["priority"] == "high"

    @pytest.mark.asyncio
    async def test_search_by_tags(self, authenticated_client):
        """Test searching tasks by tags."""
        response = await authenticated_client.get("/api/tasks/search?tags=work,urgent")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_search_by_text(self, authenticated_client):
        """Test full-text search."""
        response = await authenticated_client.get("/api/tasks/search?q=urgent")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_search_with_date_range(self, authenticated_client):
        """Test searching tasks by due date range."""
        due_after = datetime.utcnow().isoformat()
        due_before = (datetime.utcnow() + timedelta(days=30)).isoformat()

        response = await authenticated_client.get(
            f"/api/tasks/search?due_after={due_after}&due_before={due_before}"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_search_with_sorting(self, authenticated_client):
        """Test searching with custom sorting."""
        response = await authenticated_client.get(
            "/api/tasks/search?sort_by=priority&sort_order=desc"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestTagManagement:
    """Test tag management endpoints."""

    @pytest.mark.asyncio
    async def test_add_tags_to_task(self, authenticated_client):
        """Test adding tags to an existing task."""
        # First create a task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Task for tag testing",
            "priority": "medium"
        })
        task_id = create_response.json()["id"]

        # Add tags
        response = await authenticated_client.post(
            f"/api/tasks/{task_id}/tags",
            json={"tags": ["test", "integration", "phase5"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "tags" in data
        assert len(data["tags"]) == 3
        assert "test" in data["tags"]


class TestReminders:
    """Test reminder functionality."""

    @pytest.mark.asyncio
    async def test_create_reminder(self, authenticated_client):
        """Test creating a reminder for a task."""
        # Create a task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Task with reminder",
            "priority": "high"
        })
        task_id = create_response.json()["id"]

        # Create reminder
        reminder_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()
        response = await authenticated_client.post(
            f"/api/tasks/{task_id}/reminders",
            json={
                "reminder_time": reminder_time,
                "reminder_type": "notification"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["task_id"] == task_id
        assert data["reminder_type"] == "notification"
        assert data["is_sent"] == False

    @pytest.mark.asyncio
    async def test_create_email_reminder(self, authenticated_client):
        """Test creating an email reminder."""
        # Create a task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Task with email reminder",
            "priority": "medium"
        })
        task_id = create_response.json()["id"]

        # Create email reminder
        reminder_time = (datetime.utcnow() + timedelta(days=1)).isoformat()
        response = await authenticated_client.post(
            f"/api/tasks/{task_id}/reminders",
            json={
                "reminder_time": reminder_time,
                "reminder_type": "email"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["reminder_type"] == "email"


class TestRecurringTasks:
    """Test recurring task functionality."""

    @pytest.mark.asyncio
    async def test_create_recurring_pattern(self, authenticated_client):
        """Test creating a recurring pattern for a task."""
        # Create a recurring task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Daily recurring task",
            "priority": "medium",
            "is_recurring": True
        })
        task_id = create_response.json()["id"]

        # Create recurring pattern
        response = await authenticated_client.post(
            f"/api/tasks/{task_id}/recurring",
            json={
                "frequency": "daily",
                "interval": 1
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["frequency"] == "daily"
        assert data["interval"] == 1
        assert data["is_active"] == True

    @pytest.mark.asyncio
    async def test_create_weekly_recurring_pattern(self, authenticated_client):
        """Test creating a weekly recurring pattern."""
        # Create a recurring task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Weekly meeting",
            "priority": "high",
            "is_recurring": True
        })
        task_id = create_response.json()["id"]

        # Create weekly pattern (every Monday and Friday)
        response = await authenticated_client.post(
            f"/api/tasks/{task_id}/recurring",
            json={
                "frequency": "weekly",
                "interval": 1,
                "days_of_week": "[1,5]"  # Monday and Friday
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["frequency"] == "weekly"
        assert data["days_of_week"] == "[1,5]"

    @pytest.mark.asyncio
    async def test_get_recurring_instances(self, authenticated_client):
        """Test getting all instances of a recurring task."""
        # Create a recurring task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Recurring task with instances",
            "priority": "medium",
            "is_recurring": True
        })
        task_id = create_response.json()["id"]

        # Get instances
        response = await authenticated_client.get(f"/api/tasks/{task_id}/instances")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the parent task


class TestTaskCompletion:
    """Test task completion with event publishing."""

    @pytest.mark.asyncio
    async def test_complete_task(self, authenticated_client):
        """Test completing a task."""
        # Create a task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Task to complete",
            "priority": "low"
        })
        task_id = create_response.json()["id"]

        # Complete the task
        response = await authenticated_client.patch(f"/api/tasks/{task_id}/complete")

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] == True

    @pytest.mark.asyncio
    async def test_complete_recurring_task(self, authenticated_client):
        """Test completing a recurring task (should trigger instance generation)."""
        # Create a recurring task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Recurring task to complete",
            "priority": "medium",
            "is_recurring": True
        })
        task_id = create_response.json()["id"]

        # Create recurring pattern
        await authenticated_client.post(
            f"/api/tasks/{task_id}/recurring",
            json={
                "frequency": "daily",
                "interval": 1
            }
        )

        # Complete the task
        response = await authenticated_client.patch(f"/api/tasks/{task_id}/complete")

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] == True

        # Wait a bit for event processing
        await asyncio.sleep(2)

        # Check if new instance was created (this might take time due to async processing)
        instances_response = await authenticated_client.get(f"/api/tasks/{task_id}/instances")
        instances = instances_response.json()

        # Should have at least the parent task
        assert len(instances) >= 1


class TestDataValidation:
    """Test input validation and error handling."""

    @pytest.mark.asyncio
    async def test_invalid_priority(self, authenticated_client):
        """Test creating task with invalid priority."""
        response = await authenticated_client.post("/api/tasks", json={
            "title": "Task with invalid priority",
            "priority": "super-urgent"  # Invalid
        })

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_past_reminder_time(self, authenticated_client):
        """Test creating reminder with past time."""
        # Create a task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Task for reminder test",
            "priority": "medium"
        })
        task_id = create_response.json()["id"]

        # Try to create reminder with past time
        past_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        response = await authenticated_client.post(
            f"/api/tasks/{task_id}/reminders",
            json={
                "reminder_time": past_time,
                "reminder_type": "notification"
            }
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_recurring_frequency(self, authenticated_client):
        """Test creating recurring pattern with invalid frequency."""
        # Create a task
        create_response = await authenticated_client.post("/api/tasks", json={
            "title": "Task for recurring test",
            "priority": "medium",
            "is_recurring": True
        })
        task_id = create_response.json()["id"]

        # Try invalid frequency
        response = await authenticated_client.post(
            f"/api/tasks/{task_id}/recurring",
            json={
                "frequency": "sometimes",  # Invalid
                "interval": 1
            }
        )

        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
