# OpenAPI Specification Guide

Complete guide to creating OpenAPI 3.0 specifications for REST APIs.

## Table of Contents
- OpenAPI Basics
- Document Structure
- Path Definitions
- Schema Definitions
- Authentication
- Examples and Documentation
- Tools and Validation

---

## OpenAPI Basics

### What is OpenAPI?

OpenAPI (formerly Swagger) is a specification for describing REST APIs in a machine-readable format.

**Benefits:**
- **Documentation**: Auto-generate interactive API docs
- **Client SDKs**: Generate client libraries in multiple languages
- **Server Stubs**: Generate server boilerplate code
- **Validation**: Validate requests/responses against spec
- **Testing**: Generate test cases from spec
- **Mocking**: Create mock servers for development

### OpenAPI 3.0 vs 2.0 (Swagger)

Use OpenAPI 3.0 (latest is 3.1):
- Better schema support (JSON Schema)
- Multiple servers
- Callbacks and webhooks
- Improved examples
- Better security definitions

---

## Document Structure

### Basic Template

```yaml
openapi: 3.0.0

info:
  title: Task Management API
  version: 1.0.0
  description: RESTful API for managing tasks
  contact:
    name: API Support
    email: support@example.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: http://localhost:8000
    description: Development server
  - url: https://api.example.com
    description: Production server

paths:
  # API endpoints

components:
  schemas:
    # Data models
  securitySchemes:
    # Authentication methods
  responses:
    # Reusable responses
  parameters:
    # Reusable parameters

security:
  # Global security requirements

tags:
  - name: Tasks
    description: Task management operations
  - name: Auth
    description: Authentication operations
```

### Info Object

```yaml
info:
  title: Task Management API
  version: 1.0.0
  description: |
    RESTful API for managing tasks with user authentication.

    ## Features
    - Create, read, update, delete tasks
    - User authentication with JWT
    - Task filtering and sorting
    - Pagination support

  termsOfService: https://example.com/terms
  contact:
    name: API Support
    email: support@example.com
    url: https://example.com/support
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT
```

### Servers

```yaml
servers:
  - url: http://localhost:8000
    description: Local development
  - url: https://staging-api.example.com
    description: Staging environment
  - url: https://api.example.com
    description: Production environment

  # With variables
  - url: https://{environment}.example.com/api/{version}
    description: Configurable server
    variables:
      environment:
        default: api
        enum:
          - api
          - staging
      version:
        default: v1
```

---

## Path Definitions

### Basic Endpoint

```yaml
paths:
  /api/tasks:
    get:
      summary: List tasks
      description: Retrieve a paginated list of tasks for the authenticated user
      operationId: listTasks
      tags:
        - Tasks
      parameters:
        - name: page
          in: query
          description: Page number (1-indexed)
          required: false
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: page_size
          in: query
          description: Number of items per page
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/TaskListResponse'
        '401':
          $ref: '#/components/responses/Unauthorized'
      security:
        - bearerAuth: []
```

### CRUD Operations

```yaml
paths:
  /api/tasks:
    get:
      summary: List tasks
      # ... (see above)

    post:
      summary: Create task
      description: Create a new task
      operationId: createTask
      tags:
        - Tasks
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateTaskRequest'
            examples:
              basic:
                summary: Basic task
                value:
                  title: Complete documentation
                  priority: medium
              withDueDate:
                summary: Task with due date
                value:
                  title: Review PR
                  priority: high
                  due_date: "2026-02-15T10:00:00Z"
      responses:
        '201':
          description: Task created
          headers:
            Location:
              description: URL of created task
              schema:
                type: string
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        '400':
          $ref: '#/components/responses/BadRequest'
        '422':
          $ref: '#/components/responses/ValidationError'
      security:
        - bearerAuth: []

  /api/tasks/{taskId}:
    parameters:
      - name: taskId
        in: path
        required: true
        description: Task ID
        schema:
          type: string
          format: uuid

    get:
      summary: Get task
      description: Retrieve a single task by ID
      operationId: getTask
      tags:
        - Tasks
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        '404':
          $ref: '#/components/responses/NotFound'
      security:
        - bearerAuth: []

    patch:
      summary: Update task
      description: Partially update a task
      operationId: updateTask
      tags:
        - Tasks
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateTaskRequest'
      responses:
        '200':
          description: Task updated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        '404':
          $ref: '#/components/responses/NotFound'
        '422':
          $ref: '#/components/responses/ValidationError'
      security:
        - bearerAuth: []

    delete:
      summary: Delete task
      description: Delete a task
      operationId: deleteTask
      tags:
        - Tasks
      responses:
        '204':
          description: Task deleted
        '404':
          $ref: '#/components/responses/NotFound'
      security:
        - bearerAuth: []
```

