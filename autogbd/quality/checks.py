"""
Data quality assessment and validation.

This module runs a series of quality checks defined in configuration
and generates quality scores and summaries.
"""

from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

from autogbd.core.config_loader import QualityCheck
from autogbd.core.provenance import ProvenanceTracker


class QualityChecker:
    """
    Engine for running data quality checks.

    Provides a library of standard quality checks that can be
    configured and applied to datasets.
    """

    def __init__(self, provenance: Optional[ProvenanceTracker] = None):
        """
        Initialize the quality checker.

        Parameters
        ----------
        provenance : ProvenanceTracker, optional
            Provenance tracker for logging actions.
        """
        self.provenance = provenance
        self._checks = {
            "check_age_range": self._check_age_range,
            "check_sex_values": self._check_sex_values,
            "check_missing_values": self._check_missing_values,
            "check_unmapped_codes": self._check_unmapped_codes,
            "check_death_count_validity": self._check_death_count_validity,
            "check_value_ranges": self._check_value_ranges,
            "check_duplicates": self._check_duplicates,
            "check_date_validity": self._check_date_validity,
            "check_completeness": self._check_completeness,
        }

    def run_checks(
        self, data: pd.DataFrame, checks: List[QualityCheck]
    ) -> Dict[str, Any]:
        """
        Run a list of quality checks on the data.

        Parameters
        ----------
        data : pd.DataFrame
            Data to check.
        checks : list of QualityCheck
            List of quality checks to run.

        Returns
        -------
        dict
            Summary of quality check results.
        """
        results = {
            "total_rows": len(data),
            "checks_run": [],
            "issues_found": [],
            "quality_score": 100.0,
        }

        for check in checks:
            if not check.enabled:
                continue

            if check.name not in self._checks:
                if self.provenance:
                    self.provenance.log(
                        step="quality",
                        action="check_skipped",
                        details={"reason": f"Unknown check: {check.name}"},
                    )
                continue

            try:
                check_result = self._checks[check.name](data, check.parameters)
                results["checks_run"].append(check.name)
                results["issues_found"].extend(check_result.get("issues", []))

                if self.provenance:
                    self.provenance.log(
                        step="quality",
                        action=check.name,
                        details=check_result,
                    )
            except Exception as e:
                if self.provenance:
                    self.provenance.log(
                        step="quality",
                        action="check_error",
                        details={"error": str(e), "check": check.name},
                    )
                results["issues_found"].append(
                    {
                        "check": check.name,
                        "severity": "error",
                        "message": f"Check failed with error: {str(e)}",
                    }
                )

        # Calculate overall quality score
        results["quality_score"] = self._calculate_quality_score(data, results)

        if self.provenance:
            self.provenance.log(
                step="quality",
                action="quality_check_complete",
                details={
                    "checks_run": len(results["checks_run"]),
                    "issues_found": len(results["issues_found"]),
                    "quality_score": results["quality_score"],
                },
            )

        return results

    def _check_age_range(
        self, data: pd.DataFrame, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if ages are within valid range."""
        column = params.get("column", "age")
        min_age = params.get("min_age", 0)
        max_age = params.get("max_age", 150)

        issues = []

        if column in data.columns:
            invalid_ages = data[
                (data[column] < min_age) | (data[column] > max_age)
            ].index.tolist()

            if invalid_ages:
                issues.append(
                    {
                        "check": "check_age_range",
                        "severity": "warning",
                        "message": f"Found {len(invalid_ages)} rows with ages outside range [{min_age}, {max_age}]",
                        "count": len(invalid_ages),
                    }
                )

        return {
            "issues": issues,
            "summary": f"Age range check: {len(issues)} issues found",
        }

    def _check_sex_values(self, data: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check if sex values are valid."""
        column = params.get("column", "sex")
        valid_values = params.get("valid_values", ["male", "female", "unknown"])

        issues = []

        if column in data.columns:
            invalid_sex = data[~data[column].isin(valid_values)].index.tolist()

            if invalid_sex:
                unique_invalid = data.loc[invalid_sex, column].unique().tolist()
                issues.append(
                    {
                        "check": "check_sex_values",
                        "severity": "warning",
                        "message": f"Found {len(invalid_sex)} rows with invalid sex values: {unique_invalid}",
                        "count": len(invalid_sex),
                        "invalid_values": unique_invalid,
                    }
                )

        return {
            "issues": issues,
            "summary": f"Sex values check: {len(issues)} issues found",
        }

    def _check_missing_values(
        self, data: pd.DataFrame, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for missing values in critical columns."""
        columns = params.get("columns", [])
        threshold = params.get("threshold", 0.1)  # 10% missing allowed

        issues = []

        for col in columns:
            if col in data.columns:
                missing_count = data[col].isna().sum()
                missing_pct = missing_count / len(data)

                if missing_pct > threshold:
                    issues.append(
                        {
                            "check": "check_missing_values",
                            "severity": "warning",
                            "message": f"Column '{col}' has {missing_count} ({missing_pct:.1%}) missing values (threshold: {threshold:.1%})",
                            "column": col,
                            "missing_count": missing_count,
                            "missing_percentage": missing_pct,
                        }
                    )

        return {
            "issues": issues,
            "summary": f"Missing values check: {len(issues)} issues found",
        }

    def _check_unmapped_codes(
        self, data: pd.DataFrame, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for unmapped cause codes."""
        target_column = params.get("target_column", "gbd_cause")
        threshold = params.get("threshold", 0.05)  # 5% unmapped allowed

        issues = []

        if target_column in data.columns:
            unmapped_count = data[target_column].isna().sum()
            unmapped_pct = unmapped_count / len(data) if len(data) > 0 else 0

            if unmapped_pct > threshold:
                unique_unmapped = (
                    data[data[target_column].isna()][params.get("source_column", "")]
                    .unique()
                    .tolist()
                    if params.get("source_column") in data.columns
                    else []
                )

                issues.append(
                    {
                        "check": "check_unmapped_codes",
                        "severity": "warning",
                        "message": f"Found {unmapped_count} ({unmapped_pct:.1%}) unmapped codes (threshold: {threshold:.1%})",
                        "count": unmapped_count,
                        "percentage": unmapped_pct,
                        "unique_unmapped": len(unique_unmapped),
                    }
                )

        return {
            "issues": issues,
            "summary": f"Unmapped codes check: {len(issues)} issues found",
        }

    def _check_death_count_validity(
        self, data: pd.DataFrame, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if death counts are valid (non-negative, reasonable)."""
        column = params.get("column", "deaths")
        max_reasonable = params.get("max_reasonable", 1000000)

        issues = []

        if column in data.columns:
            negative = data[data[column] < 0].index.tolist()
            too_large = data[data[column] > max_reasonable].index.tolist()

            if negative:
                issues.append(
                    {
                        "check": "check_death_count_validity",
                        "severity": "error",
                        "message": f"Found {len(negative)} rows with negative death counts",
                        "count": len(negative),
                    }
                )

            if too_large:
                issues.append(
                    {
                        "check": "check_death_count_validity",
                        "severity": "warning",
                        "message": f"Found {len(too_large)} rows with death counts > {max_reasonable}",
                        "count": len(too_large),
                    }
                )

        return {
            "issues": issues,
            "summary": f"Death count validity check: {len(issues)} issues found",
        }

    def _check_value_ranges(
        self, data: pd.DataFrame, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if values are within expected ranges."""
        column = params.get("column")
        min_value = params.get("min_value")
        max_value = params.get("max_value")

        issues = []

        if column and column in data.columns:
            invalid = []

            if min_value is not None:
                invalid.extend(data[data[column] < min_value].index.tolist())

            if max_value is not None:
                invalid.extend(data[data[column] > max_value].index.tolist())

            if invalid:
                issues.append(
                    {
                        "check": "check_value_ranges",
                        "severity": "warning",
                        "message": f"Found {len(set(invalid))} rows with values outside range [{min_value}, {max_value}]",
                        "count": len(set(invalid)),
                    }
                )

        return {
            "issues": issues,
            "summary": f"Value range check: {len(issues)} issues found",
        }

    def _check_duplicates(self, data: pd.DataFrame, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check for duplicate rows."""
        subset = params.get("subset", None)
        allow_duplicates = params.get("allow_duplicates", False)

        issues = []

        if not allow_duplicates:
            duplicates = data.duplicated(subset=subset)

            if duplicates.any():
                issues.append(
                    {
                        "check": "check_duplicates",
                        "severity": "warning",
                        "message": f"Found {duplicates.sum()} duplicate rows",
                        "count": duplicates.sum(),
                    }
                )

        return {
            "issues": issues,
            "summary": f"Duplicate check: {len(issues)} issues found",
        }

    def _check_date_validity(
        self, data: pd.DataFrame, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if date columns contain valid dates."""
        column = params.get("column")

        issues = []

        if column and column in data.columns:
            # Try to parse dates
            try:
                pd.to_datetime(data[column], errors="raise")
            except Exception:
                invalid_count = len(data) - len(pd.to_datetime(data[column], errors="coerce").dropna())

                if invalid_count > 0:
                    issues.append(
                        {
                            "check": "check_date_validity",
                            "severity": "warning",
                            "message": f"Found {invalid_count} rows with invalid dates in column '{column}'",
                            "count": invalid_count,
                        }
                    )

        return {
            "issues": issues,
            "summary": f"Date validity check: {len(issues)} issues found",
        }

    def _check_completeness(
        self, data: pd.DataFrame, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check overall data completeness."""
        required_columns = params.get("required_columns", [])

        issues = []

        missing_columns = [col for col in required_columns if col not in data.columns]

        if missing_columns:
            issues.append(
                {
                    "check": "check_completeness",
                    "severity": "error",
                    "message": f"Missing required columns: {missing_columns}",
                    "missing_columns": missing_columns,
                }
            )

        return {
            "issues": issues,
            "summary": f"Completeness check: {len(issues)} issues found",
        }

    def _calculate_quality_score(
        self, data: pd.DataFrame, results: Dict[str, Any]
    ) -> float:
        """
        Calculate overall data quality score (0-100).

        Parameters
        ----------
        data : pd.DataFrame
            The data being checked.
        results : dict
            Results from quality checks.

        Returns
        -------
        float
            Quality score from 0 to 100.
        """
        if len(data) == 0:
            return 0.0

        score = 100.0

        # Penalize based on issues found
        for issue in results["issues_found"]:
            if issue.get("severity") == "error":
                score -= 10.0
            elif issue.get("severity") == "warning":
                score -= 2.0

        # Bonus for completeness
        completeness = 1.0 - (data.isna().sum().sum() / (len(data) * len(data.columns)))
        score = score * 0.7 + (completeness * 100) * 0.3

        return max(0.0, min(100.0, score))

