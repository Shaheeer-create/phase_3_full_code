# State Patterns

Comprehensive patterns for handling loading, error, and empty states in React applications.

## Table of Contents
- Loading States
- Error States
- Empty States
- Skeleton Screens
- Progressive Loading
- Error Boundaries
- Toast Notifications

---

## Loading States

### Pattern 1: Inline Loading

Simple loading indicator that replaces content.

```tsx
function TaskList() {
  const { data, isLoading, error } = useTasks()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Spinner className="h-8 w-8" />
        <span className="ml-2">Loading tasks...</span>
      </div>
    )
  }

  if (error) return <ErrorMessage error={error} />

  return <TaskCards tasks={data} />
}
```

**Pros**: Simple, clear loading state
**Cons**: Content disappears during loading, jarring UX

### Pattern 2: Skeleton Screens

Show placeholder content that matches the final layout.

```tsx
function TaskList() {
  const { data, isLoading } = useTasks()

  if (isLoading) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <TaskCardSkeleton key={i} />
        ))}
      </div>
    )
  }

  return <TaskCards tasks={data} />
}

// Skeleton component
function TaskCardSkeleton() {
  return (
    <div className="rounded-lg border p-4 space-y-3">
      <Skeleton className="h-5 w-3/4" />
      <Skeleton className="h-4 w-full" />
      <Skeleton className="h-4 w-2/3" />
    </div>
  )
}

// Reusable Skeleton component
function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-md bg-muted",
        className
      )}
    />
  )
}
```

**Pros**: Better perceived performance, maintains layout
**Cons**: More code, need to match final layout

### Pattern 3: Progressive Loading

Show existing data while fetching updates.

```tsx
function TaskList() {
  const { data, isLoading, isFetching } = useTasks()

  return (
    <div>
      {/* Show loading bar at top when refetching */}
      {isFetching && !isLoading && (
        <div className="h-1 w-full bg-primary/20">
          <div className="h-full w-1/3 bg-primary animate-pulse" />
        </div>
      )}

      {/* Show skeleton only on initial load */}
      {isLoading ? (
        <TaskListSkeleton />
      ) : (
        <TaskCards tasks={data} />
      )}
    </div>
  )
}
```

**Pros**: Best UX, shows progress without hiding content
**Cons**: More complex state management

### Pattern 4: Suspense Boundaries

Use React Suspense for declarative loading states.

```tsx
// Component that suspends
function TaskList() {
  const { data } = useTasks() // Throws promise when loading
  return <TaskCards tasks={data} />
}

// Parent with Suspense boundary
function TasksPage() {
  return (
    <Suspense fallback={<TaskListSkeleton />}>
      <TaskList />
    </Suspense>
  )
}
```

**Pros**: Declarative, composable, clean component code
**Cons**: Requires Suspense-compatible data fetching

### Pattern 5: Button Loading States

Show loading state on buttons during mutations.

```tsx
function CreateTaskForm() {
  const createTask = useCreateTask()

  return (
    <form onSubmit={handleSubmit}>
      <Input name="title" />
      <Button
        type="submit"
        disabled={createTask.isPending}
      >
        {createTask.isPending ? (
          <>
            <Spinner className="mr-2 h-4 w-4" />
            Creating...
          </>
        ) : (
          <>
            <PlusIcon className="mr-2 h-4 w-4" />
            Create Task
          </>
        )}
      </Button>
    </form>
  )
}

// Or with a loading prop on Button component
<Button
  type="submit"
  loading={createTask.isPending}
  loadingText="Creating..."
>
  Create Task
</Button>
```

### Pattern 6: Optimistic Loading

Show success immediately, rollback on error.

```tsx
function TaskCheckbox({ task }: { task: Task }) {
  const toggleTask = useToggleTask()

  return (
    <Checkbox
      checked={task.completed}
      disabled={toggleTask.isPending}
      onCheckedChange={(completed) => {
        // Optimistic update happens in mutation hook
        toggleTask.mutate({ id: task.id, completed: !!completed })
      }}
    />
  )
}
```

---

## Error States

### Pattern 1: Inline Error Message

Show error message in place of content.

```tsx
function TaskList() {
  const { data, error, isLoading } = useTasks()

  if (isLoading) return <Spinner />

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>
          {error.message || 'Failed to load tasks'}
        </AlertDescription>
      </Alert>
    )
  }

  return <TaskCards tasks={data} />
}
```

