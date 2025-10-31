"""Tests for the main pipeline."""

import pytest
import pandas as pd
import yaml
from pathlib import Path
import tempfile

from autogbd.core.pipeline import AutoGBDPipeline
from autogbd.core.config_loader import ConfigLoader
from autogbd.core.provenance import ProvenanceTracker


def test_pipeline_initialization(sample_config_file):
    """Test pipeline initialization."""
    config = ConfigLoader.load(sample_config_file)
    pipeline = AutoGBDPipeline(config)

    assert pipeline.config == config
    assert pipeline.data is None
    assert pipeline.provenance is not None


def test_pipeline_full_run(tmp_path):
    """Test a complete pipeline run."""
    # Create input data
    input_file = tmp_path / "input.csv"
    df = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "icd10_code": ["A00", "B20", "I21"],
            "age": [45, 67, 23],
            "sex": ["M", "F", "M"],
            "deaths": [1, 2, 1],
        }
    )
    df.to_csv(input_file, index=False)

    # Create config
    config_dict = {
        "io": {
            "input_file": str(input_file),
            "output_file": str(tmp_path / "output.csv"),
            "input_format": "csv",
            "output_format": "csv",
        },
        "cleaning": {
            "enabled": True,
            "rules": [
                {
                    "name": "remove_duplicates",
                    "enabled": True,
                    "parameters": {},
                }
            ],
        },
        "mapping": {
            "enabled": True,
            "source_column": "icd10_code",
            "target_column": "gbd_cause",
            "sources": [],
        },
        "quality": {
            "enabled": True,
            "checks": [],
        },
        "reporting": {
            "enabled": False,  # Disable reporting for faster tests
        },
    }

    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_dict, f)

    config = ConfigLoader.load(config_file)
    pipeline = AutoGBDPipeline(config)

    result = pipeline.run()

    assert len(result) > 0
    assert (tmp_path / "output.csv").exists()


def test_pipeline_provenance_logging(tmp_path):
    """Test that pipeline logs to provenance."""
    # Create minimal input
    input_file = tmp_path / "input.csv"
    df = pd.DataFrame({"a": [1, 2, 3]})
    df.to_csv(input_file, index=False)

    # Create minimal config
    config_dict = {
        "io": {
            "input_file": str(input_file),
            "output_file": str(tmp_path / "output.csv"),
            "input_format": "csv",
        },
        "mapping": {
            "source_column": "icd10_code",
            "sources": [],
        },
        "cleaning": {"enabled": False},
        "quality": {"enabled": False},
        "reporting": {"enabled": False},
    }

    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_dict, f)

    config = ConfigLoader.load(config_file)
    provenance = ProvenanceTracker()
    pipeline = AutoGBDPipeline(config, provenance)

    pipeline.run()

    # Should have pipeline entries
    assert len(provenance.entries) > 0
    assert any(e.step == "pipeline" for e in provenance.entries)

