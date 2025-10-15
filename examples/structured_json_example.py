"""
Example: Using the Structured JSON Export Endpoint

This script demonstrates how to retrieve schedule data in the structured JSON format
suitable for external API integration and data archival.
"""

import json

import requests


def get_structured_schedule(base_url: str, schedule_id: int, token: str):
    """
    Retrieve a schedule in structured JSON format.

    Args:
        base_url: API base URL (e.g., "http://192.168.56.101:8000")
        schedule_id: Schedule ID to retrieve
        token: JWT authentication token

    Returns:
        dict: Structured schedule data
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    response = requests.get(f"{base_url}/api/v1/schedule/{schedule_id}/structured", headers=headers)

    response.raise_for_status()
    return response.json()


def print_schedule_summary(data: dict):
    """Print a summary of the structured schedule data."""
    schedule = data["schedule"]
    results = data["results"]
    metadata = data["metadata"]

    print("\n" + "=" * 60)
    print("SCHEDULE SUMMARY")
    print("=" * 60)

    print("\nSchedule Information:")
    print(f"  ID: {schedule['id']}")
    print(f"  Name: {schedule['name']}")
    print(f"  Strategy: {schedule['strategy']}")
    print(f"  Status: {schedule['status']}")
    print(f"  Created: {schedule['created_at']}")
    print(f"  Completed: {schedule['completed_at']}")

    print("\nResults:")
    print(f"  Makespan: {results['makespan']} hours")
    print(f"  Utilization: {results['utilization']}%")
    print(f"  Changeovers: {results['changeovers']} hours")
    print(f"  Lots Scheduled: {results['lots_scheduled']}")

    print("\nKey Performance Indicators:")
    for key, value in results["kpis"].items():
        print(f"  {key}: {value}")

    print("\nActivities:")
    print(f"  Total Activities: {len(results['activities'])}")

    # Count by type
    activity_types = {}
    for activity in results["activities"]:
        kind = activity["kind"]
        activity_types[kind] = activity_types.get(kind, 0) + 1

    for kind, count in sorted(activity_types.items()):
        print(f"  {kind}: {count}")

    print("\nMetadata:")
    print(f"  Generated: {metadata['generated_at']}")
    print(f"  API Version: {metadata['api_version']}")
    print(f"  Format Version: {metadata['format_version']}")

    print("\n" + "=" * 60)


def print_activity_details(activities: list, max_activities: int = 5):
    """Print details of first few activities."""
    print(f"\nFirst {max_activities} Activities:")
    print("-" * 80)

    for i, activity in enumerate(activities[:max_activities]):
        print(f"\nActivity {i + 1} ({activity['id']}):")
        print(f"  Type: {activity['kind']}")
        print(f"  Filler: {activity['filler_id']}")
        print(f"  Start: {activity['start']}")
        print(f"  End: {activity['end']}")
        print(f"  Duration: {activity['duration']} hours")

        if activity["lot_id"]:
            print(f"  Lot ID: {activity['lot_id']}")
            print(f"  Lot Type: {activity['lot_type']}")
            if activity["num_units"]:
                print(f"  Units: {activity['num_units']:,}")

        if activity["note"]:
            print(f"  Note: {activity['note']}")


def save_to_file(data: dict, filename: str):
    """Save structured data to JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nData saved to: {filename}")


# Example usage
if __name__ == "__main__":
    # Configuration
    BASE_URL = "http://192.168.56.101:8000"
    SCHEDULE_ID = 1  # Change to your schedule ID
    TOKEN = "your-jwt-token-here"  # Get from login endpoint

    try:
        print("Fetching structured schedule data...")
        data = get_structured_schedule(BASE_URL, SCHEDULE_ID, TOKEN)

        print_schedule_summary(data)
        print_activity_details(data["results"]["activities"])

        # Save to file
        save_to_file(data, f"schedule_{SCHEDULE_ID}_structured.json")

        print("\n✅ Success!")

    except requests.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        if e.response is not None:
            print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
