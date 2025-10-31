"""
Pytest configuration and fixtures.
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path
import yaml

from autogbd.core.config_loader import AutoGBDConfig
from autogbd.core.provenance import ProvenanceTracker


@pytest.fixture
def sample_data():
    """Create sample health data for testing."""
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "icd10_code": ["A00", "B20", "I21", "J44", "K92"],
            "age": [45, 67, 23, 89, 34],
            "sex": ["M", "F", "M", "F", "male"],
            "deaths": [1, 2, 1, 3, 1],
            "year": [2020, 2020, 2021, 2021, 2022],
        }
    )


@pytest.fixture
def sample_config_file(tmp_path):
    """Create a sample configuration file."""
    config_dict = {
        "io": {
            "input_file": str(tmp_path / "input.csv"),
            "output_file": str(tmp_path / "output.csv"),
            "input_format": "csv",
            "output_format": "csv",
        },
        "mapping": {
            "enabled": True,
            "source_column": "icd10_code",
            "target_column": "gbd_cause",
            "sources": [],
        },
        "cleaning": {
            "enabled": True,
            "rules": [],
        },
        "quality": {
            "enabled": True,
            "checks": [],
        },
        "reporting": {
            "enabled": True,
            "output_file": "report.md",
        },
    }

    config_file = tmp_path / "config.yaml"
    with open(config_file, "w") as f:
        yaml.dump(config_dict, f)

    return config_file


@pytest.fixture
def sample_mapping_file(tmp_path):
    """Create a sample mapping file."""
    mapping_df = pd.DataFrame(
        {
            "source_code": ["A00", "B20", "I21"],
            "target_code": [
                "Cholera",
                "HIV/AIDS",
                "Ischemic heart disease",
            ],
        }
    )

    mapping_file = tmp_path / "mapping.csv"
    mapping_df.to_csv(mapping_file, index=False)

    return mapping_file


@pytest.fixture
def provenance():
    """Create a provenance tracker for testing."""
    return ProvenanceTracker(run_id="test_run")

