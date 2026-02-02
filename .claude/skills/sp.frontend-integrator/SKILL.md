---
name: sp.frontend-integrator
description: Wire UI components to real data and APIs. Use when the user needs to: (1) Connect components to backend APIs, (2) Create custom hooks for data fetching, (3) Implement loading, error, and empty states, (4) Handle form submissions and mutations, (5) Manage client-side state, (6) Implement real-time updates or polling, or (7) Add optimistic updates and caching. Should be run after components are built and API contracts are defined.
---

# Frontend Integrator

Wire UI components to real data sources, handle API integration, and manage application state for production-ready interactive UIs.

## Workflow

### 1. Gather Context

Read existing specifications and implementations:
- `specs/api/rest-endpoints.md` - API contracts and endpoints (REQUIRED)
- `specs/features/<feature-name>.md` - Feature requirements
- `specs/architecture.md` - Auth flow, API base URL, error handling
- `components/ui/` - Existing UI components
- Project CLAUDE.md - Tech stack (Next.js, React Query, etc.)

Extract:
- API endpoints and request/response schemas
- Authentication requirements (JWT, headers)
- Data models and relationships
- Required user interactions (CRUD operations)
- Real-time requirements (if any)

### 2. Choose Data Fetching Strategy

Select appropriate data fetching approach based on requirements. See [references/data-fetching-strategies.md](references/data-fetching-strategies.md) for detailed comparison.

**Options**:

**React Query / TanStack Query** (Recommended):
- Automatic caching and background refetching
- Loading and error states built-in
- Optimistic updates
- Pagination and infinite scroll support
- Best for: Most applications with server state

**SWR (Stale-While-Revalidate)**:
- Similar to React Query, lighter weight
- Focus on cache-first approach
- Built by Vercel, great Next.js integration
- Best for: Next.js apps, simpler requirements

**Native Fetch with Custom Hooks**:
- Full control, no dependencies
- Manual state management
- Best for: Simple apps, learning, specific requirements

**Server Components (Next.js 13+)**:
- Fetch data on server, no client-side JS
- Automatic caching and revalidation
- Best for: Static/semi-static data, SEO-critical pages

**Decision Matrix**:
```
Complex state + mutations → React Query
Next.js + simple fetching → SWR or Server Components
Full control needed → Custom hooks
Static data → Server Components
```

### 3. Setup Data Fetching Infrastructure

Install and configure chosen data fetching library.

#### React Query Setup

```bash
npm install @tanstack/react-query
npm install @tanstack/react-query-devtools
```

Create query client provider:

```tsx
// app/providers.tsx
"use client"

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000, // 1 minute
        retry: 1,
      },
    },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

Wrap app:

```tsx
// app/layout.tsx
import { Providers } from './providers'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
```

#### API Client Setup

Create centralized API client:

```ts
// lib/api-client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export async function apiClient<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`

  // Get auth token (from localStorage, cookie, or context)
  const token = localStorage.getItem('auth_token')

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options?.headers,
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new ApiError(
      error.message || 'An error occurred',
      response.status,
      error
    )
  }

  return response.json()
}
```

### 4. Create Data Fetching Hooks

Build custom hooks for each API endpoint. See [references/hook-patterns.md](references/hook-patterns.md) for detailed patterns.

#### Query Hook Pattern (GET)

```tsx
// hooks/use-tasks.ts
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

interface Task {
  id: string
  title: string
  completed: boolean
  created_at: string
}

export function useTasks() {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: () => apiClient<Task[]>('/api/tasks'),
  })
}

// Usage in component
function TaskList() {
  const { data: tasks, isLoading, error } = useTasks()

  if (isLoading) return <Spinner />
  if (error) return <ErrorMessage error={error} />
  if (!tasks?.length) return <EmptyState />

  return (
    <ul>
      {tasks.map(task => (
        <TaskCard key={task.id} task={task} />
      ))}
    </ul>
  )
}
```

#### Mutation Hook Pattern (POST/PUT/DELETE)

```tsx
// hooks/use-create-task.ts
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

interface CreateTaskInput {
  title: string
  description?: string
}

