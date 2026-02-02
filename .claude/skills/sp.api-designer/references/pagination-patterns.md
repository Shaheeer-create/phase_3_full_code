# Pagination Patterns

Comprehensive guide to implementing pagination in REST APIs.

## Table of Contents
- Pagination Strategies
- Offset-Based Pagination
- Cursor-Based Pagination
- Keyset Pagination
- Comparison and Decision Guide

---

## Pagination Strategies

### Why Paginate?

**Problems without pagination:**
- Large response payloads (slow, memory-intensive)
- Poor user experience (long load times)
- Database performance issues
- Network bandwidth waste

**Benefits of pagination:**
- Faster response times
- Better database performance
- Improved user experience
- Reduced server load

### Common Strategies

| Strategy | Best For | Pros | Cons |
|----------|----------|------|------|
| Offset-based | Static data, simple UIs | Simple, jump to any page | Performance degrades, inconsistent with real-time data |
| Cursor-based | Real-time data, infinite scroll | Consistent, performant | Can't jump to arbitrary page |
| Keyset | Large datasets, performance-critical | Very fast, consistent | Complex, requires indexed column |

---

## Offset-Based Pagination

### Overview

Use `page` and `page_size` (or `limit` and `offset`) to paginate.

**Best for:**
- Static or slowly-changing data
- Traditional page-based UIs
- Simple implementation requirements

### Request Format

```
GET /api/tasks?page=2&page_size=20
```

**Parameters:**
- `page`: Page number (1-indexed)
- `page_size`: Items per page (default: 20, max: 100)

**Alternative format:**
```
GET /api/tasks?limit=20&offset=20
```

**Parameters:**
- `limit`: Items per page
- `offset`: Number of items to skip

### Response Format

```json
{
  "items": [
    { "id": "21", "title": "Task 21" },
    { "id": "22", "title": "Task 22" }
  ],
  "pagination": {
    "total": 150,
    "page": 2,
    "page_size": 20,
    "total_pages": 8,
    "has_previous": true,
    "has_next": true
  }
}
```

### Implementation (SQL)

```sql
-- Page 2, 20 items per page
SELECT * FROM tasks
ORDER BY created_at DESC
LIMIT 20 OFFSET 20;

-- Calculate offset from page number
-- offset = (page - 1) * page_size
-- Page 1: OFFSET 0
-- Page 2: OFFSET 20
-- Page 3: OFFSET 40
```

### Pros

✅ **Simple to implement**
✅ **Easy to understand**
✅ **Can jump to any page**
✅ **Shows total count**
✅ **Good for static data**

### Cons

❌ **Performance degrades with large offsets**
- `OFFSET 10000` scans and discards 10,000 rows
- Slow for deep pagination

❌ **Inconsistent with real-time data**
- Items added/removed between requests
- Users may see duplicates or miss items

❌ **Total count can be expensive**
- `COUNT(*)` query on large tables

### Example

```python
# FastAPI implementation
@app.get("/api/tasks")
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * page_size

    # Get total count
    total = db.query(Task).count()

    # Get paginated items
    items = db.query(Task)\
        .order_by(Task.created_at.desc())\
        .limit(page_size)\
        .offset(offset)\
        .all()

    return {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
            "has_previous": page > 1,
            "has_next": offset + page_size < total
        }
    }
```

---

## Cursor-Based Pagination

### Overview

Use an opaque cursor (token) to mark position in dataset.

**Best for:**
- Real-time data (social feeds, chat messages)
- Infinite scroll UIs
- Consistent pagination experience

### Request Format

```
# First request (no cursor)
GET /api/tasks?limit=20

# Subsequent requests (with cursor)
GET /api/tasks?cursor=eyJpZCI6IjEyMyJ9&limit=20
```

**Parameters:**
- `cursor`: Opaque token from previous response (optional)
- `limit`: Items per page

### Response Format

```json
{
  "items": [
    { "id": "21", "title": "Task 21" },
    { "id": "22", "title": "Task 22" }
  ],
  "pagination": {
    "next_cursor": "eyJpZCI6IjQwIn0=",
    "has_more": true
  }
}
```

### Cursor Encoding

**Option 1: Base64-encoded ID**
```python
import base64
import json

# Encode
cursor_data = {"id": "123", "created_at": "2026-02-01T10:00:00Z"}
cursor = base64.b64encode(json.dumps(cursor_data).encode()).decode()
# Result: eyJpZCI6IjEyMyIsImNyZWF0ZWRfYXQiOiIyMDI2LTAyLTAxVDEwOjAwOjAwWiJ9

# Decode
cursor_data = json.loads(base64.b64decode(cursor).decode())
```

**Option 2: Encrypted cursor**
```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher = Fernet(key)

# Encode
cursor = cipher.encrypt(json.dumps(cursor_data).encode()).decode()

# Decode
cursor_data = json.loads(cipher.decrypt(cursor.encode()).decode())
```

### Implementation (SQL)

