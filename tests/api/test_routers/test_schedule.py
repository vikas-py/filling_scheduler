"""
Tests for Schedule Router API endpoints.

Tests schedule creation, retrieval, deletion, and WebSocket integration.
"""

from fillscheduler.api.models.database import Schedule, ScheduleResult


def test_create_schedule_endpoint(client, auth_headers, sample_lots):
    """Test creating a schedule via API."""
    response = client.post(
        "/api/v1/schedule",
        headers=auth_headers,
        json={
            "name": "Test Schedule",
            "lots_data": sample_lots,
            "strategy": "smart-pack",
            "config": {},
        },
    )

    assert response.status_code == 202  # Accepted
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Schedule"
    assert data["strategy"] == "smart-pack"
    assert data["status"] in ["pending", "running"]


def test_create_schedule_requires_authentication(client, sample_lots):
    """Test that creating schedule requires authentication."""
    response = client.post(
        "/api/v1/schedule",
        json={"lots_data": sample_lots, "strategy": "smart-pack"},
    )

    assert response.status_code == 401  # Unauthorized


def test_create_schedule_with_invalid_lots(client, auth_headers):
    """Test creating schedule with invalid lots data."""
    invalid_lots = [
        {"lot_id": "", "lot_type": "TypeA", "vials": 1000}  # Missing lot_id and fill_hours
    ]

    response = client.post(
        "/api/v1/schedule", headers=auth_headers, json={"lots_data": invalid_lots}
    )

    assert response.status_code == 400  # Bad Request
    data = response.json()
    assert "errors" in data["detail"]


def test_create_schedule_with_duplicate_lot_ids(client, auth_headers):
    """Test Bug #5 fix - duplicate lot_id should be caught as error."""
    duplicate_lots = [
        {"lot_id": "LOT001", "lot_type": "TypeA", "vials": 1000, "fill_hours": 2.0},
        {"lot_id": "LOT001", "lot_type": "TypeB", "vials": 1500, "fill_hours": 3.0},  # Duplicate
    ]

    response = client.post(
        "/api/v1/schedule", headers=auth_headers, json={"lots_data": duplicate_lots}
    )

    assert response.status_code == 400
    data = response.json()
    assert "Duplicate lot_ids" in str(data["detail"]["errors"])


def test_create_schedule_with_timezone_aware_start_time(client, auth_headers, sample_lots):
    """Test Bug #4 fix - timezone-aware start_time handling."""
    response = client.post(
        "/api/v1/schedule",
        headers=auth_headers,
        json={
            "lots_data": sample_lots,
            "start_time": "2025-10-13T10:00:00+00:00",  # UTC timezone
        },
    )

    assert response.status_code == 202


def test_create_schedule_with_invalid_start_time(client, auth_headers, sample_lots):
    """Test Bug #4 fix - invalid start_time format raises error."""
    response = client.post(
        "/api/v1/schedule",
        headers=auth_headers,
        json={"lots_data": sample_lots, "start_time": "invalid-datetime"},
    )

    assert response.status_code == 400
    data = response.json()
    assert "Invalid start_time format" in data["detail"]


