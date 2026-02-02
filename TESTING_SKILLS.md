# Testing Frontend Skills on Todo App Project

## Overview

You have created three frontend development skills:
1. **sp.ui-architect** - Design UI/UX layouts and components
2. **sp.design-system** - Build reusable component library
3. **sp.frontend-integrator** - Wire components to APIs

## Step 1: Verify Skills Are Installed

### Check Skill Files

Your skills are located at:
```
.claude/skills/
├── sp.ui-architect.skill (12KB)
├── sp.design-system.skill (19KB)
└── sp.frontend-integrator.skill (23KB)
```

### Verify Skills Are Loaded

Skills should appear in Claude Code's available skills list. You can check by:
1. Starting a new conversation with Claude Code
2. The system will list available skills in system reminders
3. Look for your three skills in the list

## Step 2: Test sp.ui-architect (Design UI/UX)

### Test Case: Design Task CRUD UI

**Command:**
```
/sp.ui-architect task-crud
```

**What It Should Do:**
1. Read `specs/features/authentication.md` (or create task-crud spec first)
2. Read `specs/architecture.md` for tech stack
3. Design component hierarchy for task management
4. Choose design pattern (likely Master-Detail or List pattern)
5. Define design tokens (spacing, typography, colors)
6. Create page layouts with wireframes
7. Document accessibility requirements

**Expected Outputs:**
```
specs/ui/components/task-crud-components.md
specs/ui/layouts/task-crud-layouts.md
specs/ui/design-tokens.md (created or updated)
```

**What to Check:**
- [ ] Component hierarchy is clear (TaskList, TaskCard, TaskForm, etc.)
- [ ] Design pattern chosen with rationale
- [ ] Layout includes desktop, tablet, mobile views
- [ ] Design tokens defined (spacing, colors, typography)
- [ ] Accessibility requirements specified (WCAG AA)
- [ ] PHR created in `history/prompts/task-crud/`

### Manual Test (Without Running Skill)

You can manually verify the skill would work by checking:
1. Does `specs/features/` have task-crud requirements?
2. Does `specs/architecture.md` specify Next.js + Tailwind?
3. Are there existing UI specs to reference?

**If missing specs, create them first:**
```
/sp.specify task-crud
```

## Step 3: Test sp.design-system (Build Components)

### Test Case: Build Core Components

**Command:**
```
/sp.design-system
```

**What It Should Do:**
1. Read `specs/ui/design-tokens.md` (from previous step)
2. Read `specs/ui/components/` for component specs
3. Setup Tailwind CSS configuration
4. Install shadcn/ui or Radix UI
5. Create reusable components (Button, Card, Input, Modal, etc.)
6. Implement variants and states
7. Setup theme with dark mode
8. Create global styles

**Expected Outputs:**
```
components/ui/button.tsx
components/ui/card.tsx
components/ui/input.tsx
components/ui/modal.tsx
components/ui/form.tsx
tailwind.config.js (updated)
app/globals.css (updated)
components/theme-provider.tsx
lib/utils.ts
```

**What to Check:**
- [ ] Tailwind configured with design tokens
- [ ] Components use CVA for variants
- [ ] Dark mode setup with next-themes
- [ ] Components are TypeScript typed
- [ ] Components use forwardRef pattern
- [ ] Accessibility attributes included
- [ ] PHR created in `history/prompts/general/` or `history/prompts/task-crud/`

### Manual Test

Check if the skill would work:
1. Does `specs/ui/design-tokens.md` exist?
2. Is Next.js + Tailwind specified in architecture?
3. Does `package.json` exist for npm installs?

## Step 4: Test sp.frontend-integrator (Wire to APIs)

### Test Case: Connect Task CRUD to API

**Command:**
```
/sp.frontend-integrator task-crud
```

**What It Should Do:**
1. Read `specs/api/rest-endpoints.md` for API contracts
2. Read `specs/architecture.md` for auth flow
3. Choose data fetching strategy (React Query recommended)
4. Setup QueryClient provider
5. Create API client with auth
6. Create custom hooks (useTasks, useCreateTask, useUpdateTask, useDeleteTask)
7. Implement loading, error, empty states
8. Wire components to hooks
9. Add optimistic updates

**Expected Outputs:**
```
hooks/use-tasks.ts
hooks/use-create-task.ts
hooks/use-update-task.ts
hooks/use-delete-task.ts
lib/api-client.ts
types/task.ts
app/providers.tsx (updated)
components/task-list.tsx (updated)
components/create-task-form.tsx (updated)
```

**What to Check:**
- [ ] API client configured with base URL and auth
- [ ] Custom hooks created for all CRUD operations
- [ ] Loading states implemented (skeletons)
- [ ] Error states handled (with retry)
- [ ] Empty states designed
- [ ] Forms use React Hook Form + Zod
- [ ] Optimistic updates implemented
- [ ] TypeScript types match API contracts
- [ ] PHR created in `history/prompts/task-crud/`

### Manual Test

