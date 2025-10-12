"""
Backward-compatible setup.py for filling-scheduler.

Modern configuration is in pyproject.toml.
This file exists for compatibility with older tools.
"""
from setuptools import setup

# Read dependencies from pyproject.toml is handled automatically by setuptools>=61
# This is a minimal setup.py for backward compatibility
setup()
