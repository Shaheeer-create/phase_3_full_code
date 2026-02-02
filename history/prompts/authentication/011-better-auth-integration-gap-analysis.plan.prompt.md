---
id: 011
title: Better Auth integration gap analysis
stage: plan
date: 2026-02-01
surface: agent
model: Claude Sonnet 4.5
feature: authentication
branch: master
user: user
command: none
labels: ["authentication", "better-auth", "gap-analysis", "architecture"]
links:
  spec: specs/features/authentication.md
  ticket: null
  adr: null
  pr: null
files:
  - path: frontend/components/AuthForm.tsx
    action: read
  - path: frontend/lib/auth.ts
    action: read
  - path: backend/dependencies.py
    action: read
  - path: specs/database/schema.md
    action: read
  - path: specs/architecture.md
    action: read
  - path: backend/database.py
    action: read
  - path: history/prompts/authentication/011-better-auth-integration-gap-analysis.plan.prompt.md
    action: created
tests: []
---

## Prompt

Continue

(User continued requesting exploration after initial status summary)

## Response snapshot

Identified critical missing component in authentication flow:

**Problem:** Frontend calls Better Auth methods (`authClient.signUp.email()`, `authClient.signIn.email()`) but there's no Better Auth server to handle these requests.

**Current State:**
- Frontend: Better Auth client configured, calls signup/login methods
- Backend: JWT validation working, expects tokens from Better Auth
- Missing: Better Auth server endpoints to create users and issue JWT tokens

**Root Cause:** Better Auth requires server-side setup. In Next.js + FastAPI architecture, Better Auth server should run as Next.js API routes (`/app/api/auth/[...all]/route.ts`).

**Required Components:**
1. Better Auth server configuration (`frontend/lib/auth-server.ts`)
2. API route handler (`frontend/app/api/auth/[...all]/route.ts`)
3. Database adapter (connect Better Auth to Neon PostgreSQL)

**Proposed Flow:**
User → AuthForm → authClient.signUp.email() → POST /api/auth/sign-up (Next.js) → Better Auth creates user + JWT → JWT in cookie → FastAPI validates JWT

**Options Presented:**
1. Implement Better Auth server setup (recommended)
2. Switch to simpler custom FastAPI auth
3. Review detailed implementation plan first

## Outcome

- ✅ Impact: Identified root cause of authentication gap - Better Auth server not configured
- 🧪 Tests: None
- 📁 Files: Read 6 files, created PHR 011
- 🔁 Next prompts: User to choose implementation approach (Better Auth setup, custom auth, or plan review)
- 🧠 Reflection: Deep analysis revealed architectural mismatch - frontend expects Better Auth server at Next.js API routes but no such routes exist. This is blocking all authentication functionality.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
