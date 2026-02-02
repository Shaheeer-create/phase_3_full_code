# REST API Design Principles

Best practices and conventions for designing RESTful APIs.

## Table of Contents
- Resource-Based Design
- HTTP Methods
- URL Structure
- Request/Response Format
- Status Codes
- Versioning
- HATEOAS

---

## Resource-Based Design

### Core Principle

REST APIs are built around **resources** (nouns), not actions (verbs).

**Good:**
```
GET    /api/tasks
POST   /api/tasks
GET    /api/tasks/{id}
DELETE /api/tasks/{id}
```

**Bad:**
```
GET    /api/getTasks
POST   /api/createTask
GET    /api/getTaskById?id=123
POST   /api/deleteTask
```

### Resource Naming

**Use plural nouns:**
```
/tasks      ✅ (not /task)
/users      ✅ (not /user)
/comments   ✅ (not /comment)
```

**Use kebab-case for multi-word resources:**
```
/task-templates     ✅
/user-preferences   ✅
/api-keys           ✅
```

**Avoid verbs in URLs:**
```
/tasks              ✅
/getTasks           ❌
/tasks/create       ❌
/tasks/delete       ❌
```

### Nested Resources

Use nested routes for relationships:

```
# Comments belong to tasks
GET    /api/tasks/{taskId}/comments
POST   /api/tasks/{taskId}/comments
GET    /api/tasks/{taskId}/comments/{commentId}
DELETE /api/tasks/{taskId}/comments/{commentId}

# Limit nesting to 2 levels
GET    /api/users/{userId}/tasks/{taskId}/comments  ❌ (too deep)
GET    /api/tasks/{taskId}/comments                 ✅ (better)
```

---

## HTTP Methods

### Standard CRUD Operations

| Method | Operation | Idempotent | Safe |
|--------|-----------|------------|------|
| GET | Read | Yes | Yes |
| POST | Create | No | No |
| PUT | Update (full) | Yes | No |
| PATCH | Update (partial) | No | No |
| DELETE | Delete | Yes | No |

### GET - Retrieve Resources

```
# List resources
GET /api/tasks
Response: 200 OK, array of tasks

# Get single resource
GET /api/tasks/{id}
Response: 200 OK, single task
Response: 404 Not Found (if doesn't exist)
```

**Characteristics:**
- Safe: No side effects
- Idempotent: Multiple calls return same result
- Cacheable: Can be cached by browsers/proxies

### POST - Create Resources

```
POST /api/tasks
Request Body: { "title": "New task" }
Response: 201 Created
Response Headers: Location: /api/tasks/{newId}
Response Body: Created task with ID
```

**Characteristics:**
- Not idempotent: Multiple calls create multiple resources
- Returns 201 Created with Location header
- Response body contains created resource

### PUT - Full Update

```
PUT /api/tasks/{id}
Request Body: Complete task object
Response: 200 OK, updated task
Response: 404 Not Found (if doesn't exist)
```

**Characteristics:**
- Idempotent: Multiple calls have same effect
- Replaces entire resource
- All fields must be provided

### PATCH - Partial Update

```
PATCH /api/tasks/{id}
Request Body: { "completed": true }
Response: 200 OK, updated task
Response: 404 Not Found (if doesn't exist)
```

**Characteristics:**
- Not strictly idempotent (depends on implementation)
- Updates only specified fields
- More flexible than PUT

### DELETE - Remove Resources

```
DELETE /api/tasks/{id}
Response: 204 No Content
Response: 404 Not Found (if doesn't exist)
```

**Characteristics:**
- Idempotent: Multiple calls have same effect
- Returns 204 No Content (no body)
- Or 200 OK with deleted resource in body

---

## URL Structure

### Base URL

```
https://api.example.com/v1
```

Components:
- Protocol: `https://` (always use HTTPS)
- Domain: `api.example.com` (subdomain for API)
- Version: `/v1` (API version)

### Resource Paths

```
/api/tasks                    # Collection
/api/tasks/{id}               # Single resource
/api/tasks/{id}/comments      # Nested collection
/api/tasks/{id}/comments/{id} # Nested resource
```

### Query Parameters

Use for filtering, sorting, pagination:

```
# Filtering
/api/tasks?status=completed
/api/tasks?priority=high&status=active

# Sorting
/api/tasks?sort_by=created_at&order=desc

# Pagination
/api/tasks?page=2&page_size=20

# Search
/api/tasks?search=documentation

# Combined
/api/tasks?status=active&sort_by=due_date&order=asc&page=1
```

**Guidelines:**
- Use snake_case for parameter names
- Support multiple filters
- Document all supported parameters
- Validate parameter values

---

## Request/Response Format

### Content Type

Always use JSON:

```
Request Headers:
  Content-Type: application/json

Response Headers:
  Content-Type: application/json
```

### Field Naming

**Choose one convention and stick to it:**

**snake_case (Python, Ruby):**
```json
{
  "task_id": "123",
  "created_at": "2026-02-01T10:00:00Z",
  "is_completed": false
}
```

**camelCase (JavaScript):**
```json
{
  "taskId": "123",
  "createdAt": "2026-02-01T10:00:00Z",
  "isCompleted": false
}
```

### Date/Time Format

Use ISO 8601:

```json
{
  "created_at": "2026-02-01T10:00:00Z",
  "due_date": "2026-02-15T14:30:00+00:00"
}
```

### Null vs Omission

**Be consistent:**

