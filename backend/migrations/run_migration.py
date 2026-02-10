#!/usr/bin/env python3
"""
Database migration runner for Phase V.

Usage:
    python run_migration.py up    # Apply migration
    python run_migration.py down  # Rollback migration
"""
import sys
import os
from pathlib import Path
import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment")
    sys.exit(1)


async def run_migration(direction: str):
    """Run migration up or down."""
    if direction not in ["up", "down"]:
        print("ERROR: Direction must be 'up' or 'down'")
        sys.exit(1)

    # Determine which SQL file to run
    if direction == "up":
        sql_file = Path(__file__).parent / "001_add_advanced_features.sql"
    else:
        sql_file = Path(__file__).parent / "001_rollback.sql"

    if not sql_file.exists():
        print(f"ERROR: Migration file not found: {sql_file}")
        sys.exit(1)

    # Read SQL file
    with open(sql_file, "r") as f:
        sql = f.read()

    print(f"Running migration: {sql_file.name}")
    print("=" * 80)

    # Connect to database
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("✓ Connected to database")

        # Execute migration
        await conn.execute(sql)
        print(f"✓ Migration {direction} completed successfully")

        # Verify tables exist (for 'up' migration)
        if direction == "up":
            tables = await conn.fetch("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('task_tags', 'recurring_patterns', 'task_reminders', 'audit_log')
                ORDER BY table_name
            """)
            print("\n✓ New tables created:")
            for table in tables:
                print(f"  - {table['table_name']}")

            # Verify new columns in tasks table
            columns = await conn.fetch("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'tasks'
                AND column_name IN ('priority', 'due_date', 'is_recurring', 'parent_task_id', 'recurrence_instance_date')
                ORDER BY column_name
            """)
            print("\n✓ New columns added to tasks table:")
            for col in columns:
                print(f"  - {col['column_name']}")

        await conn.close()
        print("\n✓ Database connection closed")
        print("=" * 80)
        print(f"Migration {direction} completed successfully!")

    except Exception as e:
        print(f"\n✗ ERROR: Migration failed")
        print(f"  {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio

    if len(sys.argv) != 2:
        print("Usage: python run_migration.py [up|down]")
        sys.exit(1)

    direction = sys.argv[1].lower()
    asyncio.run(run_migration(direction))
