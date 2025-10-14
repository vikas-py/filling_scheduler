#!/usr/bin/env python3
"""
Create Admin User Script

Simple script to create an administrator account in the Filling Scheduler application.
This script works directly with the SQLite database and doesn't require the full
application to be running.

Usage:
    python3 scripts/create_admin.py [--email EMAIL] [--password PASSWORD]

Examples:
    # Interactive mode (will prompt for credentials)
    python3 scripts/create_admin.py

    # With command line arguments
    python3 scripts/create_admin.py --email admin@company.com --password MySecurePass123

    # Quick default admin (for testing only!)
    python3 scripts/create_admin.py --email admin@example.com --password admin123
"""

import argparse
import sqlite3
import sys
from datetime import datetime
from getpass import getpass
from pathlib import Path

# Try to import passlib for password hashing
try:
    from passlib.context import CryptContext
except ImportError:
    print("Error: passlib is not installed.")
    print("Please install it with: pip install passlib[bcrypt]")
    sys.exit(1)

# Password hashing context (must match the application's configuration)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Default database path (relative to project root)
DEFAULT_DB_PATH = "filling_scheduler.db"


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    hashed: str = pwd_context.hash(password)
    return hashed


def get_db_path(custom_path: str | None = None) -> Path:
    """
    Get the database path.

    Args:
        custom_path: Custom database path (optional)

    Returns:
        Path object to the database file
    """
    if custom_path:
        return Path(custom_path)

    # Try to find project root and database
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    db_path = project_root / DEFAULT_DB_PATH

    return db_path


def check_database_exists(db_path: Path) -> bool:
    """Check if the database file exists."""
    return db_path.exists()


def initialize_database(db_path: Path) -> bool:
    """
    Initialize database by importing and running init_db.

    This will create all tables using SQLAlchemy models.
    """
    try:
        # Add src directory to path to import the API modules
        import sys

        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        src_path = project_root / "src"

        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        # Import and run database initialization
        from fillscheduler.api.database.session import init_db

        print("🔄 Initializing database...")
        init_db()
        print(f"✅ Database initialized at: {db_path}")
        return True

    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False


def create_or_upgrade_admin(email: str, password: str, db_path: Path) -> bool:
    """
    Create a new admin user or upgrade an existing user to admin.

    Args:
        email: Admin email address
        password: Admin password (plain text, will be hashed)
        db_path: Path to the SQLite database

    Returns:
        True if successful, False otherwise
    """
    if not check_database_exists(db_path):
        print(f"\n⚠️  Database not found at: {db_path}")
        print("Attempting to initialize database...")

        if not initialize_database(db_path):
            print("\n❌ Failed to initialize database.")
            print("Please ensure you've installed the package dependencies:")
            print("  pip install -r requirements.txt")
            return False

    # Hash the password
    hashed_password = hash_password(password)

    # Connect to database
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT id, email, is_superuser FROM users WHERE email = ?", (email,))
        existing = cursor.fetchone()

        if existing:
            user_id, user_email, is_superuser = existing

            if is_superuser:
                print(f"\n✅ User '{email}' is already an administrator")
                return True
            else:
                # Upgrade existing user to admin
                cursor.execute("UPDATE users SET is_superuser = 1 WHERE id = ?", (user_id,))
                conn.commit()
                print(f"\n✅ Successfully upgraded '{email}' to administrator")
                return True
        else:
            # Create new admin user
            now = datetime.utcnow().isoformat()
            cursor.execute(
                """
                INSERT INTO users (email, hashed_password, is_active, is_superuser, created_at)
                VALUES (?, ?, 1, 1, ?)
                """,
                (email, hashed_password, now),
            )
            conn.commit()
            print(f"\n✅ Successfully created administrator account: {email}")
            return True

    except sqlite3.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False
    finally:
        if "conn" in locals():
            conn.close()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Create an administrator account for the Filling Scheduler application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Interactive mode:
    python3 scripts/create_admin.py

  With arguments:
    python3 scripts/create_admin.py --email admin@company.com --password SecurePass123

  Custom database path:
    python3 scripts/create_admin.py --db /path/to/database.db --email admin@test.com
        """,
    )

    parser.add_argument("--email", help="Admin email address")
    parser.add_argument("--password", help="Admin password (will be hashed)")
    parser.add_argument("--db", help=f"Database path (default: {DEFAULT_DB_PATH})")

    args = parser.parse_args()

    # Print header
    print("\n" + "=" * 70)
    print(" Filling Scheduler - Admin User Creation")
    print("=" * 70)

    # Get database path
    db_path = get_db_path(args.db)
    print(f"\nDatabase: {db_path}")

    # Get email
    if args.email:
        email = args.email
    else:
        print("\nEnter administrator credentials:")
        email = input("Email: ").strip()
        if not email:
            print("❌ Email is required")
            sys.exit(1)

    # Validate email format (basic check)
    if "@" not in email or "." not in email.split("@")[1]:
        print("❌ Invalid email format")
        sys.exit(1)

    # Get password
    if args.password:
        password = args.password
    else:
        password = getpass("Password: ")
        if not password:
            print("❌ Password is required")
            sys.exit(1)

        confirm = getpass("Confirm password: ")
        if password != confirm:
            print("❌ Passwords don't match")
            sys.exit(1)

    # Validate password strength (basic check)
    if len(password) < 8:
        print("⚠️  Warning: Password is shorter than 8 characters")
        response = input("Continue anyway? [y/N]: ").strip().lower()
        if response not in ("y", "yes"):
            sys.exit(0)

    # Create or upgrade the admin user
    success = create_or_upgrade_admin(email, password, db_path)

    if success:
        print("\n" + "=" * 70)
        print(" Login Information")
        print("=" * 70)
        print(f"\n  Email:    {email}")
        print(f"  Password: {'*' * len(password)}")
        print("\n  Frontend: http://localhost:5173 (or your VM IP)")
        print("  Backend:  http://localhost:8000 (or your VM IP)")
        print("\n" + "=" * 70)
        print("\n✅ You can now login to the application with these credentials")
        print()
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
