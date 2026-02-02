# Database Schema

## Tables

### users (Managed by Better Auth)
| Field | Type | Constraints |
|-------|------|-------------|
| id | string | PK, UUID |
| email | string | Unique, Not Null |
| name | string | Nullable |
| created_at | timestamp | Default now() |

### tasks
| Field | Type | Constraints |
|-------|------|-------------|
| id | integer | PK, Auto-increment |
| user_id | string | FK → users.id, Index |
| title | string | Not Null, Max 200 chars |
| description | text | Nullable, Max 1000 chars |
| completed | boolean | Default false |
| created_at | timestamp | Default now() |
| updated_at | timestamp | Auto-update |

### conversations (Phase III)
| Field | Type | Constraints |
|-------|------|-------------|
| id | integer | PK, Auto-increment |
| user_id | string | FK → users.id, Index |
| created_at | timestamp | Default now() |
| updated_at | timestamp | Auto-update |

### messages (Phase III)
| Field | Type | Constraints |
|-------|------|-------------|
| id | integer | PK, Auto-increment |
| conversation_id | integer | FK → conversations.id, Index |
| user_id | string | FK → users.id |
| role | string | Enum: 'user', 'assistant', 'tool' |
| content | text | Not Null |
| tool_calls | json | Nullable |
| created_at | timestamp | Default now() |

## Indexes
- tasks.user_id (for user filtering)
- tasks.completed (for status filtering)
- messages.conversation_id (for chat history)
