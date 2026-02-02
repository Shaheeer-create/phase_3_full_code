# Component Patterns

Detailed patterns for building production-ready React components with Tailwind CSS, shadcn/ui, and Radix UI.

## Table of Contents
- Component Architecture
- Variant Management with CVA
- Composition Patterns
- State Management
- Accessibility Patterns
- Common Components

---

## Component Architecture

### File Structure

```tsx
// components/ui/button.tsx
import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

// 1. Define variants with cva
const buttonVariants = cva(/* ... */)

// 2. Define props interface
export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  // Custom props
}

// 3. Implement component with forwardRef
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return <button className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
  }
)
Button.displayName = "Button"

// 4. Export component and variants
export { Button, buttonVariants }
```

### Key Principles

1. **Forward Refs**: Always use `React.forwardRef` for DOM components
2. **Extend Native Props**: Extend HTML element props for type safety
3. **Variant Props**: Use `VariantProps` from cva for variant typing
4. **className Merging**: Use `cn()` utility to merge Tailwind classes
5. **Display Name**: Set `displayName` for better debugging

---

## Variant Management with CVA

### Basic Variant Definition

```tsx
import { cva } from "class-variance-authority"

const buttonVariants = cva(
  // Base classes (always applied)
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      // Variant dimension 1: visual style
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent",
        ghost: "hover:bg-accent hover:text-accent-foreground",
      },
      // Variant dimension 2: size
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 px-3 text-sm",
        lg: "h-11 px-8",
        icon: "h-10 w-10",
      },
    },
    // Default values
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

### Compound Variants

Handle interactions between variants:

```tsx
const buttonVariants = cva("base-classes", {
  variants: {
    variant: {
      default: "bg-primary",
      outline: "border",
    },
    size: {
      sm: "h-9",
      lg: "h-11",
    },
    loading: {
      true: "cursor-wait",
    },
  },
  compoundVariants: [
    // When both outline and small, adjust padding
    {
      variant: "outline",
      size: "sm",
      class: "px-2",
    },
    // When loading, reduce opacity
    {
      loading: true,
      class: "opacity-70",
    },
  ],
  defaultVariants: {
    variant: "default",
    size: "default",
  },
})
```

### Boolean Variants

```tsx
const cardVariants = cva("rounded-lg border", {
  variants: {
    elevated: {
      true: "shadow-lg",
      false: "shadow-none",
    },
    interactive: {
      true: "cursor-pointer hover:shadow-md transition-shadow",
      false: "",
    },
  },
  defaultVariants: {
    elevated: false,
    interactive: false,
  },
})
```

---

## Composition Patterns

### Slot Pattern (Polymorphic Components)

Allow components to render as different elements:

```tsx
import { Slot } from "@radix-ui/react-slot"

interface ButtonProps {
  asChild?: boolean
  // ... other props
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return <Comp ref={ref} {...props} />
  }
)

// Usage: Render as Link
<Button asChild>
  <Link href="/dashboard">Dashboard</Link>
</Button>
```

### Compound Components

Create related components that work together:

```tsx
// Card with subcomponents
const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("rounded-lg border bg-card", className)} {...props} />
  )
)

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />
  )
)

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={cn("text-2xl font-semibold", className)} {...props} />
  )
)

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
  )
)

// Usage
<Card>
  <CardHeader>
    <CardTitle>Title</CardTitle>
  </CardHeader>
  <CardContent>Content</CardContent>
</Card>
```

### Render Props Pattern

For flexible rendering:

```tsx
interface ListProps<T> {
  items: T[]
  renderItem: (item: T, index: number) => React.ReactNode
  emptyState?: React.ReactNode
}

function List<T>({ items, renderItem, emptyState }: ListProps<T>) {
  if (items.length === 0) {
    return <>{emptyState || <p>No items</p>}</>
  }

  return (
    <ul className="space-y-2">
      {items.map((item, index) => (
        <li key={index}>{renderItem(item, index)}</li>
      ))}
    </ul>
  )
}

// Usage
<List
  items={tasks}
  renderItem={(task) => <TaskCard task={task} />}
  emptyState={<EmptyState />}
/>
```

---

## State Management

### Loading State

```tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean
  loadingText?: string
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, loading, loadingText, disabled, ...props }, ref) => {
    return (
      <button ref={ref} disabled={disabled || loading} {...props}>
        {loading && <Spinner className="mr-2 h-4 w-4 animate-spin" />}
        {loading ? loadingText || children : children}
      </button>
    )
  }
)

// Usage
<Button loading={isSubmitting} loadingText="Saving...">
  Save
</Button>
```

### Error State

```tsx
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <div className="space-y-1">
        <input
          ref={ref}
          className={cn(
            "flex h-10 w-full rounded-md border px-3",
            error && "border-destructive focus-visible:ring-destructive",
            className
          )}
          aria-invalid={!!error}
          aria-describedby={error ? `${props.id}-error` : undefined}
          {...props}
        />
        {error && (
          <p id={`${props.id}-error`} className="text-sm text-destructive" role="alert">
            {error}
          </p>
        )}
      </div>
    )
  }
)

// Usage
<Input id="email" error={errors.email} />
```

### Controlled vs Uncontrolled

```tsx
// Controlled component
interface ControlledInputProps {
  value: string
  onChange: (value: string) => void
}

const ControlledInput: React.FC<ControlledInputProps> = ({ value, onChange }) => {
  return (
    <input
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  )
}

