# Tailwind CSS Setup

Complete guide for configuring Tailwind CSS with design tokens and custom utilities.

## Table of Contents
- Installation
- Configuration Structure
- Design Token Integration
- Custom Utilities
- Plugins
- Content Configuration
- JIT Mode Optimization

---

## Installation

### Basic Setup

```bash
# Install Tailwind CSS
npm install -D tailwindcss postcss autoprefixer

# Initialize configuration
npx tailwindcss init -p
```

This creates:
- `tailwind.config.js` - Tailwind configuration
- `postcss.config.js` - PostCSS configuration

### Additional Dependencies

```bash
# For animations
npm install -D tailwindcss-animate

# For forms (optional)
npm install -D @tailwindcss/forms

# For typography (optional)
npm install -D @tailwindcss/typography

# For className utilities
npm install clsx tailwind-merge
npm install class-variance-authority
```

---

## Configuration Structure

### Complete tailwind.config.js

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  // Dark mode configuration
  darkMode: ["class"],

  // Content paths for JIT
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],

  // Theme customization
  theme: {
    // Container configuration
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },

    // Extend default theme
    extend: {
      // Custom colors with CSS variables
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

      // Custom border radius
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },

      // Custom keyframes for animations
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        "fade-in": {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        "fade-out": {
          from: { opacity: "1" },
          to: { opacity: "0" },
        },
        "slide-in-from-top": {
          from: { transform: "translateY(-100%)" },
          to: { transform: "translateY(0)" },
        },
        "slide-in-from-bottom": {
          from: { transform: "translateY(100%)" },
          to: { transform: "translateY(0)" },
        },
        "slide-in-from-left": {
          from: { transform: "translateX(-100%)" },
          to: { transform: "translateX(0)" },
        },
        "slide-in-from-right": {
          from: { transform: "translateX(100%)" },
          to: { transform: "translateX(0)" },
        },
      },

      // Custom animations
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "fade-in": "fade-in 0.2s ease-out",
        "fade-out": "fade-out 0.2s ease-out",
        "slide-in-from-top": "slide-in-from-top 0.3s ease-out",
        "slide-in-from-bottom": "slide-in-from-bottom 0.3s ease-out",
        "slide-in-from-left": "slide-in-from-left 0.3s ease-out",
        "slide-in-from-right": "slide-in-from-right 0.3s ease-out",
      },

      // Custom spacing (if needed beyond defaults)
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },

      // Custom font sizes (if needed beyond defaults)
      fontSize: {
        '2xs': '0.625rem',
      },

      // Custom z-index scale
      zIndex: {
        '60': '60',
        '70': '70',
        '80': '80',
        '90': '90',
        '100': '100',
      },
    },
  },

  // Plugins
  plugins: [
    require("tailwindcss-animate"),
    // require("@tailwindcss/forms"),
    // require("@tailwindcss/typography"),
  ],
}
```

---

## Design Token Integration

### Mapping Design Tokens to Tailwind

**From design-tokens.md to Tailwind config:**

```markdown
## Design Tokens (from specs/ui/design-tokens.md)

### Spacing Scale
- xs: 0.25rem (4px)
- sm: 0.5rem (8px)
- md: 1rem (16px)
- lg: 1.5rem (24px)
- xl: 2rem (32px)
```

**Tailwind already provides this scale:**
- `space-1` = 0.25rem (4px)
- `space-2` = 0.5rem (8px)
- `space-4` = 1rem (16px)
- `space-6` = 1.5rem (24px)
- `space-8` = 2rem (32px)

**For custom spacing:**

```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      spacing: {
        'xs': '0.25rem',
        'sm': '0.5rem',
        'md': '1rem',
        'lg': '1.5rem',
        'xl': '2rem',
        '2xl': '3rem',
      },
    },
  },
}

// Usage
<div className="p-md gap-lg">
```

### Semantic Colors with CSS Variables

**Why CSS Variables?**
- Theme switching (light/dark mode)
- Runtime customization
- Consistent color references

**Setup:**

```js
// tailwind.config.js
colors: {
  primary: {
    DEFAULT: "hsl(var(--primary))",
    foreground: "hsl(var(--primary-foreground))",
  },
  secondary: {
    DEFAULT: "hsl(var(--secondary))",
    foreground: "hsl(var(--secondary-foreground))",
  },
  // ... more semantic colors
}
```

```css
/* globals.css */
:root {
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
}

.dark {
  --primary: 210 40% 98%;
  --primary-foreground: 222.2 47.4% 11.2%;
}
```

**Usage:**

```tsx
<button className="bg-primary text-primary-foreground">
  Primary Button
</button>
```

---

## Custom Utilities

### Adding Custom Utilities

```js
// tailwind.config.js
const plugin = require('tailwindcss/plugin')

module.exports = {
  plugins: [
    plugin(function({ addUtilities, addComponents, theme }) {
      // Custom utilities
      addUtilities({
        '.scrollbar-hide': {
          '-ms-overflow-style': 'none',
          'scrollbar-width': 'none',
          '&::-webkit-scrollbar': {
            display: 'none',
          },
        },
        '.text-balance': {
          'text-wrap': 'balance',
        },
      })

      // Custom components
      addComponents({
        '.btn': {
          padding: theme('spacing.4'),
          borderRadius: theme('borderRadius.md'),
          fontWeight: theme('fontWeight.semibold'),
          '&:hover': {
            opacity: '0.9',
          },
        },
      })
    }),
  ],
}
```

### Common Custom Utilities

```js
// Glassmorphism
'.glass': {
  'background': 'rgba(255, 255, 255, 0.1)',
  'backdrop-filter': 'blur(10px)',
  'border': '1px solid rgba(255, 255, 255, 0.2)',
}

