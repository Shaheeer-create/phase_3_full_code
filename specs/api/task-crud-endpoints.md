# Task CRUD API Endpoints

## Overview

RESTful API endpoints for task management with full CRUD operations, pagination, filtering, and sorting.

## Base URL

```
http://localhost:8000/api/tasks
```

## Authentication

All endpoints require JWT authentication.

**Header:**
```
Authorization: Bearer <token>
```

---

## Endpoints

### 1. List Tasks

**GET** `/api/tasks`

Retrieve paginated list of user's tasks with optional filtering and sorting.

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number (1-indexed) |
| page_size | integer | 20 | Items per page (max: 100) |
| completed | boolean | - | Filter by completion status |
| priority | string | - | Filter by priority (low, medium, high) |
| search | string | - | Search in title and description |
| sort_by | string | created_at | Sort field (created_at, due_date, priority, title) |
| order | string | desc | Sort order (asc, desc) |

**Example Request:**
```
GET /api/tasks?page=1&page_size=20&completed=false&priority=high&sort_by=due_date&order=asc
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete project documentation",
      "description": "Write comprehensive API documentation",
      "priority": "high",
      "completed": false,
      "due_date": "2026-02-15T10:00:00Z",
      "tags": ["documentation", "urgent"],
      "created_at": "2026-02-01T09:00:00Z",
      "updated_at": "2026-02-01T09:00:00Z",
      "user_id": "123e4567-e89b-12d3-a456-426614174000"
    }
  ],
  "pagination": {
    "total": 150,
    "page": 1,
    "page_size": 20,
    "total_pages": 8,
    "has_previous": false,
    "has_next": true
  }
}
```

---

### 2. Create Task

**POST** `/api/tasks`

Create a new task for the authenticated user.

**Request Body:**
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "priority": "high",
  "due_date": "2026-02-15T10:00:00Z",
  "tags": ["documentation", "urgent"]
}
```

**Validation Rules:**
- `title`: Required, 1-100 characters
- `description`: Optional, max 500 characters
- `priority`: Optional, one of: low, medium, high (default: medium)
- `due_date`: Optional, ISO 8601 datetime, must be in future
- `tags`: Optional, array of strings, max 10 tags, each max 20 characters

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "priority": "high",
  "completed": false,
  "due_date": "2026-02-15T10:00:00Z",
  "tags": ["documentation", "urgent"],
  "created_at": "2026-02-01T09:00:00Z",
  "updated_at": "2026-02-01T09:00:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Headers:**
```
Location: /api/tasks/550e8400-e29b-41d4-a716-446655440000
```

**Error Responses:**

**422 Unprocessable Entity** - Validation failed
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "title": "Title is required and must be between 1-100 characters",
      "due_date": "Due date must be in the future"
    }
  }
}
```

---

### 3. Get Single Task

**GET** `/api/tasks/{task_id}`

Retrieve a specific task by ID.

**Path Parameters:**
- `task_id`: UUID of the task

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete project documentation",
  "description": "Write comprehensive API documentation",
  "priority": "high",
  "completed": false,
  "due_date": "2026-02-15T10:00:00Z",
  "tags": ["documentation", "urgent"],
  "created_at": "2026-02-01T09:00:00Z",
  "updated_at": "2026-02-01T09:00:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Error Responses:**

**404 Not Found** - Task doesn't exist
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found"
  }
}
```

**403 Forbidden** - Task belongs to another user
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You don't have permission to access this task"
  }
}
```

---

### 4. Update Task

**PATCH** `/api/tasks/{task_id}`

Partially update a task. Only provided fields will be updated.

**Path Parameters:**
- `task_id`: UUID of the task

**Request Body:**
```json
{
  "title": "Updated title",
  "completed": true,
  "priority": "medium"
}
```

**All fields are optional:**
- `title`: 1-100 characters
- `description`: max 500 characters
- `priority`: low, medium, high
- `completed`: boolean
- `due_date`: ISO 8601 datetime
- `tags`: array of strings

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Updated title",
  "description": "Write comprehensive API documentation",
  "priority": "medium",
  "completed": true,
  "due_date": "2026-02-15T10:00:00Z",
  "tags": ["documentation", "urgent"],
  "created_at": "2026-02-01T09:00:00Z",
  "updated_at": "2026-02-01T15:30:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

