"""
Minimal test to isolate the error.
"""

import json

import requests

BASE_URL = "http://localhost:8000/api/v1"

# Very minimal test
lots = [{"lot_id": "L1", "lot_type": "A", "vials": 100, "fill_hours": 1.0}]

# Get token
email = "test999@example.com"
password = "Test123456!"

# Register
try:
    requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password})
except Exception:
    pass  # User might already exist

# Login
resp = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test validation first
print("Testing validation...")
resp = requests.post(f"{BASE_URL}/schedule/validate", json=lots, headers=headers)
print(f"Validation: {resp.status_code}")
if resp.status_code == 200:
    print(json.dumps(resp.json(), indent=2))

# Try to create schedule with minimal data
print("\nTesting schedule creation...")
schedule_req = {"lots_data": lots, "strategy": "smart-pack"}

resp = requests.post(f"{BASE_URL}/schedule", json=schedule_req, headers=headers)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:500]}")

if resp.status_code == 202:
    print("\nSUCCESS!")
    print(json.dumps(resp.json(), indent=2))
