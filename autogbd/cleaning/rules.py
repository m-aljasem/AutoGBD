"""
Data cleaning and normalization rules.

This module implements a library of common cleaning functions
that can be applied based on configuration.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import re

from autogbd.core.config_loader import CleaningRule
from autogbd.core.provenance import ProvenanceTracker


class CleaningEngine:
    """
    Engine for applying data cleaning rules.

    Provides a library of standard cleaning functions that can be
    configured and applied to datasets.
    """

    def __init__(self, provenance: Optional[ProvenanceTracker] = None):
        """
        Initialize the cleaning engine.

        Parameters
        ----------
        provenance : ProvenanceTracker, optional
            Provenance tracker for logging actions.
        """
        self.provenance = provenance
        self._rules = {
            "normalize_column_names": self._normalize_column_names,
            "remove_duplicates": self._remove_duplicates,
            "normalize_sex": self._normalize_sex,
            "standardize_ages": self._standardize_ages,
            "handle_missing_values": self._handle_missing_values,
            "normalize_text": self._normalize_text,
            "remove_outliers": self._remove_outliers,
            "standardize_dates": self._standardize_dates,
        }

    def apply_rules(self, data: pd.DataFrame, rules: List[CleaningRule]) -> pd.DataFrame:
        """
        Apply a list of cleaning rules to the data.

        Parameters
        ----------
        data : pd.DataFrame
            Data to clean.
        rules : list of CleaningRule
            List of rules to apply.

        Returns
        -------
        pd.DataFrame
            Cleaned data.
        """
        result = data.copy()
        initial_rows = len(result)

        for rule in rules:
            if not rule.enabled:
                continue

            if rule.name not in self._rules:
                if self.provenance:
                    self.provenance.log(
                        step="cleaning",
                        action="rule_skipped",
                        details={"reason": f"Unknown rule: {rule.name}"},
                        rule_name=rule.name,
                    )
                continue

            try:
                rows_before = len(result)
                result = self._rules[rule.name](result, rule.parameters)
                rows_after = len(result)
                rows_affected = abs(rows_after - rows_before)

                if self.provenance:
                    self.provenance.log(
                        step="cleaning",
                        action=rule.name,
                        details=rule.parameters,
                        rows_affected=rows_affected,
                        rule_name=rule.name,
                    )
            except Exception as e:
                if self.provenance:
                    self.provenance.log(
                        step="cleaning",
                        action="rule_error",
                        details={"error": str(e), "rule": rule.name},
                        rule_name=rule.name,
                    )
                raise

        final_rows = len(result)
        if self.provenance:
            self.provenance.log(
                step="cleaning",
                action="cleaning_complete",
                details={
                    "initial_rows": initial_rows,
                    "final_rows": final_rows,
                    "rows_removed": initial_rows - final_rows,
                },
            )

        return result

    def _normalize_column_names(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Normalize column names to lowercase with underscores."""
        data = data.copy()
        old_names = list(data.columns)
        data.columns = data.columns.str.lower().str.replace(" ", "_", regex=False)
        new_names = list(data.columns)
        rename_map = dict(zip(old_names, new_names))
        return data

    def _remove_duplicates(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Remove duplicate rows."""
        subset = params.get("subset", None)
        keep = params.get("keep", "first")
        return data.drop_duplicates(subset=subset, keep=keep)

    def _normalize_sex(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Normalize sex/gender column values."""
        data = data.copy()
        column = params.get("column", "sex")

        if column not in data.columns:
            return data

        # Common mappings
        mapping = {
            "m": "male",
            "male": "male",
            "1": "male",
            "f": "female",
            "female": "female",
            "2": "female",
            "0": "unknown",
            "unknown": "unknown",
            "u": "unknown",
        }

        data[column] = data[column].astype(str).str.lower().str.strip()
        data[column] = data[column].map(mapping).fillna(data[column])

        # Allow custom mappings from params
        custom_mapping = params.get("custom_mapping", {})
        if custom_mapping:
            data[column] = data[column].replace(custom_mapping)

        return data

    def _standardize_ages(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Standardize age values."""
        data = data.copy()
        column = params.get("column", "age")

        if column not in data.columns:
            return data

        # Convert to numeric, handling non-numeric values
        data[column] = pd.to_numeric(data[column], errors="coerce")

        # Remove negative ages or ages > 150
        min_age = params.get("min_age", 0)
        max_age = params.get("max_age", 150)
        invalid_mask = (data[column] < min_age) | (data[column] > max_age)

        if invalid_mask.any():
            # Option to set to NaN or remove
            if params.get("remove_invalid", False):
                data = data[~invalid_mask]
            else:
                data.loc[invalid_mask, column] = None

        return data

    def _handle_missing_values(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Handle missing values based on strategy."""
        data = data.copy()
        strategy = params.get("strategy", "keep")  # keep, drop, fill

        if strategy == "drop":
            subset = params.get("subset", None)
            data = data.dropna(subset=subset)
        elif strategy == "fill":
            columns = params.get("columns", data.columns)
            value = params.get("value", "")
            for col in columns:
                if col in data.columns:
                    data[col] = data[col].fillna(value)

        return data

    def _normalize_text(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Normalize text columns (trim, lowercase, etc.)."""
        data = data.copy()
        columns = params.get("columns", [])

        for col in columns:
            if col in data.columns:
                data[col] = data[col].astype(str).str.strip().str.lower()

        return data

    def _remove_outliers(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Remove outliers using IQR method."""
        data = data.copy()
        column = params.get("column")
        if not column or column not in data.columns:
            return data

        Q1 = data[column].quantile(0.25)
        Q3 = data[column].quantile(0.75)
        IQR = Q3 - Q1

        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        data = data[(data[column] >= lower_bound) & (data[column] <= upper_bound)]

        return data

    def _standardize_dates(self, data: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Standardize date columns."""
        data = data.copy()
        column = params.get("column")

        if not column or column not in data.columns:
            return data

        date_format = params.get("format", None)
        try:
            data[column] = pd.to_datetime(data[column], format=date_format, errors="coerce")
        except Exception:
            pass

        return data

