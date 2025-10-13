"""
Authentication router.

Provides endpoints for:
- User registration
- User login (JWT token)
- Get current user info
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from fillscheduler.api.config import settings
from fillscheduler.api.database.session import get_db
from fillscheduler.api.dependencies import get_current_active_user
from fillscheduler.api.models.schemas import (
    MessageResponse,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from fillscheduler.api.services.auth import authenticate_user, create_user, get_user_by_email
from fillscheduler.api.utils.security import create_access_token

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user: User registration data
        db: Database session

    Returns:
        Created user object

    Raises:
        HTTPException: If email already registered
    """
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    new_user = create_user(db, user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login and get JWT access token.

    OAuth2 compatible endpoint - expects:
    - username: User email
    - password: User password

    Args:
        form_data: OAuth2 form with username and password
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: If credentials are invalid
    """
    # Authenticate user (username field contains email)
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user=Depends(get_current_active_user)):
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user object
    """
    return current_user


@router.post("/logout", response_model=MessageResponse)
def logout():
    """
    Logout endpoint (for compatibility).

    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token. This endpoint is provided for API consistency.

    Returns:
        Success message
    """
    return {
        "message": "Successfully logged out",
        "detail": "Remove the access token from client storage",
    }
