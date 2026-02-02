# REST API Specification

## Base URL
- **Development:** `http://localhost:8000`  
- **Production:** `[YOUR_PRODUCTION_URL]`

## Authentication
All endpoints require the following header:

```

Authorization: Bearer <jwt_token>

````

---

## Endpoints

### Tasks

#### GET /api/tasks
List all tasks for the authenticated user.

**Query Parameters:**
- `status`: `"all"` | `"pending"` | `"completed"` (default: `"all"`)  
- `sort`: `"created"` | `"title"` | `"updated"` (default: `"created"`)

**Response 200:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Milk and eggs",
      "completed": false,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
````

---

#### POST /api/tasks

Create a new task.

**Request Body:**

```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 1000 chars)"
}
```

**Response 201:** Created task object.

---

#### GET /api/tasks/{id}

Get details of a single task.

**Response 200:** Task object
**Response 404:** Not found or not owned by user

---

#### PUT /api/tasks/{id}

Update a task.

**Request Body:**

```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "completed": "boolean (optional)"
}
```

**Response 200:** Updated task object

---

#### DELETE /api/tasks/{id}

Delete a task.

**Response 204:** No content

---

#### PATCH /api/tasks/{id}/complete

Toggle the completion status of a task.

**Response 200:** Updated task with new `completed` status

---

## Error Responses

All errors return JSON:

```json
{
  "detail": "Error message here"
}
```

**Common Status Codes:**

* `401`: Missing or invalid token
* `403`: Token valid but user_id mismatch
* `404`: Task not found
* `422`: Validation error

```


