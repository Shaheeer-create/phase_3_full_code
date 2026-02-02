# System Architecture

## High-Level Flow
[User] → [Next.js Frontend] → [FastAPI Backend] → [Neon PostgreSQL]
                    ↓
              [Better Auth JWT]

## Authentication Flow
1. User logs in via Better Auth (frontend)
2. Better Auth issues JWT token
3. Frontend stores token (httpOnly cookie or localStorage)
4. Frontend sends `Authorization: Bearer <token>` with every API request
5. FastAPI validates JWT and extracts user_id
6. FastAPI filters all database queries by user_id

## Data Flow
- Create: Frontend POST → Backend validate JWT → SQLModel → DB
- Read: Frontend GET → Backend validate JWT → Filter by user → Return JSON
- Update: Frontend PUT → Backend validate JWT → Verify ownership → Update
- Delete: Frontend DELETE → Backend validate JWT → Verify ownership → Delete

## Security Model
- Shared secret: `BETTER_AUTH_SECRET` (same in frontend .env and backend .env)
- Token expiry: 7 days
- CORS: Frontend origin allowed
- Database: Row-level security via application filtering (user_id checks)
