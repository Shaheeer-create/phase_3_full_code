"""
End-to-End Tests for Phase V Frontend

Tests complete user workflows using Playwright.
"""
import pytest
from playwright.async_api import async_playwright, Page, expect
import asyncio
import os

# Configuration
BASE_URL = os.getenv("BASE_URL", "http://todo.local")
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpass123"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def browser():
    """Launch browser for tests."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture
async def authenticated_page(browser):
    """Create authenticated page."""
    context = await browser.new_context()
    page = await context.new_page()

    # Navigate to login page
    await page.goto(f"{BASE_URL}/login")

    # Login
    await page.fill('input[name="email"]', TEST_USER_EMAIL)
    await page.fill('input[name="password"]', TEST_USER_PASSWORD)
    await page.click('button[type="submit"]')

    # Wait for navigation to tasks page
    await page.wait_for_url(f"{BASE_URL}/tasks", timeout=10000)

    yield page

    await context.close()


class TestTaskCreation:
    """Test task creation workflows."""

    @pytest.mark.asyncio
    async def test_create_basic_task(self, authenticated_page: Page):
        """Test creating a basic task."""
        page = authenticated_page

        # Click on task input to expand form
        await page.click('input[placeholder*="Add a new task"]')

        # Fill in task title
        await page.fill('input[placeholder*="Add a new task"]', "E2E Test Task")

        # Submit form
        await page.click('button:has-text("Add task")')

        # Wait for task to appear
        await page.wait_for_selector('text=E2E Test Task', timeout=5000)

        # Verify task is visible
        task = page.locator('text=E2E Test Task')
        await expect(task).to_be_visible()

    @pytest.mark.asyncio
    async def test_create_task_with_priority(self, authenticated_page: Page):
        """Test creating a task with priority selection."""
        page = authenticated_page

        # Expand task form
        await page.click('input[placeholder*="Add a new task"]')

        # Fill in task title
        await page.fill('input[placeholder*="Add a new task"]', "High Priority Task")

        # Select high priority
        await page.click('button:has-text("High")')

        # Submit form
        await page.click('button:has-text("Add task")')

        # Wait for task to appear
        await page.wait_for_selector('text=High Priority Task', timeout=5000)

        # Verify priority badge is visible
        high_badge = page.locator('text=High Priority Task').locator('..').locator('text=High')
        await expect(high_badge).to_be_visible()

    @pytest.mark.asyncio
    async def test_create_task_with_tags(self, authenticated_page: Page):
        """Test creating a task with tags."""
        page = authenticated_page

        # Expand task form
        await page.click('input[placeholder*="Add a new task"]')

        # Fill in task title
        await page.fill('input[placeholder*="Add a new task"]', "Task with Tags")

        # Add tags
        await page.fill('input[placeholder*="Add tags"]', "work")
        await page.press('input[placeholder*="Add tags"]', "Enter")

        await page.fill('input[placeholder*="Add tags"]', "urgent")
        await page.press('input[placeholder*="Add tags"]', "Enter")

        # Submit form
        await page.click('button:has-text("Add task")')

        # Wait for task to appear
        await page.wait_for_selector('text=Task with Tags', timeout=5000)

        # Verify tags are visible
        work_tag = page.locator('text=Task with Tags').locator('..').locator('text=#work')
        urgent_tag = page.locator('text=Task with Tags').locator('..').locator('text=#urgent')

        await expect(work_tag).to_be_visible()
        await expect(urgent_tag).to_be_visible()

    @pytest.mark.asyncio
    async def test_create_task_with_due_date(self, authenticated_page: Page):
        """Test creating a task with due date."""
        page = authenticated_page

        # Expand task form
        await page.click('input[placeholder*="Add a new task"]')

        # Fill in task title
        await page.fill('input[placeholder*="Add a new task"]', "Task with Due Date")

        # Set due date (tomorrow)
        from datetime import datetime, timedelta
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        await page.fill('input[type="datetime-local"]', tomorrow)

        # Submit form
        await page.click('button:has-text("Add task")')

        # Wait for task to appear
        await page.wait_for_selector('text=Task with Due Date', timeout=5000)

        # Verify due date indicator is visible
        due_indicator = page.locator('text=Task with Due Date').locator('..').locator('text=/Due in/')
        await expect(due_indicator).to_be_visible()


class TestTaskCompletion:
    """Test task completion workflows."""

    @pytest.mark.asyncio
    async def test_complete_task(self, authenticated_page: Page):
        """Test completing a task."""
        page = authenticated_page

        # Create a task first
        await page.click('input[placeholder*="Add a new task"]')
        await page.fill('input[placeholder*="Add a new task"]', "Task to Complete")
        await page.click('button:has-text("Add task")')
        await page.wait_for_selector('text=Task to Complete', timeout=5000)

        # Find and click the checkbox
        task_row = page.locator('text=Task to Complete').locator('..')
        checkbox = task_row.locator('button[aria-label*="Mark as complete"]')
        await checkbox.click()

        # Wait for completion animation
        await page.wait_for_timeout(1000)

        # Verify task is marked as completed
        completed_indicator = task_row.locator('text=Completed')
        await expect(completed_indicator).to_be_visible()

    @pytest.mark.asyncio
    async def test_uncomplete_task(self, authenticated_page: Page):
        """Test uncompleting a task."""
        page = authenticated_page

        # Create and complete a task
        await page.click('input[placeholder*="Add a new task"]')
        await page.fill('input[placeholder*="Add a new task"]', "Task to Uncomplete")
        await page.click('button:has-text("Add task")')
        await page.wait_for_selector('text=Task to Uncomplete', timeout=5000)

        # Complete it
        task_row = page.locator('text=Task to Uncomplete').locator('..')
        checkbox = task_row.locator('button[aria-label*="Mark as complete"]')
        await checkbox.click()
        await page.wait_for_timeout(1000)

        # Uncomplete it
        await checkbox.click()
        await page.wait_for_timeout(1000)

        # Verify task is no longer marked as completed
        completed_indicator = task_row.locator('text=Completed')
        await expect(completed_indicator).not_to_be_visible()


class TestTaskFiltering:
    """Test task filtering and search."""

    @pytest.mark.asyncio
    async def test_filter_by_status(self, authenticated_page: Page):
        """Test filtering tasks by status."""
        page = authenticated_page

        # Create a completed task
        await page.click('input[placeholder*="Add a new task"]')
        await page.fill('input[placeholder*="Add a new task"]', "Completed Task")
        await page.click('button:has-text("Add task")')
        await page.wait_for_selector('text=Completed Task', timeout=5000)

        task_row = page.locator('text=Completed Task').locator('..')
        checkbox = task_row.locator('button[aria-label*="Mark as complete"]')
        await checkbox.click()
        await page.wait_for_timeout(1000)

        # Create a pending task
        await page.click('input[placeholder*="Add a new task"]')
        await page.fill('input[placeholder*="Add a new task"]', "Pending Task")
        await page.click('button:has-text("Add task")')
        await page.wait_for_selector('text=Pending Task', timeout=5000)

        # Filter to show only completed
        await page.click('button:has-text("Completed")')
        await page.wait_for_timeout(500)

        # Verify completed task is visible and pending is not
        await expect(page.locator('text=Completed Task')).to_be_visible()
        await expect(page.locator('text=Pending Task')).not_to_be_visible()

        # Filter to show only pending
        await page.click('button:has-text("Pending")')
        await page.wait_for_timeout(500)

        # Verify pending task is visible and completed is not
        await expect(page.locator('text=Pending Task')).to_be_visible()
        await expect(page.locator('text=Completed Task')).not_to_be_visible()

    @pytest.mark.asyncio
    async def test_search_tasks(self, authenticated_page: Page):
        """Test searching tasks."""
        page = authenticated_page

        # Create tasks with different titles
        tasks = ["Frontend Bug", "Backend Feature", "Database Migration"]

        for task_title in tasks:
            await page.click('input[placeholder*="Add a new task"]')
            await page.fill('input[placeholder*="Add a new task"]', task_title)
            await page.click('button:has-text("Add task")')
            await page.wait_for_selector(f'text={task_title}', timeout=5000)

        # Search for "Backend"
        await page.fill('input[placeholder*="Search tasks"]', "Backend")
        await page.press('input[placeholder*="Search tasks"]', "Enter")
        await page.wait_for_timeout(1000)

        # Verify only Backend task is visible
        await expect(page.locator('text=Backend Feature')).to_be_visible()
        await expect(page.locator('text=Frontend Bug')).not_to_be_visible()


class TestTaskDeletion:
    """Test task deletion workflows."""

    @pytest.mark.asyncio
    async def test_delete_task(self, authenticated_page: Page):
        """Test deleting a task."""
        page = authenticated_page

        # Create a task
        await page.click('input[placeholder*="Add a new task"]')
        await page.fill('input[placeholder*="Add a new task"]', "Task to Delete")
        await page.click('button:has-text("Add task")')
        await page.wait_for_selector('text=Task to Delete', timeout=5000)

        # Hover over task to show delete button
        task_row = page.locator('text=Task to Delete').locator('..')
        await task_row.hover()

        # Click delete button
        delete_button = task_row.locator('button[aria-label*="Delete"]')
        await delete_button.click()

        # Wait for deletion animation
        await page.wait_for_timeout(1000)

        # Verify task is no longer visible
        await expect(page.locator('text=Task to Delete')).not_to_be_visible()


class TestAdvancedFiltering:
    """Test advanced filtering features."""

    @pytest.mark.asyncio
    async def test_filter_by_priority(self, authenticated_page: Page):
        """Test filtering tasks by priority."""
        page = authenticated_page

        # Create tasks with different priorities
        priorities = [("Low Priority Task", "Low"), ("High Priority Task", "High")]

        for task_title, priority in priorities:
            await page.click('input[placeholder*="Add a new task"]')
            await page.fill('input[placeholder*="Add a new task"]', task_title)
            await page.click(f'button:has-text("{priority}")')
            await page.click('button:has-text("Add task")')
            await page.wait_for_selector(f'text={task_title}', timeout=5000)

        # Open filters
        await page.click('button:has-text("Filters")')
        await page.wait_for_timeout(500)

        # Select high priority filter
        await page.click('button:has-text("High")')

        # Apply filters
        await page.click('button:has-text("Apply Filters")')
        await page.wait_for_timeout(1000)

        # Verify only high priority task is visible
        await expect(page.locator('text=High Priority Task')).to_be_visible()
        await expect(page.locator('text=Low Priority Task')).not_to_be_visible()


class TestResponsiveness:
    """Test responsive design."""

    @pytest.mark.asyncio
    async def test_mobile_view(self, browser):
        """Test mobile responsive layout."""
        # Create mobile context
        context = await browser.new_context(
            viewport={'width': 375, 'height': 667},  # iPhone SE size
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
        )
        page = await context.new_page()

        # Navigate and login
        await page.goto(f"{BASE_URL}/login")
        await page.fill('input[name="email"]', TEST_USER_EMAIL)
        await page.fill('input[name="password"]', TEST_USER_PASSWORD)
        await page.click('button[type="submit"]')
        await page.wait_for_url(f"{BASE_URL}/tasks", timeout=10000)

        # Verify page is responsive
        await expect(page.locator('input[placeholder*="Add a new task"]')).to_be_visible()

        # Create a task on mobile
        await page.click('input[placeholder*="Add a new task"]')
        await page.fill('input[placeholder*="Add a new task"]', "Mobile Task")
        await page.click('button:has-text("Add task")')
        await page.wait_for_selector('text=Mobile Task', timeout=5000)

        await expect(page.locator('text=Mobile Task')).to_be_visible()

        await context.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--headed"])
