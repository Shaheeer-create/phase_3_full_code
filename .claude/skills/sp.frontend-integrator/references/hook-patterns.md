# Hook Patterns

Comprehensive patterns for building custom data fetching and mutation hooks with React Query.

## Table of Contents
- Query Hook Patterns
- Mutation Hook Patterns
- Advanced Query Patterns
- Error Handling
- Type Safety
- Testing Hooks

---

## Query Hook Patterns

### Basic Query Hook

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

// Usage
function TaskList() {
  const { data: tasks, isLoading, error } = useTasks()

  if (isLoading) return <Spinner />
  if (error) return <ErrorMessage error={error} />

  return (
    <ul>
      {tasks?.map(task => (
        <TaskCard key={task.id} task={task} />
      ))}
    </ul>
  )
}
```

### Parameterized Query Hook

```tsx
// hooks/use-task.ts
export function useTask(taskId: string) {
  return useQuery({
    queryKey: ['tasks', taskId],
    queryFn: () => apiClient<Task>(`/api/tasks/${taskId}`),
    enabled: !!taskId, // Only fetch if taskId exists
  })
}

// Usage
function TaskDetail({ taskId }: { taskId: string }) {
  const { data: task } = useTask(taskId)
  return <div>{task?.title}</div>
}
```

### Query with Filters

```tsx
// hooks/use-tasks.ts
interface TaskFilters {
  completed?: boolean
  priority?: 'low' | 'medium' | 'high'
  search?: string
}

export function useTasks(filters: TaskFilters = {}) {
  return useQuery({
    queryKey: ['tasks', filters],
    queryFn: () => {
      const params = new URLSearchParams()
      if (filters.completed !== undefined) {
        params.append('completed', String(filters.completed))
      }
      if (filters.priority) {
        params.append('priority', filters.priority)
      }
      if (filters.search) {
        params.append('search', filters.search)
      }
      return apiClient<Task[]>(`/api/tasks?${params}`)
    },
  })
}

// Usage
function TaskList() {
  const [filters, setFilters] = useState<TaskFilters>({})
  const { data: tasks } = useTasks(filters)

  return (
    <div>
      <FilterBar filters={filters} onChange={setFilters} />
      <TaskCards tasks={tasks} />
    </div>
  )
}
```

### Query with Dependent Data

```tsx
// hooks/use-task-comments.ts
export function useTaskComments(taskId: string | undefined) {
  return useQuery({
    queryKey: ['tasks', taskId, 'comments'],
    queryFn: () => apiClient<Comment[]>(`/api/tasks/${taskId}/comments`),
    enabled: !!taskId, // Only fetch when taskId is available
  })
}

// Usage
function TaskDetail() {
  const { data: task } = useTask(taskId)
  const { data: comments } = useTaskComments(task?.id)

  return (
    <div>
      <h1>{task?.title}</h1>
      <CommentList comments={comments} />
    </div>
  )
}
```

### Query with Polling

```tsx
// hooks/use-task-status.ts
export function useTaskStatus(taskId: string) {
  return useQuery({
    queryKey: ['tasks', taskId, 'status'],
    queryFn: () => apiClient<TaskStatus>(`/api/tasks/${taskId}/status`),
    refetchInterval: 5000, // Poll every 5 seconds
    refetchIntervalInBackground: false, // Stop polling when tab is inactive
  })
}

// Usage
function TaskStatusBadge({ taskId }: { taskId: string }) {
  const { data: status } = useTaskStatus(taskId)
  return <Badge>{status?.state}</Badge>
}
```

---

## Mutation Hook Patterns

### Create Mutation

```tsx
// hooks/use-create-task.ts
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'

interface CreateTaskInput {
  title: string
  description?: string
  priority?: 'low' | 'medium' | 'high'
}

export function useCreateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (input: CreateTaskInput) =>
      apiClient<Task>('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(input),
      }),
    onSuccess: () => {
      // Invalidate tasks list to trigger refetch
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}

