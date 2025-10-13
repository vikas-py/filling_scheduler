"""
Integration tests for Configuration Template API endpoints.

Tests all CRUD operations, public template sharing, default config management,
validation, and import/export functionality.
"""

from datetime import datetime

import requests

BASE_URL = "http://localhost:8000/api/v1"

# Use timestamp-based unique email for testing
TEST_EMAIL = f"config_test_{datetime.now().strftime('%H%M%S')}@example.com"
TEST_EMAIL_2 = f"config_test2_{datetime.now().strftime('%H%M%S')}@example.com"
TEST_PASSWORD = "testpass123"


def test_config_api():
    """Test all configuration template endpoints."""

    print("\n" + "=" * 70)
    print("TESTING CONFIGURATION TEMPLATE API")
    print("=" * 70)

    # ========================================================================
    # Setup: Register and login two users
    # ========================================================================
    print("\n1. Setting up test users...")

    # User 1
    register_response = requests.post(
        f"{BASE_URL}/auth/register", json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert register_response.status_code == 201, f"Registration failed: {register_response.text}"

    login_response = requests.post(
        f"{BASE_URL}/auth/login", data={"username": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    assert login_response.status_code == 200, f"Login failed: {login_response.text}"
    token_1 = login_response.json()["access_token"]
    headers_1 = {"Authorization": f"Bearer {token_1}"}
    print(f"   ✓ User 1 authenticated: {TEST_EMAIL}")

    # User 2
    register_response_2 = requests.post(
        f"{BASE_URL}/auth/register", json={"email": TEST_EMAIL_2, "password": TEST_PASSWORD}
    )
    assert register_response_2.status_code == 201

    login_response_2 = requests.post(
        f"{BASE_URL}/auth/login", data={"username": TEST_EMAIL_2, "password": TEST_PASSWORD}
    )
    assert login_response_2.status_code == 200
    token_2 = login_response_2.json()["access_token"]
    headers_2 = {"Authorization": f"Bearer {token_2}"}
    print(f"   ✓ User 2 authenticated: {TEST_EMAIL_2}")

    # ========================================================================
    # Test 1: Get system default configuration
    # ========================================================================
    print("\n2. Getting system default configuration...")

    default_response = requests.get(f"{BASE_URL}/config/system/default", headers=headers_1)
    assert default_response.status_code == 200
    system_defaults = default_response.json()
    print("   ✓ System defaults retrieved")
    print(f"   - max_clean_hours: {system_defaults['max_clean_hours']}")
    print(f"   - default_changeover_hours: {system_defaults['default_changeover_hours']}")
    assert "max_clean_hours" in system_defaults
    assert "changeover_matrix" in system_defaults

    # ========================================================================
    # Test 2: Validate configuration
    # ========================================================================
    print("\n3. Testing configuration validation...")

    # Valid configuration
    valid_config = {
        "max_clean_hours": 5.0,
        "default_changeover_hours": 2.5,
        "changeover_matrix": {"Product-A": {"Product-B": 3.0}, "Product-B": {"Product-A": 2.0}},
    }

    validate_response = requests.post(
        f"{BASE_URL}/config/validate", headers=headers_1, json=valid_config
    )
    assert validate_response.status_code == 200
    validation = validate_response.json()
    print(f"   ✓ Valid config validated: valid={validation['valid']}")
    assert validation["valid"] == True

    # Invalid configuration
    invalid_config = {
        "max_clean_hours": "not a number",  # Should be numeric
        "default_changeover_hours": -1.0,  # Should be positive
    }

    validate_response_invalid = requests.post(
        f"{BASE_URL}/config/validate", headers=headers_1, json=invalid_config
    )
    assert validate_response_invalid.status_code == 200
    validation_invalid = validate_response_invalid.json()
    print(f"   ✓ Invalid config detected: valid={validation_invalid['valid']}")
    print(f"     Errors: {validation_invalid['errors']}")
    assert validation_invalid["valid"] == False
    assert len(validation_invalid["errors"]) > 0

    # ========================================================================
    # Test 3: Create private configuration template
    # ========================================================================
    print("\n4. Creating private configuration template...")

    private_config_data = {
        "name": "My Custom Config",
        "description": "Custom configuration for my schedules",
        "config": {
            "max_clean_hours": 6.0,
            "default_changeover_hours": 3.0,
            "min_lot_spacing_hours": 1.0,
            "changeover_matrix": {
                "Product-A": {"Product-B": 4.0, "Product-C": 5.0},
                "Product-B": {"Product-A": 3.5, "Product-C": 4.5},
                "Product-C": {"Product-A": 5.5, "Product-B": 4.5},
            },
        },
        "is_public": False,
    }

    create_response = requests.post(
        f"{BASE_URL}/config", headers=headers_1, json=private_config_data
    )
    assert create_response.status_code == 201, f"Create failed: {create_response.text}"
    template_1 = create_response.json()
    template_1_id = template_1["id"]
    print(f"   ✓ Private template created: ID={template_1_id}")
    print(f"     Name: {template_1['name']}")
    print(f"     Public: {template_1['is_public']}")
    print(f"     Default: {template_1['is_default']}")
    assert template_1["is_public"] == False
    assert template_1["is_default"] == False

    # ========================================================================
    # Test 4: Create public configuration template
    # ========================================================================
    print("\n5. Creating public configuration template...")

    public_config_data = {
        "name": "Standard Pharma Config",
        "description": "Standard configuration for pharmaceutical fills",
        "config": {
            "max_clean_hours": 4.0,
            "default_changeover_hours": 2.0,
            "window_penalty_weight": 2.0,
            "priority_levels": {"critical": 5.0, "high": 3.0, "medium": 2.0, "low": 1.0},
        },
        "is_public": True,
    }

    create_public_response = requests.post(
        f"{BASE_URL}/config", headers=headers_1, json=public_config_data
    )
    assert create_public_response.status_code == 201
    template_2 = create_public_response.json()
    template_2_id = template_2["id"]
    print(f"   ✓ Public template created: ID={template_2_id}")
    print(f"     Name: {template_2['name']}")
    print(f"     Public: {template_2['is_public']}")
    assert template_2["is_public"] == True

    # ========================================================================
    # Test 5: Get configuration template by ID
    # ========================================================================
    print("\n6. Getting configuration template by ID...")

    get_response = requests.get(f"{BASE_URL}/config/{template_1_id}", headers=headers_1)
    assert get_response.status_code == 200
    retrieved_template = get_response.json()
    print(f"   ✓ Template retrieved: {retrieved_template['name']}")
    assert retrieved_template["id"] == template_1_id
    assert retrieved_template["name"] == "My Custom Config"
    assert "config" in retrieved_template

    # ========================================================================
    # Test 6: User 2 cannot access User 1's private template
    # ========================================================================
    print("\n7. Testing access control (private template)...")

    get_private_response = requests.get(f"{BASE_URL}/config/{template_1_id}", headers=headers_2)
    assert get_private_response.status_code == 404, "Private template should not be accessible"
    print("   ✓ User 2 cannot access User 1's private template (404)")

    # ========================================================================
    # Test 7: User 2 CAN access User 1's public template
    # ========================================================================
    print("\n8. Testing access control (public template)...")

    get_public_response = requests.get(f"{BASE_URL}/config/{template_2_id}", headers=headers_2)
    assert get_public_response.status_code == 200
    public_template = get_public_response.json()
    print("   ✓ User 2 can access User 1's public template")
    print(f"     Name: {public_template['name']}")

    # ========================================================================
    # Test 8: List configuration templates
    # ========================================================================
    print("\n9. Listing configuration templates...")

    # User 1: Should see both templates (own private + own public)
    list_response_1 = requests.get(f"{BASE_URL}/configs", headers=headers_1)
    assert list_response_1.status_code == 200
    templates_1 = list_response_1.json()
    print(f"   ✓ User 1 sees {templates_1['total']} templates")
    assert templates_1["total"] == 2

    # User 2: Should see only public template
    list_response_2 = requests.get(f"{BASE_URL}/configs", headers=headers_2)
    assert list_response_2.status_code == 200
    templates_2 = list_response_2.json()
    print(f"   ✓ User 2 sees {templates_2['total']} template(s)")
    assert templates_2["total"] >= 1  # At least the public one

    # Filter: public only
    list_public_response = requests.get(f"{BASE_URL}/configs?public_only=true", headers=headers_1)
    assert list_public_response.status_code == 200
    public_templates = list_public_response.json()
    print(f"   ✓ Public only filter: {public_templates['total']} template(s)")
    assert all(t["is_public"] for t in public_templates["templates"])

    # ========================================================================
    # Test 9: Update configuration template
    # ========================================================================
    print("\n10. Updating configuration template...")

    update_data = {
        "name": "Updated Custom Config",
        "description": "Updated description",
        "config": {"max_clean_hours": 7.0, "default_changeover_hours": 3.5},
    }

    update_response = requests.put(
        f"{BASE_URL}/config/{template_1_id}", headers=headers_1, json=update_data
    )
    assert update_response.status_code == 200
    updated_template = update_response.json()
    print("   ✓ Template updated")
    print(f"     New name: {updated_template['name']}")
    print(f"     New max_clean_hours: {updated_template['config']['max_clean_hours']}")
    assert updated_template["name"] == "Updated Custom Config"
    assert updated_template["config"]["max_clean_hours"] == 7.0

    # ========================================================================
    # Test 10: Set default configuration
    # ========================================================================
    print("\n11. Setting default configuration...")

    set_default_response = requests.post(
        f"{BASE_URL}/config/{template_1_id}/set-default", headers=headers_1
    )
    assert set_default_response.status_code == 200
    default_template = set_default_response.json()
    print(f"   ✓ Template set as default: {default_template['name']}")
    assert default_template["is_default"] == True

    # ========================================================================
    # Test 11: Get user's default configuration
    # ========================================================================
    print("\n12. Getting user's default configuration...")

    get_default_response = requests.get(f"{BASE_URL}/config/default", headers=headers_1)
    if get_default_response.status_code != 200:
        print(
            f"   ❌ GET default failed with status {get_default_response.status_code}: {get_default_response.text}"
        )
    assert get_default_response.status_code == 200
    user_default = get_default_response.json()
    print(f"   ✓ User's default config: {user_default['name']}")
    assert user_default["id"] == template_1_id
    assert user_default["is_default"] == True

    # User 2 should have no default
    get_default_response_2 = requests.get(f"{BASE_URL}/config/default", headers=headers_2)
    assert get_default_response_2.status_code == 200
    user_default_2 = get_default_response_2.json()
    print(f"   ✓ User 2 has no default: {user_default_2}")
    assert user_default_2 is None

    # ========================================================================
    # Test 12: Export configuration template
    # ========================================================================
    print("\n13. Exporting configuration template...")

    export_response = requests.get(f"{BASE_URL}/config/{template_1_id}/export", headers=headers_1)
    assert export_response.status_code == 200
    exported_data = export_response.json()
    print("   ✓ Template exported")
    print(f"     Name: {exported_data['name']}")
    print(f"     Has config: {'config' in exported_data}")
    assert "name" in exported_data
    assert "config" in exported_data
    assert "created_at" in exported_data

    # ========================================================================
    # Test 13: Import configuration template
    # ========================================================================
    print("\n14. Importing configuration template...")

    import_data = {
        "name": "Imported Config",
        "description": "Configuration imported from export",
        "config": exported_data["config"],
    }

    import_response = requests.post(
        f"{BASE_URL}/config/import", headers=headers_2, json=import_data  # User 2 imports it
    )
    assert import_response.status_code == 201
    imported_template = import_response.json()
    imported_id = imported_template["id"]
    print(f"   ✓ Template imported by User 2: ID={imported_id}")
    print(f"     Name: {imported_template['name']}")
    assert imported_template["name"] == "Imported Config"

    # ========================================================================
    # Test 14: Unset default configuration
    # ========================================================================
    print("\n15. Unsetting default configuration...")

    unset_default_response = requests.delete(f"{BASE_URL}/config/default", headers=headers_1)
    if unset_default_response.status_code != 200:
        print(
            f"   ❌ DELETE default failed with status {unset_default_response.status_code}: {unset_default_response.text}"
        )
    assert unset_default_response.status_code == 200
    print("   ✓ Default config unset")

    # Verify no default
    verify_no_default = requests.get(f"{BASE_URL}/config/default", headers=headers_1)
    assert verify_no_default.status_code == 200
    assert verify_no_default.json() is None
    print("   ✓ Verified: User 1 has no default")

    # ========================================================================
    # Test 15: Delete configuration template
    # ========================================================================
    print("\n16. Deleting configuration template...")

    delete_response = requests.delete(f"{BASE_URL}/config/{template_1_id}", headers=headers_1)
    assert delete_response.status_code == 200
    print(f"   ✓ Template deleted: ID={template_1_id}")

    # Verify deletion
    verify_deleted = requests.get(f"{BASE_URL}/config/{template_1_id}", headers=headers_1)
    assert verify_deleted.status_code == 404
    print("   ✓ Verified: Template no longer exists (404)")

    # ========================================================================
    # Test 16: Validation error on invalid config creation
    # ========================================================================
    print("\n17. Testing validation error on creation...")

    invalid_template_data = {
        "name": "Invalid Config",
        "description": "This should fail validation",
        "config": {
            "max_clean_hours": -5.0,  # Invalid: negative
            "default_changeover_hours": "not a number",  # Invalid: not numeric
        },
        "is_public": False,
    }

    create_invalid_response = requests.post(
        f"{BASE_URL}/config", headers=headers_1, json=invalid_template_data
    )
    assert create_invalid_response.status_code == 400
    error_detail = create_invalid_response.json()
    print("   ✓ Invalid config rejected (400)")
    print(f"     Errors: {error_detail['detail']['errors']}")

    # ========================================================================
    # Test 17: Pagination
    # ========================================================================
    print("\n18. Testing pagination...")

    # Create multiple templates for pagination testing
    for i in range(5):
        requests.post(
            f"{BASE_URL}/config",
            headers=headers_1,
            json={
                "name": f"Test Config {i+1}",
                "description": f"Config for pagination test {i+1}",
                "config": {"max_clean_hours": 4.0 + i},
                "is_public": False,
            },
        )

    # Test page 1
    page1_response = requests.get(f"{BASE_URL}/configs?page=1&page_size=3", headers=headers_1)
    assert page1_response.status_code == 200
    page1 = page1_response.json()
    print(f"   ✓ Page 1: {len(page1['templates'])} templates")
    print(f"     Total: {page1['total']}, Pages: {page1['pages']}")
    assert len(page1["templates"]) <= 3
    assert page1["page"] == 1

    print("\n" + "=" * 70)
    print("ALL CONFIGURATION TEMPLATE TESTS PASSED! ✓")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_config_api()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
