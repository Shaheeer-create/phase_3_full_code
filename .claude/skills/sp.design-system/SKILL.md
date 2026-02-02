---
name: sp.design-system
description: Build reusable component libraries with Tailwind CSS, shadcn/ui, and Radix UI. Use when the user needs to: (1) Set up design system infrastructure (Tailwind config, theme), (2) Build reusable UI components (Button, Card, Modal, Input, Form, etc.), (3) Implement component variants and states, (4) Create global styles and theme configuration including dark mode, (5) Document component APIs and usage, or (6) Integrate shadcn/ui or Radix UI primitives. Should be run after UI/UX design specs exist.
---

# Design System Engineer

Build production-ready, reusable component libraries using Tailwind CSS, shadcn/ui, and Radix UI primitives.

## Workflow

### 1. Gather Context

Read existing specifications and design system:
- `specs/ui/design-tokens.md` - Design tokens (spacing, typography, colors)
- `specs/ui/components/<feature>-components.md` - Component specifications
- `specs/architecture.md` - Tech stack and framework constraints
- Project CLAUDE.md - Framework versions (Next.js, React, Tailwind)
- Existing component library (if any)

Extract:
- Required components and their variants
- Design tokens to implement
- Theme requirements (light/dark mode)
- Accessibility requirements
- Framework constraints

### 2. Setup Design System Infrastructure

If starting fresh, set up the design system foundation.

#### Install Dependencies

```bash
# Tailwind CSS (if not installed)
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# shadcn/ui (recommended)
npx shadcn-ui@latest init

# Or Radix UI primitives (manual)
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install class-variance-authority clsx tailwind-merge
```

#### Configure Tailwind

Update `tailwind.config.js` with design tokens. See [references/tailwind-setup.md](references/tailwind-setup.md) for detailed configuration.

```js
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        // ... more semantic colors
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

#### Create Global Styles

Create `app/globals.css` with CSS variables for theming:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    /* ... more tokens */
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    /* ... more tokens */
  }
}
```

#### Create Utility Functions

Create `lib/utils.ts` for className merging:

```ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### 3. Build Components

Create reusable components following the component creation workflow.

#### Component Structure

Organize components in `components/ui/`:

```
components/ui/
├── button.tsx
├── card.tsx
├── input.tsx
├── modal.tsx
├── dropdown.tsx
└── ...
```

#### Component Creation Process

For each component:

1. **Choose Base**: Use shadcn/ui component or Radix primitive
2. **Define Variants**: Use `class-variance-authority` (cva)
3. **Implement States**: Handle loading, disabled, error states
4. **Add Accessibility**: ARIA attributes, keyboard navigation
5. **Document API**: Props, variants, examples

See [references/component-patterns.md](references/component-patterns.md) for detailed patterns.

#### Example: Button Component

```tsx
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
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
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

#### Using shadcn/ui Components

Leverage shadcn/ui for rapid development:

```bash
# Add specific components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add input
npx shadcn-ui@latest add form

# Customize after adding
# Components are copied to your project, not installed as dependencies
```

### 4. Implement Variants and States

Define comprehensive variants for each component.

#### Variant Dimensions

Common variant dimensions:
- **Size**: sm, md (default), lg, xl
- **Variant**: default, primary, secondary, outline, ghost, link
- **Color**: default, destructive, success, warning
- **State**: default, hover, active, focus, disabled, loading

#### State Patterns

**Loading State**:
```tsx
<Button disabled={isLoading}>
  {isLoading && <Spinner className="mr-2" />}
  {isLoading ? "Loading..." : "Submit"}
</Button>
```

**Error State**:
```tsx
<Input
  aria-invalid={!!error}
  aria-describedby={error ? "error-message" : undefined}
  className={cn(error && "border-destructive")}
/>
{error && (
  <p id="error-message" className="text-sm text-destructive">
    {error}
  </p>
)}
```

**Disabled State**:
```tsx
// Handled by variant definition
disabled:pointer-events-none disabled:opacity-50
```

### 5. Create Theme Configuration

Implement comprehensive theming with dark mode support.

#### Theme Provider

Create `components/theme-provider.tsx`:

```tsx
"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { type ThemeProviderProps } from "next-themes/dist/types"

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
```

Wrap app in provider:

```tsx
// app/layout.tsx
import { ThemeProvider } from "@/components/theme-provider"

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

#### Theme Toggle

Create `components/theme-toggle.tsx`:

```tsx
"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"

