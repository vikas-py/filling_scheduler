"""
Test script for authentication API endpoints.
"""

import json
from datetime import datetime

import requests

BASE_URL = "http://localhost:8000/api/v1"


def test_health():
    """Test health endpoint."""
    print("\n" + "=" * 60)
    print("Testing Health Endpoint")
    print("=" * 60)

    response = requests.get("http://localhost:8000/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Health check passed!")


def test_register():
    """Test user registration."""
    print("\n" + "=" * 60)
    print("Testing User Registration")
    print("=" * 60)

    # Use timestamp to create unique email
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    user_data = {"email": f"testuser_{timestamp}@example.com", "password": "SecurePassword123!"}

    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    if response.status_code != 500:
        print(f"Response JSON: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 201

    # Return email for next test
    result = response.json()
    assert "email" in result
    assert result["email"] == user_data["email"]
    assert result["is_active"] is True
    assert result["is_superuser"] is False
    print("✅ User registration passed!")
    return user_data["email"], user_data["password"]


def test_duplicate_registration(email):
    """Test duplicate registration (should fail)."""
    print("\n" + "=" * 60)
    print("Testing Duplicate Registration (should fail)")
    print("=" * 60)

    user_data = {"email": email, "password": "AnotherPassword123!"}

    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 400
    print("✅ Duplicate registration correctly rejected!")


def test_login(email, password):
    """Test user login."""
    print("\n" + "=" * 60)
    print("Testing User Login")
    print("=" * 60)

    login_data = {"username": email, "password": password}  # OAuth2 uses 'username' field

    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)  # Use form data for OAuth2
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200

    result = response.json()
    assert "access_token" in result
    assert result["token_type"] == "bearer"
    print("✅ Login passed!")
    return result["access_token"]


def test_invalid_login():
    """Test login with invalid credentials."""
    print("\n" + "=" * 60)
    print("Testing Invalid Login (should fail)")
    print("=" * 60)

    login_data = {"username": "invalid@example.com", "password": "WrongPassword123!"}

    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 401
    print("✅ Invalid login correctly rejected!")


def test_get_current_user(token):
    """Test getting current user info."""
    print("\n" + "=" * 60)
    print("Testing Get Current User")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200

    result = response.json()
    assert "email" in result
    assert "id" in result
    print("✅ Get current user passed!")


def test_unauthorized_access():
    """Test accessing protected endpoint without token."""
    print("\n" + "=" * 60)
    print("Testing Unauthorized Access (should fail)")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/auth/me")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 401
    print("✅ Unauthorized access correctly rejected!")


def test_invalid_token():
    """Test accessing protected endpoint with invalid token."""
    print("\n" + "=" * 60)
    print("Testing Invalid Token (should fail)")
    print("=" * 60)

    headers = {"Authorization": "Bearer invalid_token_12345"}

    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 401
    print("✅ Invalid token correctly rejected!")


def test_logout(token):
    """Test logout."""
    print("\n" + "=" * 60)
    print("Testing Logout")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ Logout passed!")


def main():
    """Run all authentication tests."""
    print("\n" + "=" * 60)
    print("🧪 TESTING FILLING SCHEDULER AUTHENTICATION API")
    print("=" * 60)

    try:
        # Test 1: Health check
        test_health()

        # Test 2: Register a new user
        email, password = test_register()

        # Test 3: Try to register the same user again (should fail)
        test_duplicate_registration(email)

        # Test 4: Test invalid login (should fail)
        test_invalid_login()

        # Test 5: Login with the registered user
        token = test_login(email, password)

        # Test 6: Try to access protected endpoint without token (should fail)
        test_unauthorized_access()

        # Test 7: Try to access protected endpoint with invalid token (should fail)
        test_invalid_token()

        # Test 8: Get current user info with valid token
        test_get_current_user(token)

        # Test 9: Logout
        test_logout(token)

        print("\n" + "=" * 60)
        print("✅ ALL AUTHENTICATION TESTS PASSED! 🎉")
        print("=" * 60)
        print("\n📝 Summary:")
        print("  - Health check: ✅")
        print("  - User registration: ✅")
        print("  - Duplicate registration prevention: ✅")
        print("  - User login: ✅")
        print("  - Invalid login prevention: ✅")
        print("  - JWT token generation: ✅")
        print("  - Protected endpoint access: ✅")
        print("  - Token validation: ✅")
        print("  - Logout: ✅")
        print("\n🚀 Authentication system is fully functional!")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the API server.")
        print("Make sure the server is running at http://localhost:8000")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
