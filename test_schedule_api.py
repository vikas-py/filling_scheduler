"""
Test script for schedule API endpoints.
"""

import time
from datetime import datetime

import requests

BASE_URL = "http://localhost:8000/api/v1"

# Test lots data
SAMPLE_LOTS = [
    {"lot_id": "LOT001", "lot_type": "TypeA", "vials": 1000, "fill_hours": 2.0},
    {"lot_id": "LOT002", "lot_type": "TypeB", "vials": 1500, "fill_hours": 3.0},
    {"lot_id": "LOT003", "lot_type": "TypeA", "vials": 800, "fill_hours": 1.6},
    {"lot_id": "LOT004", "lot_type": "TypeC", "vials": 1200, "fill_hours": 2.4},
]


def register_and_login():
    """Register a user and get auth token."""
    print("\n" + "=" * 60)
    print("Setting up authentication")
    print("=" * 60)

    # Create unique email with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    email = f"scheduler_test_{timestamp}@example.com"
    password = "TestPassword123!"

    # Register
    response = requests.post(
        f"{BASE_URL}/auth/register", json={"email": email, "password": password}
    )
    print(f"Register Status: {response.status_code}")

    # Login
    response = requests.post(
        f"{BASE_URL}/auth/login", data={"username": email, "password": password}
    )
    print(f"Login Status: {response.status_code}")

    token = response.json()["access_token"]
    print("PASS Got auth token")

    return token


def test_list_strategies(headers):
    """Test listing available strategies."""
    print("\n" + "=" * 60)
    print("Testing List Strategies")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/strategies", headers=headers)
    print(f"Status Code: {response.status_code}")

    strategies = response.json()
    print(f"Available strategies: {len(strategies)}")
    for strategy in strategies:
        print(f"  - {strategy['name']}: {strategy['description']}")

    assert response.status_code == 200
    assert len(strategies) > 0
    print("PASS List strategies passed!")
    return strategies


def test_validate_lots(headers):
    """Test lots data validation."""
    print("\n" + "=" * 60)
    print("Testing Lots Validation")
    print("=" * 60)

    response = requests.post(f"{BASE_URL}/schedule/validate", json=SAMPLE_LOTS, headers=headers)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Valid: {result['valid']}")
    print(f"Lots count: {result['lots_count']}")
    if result["errors"]:
        print(f"Errors: {result['errors']}")
    if result["warnings"]:
        print(f"Warnings: {result['warnings']}")

    assert response.status_code == 200
    assert result["valid"] is True
    assert result["lots_count"] == len(SAMPLE_LOTS)
    print("PASS Lots validation passed!")


def test_create_schedule(headers):
    """Test creating a new schedule."""
    print("\n" + "=" * 60)
    print("Testing Create Schedule")
    print("=" * 60)

    schedule_data = {
        "name": "Test Schedule " + datetime.now().strftime("%H:%M:%S"),
        "lots_data": SAMPLE_LOTS,
        "strategy": "smart-pack",
        "config": {"WINDOW_HOURS": 24.0, "CLEAN_HOURS": 2.0, "CHANGEOVER_DEFAULT": 1.0},
        "start_time": datetime.now().isoformat(),
    }

    response = requests.post(f"{BASE_URL}/schedule", json=schedule_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text[:500]}")

    if response.status_code != 202:
        print(f"ERROR: Expected 202, got {response.status_code}")
        return None

    result = response.json()
    print(f"Schedule ID: {result['id']}")
    print(f"Name: {result['name']}")
    print(f"Strategy: {result['strategy']}")
    print(f"Status: {result['status']}")

    assert response.status_code == 202  # Accepted
    assert result["id"] > 0
    assert result["status"] == "pending"
    print("PASS Create schedule passed!")
    return result["id"]


def test_get_schedule(headers, schedule_id):
    """Test getting schedule details."""
    print("\n" + "=" * 60)
    print(f"Testing Get Schedule (ID: {schedule_id})")
    print("=" * 60)

    # Wait a bit for background task to complete
    print("Waiting for schedule to complete...")
    max_wait = 10  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait:
        response = requests.get(f"{BASE_URL}/schedule/{schedule_id}", headers=headers)

        if response.status_code != 200:
            print(f"  Error: {response.status_code} - {response.text}")
            time.sleep(1)
            continue

        result = response.json()

        if "status" not in result:
            print(f"  Unexpected response: {result}")
            time.sleep(1)
            continue

        print(f"  Status: {result['status']}")

        if result["status"] in ["completed", "failed"]:
            break

        time.sleep(1)

    print(f"\nFinal Status Code: {response.status_code}")
    print(f"Schedule Status: {result['status']}")

    if result["status"] == "completed":
        print(f"Schedule Name: {result['name']}")
        print(f"Strategy: {result['strategy']}")

        if result["result"]:
            print("\nResults:")
            print(f"  Makespan: {result['result']['makespan']:.2f} hours")
            print(f"  Utilization: {result['result']['utilization']:.1f}%")
            print(f"  Changeovers: {result['result']['changeovers']}")
            print(f"  Lots Scheduled: {result['result']['lots_scheduled']}")

            # Check which field name is used (alias or original)
            activities_key = "activities" if "activities" in result["result"] else "activities_json"
            kpis_key = "kpis" if "kpis" in result["result"] else "kpis_json"

            if activities_key in result["result"]:
                print(f"  Activities: {len(result['result'][activities_key])}")

            # Show KPIs
            if kpis_key in result["result"]:
                print("\nKPIs:")
                for key, value in result["result"][kpis_key].items():
                    print(f"  {key}: {value}")
    elif result["status"] == "failed":
        print(f"Error: {result.get('error_message', 'Unknown error')}")

    assert response.status_code == 200
    assert result["status"] == "completed"
    assert result["result"] is not None
    print("PASS Get schedule passed!")
    return result


