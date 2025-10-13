"""
Tests for Comparison Router API endpoints.

Tests strategy comparison runs, result retrieval, and parallel execution.
"""

from fillscheduler.api.models.database import Comparison, ComparisonResult


def test_create_comparison_endpoint(client, auth_headers, sample_lots):
    """Test creating a comparison run via API."""
    response = client.post(
        "/api/v1/comparison",
        headers=auth_headers,
        json={
            "name": "Test Comparison",
            "lots_data": sample_lots,
            "strategies": ["smart-pack", "lpt-pack"],
            "config": {},
        },
    )

    assert response.status_code == 202  # Accepted
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Comparison"
    assert len(data["strategies"]) == 2
    assert data["status"] in ["pending", "running"]


def test_create_comparison_requires_authentication(client, sample_lots):
    """Test comparison creation requires authentication."""
    response = client.post(
        "/api/v1/comparison",
        json={
            "lots_data": sample_lots,
            "strategies": ["smart-pack"],
        },
    )

    assert response.status_code == 401


def test_create_comparison_with_single_strategy(client, auth_headers, sample_lots):
    """Test comparison requires at least 2 strategies."""
    response = client.post(
        "/api/v1/comparison",
        headers=auth_headers,
        json={
            "lots_data": sample_lots,
            "strategies": ["smart-pack"],  # Only one strategy
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert "at least 2 strategies" in data["detail"].lower()


def test_create_comparison_with_invalid_strategy(client, auth_headers, sample_lots):
    """Test comparison with invalid strategy name."""
    response = client.post(
        "/api/v1/comparison",
        headers=auth_headers,
        json={
            "lots_data": sample_lots,
            "strategies": ["invalid-strategy", "smart-pack"],
        },
    )

    assert response.status_code == 400
    data = response.json()
    assert "invalid" in data["detail"].lower()


def test_create_comparison_with_all_strategies(client, auth_headers, sample_lots):
    """Test comparison with all available strategies."""
    response = client.post(
        "/api/v1/comparison",
        headers=auth_headers,
        json={
            "lots_data": sample_lots,
            "strategies": [
                "smart-pack",
                "lpt-pack",
                "spt-pack",
                "cfs-pack",
                "hybrid-pack",
                "milp-opt",
            ],
        },
    )

    assert response.status_code == 202


def test_get_comparison_endpoint(client, auth_headers, test_db, test_user):
    """Test retrieving a comparison by ID."""
    # Create comparison
    comparison = Comparison(
        user_id=test_user.id,
        name="Test Comparison",
        strategies=["smart-pack", "lpt-pack"],
        status="completed",
        config_json="{}",
    )
    test_db.add(comparison)
    test_db.commit()
    test_db.refresh(comparison)

    response = client.get(f"/api/v1/comparison/{comparison.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == comparison.id
    assert data["name"] == comparison.name
    assert len(data["strategies"]) == 2


def test_get_comparison_not_found(client, auth_headers):
    """Test getting non-existent comparison returns 404."""
    response = client.get("/api/v1/comparison/9999", headers=auth_headers)
    assert response.status_code == 404


def test_get_comparison_with_results(client, auth_headers, test_db, test_user):
    """Test getting comparison includes results."""
    # Create comparison with results
    comparison = Comparison(
        user_id=test_user.id,
        name="Test Comparison",
        strategies=["smart-pack", "lpt-pack"],
        status="completed",
        config_json="{}",
    )
    test_db.add(comparison)
    test_db.commit()
    test_db.refresh(comparison)

    # Add results
    result1 = ComparisonResult(
        comparison_id=comparison.id,
        strategy="smart-pack",
        makespan=20.5,
        utilization=90.0,
        changeovers=2,
        lots_scheduled=10,
        kpis_json="{}",
        activities_json="[]",
    )
    result2 = ComparisonResult(
        comparison_id=comparison.id,
        strategy="lpt-pack",
        makespan=22.0,
        utilization=85.0,
        changeovers=3,
        lots_scheduled=10,
        kpis_json="{}",
        activities_json="[]",
    )
    test_db.add_all([result1, result2])
    test_db.commit()

    response = client.get(f"/api/v1/comparison/{comparison.id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 2


def test_list_comparisons_endpoint(client, auth_headers, test_db, test_user):
    """Test listing comparisons with pagination."""
    # Create comparisons
    for i in range(3):
        comparison = Comparison(
            user_id=test_user.id,
            name=f"Comparison {i}",
            strategies=["smart-pack", "lpt-pack"],
            status="completed",
            config_json="{}",
        )
        test_db.add(comparison)
    test_db.commit()

    response = client.get("/api/v1/comparisons", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "comparisons" in data
    assert "total" in data
    assert data["total"] >= 3


def test_list_comparisons_pagination(client, auth_headers, test_db, test_user):
    """Test comparison list pagination."""
    # Create multiple comparisons
    for i in range(5):
        comparison = Comparison(
            user_id=test_user.id,
            name=f"Comparison {i}",
            strategies=["smart-pack", "lpt-pack"],
            status="completed",
            config_json="{}",
        )
        test_db.add(comparison)
    test_db.commit()

    response = client.get("/api/v1/comparisons?page=1&page_size=2", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["comparisons"]) == 2
    assert data["page"] == 1


def test_list_comparisons_filter_by_status(client, auth_headers, test_db, test_user):
    """Test filtering comparisons by status."""
    # Create comparisons with different statuses
    for status in ["pending", "running", "completed"]:
        comparison = Comparison(
            user_id=test_user.id,
            name=f"Comparison {status}",
            strategies=["smart-pack", "lpt-pack"],
            status=status,
            config_json="{}",
        )
        test_db.add(comparison)
    test_db.commit()

    response = client.get("/api/v1/comparisons?status=completed", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert all(c["status"] == "completed" for c in data["comparisons"])


def test_delete_comparison_endpoint(client, auth_headers, test_db, test_user):
    """Test Bug #2 fix - delete comparison with cascade to results."""
    # Create comparison with results
    comparison = Comparison(
        user_id=test_user.id,
        name="Comparison to Delete",
        strategies=["smart-pack", "lpt-pack"],
        status="completed",
        config_json="{}",
    )
    test_db.add(comparison)
    test_db.commit()
    test_db.refresh(comparison)

    # Add results
    result = ComparisonResult(
        comparison_id=comparison.id,
        strategy="smart-pack",
        makespan=20.5,
        utilization=90.0,
        changeovers=2,
        lots_scheduled=10,
        kpis_json="{}",
        activities_json="[]",
    )
    test_db.add(result)
    test_db.commit()

    # Delete comparison
    response = client.delete(f"/api/v1/comparison/{comparison.id}", headers=auth_headers)

    assert response.status_code == 200

    # Verify comparison is deleted
    response = client.get(f"/api/v1/comparison/{comparison.id}", headers=auth_headers)
    assert response.status_code == 404

    # Verify results are also deleted (cascade)
    from sqlalchemy import select

    stmt = select(ComparisonResult).where(ComparisonResult.comparison_id == comparison.id)
    result_check = test_db.execute(stmt).first()
    assert result_check is None


def test_delete_comparison_not_found(client, auth_headers):
    """Test deleting non-existent comparison."""
    response = client.delete("/api/v1/comparison/9999", headers=auth_headers)
    assert response.status_code == 404


def test_get_comparison_summary_endpoint(client, auth_headers, test_db, test_user):
    """Test getting comparison summary statistics."""
    # Create comparison with results
    comparison = Comparison(
        user_id=test_user.id,
        name="Test Comparison",
        strategies=["smart-pack", "lpt-pack", "spt-pack"],
        status="completed",
        config_json="{}",
    )
    test_db.add(comparison)
    test_db.commit()
    test_db.refresh(comparison)

    # Add results with varying performance
    results = [
        ComparisonResult(
            comparison_id=comparison.id,
            strategy="smart-pack",
            makespan=20.5,
            utilization=90.0,
            changeovers=2,
            lots_scheduled=10,
            kpis_json="{}",
            activities_json="[]",
        ),
        ComparisonResult(
            comparison_id=comparison.id,
            strategy="lpt-pack",
            makespan=22.0,
            utilization=85.0,
            changeovers=3,
            lots_scheduled=10,
            kpis_json="{}",
            activities_json="[]",
        ),
        ComparisonResult(
            comparison_id=comparison.id,
            strategy="spt-pack",
            makespan=25.0,
            utilization=80.0,
            changeovers=5,
            lots_scheduled=10,
            kpis_json="{}",
            activities_json="[]",
        ),
    ]
    test_db.add_all(results)
    test_db.commit()

    response = client.get(f"/api/v1/comparison/{comparison.id}/summary", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "best_makespan" in data
    assert "best_utilization" in data
    assert "best_changeovers" in data
    assert data["best_makespan"]["strategy"] == "smart-pack"
    assert data["best_makespan"]["value"] == 20.5


def test_comparison_concurrent_execution(client, auth_headers, sample_lots):
    """Test that comparison strategies run concurrently."""
    import time

    start_time = time.time()

    response = client.post(
        "/api/v1/comparison",
        headers=auth_headers,
        json={
            "lots_data": sample_lots,
            "strategies": ["smart-pack", "lpt-pack", "spt-pack"],
        },
    )

    assert response.status_code == 202

    # Note: Actual concurrent execution is in background task
    # This test just verifies the endpoint accepts the request quickly
    elapsed = time.time() - start_time
    assert elapsed < 1.0  # Should return immediately (background task)
