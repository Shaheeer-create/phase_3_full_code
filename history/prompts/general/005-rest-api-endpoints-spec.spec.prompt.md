---
id: 005
title: REST API Endpoints Spec
stage: spec
date: 2026-01-31
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: Shaheer Naeem
command: none
labels: ["api", "rest", "endpoints", "fastapi", "contracts"]
links:
  spec: specs/api/rest-endpoints.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/api/rest-endpoints.md
tests:
  - none
---

## Prompt

Document the REST API specification for the Todo App backend including all task endpoints (GET, POST, PUT, DELETE, PATCH), authentication requirements, request/response formats, query parameters, and error responses with status codes.

## Response snapshot

Created REST API specification with:

**Base URL:** localhost:8000 (dev), production TBD

**Authentication:** All endpoints require `Authorization: Bearer <jwt_token>` header

**Task Endpoints:**
- GET /api/tasks - List all user tasks with query params (status: all/pending/completed, sort: created/title/updated)
- POST /api/tasks - Create task (title required 1-200 chars, description optional max 1000 chars)
- GET /api/tasks/{id} - Get single task (404 if not found or not owned)
- PUT /api/tasks/{id} - Update task (title, description, completed all optional)
- DELETE /api/tasks/{id} - Delete task (204 no content)
- PATCH /api/tasks/{id}/complete - Toggle completion status

**Error Responses:**
- 401: Missing or invalid token
- 403: Token valid but user_id mismatch
- 404: Task not found
- 422: Validation error

All errors return JSON with "detail" field.

## Outcome

- ✅ Impact: Established complete API contract for frontend-backend integration
- 🧪 Tests: None (specification document)
- 📁 Files: Created specs/api/rest-endpoints.md
- 🔁 Next prompts: Implement FastAPI routes, create Pydantic schemas, write API integration tests
- 🧠 Reflection: Clear separation between 404 (not found) and 403 (unauthorized access) for security

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add pagination parameters for GET /api/tasks
