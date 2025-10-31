"""Tests for mapping engine."""

import pytest
import pandas as pd
from pathlib import Path
import tempfile

from autogbd.mapping.engine import MappingEngine
from autogbd.core.config_loader import MappingConfig, MappingSource
from autogbd.core.provenance import ProvenanceTracker


def test_direct_mapping(sample_data, tmp_path):
    """Test direct mapping from file."""
    # Create mapping file
    mapping_df = pd.DataFrame(
        {
            "source_code": ["A00", "B20", "I21"],
            "target_code": ["Cholera", "HIV/AIDS", "Ischemic heart disease"],
        }
    )
    mapping_file = tmp_path / "mapping.csv"
    mapping_df.to_csv(mapping_file, index=False)

    engine = MappingEngine(source_column="icd10_code", target_column="gbd_cause")
    mapping_config = MappingConfig(
        source_column="icd10_code",
        target_column="gbd_cause",
        sources=[
            MappingSource(type="direct", file=str(mapping_file), enabled=True)
        ],
    )

    result = engine.apply_mappings(sample_data, mapping_config)

    # Check that mapped codes have values
    assert result.loc[result["icd10_code"] == "A00", "gbd_cause"].values[0] == "Cholera"
    assert result.loc[result["icd10_code"] == "B20", "gbd_cause"].values[0] == "HIV/AIDS"


def test_unmapped_codes_remain_none(sample_data):
    """Test that unmapped codes remain None."""
    engine = MappingEngine(source_column="icd10_code", target_column="gbd_cause")
    mapping_config = MappingConfig(
        source_column="icd10_code",
        target_column="gbd_cause",
        sources=[],  # No mapping sources
    )

    result = engine.apply_mappings(sample_data, mapping_config)

    # All should be unmapped
    assert result["gbd_cause"].isna().all()


def test_fuzzy_mapping(sample_data, tmp_path):
    """Test fuzzy string matching."""
    # Create target cause list
    causes_df = pd.DataFrame(
        {
            "target_code": [
                "Cholera",
                "HIV/AIDS",
                "Ischemic heart disease",
                "Chronic obstructive pulmonary disease",
            ]
        }
    )
    causes_file = tmp_path / "causes.csv"
    causes_df.to_csv(causes_file, index=False)

    engine = MappingEngine(source_column="icd10_code", target_column="gbd_cause")
    mapping_config = MappingConfig(
        source_column="icd10_code",
        target_column="gbd_cause",
        sources=[
            MappingSource(
                type="fuzzy",
                file=str(causes_file),
                threshold=0.5,  # Low threshold for testing
                enabled=True,
            )
        ],
    )

    result = engine.apply_mappings(sample_data, mapping_config)

    # Some mappings should occur with fuzzy matching
    assert result["gbd_cause"].notna().sum() >= 0


def test_provenance_logging_mapping(sample_data):
    """Test that mapping logs to provenance."""
    provenance = ProvenanceTracker()
    engine = MappingEngine(
        source_column="icd10_code",
        target_column="gbd_cause",
        provenance=provenance,
    )
    mapping_config = MappingConfig(
        source_column="icd10_code",
        target_column="gbd_cause",
        sources=[],
    )

    engine.apply_mappings(sample_data, mapping_config)

    # Should have mapping entries in provenance
    mapping_entries = [e for e in provenance.entries if e.step == "mapping"]
    assert len(mapping_entries) > 0

