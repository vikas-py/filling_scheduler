"""Tests for configuration file loading and validation."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
import yaml

from fillscheduler.config import AppConfig
from fillscheduler.config_loader import (
    CFSConfig,
    ConfigFile,
    SmartPackConfig,
    export_default_config,
    find_config_file,
    get_config_from_env,
    load_config_from_file,
    load_config_with_overrides,
    load_json_config,
    load_yaml_config,
    save_config_to_json,
    save_config_to_yaml,
)


class TestSmartPackConfig:
    """Test SmartPackConfig validation."""

    def test_default_values(self):
        """Test default SmartPackConfig values."""
        config = SmartPackConfig()
        assert config.util_pad_hours == 0.0
        assert config.beam_width == 3
        assert config.score_alpha == 8.0
        assert config.score_beta == 4.0

    def test_custom_values(self):
        """Test custom SmartPackConfig values."""
        config = SmartPackConfig(beam_width=5, score_alpha=10.0)
        assert config.beam_width == 5
        assert config.score_alpha == 10.0

    def test_validation_beam_width(self):
        """Test beam_width validation."""
        with pytest.raises(ValueError):
            SmartPackConfig(beam_width=0)  # Too low
        with pytest.raises(ValueError):
            SmartPackConfig(beam_width=11)  # Too high


class TestCFSConfig:
    """Test CFSConfig validation."""

    def test_default_values(self):
        """Test default CFSConfig values."""
        config = CFSConfig()
        assert config.cluster_order == "by_count"
        assert config.within == "LPT"

    def test_valid_cluster_orders(self):
        """Test valid cluster order values."""
        config1 = CFSConfig(cluster_order="by_count")
        assert config1.cluster_order == "by_count"

        config2 = CFSConfig(cluster_order="by_total_hours")
        assert config2.cluster_order == "by_total_hours"

    def test_invalid_cluster_order(self):
        """Test invalid cluster order."""
        with pytest.raises(ValueError, match="cluster_order must be one of"):
            CFSConfig(cluster_order="invalid")

    def test_invalid_within(self):
        """Test invalid within value."""
        with pytest.raises(ValueError, match="within must be one of"):
            CFSConfig(within="invalid")


class TestConfigFile:
    """Test ConfigFile validation and conversion."""

    def test_default_config(self):
        """Test default ConfigFile values."""
        config = ConfigFile()
        assert config.strategy == "smart-pack"
        assert config.fill_rate_vph == 19920.0
        assert config.clean_hours == 24.0

    def test_custom_config(self):
        """Test custom ConfigFile values."""
        config = ConfigFile(
            strategy="milp", fill_rate_vph=20000.0, strategies={"milp": {"time_limit": 120}}
        )
        assert config.strategy == "milp"
        assert config.fill_rate_vph == 20000.0
        assert config.strategies.milp.time_limit == 120

    def test_strategy_validation(self):
        """Test strategy name validation."""
        valid_strategies = [
            "smart-pack",
            "spt-pack",
            "lpt-pack",
            "cfs-pack",
            "hybrid-pack",
            "milp",
        ]
        for strategy in valid_strategies:
            config = ConfigFile(strategy=strategy)
            assert config.strategy == strategy

        with pytest.raises(ValueError, match="strategy must be one of"):
            ConfigFile(strategy="invalid-strategy")

    def test_start_time_validation(self):
        """Test start_time_str validation."""
        # Valid format
        config = ConfigFile(start_time_str="2025-01-01 08:00")
        assert config.start_time_str == "2025-01-01 08:00"

        # Invalid format
        with pytest.raises(ValueError, match="start_time_str must be in format"):
            ConfigFile(start_time_str="01/01/2025 08:00")

    def test_to_app_config(self):
        """Test conversion to AppConfig."""
        config_file = ConfigFile(
            data_path="test/data.csv",
            strategy="milp",
            fill_rate_vph=20000.0,
            strategies={
                "milp": {"time_limit": 120},
                "smart_pack": {"beam_width": 5},
            },
        )

        app_config = config_file.to_app_config()

        assert isinstance(app_config, AppConfig)
        assert app_config.DATA_PATH == Path("test/data.csv")
        assert app_config.STRATEGY == "milp"
        assert app_config.FILL_RATE_VPH == 20000.0
        assert app_config.MILP_TIME_LIMIT == 120
        assert app_config.BEAM_WIDTH == 5


class TestConfigFileLoading:
    """Test configuration file loading."""

    def test_load_yaml_config(self, tmp_path):
        """Test loading YAML configuration."""
        config_data = {
            "strategy": "milp",
            "fill_rate_vph": 20000.0,
            "strategies": {"milp": {"time_limit": 120}},
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        loaded = load_yaml_config(config_path)
        assert loaded["strategy"] == "milp"
        assert loaded["fill_rate_vph"] == 20000.0

    def test_load_json_config(self, tmp_path):
        """Test loading JSON configuration."""
        config_data = {
            "strategy": "cfs-pack",
            "clean_hours": 20.0,
            "strategies": {"cfs": {"cluster_order": "by_total_hours"}},
        }

        config_path = tmp_path / "config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        loaded = load_json_config(config_path)
        assert loaded["strategy"] == "cfs-pack"
        assert loaded["clean_hours"] == 20.0

    def test_load_nonexistent_file(self, tmp_path):
        """Test loading nonexistent file."""
        config_path = tmp_path / "nonexistent.yaml"

        with pytest.raises(FileNotFoundError):
            load_yaml_config(config_path)

    def test_load_config_from_yaml_file(self, tmp_path):
        """Test load_config_from_file with YAML."""
        config_data = {"strategy": "hybrid-pack", "window_hours": 100.0}

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        config = load_config_from_file(config_path)
        assert config.strategy == "hybrid-pack"
        assert config.window_hours == 100.0

    def test_load_config_from_json_file(self, tmp_path):
        """Test load_config_from_file with JSON."""
        config_data = {"strategy": "lpt-pack", "chg_same_hours": 3.0}

        config_path = tmp_path / "config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        config = load_config_from_file(config_path)
        assert config.strategy == "lpt-pack"
        assert config.chg_same_hours == 3.0

    def test_load_config_unsupported_format(self, tmp_path):
        """Test loading unsupported file format."""
        config_path = tmp_path / "config.txt"
        config_path.write_text("some text")

        with pytest.raises(ValueError, match="Unsupported config file format"):
            load_config_from_file(config_path)

    def test_load_config_no_file_uses_defaults(self):
        """Test that no config file returns defaults."""
        config = load_config_from_file(None)
        assert config.strategy == "smart-pack"
        assert config.fill_rate_vph == 19920.0


class TestConfigSaving:
    """Test configuration file saving."""

    def test_save_config_to_yaml(self, tmp_path):
        """Test saving configuration to YAML."""
        config = ConfigFile(strategy="milp", fill_rate_vph=20000.0)
        output_path = tmp_path / "output.yaml"

        save_config_to_yaml(config, output_path)

        assert output_path.exists()
        with open(output_path) as f:
            data = yaml.safe_load(f)
        assert data["strategy"] == "milp"
        assert data["fill_rate_vph"] == 20000.0

    def test_save_config_to_json(self, tmp_path):
        """Test saving configuration to JSON."""
        config = ConfigFile(strategy="cfs-pack", clean_hours=20.0)
        output_path = tmp_path / "output.json"

        save_config_to_json(config, output_path)

        assert output_path.exists()
        with open(output_path) as f:
            data = json.load(f)
        assert data["strategy"] == "cfs-pack"
        assert data["clean_hours"] == 20.0


class TestConfigExport:
    """Test configuration export functionality."""

    def test_export_default_yaml(self, tmp_path):
        """Test exporting default config as YAML."""
        output_path = tmp_path / "exported.yaml"
        result = export_default_config("yaml", output_path)

        assert result == output_path
        assert output_path.exists()

        with open(output_path) as f:
            data = yaml.safe_load(f)
        assert data["strategy"] == "smart-pack"

    def test_export_default_json(self, tmp_path):
        """Test exporting default config as JSON."""
        output_path = tmp_path / "exported.json"
        result = export_default_config("json", output_path)

        assert result == output_path
        assert output_path.exists()

        with open(output_path) as f:
            data = json.load(f)
        assert data["strategy"] == "smart-pack"

    def test_export_unsupported_format(self, tmp_path):
        """Test exporting with unsupported format."""
        output_path = tmp_path / "exported.txt"

        with pytest.raises(ValueError, match="Unsupported format"):
            export_default_config("txt", output_path)


class TestConfigWithOverrides:
    """Test configuration loading with overrides."""

    def test_load_with_simple_override(self, tmp_path):
        """Test loading config with simple override."""
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"strategy": "smart-pack"}, f)

        config = load_config_with_overrides(config_path, overrides={"strategy": "milp"})

        assert config.STRATEGY == "milp"

    def test_load_with_nested_override(self, tmp_path):
        """Test loading config with nested override."""
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"strategy": "milp"}, f)

        config = load_config_with_overrides(
            config_path, overrides={"strategies.milp.time_limit": 200}
        )

        assert config.MILP_TIME_LIMIT == 200

    def test_load_without_overrides(self, tmp_path):
        """Test loading config without overrides."""
        config_path = tmp_path / "config.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"fill_rate_vph": 25000.0}, f)

        config = load_config_with_overrides(config_path)

        assert config.FILL_RATE_VPH == 25000.0


class TestEnvironmentVariables:
    """Test environment variable support."""

    def test_get_config_from_env_simple(self):
        """Test loading simple env variable."""
        os.environ["FILLSCHEDULER_STRATEGY"] = "milp"
        overrides = get_config_from_env()

        assert overrides["strategy"] == "milp"

        # Cleanup
        del os.environ["FILLSCHEDULER_STRATEGY"]

    def test_get_config_from_env_nested(self):
        """Test loading nested env variable."""
        os.environ["FILLSCHEDULER_STRATEGIES__MILP__TIME_LIMIT"] = "150"
        overrides = get_config_from_env()

        # JSON parsing converts numeric strings to numbers
        assert overrides["strategies.milp.time_limit"] == 150

        # Cleanup
        del os.environ["FILLSCHEDULER_STRATEGIES__MILP__TIME_LIMIT"]

    def test_get_config_from_env_json_value(self):
        """Test loading JSON value from env variable."""
        os.environ["FILLSCHEDULER_INTERACTIVE"] = "true"
        overrides = get_config_from_env()

        assert overrides["interactive"] is True

        # Cleanup
        del os.environ["FILLSCHEDULER_INTERACTIVE"]

    def test_get_config_from_env_no_variables(self):
        """Test with no environment variables set."""
        # Clear any existing FILLSCHEDULER_ vars
        for key in list(os.environ.keys()):
            if key.startswith("FILLSCHEDULER_"):
                del os.environ[key]

        overrides = get_config_from_env()
        assert overrides == {}


class TestConfigFileDiscovery:
    """Test configuration file discovery."""

    def test_find_config_in_cwd(self, tmp_path, monkeypatch):
        """Test finding config in current directory."""
        monkeypatch.chdir(tmp_path)
        config_path = tmp_path / ".fillscheduler.yaml"
        config_path.write_text("strategy: milp")

        found = find_config_file()
        assert found == config_path

    def test_find_config_yml_extension(self, tmp_path, monkeypatch):
        """Test finding .yml extension."""
        monkeypatch.chdir(tmp_path)
        config_path = tmp_path / ".fillscheduler.yml"
        config_path.write_text("strategy: cfs-pack")

        found = find_config_file()
        assert found == config_path

    def test_find_config_none(self, tmp_path, monkeypatch):
        """Test when no config file found."""
        monkeypatch.chdir(tmp_path)
        found = find_config_file()
        assert found is None
