---
id: 14
title: Create UI/UX Architect Skill
stage: misc
date: 2026-02-01
surface: agent
model: Claude Sonnet 4.5
feature: none
branch: master
user: user
command: create a skill for UI/UX Architect
labels: ["skill-creation", "ui-ux", "design-system"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - path: .claude/skills/sp.ui-architect/SKILL.md
    status: created
  - path: .claude/skills/sp.ui-architect/references/design-patterns.md
    status: created
  - path: .claude/skills/sp.ui-architect/references/accessibility-guidelines.md
    status: created
  - path: .claude/skills/sp.ui-architect.skill
    status: created
tests:
  - name: none
    status: not_applicable
---

## Prompt

create a skill for UI/UX Architect

Role:

Designs layout systems

Chooses design patterns (dashboard, cards, flows)

Defines spacing, typography, hierarchy

Output:

Component structure

Page layout plans

Design tokens (sizes, variants)

## Response snapshot

Created the `sp.ui-architect` skill with comprehensive UI/UX design workflow:

**Skill Structure:**
- SKILL.md - Main workflow with 8-step process for designing UI/UX
- references/design-patterns.md - 8 common UI patterns (Dashboard, List/Table, Form, Modal, Master-Detail, Wizard, Card Grid, Sidebar Navigation)
- references/accessibility-guidelines.md - WCAG AA compliance guidelines with implementation examples
- sp.ui-architect.skill - Packaged distributable (12KB)

**Workflow Steps:**
1. Gather context from specs
2. Design component hierarchy
3. Choose design patterns
4. Define design tokens (spacing, typography, colors, variants)
5. Create page layout plans with wireframes
6. Document accessibility requirements
7. Create output files in specs/ui/
8. Integration with Spec-Kit workflow

**Key Features:**
- Integrates with existing Spec-Kit Plus workflow (runs after /sp.specify, before /sp.plan)
- Creates PHR in history/prompts/<feature-name>/
- Suggests ADR for significant design system decisions
- Tailwind CSS integration guidance
- Responsive design specifications (desktop, tablet, mobile)
- WCAG AA accessibility compliance

**Output Files:**
- specs/ui/components/<feature-name>-components.md
- specs/ui/layouts/<feature-name>-layouts.md
- specs/ui/design-tokens.md

## Outcome

- ✅ Impact: New skill enables systematic UI/UX design before implementation, ensuring consistent design systems and accessibility compliance
- 🧪 Tests: Not applicable (skill creation)
- 📁 Files: Created 4 files (SKILL.md, 2 reference files, packaged .skill file)
- 🔁 Next prompts: Test skill with `/sp.ui-architect <feature-name>`, integrate into project workflow
- 🧠 Reflection: Skill follows progressive disclosure pattern with core workflow in SKILL.md and detailed reference material in separate files. Comprehensive coverage of design patterns and accessibility guidelines provides practical guidance for UI/UX design work.

## Evaluation notes (flywheel)

- Failure modes observed: None - skill creation completed successfully
- Graders run and results (PASS/FAIL): Not applicable
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): Test skill on actual feature (e.g., task-crud) to validate workflow and identify improvements