### Pattern 2: Error with Retry

Allow users to retry failed requests.

```tsx
function TaskList() {
  const { data, error, isLoading, refetch } = useTasks()

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-8 space-y-4">
        <AlertCircle className="h-12 w-12 text-destructive" />
        <div className="text-center">
          <h3 className="font-semibold">Failed to load tasks</h3>
          <p className="text-sm text-muted-foreground">
            {error.message}
          </p>
        </div>
        <Button onClick={() => refetch()}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Try Again
        </Button>
      </div>
    )
  }

  return <TaskCards tasks={data} />
}
```

### Pattern 3: Error Boundary

Catch errors at component boundaries.

```tsx
// components/error-boundary.tsx
import React from 'react'

interface Props {
  children: React.ReactNode
  fallback?: React.ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-8 text-center">
          <h2 className="text-lg font-semibold">Something went wrong</h2>
          <p className="text-sm text-muted-foreground">
            {this.state.error?.message}
          </p>
          <Button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-4"
          >
            Try Again
          </Button>
        </div>
      )
    }

    return this.props.children
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary>
      <TasksPage />
    </ErrorBoundary>
  )
}
```

### Pattern 4: Toast Notifications

Show errors as toast notifications without blocking UI.

```tsx
import { useToast } from '@/components/ui/use-toast'

function CreateTaskForm() {
  const createTask = useCreateTask()
  const { toast } = useToast()

  const handleSubmit = async (data: CreateTaskInput) => {
    try {
      await createTask.mutateAsync(data)
      toast({
        title: "Success",
        description: "Task created successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: error.message || "Failed to create task",
        variant: "destructive",
      })
    }
  }

  return <form onSubmit={handleSubmit}>...</form>
}
```

### Pattern 5: Field-Level Errors

Show errors next to specific form fields.

```tsx
function CreateTaskForm() {
  const createTask = useCreateTask()
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  const handleSubmit = async (data: CreateTaskInput) => {
    try {
      await createTask.mutateAsync(data)
    } catch (error) {
      if (error instanceof ApiError && error.data?.errors) {
        // Backend returns field-specific errors
        setFieldErrors(error.data.errors)
      }
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <Label htmlFor="title">Title</Label>
        <Input
          id="title"
          name="title"
          error={fieldErrors.title}
        />
      </div>
      <Button type="submit">Create</Button>
    </form>
  )
}
```

### Pattern 6: Categorized Errors

Handle different error types differently.

```tsx
function TaskList() {
  const { data, error } = useTasks()

  if (error) {
    if (error instanceof ApiError) {
      switch (error.status) {
        case 401:
          return <LoginPrompt />
        case 403:
          return <AccessDenied />
        case 404:
          return <NotFound message="Tasks not found" />
        case 500:
          return <ServerError onRetry={refetch} />
        default:
          return <GenericError error={error} />
      }
    }
    return <GenericError error={error} />
  }

  return <TaskCards tasks={data} />
}
```

---

## Empty States

### Pattern 1: Basic Empty State

Simple message when no data exists.

```tsx
function TaskList() {
  const { data, isLoading } = useTasks()

  if (isLoading) return <Spinner />

  if (!data?.length) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center">
        <InboxIcon className="h-12 w-12 text-muted-foreground" />
        <h3 className="mt-4 text-lg font-semibold">No tasks yet</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          Get started by creating your first task
        </p>
      </div>
    )
  }

  return <TaskCards tasks={data} />
}
```

### Pattern 2: Empty State with Action

Encourage users to take action.

```tsx
function TaskList() {
  const { data, isLoading } = useTasks()
  const [isCreateOpen, setIsCreateOpen] = useState(false)

  if (!data?.length && !isLoading) {
    return (
      <EmptyState
        icon={<InboxIcon />}
        title="No tasks yet"
        description="Create your first task to get started"
        action={
          <Button onClick={() => setIsCreateOpen(true)}>
            <PlusIcon className="mr-2 h-4 w-4" />
            Create Task
          </Button>
        }
      />
    )
  }

  return (
    <>
      <TaskCards tasks={data} />
      <CreateTaskDialog open={isCreateOpen} onOpenChange={setIsCreateOpen} />
    </>
  )
}

// Reusable EmptyState component
interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: React.ReactNode
}

function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      {icon && <div className="text-muted-foreground">{icon}</div>}
      <h3 className="mt-4 text-lg font-semibold">{title}</h3>
      {description && (
        <p className="mt-2 text-sm text-muted-foreground max-w-sm">
          {description}
        </p>
      )}
      {action && <div className="mt-6">{action}</div>}
    </div>
  )
}
```