```json
// Option 1: Include null fields
{
  "title": "Task",
  "description": null,
  "due_date": null
}

// Option 2: Omit null fields
{
  "title": "Task"
}
```

### Response Envelopes

**Option 1: No envelope (preferred for simple APIs):**
```json
GET /api/tasks
[
  { "id": "1", "title": "Task 1" },
  { "id": "2", "title": "Task 2" }
]
```

**Option 2: With envelope (for metadata):**
```json
GET /api/tasks
{
  "data": [
    { "id": "1", "title": "Task 1" },
    { "id": "2", "title": "Task 2" }
  ],
  "meta": {
    "total": 150,
    "page": 1,
    "page_size": 20
  }
}
```

---

## Status Codes

### Success Codes (2xx)

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 OK | Success | GET, PUT, PATCH successful |
| 201 Created | Resource created | POST successful |
| 204 No Content | Success, no body | DELETE successful |

### Client Error Codes (4xx)

| Code | Meaning | Use Case |
|------|---------|----------|
| 400 Bad Request | Invalid input | Malformed JSON, invalid data |
| 401 Unauthorized | Auth required | Missing/invalid token |
| 403 Forbidden | No permission | Valid token, insufficient rights |
| 404 Not Found | Resource missing | Resource doesn't exist |
| 409 Conflict | Resource conflict | Duplicate resource |
| 422 Unprocessable Entity | Validation failed | Valid JSON, failed validation |
| 429 Too Many Requests | Rate limit | Too many requests |

### Server Error Codes (5xx)

| Code | Meaning | Use Case |
|------|---------|----------|
| 500 Internal Server Error | Server error | Unexpected error |
| 502 Bad Gateway | Upstream error | Proxy/gateway error |
| 503 Service Unavailable | Service down | Maintenance, overload |

### Examples

```
# Success
GET /api/tasks/123
200 OK
{ "id": "123", "title": "Task" }

# Created
POST /api/tasks
201 Created
Location: /api/tasks/456
{ "id": "456", "title": "New Task" }

# No Content
DELETE /api/tasks/123
204 No Content

# Not Found
GET /api/tasks/999
404 Not Found
{ "error": { "code": "NOT_FOUND", "message": "Task not found" } }

# Validation Error
POST /api/tasks
422 Unprocessable Entity
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": {
      "title": "Title is required"
    }
  }
}
```

---

## Versioning

### URL Versioning (Recommended)

```
https://api.example.com/v1/tasks
https://api.example.com/v2/tasks
```

**Pros:**
- Clear and explicit
- Easy to route
- Easy to test different versions

**Cons:**
- URL changes between versions

### Header Versioning

```
GET /api/tasks
Accept: application/vnd.example.v1+json
```

**Pros:**
- Clean URLs
- RESTful purists prefer

**Cons:**
- Less visible
- Harder to test

### When to Version

Create new version when:
- Breaking changes to existing endpoints
- Removing fields from responses
- Changing field types
- Changing authentication

Don't version for:
- Adding new endpoints
- Adding optional fields to requests
- Adding fields to responses (non-breaking)

---

## HATEOAS

Hypermedia As The Engine Of Application State - include links in responses.

### Basic Example

```json
GET /api/tasks/123
{
  "id": "123",
  "title": "Task",
  "completed": false,
  "_links": {
    "self": { "href": "/api/tasks/123" },
    "comments": { "href": "/api/tasks/123/comments" },
    "complete": { "href": "/api/tasks/123/complete", "method": "POST" },
    "delete": { "href": "/api/tasks/123", "method": "DELETE" }
  }
}
```

### Benefits

- Self-documenting API
- Clients discover available actions
- Server controls navigation
- Easier to evolve API

### Drawbacks

- More complex responses
- Larger payload size
- Not always necessary for simple APIs

---

## Best Practices Summary

1. **Use nouns, not verbs** in URLs
2. **Use plural resource names** (/tasks not /task)
3. **Use HTTP methods correctly** (GET, POST, PUT, PATCH, DELETE)
4. **Return appropriate status codes** (200, 201, 404, etc.)
5. **Use JSON** for request/response
6. **Be consistent** with naming conventions
7. **Version your API** when making breaking changes
8. **Document everything** with OpenAPI
9. **Use HTTPS** always
10. **Implement pagination** for collections
11. **Support filtering and sorting** via query params
12. **Handle errors gracefully** with standard format
13. **Use authentication** (JWT, OAuth)
14. **Rate limit** to prevent abuse
15. **Test thoroughly** all endpoints

---

## Anti-Patterns to Avoid

❌ **Verbs in URLs:**
```
/api/getTasks
/api/createTask
```

❌ **Non-standard HTTP methods:**
```
POST /api/tasks/delete
GET /api/tasks/create
```

❌ **Inconsistent naming:**
```
/api/tasks
/api/user
/api/Comments
```

❌ **Exposing implementation details:**
```
/api/tasks.php
/api/tasks?action=delete
```

❌ **Ignoring status codes:**
```
200 OK
{ "error": "Task not found" }
```

❌ **Inconsistent error format:**
```
{ "error": "Not found" }
{ "message": "Invalid input" }
{ "err": { "msg": "Server error" } }
```

---

## Resources

- [REST API Tutorial](https://restfulapi.net/)
- [HTTP Status Codes](https://httpstatuses.com/)
- [JSON API Specification](https://jsonapi.org/)
- [OpenAPI Specification](https://swagger.io/specification/)