---

## Schema Definitions

### Basic Schema

```yaml
components:
  schemas:
    Task:
      type: object
      required:
        - id
        - title
        - completed
        - created_at
        - updated_at
        - user_id
      properties:
        id:
          type: string
          format: uuid
          description: Unique task identifier
          example: "550e8400-e29b-41d4-a716-446655440000"
        title:
          type: string
          minLength: 1
          maxLength: 100
          description: Task title
          example: "Complete project documentation"
        description:
          type: string
          maxLength: 500
          nullable: true
          description: Task description
          example: "Write comprehensive API documentation"
        priority:
          type: string
          enum: [low, medium, high]
          default: medium
          description: Task priority
          example: "high"
        completed:
          type: boolean
          description: Whether task is completed
          example: false
        due_date:
          type: string
          format: date-time
          nullable: true
          description: Task due date (ISO 8601)
          example: "2026-02-15T10:00:00Z"
        tags:
          type: array
          items:
            type: string
            maxLength: 20
          description: Task tags
          example: ["documentation", "urgent"]
        created_at:
          type: string
          format: date-time
          description: Creation timestamp
          example: "2026-02-01T09:00:00Z"
        updated_at:
          type: string
          format: date-time
          description: Last update timestamp
          example: "2026-02-01T09:00:00Z"
        user_id:
          type: string
          format: uuid
          description: Owner user ID
          example: "123e4567-e89b-12d3-a456-426614174000"
```

### Request Schemas

```yaml
components:
  schemas:
    CreateTaskRequest:
      type: object
      required:
        - title
      properties:
        title:
          type: string
          minLength: 1
          maxLength: 100
          example: "Complete documentation"
        description:
          type: string
          maxLength: 500
          example: "Write API docs"
        priority:
          type: string
          enum: [low, medium, high]
          default: medium
        due_date:
          type: string
          format: date-time
          example: "2026-02-15T10:00:00Z"
        tags:
          type: array
          items:
            type: string

    UpdateTaskRequest:
      type: object
      properties:
        title:
          type: string
          minLength: 1
          maxLength: 100
        description:
          type: string
          maxLength: 500
        priority:
          type: string
          enum: [low, medium, high]
        completed:
          type: boolean
        due_date:
          type: string
          format: date-time
        tags:
          type: array
          items:
            type: string
```

### Response Schemas

```yaml
components:
  schemas:
    TaskListResponse:
      type: object
      required:
        - items
        - pagination
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/Task'
        pagination:
          type: object
          required:
            - total
            - page
            - page_size
            - total_pages
          properties:
            total:
              type: integer
              description: Total number of tasks
              example: 150
            page:
              type: integer
              description: Current page number
              example: 1
            page_size:
              type: integer
              description: Items per page
              example: 20
            total_pages:
              type: integer
              description: Total number of pages
              example: 8
            has_previous:
              type: boolean
              example: false
            has_next:
              type: boolean
              example: true
```

### Error Schemas

