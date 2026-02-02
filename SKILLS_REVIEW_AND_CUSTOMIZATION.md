# Skills Review & Customization Guide

## Executive Summary

You have created a **production-ready, full-stack development skill suite** with:
- ✅ 5 skills covering UI design → Backend implementation
- ✅ 2,857 lines of workflow guidance
- ✅ 17 reference files with ~10,000 lines of patterns
- ✅ Consistent structure and progressive disclosure
- ✅ Complete documentation and PHRs

## Architecture Analysis

### Skill Structure Consistency

All skills follow the same proven pattern:

```
skill-name/
├── SKILL.md (10-20KB)
│   ├── YAML frontmatter (name, description)
│   ├── Workflow (8-10 steps)
│   ├── Usage examples
│   ├── Success criteria
│   └── References to detailed files
└── references/
    ├── pattern-1.md (10-15KB)
    ├── pattern-2.md (10-15KB)
    └── pattern-3.md (10-15KB)
```

**Why This Works:**
- Progressive disclosure (metadata → workflow → details)
- SKILL.md stays focused (~500 lines)
- Reference files loaded only when needed
- Consistent navigation across all skills

### Workflow Pattern Analysis

All skills use a similar workflow structure:

1. **Gather Context** - Read specs, architecture, existing code
2. **Choose Strategy** - Select approach (React Query vs SWR, offset vs cursor pagination)
3. **Setup Infrastructure** - Install dependencies, configure tools
4. **Create Core Artifacts** - Models, components, endpoints
5. **Implement Patterns** - Apply best practices
6. **Handle Edge Cases** - Errors, validation, accessibility
7. **Create Output Files** - Generate code in proper locations
8. **Integration** - Connect with workflow (PHR, ADR)

**Strengths:**
- Predictable structure
- Easy to follow
- Comprehensive coverage
- Integration with Spec-Kit workflow

### Reference File Quality

| Skill | Reference Files | Avg Size | Coverage |
|-------|----------------|----------|----------|
| sp.ui-architect | 2 | 10KB | Design patterns, accessibility |
| sp.design-system | 3 | 13KB | Components, Tailwind, theming |
| sp.frontend-integrator | 4 | 14.5KB | Data fetching, hooks, state, forms |
| sp.api-designer | 4 | 11.5KB | REST, pagination, errors, OpenAPI |
| sp.backend-engineer | 4 | 12.75KB | SQLModel, Pydantic, FastAPI, auth |

**Quality Indicators:**
- ✅ Comprehensive examples
- ✅ Best practices documented
- ✅ Anti-patterns identified
- ✅ Decision guides included
- ✅ Code snippets tested patterns

---

## Customization Opportunities

### 1. Tech Stack Variations

**Current Stack:**
- Frontend: Next.js, React, Tailwind, shadcn/ui
- Backend: FastAPI, SQLModel, PostgreSQL
- Auth: JWT with python-jose

**Customization Options:**

#### Alternative Frontend Frameworks

**Add Vite + React:**
```yaml
# In sp.design-system/SKILL.md
## Alternative: Vite Setup

For Vite projects:
```bash
npm create vite@latest my-app -- --template react-ts
npm install -D tailwindcss postcss autoprefixer
```

Update imports:
- `app/globals.css` → `src/index.css`
- `components/` → `src/components/`
```

**Add Vue.js Support:**
```yaml
# Create sp.design-system-vue/SKILL.md
Similar structure but with:
- Vue components instead of React
- Composition API patterns
- Pinia for state management
```

#### Alternative Backend Frameworks

**Add Django REST Framework:**
```yaml
# Create sp.backend-engineer-django/SKILL.md
Replace FastAPI patterns with:
- Django models instead of SQLModel
- Django serializers instead of Pydantic
- Django views/viewsets instead of FastAPI routers
```

**Add NestJS (TypeScript Backend):**
```yaml
# Create sp.backend-engineer-nestjs/SKILL.md
TypeScript backend with:
- NestJS modules and controllers
- TypeORM for database
- Passport for authentication
```

