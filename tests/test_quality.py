"""Tests for quality checks."""

import pytest
import pandas as pd
import numpy as np

from autogbd.quality.checks import QualityChecker
from autogbd.core.config_loader import QualityCheck
from autogbd.core.provenance import ProvenanceTracker


def test_check_age_range():
    """Test age range check."""
    df = pd.DataFrame({"age": [25, 150, -5, 200, 45]})
    checker = QualityChecker()

    check = QualityCheck(
        name="check_age_range",
        enabled=True,
        parameters={"column": "age", "min_age": 0, "max_age": 150},
    )

    results = checker.run_checks(df, [check])

    assert len(results["checks_run"]) == 1
    assert len(results["issues_found"]) > 0


def test_check_sex_values():
    """Test sex values check."""
    df = pd.DataFrame({"sex": ["male", "female", "invalid", "unknown"]})
    checker = QualityChecker()

    check = QualityCheck(
        name="check_sex_values",
        enabled=True,
        parameters={
            "column": "sex",
            "valid_values": ["male", "female", "unknown"],
        },
    )

    results = checker.run_checks(df, [check])

    # Should find invalid sex value
    assert any("invalid" in str(issue.get("message", "")) for issue in results["issues_found"])


def test_check_missing_values():
    """Test missing values check."""
    df = pd.DataFrame(
        {
            "a": [1, 2, None, 4, 5],
            "b": [None, None, None, None, None],
        }
    )
    checker = QualityChecker()

    check = QualityCheck(
        name="check_missing_values",
        enabled=True,
        parameters={"columns": ["b"], "threshold": 0.5},  # 50% threshold
    )

    results = checker.run_checks(df, [check])

    # Column b has 100% missing, should be flagged
    assert len(results["issues_found"]) > 0


def test_check_unmapped_codes():
    """Test unmapped codes check."""
    df = pd.DataFrame(
        {
            "icd10_code": ["A00", "B20", "I21"],
            "gbd_cause": ["Cholera", None, "Ischemic heart disease"],
        }
    )
    checker = QualityChecker()

    check = QualityCheck(
        name="check_unmapped_codes",
        enabled=True,
        parameters={
            "source_column": "icd10_code",
            "target_column": "gbd_cause",
            "threshold": 0.1,  # 10% threshold
        },
    )

    results = checker.run_checks(df, [check])

    # 33% unmapped should exceed 10% threshold
    assert len(results["issues_found"]) > 0


def test_quality_score_calculation():
    """Test quality score calculation."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    checker = QualityChecker()

    results = checker.run_checks(df, [])

    assert "quality_score" in results
    assert 0 <= results["quality_score"] <= 100


def test_provenance_logging():
    """Test that quality checks log to provenance."""
    df = pd.DataFrame({"age": [25, 150, -5]})
    provenance = ProvenanceTracker()
    checker = QualityChecker(provenance=provenance)

    check = QualityCheck(
        name="check_age_range",
        enabled=True,
        parameters={"column": "age", "min_age": 0, "max_age": 150},
    )

    checker.run_checks(df, [check])

    assert len(provenance.entries) > 0
    assert any(e.step == "quality" for e in provenance.entries)