// Gradient text
'.gradient-text': {
  'background': 'linear-gradient(to right, #3b82f6, #8b5cf6)',
  '-webkit-background-clip': 'text',
  '-webkit-text-fill-color': 'transparent',
}

// Truncate with lines
'.line-clamp-3': {
  'display': '-webkit-box',
  '-webkit-line-clamp': '3',
  '-webkit-box-orient': 'vertical',
  'overflow': 'hidden',
}
```

---

## Plugins

### Essential Plugins

**tailwindcss-animate**:
```bash
npm install -D tailwindcss-animate
```

Provides animation utilities for Radix UI components.

**@tailwindcss/forms**:
```bash
npm install -D @tailwindcss/forms
```

Better default styles for form elements.

```js
// tailwind.config.js
plugins: [
  require('@tailwindcss/forms')({
    strategy: 'class', // Use .form-input, .form-select, etc.
  }),
]
```

**@tailwindcss/typography**:
```bash
npm install -D @tailwindcss/typography
```

Beautiful typography defaults for prose content.

```tsx
<article className="prose dark:prose-invert">
  {/* Markdown content */}
</article>
```

---

## Content Configuration

### Optimizing Content Paths

```js
// tailwind.config.js
module.exports = {
  content: [
    // App directory (Next.js 13+)
    './app/**/*.{js,ts,jsx,tsx,mdx}',

    // Pages directory
    './pages/**/*.{js,ts,jsx,tsx,mdx}',

    // Components directory
    './components/**/*.{js,ts,jsx,tsx,mdx}',

    // Src directory
    './src/**/*.{js,ts,jsx,tsx,mdx}',

    // Include node_modules if using component libraries
    './node_modules/@my-company/design-system/**/*.{js,ts,jsx,tsx}',
  ],
}
```

### Safelist for Dynamic Classes

```js
// tailwind.config.js
module.exports = {
  safelist: [
    // Safelist specific classes
    'bg-red-500',
    'text-3xl',

    // Safelist patterns
    {
      pattern: /bg-(red|green|blue)-(100|500|900)/,
      variants: ['hover', 'focus'],
    },

    // Safelist all colors (use sparingly)
    {
      pattern: /bg-.+/,
    },
  ],
}
```

**Note**: Avoid safelisting when possible. Use dynamic classes carefully:

```tsx
// Bad: Dynamic class won't be detected
<div className={`bg-${color}-500`} />

// Good: Use safelist or conditional classes
<div className={color === 'red' ? 'bg-red-500' : 'bg-blue-500'} />
```

---

## JIT Mode Optimization

### JIT (Just-In-Time) Mode

JIT is enabled by default in Tailwind CSS v3+. Benefits:
- Faster build times
- Smaller CSS files
- All variants enabled by default
- Arbitrary values support

### Arbitrary Values

```tsx
// Custom values on the fly
<div className="top-[117px]" />
<div className="bg-[#1da1f2]" />
<div className="grid-cols-[1fr_500px_2fr]" />
```

### Arbitrary Variants

```tsx
// Custom selectors
<div className="[&>*]:p-4" />
<div className="[&:nth-child(3)]:bg-red-500" />
```

### Performance Tips

1. **Keep content paths specific**: Don't scan entire node_modules
2. **Use PurgeCSS options**: Remove unused styles in production
3. **Minimize arbitrary values**: Use theme values when possible
4. **Cache Tailwind builds**: Use build caching in CI/CD

---

## PostCSS Configuration

### postcss.config.js

```js
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
    ...(process.env.NODE_ENV === 'production' ? { cssnano: {} } : {}),
  },
}
```

### Import in CSS

```css
/* app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* Custom base styles */
@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}

/* Custom components */
@layer components {
  .btn-primary {
    @apply bg-primary text-primary-foreground hover:bg-primary/90;
  }
}

/* Custom utilities */
@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}
```

---

## TypeScript Support

### Type-safe Tailwind Config

```ts
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
      },
    },
  },
  plugins: [],
}

export default config
```

### Tailwind IntelliSense

Install VS Code extension:
- **Tailwind CSS IntelliSense**

Configure in `.vscode/settings.json`:

```json
{
  "tailwindCSS.experimental.classRegex": [
    ["cva\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"],
    ["cn\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"]
  ]
}
```

---

## Best Practices

1. **Use semantic color names**: `bg-primary` not `bg-blue-500`
2. **Leverage CSS variables**: For theme switching
3. **Keep config minimal**: Extend only what you need
4. **Use @layer directives**: Organize custom styles
5. **Avoid arbitrary values**: Use theme values when possible
6. **Configure content paths**: Optimize JIT compilation
7. **Use plugins wisely**: Only include what you use
8. **Document custom utilities**: Add comments in config
9. **Version control config**: Track changes to design system
10. **Test dark mode**: Ensure all colors work in both themes
