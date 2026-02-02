# Backend Guidelines

## Stack
- **FastAPI**
- **SQLModel** (ORM)
- **Neon PostgreSQL** (asyncpg)
- **PyJWT** (for token verification)
- **Python 3.11+**

---

## Project Structure

```txt
main.py        (FastAPI app factory)
models.py      (SQLModel definitions)
deps.py        (dependencies: get_db, get_current_user)
routers/
  tasks.py     (task endpoints)
  auth.py      (if needed for webhooks)
db.py          (database connection/session)
config.py      (settings from env)
````

---

## Authentication Middleware

```python
# deps.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]  # user_id
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

---

## API Conventions

* All routes under `/api/*`
* Prefix every route file with:

  ```python
  router = APIRouter(prefix="/api")
  ```
* Return type hints with **Pydantic models**
* Use `HTTPException` for errors:

| Status | Meaning                |
| ------ | ---------------------- |
| 401    | Auth issues            |
| 403    | Forbidden (wrong user) |
| 404    | Not found              |
| 422    | Validation error       |

---

## Database Conventions

* Use **SQLModel** for all queries
* Always filter by `user_id`:

  ```python
  select(Task).where(Task.user_id == current_user)
  ```
* Use **async sessions**: `AsyncSession`
* Connection string from env:

  ```env
  DATABASE_URL=postgresql+asyncpg://...
  ```

---

## Security Checklist

* Verify JWT on every protected endpoint
* Verify task ownership before update/delete
* Never return other users' data
* Validate input with Pydantic models
* Use parameterized queries (SQLModel handles this)

---


