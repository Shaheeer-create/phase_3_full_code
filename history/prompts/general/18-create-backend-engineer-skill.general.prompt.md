---
id: 18
title: Create Backend Engineer Skill
stage: misc
date: 2026-02-01
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: user
command: yes make backend skills
labels: ["skill-creation", "backend", "fastapi", "sqlmodel", "authentication"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - path: .claude/skills/sp.backend-engineer/SKILL.md
    status: created
  - path: .claude/skills/sp.backend-engineer/references/sqlmodel-patterns.md
    status: created
  - path: .claude/skills/sp.backend-engineer/references/pydantic-validation.md
    status: created
  - path: .claude/skills/sp.backend-engineer/references/fastapi-patterns.md
    status: created
  - path: .claude/skills/sp.backend-engineer/references/auth-patterns.md
    status: created
  - path: .claude/skills/sp.backend-engineer.skill
    status: created
tests:
  - name: none
    status: not_applicable
---

## Prompt

yes make backend skills

## Response snapshot

Created the `sp.backend-engineer` skill for implementing FastAPI endpoints with SQLModel and authentication:

**Skill Structure:**
- SKILL.md - 10-step workflow for backend implementation (20KB)
- references/sqlmodel-patterns.md - Database models and relationships (14KB)
- references/pydantic-validation.md - Request validation patterns (12KB)
- references/fastapi-patterns.md - Endpoint implementation patterns (10KB)
- references/auth-patterns.md - JWT authentication and authorization (15KB)
- sp.backend-engineer.skill - Packaged distributable (19KB)

**Workflow Steps:**
1. Gather context from API contracts and database schema
2. Setup project structure (models, schemas, routers, services)
3. Create database models with SQLModel
4. Create request/response schemas with Pydantic
5. Implement authentication (JWT token generation/verification)
6. Implement API endpoints (CRUD operations)
7. Implement error handling (global exception handlers)
8. Setup database connection and session management
9. Create output files (models, schemas, routers, utils)
10. Integration with Spec-Kit workflow

**Key Features:**
- FastAPI endpoint implementation
- SQLModel for database ORM
- Pydantic for request validation
- JWT authentication with Bearer tokens
- User data isolation enforcement
- CRUD operations with pagination
- Error handling with standard format
- Database session management
- Dependency injection patterns
- Background tasks support

**Reference Files:**
- **sqlmodel-patterns.md**: Table models, relationships (one-to-many, many-to-many, self-referential), indexes, constraints, query patterns, CRUD operations, best practices
- **pydantic-validation.md**: Field validation, model validators, custom validators, nested models, error handling, advanced patterns
- **fastapi-patterns.md**: Endpoint basics, dependency injection, response models, error handling, middleware, background tasks, router organization
- **auth-patterns.md**: JWT basics, token generation/verification, protected routes, user isolation, login/registration endpoints, password hashing, refresh tokens, RBAC

**Implementation Patterns:**
- Database models with SQLModel (table=True)
- Request/response schemas with Pydantic
- JWT authentication with python-jose
- Password hashing with passlib
- User isolation in all queries
- Pagination with offset/limit
- Error responses with standard format
- Dependency injection for session and auth

## Outcome

- ✅ Impact: New skill enables systematic backend implementation with FastAPI, SQLModel, and JWT authentication, ensuring secure and consistent API endpoints
- 🧪 Tests: Not applicable (skill creation)
- 📁 Files: Created 6 files (SKILL.md, 4 reference files, packaged .skill file)
- 🔁 Next prompts: Test skill with `/sp.backend-engineer <feature-name>`, integrate into workflow after API contracts are designed
- 🧠 Reflection: Skill provides comprehensive backend implementation guidance covering FastAPI patterns, SQLModel ORM, Pydantic validation, and JWT authentication. Progressive disclosure keeps SKILL.md focused on workflow while detailed patterns are in reference files. Complements sp.api-designer by implementing the designed API contracts with proper authentication and user isolation.

## Evaluation notes (flywheel)

- Failure modes observed: None - skill creation completed successfully
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): Test skill on actual feature to implement API endpoints, validate completeness of patterns and authentication implementation