// Usage
function CreateTaskForm() {
  const createTask = useCreateTask()

  const handleSubmit = async (data: CreateTaskInput) => {
    try {
      await createTask.mutateAsync(data)
      // Success: show toast, close modal, etc.
    } catch (error) {
      // Error: show error message
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <Input name="title" />
      <Button type="submit" loading={createTask.isPending}>
        Create
      </Button>
      {createTask.error && <ErrorMessage error={createTask.error} />}
    </form>
  )
}
```

### Update Mutation

```tsx
// hooks/use-update-task.ts
interface UpdateTaskInput {
  id: string
  title?: string
  description?: string
  completed?: boolean
}

export function useUpdateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, ...data }: UpdateTaskInput) =>
      apiClient<Task>(`/api/tasks/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    onSuccess: (updatedTask) => {
      // Update specific task in cache
      queryClient.setQueryData(['tasks', updatedTask.id], updatedTask)
      // Invalidate tasks list
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}

// Usage
function EditTaskForm({ task }: { task: Task }) {
  const updateTask = useUpdateTask()

  const handleSubmit = (data: Partial<Task>) => {
    updateTask.mutate({ id: task.id, ...data })
  }

  return <form onSubmit={handleSubmit}>...</form>
}
```

### Delete Mutation

```tsx
// hooks/use-delete-task.ts
export function useDeleteTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (taskId: string) =>
      apiClient(`/api/tasks/${taskId}`, {
        method: 'DELETE',
      }),
    onSuccess: (_, taskId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: ['tasks', taskId] })
      // Invalidate tasks list
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}

// Usage
function DeleteTaskButton({ taskId }: { taskId: string }) {
  const deleteTask = useDeleteTask()

  const handleDelete = async () => {
    if (confirm('Are you sure?')) {
      await deleteTask.mutateAsync(taskId)
    }
  }

  return (
    <Button
      variant="destructive"
      onClick={handleDelete}
      loading={deleteTask.isPending}
    >
      Delete
    </Button>
  )
}
```

### Mutation with Optimistic Update

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
      const previousTasks = queryClient.getQueryData<Task[]>(['tasks'])

      // Optimistically update
      queryClient.setQueryData<Task[]>(['tasks'], (old) =>
        old?.map(task =>
          task.id === id ? { ...task, completed } : task
        ) || []
      )

      // Return context with snapshot
      return { previousTasks }
    },

    // Rollback on error
    onError: (err, variables, context) => {
      if (context?.previousTasks) {
        queryClient.setQueryData(['tasks'], context.previousTasks)
      }
    },

    // Refetch on success or error
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}

// Usage
function TaskCheckbox({ task }: { task: Task }) {
  const toggleTask = useToggleTask()

  return (
    <Checkbox
      checked={task.completed}
      onCheckedChange={(completed) => {
        toggleTask.mutate({ id: task.id, completed: !!completed })
      }}
    />
  )
}
```

---

## Advanced Query Patterns

### Paginated Query

```tsx
// hooks/use-paginated-tasks.ts
interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
}

export function usePaginatedTasks(page: number, pageSize: number = 10) {
  return useQuery({
    queryKey: ['tasks', 'paginated', page, pageSize],
    queryFn: () =>
      apiClient<PaginatedResponse<Task>>(
        `/api/tasks?page=${page}&pageSize=${pageSize}`
      ),
    keepPreviousData: true, // Keep old data while fetching new page
  })
}

// Usage
function PaginatedTaskList() {
  const [page, setPage] = useState(1)
  const { data, isLoading, isFetching } = usePaginatedTasks(page)

  return (
    <div>
      {isFetching && <LoadingBar />}
      <TaskCards tasks={data?.items} />
      <Pagination
        currentPage={page}
        totalPages={Math.ceil((data?.total || 0) / 10)}
        onPageChange={setPage}
      />
    </div>
  )
}
```

### Infinite Query

```tsx
// hooks/use-infinite-tasks.ts
interface InfiniteResponse {
  items: Task[]
  nextCursor: string | null
}

export function useInfiniteTasks() {
  return useInfiniteQuery({
    queryKey: ['tasks', 'infinite'],
    queryFn: ({ pageParam = null }) =>
      apiClient<InfiniteResponse>(
        `/api/tasks${pageParam ? `?cursor=${pageParam}` : ''}`
      ),
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  })
}

