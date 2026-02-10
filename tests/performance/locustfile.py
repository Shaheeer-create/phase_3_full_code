"""
Performance Tests for Phase V using Locust

Load testing for API endpoints with Phase V features.
"""
from locust import HttpUser, task, between, events
import random
import json
from datetime import datetime, timedelta

# Test data
PRIORITIES = ["low", "medium", "high"]
TAGS = ["work", "personal", "urgent", "backend", "frontend", "bug", "feature"]
TASK_TITLES = [
    "Fix authentication bug",
    "Implement new feature",
    "Update documentation",
    "Review pull request",
    "Deploy to production",
    "Database migration",
    "Performance optimization",
    "Security audit",
    "Code refactoring",
    "Write unit tests"
]


class TodoAppUser(HttpUser):
    """Simulates a user interacting with the Todo App."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        """Called when a user starts. Login and get token."""
        # Login
        response = self.client.post("/auth/login", json={
            "email": f"loadtest{random.randint(1, 100)}@example.com",
            "password": "testpass123"
        }, catch_response=True)

        if response.status_code == 200:
            self.token = response.json().get("token")
            self.client.headers["Authorization"] = f"Bearer {self.token}"
            response.success()
        else:
            response.failure(f"Login failed: {response.status_code}")
            self.token = None

    @task(10)
    def list_tasks(self):
        """List all tasks (most common operation)."""
        with self.client.get("/api/tasks", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to list tasks: {response.status_code}")

    @task(5)
    def create_task(self):
        """Create a new task with Phase V fields."""
        task_data = {
            "title": random.choice(TASK_TITLES),
            "description": f"Load test task created at {datetime.now().isoformat()}",
            "priority": random.choice(PRIORITIES),
            "tags": random.sample(TAGS, k=random.randint(1, 3))
        }

        # 30% chance to add due date
        if random.random() < 0.3:
            due_date = datetime.now() + timedelta(days=random.randint(1, 30))
            task_data["due_date"] = due_date.isoformat()

        with self.client.post("/api/tasks", json=task_data, catch_response=True) as response:
            if response.status_code == 201:
                response.success()
                # Store task ID for later operations
                if not hasattr(self, 'task_ids'):
                    self.task_ids = []
                self.task_ids.append(response.json()["id"])
            else:
                response.failure(f"Failed to create task: {response.status_code}")

    @task(3)
    def search_tasks(self):
        """Search tasks with various filters."""
        search_params = {}

        # Random search criteria
        if random.random() < 0.3:
            search_params["priority"] = random.choice(PRIORITIES)

        if random.random() < 0.3:
            search_params["tags"] = ",".join(random.sample(TAGS, k=2))

        if random.random() < 0.2:
            search_params["q"] = random.choice(["bug", "feature", "fix", "update"])

        if random.random() < 0.2:
            search_params["status"] = random.choice(["pending", "completed"])

        with self.client.get("/api/tasks/search", params=search_params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to search tasks: {response.status_code}")

    @task(4)
    def complete_task(self):
        """Complete a random task."""
        if hasattr(self, 'task_ids') and self.task_ids:
            task_id = random.choice(self.task_ids)

            with self.client.patch(f"/api/tasks/{task_id}/complete", catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed to complete task: {response.status_code}")

    @task(2)
    def update_task(self):
        """Update a random task."""
        if hasattr(self, 'task_ids') and self.task_ids:
            task_id = random.choice(self.task_ids)

            update_data = {
                "priority": random.choice(PRIORITIES)
            }

            with self.client.put(f"/api/tasks/{task_id}", json=update_data, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed to update task: {response.status_code}")

    @task(2)
    def add_tags_to_task(self):
        """Add tags to a random task."""
        if hasattr(self, 'task_ids') and self.task_ids:
            task_id = random.choice(self.task_ids)

            tags_data = {
                "tags": random.sample(TAGS, k=random.randint(1, 2))
            }

            with self.client.post(f"/api/tasks/{task_id}/tags", json=tags_data, catch_response=True) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Failed to add tags: {response.status_code}")

    @task(1)
    def create_reminder(self):
        """Create a reminder for a random task."""
        if hasattr(self, 'task_ids') and self.task_ids:
            task_id = random.choice(self.task_ids)

            reminder_time = (datetime.now() + timedelta(hours=random.randint(1, 48))).isoformat()
            reminder_data = {
                "reminder_time": reminder_time,
                "reminder_type": random.choice(["notification", "email"])
            }

            with self.client.post(f"/api/tasks/{task_id}/reminders", json=reminder_data, catch_response=True) as response:
                if response.status_code == 201:
                    response.success()
                else:
                    response.failure(f"Failed to create reminder: {response.status_code}")

    @task(1)
    def delete_task(self):
        """Delete a random task."""
        if hasattr(self, 'task_ids') and self.task_ids:
            task_id = self.task_ids.pop(random.randint(0, len(self.task_ids) - 1))

            with self.client.delete(f"/api/tasks/{task_id}", catch_response=True) as response:
                if response.status_code == 204:
                    response.success()
                else:
                    response.failure(f"Failed to delete task: {response.status_code}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    print("=" * 80)
    print("Phase V Performance Test Starting")
    print("=" * 80)
    print(f"Target: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'N/A'}")
    print("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    print("=" * 80)
    print("Phase V Performance Test Complete")
    print("=" * 80)

    # Print summary statistics
    stats = environment.stats
    print(f"Total Requests: {stats.total.num_requests}")
    print(f"Total Failures: {stats.total.num_failures}")
    print(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
    print(f"Min Response Time: {stats.total.min_response_time:.2f}ms")
    print(f"Max Response Time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests per Second: {stats.total.total_rps:.2f}")
    print("=" * 80)

    # Check if performance targets are met
    if stats.total.avg_response_time > 200:
        print("⚠ WARNING: Average response time exceeds target (200ms)")
    else:
        print("✓ Performance target met: Average response time < 200ms")

    if stats.total.num_failures > 0:
        failure_rate = (stats.total.num_failures / stats.total.num_requests) * 100
        print(f"⚠ WARNING: Failure rate: {failure_rate:.2f}%")
    else:
        print("✓ No failures detected")


# Run with:
# locust -f locustfile.py --host=http://localhost:8000 --users=100 --spawn-rate=10 --run-time=5m
