 Here is your updated **root CLAUDE.md** that merges the Spec-Kit Plus governance rules with your Todo App Phase II context:

```markdown
# Claude Code Rules - Todo App Hackathon II

## Task Context

**Surface:** You operate on the project level for the Todo App Full-Stack implementation (Phase II), providing guidance and executing development tasks via MCP tools and CLI commands.

**Success is Measured By:**
- All outputs strictly follow the user intent and specifications in `/specs/`
- Prompt History Records (PHRs) are created automatically for every user prompt under `history/prompts/`
- Architectural Decision Record (ADR) suggestions are made for significant decisions (Auth strategy, Database schema, API design)
- All changes are small, testable, and reference code precisely
- Strict adherence to Spec-Driven Development workflow

---

## Core Guarantees (Product Promise)

- **Record Every Input:** Create a Prompt History Record (PHR) after every user message. Do not truncate; preserve full multiline input.
- **PHR Routing** (all under `history/prompts/`):
  - Constitution → `history/prompts/constitution/`
  - Feature-specific → `history/prompts/<feature-name>/` (e.g., `history/prompts/task-crud/`, `history/prompts/authentication/`)
  - General → `history/prompts/general/`
- **ADR Suggestions:** When architecturally significant decisions are detected (Tech stack, Auth method, State management), suggest:  
  📋 Architectural decision detected: [brief description]. Document? Run `/sp.adr <title>`.  
  Never auto-create ADRs; require user consent.

---

## Development Guidelines

### 1. Authoritative Source Mandate
MUST prioritize MCP tools and CLI commands for all information gathering. NEVER assume a solution from internal knowledge; verify via:
- Database schema in `@specs/database/schema.md`
- API contracts in `@specs/api/rest-endpoints.md`
- Feature requirements in `@specs/features/*.md`

### 2. Execution Flow
Treat MCP servers as first-class tools. **PREFER CLI interactions** (running commands, capturing outputs) over manual file creation. Use `npm`, `pip`, `git`, and database CLI tools for verification.

### 3. Knowledge Capture (PHR) - MANDATORY FOR EVERY USER INPUT

**PHR Creation Process:**

1) **Detect Stage** (one of):
   - `constitution` - Project setup, repo structure
   - `spec` - Writing/editing specifications
   - `plan` - Architecture planning
   - `tasks` - Task breakdown
   - `red` - Failing test implementation (TDD)
   - `green` - Implementation to pass tests
   - `refactor` - Code improvement
   - `explainer` - Documentation/explanation
   - `misc` - Other work
   - `general` - General queries

2) **Generate Title:** 3-7 words; create slug for filename.

3) **Resolve Route** (all under `history/prompts/`):
   - `constitution` → `history/prompts/constitution/`
   - Feature stages → `history/prompts/<feature-name>/` (auto-detect from context: "task-crud", "authentication", "chatbot")
   - `general` → `history/prompts/general/`

4) **Prefer Agent-Native Flow** (no shell):
   - Read PHR template from `.specify/templates/phr-template.prompt.md` or `templates/phr-template.prompt.md`
   - Allocate ID (increment; on collision, increment again)
   - Compute output path:
     - Constitution: `history/prompts/constitution/<ID>-<slug>.constitution.prompt.md`
     - Feature: `history/prompts/<feature-name>/<ID>-<slug>.<stage>.prompt.md`
     - General: `history/prompts/general/<ID>-<slug>.general.prompt.md`
   - Fill ALL placeholders in YAML frontmatter:
     - ID, TITLE, STAGE, DATE_ISO (YYYY-MM-DD), SURFACE="agent"
     - MODEL (Claude Sonnet/Opus), FEATURE (or "none"), BRANCH, USER
     - COMMAND (current command), LABELS (["topic1","topic2"])
     - LINKS: SPEC/TICKET/ADR/PR (URLs or "null")
     - FILES_YAML: list created/modified files
     - TESTS_YAML: list tests run/added
     - PROMPT_TEXT: full user input (verbatim, never truncated)
     - RESPONSE_TEXT: key assistant output (concise)
   - Write file with agent file tools
   - Confirm absolute path in output

5) **Post-Creation Validations:**
   - No unresolved placeholders (`{{THIS}}`, `[THAT]`)
   - Title, stage, dates match front-matter
   - PROMPT_TEXT is complete
   - File exists at expected path

6) **Report:** Print ID, path, stage, title. Skip PHR only for `/sp.phr` command itself.

### 4. Explicit ADR Suggestions
When significant architectural decisions are made (during `/sp.plan` and `/sp.tasks`), run three-part test:
- Impact: Long-term consequences?
- Alternatives: Multiple viable options?
- Scope: Cross-cutting influences?

If ALL true, suggest:  
📋 Architectural decision detected: [brief] — Document reasoning? Run `/sp.adr [decision-title]`

### 5. Human as Tool Strategy
Invoke user for input when encountering:
- **Ambiguous Requirements:** Ask 2-3 targeted questions before proceeding
- **Unforeseen Dependencies:** Surface them and ask for prioritization  
- **Architectural Uncertainty:** Present options with tradeoffs, get preference
- **Completion Checkpoint:** Summarize milestones, confirm next steps

---

## Default Policies (Must Follow)

- **Clarify and Plan First:** Keep business understanding separate from technical plan. Carefully architect before implementing.
- **Do Not Invent:** Never invent APIs, data, or contracts. If missing from `@specs/`, ask targeted clarifiers.
- **No Hardcoded Secrets:** Use `.env` files only; never commit tokens.
- **Smallest Viable Diff:** Do not refactor unrelated code. One feature per changeset.
- **Code References:** Cite existing code with `start:end:path` format; propose new code in fenced blocks.
- **Private Reasoning:** Output only decisions, artifacts, and justifications.

### Execution Contract for Every Request
1) Confirm surface and success criteria (one sentence)
2) List constraints, invariants, non-goals
3) Produce artifact with acceptance checks inlined (checkboxes/tests)
4) Add follow-ups and risks (max 3 bullets)
5) Create PHR in appropriate subdirectory under `history/prompts/`
6) Surface ADR suggestion if plan/tasks identified significant decisions

### Minimum Acceptance Criteria
- Clear, testable acceptance criteria included
- Explicit error paths and constraints stated
- Smallest viable change; no unrelated edits
- Code references to modified/inspected files

---

## Project-Specific Context (Todo App Phase II)

### Current Phase
**Phase II: Full-Stack Web Application** - Converting console app to multi-user web app with persistent storage.

### Tech Stack Mandate
- **Frontend:** Next.js 16+ (App Router), TypeScript, Tailwind CSS
- **Backend:** Python FastAPI, SQLModel, Neon Serverless PostgreSQL
- **Auth:** Better Auth with JWT (shared secret between frontend/backend)
- **Architecture:** Stateless backend, user data isolation via JWT filtering

### Critical Constraints
1. **User Isolation:** Every database query MUST filter by `user_id` extracted from JWT
2. **Stateless:** Server holds no session state; all context in JWT or database
3. **Auth Flow:** Better Auth (frontend) → JWT → FastAPI verification → Filtered data
4. **API Contract:** RESTful endpoints under `/api/*` with `Authorization: Bearer <token>` header required

### Spec-Kit Structure Reference
- `.spec-kit/config.yaml` - Project configuration
- `specs/overview.md` - Project goals
- `specs/architecture.md` - System design & auth flow
- `specs/database/schema.md` - SQLModel models (tasks, users, conversations)
- `specs/api/rest-endpoints.md` - FastAPI endpoint contracts
- `specs/features/task-crud.md` - CRUD requirements
- `specs/features/authentication.md` - Auth requirements
- `specs/ui/components.md` - React component specs
- `specs/ui/pages.md` - Next.js page routes
- `frontend/CLAUDE.md` - Frontend-specific patterns
- `backend/CLAUDE.md` - Backend-specific patterns

### Workflow
1. Read relevant specs before implementing (`@specs/features/*.md`)
2. Reference architecture for auth/data flow (`@specs/architecture.md`)
3. Update specs if requirements change
4. Create PHR after every interaction
5. Suggest ADR for architectural decisions (Auth strategy, Database design, API versioning)

---

## Basic Project Structure

```
.specify/
├── memory/
│   └── constitution.md          # Project principles & code standards
├── templates/
│   └── phr-template.prompt.md   # PHR template
├── scripts/
│   └── bash/
│       └── create-phr.sh        # PHR creation script (fallback)
specs/
├── overview.md
├── architecture.md
├── database/schema.md
├── api/rest-endpoints.md
├── features/task-crud.md
├── features/authentication.md
├── ui/components.md
└── ui/pages.md
history/
├── prompts/
│   ├── constitution/            # Setup PHRs
│   ├── task-crud/               # Feature PHRs
│   ├── authentication/          # Feature PHRs
│   └── general/                 # General PHRs
└── adr/                         # Architecture Decision Records
frontend/                        # Next.js app
backend/                         # FastAPI app
CLAUDE.md                        # This file
.spec-kit/config.yaml            # Spec-Kit configuration
```

## Code Standards
Refer to `.specify/memory/constitution.md` for:
- Code quality standards
- Testing requirements (unit, integration, e2e)
- Performance budgets (p95 latency)
- Security principles (OWASP, secrets management)
- Architecture principles (SOLID, DRY, single responsibility)

---

## Example Prompts for This Project

**Constitution/Setup:**
"Set up the monorepo structure for Phase II"

**Spec:**
"Draft the authentication spec based on Better Auth + JWT requirements"

**Plan:**
"Create implementation plan for task-crud feature"

**Tasks:**
"Break down the task-crud implementation into testable tasks"

**Implementation:**
"Implement the POST /api/tasks endpoint following @specs/api/rest-endpoints.md"

**PHR Check:**
After every response, verify: "Did I create the PHR in `history/prompts/[appropriate-folder]/`?"
```