// Usage
function InfiniteTaskList() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteTasks()

  return (
    <div>
      {data?.pages.map((page, i) => (
        <div key={i}>
          {page.items.map(task => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      ))}
      {hasNextPage && (
        <Button
          onClick={() => fetchNextPage()}
          loading={isFetchingNextPage}
        >
          Load More
        </Button>
      )}
    </div>
  )
}
```

### Parallel Queries

```tsx
// hooks/use-dashboard-data.ts
export function useDashboardData() {
  const tasks = useQuery({
    queryKey: ['tasks'],
    queryFn: () => apiClient<Task[]>('/api/tasks'),
  })

  const stats = useQuery({
    queryKey: ['stats'],
    queryFn: () => apiClient<Stats>('/api/stats'),
  })

  const notifications = useQuery({
    queryKey: ['notifications'],
    queryFn: () => apiClient<Notification[]>('/api/notifications'),
  })

  return {
    tasks,
    stats,
    notifications,
    isLoading: tasks.isLoading || stats.isLoading || notifications.isLoading,
    error: tasks.error || stats.error || notifications.error,
  }
}

// Usage
function Dashboard() {
  const { tasks, stats, notifications, isLoading } = useDashboardData()

  if (isLoading) return <Spinner />

  return (
    <div>
      <StatsCards data={stats.data} />
      <TaskList tasks={tasks.data} />
      <NotificationList notifications={notifications.data} />
    </div>
  )
}
```

### Dependent Queries

```tsx
// hooks/use-user-tasks.ts
export function useUserTasks(userId: string | undefined) {
  // First query: Get user
  const userQuery = useQuery({
    queryKey: ['users', userId],
    queryFn: () => apiClient<User>(`/api/users/${userId}`),
    enabled: !!userId,
  })

  // Second query: Get user's tasks (depends on first query)
  const tasksQuery = useQuery({
    queryKey: ['users', userId, 'tasks'],
    queryFn: () => apiClient<Task[]>(`/api/users/${userId}/tasks`),
    enabled: !!userQuery.data, // Only fetch when user is loaded
  })

  return {
    user: userQuery.data,
    tasks: tasksQuery.data,
    isLoading: userQuery.isLoading || tasksQuery.isLoading,
  }
}
```

---

## Error Handling

### Global Error Handler

```tsx
// lib/api-client.ts
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
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
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...options?.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({}))
    throw new ApiError(
      error.message || 'An error occurred',
      response.status,
      error.code,
      error
    )
  }

  return response.json()
}
```

### Hook-Level Error Handling

```tsx
// hooks/use-tasks.ts
export function useTasks() {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: () => apiClient<Task[]>('/api/tasks'),
    retry: (failureCount, error) => {
      // Don't retry on 4xx errors
      if (error instanceof ApiError && error.status < 500) {
        return false
      }
      return failureCount < 3
    },
    onError: (error) => {
      // Log error to monitoring service
      console.error('Failed to fetch tasks:', error)
    },
  })
}
```

### Component-Level Error Handling

```tsx
function TaskList() {
  const { data, error } = useTasks()

  if (error) {
    if (error instanceof ApiError) {
      if (error.status === 401) {
        return <LoginPrompt />
      }
      if (error.status === 403) {
        return <AccessDenied />
      }
      if (error.status === 404) {
        return <NotFound />
      }
    }
    return <ErrorMessage error={error} />
  }

  return <TaskCards tasks={data} />
}
```

---

## Type Safety

### Typed API Client

```tsx
// lib/api-client.ts
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

interface ApiClientOptions extends Omit<RequestInit, 'method' | 'body'> {
  method?: HttpMethod
  body?: any
}

export async function apiClient<TResponse>(
  endpoint: string,
  options?: ApiClientOptions
): Promise<TResponse> {
  // Implementation
}
```

### Typed Hooks

```tsx
// types/task.ts
export interface Task {
  id: string
  title: string
  description: string | null
  completed: boolean
  priority: 'low' | 'medium' | 'high'
  created_at: string
  updated_at: string
}

export interface CreateTaskInput {
  title: string
  description?: string
  priority?: Task['priority']
}

export interface UpdateTaskInput extends Partial<CreateTaskInput> {
  completed?: boolean
}

// hooks/use-tasks.ts
import type { Task, CreateTaskInput, UpdateTaskInput } from '@/types/task'

export function useTasks(): UseQueryResult<Task[]> {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: () => apiClient<Task[]>('/api/tasks'),
  })
}

export function useCreateTask(): UseMutationResult<Task, Error, CreateTaskInput> {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (input: CreateTaskInput) =>
      apiClient<Task>('/api/tasks', {
        method: 'POST',
        body: JSON.stringify(input),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}
```

---

## Testing Hooks

### Testing Query Hooks

```tsx
// hooks/__tests__/use-tasks.test.ts
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useTasks } from '../use-tasks'

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

test('fetches tasks', async () => {
  const { result } = renderHook(() => useTasks(), {
    wrapper: createWrapper(),
  })

  expect(result.current.isLoading).toBe(true)

  await waitFor(() => expect(result.current.isSuccess).toBe(true))

  expect(result.current.data).toHaveLength(3)
})
```

### Testing Mutation Hooks

```tsx
// hooks/__tests__/use-create-task.test.ts
test('creates task', async () => {
  const { result } = renderHook(() => useCreateTask(), {
    wrapper: createWrapper(),
  })

  act(() => {
    result.current.mutate({ title: 'New task' })
  })

  await waitFor(() => expect(result.current.isSuccess).toBe(true))

  expect(result.current.data).toMatchObject({ title: 'New task' })
})
```

---

## Best Practices

1. **Consistent Query Keys**: Use arrays for query keys: `['resource', id, 'subresource']`
2. **Type Everything**: Use TypeScript for all hooks and API responses
3. **Handle All States**: Loading, error, empty, success
4. **Optimistic Updates**: For better UX on mutations
5. **Error Boundaries**: Catch errors at component boundaries
6. **Retry Logic**: Retry on network errors, not on 4xx
7. **Cache Invalidation**: Invalidate related queries after mutations
8. **Dependent Queries**: Use `enabled` option for dependent data
9. **Polling**: Use `refetchInterval` for real-time data
10. **Testing**: Test hooks in isolation with mock data
