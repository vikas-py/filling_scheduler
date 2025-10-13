"""
Configuration service for validating and managing configuration templates.

Provides functions for:
- Configuration validation
- Default configuration management
- Configuration merging and defaults
"""

import json
from typing import Any

from sqlalchemy.orm import Session

from fillscheduler.api.models.database import ConfigTemplate


def validate_config(config_data: dict[str, Any]) -> dict[str, Any]:
    """
    Validate configuration parameters.

    Args:
        config_data: Dictionary containing configuration parameters

    Returns:
        Dictionary with keys:
        - valid (bool): Whether configuration is valid
        - errors (List[str]): List of error messages
        - warnings (List[str]): List of warning messages
    """
    errors = []
    warnings = []

    # Validate max_clean_hours
    if "max_clean_hours" in config_data:
        max_clean = config_data["max_clean_hours"]
        if not isinstance(max_clean, (int, float)):
            errors.append("max_clean_hours must be a number")
        elif max_clean < 0:
            errors.append("max_clean_hours must be positive")
        elif max_clean > 24:
            warnings.append("max_clean_hours > 24 is unusual for a single shift")

    # Validate changeover_matrix
    if "changeover_matrix" in config_data:
        matrix = config_data["changeover_matrix"]
        if not isinstance(matrix, dict):
            errors.append("changeover_matrix must be a dictionary")
        else:
            # Validate matrix structure
            for from_type, to_dict in matrix.items():
                if not isinstance(to_dict, dict):
                    errors.append(f"changeover_matrix[{from_type}] must be a dictionary")
                else:
                    for to_type, hours in to_dict.items():
                        if not isinstance(hours, (int, float)):
                            errors.append(
                                f"changeover_matrix[{from_type}][{to_type}] must be a number"
                            )
                        elif hours < 0:
                            errors.append(
                                f"changeover_matrix[{from_type}][{to_type}] must be non-negative"
                            )

    # Validate default_changeover_hours
    if "default_changeover_hours" in config_data:
        default_changeover = config_data["default_changeover_hours"]
        if not isinstance(default_changeover, (int, float)):
            errors.append("default_changeover_hours must be a number")
        elif default_changeover < 0:
            errors.append("default_changeover_hours must be non-negative")

    # Validate min_lot_spacing_hours
    if "min_lot_spacing_hours" in config_data:
        spacing = config_data["min_lot_spacing_hours"]
        if not isinstance(spacing, (int, float)):
            errors.append("min_lot_spacing_hours must be a number")
        elif spacing < 0:
            errors.append("min_lot_spacing_hours must be non-negative")

    # Validate window_penalty_weight
    if "window_penalty_weight" in config_data:
        penalty = config_data["window_penalty_weight"]
        if not isinstance(penalty, (int, float)):
            errors.append("window_penalty_weight must be a number")
        elif penalty < 0:
            errors.append("window_penalty_weight must be non-negative")

    # Validate priority_levels
    if "priority_levels" in config_data:
        priorities = config_data["priority_levels"]
        if not isinstance(priorities, dict):
            errors.append("priority_levels must be a dictionary")
        else:
            for level, weight in priorities.items():
                if not isinstance(weight, (int, float)):
                    errors.append(f"priority_levels[{level}] must be a number")

    # Validate milp_time_limit
    if "milp_time_limit" in config_data:
        time_limit = config_data["milp_time_limit"]
        if not isinstance(time_limit, (int, float)):
            errors.append("milp_time_limit must be a number")
        elif time_limit <= 0:
            errors.append("milp_time_limit must be positive")
        elif time_limit > 3600:
            warnings.append("milp_time_limit > 3600 seconds (1 hour) may be too long")

    # Validate allowed_strategies
    if "allowed_strategies" in config_data:
        strategies = config_data["allowed_strategies"]
        if not isinstance(strategies, list):
            errors.append("allowed_strategies must be a list")
        else:
            valid_strategies = [
                "smart-pack",
                "spt-pack",
                "lpt-pack",
                "cfs-pack",
                "hybrid-pack",
                "milp-opt",
            ]
            for strategy in strategies:
                if strategy not in valid_strategies:
                    errors.append(
                        f"Invalid strategy '{strategy}'. "
                        f"Must be one of: {', '.join(valid_strategies)}"
                    )

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def get_default_config() -> dict[str, Any]:
    """
    Get the default configuration values.

    Returns:
        Dictionary with default configuration parameters
    """
    return {
        "max_clean_hours": 4.0,
        "default_changeover_hours": 2.0,
        "min_lot_spacing_hours": 0.5,
        "window_penalty_weight": 1.0,
        "priority_levels": {
            "high": 3.0,
            "medium": 2.0,
            "low": 1.0,
        },
        "changeover_matrix": {},  # Empty by default, user can customize
        "milp_time_limit": 300,  # 5 minutes
        "allowed_strategies": [
            "smart-pack",
            "spt-pack",
            "lpt-pack",
            "cfs-pack",
            "hybrid-pack",
            "milp-opt",
        ],
    }


