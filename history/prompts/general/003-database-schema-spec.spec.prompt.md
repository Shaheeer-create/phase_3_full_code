---
id: 003
title: Database Schema Spec
stage: spec
date: 2026-01-31
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: Shaheer Naeem
command: none
labels: ["database", "schema", "postgresql", "data-model"]
links:
  spec: specs/database/schema.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/database/schema.md
tests:
  - none
---

## Prompt

Define the database schema for the Todo App including users (managed by Better Auth), tasks table with user_id foreign key, and Phase III tables for conversations and messages. Include all fields, types, constraints, and indexes.

## Response snapshot

Created database schema specification with 4 tables:

**users** (Better Auth managed):
- id (string, PK, UUID), email (unique), name (nullable), created_at

**tasks** (Phase II):
- id (integer, PK, auto-increment), user_id (FK → users.id, indexed), title (max 200 chars), description (max 1000 chars, nullable), completed (boolean, default false), created_at, updated_at

**conversations** (Phase III):
- id, user_id (FK, indexed), created_at, updated_at

**messages** (Phase III):
- id, conversation_id (FK, indexed), user_id (FK), role (enum: user/assistant/tool), content, tool_calls (JSON, nullable), created_at

**Indexes:**
- tasks.user_id (critical for user filtering)
- tasks.completed (for status filtering)
- messages.conversation_id (for chat history retrieval)

## Outcome

- ✅ Impact: Established complete data model for Phase II and Phase III with proper foreign keys and indexes
- 🧪 Tests: None (specification document)
- 📁 Files: Created specs/database/schema.md
- 🔁 Next prompts: Create SQLModel models, write migration scripts, implement user_id filtering
- 🧠 Reflection: User_id indexing on tasks table is critical for performance with multi-user filtering

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add composite indexes for common query patterns (user_id + completed)