### 2. Company-Specific Patterns

#### Add Internal Component Library

```yaml
# In sp.design-system/SKILL.md, add section:

## Company Component Library

Instead of shadcn/ui, use internal library:

```bash
npm install @company/ui-components
```

Import components:
```tsx
import { Button, Card, Input } from '@company/ui-components'
```

Reference internal design system:
- Design tokens: `@company/design-tokens`
- Documentation: https://design.company.com
```

#### Add Company API Standards

```yaml
# In sp.api-designer/SKILL.md, add section:

## Company API Standards

Follow company conventions:

**URL Structure:**
```
/api/v1/{service}/{resource}
Example: /api/v1/tasks-service/tasks
```

**Error Format:**
```json
{
  "error": {
    "code": "COMPANY_ERROR_CODE",
    "message": "User-friendly message",
    "trace_id": "uuid",
    "timestamp": "ISO 8601"
  }
}
```

**Headers:**
- `X-Request-ID`: Required for all requests
- `X-Company-Client-Version`: Client version
```

### 3. Code Style Preferences

#### Customize Naming Conventions

```yaml
# In sp.backend-engineer/references/sqlmodel-patterns.md

## Company Naming Conventions

**Database Tables:**
- Use plural: `tasks`, `users` (not `task`, `user`)
- Prefix with service: `tasks_service_tasks`
- Snake_case: `task_templates` (not `taskTemplates`)

**Python Files:**
- Models: `task_model.py` (not `task.py`)
- Schemas: `task_schema.py`
- Services: `task_service.py`

**API Endpoints:**
- Versioned: `/api/v1/tasks`
- Kebab-case: `/api/v1/task-templates`
```

#### Customize Component Structure

```yaml
# In sp.design-system/references/component-patterns.md

## Company Component Structure

```tsx
// components/Button/Button.tsx
export const Button = () => { }

// components/Button/Button.test.tsx
describe('Button', () => { })

// components/Button/Button.stories.tsx
export default { title: 'Button' }

// components/Button/index.ts
export { Button } from './Button'
```

Directory structure:
```
components/
├── Button/
│   ├── Button.tsx
│   ├── Button.test.tsx
│   ├── Button.stories.tsx
│   └── index.ts
```
```

### 4. Additional Patterns

#### Add GraphQL Support

```yaml
# Create sp.api-designer-graphql/SKILL.md

## GraphQL API Design

Instead of REST endpoints, design GraphQL schema:

```graphql
type Task {
  id: ID!
  title: String!
  completed: Boolean!
}

type Query {
  tasks(filter: TaskFilter): [Task!]!
  task(id: ID!): Task
}

type Mutation {
  createTask(input: CreateTaskInput!): Task!
  updateTask(id: ID!, input: UpdateTaskInput!): Task!
}
```

Reference: [references/graphql-patterns.md]
```

#### Add Real-Time Features

```yaml
# In sp.frontend-integrator/references/data-fetching-strategies.md

## Real-Time Updates

### WebSocket Pattern

```tsx
import { useEffect } from 'react'

function useTaskUpdates() {
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/tasks')

    ws.onmessage = (event) => {
      const update = JSON.parse(event.data)
      // Update React Query cache
      queryClient.setQueryData(['tasks'], (old) => {
        // Merge update
      })
    }

    return () => ws.close()
  }, [])
}
```

### Server-Sent Events (SSE)

```tsx
function useTaskSSE() {
  useEffect(() => {
    const eventSource = new EventSource('/api/tasks/stream')

    eventSource.onmessage = (event) => {
      const task = JSON.parse(event.data)
      // Update cache
    }

    return () => eventSource.close()
  }, [])
}
```
```

### 5. Testing Patterns

#### Add Testing Guidance