export function useCreateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (input: CreateTaskInput) =>
      apiClient('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(input),
      }),
    onSuccess: () => {
      // Invalidate and refetch tasks
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}

// Usage in component
function CreateTaskForm() {
  const createTask = useCreateTask()

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)

    try {
      await createTask.mutateAsync({
        title: formData.get('title') as string,
      })
      // Success: form reset, show toast, etc.
    } catch (error) {
      // Error handled by mutation
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Input name="title" required />
      <Button type="submit" loading={createTask.isPending}>
        Create Task
      </Button>
      {createTask.error && <ErrorMessage error={createTask.error} />}
    </form>
  )
}
```

### 5. Implement State Patterns

Handle loading, error, and empty states consistently. See [references/state-patterns.md](references/state-patterns.md) for comprehensive patterns.

#### Loading States

```tsx
// Pattern 1: Inline loading
function TaskList() {
  const { data, isLoading } = useTasks()

  if (isLoading) {
    return <Skeleton count={3} />
  }

  return <TaskCards tasks={data} />
}

// Pattern 2: Suspense (React 18+)
function TaskList() {
  const { data } = useTasks()
  return <TaskCards tasks={data} />
}

// Wrap with Suspense boundary
<Suspense fallback={<Skeleton count={3} />}>
  <TaskList />
</Suspense>

// Pattern 3: Progressive loading
function TaskList() {
  const { data, isLoading, isFetching } = useTasks()

  return (
    <div>
      {isFetching && <LoadingBar />}
      <TaskCards tasks={data || []} />
    </div>
  )
}
```

#### Error States

```tsx
// Pattern 1: Inline error
function TaskList() {
  const { data, error } = useTasks()

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error loading tasks</AlertTitle>
        <AlertDescription>{error.message}</AlertDescription>
      </Alert>
    )
  }

  return <TaskCards tasks={data} />
}

// Pattern 2: Error boundary
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />
    }
    return this.props.children
  }
}

// Pattern 3: Toast notifications
function CreateTaskForm() {
  const createTask = useCreateTask()
  const { toast } = useToast()

  const handleSubmit = async (data) => {
    try {
      await createTask.mutateAsync(data)
      toast({ title: "Task created successfully" })
    } catch (error) {
      toast({
        title: "Error creating task",
        description: error.message,
        variant: "destructive",
      })
    }
  }
}
```

#### Empty States

```tsx
function TaskList() {
  const { data: tasks, isLoading } = useTasks()

  if (isLoading) return <Skeleton />

  if (!tasks?.length) {
    return (
      <EmptyState
        icon={<InboxIcon />}
        title="No tasks yet"
        description="Create your first task to get started"
        action={
          <Button onClick={openCreateDialog}>
            <PlusIcon /> Create Task
          </Button>
        }
      />
    )
  }

  return <TaskCards tasks={tasks} />
}
```

### 6. Handle Forms and Mutations

Implement form handling with validation and submission. See [references/form-patterns.md](references/form-patterns.md) for detailed patterns.

#### React Hook Form Integration

```bash
npm install react-hook-form zod @hookform/resolvers
```

```tsx
// components/create-task-form.tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'

const taskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(100),
  description: z.string().optional(),
  priority: z.enum(['low', 'medium', 'high']),
})

type TaskFormData = z.infer<typeof taskSchema>

