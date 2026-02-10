# Database Migrations

This directory contains database migration scripts for Phase V advanced features.

## Migration 001: Add Advanced Features

**Date:** 2026-02-07
**Phase:** V - Event-Driven Microservices Architecture

### Changes

#### New Columns in `tasks` Table
- `priority` (VARCHAR) - Task priority: low, medium, high
- `due_date` (TIMESTAMP) - When the task is due
- `is_recurring` (BOOLEAN) - Whether this is a recurring task template
- `parent_task_id` (INTEGER) - Reference to parent task for recurring instances
- `recurrence_instance_date` (TIMESTAMP) - The date this instance represents

#### New Tables
- `task_tags` - Tags for task categorization
- `recurring_patterns` - Defines how recurring tasks are generated
- `task_reminders` - Reminders for tasks
- `audit_log` - Audit trail for all operations

### Running Migrations

#### Prerequisites
```bash
pip install asyncpg python-dotenv
```

#### Apply Migration (Forward)
```bash
cd backend/migrations
python run_migration.py up
```

#### Rollback Migration
```bash
cd backend/migrations
python run_migration.py down
```

### Manual Migration (Alternative)

If you prefer to run migrations manually using psql:

```bash
# Forward migration
psql $DATABASE_URL -f 001_add_advanced_features.sql

# Rollback
psql $DATABASE_URL -f 001_rollback.sql
```

### Verification

After running the migration, verify the changes:

```sql
-- Check new columns in tasks table
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'tasks'
AND column_name IN ('priority', 'due_date', 'is_recurring', 'parent_task_id', 'recurrence_instance_date');

-- Check new tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('task_tags', 'recurring_patterns', 'task_reminders', 'audit_log');

-- Check indexes
SELECT indexname, tablename
FROM pg_indexes
WHERE tablename IN ('tasks', 'task_tags', 'recurring_patterns', 'task_reminders', 'audit_log')
ORDER BY tablename, indexname;
```

### Rollback Safety

The rollback script will:
- Drop all new tables (task_tags, recurring_patterns, task_reminders, audit_log)
- Remove all new columns from tasks table
- Drop all new indexes

**WARNING:** Rollback will result in data loss for all advanced features data.

### Next Steps

After successful migration:
1. Update backend API endpoints to use new fields
2. Implement event publishing for Kafka integration
3. Build microservices (Notification, Recurring, Audit)
4. Update frontend UI to support new features