```yaml
# Create new reference file in each skill:
# references/testing-patterns.md

## Testing Strategy

### Unit Tests
- Test individual functions
- Mock dependencies
- Fast execution

### Integration Tests
- Test API endpoints
- Real database (test DB)
- Test authentication

### E2E Tests
- Test full user flows
- Real browser (Playwright)
- Test critical paths

### Example: Testing FastAPI Endpoint

```python
from fastapi.testclient import TestClient

def test_create_task():
    client = TestClient(app)
    response = client.post(
        "/api/tasks",
        json={"title": "Test task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test task"
```
```

---

## Customization Process

### Step 1: Identify What to Customize

**Questions to Ask:**
1. Does our tech stack differ? (Framework, database, etc.)
2. Do we have company-specific patterns? (Naming, structure, etc.)
3. Do we have internal tools/libraries? (Component library, API client, etc.)
4. Do we have specific requirements? (Security, compliance, etc.)
5. What patterns do we use differently? (State management, auth, etc.)

### Step 2: Choose Customization Approach

**Option A: Modify Existing Skills**
- Edit SKILL.md to add company sections
- Update reference files with company patterns
- Add examples using company tools

**Option B: Create Variant Skills**
- Copy skill directory (e.g., `sp.design-system-vue`)
- Modify for alternative tech stack
- Keep original skill intact

**Option C: Add Reference Files**
- Keep SKILL.md unchanged
- Add new reference files (e.g., `company-patterns.md`)
- Reference from SKILL.md

### Step 3: Make Changes

**Example: Add Company API Standards**

1. **Edit SKILL.md:**
```yaml
# In sp.api-designer/SKILL.md, add to workflow:

### 2. Design API Endpoints

Follow company API standards. See [references/company-api-standards.md]

Create RESTful endpoints following best practices...
```

2. **Create Reference File:**
```bash
# Create new file
touch .claude/skills/sp.api-designer/references/company-api-standards.md
```

3. **Add Content:**
```yaml
# Company API Standards

## URL Structure
All APIs must follow: `/api/v1/{service}/{resource}`

## Authentication
Use company SSO with OAuth 2.0

## Error Codes
Use company error code registry: https://errors.company.com
```

4. **Repackage Skill:**
```bash
cd .claude/skills
powershell -Command "Compress-Archive -Path 'sp.api-designer/*' -DestinationPath 'sp.api-designer.zip' -Force"
mv sp.api-designer.zip sp.api-designer.skill
```

### Step 4: Test Changes

1. **Read through modified skill**
2. **Test on small feature**
3. **Verify outputs match expectations**
4. **Iterate based on feedback**

### Step 5: Document Changes

**Create CUSTOMIZATIONS.md:**
```yaml
# Skill Customizations

## Changes Made

### sp.api-designer
- Added company API standards reference
- Updated error format to match company standard
- Added internal API gateway documentation

### sp.design-system
- Replaced shadcn/ui with @company/ui-components
- Updated theme tokens to match brand guidelines
- Added company-specific component patterns

## Maintenance

- Review quarterly for updates
- Sync with company standards changes
- Update examples with real project code
```

---

## Best Practices for Customization

### 1. Keep Original Skills Intact

```bash
# Create backup before modifying
cp -r .claude/skills/sp.design-system .claude/skills/sp.design-system.original

# Or create variant
cp -r .claude/skills/sp.design-system .claude/skills/sp.design-system-company
```

### 2. Use Progressive Disclosure

Don't bloat SKILL.md with company details. Add reference files:

```
sp.api-designer/
├── SKILL.md (keep focused)
└── references/
    ├── rest-api-design.md (original)
    ├── company-api-standards.md (NEW)
    └── company-examples.md (NEW)
```

### 3. Document Deviations

```yaml
# In SKILL.md, add note:

## Company Customizations

This skill has been customized for [Company Name]:
- Uses internal component library (@company/ui)
- Follows company API standards (see references/company-api-standards.md)
- Integrates with company SSO

For original skill, see: sp.design-system.original.skill
```

### 4. Version Control Skills

```bash
# Initialize git in skills directory
cd .claude/skills
git init
git add .
git commit -m "Initial skill suite"

# Track changes
git add sp.api-designer/
git commit -m "Add company API standards to sp.api-designer"
```

### 5. Share with Team

```bash
# Create skill repository
git remote add origin https://github.com/company/claude-skills
git push -u origin main

# Team members can clone
git clone https://github.com/company/claude-skills ~/.claude/skills
```

---

## Common Customization Examples

### Example 1: Add Monorepo Support

```yaml
# In all skills, update file paths:

## Output Files

For monorepo structure:

**Frontend:**
- `apps/web/components/ui/button.tsx`
- `apps/web/app/page.tsx`

**Backend:**
- `apps/api/app/routers/tasks.py`
- `apps/api/app/models/task.py`

**Shared:**
- `packages/types/src/task.ts`
- `packages/ui/src/Button.tsx`
```

### Example 2: Add Internationalization

```yaml
# In sp.frontend-integrator, add section:

## Internationalization (i18n)

### Setup next-intl

```bash
npm install next-intl
```

### Create translations

```tsx
// messages/en.json
{
  "tasks": {
    "title": "Tasks",
    "create": "Create Task",
    "empty": "No tasks yet"
  }
}

// Usage
import { useTranslations } from 'next-intl'

function TaskList() {
  const t = useTranslations('tasks')
  return <h1>{t('title')}</h1>
}
```
```

### Example 3: Add Logging Standards

```yaml
# In sp.backend-engineer, add section:

## Logging

Use structured logging with company logger:

```python
from company_logger import get_logger

logger = get_logger(__name__)

@app.post("/api/tasks")
async def create_task(task: TaskCreate):
    logger.info(
        "Creating task",
        extra={
            "user_id": user_id,
            "task_title": task.title,
            "trace_id": request.state.trace_id
        }
    )
```

**Log Levels:**
- DEBUG: Development debugging
- INFO: Normal operations
- WARNING: Unexpected but handled
- ERROR: Errors requiring attention
- CRITICAL: System failures
```

---

## Next Steps

### Immediate Actions

1. **Review SKILLS_SUMMARY.md** - Understand what you have
2. **Read through one skill completely** - Pick sp.ui-architect (smallest)
3. **Identify customization needs** - List company-specific requirements
4. **Make one small change** - Test the customization process
5. **Document the change** - Create CUSTOMIZATIONS.md

### Short-Term (This Week)

1. **Test skills on real feature** - Use on task-crud or authentication
2. **Gather feedback** - What works? What's missing?
3. **Add company patterns** - One skill at a time
4. **Create examples** - Real code from your project
5. **Share with team** - Get input on customizations

### Long-Term (This Month)

1. **Create variant skills** - For alternative tech stacks
2. **Add testing patterns** - Unit, integration, E2E
3. **Build skill library** - Additional roles (DevOps, Testing, etc.)
4. **Establish maintenance process** - Quarterly reviews
5. **Measure impact** - Track time saved, consistency improved

---

## Support & Resources

### Documentation
- ✅ SKILLS_SUMMARY.md - Complete overview
- ✅ TESTING_SKILLS.md - How to test
- ✅ QUICK_START.md - Quick reference
- ✅ This file - Customization guide

### Getting Help
1. Read SKILL.md for workflow
2. Check reference files for patterns
3. Review PHRs for examples
4. Test on small features first
5. Iterate based on feedback

### Contributing Back
If you create valuable customizations:
1. Document them well
2. Create examples
3. Share with community
4. Contribute to skill-creator

---

## Conclusion

You have a **solid foundation** for full-stack development. The skills are:
- ✅ Well-structured and consistent
- ✅ Comprehensive and detailed
- ✅ Ready to use as-is
- ✅ Easy to customize
- ✅ Maintainable and extensible

**Recommended Path:**
1. Use skills as-is on one feature
2. Identify what needs customization
3. Make targeted changes
4. Test and iterate
5. Share with team

The skills will improve with use. Start simple, customize gradually, and build your team's development system.
