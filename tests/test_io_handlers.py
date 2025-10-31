"""Tests for I/O handlers."""

import pytest
import pandas as pd
from pathlib import Path
import tempfile

from autogbd.io.handlers import DataHandler


def test_load_csv(tmp_path):
    """Test loading CSV file."""
    # Create test CSV
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    csv_file = tmp_path / "test.csv"
    df.to_csv(csv_file, index=False)

    handler = DataHandler()
    loaded_df = handler.load(str(csv_file), "csv")

    pd.testing.assert_frame_equal(loaded_df, df)


def test_save_csv(tmp_path):
    """Test saving CSV file."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    output_file = tmp_path / "output.csv"

    handler = DataHandler()
    handler.save(df, str(output_file), "csv")

    assert output_file.exists()
    loaded_df = pd.read_csv(output_file)
    pd.testing.assert_frame_equal(loaded_df, df)


def test_load_excel(tmp_path):
    """Test loading Excel file."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    excel_file = tmp_path / "test.xlsx"
    df.to_excel(excel_file, index=False)

    handler = DataHandler()
    loaded_df = handler.load(str(excel_file), "excel")

    pd.testing.assert_frame_equal(loaded_df, df)


def test_load_parquet(tmp_path):
    """Test loading Parquet file."""
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
    parquet_file = tmp_path / "test.parquet"
    df.to_parquet(parquet_file)

    handler = DataHandler()
    loaded_df = handler.load(str(parquet_file), "parquet")

    pd.testing.assert_frame_equal(loaded_df, df)


def test_load_nonexistent_file():
    """Test loading non-existent file."""
    handler = DataHandler()

    with pytest.raises(FileNotFoundError):
        handler.load("nonexistent.csv", "csv")


def test_load_unsupported_format(tmp_path):
    """Test loading unsupported format."""
    handler = DataHandler()

    with pytest.raises(ValueError):
        handler.load("test.xyz", "xyz")


def test_register_custom_loader(tmp_path):
    """Test registering custom loader."""
    handler = DataHandler()

    def custom_loader(file_path, **kwargs):
        return pd.DataFrame({"custom": [1, 2, 3]})

    handler.register_loader("custom", custom_loader)

    # Create a dummy file
    test_file = tmp_path / "test.custom"
    test_file.touch()

    df = handler.load(str(test_file), "custom")
    assert len(df) == 3
    assert "custom" in df.columns

