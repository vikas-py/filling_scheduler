"""
Authentication service.

Handles user authentication, registration, and token management.
"""

from sqlalchemy.orm import Session

from fillscheduler.api.models.database import User
from fillscheduler.api.models.schemas import UserCreate
from fillscheduler.api.utils.security import get_password_hash, verify_password


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Get user by email address.

    Args:
        db: Database session
        email: User email address

    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Get user by ID.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User object or None if not found
    """
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        user: User creation schema

    Returns:
        Created user object
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Authenticate a user by email and password.

    Args:
        db: Database session
        email: User email
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def update_user_password(db: Session, user: User, new_password: str) -> User:
    """
    Update user's password.

    Args:
        db: Database session
        user: User object
        new_password: New plain text password

    Returns:
        Updated user object
    """
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user: User) -> User:
    """
    Deactivate a user account.

    Args:
        db: Database session
        user: User object

    Returns:
        Updated user object
    """
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user
