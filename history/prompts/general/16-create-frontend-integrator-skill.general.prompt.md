---
id: 16
title: Create Frontend Integrator Skill
stage: misc
date: 2026-02-01
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: user
command: create a skill for Frontend Integrator
labels: ["skill-creation", "frontend", "api-integration", "react-query", "hooks"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - path: .claude/skills/sp.frontend-integrator/SKILL.md
    status: created
  - path: .claude/skills/sp.frontend-integrator/references/data-fetching-strategies.md
    status: created
  - path: .claude/skills/sp.frontend-integrator/references/hook-patterns.md
    status: created
  - path: .claude/skills/sp.frontend-integrator/references/state-patterns.md
    status: created
  - path: .claude/skills/sp.frontend-integrator/references/form-patterns.md
    status: created
  - path: .claude/skills/sp.frontend-integrator.skill
    status: created
tests:
  - name: none
    status: not_applicable
---

## Prompt

create a skill for Skill 3: Frontend Integrator

Role:

Wires UI to real data

Connects API → components

Handles loading, error, empty states

Output:

Hooks

Data bindings

Real interactive UI

## Response snapshot

Created the `sp.frontend-integrator` skill with comprehensive API integration and data binding workflows:

**Skill Structure:**
- SKILL.md - 9-step workflow for wiring UI to APIs (17KB)
- references/data-fetching-strategies.md - Comparison of React Query, SWR, custom hooks, Server Components (15KB)
- references/hook-patterns.md - Query and mutation hook patterns with React Query (16KB)
- references/state-patterns.md - Loading, error, empty state patterns (14KB)
- references/form-patterns.md - Form handling with React Hook Form and Zod (13KB)
- sp.frontend-integrator.skill - Packaged distributable (23KB)

**Workflow Steps:**
1. Gather context from API specs and components
2. Choose data fetching strategy (React Query, SWR, custom hooks, Server Components)
3. Setup data fetching infrastructure (QueryClient, API client)
4. Create data fetching hooks (queries and mutations)
5. Implement state patterns (loading, error, empty)
6. Handle forms and mutations (React Hook Form, Zod validation)
7. Implement optimistic updates
8. Create output files (hooks/, lib/api-client.ts, types/)
9. Integration with Spec-Kit workflow

**Key Features:**
- React Query / TanStack Query integration
- SWR integration patterns
- Custom hooks with native fetch
- Next.js Server Components patterns
- Comprehensive hook patterns (queries, mutations, pagination, infinite scroll)
- State management (loading, error, empty states)
- Form handling with React Hook Form and Zod
- Optimistic updates and cache invalidation
- Error handling strategies
- TypeScript type safety throughout

**Reference Files:**
- **data-fetching-strategies.md**: Comparison matrix of React Query, SWR, custom hooks, Server Components with decision guide
- **hook-patterns.md**: Query hooks, mutation hooks, advanced patterns (pagination, infinite scroll, parallel queries), error handling, type safety, testing
- **state-patterns.md**: Loading states (inline, skeleton, progressive, Suspense), error states (inline, retry, boundaries, toasts), empty states (basic, with action, search results)
- **form-patterns.md**: React Hook Form basics, Zod validation, form submission, field-level validation, complex forms (nested, arrays), file uploads, multi-step forms

**Integration Patterns:**
- CRUD operations with custom hooks
- Pagination and infinite scroll
- Real-time updates with polling
- File uploads with preview
- Multi-step forms with validation
- Optimistic updates with rollback
- Server-side validation errors

## Outcome

- ✅ Impact: New skill enables systematic API integration and data binding, connecting UI components to real backend data with proper state management
- 🧪 Tests: Not applicable (skill creation)
- 📁 Files: Created 6 files (SKILL.md, 4 reference files, packaged .skill file)
- 🔁 Next prompts: Test skill with `/sp.frontend-integrator <feature-name>`, integrate into project workflow after components are built
- 🧠 Reflection: Skill provides comprehensive guidance for connecting UI to APIs with modern React patterns. Covers multiple data fetching strategies with decision guide, extensive hook patterns, and complete state management. Progressive disclosure keeps SKILL.md focused on workflow while detailed patterns are in reference files. Complements sp.design-system by adding data layer to UI components.

## Evaluation notes (flywheel)

- Failure modes observed: None - skill creation completed successfully
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): Test skill on actual feature to wire components to API, validate hook patterns and state management completeness
