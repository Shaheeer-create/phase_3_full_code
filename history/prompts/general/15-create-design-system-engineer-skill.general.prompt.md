---
id: 15
title: Create Design System Engineer Skill
stage: misc
date: 2026-02-01
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: user
command: create a skill for Design System Engineer
labels: ["skill-creation", "design-system", "tailwind", "shadcn", "components"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - path: .claude/skills/sp.design-system/SKILL.md
    status: created
  - path: .claude/skills/sp.design-system/references/component-patterns.md
    status: created
  - path: .claude/skills/sp.design-system/references/tailwind-setup.md
    status: created
  - path: .claude/skills/sp.design-system/references/theme-config.md
    status: created
  - path: .claude/skills/sp.design-system.skill
    status: created
tests:
  - name: none
    status: not_applicable
---

## Prompt

create a skill for Design System Engineer

Role:

Builds reusable components

Sets up Tailwind / shadcn / Radix

Creates theme (colors, dark mode)

Output:

Button, Card, Modal, Input, etc.

Variants & states

Global styles

## Response snapshot

Created the `sp.design-system` skill with comprehensive component building and design system infrastructure workflows:

**Skill Structure:**
- SKILL.md - 8-step workflow for building design systems (15KB)
- references/component-patterns.md - React component patterns with CVA, composition, state management (14KB)
- references/tailwind-setup.md - Complete Tailwind configuration guide (12KB)
- references/theme-config.md - Dark mode and theming implementation (13KB)
- sp.design-system.skill - Packaged distributable (19KB)

**Workflow Steps:**
1. Gather context from UI specs and design tokens
2. Setup design system infrastructure (Tailwind, shadcn/ui, Radix UI)
3. Build reusable components with variants
4. Implement variants and states (loading, error, disabled)
5. Create theme configuration with dark mode
6. Document component APIs
7. Create output files (components/ui/, tailwind.config.js, globals.css)
8. Integration with Spec-Kit workflow

**Key Features:**
- shadcn/ui and Radix UI integration patterns
- Class Variance Authority (CVA) for variant management
- Comprehensive component patterns (Button, Card, Input, Modal, etc.)
- Dark mode implementation with next-themes
- CSS variables strategy for theming
- HSL color format for easy manipulation
- Accessibility patterns (focus management, keyboard navigation, ARIA)
- TypeScript support with forwardRef patterns
- Component composition patterns (Slot, compound components)

**Reference Files:**
- **component-patterns.md**: CVA variants, composition patterns, state management, accessibility, common components
- **tailwind-setup.md**: Installation, configuration, design token integration, custom utilities, plugins, JIT optimization
- **theme-config.md**: Dark mode implementation, CSS variables, theme provider, theme switching, component theming

**Core Components Checklist:**
- Form Controls: Button, Input, Textarea, Select, Checkbox, Radio, Switch, Label
- Layout: Card, Container, Stack, Grid, Separator
- Feedback: Alert, Badge, Progress, Spinner, Skeleton
- Overlay: Modal, Dropdown, Popover, Tooltip, Sheet
- Navigation: Tabs, Breadcrumb, Pagination
- Data Display: Table, Avatar, List

## Outcome

- ✅ Impact: New skill enables systematic component library development with Tailwind CSS, shadcn/ui, and Radix UI, ensuring consistent design systems and reusable components
- 🧪 Tests: Not applicable (skill creation)
- 📁 Files: Created 5 files (SKILL.md, 3 reference files, packaged .skill file)
- 🔁 Next prompts: Test skill with `/sp.design-system`, integrate into project workflow after UI/UX design phase
- 🧠 Reflection: Skill provides comprehensive guidance for building production-ready component libraries. Progressive disclosure pattern keeps SKILL.md focused on workflow while detailed implementation patterns are in reference files. Covers modern React patterns (forwardRef, CVA, composition) and essential tooling (Tailwind, shadcn/ui, Radix UI, next-themes).

## Evaluation notes (flywheel)

- Failure modes observed: None - skill creation completed successfully
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): Test skill on actual project to build component library, validate workflow completeness and identify missing patterns
