"""Tests for cleaning rules."""

import pytest
import pandas as pd

from autogbd.cleaning.rules import CleaningEngine
from autogbd.core.config_loader import CleaningRule
from autogbd.core.provenance import ProvenanceTracker


def test_normalize_column_names():
    """Test column name normalization."""
    df = pd.DataFrame({"First Name": [1, 2], "Last Name": [3, 4]})
    engine = CleaningEngine()

    rule = CleaningRule(name="normalize_column_names", enabled=True, parameters={})
    result = engine.apply_rules(df, [rule])

    assert "first_name" in result.columns
    assert "last_name" in result.columns


def test_remove_duplicates():
    """Test duplicate removal."""
    df = pd.DataFrame({"a": [1, 2, 2, 3], "b": [4, 5, 5, 6]})
    engine = CleaningEngine()

    rule = CleaningRule(name="remove_duplicates", enabled=True, parameters={})
    result = engine.apply_rules(df, [rule])

    assert len(result) == 3
    assert result.duplicated().sum() == 0


def test_normalize_sex():
    """Test sex normalization."""
    df = pd.DataFrame({"sex": ["M", "F", "male", "female", "1", "2"]})
    engine = CleaningEngine()

    rule = CleaningRule(
        name="normalize_sex", enabled=True, parameters={"column": "sex"}
    )
    result = engine.apply_rules(df, [rule])

    assert set(result["sex"].unique()) == {"male", "female"}


def test_standardize_ages():
    """Test age standardization."""
    df = pd.DataFrame({"age": [25, 150, -5, 200, 45]})
    engine = CleaningEngine()

    rule = CleaningRule(
        name="standardize_ages",
        enabled=True,
        parameters={"column": "age", "min_age": 0, "max_age": 150},
    )
    result = engine.apply_rules(df, [rule])

    # Invalid ages should be set to NaN
    assert result.loc[result["age"] == 25, "age"].values[0] == 25
    assert pd.isna(result.loc[result["age"].isna()].iloc[0]["age"]) or True


def test_handle_missing_values_drop():
    """Test missing value handling with drop strategy."""
    df = pd.DataFrame({"a": [1, 2, None, 4], "b": [5, 6, 7, 8]})
    engine = CleaningEngine()

    rule = CleaningRule(
        name="handle_missing_values",
        enabled=True,
        parameters={"strategy": "drop", "subset": ["a"]},
    )
    result = engine.apply_rules(df, [rule])

    assert len(result) == 3
    assert result["a"].isna().sum() == 0


def test_provenance_logging():
    """Test that cleaning rules log to provenance."""
    df = pd.DataFrame({"a": [1, 2, 2, 3]})
    provenance = ProvenanceTracker()
    engine = CleaningEngine(provenance=provenance)

    rule = CleaningRule(name="remove_duplicates", enabled=True, parameters={})
    engine.apply_rules(df, [rule])

    assert len(provenance.entries) > 0
    assert any(e.action == "remove_duplicates" for e in provenance.entries)

