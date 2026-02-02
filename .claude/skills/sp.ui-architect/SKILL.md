---
name: sp.ui-architect
description: Design layout systems, component hierarchies, and design tokens for features. Use when the user needs UI/UX design work including: (1) Creating component structures and hierarchies, (2) Choosing design patterns (dashboard, cards, forms, modals, flows), (3) Defining design tokens (spacing, typography, colors, variants), (4) Creating page layout plans with wireframes, (5) Defining responsive behavior, or (6) Documenting accessibility requirements. Should be run after feature specs exist and before implementation planning.
---

# UI/UX Architect

Design layout systems, component hierarchies, page layouts, and design tokens for features following specification-driven development principles.

## Workflow

### 1. Gather Context

Read existing specifications:
- `specs/features/<feature-name>.md` - Feature requirements (REQUIRED)
- `specs/architecture.md` - System architecture and constraints
- `specs/ui/design-tokens.md` - Existing design system (if exists)
- `specs/ui/components.md` - Existing component library (if exists)
- Project CLAUDE.md - Tech stack constraints (e.g., Tailwind CSS, Next.js)

Extract:
- User flows and interactions
- Data to display
- Actions users can perform
- Tech stack constraints (CSS framework, component library)

### 2. Design Component Hierarchy

Create component structure with clear responsibilities:

```markdown
## Component Hierarchy

### [FeatureName]Page (Page Component)
- **Responsibility**: Layout container, data fetching, routing
- **Children**: [FeatureHeader], [FeatureList], [FeatureForm]

### [FeatureHeader] (Presentational)
- **Responsibility**: Title, actions, filters
- **Props**: title, onAction, filters
- **Children**: [Button], [FilterDropdown]

### [FeatureList] (Container)
- **Responsibility**: Display items, handle selection
- **Props**: items[], onSelect, loading
- **Children**: [FeatureCard]

### [FeatureCard] (Presentational)
- **Responsibility**: Display single item
- **Props**: item, selected, onClick
- **Variants**: default, compact, expanded
```

**Principles**:
- Container components handle logic and state
- Presentational components handle display
- One responsibility per component
- Clear parent-child relationships

### 3. Choose Design Patterns

Select appropriate patterns for the feature. See [references/design-patterns.md](references/design-patterns.md) for detailed guidance.

Common patterns:
- **Dashboard**: Overview with cards, metrics, charts
- **List/Table**: Browsing collections with filters, sorting, pagination
- **Form**: Data entry with validation, multi-step flows
- **Modal/Dialog**: Focused tasks, confirmations, details
- **Master-Detail**: List with side panel for details
- **Wizard**: Multi-step guided process

Document pattern choice with rationale:
```markdown
## Design Pattern: Master-Detail

**Rationale**: Users need to browse tasks while viewing/editing details without losing context.

**Layout**:
- Left: Task list (40% width)
- Right: Task detail panel (60% width)
- Mobile: Stack vertically, detail slides over list
```

### 4. Define Design Tokens

Create or update design tokens for consistency. If `specs/ui/design-tokens.md` exists, update it. Otherwise, create it.

```markdown
## Spacing Scale
- xs: 0.25rem (4px)
- sm: 0.5rem (8px)
- md: 1rem (16px)
- lg: 1.5rem (24px)
- xl: 2rem (32px)
- 2xl: 3rem (48px)

## Typography Scale
- heading-1: 2.5rem (40px), font-bold, line-height: 1.2
- heading-2: 2rem (32px), font-bold, line-height: 1.3
- heading-3: 1.5rem (24px), font-semibold, line-height: 1.4
- body: 1rem (16px), font-normal, line-height: 1.5
- small: 0.875rem (14px), font-normal, line-height: 1.5
- label: 0.875rem (14px), font-medium, line-height: 1.5

## Color Tokens (Semantic)
- primary: Brand color for main actions
- secondary: Supporting actions
- success: Positive feedback, completed states
- warning: Caution, pending states
- error: Errors, destructive actions
- neutral: Text, borders, backgrounds (50-900 scale)

## Component Variants
### Button
- sizes: sm, md, lg
- variants: primary, secondary, outline, ghost, danger

### Card
- sizes: default, compact
- variants: default, elevated, bordered
```

**Tailwind CSS Integration**: Map tokens to Tailwind classes:
- Spacing: Use Tailwind's default scale (matches above)
- Typography: Use Tailwind's text-* and font-* utilities
- Colors: Extend Tailwind config with semantic colors

### 5. Create Page Layout Plans

Design layouts with wireframe descriptions for each page/view.

