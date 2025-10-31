"""
Data input/output handlers for various formats.

This module provides extensible handlers for loading and saving
data in CSV, Excel, and Parquet formats, with plugin support.
"""

from pathlib import Path
from typing import Optional, Dict, Any, Callable
import pandas as pd


class DataHandler:
    """
    Handler for loading and saving data in various formats.

    Supports CSV, Excel, and Parquet formats, with extensibility
    for additional formats via plugins.
    """

    def __init__(self):
        """Initialize the data handler."""
        self._loaders: Dict[str, Callable] = {
            "csv": self._load_csv,
            "excel": self._load_excel,
            "xlsx": self._load_excel,
            "parquet": self._load_parquet,
        }
        self._savers: Dict[str, Callable] = {
            "csv": self._save_csv,
            "excel": self._save_excel,
            "xlsx": self._save_excel,
            "parquet": self._save_parquet,
        }

    def load(
        self,
        file_path: str,
        file_format: str,
        sheet_name: Optional[str] = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        Load data from a file.

        Parameters
        ----------
        file_path : str
            Path to the input file.
        file_format : str
            Format of the file (csv, excel, parquet).
        sheet_name : str, optional
            Sheet name for Excel files.
        **kwargs
            Additional arguments passed to the loader function.

        Returns
        -------
        pd.DataFrame
            Loaded data.

        Raises
        ------
        ValueError
            If the file format is not supported.
        FileNotFoundError
            If the file doesn't exist.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        file_format = file_format.lower()
        if file_format not in self._loaders:
            raise ValueError(
                f"Unsupported file format: {file_format}. "
                f"Supported formats: {list(self._loaders.keys())}"
            )

        loader = self._loaders[file_format]
        if file_format in {"excel", "xlsx"} and sheet_name:
            return loader(file_path, sheet_name=sheet_name, **kwargs)
        return loader(file_path, **kwargs)

    def save(
        self,
        data: pd.DataFrame,
        file_path: str,
        file_format: str,
        **kwargs,
    ) -> None:
        """
        Save data to a file.

        Parameters
        ----------
        data : pd.DataFrame
            Data to save.
        file_path : str
            Path where the file should be saved.
        file_format : str
            Format of the file (csv, excel, parquet).
        **kwargs
            Additional arguments passed to the saver function.
        """
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        file_format = file_format.lower()
        if file_format not in self._savers:
            raise ValueError(
                f"Unsupported file format: {file_format}. "
                f"Supported formats: {list(self._savers.keys())}"
            )

        saver = self._savers[file_format]
        saver(data, file_path, **kwargs)

    def _load_csv(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """Load CSV file."""
        return pd.read_csv(file_path, **kwargs)

    def _load_excel(self, file_path: Path, sheet_name: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """Load Excel file."""
        return pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)

    def _load_parquet(self, file_path: Path, **kwargs) -> pd.DataFrame:
        """Load Parquet file."""
        return pd.read_parquet(file_path, **kwargs)

    def _save_csv(self, data: pd.DataFrame, file_path: Path, **kwargs) -> None:
        """Save CSV file."""
        default_kwargs = {"index": False}
        default_kwargs.update(kwargs)
        data.to_csv(file_path, **default_kwargs)

    def _save_excel(self, data: pd.DataFrame, file_path: Path, **kwargs) -> None:
        """Save Excel file."""
        default_kwargs = {"index": False}
        default_kwargs.update(kwargs)
        data.to_excel(file_path, **default_kwargs)

    def _save_parquet(self, data: pd.DataFrame, file_path: Path, **kwargs) -> None:
        """Save Parquet file."""
        data.to_parquet(file_path, **kwargs)

    def register_loader(self, format_name: str, loader_func: Callable) -> None:
        """
        Register a custom loader function.

        This allows plugins to extend support for additional formats.

        Parameters
        ----------
        format_name : str
            Name of the format (e.g., "json", "sql").
        loader_func : callable
            Function that takes a Path and returns a DataFrame.
        """
        self._loaders[format_name.lower()] = loader_func

    def register_saver(self, format_name: str, saver_func: Callable) -> None:
        """
        Register a custom saver function.

        This allows plugins to extend support for additional formats.

        Parameters
        ----------
        format_name : str
            Name of the format (e.g., "json", "sql").
        saver_func : callable
            Function that takes (DataFrame, Path) and saves the data.
        """
        self._savers[format_name.lower()] = saver_func

