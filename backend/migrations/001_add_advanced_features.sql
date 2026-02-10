-- Migration 001: Add Advanced Features (Priority, Tags, Recurring, Reminders, Audit)
-- Phase V: Event-Driven Microservices Architecture
-- Date: 2026-02-07

BEGIN;

-- ============================================================================
-- Step 1: Add new columns to tasks table
-- ============================================================================

ALTER TABLE tasks
ADD COLUMN priority VARCHAR(10) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
ADD COLUMN due_date TIMESTAMP,
ADD COLUMN is_recurring BOOLEAN DEFAULT FALSE,
ADD COLUMN parent_task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL,
ADD COLUMN recurrence_instance_date TIMESTAMP;

-- Add indexes for new columns
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_parent_id ON tasks(parent_task_id);
CREATE INDEX idx_tasks_is_recurring ON tasks(is_recurring);

-- ============================================================================
-- Step 2: Create task_tags table
-- ============================================================================

CREATE TABLE task_tags (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_name VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(task_id, tag_name)
);

CREATE INDEX idx_task_tags_task_id ON task_tags(task_id);
CREATE INDEX idx_task_tags_tag_name ON task_tags(tag_name);

-- ============================================================================
-- Step 3: Create recurring_patterns table
-- ============================================================================

CREATE TABLE recurring_patterns (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('daily', 'weekly', 'monthly', 'yearly')),
    interval INTEGER DEFAULT 1 CHECK (interval > 0),
    days_of_week VARCHAR(50), -- JSON array: [0,1,2,3,4,5,6] where 0=Sunday
    day_of_month INTEGER CHECK (day_of_month BETWEEN 1 AND 31),
    month_of_year INTEGER CHECK (month_of_year BETWEEN 1 AND 12),
    end_date TIMESTAMP,
    last_generated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_recurring_patterns_task_id ON recurring_patterns(task_id);
CREATE INDEX idx_recurring_patterns_is_active ON recurring_patterns(is_active);

-- ============================================================================
-- Step 4: Create task_reminders table
-- ============================================================================

CREATE TABLE task_reminders (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    reminder_time TIMESTAMP NOT NULL,
    reminder_type VARCHAR(20) DEFAULT 'notification' CHECK (reminder_type IN ('notification', 'email', 'both')),
    is_sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reminders_task_id ON task_reminders(task_id);
CREATE INDEX idx_reminders_user_id ON task_reminders(user_id);
CREATE INDEX idx_reminders_time ON task_reminders(reminder_time, is_sent);

-- ============================================================================
-- Step 5: Create audit_log table
-- ============================================================================

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    action VARCHAR(20) NOT NULL CHECK (action IN ('create', 'update', 'delete', 'complete', 'uncomplete')),
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_action ON audit_log(action);

-- ============================================================================
-- Step 6: Add comments for documentation
-- ============================================================================

COMMENT ON COLUMN tasks.priority IS 'Task priority: low, medium, high';
COMMENT ON COLUMN tasks.due_date IS 'When the task is due';
COMMENT ON COLUMN tasks.is_recurring IS 'Whether this task is a recurring task template';
COMMENT ON COLUMN tasks.parent_task_id IS 'Reference to parent task if this is a recurring instance';
COMMENT ON COLUMN tasks.recurrence_instance_date IS 'The date this instance represents for recurring tasks';

COMMENT ON TABLE task_tags IS 'Tags associated with tasks for categorization';
COMMENT ON TABLE recurring_patterns IS 'Defines how recurring tasks should be generated';
COMMENT ON TABLE task_reminders IS 'Reminders for tasks';
COMMENT ON TABLE audit_log IS 'Audit trail for all task operations';

COMMIT;

-- Migration completed successfully
