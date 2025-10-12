# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modern Python packaging with `pyproject.toml`
- Development dependencies in `requirements-dev.txt`
- Comprehensive README with examples and documentation
- CHANGELOG.md for tracking changes
- Optional MILP dependency documentation

### Changed
- Project structure flattened (removed nested `filling_scheduler/filling_scheduler/`)
- Moved `requirements.txt` to project root
- Updated `requirements.txt` to include `pulp>=2.7` with optional note

### Fixed
- Missing dependency documentation for MILP optimization

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