def test_list_schedules(headers):
    """Test listing schedules."""
    print("\n" + "=" * 60)
    print("Testing List Schedules")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/schedules?page=1&page_size=10", headers=headers)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Total schedules: {result['total']}")
    print(f"Page: {result['page']}/{((result['total']-1)//result['page_size'])+1}")
    print(f"Schedules on this page: {len(result['schedules'])}")

    for schedule in result["schedules"][:3]:  # Show first 3
        print(f"  - {schedule['name']} ({schedule['strategy']}) - {schedule['status']}")

    assert response.status_code == 200
    assert result["total"] > 0
    print("PASS List schedules passed!")


def test_export_schedule(headers, schedule_id):
    """Test exporting schedule."""
    print("\n" + "=" * 60)
    print(f"Testing Export Schedule (ID: {schedule_id})")
    print("=" * 60)

    # Test JSON export
    response = requests.get(
        f"{BASE_URL}/schedule/{schedule_id}/export?format=json", headers=headers
    )
    print(f"JSON Export Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"  Schedule: {data['schedule']['name']}")
        print(f"  Activities: {len(data['results']['activities'])}")

    # Test CSV export
    response = requests.get(f"{BASE_URL}/schedule/{schedule_id}/export?format=csv", headers=headers)
    print(f"CSV Export Status: {response.status_code}")

    if response.status_code == 200:
        lines = response.text.split("\n")
        print(f"  CSV rows: {len(lines)}")
        print(f"  Header: {lines[0][:80]}...")

    assert response.status_code == 200
    print("PASS Export schedule passed!")


def test_delete_schedule(headers, schedule_id):
    """Test deleting a schedule."""
    print("\n" + "=" * 60)
    print(f"Testing Delete Schedule (ID: {schedule_id})")
    print("=" * 60)

    response = requests.delete(f"{BASE_URL}/schedule/{schedule_id}", headers=headers)
    print(f"Status Code: {response.status_code}")
    result = response.json()
    print(f"Message: {result['message']}")

    # Verify it's deleted
    response = requests.get(f"{BASE_URL}/schedule/{schedule_id}", headers=headers)
    print(f"Verification Status: {response.status_code}")

    assert response.status_code == 404  # Not found
    print("PASS Delete schedule passed!")


def main():
    """Run all schedule endpoint tests."""
    print("\n" + "=" * 60)
    print("TESTING FILLING SCHEDULER SCHEDULE API")
    print("=" * 60)

    try:
        # Setup authentication
        token = register_and_login()
        headers = {"Authorization": f"Bearer {token}"}

        # Test 1: List strategies
        test_list_strategies(headers)

        # Test 2: Validate lots data
        test_validate_lots(headers)

        # Test 3: Create schedule
        schedule_id = test_create_schedule(headers)

        # Test 4: Get schedule details
        test_get_schedule(headers, schedule_id)

        # Test 5: List schedules
        test_list_schedules(headers)

        # Test 6: Export schedule
        test_export_schedule(headers, schedule_id)

        # Test 7: Delete schedule
        test_delete_schedule(headers, schedule_id)

        print("\n" + "=" * 60)
        print("ALL SCHEDULE TESTS PASSED!")
        print("=" * 60)
        print("\nSummary:")
        print("  - List strategies: PASS")
        print("  - Validate lots data: PASS")
        print("  - Create schedule: PASS")
        print("  - Get schedule details: PASS")
        print("  - List schedules: PASS")
        print("  - Export schedule (JSON/CSV): PASS")
        print("  - Delete schedule: PASS")
        print("\nSchedule API is fully functional!")

    except AssertionError as e:
        print(f"\nFAIL Test failed: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print("\nFAIL Error: Could not connect to the API server.")
        print("Make sure the server is running at http://localhost:8000")
        return 1
    except Exception as e:
        print(f"\nFAIL Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
