# Data Fetching Strategies

Comprehensive comparison of data fetching approaches for React applications.

## Table of Contents
- Strategy Overview
- React Query (TanStack Query)
- SWR (Stale-While-Revalidate)
- Custom Hooks with Fetch
- Next.js Server Components
- Decision Guide

---

## Strategy Overview

### Comparison Matrix

| Feature | React Query | SWR | Custom Hooks | Server Components |
|---------|-------------|-----|--------------|-------------------|
| **Caching** | ✅ Advanced | ✅ Good | ❌ Manual | ✅ Built-in |
| **Auto-refetch** | ✅ Yes | ✅ Yes | ❌ Manual | ✅ Revalidation |
| **Optimistic updates** | ✅ Built-in | ✅ Built-in | ❌ Manual | ❌ N/A |
| **Pagination** | ✅ Excellent | ✅ Good | ❌ Manual | ⚠️ Limited |
| **DevTools** | ✅ Excellent | ✅ Good | ❌ None | ✅ React DevTools |
| **Bundle size** | ~13KB | ~5KB | 0KB | 0KB (server) |
| **Learning curve** | Medium | Low | Low | Medium |
| **TypeScript** | ✅ Excellent | ✅ Good | ✅ Full control | ✅ Excellent |
| **SSR support** | ✅ Yes | ✅ Yes | ⚠️ Manual | ✅ Native |
| **Real-time** | ⚠️ Polling | ⚠️ Polling | ✅ Full control | ❌ N/A |

---

## React Query (TanStack Query)

### Overview

Most feature-rich data fetching library. Handles caching, background updates, optimistic updates, and more.

**Best for**: Complex applications with lots of server state, mutations, and real-time requirements.

### Installation

```bash
npm install @tanstack/react-query
npm install @tanstack/react-query-devtools
```

### Setup

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
        staleTime: 60 * 1000, // Consider data fresh for 1 minute
        cacheTime: 5 * 60 * 1000, // Keep unused data in cache for 5 minutes
        retry: 1, // Retry failed requests once
        refetchOnWindowFocus: false, // Don't refetch on window focus
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

### Query Pattern

```tsx
import { useQuery } from '@tanstack/react-query'

interface Task {
  id: string
  title: string
  completed: boolean
}

function useTasks() {
  return useQuery({
    queryKey: ['tasks'],
    queryFn: async () => {
      const response = await fetch('/api/tasks')
      if (!response.ok) throw new Error('Failed to fetch tasks')
      return response.json() as Promise<Task[]>
    },
  })
}

// Usage
function TaskList() {
  const { data, isLoading, error, refetch } = useTasks()

  if (isLoading) return <Spinner />
  if (error) return <Error message={error.message} />

  return (
    <div>
      <button onClick={() => refetch()}>Refresh</button>
      {data?.map(task => <TaskCard key={task.id} task={task} />)}
    </div>
  )
}
```

### Mutation Pattern

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query'

function useCreateTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async (newTask: { title: string }) => {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTask),
      })
      if (!response.ok) throw new Error('Failed to create task')
      return response.json()
    },
    onSuccess: () => {
      // Invalidate and refetch tasks
      queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })
}