### Pattern 3: Empty Search Results

Different message for filtered/searched empty states.

```tsx
function TaskList() {
  const [search, setSearch] = useState('')
  const { data, isLoading } = useTasks({ search })

  if (isLoading) return <Spinner />

  if (!data?.length) {
    if (search) {
      return (
        <EmptyState
          icon={<SearchIcon />}
          title="No results found"
          description={`No tasks match "${search}"`}
          action={
            <Button variant="outline" onClick={() => setSearch('')}>
              Clear Search
            </Button>
          }
        />
      )
    }

    return (
      <EmptyState
        icon={<InboxIcon />}
        title="No tasks yet"
        description="Create your first task to get started"
        action={<Button>Create Task</Button>}
      />
    )
  }

  return <TaskCards tasks={data} />
}
```

### Pattern 4: Contextual Empty States

Show different empty states based on context.

```tsx
function TaskList({ filter }: { filter: 'all' | 'completed' | 'active' }) {
  const { data } = useTasks({ completed: filter === 'completed' ? true : filter === 'active' ? false : undefined })

  if (!data?.length) {
    const emptyStates = {
      all: {
        title: "No tasks yet",
        description: "Create your first task to get started",
        action: <Button>Create Task</Button>,
      },
      completed: {
        title: "No completed tasks",
        description: "Complete a task to see it here",
      },
      active: {
        title: "No active tasks",
        description: "All tasks are completed!",
        icon: <CheckCircleIcon className="text-green-500" />,
      },
    }

    const state = emptyStates[filter]
    return <EmptyState {...state} />
  }

  return <TaskCards tasks={data} />
}
```

---

## Combined State Patterns

### Pattern 1: Comprehensive State Handling

Handle all states in one component.

```tsx
function TaskList() {
  const { data, isLoading, error, refetch } = useTasks()

  // Loading state
  if (isLoading) {
    return <TaskListSkeleton />
  }

  // Error state
  if (error) {
    return (
      <ErrorState
        error={error}
        onRetry={refetch}
      />
    )
  }

  // Empty state
  if (!data?.length) {
    return (
      <EmptyState
        title="No tasks yet"
        description="Create your first task to get started"
        action={<CreateTaskButton />}
      />
    )
  }

  // Success state
  return <TaskCards tasks={data} />
}
```

### Pattern 2: State Machine Pattern

Use explicit state machine for complex state logic.

```tsx
type State =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'empty' }
  | { status: 'success'; data: Task[] }

function TaskList() {
  const query = useTasks()

  const state: State = query.isLoading
    ? { status: 'loading' }
    : query.error
    ? { status: 'error', error: query.error }
    : !query.data?.length
    ? { status: 'empty' }
    : { status: 'success', data: query.data }

  switch (state.status) {
    case 'loading':
      return <TaskListSkeleton />
    case 'error':
      return <ErrorState error={state.error} />
    case 'empty':
      return <EmptyState />
    case 'success':
      return <TaskCards tasks={state.data} />
  }
}
```

---

## Best Practices

### Loading States
1. **Use skeletons** for better perceived performance
2. **Show progress** for long operations
3. **Disable interactions** during loading
4. **Keep layout stable** - avoid content shifts
5. **Progressive loading** for refetches

### Error States
1. **Be specific** - explain what went wrong
2. **Provide actions** - retry, contact support, go back
3. **Log errors** - send to monitoring service
4. **Categorize errors** - handle different types differently
5. **Don't block UI** - use toasts for non-critical errors

### Empty States
1. **Be encouraging** - positive, helpful tone
2. **Provide context** - explain why it's empty
3. **Offer actions** - help users get started
4. **Use illustrations** - make it visually appealing
5. **Differentiate** - different messages for search vs no data

### General
1. **Consistent patterns** - use same patterns across app
2. **Accessibility** - announce state changes to screen readers
3. **Test all states** - loading, error, empty, success
4. **Graceful degradation** - handle edge cases
5. **User feedback** - always acknowledge user actions