```sql
-- First request (no cursor)
SELECT * FROM tasks
ORDER BY created_at DESC, id DESC
LIMIT 20;

-- Subsequent request (with cursor)
-- Cursor contains: {"created_at": "2026-02-01T10:00:00Z", "id": "123"}
SELECT * FROM tasks
WHERE (created_at, id) < ('2026-02-01T10:00:00Z', '123')
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

### Pros

✅ **Consistent results**
- No duplicates or missing items
- Works with real-time data

✅ **Good performance**
- No large offsets
- Uses indexed columns

✅ **Stateless**
- Cursor contains all needed info

### Cons

❌ **Can't jump to arbitrary page**
- Must paginate sequentially

❌ **No total count**
- Don't know how many pages

❌ **More complex**
- Cursor encoding/decoding
- More complex queries

### Example

```python
# FastAPI implementation
@app.get("/api/tasks")
async def list_tasks(
    cursor: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Task).order_by(Task.created_at.desc(), Task.id.desc())

    # Apply cursor filter
    if cursor:
        cursor_data = decode_cursor(cursor)
        query = query.filter(
            or_(
                Task.created_at < cursor_data["created_at"],
                and_(
                    Task.created_at == cursor_data["created_at"],
                    Task.id < cursor_data["id"]
                )
            )
        )

    # Fetch limit + 1 to check if there are more
    items = query.limit(limit + 1).all()

    has_more = len(items) > limit
    items = items[:limit]

    # Generate next cursor
    next_cursor = None
    if has_more and items:
        last_item = items[-1]
        next_cursor = encode_cursor({
            "created_at": last_item.created_at.isoformat(),
            "id": last_item.id
        })

    return {
        "items": items,
        "pagination": {
            "next_cursor": next_cursor,
            "has_more": has_more
        }
    }

def encode_cursor(data: dict) -> str:
    import base64
    import json
    return base64.b64encode(json.dumps(data).encode()).decode()

def decode_cursor(cursor: str) -> dict:
    import base64
    import json
    return json.loads(base64.b64decode(cursor).decode())
```

---

## Keyset Pagination

### Overview

Similar to cursor-based, but uses actual column values instead of opaque cursor.

**Best for:**
- Large datasets
- Performance-critical applications
- When you need to show page numbers

### Request Format

```
# First request
GET /api/tasks?limit=20

# Subsequent requests
GET /api/tasks?after_id=123&limit=20
```

**Parameters:**
- `after_id`: ID of last item from previous page
- `limit`: Items per page

### Response Format

```json
{
  "items": [
    { "id": "124", "title": "Task 124" },
    { "id": "125", "title": "Task 125" }
  ],
  "pagination": {
    "after_id": "143",
    "has_more": true
  }
}
```

### Implementation (SQL)

```sql
-- First request
SELECT * FROM tasks
ORDER BY id DESC
LIMIT 20;

-- Subsequent request
SELECT * FROM tasks
WHERE id < 123
ORDER BY id DESC
LIMIT 20;
```

### Pros

✅ **Very fast**
- Uses index efficiently
- No offset scanning

✅ **Consistent**
- No duplicates or missing items

✅ **Simple**
- No cursor encoding
- Clear query parameters

### Cons

❌ **Requires indexed column**
- Must order by indexed column

❌ **Can't jump to arbitrary page**
- Sequential pagination only

❌ **Exposed implementation**
- Reveals database IDs

---

## Comparison and Decision Guide

### Performance Comparison

| Strategy | Small Dataset | Large Dataset | Real-time Data |
|----------|---------------|---------------|----------------|
| Offset | ⭐⭐⭐ | ⭐ | ⭐ |
| Cursor | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Keyset | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

### Decision Matrix

**Use Offset-based when:**
- Dataset is small (< 10,000 items)
- Data is static or rarely changes
- Need to jump to arbitrary pages
- Need to show total count
- Simple implementation is priority

**Use Cursor-based when:**
- Data changes frequently (real-time)
- Infinite scroll UI
- Large datasets
- Consistency is important
- Don't need page numbers

**Use Keyset when:**
- Very large datasets (millions of rows)
- Performance is critical
- Have indexed columns to sort by
- Don't need page numbers
- Okay exposing IDs

### Hybrid Approach

Combine strategies for best of both worlds:

```
# Offset for first few pages (fast, can jump)
GET /api/tasks?page=1&page_size=20
GET /api/tasks?page=2&page_size=20

# Cursor for deep pagination (consistent, performant)
GET /api/tasks?cursor=abc123&limit=20
```

---

## Best Practices

1. **Set reasonable limits**
   - Default: 20-50 items
   - Maximum: 100 items
   - Prevent abuse

2. **Always sort consistently**
   - Include unique column (id) in sort
   - Prevents non-deterministic results

3. **Document pagination**
   - Explain parameters
   - Show examples
   - Document limits

4. **Handle edge cases**
   - Empty results
   - Invalid cursors
   - Out of range pages

5. **Consider caching**
   - Cache total counts
   - Cache first page
   - Use ETags

6. **Provide metadata**
   - Has more pages?
   - Total count (if available)
   - Current position

7. **Test with large datasets**
   - Performance testing
   - Consistency testing
   - Edge case testing

---

## Examples by Use Case

### Social Media Feed (Cursor-based)

```
GET /api/feed?limit=20
GET /api/feed?cursor=abc123&limit=20
```

**Why:** Real-time data, infinite scroll, consistency matters

### Admin Dashboard (Offset-based)

```
GET /api/users?page=1&page_size=50
GET /api/users?page=2&page_size=50
```

**Why:** Need page numbers, jump to pages, show total count

### Analytics Report (Keyset)

```
GET /api/events?after_id=1000000&limit=1000
```

**Why:** Millions of rows, performance critical, sequential processing

### Search Results (Offset-based)

```
GET /api/search?q=task&page=1&page_size=20
```

**Why:** Need page numbers, relatively small result sets, jump to pages