**Error Responses:**

**404 Not Found** - Task doesn't exist
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found"
  }
}
```

**403 Forbidden** - Task belongs to another user
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You don't have permission to update this task"
  }
}
```

**422 Unprocessable Entity** - Validation failed
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "title": "Title must be between 1-100 characters"
    }
  }
}
```

---

### 5. Delete Task

**DELETE** `/api/tasks/{task_id}`

Delete a task permanently.

**Path Parameters:**
- `task_id`: UUID of the task

**Response (204 No Content)**

No response body.

**Error Responses:**

**404 Not Found** - Task doesn't exist
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found"
  }
}
```

**403 Forbidden** - Task belongs to another user
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "You don't have permission to delete this task"
  }
}
```

---

## Data Model

### Task Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | UUID | Yes | Unique task identifier |
| title | string | Yes | Task title (1-100 chars) |
| description | string | No | Task description (max 500 chars) |
| priority | string | Yes | Priority level: low, medium, high |
| completed | boolean | Yes | Completion status |
| due_date | datetime | No | Due date (ISO 8601) |
| tags | array[string] | No | Task tags |
| created_at | datetime | Yes | Creation timestamp |
| updated_at | datetime | Yes | Last update timestamp |
| user_id | UUID | Yes | Owner user ID |

---

## User Isolation

**Critical:** All endpoints MUST filter tasks by the authenticated user's ID.

```python
# Every query must include user_id filter
tasks = session.exec(
    select(Task).where(Task.user_id == current_user_id)
).all()
```

**Security Rules:**
1. Users can only see their own tasks
2. Users can only create tasks for themselves
3. Users can only update their own tasks
4. Users can only delete their own tasks
5. Attempting to access another user's task returns 403 Forbidden

---

## Pagination

**Default:** 20 items per page
**Maximum:** 100 items per page
**Format:** Offset-based pagination

**Response includes:**
- `total`: Total number of items
- `page`: Current page number
- `page_size`: Items per page
- `total_pages`: Total number of pages
- `has_previous`: Boolean, has previous page
- `has_next`: Boolean, has next page

---

## Filtering

**Supported Filters:**

1. **By Completion Status**
   ```
   GET /api/tasks?completed=true
   GET /api/tasks?completed=false
   ```

2. **By Priority**
   ```
   GET /api/tasks?priority=high
   GET /api/tasks?priority=medium
   GET /api/tasks?priority=low
   ```

3. **By Search (title and description)**
   ```
   GET /api/tasks?search=documentation
   ```

4. **Combined Filters**
   ```
   GET /api/tasks?completed=false&priority=high&search=urgent
   ```

---

## Sorting

**Supported Sort Fields:**
- `created_at` (default)
- `updated_at`
- `due_date`
- `priority`
- `title`

**Sort Order:**
- `asc` - Ascending
- `desc` - Descending (default)

**Examples:**
```
GET /api/tasks?sort_by=due_date&order=asc
GET /api/tasks?sort_by=priority&order=desc
GET /api/tasks?sort_by=title&order=asc
```

---

## Examples

### Create a high-priority task

**Request:**
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Finish quarterly report",
    "description": "Complete Q4 financial report",
    "priority": "high",
    "due_date": "2026-02-10T17:00:00Z",
    "tags": ["finance", "quarterly"]
  }'
```

### Get all incomplete high-priority tasks

**Request:**
```bash
curl -X GET "http://localhost:8000/api/tasks?completed=false&priority=high" \
  -H "Authorization: Bearer <token>"
```

### Mark task as complete

**Request:**
```bash
curl -X PATCH http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'
```

### Delete a task

**Request:**
```bash
curl -X DELETE http://localhost:8000/api/tasks/550e8400-e29b-41d4-a716-446655440000 \
  -H "Authorization: Bearer <token>"
```

---

## Performance Considerations

1. **Indexes**
   - `user_id` (for user isolation)
   - `completed` (for filtering)
   - `user_id, completed` (composite for common query)
   - `created_at` (for sorting)
   - `due_date` (for sorting)

2. **Query Optimization**
   - Always filter by user_id first
   - Use pagination to limit results
   - Avoid N+1 queries

3. **Caching**
   - Cache task lists for 60 seconds
   - Invalidate cache on create/update/delete
