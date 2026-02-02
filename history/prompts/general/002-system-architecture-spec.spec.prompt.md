---
id: 002
title: System Architecture Spec
stage: spec
date: 2026-01-31
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: Shaheer Naeem
command: none
labels: ["architecture", "auth-flow", "data-flow", "security"]
links:
  spec: specs/architecture.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/architecture.md
tests:
  - none
---

## Prompt

Document the system architecture for the Todo App, including high-level flow, authentication flow, data flow for CRUD operations, and security model with JWT and user data isolation.

## Response snapshot

Created system architecture specification documenting:
- High-Level Flow: User → Next.js Frontend → FastAPI Backend → Neon PostgreSQL with Better Auth JWT
- Authentication Flow: 6-step process from login through JWT validation and user_id extraction
- Data Flow: CRUD operations with JWT validation and user_id filtering at every step
- Security Model: Shared BETTER_AUTH_SECRET, 7-day token expiry, CORS configuration, application-level row security via user_id checks

Key architectural decisions:
- Stateless backend with JWT-based authentication
- User data isolation enforced at application layer (not database RLS)
- Shared secret between frontend and backend for JWT validation

## Outcome

- ✅ Impact: Defined critical security and data flow patterns for entire application
- 🧪 Tests: None (specification document)
- 📁 Files: Created specs/architecture.md
- 🔁 Next prompts: Document database schema, API endpoints, implement JWT middleware
- 🧠 Reflection: Clear separation of concerns between auth (Better Auth) and data access (FastAPI with user_id filtering)

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Consider documenting error handling and retry strategies