```yaml
components:
  schemas:
    Error:
      type: object
      required:
        - error
      properties:
        error:
          type: object
          required:
            - code
            - message
          properties:
            code:
              type: string
              description: Machine-readable error code
              example: "NOT_FOUND"
            message:
              type: string
              description: Human-readable error message
              example: "Task not found"
            details:
              type: object
              description: Additional error details
              additionalProperties: true

    ValidationError:
      type: object
      required:
        - error
      properties:
        error:
          type: object
          required:
            - code
            - message
            - details
          properties:
            code:
              type: string
              example: "VALIDATION_ERROR"
            message:
              type: string
              example: "Validation failed"
            details:
              type: object
              additionalProperties:
                type: string
              example:
                title: "Title is required"
                due_date: "Due date must be in the future"
```

---

## Authentication

### Bearer Token (JWT)

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        JWT token obtained from /api/auth/login endpoint.
        Include in Authorization header: `Bearer <token>`

# Apply globally
security:
  - bearerAuth: []

# Or per endpoint
paths:
  /api/tasks:
    get:
      security:
        - bearerAuth: []
```

### API Key

```yaml
components:
  securitySchemes:
    apiKey:
      type: apiKey
      in: header
      name: X-API-Key
      description: API key for authentication
```

### OAuth 2.0

```yaml
components:
  securitySchemes:
    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://example.com/oauth/authorize
          tokenUrl: https://example.com/oauth/token
          scopes:
            read:tasks: Read tasks
            write:tasks: Create and update tasks
            delete:tasks: Delete tasks
```

---

## Reusable Components

### Responses

```yaml
components:
  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          example:
            error:
              code: "UNAUTHORIZED"
              message: "Authentication required"

    Forbidden:
      description: Insufficient permissions
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'

    ValidationError:
      description: Validation failed
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ValidationError'

    BadRequest:
      description: Invalid request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
```

### Parameters

```yaml
components:
  parameters:
    PageParam:
      name: page
      in: query
      description: Page number
      schema:
        type: integer
        minimum: 1
        default: 1

    PageSizeParam:
      name: page_size
      in: query
      description: Items per page
      schema:
        type: integer
        minimum: 1
        maximum: 100
        default: 20

    TaskIdParam:
      name: taskId
      in: path
      required: true
      description: Task ID
      schema:
        type: string
        format: uuid

# Use in paths
paths:
  /api/tasks:
    get:
      parameters:
        - $ref: '#/components/parameters/PageParam'
        - $ref: '#/components/parameters/PageSizeParam'
```

---

## Tools and Validation

### Swagger UI

Interactive API documentation:

```bash
# Install
pip install fastapi[all]

# FastAPI automatically serves Swagger UI at /docs
```

### Redoc

Alternative documentation UI:

```bash
# FastAPI serves Redoc at /redoc
```

### Validation Tools

**Swagger Editor**: https://editor.swagger.io/
- Online editor with validation
- Real-time error checking

**OpenAPI Generator**: https://openapi-generator.tech/
- Generate client SDKs
- Generate server stubs
- Multiple languages supported

**Spectral**: https://stoplight.io/open-source/spectral
- Linting and validation
- Custom rules

### Generate from Code

**FastAPI** (Python):
```python
from fastapi import FastAPI

app = FastAPI(
    title="Task Management API",
    version="1.0.0",
    description="RESTful API for managing tasks"
)

# OpenAPI spec auto-generated at /openapi.json
```

---

## Best Practices

1. **Use $ref for reusability**: Define schemas once, reference everywhere
2. **Provide examples**: Help users understand expected format
3. **Document all fields**: Clear descriptions for every property
4. **Use tags**: Organize endpoints into logical groups
5. **Version your API**: Include version in URL or header
6. **Validate spec**: Use tools to catch errors
7. **Keep it updated**: Spec should match implementation
8. **Use operationId**: Unique identifier for each operation
9. **Document errors**: All possible error responses
10. **Security first**: Document authentication requirements

---

## Complete Example

See the full example in the API Designer skill's output files.

---

## Resources

- [OpenAPI Specification](https://swagger.io/specification/)
- [Swagger Editor](https://editor.swagger.io/)
- [OpenAPI Generator](https://openapi-generator.tech/)
- [FastAPI OpenAPI](https://fastapi.tiangolo.com/tutorial/metadata/)
