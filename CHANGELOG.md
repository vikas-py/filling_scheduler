# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Configuration Management System** (Section 9.1, 9.2)
  - YAML and JSON configuration file support
  - Environment variable configuration (FILLSCHEDULER_ prefix)
  - Pydantic v2 validation for all settings
  - Configuration auto-discovery (searches for config.yaml/config.json)
  - `load_config_from_file()`, `load_config_with_overrides()`, `export_default_config()`
  - 34 comprehensive configuration tests
  - Template config file with documentation (config.example.yaml)
  - Configuration Guide documentation (370+ lines)

- **Code Quality Improvements** (Section 6.1, 6.2)
  - Pre-commit hooks with Black, Ruff, isort, mypy
  - Enhanced mypy strictness (11 strict flags enabled)
  - Type checking in CI/CD pipeline
  - Comprehensive type hints across codebase
  - Type Checking Guide documentation (261 lines)

- **Testing Enhancements**
  - Expanded test suite: 160 tests (from 11, +1,354% increase)
  - Test coverage: 74.6% (from 55.3%, +35% improvement)
  - 34 new configuration validation tests
  - 20 test fixture CSV files for comprehensive testing
  - Improved test organization and fixtures

- **Documentation**
  - Configuration Guide (docs/configuration.md)
  - Type Checking Guide (docs/type_checking.md)
  - Updated all examples to use configuration files
  - Comprehensive API reference updates
  - Getting Started guide improvements

- Modern Python packaging with `pyproject.toml`
- Development dependencies in `requirements-dev.txt`
- Comprehensive README with examples and documentation
- CHANGELOG.md for tracking changes
- Optional MILP dependency documentation

### Changed
- Configuration system now uses Pydantic v2 with validation
- All documentation examples updated to use `config_loader`
- Pre-commit hooks automatically format code on commit
- CI/CD includes mypy type checking
- Project structure flattened (removed nested `filling_scheduler/filling_scheduler/`)
- Moved `requirements.txt` to project root
- Updated `requirements.txt` to include `pulp>=2.7` with optional note

### Fixed
- Missing dependency documentation for MILP optimization
- Type hints across all modules
- Configuration validation edge cases
- Test coverage gaps

## [0.1.0] - 2025-10-11

### Added
- Initial project structure
- Six scheduling strategies:
  - `smart-pack` - Advanced heuristic (recommended)
  - `spt-pack` - Shortest Processing Time
  - `lpt-pack` - Longest Processing Time
  - `cfs-pack` - Cluster-First, Schedule-Second
  - `hybrid-pack` - Hybrid heuristic
  - `milp-opt` - Exact MILP optimization
- Comprehensive validation system (input and output)
- HTML and CSV report generation
- Multi-strategy comparison tool
- Test suite with 11 passing tests
- Example datasets (15 lots and 500 lots)
- Data generator utility

### Features
- Strict operational constraints enforcement
- Clean window management (24h clean, 120h max window)
- Changeover time calculation (4h same type, 8h different type)
- Fill rate enforcement (19,920 vials/hour)
- No lot splitting validation
- KPI tracking and reporting

---

## Version History

- **v0.1.0** (2025-10-11) - Initial release with 6 strategies
- **Unreleased** - Project restructuring and improved documentation

[Unreleased]: https://github.com/vikas-py/filling_scheduler/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/vikas-py/filling_scheduler/releases/tag/v0.1.0
