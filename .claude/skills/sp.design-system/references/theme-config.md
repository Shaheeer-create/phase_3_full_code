# Theme Configuration

Complete guide for implementing theming and dark mode in React applications with Tailwind CSS.

## Table of Contents
- Theme Architecture
- Dark Mode Implementation
- Theme Provider Setup
- CSS Variables Strategy
- Theme Switching
- Component Theming
- Best Practices

---

## Theme Architecture

### Design Principles

1. **CSS Variables for Tokens**: Use CSS variables for all theme values
2. **Semantic Naming**: Colors named by purpose (primary, destructive) not appearance (blue, red)
3. **HSL Color Format**: Easier to manipulate (lightness, saturation)
4. **Class-based Dark Mode**: Toggle via `.dark` class on root element
5. **System Preference Support**: Respect user's OS theme preference

### Theme Structure

```
Theme System
├── CSS Variables (globals.css)
│   ├── Light theme (:root)
│   └── Dark theme (.dark)
├── Tailwind Config (tailwind.config.js)
│   └── Map variables to utilities
├── Theme Provider (theme-provider.tsx)
│   └── Manage theme state
└── Theme Toggle (theme-toggle.tsx)
    └── UI for switching themes
```

---

## Dark Mode Implementation

### Step 1: Install next-themes

```bash
npm install next-themes
```

### Step 2: Configure Tailwind

```js
// tailwind.config.js
module.exports = {
  darkMode: ["class"], // Enable class-based dark mode
  // ... rest of config
}
```

### Step 3: Define CSS Variables

```css
/* app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* Light theme */
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;

    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;

    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;

    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;

    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;

    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;

    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;

    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;

    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;

    --radius: 0.5rem;
  }

  .dark {
    /* Dark theme */
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;

    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;

    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;

    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;

    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;

    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;

    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;

    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;

    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

### Step 4: Map to Tailwind

```js
// tailwind.config.js
module.exports = {
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
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
    },
  },
}
```

---

## Theme Provider Setup

### Create Theme Provider

```tsx
// components/theme-provider.tsx
"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { type ThemeProviderProps } from "next-themes/dist/types"

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}
```

### Wrap Application

```tsx
// app/layout.tsx
import { ThemeProvider } from "@/components/theme-provider"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head />
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

**Props Explained**:
- `attribute="class"`: Add `.dark` class to `<html>` element
- `defaultTheme="system"`: Use OS preference by default
- `enableSystem`: Allow system theme detection
- `disableTransitionOnChange`: Prevent flash during theme switch

---

## CSS Variables Strategy

### Why HSL Format?

HSL (Hue, Saturation, Lightness) is easier to manipulate than RGB:

```css
/* HSL: Easy to adjust lightness */
--primary: 222.2 47.4% 11.2%;
--primary-light: 222.2 47.4% 20%; /* Just change lightness */
--primary-dark: 222.2 47.4% 5%;

/* RGB: Harder to adjust */
--primary: 29 78 216;
--primary-light: ??? /* Need to calculate */
```

### Using HSL in Tailwind

```css
/* Define variable without hsl() wrapper */
:root {
  --primary: 222.2 47.4% 11.2%;
}

/* Wrap in hsl() when using */
.bg-primary {
  background-color: hsl(var(--primary));
}
```

### Alpha Channel Support

```tsx
// Tailwind automatically supports alpha
<div className="bg-primary/50" /> // 50% opacity
<div className="bg-primary/20" /> // 20% opacity
```

### Generating Color Scales

```css
:root {
  --primary: 222.2 47.4% 11.2%;
}

/* Generate scale by adjusting lightness */
.bg-primary-50 { background: hsl(222.2 47.4% 95%); }
.bg-primary-100 { background: hsl(222.2 47.4% 90%); }
.bg-primary-200 { background: hsl(222.2 47.4% 80%); }
/* ... */
.bg-primary-900 { background: hsl(222.2 47.4% 10%); }
```

---

## Theme Switching

### Theme Toggle Component

```tsx
// components/theme-toggle.tsx
"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function ThemeToggle() {
  const { setTheme } = useTheme()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>
          Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>
          System
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

### Simple Toggle (No Dropdown)

```tsx
// components/theme-toggle.tsx
"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()

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

### Using Theme in Components

```tsx
"use client"

import { useTheme } from "next-themes"

export function MyComponent() {
  const { theme, setTheme, systemTheme } = useTheme()

  // Current theme (resolves "system" to actual theme)
  const currentTheme = theme === "system" ? systemTheme : theme

  return (
    <div>
      <p>Current theme: {currentTheme}</p>
      <button onClick={() => setTheme("dark")}>Dark</button>
      <button onClick={() => setTheme("light")}>Light</button>
    </div>
  )
}
```

---

## Component Theming

### Theme-Aware Components