// Uncontrolled component with ref
const UncontrolledInput = React.forwardRef<HTMLInputElement>((props, ref) => {
  return <input ref={ref} {...props} />
})

// Usage
const [value, setValue] = useState("")
<ControlledInput value={value} onChange={setValue} />

const inputRef = useRef<HTMLInputElement>(null)
<UncontrolledInput ref={inputRef} defaultValue="initial" />
```

---

## Accessibility Patterns

### Focus Management

```tsx
// Modal with focus trap
import { Dialog, DialogContent } from "@radix-ui/react-dialog"

const Modal: React.FC<{ open: boolean; onClose: () => void }> = ({ open, onClose, children }) => {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent
        onOpenAutoFocus={(e) => {
          // Focus first input on open
          const firstInput = e.currentTarget.querySelector('input, button')
          if (firstInput instanceof HTMLElement) {
            firstInput.focus()
          }
        }}
        onCloseAutoFocus={(e) => {
          // Return focus to trigger element
          e.preventDefault()
        }}
      >
        {children}
      </DialogContent>
    </Dialog>
  )
}
```

### Keyboard Navigation

```tsx
// Custom dropdown with keyboard support
const Dropdown: React.FC = ({ items, onSelect }) => {
  const [selectedIndex, setSelectedIndex] = useState(0)

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case "ArrowDown":
        e.preventDefault()
        setSelectedIndex((i) => (i + 1) % items.length)
        break
      case "ArrowUp":
        e.preventDefault()
        setSelectedIndex((i) => (i - 1 + items.length) % items.length)
        break
      case "Enter":
        e.preventDefault()
        onSelect(items[selectedIndex])
        break
      case "Escape":
        e.preventDefault()
        // Close dropdown
        break
    }
  }

  return (
    <div role="listbox" onKeyDown={handleKeyDown} tabIndex={0}>
      {items.map((item, index) => (
        <div
          key={index}
          role="option"
          aria-selected={index === selectedIndex}
          className={cn(index === selectedIndex && "bg-accent")}
        >
          {item}
        </div>
      ))}
    </div>
  )
}
```

### ARIA Attributes

```tsx
// Button with loading state
<button
  disabled={isLoading}
  aria-busy={isLoading}
  aria-label={isLoading ? "Loading" : "Submit"}
>
  {isLoading ? <Spinner /> : "Submit"}
</button>

// Toggle button
<button
  role="switch"
  aria-checked={isEnabled}
  onClick={() => setIsEnabled(!isEnabled)}
>
  {isEnabled ? "Enabled" : "Disabled"}
</button>

// Expandable section
<button
  aria-expanded={isOpen}
  aria-controls="content-id"
  onClick={() => setIsOpen(!isOpen)}
>
  Toggle
</button>
<div id="content-id" hidden={!isOpen}>
  Content
</div>
```

---

## Common Components

### Button

```tsx
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

### Input

```tsx
export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: string
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, ...props }, ref) => {
    return (
      <div className="space-y-1">
        <input
          type={type}
          className={cn(
            "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-destructive focus-visible:ring-destructive",
            className
          )}
          ref={ref}
          aria-invalid={!!error}
          aria-describedby={error ? `${props.id}-error` : undefined}
          {...props}
        />
        {error && (
          <p id={`${props.id}-error`} className="text-sm text-destructive" role="alert">
            {error}
          </p>
        )}
      </div>
    )
  }
)
Input.displayName = "Input"

export { Input }
```

### Card

```tsx
const Card = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("rounded-lg border bg-card text-card-foreground shadow-sm", className)}
      {...props}
    />
  )
)
Card.displayName = "Card"

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />
  )
)
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3 ref={ref} className={cn("text-2xl font-semibold leading-none tracking-tight", className)} {...props} />
  )
)
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p ref={ref} className={cn("text-sm text-muted-foreground", className)} {...props} />
  )
)
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
  )
)
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("flex items-center p-6 pt-0", className)} {...props} />
  )
)
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
```

### Modal (Dialog)

```tsx
import * as DialogPrimitive from "@radix-ui/react-dialog"
import { X } from "lucide-react"

const Dialog = DialogPrimitive.Root
const DialogTrigger = DialogPrimitive.Trigger
const DialogPortal = DialogPrimitive.Portal

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      "fixed inset-0 z-50 bg-background/80 backdrop-blur-sm data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className
    )}
    {...props}
  />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content>
>(({ className, children, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      className={cn(
        "fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg duration-200 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=closed]:slide-out-to-left-1/2 data-[state=closed]:slide-out-to-top-[48%] data-[state=open]:slide-in-from-left-1/2 data-[state=open]:slide-in-from-top-[48%] sm:rounded-lg",
        className
      )}
      {...props}
    >
      {children}
      <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
        <X className="h-4 w-4" />
        <span className="sr-only">Close</span>
      </DialogPrimitive.Close>
    </DialogPrimitive.Content>
  </DialogPortal>
))
DialogContent.displayName = DialogPrimitive.Content.displayName

export { Dialog, DialogTrigger, DialogContent }
```

---

## Best Practices

1. **Always forward refs** for DOM components
2. **Use semantic HTML** before adding ARIA
3. **Merge classNames** with cn() utility
4. **Define variants** with cva for consistency
5. **Handle all states**: default, hover, focus, active, disabled, loading, error
6. **Test keyboard navigation** for all interactive components
7. **Provide TypeScript types** for all props
8. **Document component APIs** with JSDoc
9. **Use Radix primitives** for complex components (Dialog, Dropdown, etc.)
10. **Keep components focused** - single responsibility principle
