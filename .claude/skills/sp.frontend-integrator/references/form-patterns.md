# Form Patterns

Comprehensive patterns for form handling, validation, and submission in React applications.

## Table of Contents
- React Hook Form Basics
- Validation with Zod
- Form Submission
- Field-Level Validation
- Complex Forms
- File Uploads
- Multi-Step Forms

---

## React Hook Form Basics

### Installation

```bash
npm install react-hook-form
npm install zod @hookform/resolvers
```

### Basic Form

```tsx
import { useForm } from 'react-hook-form'

interface FormData {
  title: string
  description: string
}

function CreateTaskForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>()

  const onSubmit = (data: FormData) => {
    console.log(data)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label htmlFor="title">Title</label>
        <input
          id="title"
          {...register('title', { required: 'Title is required' })}
        />
        {errors.title && <span>{errors.title.message}</span>}
      </div>

      <div>
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          {...register('description')}
        />
      </div>

      <button type="submit">Create</button>
    </form>
  )
}
```

### With UI Components

```tsx
import { useForm } from 'react-hook-form'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'

function CreateTaskForm() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormData>()

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <Label htmlFor="title">Title</Label>
        <Input
          id="title"
          {...register('title')}
          error={errors.title?.message}
        />
      </div>

      <Button type="submit">Create</Button>
    </form>
  )
}
```

---

## Validation with Zod

### Schema Definition

```tsx
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'

const taskSchema = z.object({
  title: z.string()
    .min(1, 'Title is required')
    .max(100, 'Title must be less than 100 characters'),
  description: z.string()
    .max(500, 'Description must be less than 500 characters')
    .optional(),
  priority: z.enum(['low', 'medium', 'high']),
  dueDate: z.string().datetime().optional(),
  tags: z.array(z.string()).optional(),
})

type TaskFormData = z.infer<typeof taskSchema>

function CreateTaskForm() {
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: '',
      description: '',
      priority: 'medium',
    },
  })

  return <form onSubmit={form.handleSubmit(onSubmit)}>...</form>
}
```

### Custom Validation Rules

```tsx
const taskSchema = z.object({
  title: z.string().min(1),
  dueDate: z.string().datetime(),
}).refine(
  (data) => {
    // Custom validation: due date must be in the future
    return new Date(data.dueDate) > new Date()
  },
  {
    message: 'Due date must be in the future',
    path: ['dueDate'],
  }
)
```

### Async Validation

```tsx
const taskSchema = z.object({
  title: z.string().min(1),
}).refine(
  async (data) => {
    // Check if title is unique
    const response = await fetch(`/api/tasks/check-title?title=${data.title}`)
    const { available } = await response.json()
    return available
  },
  {
    message: 'A task with this title already exists',
    path: ['title'],
  }
)
```

---

## Form Submission

### With React Query Mutation

```tsx
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useCreateTask } from '@/hooks/use-create-task'
import { useToast } from '@/components/ui/use-toast'

function CreateTaskForm({ onSuccess }: { onSuccess?: () => void }) {
  const createTask = useCreateTask()
  const { toast } = useToast()

  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: '',
      priority: 'medium',
    },
  })

  const onSubmit = async (data: TaskFormData) => {
    try {
      await createTask.mutateAsync(data)
      toast({
        title: 'Success',
        description: 'Task created successfully',
      })
      form.reset()
      onSuccess?.()
    } catch (error) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to create task',
        variant: 'destructive',
      })
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

      <Button
        type="submit"
        disabled={!form.formState.isValid || createTask.isPending}
        loading={createTask.isPending}
      >
        Create Task
      </Button>
    </form>
  )
}
```

### Server-Side Validation Errors

```tsx
function CreateTaskForm() {
  const createTask = useCreateTask()
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
  })

  const onSubmit = async (data: TaskFormData) => {
    try {
      await createTask.mutateAsync(data)
    } catch (error) {
      if (error instanceof ApiError && error.data?.errors) {
        // Set server-side validation errors
        Object.entries(error.data.errors).forEach(([field, message]) => {
          form.setError(field as keyof TaskFormData, {
            type: 'server',
            message: message as string,
          })
        })
      }
    }
  }

  return <form onSubmit={form.handleSubmit(onSubmit)}>...</form>
}
```

---

## Field-Level Validation