// Usage
function CreateTaskForm() {
  const createTask = useCreateTask()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createTask.mutate({ title: 'New task' })
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="title" />
      <button disabled={createTask.isPending}>
        {createTask.isPending ? 'Creating...' : 'Create'}
      </button>
      {createTask.error && <p>{createTask.error.message}</p>}
    </form>
  )
}
```

### Advanced Features

**Pagination**:
```tsx
function usePaginatedTasks(page: number) {
  return useQuery({
    queryKey: ['tasks', page],
    queryFn: () => fetchTasks(page),
    keepPreviousData: true, // Keep old data while fetching new
  })
}
```

**Infinite Scroll**:
```tsx
function useInfiniteTasks() {
  return useInfiniteQuery({
    queryKey: ['tasks'],
    queryFn: ({ pageParam = 0 }) => fetchTasks(pageParam),
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  })
}
```

**Optimistic Updates**:
```tsx
function useToggleTask() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateTask,
    onMutate: async (updatedTask) => {
      await queryClient.cancelQueries({ queryKey: ['tasks'] })
      const previous = queryClient.getQueryData(['tasks'])
      queryClient.setQueryData(['tasks'], (old: Task[]) =>
        old.map(t => t.id === updatedTask.id ? updatedTask : t)
      )
      return { previous }
    },
    onError: (err, variables, context) => {
      queryClient.setQueryData(['tasks'], context?.previous)
    },
  })
}
```

### Pros & Cons

**Pros**:
- Comprehensive feature set
- Excellent TypeScript support
- Great DevTools
- Active community and maintenance
- Handles complex scenarios well

**Cons**:
- Larger bundle size (~13KB)
- Steeper learning curve
- Can be overkill for simple apps

---

## SWR (Stale-While-Revalidate)

### Overview

Lightweight data fetching library by Vercel. Focus on cache-first approach with automatic revalidation.

**Best for**: Next.js applications, simpler data fetching needs, smaller bundle size requirements.

### Installation

```bash
npm install swr
```

### Setup

```tsx
// app/providers.tsx
"use client"

import { SWRConfig } from 'swr'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SWRConfig
      value={{
        fetcher: (url: string) => fetch(url).then(res => res.json()),
        revalidateOnFocus: false,
        revalidateOnReconnect: true,
      }}
    >
      {children}
    </SWRConfig>
  )
}
```

### Query Pattern

```tsx
import useSWR from 'swr'

function useTasks() {
  return useSWR<Task[]>('/api/tasks')
}

// Usage
function TaskList() {
  const { data, error, isLoading, mutate } = useTasks()

  if (isLoading) return <Spinner />
  if (error) return <Error />

  return (
    <div>
      <button onClick={() => mutate()}>Refresh</button>
      {data?.map(task => <TaskCard key={task.id} task={task} />)}
    </div>
  )
}
```

### Mutation Pattern

```tsx
import useSWRMutation from 'swr/mutation'

async function createTask(url: string, { arg }: { arg: { title: string } }) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(arg),
  })
  return response.json()
}

function useCreateTask() {
  return useSWRMutation('/api/tasks', createTask)
}

