# Filling Scheduler Documentation

Welcome to the Filling Scheduler documentation!

## Contents

- [Getting Started](getting_started.md) - Installation and first steps
- [Configuration Guide](configuration.md) - YAML/JSON configs, environment variables, validation
- [Strategies](strategies.md) - Detailed guide to all scheduling strategies
- [Type Checking](type_checking.md) - mypy configuration and type hints guide
- [API Reference](api_reference.md) - Function and class documentation
- [Examples](examples.md) - Usage examples and tutorials

## Quick Links

- [GitHub Repository](https://github.com/vikas-py/filling_scheduler)
- [Issue Tracker](https://github.com/vikas-py/filling_scheduler/issues)
- [README](../README.md)

## Overview

Filling Scheduler is a production-grade pharmaceutical filling line scheduler that optimizes lot sequencing under strict operational constraints. It provides multiple scheduling strategies from fast heuristics to exact mathematical optimization.

### Key Features

- **6 Scheduling Strategies**: From fast heuristics to exact MILP optimization
- **Configuration Management**: YAML/JSON files with Pydantic validation
- **Environment Variable Support**: 12-factor app compliant
- **Type Safety**: Full mypy type checking with enhanced strictness
- **Comprehensive Testing**: 160 tests with 74.6% coverage
- **Code Quality**: Pre-commit hooks with Black, Ruff, isort, mypy
- **Strict Validation**: Comprehensive constraint checking
- **Rich Reporting**: CSV exports and interactive HTML reports
- **Extensible**: Easy to add new strategies via the Strategy protocol

### For Developers

See [Contributing Guide](../CONTRIBUTING.md) for development setup and guidelines.