```markdown
## [FeatureName] Page Layout

### Desktop (≥1024px)
┌─────────────────────────────────────────┐
│ Header (h-16)                           │
│ [Logo] [Nav] [User Menu]               │
├─────────────────────────────────────────┤
│ Main Content (flex-1)                   │
│ ┌─────────────┬─────────────────────┐  │
│ │ List (40%)  │ Detail Panel (60%)  │  │
│ │             │                     │  │
│ │ [Filters]   │ [Detail Header]     │  │
│ │ [Items...]  │ [Content]           │  │
│ │             │ [Actions]           │  │
│ └─────────────┴─────────────────────┘  │
└─────────────────────────────────────────┘

### Tablet (768px - 1023px)
- Stack list and detail vertically
- List: Full width, collapsible
- Detail: Slides up from bottom

### Mobile (<768px)
- Single column layout
- List view by default
- Detail view replaces list (with back button)
- Bottom navigation for main actions
```

**Include**:
- Breakpoint-specific layouts
- Spacing and sizing (use design tokens)
- Component placement
- Responsive behavior (stack, hide, collapse)

### 6. Document Accessibility

Include WCAG AA compliance requirements. See [references/accessibility-guidelines.md](references/accessibility-guidelines.md) for detailed guidance.

```markdown
## Accessibility Requirements

### Keyboard Navigation
- All interactive elements accessible via Tab
- Modal traps focus, Esc to close
- Arrow keys for list navigation

### Screen Reader Support
- Semantic HTML (nav, main, article, button)
- ARIA labels for icon-only buttons
- ARIA live regions for dynamic updates
- Alt text for images

### Visual Accessibility
- Color contrast ratio ≥4.5:1 for text
- Focus indicators visible (2px outline)
- Text resizable to 200% without loss of function
- No information conveyed by color alone

### Interactive Elements
- Touch targets ≥44x44px
- Error messages associated with inputs
- Loading states announced to screen readers
```

### 7. Create Output Files

Generate specification files in the appropriate directories:

**Component Structure**: `specs/ui/components/<feature-name>-components.md`
```markdown
# [Feature Name] Components

## Component Hierarchy
[Component tree with responsibilities]

## Component Specifications
[Detailed specs for each component: props, variants, states]

## Component Interactions
[How components communicate and handle events]
```

**Page Layouts**: `specs/ui/layouts/<feature-name>-layouts.md`
```markdown
# [Feature Name] Layouts

## Design Pattern
[Pattern choice and rationale]

## Page Layouts
[Wireframes for each page/view with breakpoints]

## Responsive Behavior
[How layout adapts across devices]

## Navigation Flow
[How users move between views]
```

**Design Tokens**: `specs/ui/design-tokens.md` (create or update)
```markdown
# Design Tokens

## Spacing Scale
[Token definitions]

## Typography Scale
[Token definitions]

## Color Tokens
[Semantic color definitions]

## Component Variants
[Variant definitions for reusable components]

## Framework Integration
[How tokens map to CSS framework (e.g., Tailwind)]
```

### 8. Integration with Workflow

**Before running this skill**:
- Feature spec must exist (`/sp.specify` completed)
- Requirements and user flows documented

**After running this skill**:
- Run `/sp.plan` to create implementation plan
- UI specs inform component implementation tasks

**PHR Creation**:
- Create PHR in `history/prompts/<feature-name>/`
- Stage: `spec` (design is part of specification phase)
- Include links to created UI spec files

**ADR Suggestions**:
Suggest ADR for significant design system decisions:
- New design pattern adoption
- Design token system changes
- Component library choices
- Accessibility approach

Example: "📋 Architectural decision detected: Adopting Master-Detail pattern for task management. Document reasoning? Run `/sp.adr master-detail-pattern`"

## Usage Examples

Basic usage:
```
/sp.ui-architect task-crud
```

With specific pattern:
```
/sp.ui-architect authentication --pattern=modal
```

With design token update:
```
/sp.ui-architect dashboard --tokens
```

## Success Criteria

- [ ] Component hierarchy defined with clear responsibilities
- [ ] Design pattern chosen with rationale
- [ ] Design tokens defined or updated
- [ ] Page layouts include desktop, tablet, mobile views
- [ ] Responsive behavior documented
- [ ] Accessibility requirements specified (WCAG AA)
- [ ] Output files created in `specs/ui/`
- [ ] PHR created in `history/prompts/<feature-name>/`
- [ ] ADR suggested for significant design decisions

## References

- [Design Patterns](references/design-patterns.md) - Common UI patterns and when to use them
- [Accessibility Guidelines](references/accessibility-guidelines.md) - WCAG AA compliance checklist
