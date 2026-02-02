# Page Specifications

## Public Pages

### /login
**Layout:** AuthLayout
**Components:** AuthForm (default tab: login)
**Behavior:** 
- On success: redirect to /tasks
- If already logged in: redirect to /tasks
- Link to signup

### /signup
**Layout:** AuthLayout  
**Components:** AuthForm (default tab: signup)
**Behavior:**
- On success: redirect to /tasks
- Validate password strength
- Show terms of service checkbox

## Protected Pages

### /tasks (Dashboard)
**Layout:** DashboardLayout
**Components:** 
- TaskForm (top, sticky)
- FilterTabs
- TaskList
**Empty State:** "No tasks yet. Add your first task above!"
**Loading State:** Skeleton loading for task items
**Error State:** Toast notification if fetch fails

### /tasks/[id]/edit (Edit Modal/Page)
**Components:** TaskForm pre-filled
**Behavior:** 
- Load task data
- Save changes
- Cancel returns to /tasks

## Navigation Structure

### TopNav (DashboardLayout)
- Left: App Logo/Name "TodoAI"
- Right: 
  - User email (dropdown)
  - Logout option
  - Settings (optional)

### Route Guards
- All routes under /tasks/* require authentication
- Unauthenticated users redirected to /login with `?redirect=` param