// Usage
function CreateTaskForm() {
  const { trigger, isMutating, error } = useCreateTask()
  const { mutate } = useSWR('/api/tasks') // For revalidation

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await trigger({ title: 'New task' })
    mutate() // Revalidate tasks list
  }

  return (
    <form onSubmit={handleSubmit}>
      <input name="title" />
      <button disabled={isMutating}>Create</button>
    </form>
  )
}
```

### Advanced Features

**Optimistic Updates**:
```tsx
function useToggleTask(taskId: string) {
  const { mutate } = useSWR('/api/tasks')

  const toggle = async (completed: boolean) => {
    // Optimistic update
    mutate(
      (tasks: Task[]) =>
        tasks.map(t => t.id === taskId ? { ...t, completed } : t),
      { revalidate: false }
    )

    // Actual update
    await fetch(`/api/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify({ completed }),
    })

    // Revalidate
    mutate()
  }

  return toggle
}
```

**Pagination**:
```tsx
function usePaginatedTasks(page: number) {
  return useSWR(`/api/tasks?page=${page}`)
}
```

### Pros & Cons

**Pros**:
- Lightweight (~5KB)
- Simple API
- Great Next.js integration
- Built by Vercel
- Good for most use cases

**Cons**:
- Less features than React Query
- Mutation handling less elegant
- Smaller ecosystem

---

## Custom Hooks with Fetch

### Overview

Build your own data fetching hooks using native fetch API. Full control, no dependencies.

**Best for**: Learning, simple apps, specific requirements, avoiding dependencies.

### Basic Pattern

```tsx
import { useState, useEffect } from 'react'

function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchData() {
      try {
        setLoading(true)
        const response = await fetch(url)
        if (!response.ok) throw new Error('Failed to fetch')
        const json = await response.json()
        if (!cancelled) {
          setData(json)
          setError(null)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err as Error)
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchData()

    return () => {
      cancelled = true
    }
  }, [url])

  return { data, loading, error }
}

// Usage
function TaskList() {
  const { data, loading, error } = useFetch<Task[]>('/api/tasks')

  if (loading) return <Spinner />
  if (error) return <Error />

  return data?.map(task => <TaskCard key={task.id} task={task} />)
}
```

### With Refetch

```tsx
function useFetch<T>(url: string) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const [refetchIndex, setRefetchIndex] = useState(0)

  useEffect(() => {
    // ... fetch logic
  }, [url, refetchIndex])

  const refetch = () => setRefetchIndex(prev => prev + 1)

  return { data, loading, error, refetch }
}
```

### Mutation Pattern

```tsx
function useCreateTask() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const create = async (task: { title: string }) => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(task),
      })
      if (!response.ok) throw new Error('Failed to create')
      return response.json()
    } catch (err) {
      setError(err as Error)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { create, loading, error }
}
```

### Pros & Cons

**Pros**:
- No dependencies
- Full control
- Smallest bundle size
- Great for learning

**Cons**:
- Manual caching
- Manual refetching
- More boilerplate
- Need to handle edge cases

---

## Next.js Server Components

### Overview

Fetch data on the server, render HTML, send to client. No client-side JavaScript for data fetching.

**Best for**: Static or semi-static data, SEO-critical pages, reducing client-side JavaScript.

### Basic Pattern

```tsx
// app/tasks/page.tsx (Server Component)
async function getTasks() {
  const response = await fetch('http://localhost:8000/api/tasks', {
    next: { revalidate: 60 }, // Revalidate every 60 seconds
  })
  return response.json()
}

export default async function TasksPage() {
  const tasks = await getTasks()

  return (
    <div>
      {tasks.map(task => (
        <TaskCard key={task.id} task={task} />
      ))}
    </div>
  )
}
```

### With Loading State

```tsx
// app/tasks/loading.tsx
export default function Loading() {
  return <Skeleton count={5} />
}

// app/tasks/page.tsx
export default async function TasksPage() {
  const tasks = await getTasks()
  return <TaskList tasks={tasks} />
}
```

### Revalidation Strategies

```tsx
// Time-based revalidation
fetch(url, { next: { revalidate: 3600 } }) // Every hour

// On-demand revalidation
import { revalidatePath } from 'next/cache'
revalidatePath('/tasks')

// No caching
fetch(url, { cache: 'no-store' })
```

### Pros & Cons

**Pros**:
- No client-side JS for data fetching
- Great for SEO
- Automatic caching
- Simpler mental model

**Cons**:
- Less interactive
- No real-time updates
- Requires server
- Limited for dynamic UIs

---

## Decision Guide

### Choose React Query if:
- Complex application with lots of mutations
- Need optimistic updates
- Pagination or infinite scroll
- Real-time requirements (with polling)
- Large team, need consistency

### Choose SWR if:
- Using Next.js
- Simpler data fetching needs
- Want smaller bundle size
- Cache-first approach preferred

### Choose Custom Hooks if:
- Very simple application
- Learning React
- Specific requirements not met by libraries
- Want zero dependencies

### Choose Server Components if:
- Static or semi-static data
- SEO is critical
- Want to minimize client-side JS
- Using Next.js 13+ App Router

### Hybrid Approach

Often the best solution combines multiple strategies:

```tsx
// Server Component for initial data
export default async function TasksPage() {
  const initialTasks = await getTasks()

  return (
    <ClientTaskList initialData={initialTasks} />
  )
}

// Client Component for interactivity
"use client"
function ClientTaskList({ initialData }) {
  const { data } = useTasks({ initialData })
  // Now has real-time updates, mutations, etc.
}
```