export function ThemeToggle() {
  const { setTheme, theme } = useTheme()

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={() => setTheme(theme === "light" ? "dark" : "light")}
    >
      <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
```

### 6. Document Components

Create comprehensive documentation for each component.

#### Component Documentation Template

For each component, document:

**API Reference**:
```markdown
## Button

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | "default" \| "destructive" \| "outline" \| "secondary" \| "ghost" \| "link" | "default" | Visual style variant |
| size | "default" \| "sm" \| "lg" \| "icon" | "default" | Size variant |
| asChild | boolean | false | Render as child component (Slot) |
| disabled | boolean | false | Disable button interaction |

### Variants

- **default**: Primary action button
- **destructive**: Dangerous/delete actions
- **outline**: Secondary actions
- **ghost**: Tertiary actions, minimal style
- **link**: Text link styled as button

### Examples

\`\`\`tsx
// Primary action
<Button>Submit</Button>

// Destructive action
<Button variant="destructive">Delete</Button>

// With icon
<Button size="icon">
  <PlusIcon />
</Button>

// Loading state
<Button disabled={isLoading}>
  {isLoading && <Spinner />}
  Submit
</Button>
\`\`\`
```

Create documentation in:
- `components/ui/README.md` - Component library overview
- Inline JSDoc comments in component files
- Storybook stories (optional)

### 7. Create Output Files

Generate or update design system files:

**Component Files**: `components/ui/<component>.tsx`
- Reusable component implementations
- Variant definitions with cva
- TypeScript types and interfaces
- Accessibility attributes

**Configuration**: `tailwind.config.js`
- Extended theme with design tokens
- Custom colors, spacing, typography
- Dark mode configuration
- Plugins

**Global Styles**: `app/globals.css`
- CSS variables for theming
- Light and dark mode tokens
- Base styles and resets
- Utility classes

**Utilities**: `lib/utils.ts`
- className merging (cn)
- Helper functions
- Type utilities

**Documentation**: `components/ui/README.md`
- Component API reference
- Usage examples
- Variant documentation
- Accessibility notes

### 8. Integration with Workflow

**Before running this skill**:
- UI/UX design specs exist (`/sp.ui-architect` completed)
- Design tokens defined in `specs/ui/design-tokens.md`
- Component specifications in `specs/ui/components/`

**After running this skill**:
- Components ready for feature implementation
- Run `/sp.implement` to build features using components
- Components can be used across multiple features

**PHR Creation**:
- Create PHR in `history/prompts/<feature-name>/` or `history/prompts/general/`
- Stage: `green` (implementation work)
- Include links to created component files

**ADR Suggestions**:
Suggest ADR for significant design system decisions:
- Component library choice (shadcn vs custom vs other)
- Styling approach (Tailwind vs CSS-in-JS)
- Theme architecture
- Variant strategy

Example: "📋 Architectural decision detected: Adopting shadcn/ui for component library. Document reasoning? Run `/sp.adr shadcn-component-library`"

## Usage Examples

Basic usage:
```
/sp.design-system
```

Specific components:
```
/sp.design-system button card input
```

With theme setup:
```
/sp.design-system --theme
```

## Success Criteria

- [ ] Design system infrastructure set up (Tailwind, shadcn/Radix)
- [ ] Theme configured with light and dark mode
- [ ] Core components implemented (Button, Card, Input, Modal, etc.)
- [ ] Variants and states defined for each component
- [ ] Global styles created with CSS variables
- [ ] Components follow accessibility guidelines
- [ ] Component APIs documented
- [ ] TypeScript types defined
- [ ] PHR created
- [ ] ADR suggested for significant decisions

## Core Components Checklist

Essential components to implement:

**Form Controls**:
- [ ] Button (with variants and loading state)
- [ ] Input (text, email, password, number)
- [ ] Textarea
- [ ] Select / Dropdown
- [ ] Checkbox
- [ ] Radio
- [ ] Switch / Toggle
- [ ] Label

**Layout**:
- [ ] Card (with header, content, footer)
- [ ] Container
- [ ] Stack / Flex utilities
- [ ] Grid utilities
- [ ] Separator / Divider

**Feedback**:
- [ ] Alert / Toast
- [ ] Badge
- [ ] Progress
- [ ] Spinner / Loader
- [ ] Skeleton

**Overlay**:
- [ ] Modal / Dialog
- [ ] Dropdown Menu
- [ ] Popover
- [ ] Tooltip
- [ ] Sheet (slide-over)

**Navigation**:
- [ ] Tabs
- [ ] Breadcrumb
- [ ] Pagination

**Data Display**:
- [ ] Table
- [ ] Avatar
- [ ] List

## References

- [Component Patterns](references/component-patterns.md) - Detailed component implementation patterns
- [Tailwind Setup](references/tailwind-setup.md) - Complete Tailwind configuration guide
- [Theme Configuration](references/theme-config.md) - Dark mode and theming setup