export function CreateTaskForm({ onSuccess }: { onSuccess?: () => void }) {
  const createTask = useCreateTask()

  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: '',
      description: '',
      priority: 'medium',
    },
  })

  const onSubmit = async (data: TaskFormData) => {
    try {
      await createTask.mutateAsync(data)
      form.reset()
      onSuccess?.()
    } catch (error) {
      // Error handled by mutation
    }
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label htmlFor="title">Title</Label>
        <Input
          id="title"
          {...form.register('title')}
          error={form.formState.errors.title?.message}
        />
      </div>

      <div>
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          {...form.register('description')}
        />
      </div>

      <div>
        <Label htmlFor="priority">Priority</Label>
        <Select {...form.register('priority')}>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </Select>
      </div>

      <Button
        type="submit"
        loading={createTask.isPending}
        disabled={!form.formState.isValid}
      >
        Create Task
      </Button>
    </form>
  )
}
```

### 7. Implement Optimistic Updates

Provide instant feedback before server confirmation.

```tsx
// hooks/use-toggle-task.ts
export function useToggleTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, completed }: { id: string; completed: boolean }) =>
      apiClient(`/api/tasks/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ completed }),
      }),

    // Optimistic update
    onMutate: async ({ id, completed }) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['tasks'] })

      // Snapshot previous value
      const previousTasks = queryClient.getQueryData(['tasks'])

      // Optimistically update
      queryClient.setQueryData(['tasks'], (old: Task[]) =>
        old.map(task =>
          task.id === id ? { ...task, completed } : task
        )
      )

      return { previousTasks }
    },

    // Rollback on error
    onError: (err, variables, context) => {
      queryClient.setQueryData(['tasks'], context?.previousTasks)
    },

    // Refetch on success or error
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}
```

### 8. Create Output Files

Generate or update integration files:

**Custom Hooks**: `hooks/use-<resource>.ts`
- Data fetching hooks (queries)
- Mutation hooks (create, update, delete)
- Optimistic update logic
- Error handling

**API Client**: `lib/api-client.ts`
- Centralized fetch wrapper
- Auth token injection
- Error handling
- Type-safe requests

**Type Definitions**: `types/<resource>.ts`
- API request/response types
- Form data types
- Shared interfaces

**Components**: Update existing components
- Wire components to hooks
- Add loading/error/empty states
- Handle form submissions
- Add optimistic updates

**Providers**: `app/providers.tsx`
- Query client provider
- Auth provider (if needed)
- Toast provider

### 9. Integration with Workflow

**Before running this skill**:
- UI components built (`/sp.design-system` completed)
- API contracts defined in `specs/api/rest-endpoints.md`
- Feature requirements documented

**After running this skill**:
- Components connected to real data
- Interactive UI ready for testing
- Run `/sp.implement` to complete remaining tasks

**PHR Creation**:
- Create PHR in `history/prompts/<feature-name>/`
- Stage: `green` (implementation work)
- Include links to created hooks and updated components

**ADR Suggestions**:
Suggest ADR for significant integration decisions:
- Data fetching library choice (React Query vs SWR vs custom)
- State management approach
- Caching strategy
- Real-time update mechanism

Example: "📋 Architectural decision detected: Adopting React Query for server state management. Document reasoning? Run `/sp.adr react-query-adoption`"

## Usage Examples

Basic usage:
```
/sp.frontend-integrator task-crud
```

Specific feature:
```
/sp.frontend-integrator authentication
```

With specific strategy:
```
/sp.frontend-integrator --strategy=react-query
```

## Success Criteria

- [ ] Data fetching infrastructure set up (React Query/SWR/custom)
- [ ] API client configured with auth and error handling
- [ ] Custom hooks created for all API endpoints
- [ ] Loading states implemented consistently
- [ ] Error states handled with user feedback
- [ ] Empty states designed and implemented
- [ ] Forms connected with validation
- [ ] Mutations working with optimistic updates
- [ ] Type safety maintained throughout
- [ ] PHR created
- [ ] ADR suggested for significant decisions

## Common Integration Patterns

**CRUD Operations**:
- [ ] List/Read: `useTasks()` query hook
- [ ] Create: `useCreateTask()` mutation hook
- [ ] Update: `useUpdateTask()` mutation hook
- [ ] Delete: `useDeleteTask()` mutation hook

**Advanced Patterns**:
- [ ] Pagination: `useInfiniteQuery` or page-based
- [ ] Search/Filter: Debounced queries
- [ ] Real-time: WebSocket or polling
- [ ] File upload: Multipart form data
- [ ] Batch operations: Multiple mutations

## References

- [Data Fetching Strategies](references/data-fetching-strategies.md) - Comparison of React Query, SWR, custom hooks
- [Hook Patterns](references/hook-patterns.md) - Query and mutation hook patterns
- [State Patterns](references/state-patterns.md) - Loading, error, empty state patterns
- [Form Patterns](references/form-patterns.md) - Form handling with React Hook Form
