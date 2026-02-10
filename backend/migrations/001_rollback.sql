-- Rollback Migration 001: Remove Advanced Features
-- Phase V: Event-Driven Microservices Architecture
-- Date: 2026-02-07
-- WARNING: This will drop tables and columns. Data will be lost.

BEGIN;

-- ============================================================================
-- Step 1: Drop new tables (in reverse order of creation)
-- ============================================================================

DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS task_reminders CASCADE;
DROP TABLE IF EXISTS recurring_patterns CASCADE;
DROP TABLE IF EXISTS task_tags CASCADE;

-- ============================================================================
-- Step 2: Drop indexes from tasks table
-- ============================================================================

DROP INDEX IF EXISTS idx_tasks_is_recurring;
DROP INDEX IF EXISTS idx_tasks_parent_id;
DROP INDEX IF EXISTS idx_tasks_due_date;
DROP INDEX IF EXISTS idx_tasks_priority;

-- ============================================================================
-- Step 3: Remove new columns from tasks table
-- ============================================================================

ALTER TABLE tasks
DROP COLUMN IF EXISTS recurrence_instance_date,
DROP COLUMN IF EXISTS parent_task_id,
DROP COLUMN IF EXISTS is_recurring,
DROP COLUMN IF EXISTS due_date,
DROP COLUMN IF EXISTS priority;

COMMIT;

-- Rollback completed successfully
