# Type Checking with mypy

This project uses [mypy](https://mypy.readthedocs.io/) for static type checking to catch type-related bugs before runtime.

## Current Status

**mypy Status**: ✅ Passing with enhanced strictness
**Configuration File**: `mypy.ini`
**CI/CD Integration**: ✅ Enabled in GitHub Actions

## Strictness Level

We are progressively moving towards mypy's strict mode. Our current configuration enables:

### ✅ Currently Enabled (Level 1)

- ✅ `warn_return_any = True` - Warn if a function returns Any
- ✅ `warn_unused_configs = True` - Warn about unused mypy config sections
- ✅ `check_untyped_defs = True` - Type-check the interior of functions without type annotations
- ✅ `no_implicit_optional = True` - Don't assume arguments with default None are Optional
- ✅ `warn_redundant_casts = True` - Warn about redundant casts
- ✅ `warn_unused_ignores = True` - Warn about unnecessary `# type: ignore` comments
- ✅ `warn_no_return = True` - Warn about functions that don't return a value
- ✅ `warn_unreachable = True` - Warn about unreachable code
- ✅ `strict_equality = True` - Prohibit equality checks between incompatible types
- ✅ `strict_optional = True` - Enable strict checking of Optional types
- ✅ `disallow_incomplete_defs = True` - Disallow functions with incomplete type annotations

### 🔄 To Be Enabled (Level 2)

These will be enabled after adding more comprehensive type hints:

- ⏳ `disallow_untyped_defs = True` - Require all functions to have type annotations
- ⏳ `disallow_untyped_decorators = True` - Require decorators to preserve or add type information

### 🎯 Future (Strict Mode)

Full strict mode equivalent includes all of the above plus:

- `disallow_any_generics = True` (✅ Enabled in pyproject.toml)
- `disallow_subclassing_any = True` (✅ Enabled in pyproject.toml)
- `disallow_untyped_calls = True` (⏳ To be enabled)

## Running mypy Locally

### Check all source files:
```bash
mypy src/fillscheduler
```

### Check specific file:
```bash
mypy src/fillscheduler/scheduler.py
```

### Generate HTML report:
```bash
mypy src/fillscheduler --html-report mypy-report/
```

## Ignoring Type Errors

When necessary, you can ignore specific type errors:

```python
# Ignore specific error on one line
result = some_function()  # type: ignore[attr-defined]

# Ignore all errors on one line (discouraged)
result = some_function()  # type: ignore

# Ignore errors in entire file (legacy code only)
# At top of file:
# type: ignore
```

**Best Practice**: Always include the specific error code when using `type: ignore`.

## Configuration Files

### Primary: `mypy.ini`
- Main configuration file
- Contains all mypy settings
- Per-module overrides for test files

### Secondary: `pyproject.toml`
- Contains additional mypy settings for strict mode
- Module-specific overrides (e.g., for `pulp` library)

## Per-Module Configuration

### Ignored Modules
```ini
[mypy-tests.*]
ignore_errors = True
```
- Test files are allowed to have type errors for simplicity
- Focus is on production code quality

### Third-Party Libraries
```python
[[tool.mypy.overrides]]
module = ["pulp.*"]
ignore_missing_imports = true
```
- External libraries without type stubs are ignored
- Prevents false positives from untyped dependencies

## Type Hints Best Practices

### Function Signatures
```python
def schedule_lots(
    lots: list[Lot],
    config: AppConfig,
    strategy: str = "lpt"
) -> Schedule:
    """Schedule lots using specified strategy."""
    ...
```

### Return Types
```python
def get_makespan(schedule: Schedule) -> float:
    """Calculate makespan in hours."""
    return schedule.end_time - schedule.start_time
```

### Optional Types
```python
from typing import Optional

def find_lot(lot_id: str) -> Optional[Lot]:
    """Find lot by ID, return None if not found."""
    ...
```

### Generic Types
```python
from typing import TypeVar, Generic

T = TypeVar('T')

def first_or_none(items: list[T]) -> Optional[T]:
    """Return first item or None if list is empty."""
    return items[0] if items else None
```

## CI/CD Integration

mypy runs automatically in CI/CD pipeline:

```yaml
- name: Run type checking
  run: |
    mypy src/fillscheduler --config-file mypy.ini
```

### CI/CD Checks Include:
1. **Type checking** - All source files must pass mypy
2. **Linting** - Black, Ruff, isort checks
3. **Tests** - All tests must pass
4. **Coverage** - Maintain 70%+ coverage

## Roadmap to Strict Mode

### Phase 1: Current (✅ Complete)
- [x] Enable basic strictness (warn_return_any, etc.)
- [x] Enable strict_optional
- [x] Enable strict_equality
- [x] Enable disallow_incomplete_defs
- [x] Add mypy to CI/CD

### Phase 2: Enhanced Type Hints (In Progress)
- [ ] Add complete type hints to all public functions
- [ ] Add type hints to all decorator functions
- [ ] Enable `disallow_untyped_defs`
- [ ] Enable `disallow_untyped_decorators`

### Phase 3: Full Strict Mode (Future)
- [ ] Enable `disallow_untyped_calls`
- [ ] Remove all `type: ignore` comments
- [ ] Achieve 100% type coverage
- [ ] Enable `--strict` flag

## Troubleshooting

### Common Issues

**Issue**: `error: Incompatible return value type`
```python
# Bad
def get_count() -> int:
    return None  # Error!

# Good
def get_count() -> Optional[int]:
    return None  # OK
```

**Issue**: `error: Need type annotation for variable`
```python
# Bad
result = []  # Error: Need type annotation

# Good
result: list[Lot] = []  # OK
```

**Issue**: `error: Argument has incompatible type`
```python
# Bad
def process(x: int) -> None: ...
process("123")  # Error!

# Good
process(int("123"))  # OK
```

## Resources

- [mypy Documentation](https://mypy.readthedocs.io/)
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [typing Module Documentation](https://docs.python.org/3/library/typing.html)
- [mypy Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

## Questions?

If you encounter type checking issues or have questions:
1. Check this guide first
2. Review [mypy documentation](https://mypy.readthedocs.io/)
3. Open an issue on GitHub with the error message
