"""Configuration file loader with YAML/JSON support and validation.

This module provides configuration loading from multiple sources:
- YAML files (.yaml, .yml)
- JSON files (.json)
- Environment variables
- Default values

Configuration files are searched in the following order:
1. Path specified via --config CLI option
2. .fillscheduler.yaml in current directory
3. ~/.config/fillscheduler/config.yaml
4. Default configuration values
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

from .config import AppConfig


class SmartPackConfig(BaseModel):
    """Configuration for smart-pack strategy."""

    util_pad_hours: float = Field(
        default=0.0, description="Tiny slack to avoid float rounding", ge=0
    )
    beam_width: int = Field(default=3, description="Small look-ahead width", ge=1, le=10)
    score_alpha: float = Field(
        default=8.0, description="Different-type changeover penalty (hours)", ge=0
    )
    score_beta: float = Field(default=4.0, description="Same-type changeover penalty (hours)", ge=0)
    slack_waste_weight: float = Field(
        default=3.0, description="Penalty per hour of unusable slack", ge=0
    )
    streak_bonus: float = Field(default=1.0, description="Bonus for staying on same type", ge=0)
    dynamic_switch_mult_min: float = Field(
        default=1.0, description="Switch multiplier at 0% window used", ge=0
    )
    dynamic_switch_mult_max: float = Field(
        default=1.5, description="Switch multiplier at 100% window used", ge=0
    )


class CFSConfig(BaseModel):
    """Configuration for CFS (Cluster First Schedule) strategy."""

    cluster_order: str = Field(
        default="by_count", description="Clustering order: 'by_count' or 'by_total_hours'"
    )
    within: str = Field(default="LPT", description="Within-cluster sorting: 'LPT' or 'SPT'")

    @field_validator("cluster_order")
    @classmethod
    def validate_cluster_order(cls, v: str) -> str:
        """Validate cluster order."""
        allowed = ["by_count", "by_total_hours"]
        if v not in allowed:
            raise ValueError(f"cluster_order must be one of {allowed}, got '{v}'")
        return v

    @field_validator("within")
    @classmethod
    def validate_within(cls, v: str) -> str:
        """Validate within-cluster sorting."""
        allowed = ["LPT", "SPT"]
        if v not in allowed:
            raise ValueError(f"within must be one of {allowed}, got '{v}'")
        return v


class HybridConfig(BaseModel):
    """Configuration for hybrid strategy."""

    same_type_bonus: float = Field(default=2.0, description="Extra push to keep type streaks", ge=0)
    spt_weight: float = Field(default=0.5, description="SPT bias when staying on same type", ge=0)
    switch_penalty_mult: float = Field(default=1.1, description="Switch penalty multiplier", ge=1.0)


class MILPConfig(BaseModel):
    """Configuration for MILP (Mixed Integer Linear Programming) strategy."""

    max_lots: int = Field(default=30, description="Hard cap to keep model tractable", ge=1)
    max_blocks: int = Field(default=30, description="Maximum cleaning blocks", ge=1)
    time_limit: int = Field(default=60, description="Solver time limit (seconds)", ge=1)


class StrategyConfigs(BaseModel):
    """Strategy-specific configurations."""

    smart_pack: SmartPackConfig = Field(default_factory=SmartPackConfig)
    cfs: CFSConfig = Field(default_factory=CFSConfig)
    hybrid: HybridConfig = Field(default_factory=HybridConfig)
    milp: MILPConfig = Field(default_factory=MILPConfig)


class ConfigFile(BaseModel):
    """Main configuration file schema with validation."""

    # File & run options
    data_path: str = Field(default="examples/lots.csv", description="Path to input CSV file")
    output_dir: str = Field(default="output", description="Output directory for results")
    start_time_str: str = Field(
        default="2025-01-01 08:00", description="Start time (YYYY-MM-DD HH:MM)"
    )
    strategy: str = Field(default="smart-pack", description="Scheduling strategy to use")
    interactive: bool = Field(default=False, description="Enable interactive mode")

    # Process constants
    fill_rate_vph: float = Field(default=19920.0, description="Fill rate (vials/hour)", gt=0)
    clean_hours: float = Field(default=24.0, description="Cleaning duration (hours)", gt=0)
    window_hours: float = Field(default=120.0, description="Time window (hours)", gt=0)
    chg_same_hours: float = Field(default=4.0, description="Same-type changeover (hours)", ge=0)
    chg_diff_hours: float = Field(
        default=8.0, description="Different-type changeover (hours)", ge=0
    )

    # Strategy configurations
    strategies: StrategyConfigs = Field(default_factory=StrategyConfigs)

    # Reporting
    html_report: bool = Field(default=True, description="Generate HTML report")
    html_filename: str = Field(default="report.html", description="HTML report filename")
    datetime_fmt: str = Field(default="%Y-%m-%d %H:%M", description="Datetime format string")

    @field_validator("strategy")
    @classmethod
    def validate_strategy(cls, v: str) -> str:
        """Validate strategy name."""
        allowed = ["smart-pack", "spt-pack", "lpt-pack", "cfs-pack", "hybrid-pack", "milp"]
        if v not in allowed:
            raise ValueError(f"strategy must be one of {allowed}, got '{v}'")
        return v

    @field_validator("start_time_str")
    @classmethod
    def validate_start_time(cls, v: str) -> str:
        """Validate start time format."""
        from datetime import datetime

        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M")
        except ValueError as e:
            raise ValueError(
                f"start_time_str must be in format 'YYYY-MM-DD HH:MM', got '{v}'"
            ) from e
        return v

    def to_app_config(self) -> AppConfig:
        """Convert to legacy AppConfig object."""
        cfg = AppConfig()

        # File & run options
        cfg.DATA_PATH = Path(self.data_path)
        cfg.OUTPUT_DIR = Path(self.output_dir)
        cfg.START_TIME_STR = self.start_time_str
        cfg.STRATEGY = self.strategy
        cfg.INTERACTIVE = self.interactive

        # Process constants
        cfg.FILL_RATE_VPH = self.fill_rate_vph
        cfg.CLEAN_HOURS = self.clean_hours
        cfg.WINDOW_HOURS = self.window_hours
        cfg.CHG_SAME_HOURS = self.chg_same_hours
        cfg.CHG_DIFF_HOURS = self.chg_diff_hours

        # Smart-pack strategy
        cfg.UTIL_PAD_HOURS = self.strategies.smart_pack.util_pad_hours
        cfg.BEAM_WIDTH = self.strategies.smart_pack.beam_width
        cfg.SCORE_ALPHA = self.strategies.smart_pack.score_alpha
        cfg.SCORE_BETA = self.strategies.smart_pack.score_beta
        cfg.SLACK_WASTE_WEIGHT = self.strategies.smart_pack.slack_waste_weight
        cfg.STREAK_BONUS = self.strategies.smart_pack.streak_bonus
        cfg.DYNAMIC_SWITCH_MULT_MIN = self.strategies.smart_pack.dynamic_switch_mult_min
        cfg.DYNAMIC_SWITCH_MULT_MAX = self.strategies.smart_pack.dynamic_switch_mult_max

        # CFS strategy
        cfg.CFS_CLUSTER_ORDER = self.strategies.cfs.cluster_order
        cfg.CFS_WITHIN = self.strategies.cfs.within

        # Hybrid strategy
        cfg.HYBRID_SAME_TYPE_BONUS = self.strategies.hybrid.same_type_bonus
        cfg.HYBRID_SPT_WEIGHT = self.strategies.hybrid.spt_weight
        cfg.HYBRID_SWITCH_PENALTY_MULT = self.strategies.hybrid.switch_penalty_mult

        # MILP strategy
        cfg.MILP_MAX_LOTS = self.strategies.milp.max_lots
        cfg.MILP_MAX_BLOCKS = self.strategies.milp.max_blocks
        cfg.MILP_TIME_LIMIT = self.strategies.milp.time_limit

        # Reporting
        cfg.HTML_REPORT = self.html_report
        cfg.HTML_FILENAME = self.html_filename
        cfg.DATETIME_FMT = self.datetime_fmt

        return cfg


def find_config_file() -> Path | None:
    """Find configuration file in standard locations.

    Search order:
    1. .fillscheduler.yaml in current directory
    2. .fillscheduler.yml in current directory
    3. ~/.config/fillscheduler/config.yaml
    4. ~/.config/fillscheduler/config.yml

    Returns:
        Path to configuration file if found, None otherwise.
    """
    search_paths = [
        Path.cwd() / ".fillscheduler.yaml",
        Path.cwd() / ".fillscheduler.yml",
        Path.home() / ".config" / "fillscheduler" / "config.yaml",
        Path.home() / ".config" / "fillscheduler" / "config.yml",
    ]

    for path in search_paths:
        if path.exists():
            return path

    return None


def load_yaml_config(path: Path) -> dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        path: Path to YAML file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ValueError(f"Configuration must be a dictionary, got {type(data)}")

    return data


def load_json_config(path: Path) -> dict[str, Any]:
    """Load configuration from JSON file.

    Args:
        path: Path to JSON file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is malformed
    """
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError(f"Configuration must be a dictionary, got {type(data)}")

    return data


def load_config_from_file(path: Path | None = None) -> ConfigFile:
    """Load and validate configuration from file.

    Args:
        path: Optional path to configuration file. If not provided,
              searches standard locations.

    Returns:
        Validated ConfigFile object

    Raises:
        FileNotFoundError: If specified file doesn't exist
        ValueError: If configuration is invalid
    """
    if path is None:
        path = find_config_file()

    # If no config file found, use defaults
    if path is None:
        return ConfigFile()

    # Load based on extension
    if path.suffix in [".yaml", ".yml"]:
        data = load_yaml_config(path)
    elif path.suffix == ".json":
        data = load_json_config(path)
    else:
        raise ValueError(
            f"Unsupported config file format: {path.suffix}. Use .yaml, .yml, or .json"
        )

    # Validate and return
    return ConfigFile(**data)


def load_config_with_overrides(
    config_path: Path | None = None, overrides: dict[str, Any] | None = None
) -> AppConfig:
    """Load configuration with optional overrides.

    Args:
        config_path: Optional path to configuration file
        overrides: Optional dictionary of configuration overrides

    Returns:
        AppConfig object ready to use

    Example:
        >>> config = load_config_with_overrides(
        ...     config_path=Path("my_config.yaml"),
        ...     overrides={"strategy": "milp", "strategies.milp.time_limit": 120}
        ... )
    """
    # Load base configuration
    config_file = load_config_from_file(config_path)

    # Apply overrides if provided
    if overrides:
        # Convert to dict, apply overrides, recreate
        data = config_file.model_dump()
        for key, value in overrides.items():
            # Support nested keys like "strategies.milp.time_limit"
            keys = key.split(".")
            target = data
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]
            target[keys[-1]] = value

        config_file = ConfigFile(**data)

    # Convert to AppConfig
    return config_file.to_app_config()


def save_config_to_yaml(config: ConfigFile, path: Path) -> None:
    """Save configuration to YAML file.

    Args:
        config: ConfigFile object to save
        path: Path where to save the YAML file
    """
    data = config.model_dump()

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def save_config_to_json(config: ConfigFile, path: Path) -> None:
    """Save configuration to JSON file.

    Args:
        config: ConfigFile object to save
        path: Path where to save the JSON file
    """
    data = config.model_dump()

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def export_default_config(format: str = "yaml", path: Path | None = None) -> Path:
    """Export default configuration to file.

    Args:
        format: Output format ('yaml' or 'json')
        path: Optional output path. If not provided, uses default name.

    Returns:
        Path to created file

    Example:
        >>> export_default_config("yaml", Path("my_config.yaml"))
        Path('my_config.yaml')
    """
    config = ConfigFile()

    if path is None:
        if format == "yaml":
            path = Path(".fillscheduler.yaml")
        elif format == "json":
            path = Path(".fillscheduler.json")
        else:
            raise ValueError(f"Unsupported format: {format}. Use 'yaml' or 'json'")

    if format == "yaml":
        save_config_to_yaml(config, path)
    elif format == "json":
        save_config_to_json(config, path)
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'yaml' or 'json'")

    return path


# Environment variable support
def get_config_from_env() -> dict[str, Any]:
    """Load configuration overrides from environment variables.

    Environment variables should be prefixed with FILLSCHEDULER_
    and use double underscores for nested values.

    Examples:
        FILLSCHEDULER_STRATEGY=milp
        FILLSCHEDULER_STRATEGIES__MILP__TIME_LIMIT=120

    Returns:
        Dictionary of configuration overrides
    """
    overrides = {}
    prefix = "FILLSCHEDULER_"

    for key, value in os.environ.items():
        if key.startswith(prefix):
            # Remove prefix and convert to lowercase
            config_key = key[len(prefix) :].lower()

            # Convert double underscores to dots for nested keys
            config_key = config_key.replace("__", ".")

            # Try to parse as JSON for complex values
            try:
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                # Keep as string if not valid JSON
                parsed_value = value

            overrides[config_key] = parsed_value

    return overrides
