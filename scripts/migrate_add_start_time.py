"""
Database migration script to add start_time column to schedules table.

This script adds a new nullable start_time column to the schedules table
to store when a schedule should start.
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from sqlalchemy import text  # noqa: E402

from fillscheduler.api.database.session import SessionLocal  # noqa: E402


def migrate():
    """Add start_time column to schedules table."""
    db = SessionLocal()
    try:
        # Check if column already exists
        result = db.execute(
            text("SELECT COUNT(*) FROM pragma_table_info('schedules') WHERE name='start_time'")
        )
        column_exists = result.scalar() > 0

        if column_exists:
            print("✓ Column 'start_time' already exists in schedules table")
            return

        # Add the column
        print("Adding 'start_time' column to schedules table...")
        db.execute(text("ALTER TABLE schedules ADD COLUMN start_time TIMESTAMP"))
        db.commit()
        print("✓ Successfully added 'start_time' column")

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Running migration: Add start_time column to schedules table")
    migrate()
    print("\nMigration completed successfully!")
