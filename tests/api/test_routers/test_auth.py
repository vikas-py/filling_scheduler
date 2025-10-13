"""
Tests for Authentication Router API endpoints.

Tests user registration, login, token management, and user operations.
"""

from datetime import timedelta

import pytest

from fillscheduler.api.models.database import User
from fillscheduler.api.utils.security import create_access_token, get_password_hash


def test_register_user_endpoint(client):
    """Test user registration via API."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 201  # Created
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "password" not in data  # Password should not be returned
    assert data["is_active"] is True
    assert data["is_superuser"] is False
    assert "id" in data
    assert "created_at" in data


def test_register_duplicate_email(client, test_user):
    """Test Bug #6 fix - duplicate email raises error."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,  # Duplicate
            "password": "Password123!",
        },
    )

    assert response.status_code == 400  # Bad Request
    data = response.json()
    assert "already registered" in data["detail"].lower()


def test_register_duplicate_username(client, test_user):
    """Test duplicate email detection (username field not used)."""
    # Note: User model doesn't have username field - testing duplicate email only
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,  # Duplicate email
            "password": "Password123!",
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert "already registered" in data["detail"].lower()


def test_register_weak_password(client):
    """Test password validation rejects weak passwords."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "weak",  # Too short, no uppercase, no number, no special
        },
    )

    # Pydantic validation returns 422, not 400
    assert response.status_code == 422
    data = response.json()
    # detail is a list of validation errors
    assert isinstance(data["detail"], list)
    assert any("password" in str(error).lower() for error in data["detail"])


def test_register_invalid_email(client):
    """Test email validation."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "Password123!",
        },
    )

    assert response.status_code == 422  # Validation error


def test_login_endpoint(client, test_user):
    """Test user login."""
    response = client.post(
        "/api/v1/auth/login",
        data={  # OAuth2PasswordRequestForm uses form data
            "username": test_user.email,
            "password": "TestPassword123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_username(client, test_user):
    """Test login using email (OAuth2 'username' parameter accepts email)."""
    # Note: OAuth2 spec uses "username" parameter, but we pass email value
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "TestPassword123!"},
    )

    assert response.status_code == 200


def test_login_wrong_password(client, test_user):
    """Test login fails with wrong password."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_user.email, "password": "WrongPassword"},
    )

    assert response.status_code == 401  # Unauthorized


def test_login_nonexistent_user(client):
    """Test login fails for non-existent user."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "Password123!"},
    )

    assert response.status_code == 401


def test_login_inactive_user(client, test_db):
    """Test login fails for inactive user."""
    # Create inactive user with properly hashed password
    inactive_user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=False,
    )
    test_db.add(inactive_user)
    test_db.commit()

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "inactive@example.com", "password": "TestPassword123!"},
    )

    assert response.status_code == 401


def test_get_current_user_endpoint(client, auth_headers, test_user):
    """Test getting current user info."""
    response = client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