```tsx
// Automatically adapts to theme via CSS variables
<Button className="bg-primary text-primary-foreground">
  Primary Button
</Button>

// Works in both light and dark mode
<Card className="bg-card text-card-foreground">
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
  </CardHeader>
</Card>
```

### Dark Mode Variants

```tsx
// Apply different styles in dark mode
<div className="bg-white dark:bg-gray-900">
  <h1 className="text-gray-900 dark:text-white">Title</h1>
  <p className="text-gray-600 dark:text-gray-400">Description</p>
</div>
```

### Images in Dark Mode

```tsx
// Show different images for light/dark
<img
  src="/logo-light.png"
  className="block dark:hidden"
  alt="Logo"
/>
<img
  src="/logo-dark.png"
  className="hidden dark:block"
  alt="Logo"
/>
```

### Conditional Rendering

```tsx
"use client"

import { useTheme } from "next-themes"

export function ThemedChart() {
  const { theme } = useTheme()

  return (
    <Chart
      data={data}
      colors={theme === "dark" ? darkColors : lightColors}
    />
  )
}
```

---

## Best Practices

### 1. Avoid Flash of Unstyled Content (FOUC)

```tsx
// Add suppressHydrationWarning to html tag
<html lang="en" suppressHydrationWarning>
```

```tsx
// Use disableTransitionOnChange to prevent flash
<ThemeProvider
  attribute="class"
  defaultTheme="system"
  enableSystem
  disableTransitionOnChange
>
```

### 2. Handle Server-Side Rendering

```tsx
// Use "use client" for components using useTheme
"use client"

import { useTheme } from "next-themes"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  // ...
}
```

### 3. Test Both Themes

Always test components in both light and dark modes:

```tsx
// Use Storybook or similar
export const LightMode = () => (
  <div className="light">
    <Component />
  </div>
)

export const DarkMode = () => (
  <div className="dark">
    <Component />
  </div>
)
```

### 4. Semantic Color Names

```tsx
// Good: Semantic names
<Button className="bg-primary text-primary-foreground">

// Bad: Specific colors
<Button className="bg-blue-600 text-white">
```

### 5. Consistent Contrast

Ensure sufficient contrast in both themes:

```css
/* Light mode: dark text on light bg */
:root {
  --foreground: 222.2 84% 4.9%; /* Very dark */
  --background: 0 0% 100%; /* White */
}

/* Dark mode: light text on dark bg */
.dark {
  --foreground: 210 40% 98%; /* Very light */
  --background: 222.2 84% 4.9%; /* Very dark */
}
```

### 6. Use Muted Colors for Secondary Text

```tsx
<p className="text-muted-foreground">
  Secondary text that works in both themes
</p>
```

### 7. Border and Input Consistency

```tsx
<input className="border-input bg-background text-foreground" />
<div className="border border-border" />
```

### 8. Focus Rings

```tsx
<button className="focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
  Button
</button>
```

---

## Advanced Theming

### Multiple Themes

```tsx
// Define additional themes
<ThemeProvider
  attribute="class"
  defaultTheme="system"
  themes={["light", "dark", "blue", "green"]}
>
```

```css
/* Add theme-specific variables */
.blue {
  --primary: 217 91% 60%;
  --primary-foreground: 0 0% 100%;
}

.green {
  --primary: 142 76% 36%;
  --primary-foreground: 0 0% 100%;
}
```

### Per-Component Themes

```tsx
// Override theme for specific section
<div className="light">
  <Component /> {/* Always light */}
</div>

<div className="dark">
  <Component /> {/* Always dark */}
</div>
```

### Dynamic Theme Colors

```tsx
// Allow users to customize theme
const [primaryHue, setPrimaryHue] = useState(222)

useEffect(() => {
  document.documentElement.style.setProperty(
    '--primary',
    `${primaryHue} 47.4% 11.2%`
  )
}, [primaryHue])
```

---

## Troubleshooting

### Theme Not Applying

1. Check `suppressHydrationWarning` on `<html>`
2. Verify `darkMode: ["class"]` in Tailwind config
3. Ensure ThemeProvider wraps entire app
4. Check CSS variables are defined in globals.css

### Flash on Page Load

1. Use `disableTransitionOnChange` prop
2. Add `suppressHydrationWarning` to html tag
3. Ensure theme script loads before content

### Colors Not Updating

1. Verify CSS variables use HSL format without `hsl()` wrapper
2. Check Tailwind config maps variables correctly
3. Ensure `@layer base` is used in globals.css
4. Clear build cache and restart dev server

---

## Resources

- [next-themes Documentation](https://github.com/pacocoursey/next-themes)
- [Tailwind Dark Mode Guide](https://tailwindcss.com/docs/dark-mode)
- [shadcn/ui Theming](https://ui.shadcn.com/docs/theming)
- [HSL Color Picker](https://hslpicker.com/)
