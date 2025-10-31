"""
Configuration loader with Pydantic-based validation.

This module defines the structure of config.yaml and provides
validation with clear error messages.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator, FilePath
import yaml


class IOModel(BaseModel):
    """Input/Output configuration."""

    input_file: str = Field(..., description="Path to input data file")
    output_file: str = Field(..., description="Path to output data file")
    input_format: str = Field(..., description="Input format: csv, excel, or parquet")
    output_format: str = Field(default="csv", description="Output format")
    sheet_name: Optional[str] = Field(None, description="Sheet name for Excel files")


class CleaningRule(BaseModel):
    """Single cleaning rule configuration."""

    name: str = Field(..., description="Name of the cleaning rule")
    enabled: bool = Field(default=True, description="Whether this rule is enabled")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Rule parameters")


class CleaningConfig(BaseModel):
    """Data cleaning configuration."""

    enabled: bool = Field(default=True, description="Whether cleaning is enabled")
    rules: List[CleaningRule] = Field(default_factory=list, description="List of cleaning rules")


class MappingSource(BaseModel):
    """Mapping source configuration."""

    type: str = Field(..., description="Type: direct, fuzzy, or ai")
    file: Optional[str] = Field(None, description="Path to mapping file")
    version: Optional[str] = Field(None, description="Version of the mapping file")
    threshold: float = Field(default=0.85, description="Confidence threshold for AI mapping")
    enabled: bool = Field(default=True, description="Whether this source is enabled")


class MappingConfig(BaseModel):
    """Cause mapping configuration."""

    enabled: bool = Field(default=True, description="Whether mapping is enabled")
    source_column: str = Field(..., description="Column name containing source codes")
    target_column: str = Field(default="gbd_cause", description="Column name for GBD causes")
    sources: List[MappingSource] = Field(default_factory=list, description="Mapping sources")


class QualityCheck(BaseModel):
    """Single quality check configuration."""

    name: str = Field(..., description="Name of the quality check")
    enabled: bool = Field(default=True, description="Whether this check is enabled")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Check parameters")


class QualityConfig(BaseModel):
    """Data quality configuration."""

    enabled: bool = Field(default=True, description="Whether quality checks are enabled")
    checks: List[QualityCheck] = Field(default_factory=list, description="List of quality checks")


class ReportingConfig(BaseModel):
    """Reporting configuration."""

    enabled: bool = Field(default=True, description="Whether reporting is enabled")
    output_file: str = Field(default="harmonization_report.md", description="Output report file")
    format: str = Field(default="markdown", description="Report format: markdown or html")


class AutoGBDConfig(BaseModel):
    """Main configuration model for AutoGBD."""

    io: IOModel = Field(..., description="Input/Output configuration")
    cleaning: CleaningConfig = Field(default_factory=CleaningConfig, description="Cleaning config")
    mapping: MappingConfig = Field(..., description="Mapping configuration")
    quality: QualityConfig = Field(default_factory=QualityConfig, description="Quality config")
    reporting: ReportingConfig = Field(
        default_factory=ReportingConfig, description="Reporting configuration"
    )

    @validator("io")
    def validate_io_format(cls, v):
        """Validate input/output formats."""
        valid_input = {"csv", "excel", "xlsx", "parquet"}
        valid_output = {"csv", "excel", "xlsx", "parquet"}
        if v.input_format.lower() not in valid_input:
            raise ValueError(
                f"Invalid input_format: {v.input_format}. Must be one of {valid_input}"
            )
        if v.output_format.lower() not in valid_output:
            raise ValueError(
                f"Invalid output_format: {v.output_format}. Must be one of {valid_output}"
            )
        return v

    @classmethod
    def from_yaml(cls, config_path: Union[str, Path]) -> "AutoGBDConfig":
        """
        Load configuration from a YAML file.

        Parameters
        ----------
        config_path : str or Path
            Path to the YAML configuration file.

        Returns
        -------
        AutoGBDConfig
            Validated configuration object.

        Raises
        ------
        FileNotFoundError
            If the config file doesn't exist.
        ValueError
            If the config file is invalid.
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r") as f:
            config_dict = yaml.safe_load(f)

        try:
            return cls(**config_dict)
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}") from e


class ConfigLoader:
    """
    Configuration loader utility class.

    Provides methods for loading and validating AutoGBD configurations.
    """

    @staticmethod
    def load(config_path: Union[str, Path]) -> AutoGBDConfig:
        """
        Load and validate a configuration file.

        Parameters
        ----------
        config_path : str or Path
            Path to the YAML configuration file.

        Returns
        -------
        AutoGBDConfig
            Validated configuration object.
        """
        return AutoGBDConfig.from_yaml(config_path)

