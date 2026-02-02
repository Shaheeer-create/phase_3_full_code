
# Frontend Guidelines

## Stack
- **Next.js 16+** (App Router)
- **TypeScript** (strict mode)
- **Tailwind CSS**
- **Better Auth** (for auth UI and hooks)

---

## Patterns
- Use **Server Components** by default  
- Use **Client Components** only when needed (forms, interactivity)  
- All API calls go through **`/lib/api.ts`** (centralized fetcher)

---

## Project Structure

/app
  /login
    page.tsx
  /signup
    page.tsx
  /tasks
    page.tsx
  layout.tsx (root)

/components
  /ui        (shadcn/radix components)
  /tasks     (feature components)

/lib
  api.ts     (axios/fetch wrapper with JWT header)
  auth.ts    (Better Auth client config)
  utils.ts   (cn helper)
````

---

## API Client Pattern

```ts
// /lib/api.ts
import { authClient } from './auth';

export const api = {
  getTasks: async () => {
    const token = await authClient.getToken();
    return fetch('/api/tasks', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
  }
  // ... other methods
};
```

---

## Auth Integration

* Use `authClient` from **Better Auth** for sign in / sign up
* Store session in **httpOnly cookie** (Better Auth handles this)
* Retrieve token via `authClient.getToken()` for API calls
* Use `useSession()` hook for auth state in components

---

## Styling

* **Tailwind CSS only**
* No inline styles
* Use `cn()` utility for conditional classes
* Responsive: **mobile-first**

  * `sm:`
  * `md:`
  * `lg:`

---