### Real-Time Validation

```tsx
function CreateTaskForm() {
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    mode: 'onChange', // Validate on every change
  })

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Input
        {...form.register('title')}
        error={form.formState.errors.title?.message}
      />
    </form>
  )
}
```

### Validation Modes

```tsx
// Validate on blur
const form = useForm({ mode: 'onBlur' })

// Validate on change
const form = useForm({ mode: 'onChange' })

// Validate on submit (default)
const form = useForm({ mode: 'onSubmit' })

// Validate on touch (after first blur)
const form = useForm({ mode: 'onTouched' })

// Validate everything
const form = useForm({ mode: 'all' })
```

### Conditional Validation

```tsx
const taskSchema = z.object({
  title: z.string().min(1),
  hasDeadline: z.boolean(),
  dueDate: z.string().datetime().optional(),
}).refine(
  (data) => {
    // If hasDeadline is true, dueDate is required
    if (data.hasDeadline) {
      return !!data.dueDate
    }
    return true
  },
  {
    message: 'Due date is required when deadline is enabled',
    path: ['dueDate'],
  }
)

function CreateTaskForm() {
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
  })

  const hasDeadline = form.watch('hasDeadline')

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Checkbox {...form.register('hasDeadline')} />

      {hasDeadline && (
        <Input
          type="datetime-local"
          {...form.register('dueDate')}
          error={form.formState.errors.dueDate?.message}
        />
      )}
    </form>
  )
}
```

---

## Complex Forms

### Nested Objects

```tsx
const taskSchema = z.object({
  title: z.string().min(1),
  assignee: z.object({
    id: z.string(),
    name: z.string(),
    email: z.string().email(),
  }).optional(),
})

function CreateTaskForm() {
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
  })

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Input {...form.register('title')} />

      <Input
        {...form.register('assignee.name')}
        placeholder="Assignee name"
      />
      <Input
        {...form.register('assignee.email')}
        placeholder="Assignee email"
      />
    </form>
  )
}
```

### Dynamic Fields (Arrays)

```tsx
import { useFieldArray } from 'react-hook-form'

const taskSchema = z.object({
  title: z.string().min(1),
  subtasks: z.array(
    z.object({
      title: z.string().min(1),
      completed: z.boolean(),
    })
  ),
})

function CreateTaskForm() {
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: '',
      subtasks: [],
    },
  })

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'subtasks',
  })

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Input {...form.register('title')} />

      <div className="space-y-2">
        {fields.map((field, index) => (
          <div key={field.id} className="flex gap-2">
            <Input
              {...form.register(`subtasks.${index}.title`)}
              placeholder="Subtask title"
            />
            <Button
              type="button"
              variant="ghost"
              onClick={() => remove(index)}
            >
              Remove
            </Button>
          </div>
        ))}
      </div>

      <Button
        type="button"
        variant="outline"
        onClick={() => append({ title: '', completed: false })}
      >
        Add Subtask
      </Button>

      <Button type="submit">Create Task</Button>
    </form>
  )
}
```

### Controlled Components

```tsx
import { Controller } from 'react-hook-form'
import { Select } from '@/components/ui/select'

function CreateTaskForm() {
  const form = useForm<TaskFormData>()

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Controller
        name="priority"
        control={form.control}
        render={({ field }) => (
          <Select
            value={field.value}
            onValueChange={field.onChange}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </Select>
        )}
      />
    </form>
  )
}
```

---

## File Uploads

### Single File Upload

```tsx
const taskSchema = z.object({
  title: z.string().min(1),
  attachment: z.instanceof(File).optional(),
})

function CreateTaskForm() {
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
  })

  const onSubmit = async (data: TaskFormData) => {
    const formData = new FormData()
    formData.append('title', data.title)
    if (data.attachment) {
      formData.append('attachment', data.attachment)
    }

    await fetch('/api/tasks', {
      method: 'POST',
      body: formData,
    })
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Input {...form.register('title')} />

      <Input
        type="file"
        {...form.register('attachment')}
        accept="image/*,.pdf"
      />

      <Button type="submit">Create</Button>
    </form>
  )
}
```

### Multiple File Upload

