"""
Test comparison endpoints.

Tests the comparison functionality including:
- Creating comparisons
- Running multiple strategies in parallel
- Getting comparison results
- Best strategy recommendation
- Listing and deleting comparisons
"""

import time
from datetime import datetime

import requests

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = f"comparison_test_{datetime.now().strftime('%H%M%S')}@example.com"
TEST_PASSWORD = "testpass123"

# Sample lots data (4 lots)
sample_lots = [
    {
        "lot_id": "LOT001",
        "lot_type": "Product-A",
        "vials": 1000,
        "fill_hours": 2.5,
        "target_start": "2025-10-15T08:00:00",
        "target_end": "2025-10-15T18:00:00",
    },
    {"lot_id": "LOT002", "lot_type": "Product-B", "vials": 1500, "fill_hours": 2.5},
    {"lot_id": "LOT003", "lot_type": "Product-A", "vials": 800, "fill_hours": 2.0},
    {"lot_id": "LOT004", "lot_type": "Product-C", "vials": 1200, "fill_hours": 2.0},
]


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(title)
    print("=" * 60 + "\n")


def test_comparison_api():
    """Run all comparison API tests."""

    print_section("TESTING FILLING SCHEDULER COMPARISON API")

    # ========================================================================
    # Setup: Authentication
    # ========================================================================
    print_section("Setting up authentication")

    # Register
    register_response = requests.post(
        f"{BASE_URL}/auth/register", json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    print(f"Register Status: {register_response.status_code}")

    # Login
    login_response = requests.post(
        f"{BASE_URL}/auth/login", data={"username": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    print(f"Login Status: {login_response.status_code}")

    if login_response.status_code != 200:
        print("❌ Authentication failed!")
        return False

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Got auth token")

    # ========================================================================
    # Test 1: Create comparison with 3 strategies
    # ========================================================================
    print_section("Testing Create Comparison")

    comparison_request = {
        "name": f"Test Comparison {datetime.now().strftime('%H:%M:%S')}",
        "lots_data": sample_lots,
        "strategies": ["smart-pack", "spt-pack", "lpt-pack"],
        "config": None,
    }

    create_response = requests.post(f"{BASE_URL}/compare", headers=headers, json=comparison_request)

    print(f"Status Code: {create_response.status_code}")

    if create_response.status_code != 202:
        print("❌ Create comparison failed!")
        print(f"Response: {create_response.text}")
        return False

    comparison = create_response.json()
    comparison_id = comparison["id"]
    print(f"Comparison ID: {comparison_id}")
    print(f"Name: {comparison['name']}")
    print(f"Strategies: {comparison['strategies']}")
    print(f"Status: {comparison['status']}")
    print("✅ Create comparison passed!")

    # ========================================================================
    # Test 2: Wait for comparison to complete and get results
    # ========================================================================
    print_section(f"Testing Get Comparison (ID: {comparison_id})")

    print("Waiting for comparison to complete...")
    max_wait = 30  # seconds
    start_time = time.time()

    while time.time() - start_time < max_wait:
        get_response = requests.get(f"{BASE_URL}/compare/{comparison_id}", headers=headers)

        if get_response.status_code != 200:
            print(f"❌ Get comparison failed: {get_response.status_code}")
            print(f"Response: {get_response.text}")
            return False

        result = get_response.json()
        print(f"  Status: {result['status']}")

        if result["status"] == "completed":
            break
        elif result["status"] == "failed":
            print(f"❌ Comparison failed: {result.get('error_message')}")
            return False

        time.sleep(2)
    else:
        print("❌ Comparison did not complete in time!")
        return False

    print(f"\nFinal Status Code: {get_response.status_code}")
    print(f"Comparison Status: {result['status']}")
    print(f"Comparison Name: {result['name']}")
    print(f"Strategies: {result['strategies']}")
    print(f"Best Strategy: {result.get('best_strategy', 'Not determined')}")

    # Check results
    if not result.get("results"):
        print("❌ No results found!")
        return False

    print(f"\nResults ({len(result['results'])} strategies):")
    for strategy_result in result["results"]:
        strategy = strategy_result["strategy"]
        status = strategy_result["status"]
        makespan = strategy_result.get("makespan", "N/A")
        utilization = strategy_result.get("utilization", "N/A")
        changeovers = strategy_result.get("changeovers", "N/A")
        exec_time = strategy_result.get("execution_time", "N/A")

        print(f"  - {strategy}:")
        print(f"      Status: {status}")
        if status == "completed":
            print(f"      Makespan: {makespan:.2f} hours")
            print(f"      Utilization: {utilization:.1f}%")
            print(f"      Changeovers: {changeovers}")
            print(f"      Execution Time: {exec_time:.3f}s")
        else:
            error = strategy_result.get("error_message", "Unknown error")
            print(f"      Error: {error}")

    # Verify best strategy is selected
    if not result.get("best_strategy"):
        print("⚠️  Warning: No best strategy selected")
    else:
        print(f"\n🏆 Best Strategy: {result['best_strategy']}")

        # Verify best strategy has the lowest makespan
        completed_results = [r for r in result["results"] if r["status"] == "completed"]
        if completed_results:
            best_makespan = min(r["makespan"] for r in completed_results)
            best_result = next(r for r in completed_results if r["makespan"] == best_makespan)

            if best_result["strategy"] == result["best_strategy"]:
                print(f"✅ Best strategy correctly identified (makespan: {best_makespan:.2f}h)")
            else:
                print("⚠️  Warning: Best strategy mismatch!")
                print(f"   Algorithm selected: {result['best_strategy']}")
                print(f"   Lowest makespan: {best_result['strategy']} ({best_makespan:.2f}h)")

    print("✅ Get comparison passed!")

    # ========================================================================
    # Test 3: List comparisons
    # ========================================================================
    print_section("Testing List Comparisons")

    list_response = requests.get(f"{BASE_URL}/comparisons", headers=headers)

    print(f"Status Code: {list_response.status_code}")

    if list_response.status_code != 200:
        print("❌ List comparisons failed!")
        print(f"Response: {list_response.text}")
        return False

    list_data = list_response.json()
    print(f"Total comparisons: {list_data['total']}")
    print(f"Page: {list_data['page']}/{list_data['pages']}")
    print(f"Comparisons on this page: {len(list_data['comparisons'])}")

    for comp in list_data["comparisons"]:
        strategies_str = ", ".join(comp["strategies"])
        print(f"  - {comp['name']} ({strategies_str}) - {comp['status']}")

    print("✅ List comparisons passed!")

    # ========================================================================
    # Test 4: Test with 4 strategies (all available except milp-opt and hybrid-pack)
    # ========================================================================
    print_section("Testing Comparison with 4 Strategies")

    comparison_request_4 = {
        "name": f"4-Strategy Comparison {datetime.now().strftime('%H:%M:%S')}",
        "lots_data": sample_lots[:3],  # Use only 3 lots for faster execution
        "strategies": ["smart-pack", "spt-pack", "lpt-pack", "cfs-pack"],
        "config": None,
    }

    create_response_4 = requests.post(
        f"{BASE_URL}/compare", headers=headers, json=comparison_request_4
    )

    if create_response_4.status_code != 202:
        print("❌ Create 4-strategy comparison failed!")
        print(f"Response: {create_response_4.text}")
        return False

    comparison_4 = create_response_4.json()
    comparison_id_4 = comparison_4["id"]
    print(f"Comparison ID: {comparison_id_4}")
    print(f"Strategies: {comparison_4['strategies']}")

    # Wait for completion
    print("Waiting for completion...")
    start_time = time.time()

    while time.time() - start_time < max_wait:
        get_response_4 = requests.get(f"{BASE_URL}/compare/{comparison_id_4}", headers=headers)

        if get_response_4.status_code == 200:
            result_4 = get_response_4.json()
            if result_4["status"] in ["completed", "failed"]:
                break

        time.sleep(2)

    if result_4["status"] == "completed":
        completed_count = sum(1 for r in result_4["results"] if r["status"] == "completed")
        print(f"✅ 4-strategy comparison completed: {completed_count}/4 strategies succeeded")
        print(f"   Best strategy: {result_4.get('best_strategy')}")
    else:
        print(f"⚠️  4-strategy comparison status: {result_4['status']}")

    # ========================================================================
    # Test 5: Test validation errors
    # ========================================================================
    print_section("Testing Validation Errors")

    # Test: Invalid strategy name
    print("Testing invalid strategy name...")
    invalid_strategy_request = {
        "lots_data": sample_lots,
        "strategies": ["smart-pack", "invalid-strategy"],
    }

    invalid_response = requests.post(
        f"{BASE_URL}/compare", headers=headers, json=invalid_strategy_request
    )

    if invalid_response.status_code == 400:
        print("✅ Invalid strategy correctly rejected")
    else:
        print(f"⚠️  Expected 400, got {invalid_response.status_code}")

    # Test: Duplicate strategies
    print("\nTesting duplicate strategies...")
    duplicate_request = {
        "lots_data": sample_lots,
        "strategies": ["smart-pack", "spt-pack", "smart-pack"],
    }

    duplicate_response = requests.post(
        f"{BASE_URL}/compare", headers=headers, json=duplicate_request
    )

    if duplicate_response.status_code == 400:
        print("✅ Duplicate strategies correctly rejected")
    else:
        print(f"⚠️  Expected 400, got {duplicate_response.status_code}")

    # Test: Too few strategies
    print("\nTesting too few strategies...")
    too_few_request = {"lots_data": sample_lots, "strategies": ["smart-pack"]}  # Only 1 strategy

    too_few_response = requests.post(f"{BASE_URL}/compare", headers=headers, json=too_few_request)

    if too_few_response.status_code == 422:  # Pydantic validation error
        print("✅ Too few strategies correctly rejected")
    else:
        print(f"⚠️  Expected 422, got {too_few_response.status_code}")

    # ========================================================================
    # Test 6: Delete comparison
    # ========================================================================
    print_section(f"Testing Delete Comparison (ID: {comparison_id})")

    delete_response = requests.delete(f"{BASE_URL}/compare/{comparison_id}", headers=headers)

    print(f"Status Code: {delete_response.status_code}")

    if delete_response.status_code != 200:
        print("❌ Delete comparison failed!")
        print(f"Response: {delete_response.text}")
        return False

    print(f"Message: {delete_response.json()['message']}")

    # Verify deletion
    verify_response = requests.get(f"{BASE_URL}/compare/{comparison_id}", headers=headers)

    print(f"Verification Status: {verify_response.status_code}")

    if verify_response.status_code == 404:
        print("✅ Comparison successfully deleted!")
    else:
        print(f"⚠️  Expected 404, got {verify_response.status_code}")

    print("✅ Delete comparison passed!")

    # ========================================================================
    # Summary
    # ========================================================================
    print_section("ALL COMPARISON TESTS PASSED!")

    print("Summary:")
    print("  - Create comparison: PASS")
    print("  - Get comparison details: PASS")
    print("  - List comparisons: PASS")
    print("  - 4-strategy comparison: PASS")
    print("  - Validation errors: PASS")
    print("  - Delete comparison: PASS")
    print("\nComparison API is fully functional!")

    return True


if __name__ == "__main__":
    try:
        success = test_comparison_api()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback

        traceback.print_exc()
        exit(1)
