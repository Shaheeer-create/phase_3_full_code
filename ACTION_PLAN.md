# Skills Action Plan & Quick Reference

## What We Accomplished Today

### ✅ Created 5 Production-Ready Skills

1. **sp.ui-architect** (12KB) - Design UI/UX layouts and components
2. **sp.design-system** (19KB) - Build reusable component libraries
3. **sp.frontend-integrator** (23KB) - Wire UI to APIs with React Query
4. **sp.api-designer** (21KB) - Design REST API endpoints and OpenAPI specs
5. **sp.backend-engineer** (19KB) - Implement FastAPI endpoints with SQLModel

### ✅ Created Comprehensive Documentation

- **SKILLS_SUMMARY.md** - Complete overview of all 5 skills
- **TESTING_SKILLS.md** - Step-by-step testing guide
- **QUICK_START.md** - Quick reference for getting started
- **SKILLS_REVIEW_AND_CUSTOMIZATION.md** - Detailed customization guide
- **5 PHRs** - Documenting each skill creation

### ✅ Total Content Created

- **94KB** of core skill content (SKILL.md files)
- **214KB** of reference material (17 reference files)
- **~10,000 lines** of patterns and examples
- **2,857 lines** of workflow guidance

---

## Your Next Actions

### Immediate (Next 30 Minutes)

**1. Read One Complete Skill**

Start with the smallest skill to understand the structure:

```bash
# Read sp.ui-architect (smallest, easiest to understand)
cat .claude/skills/sp.ui-architect/SKILL.md

# Then read one reference file
cat .claude/skills/sp.ui-architect/references/design-patterns.md
```

**What to look for:**
- Workflow structure (10 steps)
- When to use the skill
- What outputs it creates
- How it integrates with other skills

**2. Review Your Project Specs**

Check what specs you already have:

```bash
# List existing specs
ls -la specs/

# You should have:
# - specs/overview.md
# - specs/architecture.md
# - specs/database/schema.md
# - specs/api/rest-endpoints.md
# - specs/features/authentication.md
```

**3. Choose a Test Feature**

Pick a simple feature to test the skills:

**Option A: Task CRUD** (Recommended - simple, complete)
- Create, read, update, delete tasks
- Good for testing all 5 skills
- Clear requirements

**Option B: Authentication** (Already have spec)
- Login, register, JWT tokens
- Tests backend skills well
- Critical feature

**Option C: User Profile** (Simple)
- View/edit user profile
- Tests frontend skills
- Single entity

### Short-Term (This Week)

**Day 1: Test UI Design Skill**

```bash
# Manually follow sp.ui-architect workflow for task-crud:

# 1. Read specs/features/ (if task-crud spec exists)
# 2. Design component hierarchy
# 3. Choose design pattern (Master-Detail for tasks)
# 4. Define design tokens
# 5. Create layout wireframes
# 6. Document accessibility
# 7. Create output files in specs/ui/
```

**Expected Output:**
- `specs/ui/components/task-crud-components.md`
- `specs/ui/layouts/task-crud-layouts.md`
- `specs/ui/design-tokens.md`

**Day 2: Test API Design Skill**

```bash
# Manually follow sp.api-designer workflow for task-crud:

# 1. Read feature requirements
# 2. Design endpoints (GET/POST/PATCH/DELETE /api/tasks)
# 3. Define request schemas (CreateTaskRequest, UpdateTaskRequest)
# 4. Define response schemas (TaskResponse, TaskListResponse)
# 5. Design pagination (offset-based)
# 6. Define error responses
# 7. Create OpenAPI spec
```

**Expected Output:**
- `specs/api/task-crud-endpoints.md`
- `specs/api/openapi.yaml` (updated)

**Day 3: Test Component Building**

```bash
# Manually follow sp.design-system workflow:

# 1. Read design tokens from specs/ui/design-tokens.md
# 2. Setup Tailwind config
# 3. Install shadcn/ui
# 4. Create core components (Button, Card, Input, Modal)
# 5. Implement variants with CVA
# 6. Setup dark mode
```

**Expected Output:**
- `components/ui/button.tsx`
- `components/ui/card.tsx`
- `components/ui/input.tsx`
- `tailwind.config.js`
- `app/globals.css`