def apply_config_defaults(config_data: dict[str, Any]) -> dict[str, Any]:
    """
    Apply default values to configuration, filling in missing keys.

    Args:
        config_data: User-provided configuration (may be partial)

    Returns:
        Complete configuration with defaults applied
    """
    defaults = get_default_config()

    # Start with defaults
    complete_config = defaults.copy()

    # Override with user-provided values
    for key, value in config_data.items():
        if key in defaults:
            # For dictionaries, merge instead of replacing
            if isinstance(defaults[key], dict) and isinstance(value, dict):
                complete_config[key] = {**defaults[key], **value}
            else:
                complete_config[key] = value
        else:
            # Keep unknown keys (forward compatibility)
            complete_config[key] = value

    return complete_config


def get_user_default_config(db: Session, user_id: int) -> ConfigTemplate | None:
    """
    Get the user's default configuration template.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        ConfigTemplate if user has a default, None otherwise
    """
    return (
        db.query(ConfigTemplate)
        .filter(
            ConfigTemplate.user_id == user_id,
            ConfigTemplate.is_default.is_(True),
        )
        .first()
    )


def set_user_default_config(db: Session, user_id: int, template_id: int) -> ConfigTemplate:
    """
    Set a configuration template as the user's default.

    Unsets any existing default and sets the specified template as default.

    Args:
        db: Database session
        user_id: User ID
        template_id: Template ID to set as default

    Returns:
        The updated ConfigTemplate

    Raises:
        ValueError: If template doesn't exist or doesn't belong to user
    """
    # Get the template
    template = (
        db.query(ConfigTemplate)
        .filter(
            ConfigTemplate.id == template_id,
            ConfigTemplate.user_id == user_id,
        )
        .first()
    )

    if not template:
        raise ValueError("Template not found or access denied")

    # Unset any existing default
    db.query(ConfigTemplate).filter(
        ConfigTemplate.user_id == user_id,
        ConfigTemplate.is_default.is_(True),
    ).update({"is_default": False})

    # Set new default
    template.is_default = True
    db.commit()
    db.refresh(template)

    return template


def unset_user_default_config(db: Session, user_id: int) -> None:
    """
    Unset the user's default configuration template.

    Args:
        db: Database session
        user_id: User ID
    """
    db.query(ConfigTemplate).filter(
        ConfigTemplate.user_id == user_id,
        ConfigTemplate.is_default.is_(True),
    ).update({"is_default": False})
    db.commit()


def export_config_to_dict(template: ConfigTemplate) -> dict[str, Any]:
    """
    Export a configuration template to a dictionary format.

    Args:
        template: ConfigTemplate instance

    Returns:
        Dictionary containing template data suitable for export
    """
    config = json.loads(template.config_json) if template.config_json else {}

    return {
        "name": template.name,
        "description": template.description,
        "config": config,
        "created_at": template.created_at.isoformat(),
        "updated_at": template.updated_at.isoformat(),
    }


def import_config_from_dict(
    db: Session, user_id: int, import_data: dict[str, Any]
) -> ConfigTemplate:
    """
    Import a configuration template from a dictionary.

    Args:
        db: Database session
        user_id: User ID (owner of the imported template)
        import_data: Dictionary with name, description, config keys

    Returns:
        Created ConfigTemplate

    Raises:
        ValueError: If import data is invalid
    """
    if "name" not in import_data:
        raise ValueError("Import data must include 'name'")

    if "config" not in import_data:
        raise ValueError("Import data must include 'config'")

    # Validate configuration
    validation = validate_config(import_data["config"])
    if not validation["valid"]:
        raise ValueError(f"Invalid configuration: {', '.join(validation['errors'])}")

    # Create template
    template = ConfigTemplate(
        user_id=user_id,
        name=import_data["name"],
        description=import_data.get("description"),
        config_json=json.dumps(import_data["config"]),
        is_public=False,  # Imported templates are private by default
        is_default=False,
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return template
