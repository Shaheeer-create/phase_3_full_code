---
id: 17
title: Create API Designer Skill
stage: misc
date: 2026-02-01
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: user
command: yes make backend skills
labels: ["skill-creation", "backend", "api-design", "rest", "openapi"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - path: .claude/skills/sp.api-designer/SKILL.md
    status: created
  - path: .claude/skills/sp.api-designer/references/rest-api-design.md
    status: created
  - path: .claude/skills/sp.api-designer/references/pagination-patterns.md
    status: created
  - path: .claude/skills/sp.api-designer/references/error-handling.md
    status: created
  - path: .claude/skills/sp.api-designer/references/openapi-spec.md
    status: created
  - path: .claude/skills/sp.api-designer.skill
    status: created
tests:
  - name: none
    status: not_applicable
---

## Prompt

yes make backend skills

## Response snapshot

Created the `sp.api-designer` skill for designing REST API endpoints and OpenAPI specifications:

**Skill Structure:**
- SKILL.md - 10-step workflow for API design (18KB)
- references/rest-api-design.md - RESTful conventions and best practices (12KB)
- references/pagination-patterns.md - Offset vs cursor pagination strategies (11KB)
- references/error-handling.md - Standard error responses and status codes (13KB)
- references/openapi-spec.md - Complete OpenAPI 3.0 guide (10KB)
- sp.api-designer.skill - Packaged distributable (21KB)

**Workflow Steps:**
1. Gather context from feature specs and database schema
2. Design API endpoints following REST conventions
3. Define request schemas with validation rules
4. Define response schemas with examples
5. Design pagination and filtering patterns
6. Define error responses with standard format
7. Design authentication requirements
8. Create OpenAPI specification
9. Create output files in specs/api/
10. Integration with Spec-Kit workflow

**Key Features:**
- RESTful API design principles
- Resource-based URL structure
- HTTP method conventions (GET, POST, PUT, PATCH, DELETE)
- Request/response schema definitions
- Pagination strategies (offset-based, cursor-based, keyset)
- Filtering and sorting patterns
- Standard error response format
- HTTP status code guidelines
- OpenAPI 3.0 specification generation
- Authentication design (JWT, OAuth)

**Reference Files:**
- **rest-api-design.md**: Resource naming, HTTP methods, URL structure, status codes, versioning, HATEOAS, best practices and anti-patterns
- **pagination-patterns.md**: Offset-based, cursor-based, keyset pagination with pros/cons, implementation examples, decision guide
- **error-handling.md**: Error response format, status codes, error codes, validation errors, error messages, best practices
- **openapi-spec.md**: OpenAPI 3.0 structure, path definitions, schema definitions, authentication, reusable components, tools

**Output Files:**
- specs/api/<feature>-endpoints.md - Endpoint documentation
- specs/api/openapi.yaml - OpenAPI specification
- specs/api/rest-endpoints.md - Consolidated API contracts

## Outcome

- ✅ Impact: New skill enables systematic API design before implementation, ensuring consistent REST conventions and comprehensive documentation
- 🧪 Tests: Not applicable (skill creation)
- 📁 Files: Created 6 files (SKILL.md, 4 reference files, packaged .skill file)
- 🔁 Next prompts: Test skill with `/sp.api-designer <feature-name>`, integrate into workflow after feature specs exist
- 🧠 Reflection: Skill provides comprehensive API design guidance covering REST principles, pagination strategies, error handling, and OpenAPI documentation. Progressive disclosure keeps SKILL.md focused on workflow while detailed patterns are in reference files. Complements sp.backend-engineer by providing API contracts before implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None - skill creation completed successfully
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): Test skill on actual feature to design API, validate completeness of patterns and OpenAPI generation
