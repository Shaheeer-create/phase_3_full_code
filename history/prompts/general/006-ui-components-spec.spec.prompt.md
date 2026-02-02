---
id: 006
title: UI Components Spec
stage: spec
date: 2026-01-31
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: Shaheer Naeem
command: none
labels: ["ui", "components", "react", "nextjs", "design"]
links:
  spec: specs/ui/components.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/ui/components.md
tests:
  - none
---

## Prompt

Define the UI component specifications for the Todo App including layout components (AuthLayout, DashboardLayout), feature components (TaskList, TaskItem, TaskForm, FilterTabs, AuthForm), and shared components (Button, Input) with props, behavior, and styling requirements.

## Response snapshot

Created UI components specification with:

**Layout Components:**
- AuthLayout: Split screen (branding left, forms right), responsive stacking on mobile
- DashboardLayout: Top nav with logo/user menu, main content area (max-width 1200px, padding 24px)

**Feature Components:**
- TaskList: Vertical list with empty state, takes tasks array and callbacks
- TaskItem: Checkbox, title (strikethrough if completed), description, edit/delete buttons on hover
- TaskForm: Title input (200 char limit with counter), expandable textarea, submit button
- FilterTabs: All/Pending/Completed with active underline
- AuthForm: Login/Signup tabs, email/password inputs, visibility toggle, error display, loading state

**Shared Components:**
- Button: Variants (primary/danger/ghost), sizes (sm/md/lg), loading spinner
- Input: Label support, error state (red border), helper text

## Outcome

- ✅ Impact: Established complete component library specification for consistent UI implementation
- 🧪 Tests: None (specification document)
- 📁 Files: Created specs/ui/components.md
- 🔁 Next prompts: Implement React components with TypeScript, create Storybook stories, add Tailwind styling
- 🧠 Reflection: Clear prop interfaces enable type-safe component development

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add accessibility requirements (ARIA labels, keyboard navigation)
