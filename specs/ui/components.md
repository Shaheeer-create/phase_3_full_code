# UI Components

## Layout Components

### AuthLayout
- Split screen: left side branding, right side auth forms
- Background gradient
- Responsive: stack on mobile

### DashboardLayout
- Top navigation bar with logo and user menu
- Main content area (padding: 24px)
- Responsive container (max-width: 1200px)

## Feature Components

### TaskList
**Props:** `tasks: Task[], onToggle: (id) => void, onDelete: (id) => void`
- Vertical list of TaskItem components
- Empty state: "No tasks yet. Create one above!"

### TaskItem
**Props:** `task: Task, onToggle: () => void, onEdit: () => void, onDelete: () => void`
- Checkbox (left side)
- Title (strikethrough if completed)
- Description (gray, smaller text, optional)
- Edit/Delete buttons (right side, visible on hover)
- Due date badge (if applicable)

### TaskForm
**Props:** `onSubmit: (title, description) => void`
- Input field for title (placeholder: "What needs to be done?")
- Textarea for description (expandable, optional)
- Submit button: "Add Task"
- Character counter for title (0/200)

### FilterTabs
**Props:** `currentFilter: string, onChange: (filter) => void`
- Tabs: All | Pending | Completed
- Active tab has underline/border highlight

### AuthForm
- Tabs: Login | Sign Up
- Email input
- Password input (with visibility toggle)
- Submit button
- Error message display (red text)
- Loading state on submit

## Shared Components

### Button
- Variants: primary (blue), danger (red), ghost (transparent)
- Sizes: sm, md, lg
- Loading state with spinner

### Input
- Label support
- Error state (red border)
- Helper text
