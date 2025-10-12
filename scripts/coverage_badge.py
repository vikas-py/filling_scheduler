#!/usr/bin/env python
"""Generate coverage badge for README.

Reads coverage.xml and generates a shields.io badge URL.
"""
import xml.etree.ElementTree as ET
from pathlib import Path


def get_coverage_percentage():
    """Extract coverage percentage from coverage.xml."""
    coverage_file = Path("coverage.xml")
    
    if not coverage_file.exists():
        print("❌ coverage.xml not found. Run: pytest --cov=fillscheduler")
        return None
    
    tree = ET.parse(coverage_file)
    root = tree.getroot()
    
    # Get line coverage
    line_rate = float(root.attrib.get("line-rate", 0))
    percentage = round(line_rate * 100, 2)
    
    return percentage


def get_badge_color(percentage):
    """Get badge color based on coverage percentage."""
    if percentage >= 90:
        return "brightgreen"
    elif percentage >= 75:
        return "green"
    elif percentage >= 60:
        return "yellowgreen"
    elif percentage >= 50:
        return "yellow"
    elif percentage >= 40:
        return "orange"
    else:
        return "red"


def generate_badge_url(percentage):
    """Generate shields.io badge URL."""
    color = get_badge_color(percentage)
    return f"https://img.shields.io/badge/coverage-{percentage}%25-{color}"


def main():
    percentage = get_coverage_percentage()
    
    if percentage is None:
        return 1
    
    badge_url = generate_badge_url(percentage)
    
    print(f"✅ Coverage: {percentage}%")
    print(f"📊 Badge URL: {badge_url}")
    print(f"\nAdd to README.md:")
    print(f"[![Coverage]({badge_url})](htmlcov/index.html)")
    
    return 0


if __name__ == "__main__":
    exit(main())