```tsx
const taskSchema = z.object({
  title: z.string().min(1),
  attachments: z.array(z.instanceof(File)).optional(),
})

function CreateTaskForm() {
  const form = useForm<TaskFormData>()

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Input
        type="file"
        multiple
        {...form.register('attachments')}
      />
    </form>
  )
}
```

### File Upload with Preview

```tsx
function CreateTaskForm() {
  const form = useForm<TaskFormData>()
  const [preview, setPreview] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      form.setValue('attachment', file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Input
        type="file"
        onChange={handleFileChange}
        accept="image/*"
      />

      {preview && (
        <img src={preview} alt="Preview" className="mt-2 h-32 w-32 object-cover" />
      )}
    </form>
  )
}
```

---

## Multi-Step Forms

### Basic Multi-Step Form

```tsx
function MultiStepTaskForm() {
  const [step, setStep] = useState(1)
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
  })

  const onSubmit = async (data: TaskFormData) => {
    await createTask(data)
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {step === 1 && (
        <div>
          <h2>Step 1: Basic Info</h2>
          <Input {...form.register('title')} />
          <Button type="button" onClick={() => setStep(2)}>
            Next
          </Button>
        </div>
      )}

      {step === 2 && (
        <div>
          <h2>Step 2: Details</h2>
          <Textarea {...form.register('description')} />
          <Button type="button" onClick={() => setStep(1)}>
            Back
          </Button>
          <Button type="button" onClick={() => setStep(3)}>
            Next
          </Button>
        </div>
      )}

      {step === 3 && (
        <div>
          <h2>Step 3: Review</h2>
          <pre>{JSON.stringify(form.watch(), null, 2)}</pre>
          <Button type="button" onClick={() => setStep(2)}>
            Back
          </Button>
          <Button type="submit">Submit</Button>
        </div>
      )}
    </form>
  )
}
```

### Multi-Step with Validation

```tsx
function MultiStepTaskForm() {
  const [step, setStep] = useState(1)
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    mode: 'onChange',
  })

  const nextStep = async () => {
    let isValid = false

    if (step === 1) {
      isValid = await form.trigger(['title'])
    } else if (step === 2) {
      isValid = await form.trigger(['description', 'priority'])
    }

    if (isValid) {
      setStep(step + 1)
    }
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Steps */}
      <Button type="button" onClick={nextStep}>
        Next
      </Button>
    </form>
  )
}
```

---

## Best Practices

### Form State Management

```tsx
function CreateTaskForm() {
  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: '',
      priority: 'medium',
    },
  })

  // Watch specific field
  const title = form.watch('title')

  // Watch all fields
  const allValues = form.watch()

  // Get form state
  const { isDirty, isValid, isSubmitting } = form.formState

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Input {...form.register('title')} />

      <Button
        type="submit"
        disabled={!isDirty || !isValid || isSubmitting}
      >
        Submit
      </Button>
    </form>
  )
}
```

### Reset Form After Submission

```tsx
const onSubmit = async (data: TaskFormData) => {
  await createTask.mutateAsync(data)
  form.reset() // Reset to default values
}
```

### Dirty Fields Tracking

```tsx
const { dirtyFields } = form.formState

// Only submit changed fields
const onSubmit = (data: TaskFormData) => {
  const changedData = Object.keys(dirtyFields).reduce((acc, key) => {
    acc[key] = data[key]
    return acc
  }, {})

  updateTask(changedData)
}
```

### Form Accessibility

```tsx
<form onSubmit={form.handleSubmit(onSubmit)}>
  <Label htmlFor="title">
    Title <span className="text-destructive">*</span>
  </Label>
  <Input
    id="title"
    {...form.register('title')}
    aria-invalid={!!form.formState.errors.title}
    aria-describedby={form.formState.errors.title ? 'title-error' : undefined}
  />
  {form.formState.errors.title && (
    <span id="title-error" role="alert" className="text-sm text-destructive">
      {form.formState.errors.title.message}
    </span>
  )}
</form>
```

---

## Summary

**Key Patterns**:
1. Use React Hook Form for form state management
2. Use Zod for schema validation
3. Integrate with React Query for mutations
4. Handle loading, error, and success states
5. Provide real-time validation feedback
6. Support complex forms (nested, arrays, files)
7. Implement multi-step forms when needed
8. Ensure accessibility (labels, ARIA, error messages)
9. Reset forms after successful submission
10. Track dirty fields for partial updates
