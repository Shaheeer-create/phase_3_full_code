# UI Design Patterns

Common patterns for web application interfaces with usage guidance.

## Table of Contents
- Dashboard Pattern
- List/Table Pattern
- Form Pattern
- Modal/Dialog Pattern
- Master-Detail Pattern
- Wizard Pattern
- Card Grid Pattern
- Sidebar Navigation Pattern

---

## Dashboard Pattern

**Use when**: Users need an overview of key metrics, status, and quick actions.

**Structure**:
- Header with title and global actions
- Grid of metric cards (2-4 columns)
- Charts and visualizations
- Recent activity feed
- Quick action buttons

**Layout**:
```
┌─────────────────────────────────────┐
│ Dashboard Header                    │
├─────────┬─────────┬─────────┬───────┤
│ Metric  │ Metric  │ Metric  │ Metric│
│ Card    │ Card    │ Card    │ Card  │
├─────────┴─────────┴─────────┴───────┤
│ Chart/Visualization                 │
├─────────────────────┬───────────────┤
│ Recent Activity     │ Quick Actions │
└─────────────────────┴───────────────┘
```

**Responsive**: Stack cards vertically on mobile, 2 columns on tablet.

**Examples**: Analytics dashboard, project overview, admin panel.

---

## List/Table Pattern

**Use when**: Users need to browse, search, filter, and sort collections of items.

**Structure**:
- Search and filter controls
- Sort options
- List/table of items
- Pagination or infinite scroll
- Bulk actions (optional)

**Layout**:
```
┌─────────────────────────────────────┐
│ [Search] [Filters] [Sort] [Actions]│
├─────────────────────────────────────┤
│ ┌─────────────────────────────────┐ │
│ │ Item 1                          │ │
│ ├─────────────────────────────────┤ │
│ │ Item 2                          │ │
│ ├─────────────────────────────────┤ │
│ │ Item 3                          │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ [Pagination]                        │
└─────────────────────────────────────┘
```

**Variants**:
- **List**: Vertical stack, good for mobile
- **Table**: Columns, good for data comparison
- **Grid**: Cards in grid, good for visual content

**Responsive**: Table → List on mobile, reduce visible columns.

**Examples**: Task list, user directory, product catalog.

---

## Form Pattern

**Use when**: Users need to input or edit structured data.

**Structure**:
- Form title and description
- Grouped fields (related fields together)
- Field labels and help text
- Validation messages
- Primary and secondary actions

**Layout**:
```
┌─────────────────────────────────────┐
│ Form Title                          │
│ Description text                    │
├─────────────────────────────────────┤
│ Section 1                           │
│ [Label] [Input field]               │
│ [Label] [Input field]               │
├─────────────────────────────────────┤
│ Section 2                           │
│ [Label] [Input field]               │
│ [Label] [Textarea]                  │
├─────────────────────────────────────┤
│ [Cancel] [Save]                     │
└─────────────────────────────────────┘
```

**Best Practices**:
- Single column for simplicity
- Required fields marked clearly
- Inline validation (real-time feedback)
- Disabled submit until valid
- Auto-save for long forms (optional)

**Responsive**: Full width on mobile, max-width on desktop (600-800px).

**Examples**: User profile, task creation, settings.

---

## Modal/Dialog Pattern

**Use when**: Users need focused attention on a task without leaving current context.

**Structure**:
- Overlay backdrop (dims background)
- Modal container (centered)
- Header with title and close button
- Content area
- Footer with actions

**Layout**:
```
     ┌─────────────────────────┐
     │ Title            [X]    │
     ├─────────────────────────┤
     │                         │
     │ Content area            │
     │                         │
     ├─────────────────────────┤
     │ [Cancel] [Confirm]      │
     └─────────────────────────┘
```

**Types**:
- **Alert**: Simple message, single action
- **Confirm**: Yes/No decision
- **Form**: Data entry in modal
- **Detail**: View item details

**Best Practices**:
- Trap focus inside modal
- Esc key to close
- Click backdrop to close (for non-critical)
- Max-width 600px for readability

**Responsive**: Full screen on mobile, centered on desktop.

**Examples**: Delete confirmation, quick edit, image preview.

---

## Master-Detail Pattern

**Use when**: Users need to browse items while viewing/editing details.

