"""
Tests for Configuration Router API endpoints.

Tests configuration management, validation, and presets.

NOTE: These tests were written for a simple config API that doesn't match
the actual template-based config system. They need to be rewritten to test:
- /config (POST) - create config template
- /configs (GET) - list config templates
- /config/{template_id} (GET, PUT, DELETE) - manage specific templates
- /config/default (GET, DELETE) - default config management
- /config/{template_id}/set-default (POST) - set default
- /config/validate (POST) - validate config
- /config/system/default (GET) - get system default
- /config/import (POST) - import config
- /config/{template_id}/export (GET) - export config
"""

import pytest


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_get_config_endpoint(client, auth_headers):
    """Test retrieving current configuration."""
    response = client.get("/api/v1/config", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "num_lines" in data
    assert "changeover_hours" in data
    assert "default_strategy" in data


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_get_config_requires_authentication(client):
    """Test configuration endpoint requires authentication."""
    response = client.get("/api/v1/config")
    assert response.status_code == 401


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_update_config_endpoint(client, auth_headers):
    """Test updating configuration."""
    response = client.put(
        "/api/v1/config",
        headers=auth_headers,
        json={
            "num_lines": 5,
            "changeover_hours": 1.5,
            "default_strategy": "lpt-pack",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["num_lines"] == 5
    assert data["changeover_hours"] == 1.5
    assert data["default_strategy"] == "lpt-pack"


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_update_config_partial(client, auth_headers):
    """Test partial configuration update."""
    response = client.put("/api/v1/config", headers=auth_headers, json={"num_lines": 8})

    assert response.status_code == 200
    data = response.json()
    assert data["num_lines"] == 8


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_update_config_invalid_num_lines(client, auth_headers):
    """Test Bug #7 fix - invalid num_lines raises error."""
    response = client.put("/api/v1/config", headers=auth_headers, json={"num_lines": 0})

    assert response.status_code == 400
    data = response.json()
    assert "num_lines" in data["detail"].lower()


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_update_config_negative_changeover(client, auth_headers):
    """Test Bug #7 fix - negative changeover_hours raises error."""
    response = client.put("/api/v1/config", headers=auth_headers, json={"changeover_hours": -1.0})

    assert response.status_code == 400
    data = response.json()
    assert "changeover_hours" in data["detail"].lower()


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_update_config_invalid_strategy(client, auth_headers):
    """Test invalid default_strategy raises error."""
    response = client.put(
        "/api/v1/config",
        headers=auth_headers,
        json={"default_strategy": "invalid-strategy"},
    )

    assert response.status_code == 400
    data = response.json()
    assert "strategy" in data["detail"].lower()


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_reset_config_endpoint(client, auth_headers):
    """Test resetting configuration to defaults."""
    # First, update config
    client.put("/api/v1/config", headers=auth_headers, json={"num_lines": 10})

    # Reset to defaults
    response = client.post("/api/v1/config/reset", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["num_lines"] == 4  # Default value


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_get_config_presets_endpoint(client, auth_headers):
    """Test getting configuration presets."""
    response = client.get("/api/v1/config/presets", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    # Check preset structure
    preset = data[0]
    assert "name" in preset
    assert "description" in preset
    assert "config" in preset


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_apply_config_preset_endpoint(client, auth_headers):
    """Test applying a configuration preset."""
    # Get available presets
    presets_response = client.get("/api/v1/config/presets", headers=auth_headers)
    presets = presets_response.json()
    preset_name = presets[0]["name"]

    # Apply preset
    response = client.post(f"/api/v1/config/presets/{preset_name}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "num_lines" in data


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_apply_invalid_preset(client, auth_headers):
    """Test applying non-existent preset fails."""
    response = client.post("/api/v1/config/presets/nonexistent", headers=auth_headers)

    assert response.status_code == 404


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_validate_config_endpoint(client, auth_headers):
    """Test validating configuration."""
    response = client.post(
        "/api/v1/config/validate",
        headers=auth_headers,
        json={
            "num_lines": 4,
            "changeover_hours": 2.0,
            "default_strategy": "smart-pack",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "valid" in data
    assert "errors" in data
    assert data["valid"] is True


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_validate_invalid_config(client, auth_headers):
    """Test validation catches invalid configuration."""
    response = client.post(
        "/api/v1/config/validate",
        headers=auth_headers,
        json={
            "num_lines": -1,  # Invalid
            "changeover_hours": -2.0,  # Invalid
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert len(data["errors"]) > 0


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_get_config_schema_endpoint(client, auth_headers):
    """Test getting configuration schema."""
    response = client.get("/api/v1/config/schema", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "properties" in data
    assert "num_lines" in data["properties"]
    assert "changeover_hours" in data["properties"]


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_export_config_endpoint(client, auth_headers):
    """Test exporting configuration as JSON."""
    response = client.get("/api/v1/config/export", headers=auth_headers)

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert "num_lines" in data
    assert "changeover_hours" in data


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_import_config_endpoint(client, auth_headers):
    """Test importing configuration from JSON."""
    config_data = {
        "num_lines": 6,
        "changeover_hours": 1.0,
        "default_strategy": "hybrid-pack",
    }

    response = client.post("/api/v1/config/import", headers=auth_headers, json=config_data)

    assert response.status_code == 200
    data = response.json()
    assert data["num_lines"] == 6
    assert data["changeover_hours"] == 1.0


@pytest.mark.skip(reason="Config API redesign needed - tests don't match template-based system")
def test_import_invalid_config(client, auth_headers):
    """Test importing invalid configuration fails."""
    invalid_config = {"num_lines": -5}

    response = client.post("/api/v1/config/import", headers=auth_headers, json=invalid_config)

    assert response.status_code == 400