**Day 4: Test Backend Implementation**

```bash
# Manually follow sp.backend-engineer workflow:

# 1. Read API contracts from specs/api/
# 2. Create SQLModel models
# 3. Create Pydantic schemas
# 4. Implement FastAPI endpoints
# 5. Add JWT authentication
# 6. Test with curl or Postman
```

**Expected Output:**
- `backend/app/models/task.py`
- `backend/app/schemas/task.py`
- `backend/app/routers/tasks.py`
- `backend/app/utils/auth.py`

**Day 5: Test Frontend Integration**

```bash
# Manually follow sp.frontend-integrator workflow:

# 1. Setup React Query
# 2. Create API client
# 3. Create custom hooks (useTasks, useCreateTask)
# 4. Wire components to hooks
# 5. Add loading/error/empty states
# 6. Test in browser
```

**Expected Output:**
- `hooks/use-tasks.ts`
- `hooks/use-create-task.ts`
- `lib/api-client.ts`
- Updated components with data

### Medium-Term (This Month)

**Week 2: Customize for Your Needs**

1. **Identify Customizations:**
   - Company-specific patterns?
   - Different tech stack?
   - Internal tools/libraries?
   - Specific requirements?

2. **Make One Customization:**
   - Add company API standards
   - Add internal component library
   - Add logging patterns
   - Add testing patterns

3. **Document Changes:**
   - Create CUSTOMIZATIONS.md
   - Update relevant SKILL.md files
   - Add examples from your project

**Week 3: Build Complete Feature**

Use all 5 skills to build one complete feature end-to-end:

```
Task CRUD Feature:
├─ /sp.ui-architect task-crud
├─ /sp.api-designer task-crud
├─ /sp.design-system
├─ /sp.backend-engineer task-crud
└─ /sp.frontend-integrator task-crud
```

**Week 4: Create Additional Skills**

Based on your needs, create:
- **sp.testing-engineer** - Unit, integration, E2E tests
- **sp.devops-engineer** - Docker, CI/CD, deployment
- **sp.database-engineer** - Migrations, optimization

---

## Quick Reference Card

### Skill Usage Order

```
1. /sp.specify <feature>          → Feature spec
2. /sp.ui-architect <feature>     → UI design
3. /sp.api-designer <feature>     → API design
4. /sp.design-system              → Components
5. /sp.backend-engineer <feature> → Backend
6. /sp.frontend-integrator <feature> → Wire UI to API
```

### When to Use Each Skill

| Skill | When | Input Required | Output |
|-------|------|----------------|--------|
| sp.ui-architect | After feature spec | Feature requirements | Component specs, layouts, tokens |
| sp.api-designer | After feature spec | Feature requirements, DB schema | API endpoints, OpenAPI spec |
| sp.design-system | After UI design | Design tokens | Component library, theme |
| sp.backend-engineer | After API design | API contracts | FastAPI endpoints, models |
| sp.frontend-integrator | After components + API | Components, API contracts | Hooks, wired components |

### File Locations

```
Skills:
.claude/skills/*.skill

Documentation:
SKILLS_SUMMARY.md              - Complete overview
TESTING_SKILLS.md              - Testing guide
QUICK_START.md                 - Quick reference
SKILLS_REVIEW_AND_CUSTOMIZATION.md - Customization guide
THIS FILE                      - Action plan

PHRs:
history/prompts/general/14-*.md - sp.ui-architect
history/prompts/general/15-*.md - sp.design-system
history/prompts/general/16-*.md - sp.frontend-integrator
history/prompts/general/17-*.md - sp.api-designer
history/prompts/general/18-*.md - sp.backend-engineer
```

### Common Commands

```bash
# List all skills
ls -lh .claude/skills/*.skill

# Read a skill
cat .claude/skills/sp.ui-architect/SKILL.md

# Read a reference
cat .claude/skills/sp.ui-architect/references/design-patterns.md

# Check project specs
ls -la specs/

# View PHRs
ls -la history/prompts/general/
```

---

## Decision Points

### Should I Use These Skills As-Is or Customize?