**Structure**:
- Master list (left or top)
- Detail panel (right or bottom)
- Selection state in master
- Actions in detail panel

**Layout (Desktop)**:
```
┌─────────────┬───────────────────────┐
│ Master List │ Detail Panel          │
│             │                       │
│ > Item 1    │ [Detail Header]       │
│   Item 2    │                       │
│   Item 3    │ [Content]             │
│             │                       │
│             │ [Actions]             │
└─────────────┴───────────────────────┘
```

**Layout (Mobile)**:
- List view by default
- Detail slides over list (with back button)
- Or stack vertically

**Split Ratios**:
- 30/70: Brief list, detailed content
- 40/60: Balanced (most common)
- 50/50: Equal importance

**Examples**: Email client, file browser, task manager.

---

## Wizard Pattern

**Use when**: Users need guidance through a multi-step process.

**Structure**:
- Step indicator (progress)
- Current step content
- Navigation (Back, Next, Skip)
- Summary at end

**Layout**:
```
┌─────────────────────────────────────┐
│ Step 1 → Step 2 → Step 3 → Step 4  │
├─────────────────────────────────────┤
│                                     │
│ Current Step Content                │
│                                     │
├─────────────────────────────────────┤
│ [Back] [Skip] [Next]                │
└─────────────────────────────────────┘
```

**Best Practices**:
- Show progress (step X of Y)
- Allow back navigation
- Save progress between steps
- Validate before advancing
- Summary/review before final submit

**Responsive**: Stack vertically on mobile, simplify step indicator.

**Examples**: Onboarding, checkout, setup wizard.

---

## Card Grid Pattern

**Use when**: Users need to browse visual or mixed content.

**Structure**:
- Grid of cards (2-4 columns)
- Each card: image, title, description, actions
- Filters and sort options
- Load more or pagination

**Layout**:
```
┌─────────┬─────────┬─────────┬─────────┐
│ [Image] │ [Image] │ [Image] │ [Image] │
│ Title   │ Title   │ Title   │ Title   │
│ Desc    │ Desc    │ Desc    │ Desc    │
│ [Action]│ [Action]│ [Action]│ [Action]│
├─────────┼─────────┼─────────┼─────────┤
│ [Image] │ [Image] │ [Image] │ [Image] │
│ Title   │ Title   │ Title   │ Title   │
│ Desc    │ Desc    │ Desc    │ Desc    │
│ [Action]│ [Action]│ [Action]│ [Action]│
└─────────┴─────────┴─────────┴─────────┘
```

**Responsive**:
- Desktop: 3-4 columns
- Tablet: 2 columns
- Mobile: 1 column

**Examples**: Product gallery, blog posts, project portfolio.

---

## Sidebar Navigation Pattern

**Use when**: Application has multiple sections or hierarchical navigation.

**Structure**:
- Sidebar (left, fixed or collapsible)
- Main content area (right)
- Top bar with global actions
- Breadcrumbs (optional)

**Layout**:
```
┌─────┬───────────────────────────────┐
│ Nav │ Top Bar                       │
├─────┼───────────────────────────────┤
│     │                               │
│ Sec │ Main Content                  │
│ Sec │                               │
│ Sec │                               │
│     │                               │
└─────┴───────────────────────────────┘
```

**Sidebar Width**:
- Collapsed: 60-80px (icons only)
- Expanded: 240-280px (icons + labels)

**Responsive**:
- Desktop: Persistent sidebar
- Tablet: Collapsible sidebar
- Mobile: Hamburger menu, overlay sidebar

**Examples**: Admin panel, documentation site, SaaS application.

---

## Pattern Selection Guide

| User Need | Recommended Pattern |
|-----------|---------------------|
| Overview of metrics | Dashboard |
| Browse collection | List/Table or Card Grid |
| Input structured data | Form |
| Quick action without navigation | Modal/Dialog |
| Browse + view details | Master-Detail |
| Multi-step process | Wizard |
| Visual content browsing | Card Grid |
| Multi-section app | Sidebar Navigation |

## Combining Patterns

Patterns can be combined:
- **Dashboard + Card Grid**: Metrics at top, content grid below
- **Sidebar + Master-Detail**: Navigation sidebar, master-detail in main area
- **List + Modal**: List view, edit in modal
- **Wizard + Form**: Multi-step form with wizard navigation
