---
name: sp.api-designer
description: Design REST API endpoints, request/response schemas, and OpenAPI specifications. Use when the user needs to: (1) Design API endpoints for features, (2) Define request/response schemas, (3) Create OpenAPI/Swagger documentation, (4) Design authentication flows, (5) Define error responses and status codes, (6) Design pagination, filtering, and sorting, or (7) Document API contracts. Should be run after feature specs exist and before backend implementation.
---

# API Designer

Design production-ready REST API endpoints with comprehensive request/response schemas and OpenAPI documentation.

## Workflow

### 1. Gather Context

Read existing specifications:
- `specs/features/<feature-name>.md` - Feature requirements (REQUIRED)
- `specs/architecture.md` - Tech stack, auth strategy, constraints
- `specs/database/schema.md` - Database models and relationships
- `specs/api/rest-endpoints.md` - Existing API contracts (if any)
- Project CLAUDE.md - API conventions and standards

Extract:
- Required CRUD operations
- Data models and relationships
- Authentication requirements
- Business logic and validation rules
- User permissions and access control

### 2. Design API Endpoints

Create RESTful endpoints following best practices. See [references/rest-api-design.md](references/rest-api-design.md) for detailed principles.

#### Resource-Based Design

```
Resource: Tasks

GET    /api/tasks           - List tasks (with filtering, pagination)
POST   /api/tasks           - Create task
GET    /api/tasks/{id}      - Get single task
PUT    /api/tasks/{id}      - Update task (full)
PATCH  /api/tasks/{id}      - Update task (partial)
DELETE /api/tasks/{id}      - Delete task

Nested resources:
GET    /api/tasks/{id}/comments     - List task comments
POST   /api/tasks/{id}/comments     - Create comment on task
```

#### Endpoint Naming Conventions

- Use plural nouns for resources: `/tasks` not `/task`
- Use kebab-case for multi-word resources: `/task-templates`
- Avoid verbs in URLs: `/tasks` not `/getTasks`
- Use nested routes for relationships: `/tasks/{id}/comments`
- Use query parameters for filtering: `/tasks?status=completed`

### 3. Define Request Schemas

Specify request body schemas for POST, PUT, PATCH operations.

```yaml
# POST /api/tasks
Request Body:
  title: string (required, 1-100 chars)
  description: string (optional, max 500 chars)
  priority: enum ["low", "medium", "high"] (optional, default: "medium")
  due_date: datetime (optional, ISO 8601 format)
  tags: array[string] (optional)

Example:
{
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs",
  "priority": "high",
  "due_date": "2026-02-15T10:00:00Z",
  "tags": ["documentation", "urgent"]
}

Validation Rules:
- title: Required, non-empty, max 100 characters
- description: Optional, max 500 characters
- priority: Must be one of: low, medium, high
- due_date: Must be valid ISO 8601 datetime, must be in future
- tags: Optional array, each tag max 20 characters
```

### 4. Define Response Schemas

Specify response schemas for all endpoints.

```yaml
# GET /api/tasks/{id}
Response (200 OK):
{
  "id": "uuid",
  "title": "string",
  "description": "string | null",
  "priority": "low" | "medium" | "high",
  "completed": boolean,
  "due_date": "datetime | null",
  "tags": ["string"],
  "created_at": "datetime",
  "updated_at": "datetime",
  "user_id": "uuid"
}

Example:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs",
  "priority": "high",
  "completed": false,
  "due_date": "2026-02-15T10:00:00Z",
  "tags": ["documentation", "urgent"],
  "created_at": "2026-02-01T09:00:00Z",
  "updated_at": "2026-02-01T09:00:00Z",
  "user_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 5. Design Pagination and Filtering

Implement consistent pagination and filtering patterns. See [references/pagination-patterns.md](references/pagination-patterns.md) for detailed strategies.

#### Pagination

```yaml
# Offset-based pagination
GET /api/tasks?page=1&page_size=20

Response:
{
  "items": [Task],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}

# Cursor-based pagination (for real-time data)
GET /api/tasks?cursor=abc123&limit=20

Response:
{
  "items": [Task],
  "next_cursor": "def456",
  "has_more": true
}
```

#### Filtering and Sorting

```yaml
# Filtering
GET /api/tasks?status=completed&priority=high&tags=urgent

# Sorting
GET /api/tasks?sort_by=created_at&order=desc

# Combined
GET /api/tasks?status=active&sort_by=due_date&order=asc&page=1&page_size=20
```

### 6. Define Error Responses

Standardize error responses across all endpoints. See [references/error-handling.md](references/error-handling.md) for comprehensive patterns.

```yaml
Error Response Format:
{
  "error": {
    "code": "string",
    "message": "string",
    "details": object (optional)
  }
}

Common Status Codes:
- 200 OK: Successful GET, PUT, PATCH
- 201 Created: Successful POST
- 204 No Content: Successful DELETE
- 400 Bad Request: Invalid input
- 401 Unauthorized: Missing or invalid auth token
- 403 Forbidden: Insufficient permissions
- 404 Not Found: Resource doesn't exist
- 409 Conflict: Resource conflict (e.g., duplicate)
- 422 Unprocessable Entity: Validation errors
- 500 Internal Server Error: Server error