Check if the skill would work:
1. Does `specs/api/rest-endpoints.md` define task endpoints?
2. Are request/response schemas documented?
3. Is auth flow (JWT) documented in architecture?
4. Do components exist to wire up?

## Step 5: Complete Workflow Test

### Full Feature Implementation

Test all three skills together for a complete feature:

```bash
# 1. Create feature spec (if not exists)
/sp.specify task-crud

# 2. Design UI/UX
/sp.ui-architect task-crud

# 3. Build component library
/sp.design-system

# 4. Wire components to API
/sp.frontend-integrator task-crud

# 5. Create implementation plan
/sp.plan task-crud

# 6. Execute implementation
/sp.implement task-crud
```

**Expected Result:**
A fully functional task management UI with:
- Designed layouts and components
- Reusable component library
- API integration with loading/error/empty states
- Forms with validation
- Optimistic updates
- Dark mode support
- Accessibility compliance

## Step 6: Verify Outputs

### Check File Structure

After running all skills, you should have:

```
specs/
├── ui/
│   ├── components/
│   │   └── task-crud-components.md
│   ├── layouts/
│   │   └── task-crud-layouts.md
│   └── design-tokens.md

components/
├── ui/
│   ├── button.tsx
│   ├── card.tsx
│   ├── input.tsx
│   ├── modal.tsx
│   └── ...
└── task-list.tsx
└── create-task-form.tsx

hooks/
├── use-tasks.ts
├── use-create-task.ts
├── use-update-task.ts
└── use-delete-task.ts

lib/
├── api-client.ts
└── utils.ts

types/
└── task.ts

app/
├── providers.tsx
└── globals.css

tailwind.config.js
```

### Check PHRs

Verify PHRs were created:
```
history/prompts/task-crud/
├── XX-design-task-crud-ui.spec.prompt.md
├── XX-build-component-library.green.prompt.md
└── XX-wire-task-crud-to-api.green.prompt.md
```

## Step 7: Test in Browser

### Run the Application

```bash
# Frontend
cd frontend
npm install
npm run dev

# Backend (separate terminal)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Manual Testing Checklist

- [ ] Components render correctly
- [ ] Dark mode toggle works
- [ ] Task list loads from API
- [ ] Loading skeleton shows during fetch
- [ ] Error message shows on API failure
- [ ] Empty state shows when no tasks
- [ ] Create task form validates input
- [ ] Create task submits to API
- [ ] Optimistic update shows immediately
- [ ] Task list refreshes after create
- [ ] Update task works
- [ ] Delete task works
- [ ] All interactions are keyboard accessible
- [ ] Screen reader announces state changes

## Troubleshooting

### Skill Not Found

**Problem:** Claude Code doesn't recognize the skill command

**Solution:**
1. Check skill files exist in `.claude/skills/`
2. Verify `.skill` extension (not `.zip`)
3. Restart Claude Code CLI
4. Check skill YAML frontmatter is valid

### Skill Runs But Produces Wrong Output

**Problem:** Skill creates files in wrong location or with wrong content

**Solution:**
1. Check required specs exist (API contracts, architecture, etc.)
2. Verify project structure matches expected (Next.js App Router)
3. Read the skill's SKILL.md to understand requirements
4. Check PHR for errors or warnings

### Missing Dependencies

**Problem:** Skill references packages not installed

**Solution:**
1. Run `npm install` commands from skill output
2. Check `package.json` for missing dependencies
3. Install manually: `npm install @tanstack/react-query react-hook-form zod`

### Type Errors

**Problem:** TypeScript errors after skill generates code

**Solution:**
1. Check types match API contracts in `specs/api/rest-endpoints.md`
2. Verify imports are correct
3. Run `npm run type-check` to see all errors
4. Update types in `types/` directory

## Next Steps

After testing the skills:

1. **Iterate on outputs** - Refine generated code as needed
2. **Create more features** - Use skills for authentication, user profile, etc.
3. **Customize skills** - Edit SKILL.md files to match your preferences
4. **Share with team** - Distribute .skill files to team members
5. **Create more skills** - Backend, testing, DevOps, etc.

## Quick Reference

| Skill | Command | Input Required | Output |
|-------|---------|----------------|--------|
| sp.ui-architect | `/sp.ui-architect <feature>` | Feature spec | Component specs, layouts, tokens |
| sp.design-system | `/sp.design-system` | Design tokens | Components, Tailwind config, theme |
| sp.frontend-integrator | `/sp.frontend-integrator <feature>` | API contracts, components | Hooks, API client, wired components |

## Example: Test on Task CRUD Feature

```bash
# Step 1: Design UI
/sp.ui-architect task-crud
# Check: specs/ui/components/task-crud-components.md created

# Step 2: Build components
/sp.design-system
# Check: components/ui/ directory created with Button, Card, etc.

# Step 3: Wire to API
/sp.frontend-integrator task-crud
# Check: hooks/use-tasks.ts created, components wired

# Step 4: Test in browser
cd frontend && npm run dev
# Visit http://localhost:3000/tasks
```