def test_get_schedule_endpoint(client, auth_headers, sample_schedule):
    """Test retrieving a schedule by ID."""
    response = client.get(f"/api/v1/schedule/{sample_schedule.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_schedule.id
    assert data["name"] == sample_schedule.name
    assert data["strategy"] == sample_schedule.strategy


def test_get_schedule_not_found(client, auth_headers):
    """Test getting non-existent schedule returns 404."""
    response = client.get("/api/v1/schedule/9999", headers=auth_headers)
    assert response.status_code == 404


def test_get_schedule_other_users_schedule(client, test_db, test_user, test_superuser):
    """Test that users cannot access other users' schedules."""
    # Create schedule for superuser
    schedule = Schedule(
        user_id=test_superuser.id,
        name="Admin Schedule",
        strategy="smart-pack",
        status="pending",
        config_json="{}",
    )
    test_db.add(schedule)
    test_db.commit()
    test_db.refresh(schedule)

    # Get token for regular test user (not the superuser)
    from fillscheduler.api.utils.security import create_access_token

    token = create_access_token(data={"sub": test_user.email, "user_id": test_user.id})

    # Try to access superuser's schedule with regular user token
    response = client.get(
        f"/api/v1/schedule/{schedule.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404  # Not found (for security)


def test_list_schedules_endpoint(client, auth_headers, sample_schedule):
    """Test listing schedules with pagination."""
    response = client.get("/api/v1/schedules", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "schedules" in data
    assert "total" in data
    assert "page" in data
    assert data["total"] >= 1


def test_list_schedules_pagination(client, auth_headers, test_db, test_user):
    """Test schedule list pagination."""
    # Create multiple schedules
    for i in range(5):
        schedule = Schedule(
            user_id=test_user.id,
            name=f"Schedule {i}",
            strategy="smart-pack",
            status="completed",
            config_json="{}",
        )
        test_db.add(schedule)
    test_db.commit()

    # Get first page
    response = client.get("/api/v1/schedules?page=1&page_size=2", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["schedules"]) == 2
    assert data["page"] == 1


def test_list_schedules_filter_by_status(client, auth_headers, test_db, test_user):
    """Test filtering schedules by status."""
    # Create schedules with different statuses
    for status in ["pending", "running", "completed"]:
        schedule = Schedule(
            user_id=test_user.id,
            name=f"Schedule {status}",
            strategy="smart-pack",
            status=status,
            config_json="{}",
        )
        test_db.add(schedule)
    test_db.commit()

    response = client.get("/api/v1/schedules?status=completed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert all(s["status"] == "completed" for s in data["schedules"])


def test_delete_schedule_endpoint(client, auth_headers, test_db, test_user):
    """Test Bug #2 fix - delete schedule with cascade."""
    # Create schedule with result
    schedule = Schedule(
        user_id=test_user.id,
        name="Schedule to Delete",
        strategy="smart-pack",
        status="completed",
        config_json="{}",
    )
    test_db.add(schedule)
    test_db.commit()
    test_db.refresh(schedule)

    result = ScheduleResult(
        schedule_id=schedule.id,
        makespan=24.5,
        utilization=85.0,
        changeovers=3,
        lots_scheduled=10,
        kpis_json="{}",
        activities_json="[]",
    )
    test_db.add(result)
    test_db.commit()

    # Delete schedule
    response = client.delete(f"/api/v1/schedule/{schedule.id}", headers=auth_headers)

    assert response.status_code == 200

    # Verify schedule is deleted
    response = client.get(f"/api/v1/schedule/{schedule.id}", headers=auth_headers)
    assert response.status_code == 404

    # Verify result is also deleted (cascade)
    from sqlalchemy import select

    stmt = select(ScheduleResult).where(ScheduleResult.schedule_id == schedule.id)
    result_check = test_db.execute(stmt).first()
    assert result_check is None


def test_delete_schedule_not_found(client, auth_headers):
    """Test deleting non-existent schedule."""
    response = client.delete("/api/v1/schedule/9999", headers=auth_headers)
    assert response.status_code == 404


def test_validate_lots_endpoint(client, auth_headers, sample_lots):
    """Test validating lots data without creating schedule."""
    response = client.post("/api/v1/schedule/validate", headers=auth_headers, json=sample_lots)

    assert response.status_code == 200
    data = response.json()
    assert "valid" in data
    assert "errors" in data
    assert "warnings" in data
    assert "lots_count" in data
    assert data["valid"] is True


def test_validate_invalid_lots(client, auth_headers):
    """Test validation endpoint catches errors."""
    invalid_lots = [{"lot_id": "", "lot_type": "TypeA"}]  # Missing fields

    response = client.post("/api/v1/schedule/validate", headers=auth_headers, json=invalid_lots)

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert len(data["errors"]) > 0


def test_list_strategies_endpoint(client, auth_headers):
    """Test Bug #3 fix - list strategies requires authentication."""
    response = client.get("/api/v1/strategies", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check strategy structure
    strategy = data[0]
    assert "name" in strategy
    assert "aliases" in strategy
    assert "description" in strategy


def test_list_strategies_requires_authentication(client):
    """Test Bug #3 fix - strategies endpoint requires auth."""
    response = client.get("/api/v1/strategies")
    assert response.status_code == 401  # Unauthorized