Examples:

# 400 Bad Request
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Invalid request data",
    "details": {
      "title": "Title is required",
      "due_date": "Due date must be in the future"
    }
  }
}

# 401 Unauthorized
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required"
  }
}

# 404 Not Found
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Task not found"
  }
}
```

### 7. Design Authentication

Specify authentication requirements for each endpoint.

```yaml
Authentication: Bearer JWT Token

Header:
  Authorization: Bearer <token>

Protected Endpoints:
  All /api/tasks/* endpoints require authentication

Public Endpoints:
  POST /api/auth/register
  POST /api/auth/login

Token Payload:
{
  "user_id": "uuid",
  "email": "string",
  "exp": timestamp
}

User Isolation:
  All queries filtered by user_id from JWT token
  Users can only access their own resources
```

### 8. Create OpenAPI Specification

Generate OpenAPI 3.0 specification for API documentation. See [references/openapi-spec.md](references/openapi-spec.md) for complete guide.

```yaml
openapi: 3.0.0
info:
  title: Task Management API
  version: 1.0.0
  description: RESTful API for task management

servers:
  - url: http://localhost:8000
    description: Development server
  - url: https://api.example.com
    description: Production server

paths:
  /api/tasks:
    get:
      summary: List tasks
      tags: [Tasks]
      security:
        - bearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: page_size
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TaskListResponse'

    post:
      summary: Create task
      tags: [Tasks]
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateTaskRequest'
      responses:
        '201':
          description: Task created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    Task:
      type: object
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
        # ... more properties
```

### 9. Create Output Files

Generate API specification files:

**Endpoint Documentation**: `specs/api/<feature-name>-endpoints.md`
- List of all endpoints
- Request/response schemas
- Authentication requirements
- Error responses
- Examples

**OpenAPI Spec**: `specs/api/openapi.yaml`
- Complete OpenAPI 3.0 specification
- Can be used with Swagger UI
- Can generate client SDKs

**API Contracts**: `specs/api/rest-endpoints.md` (update)
- Consolidated API documentation
- All endpoints across features
- Shared schemas and patterns

### 10. Integration with Workflow

**Before running this skill**:
- Feature specs exist (`/sp.specify` completed)
- Database schema defined (optional but helpful)
- Architecture documented

**After running this skill**:
- Run `/sp.backend-engineer` to implement endpoints
- Run `/sp.frontend-integrator` to connect frontend to API
- API contracts ready for frontend/backend teams

**PHR Creation**:
- Create PHR in `history/prompts/<feature-name>/`
- Stage: `spec` (API design is part of specification phase)
- Include links to created API spec files

**ADR Suggestions**:
Suggest ADR for significant API design decisions:
- REST vs GraphQL
- Pagination strategy (offset vs cursor)
- Authentication method (JWT vs session)
- API versioning strategy
- Rate limiting approach

Example: "📋 Architectural decision detected: Using cursor-based pagination for real-time task updates. Document reasoning? Run `/sp.adr cursor-pagination`"

## Usage Examples

Basic usage:
```
/sp.api-designer task-crud
```

Specific feature:
```
/sp.api-designer authentication
```

With OpenAPI generation:
```
/sp.api-designer task-crud --openapi
```

## Success Criteria

- [ ] All CRUD endpoints defined
- [ ] Request schemas specified with validation rules
- [ ] Response schemas documented with examples
- [ ] Pagination and filtering designed
- [ ] Error responses standardized
- [ ] Authentication requirements specified
- [ ] OpenAPI specification generated
- [ ] Examples provided for all endpoints
- [ ] PHR created
- [ ] ADR suggested for significant decisions

## API Design Checklist

**Endpoints**:
- [ ] Follow RESTful conventions
- [ ] Use plural nouns for resources
- [ ] Consistent naming (kebab-case)
- [ ] Proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
- [ ] Nested routes for relationships

**Request/Response**:
- [ ] JSON format
- [ ] Consistent field naming (snake_case or camelCase)
- [ ] Required vs optional fields documented
- [ ] Validation rules specified
- [ ] Examples provided

**Pagination**:
- [ ] Consistent pagination pattern
- [ ] Total count included
- [ ] Page size limits enforced

**Filtering/Sorting**:
- [ ] Query parameters documented
- [ ] Supported filters listed
- [ ] Sort fields specified

**Authentication**:
- [ ] Auth method specified (JWT, OAuth, etc.)
- [ ] Protected endpoints marked
- [ ] Token format documented
- [ ] User isolation enforced

**Error Handling**:
- [ ] Standard error format
- [ ] Appropriate status codes
- [ ] Error codes defined
- [ ] Validation errors detailed

**Documentation**:
- [ ] OpenAPI spec generated
- [ ] Examples for all endpoints
- [ ] Authentication flow documented
- [ ] Rate limits specified (if any)

## References

- [REST API Design Principles](references/rest-api-design.md) - RESTful conventions and best practices
- [Pagination Patterns](references/pagination-patterns.md) - Offset vs cursor pagination strategies
- [Error Handling](references/error-handling.md) - Standard error responses and status codes
- [OpenAPI Specification](references/openapi-spec.md) - Complete OpenAPI 3.0 guide
