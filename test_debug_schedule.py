"""
Simple test to debug schedule creation.
"""

import json
from datetime import datetime

import requests

BASE_URL = "http://localhost:8000/api/v1"

# Test lots data
SAMPLE_LOTS = [
    {"lot_id": "LOT001", "lot_type": "TypeA", "vials": 1000, "fill_hours": 2.0},
    {"lot_id": "LOT002", "lot_type": "TypeB", "vials": 1500, "fill_hours": 3.0},
]


def main():
    # Register and login
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    email = f"debug_{timestamp}@example.com"
    password = "TestPassword123!"

    print("Registering user...")
    response = requests.post(
        f"{BASE_URL}/auth/register", json={"email": email, "password": password}
    )
    print(f"Register: {response.status_code}")

    print("Logging in...")
    response = requests.post(
        f"{BASE_URL}/auth/login", data={"username": email, "password": password}
    )
    print(f"Login: {response.status_code}")
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    print("\nCreating schedule...")
    schedule_data = {
        "name": "Debug Schedule",
        "lots_data": SAMPLE_LOTS,
        "strategy": "smart-pack",
        "config": {},
        "start_time": datetime.now().isoformat(),
    }

    try:
        response = requests.post(f"{BASE_URL}/schedule", json=schedule_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Content: {response.text[:1000]}")

        if response.status_code == 202:
            result = response.json()
            print("\nSuccess!")
            print(json.dumps(result, indent=2))
        else:
            print("\nError response")
    except Exception as e:
        print(f"Exception: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
