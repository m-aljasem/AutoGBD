"""Tests for configuration loader."""

import pytest
import yaml
from pathlib import Path
import tempfile

from autogbd.core.config_loader import ConfigLoader, AutoGBDConfig


def test_load_valid_config(sample_config_file):
    """Test loading a valid configuration file."""
    config = ConfigLoader.load(sample_config_file)
    assert isinstance(config, AutoGBDConfig)
    assert config.io.input_format == "csv"


def test_load_invalid_config(tmp_path):
    """Test loading an invalid configuration file."""
    invalid_config = tmp_path / "invalid.yaml"
    with open(invalid_config, "w") as f:
        yaml.dump({"invalid": "config"}, f)

    with pytest.raises(ValueError):
        ConfigLoader.load(invalid_config)


def test_load_nonexistent_config():
    """Test loading a non-existent configuration file."""
    with pytest.raises(FileNotFoundError):
        ConfigLoader.load("nonexistent.yaml")


def test_config_validation_invalid_format(sample_config_file):
    """Test validation of invalid input format."""
    config_dict = {
        "io": {
            "input_file": "test.csv",
            "output_file": "output.csv",
            "input_format": "invalid_format",
            "output_format": "csv",
        },
        "mapping": {
            "source_column": "code",
            "sources": [],
        },
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_dict, f)
        config_path = Path(f.name)

    try:
        with pytest.raises(ValueError):
            ConfigLoader.load(config_path)
    finally:
        config_path.unlink()


def test_config_defaults():
    """Test that default values are correctly applied."""
    config_dict = {
        "io": {
            "input_file": "test.csv",
            "output_file": "output.csv",
            "input_format": "csv",
        },
        "mapping": {
            "source_column": "code",
            "sources": [],
        },
    }

    config = AutoGBDConfig(**config_dict)

    assert config.io.output_format == "csv"  # Default
    assert config.cleaning.enabled is True  # Default
    assert config.reporting.enabled is True  # Default