**Use As-Is If:**
- ✅ Using Next.js + Tailwind + FastAPI stack
- ✅ No company-specific requirements
- ✅ Want to start quickly
- ✅ Can adapt to patterns later

**Customize If:**
- ⚠️ Different tech stack (Vue, Django, etc.)
- ⚠️ Company has specific standards
- ⚠️ Using internal tools/libraries
- ⚠️ Need specific patterns

**Recommendation:** Start as-is, customize after first use.

### Should I Test on Real Project or Practice First?

**Test on Real Project If:**
- ✅ Have clear requirements
- ✅ Low-risk feature
- ✅ Can iterate quickly
- ✅ Want immediate value

**Practice First If:**
- ⚠️ Unfamiliar with workflow
- ⚠️ High-risk project
- ⚠️ Need to understand patterns
- ⚠️ Want to customize first

**Recommendation:** Test on simple real feature (task CRUD).

### Should I Use All 5 Skills or Start with Subset?

**Use All 5 If:**
- ✅ Building complete feature
- ✅ Need full-stack implementation
- ✅ Have time to follow full workflow

**Start with Subset If:**
- ⚠️ Only need frontend or backend
- ⚠️ Want to learn gradually
- ⚠️ Testing the approach

**Recommendation:** Start with 2-3 skills (UI + API design).

---

## Success Metrics

### How to Know Skills Are Working

**Week 1:**
- ✅ Successfully followed one skill workflow
- ✅ Created expected output files
- ✅ Outputs match quality standards
- ✅ Understand skill structure

**Week 2:**
- ✅ Used 3+ skills on same feature
- ✅ Outputs integrate well together
- ✅ Identified customization needs
- ✅ Made first customization

**Month 1:**
- ✅ Built complete feature with all 5 skills
- ✅ Customized for company needs
- ✅ Shared with team
- ✅ Measured time savings

**Month 3:**
- ✅ Team using skills regularly
- ✅ Created additional skills
- ✅ Established maintenance process
- ✅ Documented best practices

---

## Troubleshooting

### "I don't know where to start"

→ Read QUICK_START.md, then test sp.ui-architect on task-crud

### "Skills don't match my tech stack"

→ Read SKILLS_REVIEW_AND_CUSTOMIZATION.md, create variant skills

### "Outputs don't match my needs"

→ Customize reference files, add company patterns

### "Too much to learn at once"

→ Start with one skill, master it, then add more

### "Not sure if doing it right"

→ Compare outputs to examples in reference files

---

## Resources

### Documentation (Read in Order)

1. **QUICK_START.md** - Start here (5 min read)
2. **SKILLS_SUMMARY.md** - Complete overview (15 min read)
3. **TESTING_SKILLS.md** - How to test (20 min read)
4. **SKILLS_REVIEW_AND_CUSTOMIZATION.md** - Customization (30 min read)
5. **This file** - Action plan (10 min read)

### Skills (Read One Completely)

1. **sp.ui-architect** - Smallest, easiest to understand
2. **sp.design-system** - Most examples
3. **sp.frontend-integrator** - Most comprehensive
4. **sp.api-designer** - Best practices
5. **sp.backend-engineer** - Most technical

### Reference Files (Read As Needed)

- Design patterns when designing UI
- Component patterns when building components
- Hook patterns when integrating data
- REST API design when designing APIs
- SQLModel patterns when building backend

---

## Final Checklist

Before you start using the skills:

- [ ] Read QUICK_START.md
- [ ] Read one complete skill (sp.ui-architect recommended)
- [ ] Review your project specs
- [ ] Choose a test feature (task-crud recommended)
- [ ] Understand the workflow order
- [ ] Know where to find documentation
- [ ] Have development environment ready

Ready to start? Pick one:

**A. Test sp.ui-architect on task-crud** (Recommended)
**B. Customize one skill for your needs**
**C. Create a new skill for different role**
**D. Read more documentation first**

---

## Summary

You have everything you need:
- ✅ 5 production-ready skills
- ✅ Comprehensive documentation
- ✅ Clear action plan
- ✅ Customization guide
- ✅ Quick reference

**Next Step:** Choose a test feature and follow sp.ui-architect workflow manually.

**Remember:** Skills improve with use. Start simple, iterate, and build your development system.

Good luck! 🚀