def test_get_current_user_requires_auth(client):
    """Test /me endpoint requires authentication."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.skip(reason="PUT /me endpoint not implemented yet")
def test_update_user_endpoint(client, auth_headers, test_user):
    """Test updating user profile."""
    response = client.put(
        "/api/v1/auth/me",
        headers=auth_headers,
        json={"email": "updated@example.com"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"


@pytest.mark.skip(reason="PUT /me endpoint not implemented yet")
def test_update_user_to_duplicate_email(client, auth_headers, test_superuser):
    """Test updating email to existing email fails."""
    response = client.put(
        "/api/v1/auth/me",
        headers=auth_headers,
        json={"email": test_superuser.email},  # Duplicate
    )

    assert response.status_code == 400


@pytest.mark.skip(reason="PUT /me/password endpoint not implemented yet")
def test_update_password_endpoint(client, auth_headers):
    """Test changing password."""
    response = client.put(
        "/api/v1/auth/me/password",
        headers=auth_headers,
        json={
            "current_password": "TestPassword123!",
            "new_password": "NewPassword456!",
        },
    )

    assert response.status_code == 200

    # Verify new password works
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "NewPassword456!"},
    )
    assert response.status_code == 200


@pytest.mark.skip(reason="PUT /me/password endpoint not implemented yet")
def test_update_password_wrong_current(client, auth_headers):
    """Test changing password with wrong current password fails."""
    response = client.put(
        "/api/v1/auth/me/password",
        headers=auth_headers,
        json={"current_password": "WrongPassword", "new_password": "NewPassword456!"},
    )

    assert response.status_code == 400


@pytest.mark.skip(reason="DELETE /me endpoint not implemented yet")
def test_delete_user_endpoint(client, auth_headers, test_db, test_user):
    """Test user can delete their own account."""
    response = client.delete("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200

    # Verify user is deleted
    user_check = test_db.query(User).filter(User.id == test_user.id).first()
    assert user_check is None


@pytest.mark.skip(reason="GET /users admin endpoint not implemented yet")
def test_list_users_as_admin(client, test_db, test_superuser):
    """Test admin can list all users."""
    # Get admin token
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_superuser.email, "password": "AdminPassword123!"},
    )
    admin_token = response.json()["access_token"]

    response = client.get("/api/v1/auth/users", headers={"Authorization": f"Bearer {admin_token}"})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # At least test_user and test_superuser


@pytest.mark.skip(reason="GET /users admin endpoint not implemented yet")
def test_list_users_as_regular_user(client, auth_headers):
    """Test regular users cannot list all users."""
    response = client.get("/api/v1/auth/users", headers=auth_headers)
    assert response.status_code == 403  # Forbidden


@pytest.mark.skip(reason="GET /users/{id} admin endpoint not implemented yet")
def test_get_user_by_id_as_admin(client, test_db, test_user, test_superuser):
    """Test admin can get any user by ID."""
    # Get admin token
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_superuser.email, "password": "AdminPassword123!"},
    )
    admin_token = response.json()["access_token"]

    response = client.get(
        f"/api/v1/auth/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id


@pytest.mark.skip(reason="GET /users/{id} admin endpoint not implemented yet")
def test_get_user_by_id_as_regular_user(client, auth_headers, test_superuser):
    """Test regular users cannot get other users by ID."""
    response = client.get(f"/api/v1/auth/users/{test_superuser.id}", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.skip(reason="PUT /users/{id} admin endpoint not implemented yet")
def test_update_user_by_id_as_admin(client, test_db, test_user, test_superuser):
    """Test admin can update any user."""
    # Get admin token
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_superuser.email, "password": "AdminPassword123!"},
    )
    admin_token = response.json()["access_token"]

    response = client.put(
        f"/api/v1/auth/users/{test_user.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"is_active": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


@pytest.mark.skip(reason="DELETE /users/{id} admin endpoint not implemented yet")
def test_delete_user_by_id_as_admin(client, test_db, test_superuser):
    """Test admin can delete any user."""
    # Create user to delete
    user_to_delete = User(
        email="delete@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
    )
    test_db.add(user_to_delete)
    test_db.commit()
    test_db.refresh(user_to_delete)

    # Get admin token
    response = client.post(
        "/api/v1/auth/login",
        data={"username": test_superuser.email, "password": "AdminPassword123!"},
    )
    admin_token = response.json()["access_token"]

    response = client.delete(
        f"/api/v1/auth/users/{user_to_delete.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200

    # Verify user is deleted
    user_check = test_db.query(User).filter(User.id == user_to_delete.id).first()
    assert user_check is None


def test_token_expiration(client, test_user):
    """Test expired token is rejected."""
    # Create token with very short expiration
    expired_token = create_access_token(
        data={"sub": test_user.email}, expires_delta=timedelta(seconds=-1)
    )

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})

    assert response.status_code == 401


def test_invalid_token(client):
    """Test invalid token is rejected."""
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token"})

    assert response.status_code == 401
