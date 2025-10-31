"""
Main pipeline orchestrator for AutoGBD.

This module contains the AutoGBDPipeline class that reads configuration
and sequentially executes the harmonization steps.
"""

from pathlib import Path
from typing import Optional
import pandas as pd

from autogbd.core.config_loader import AutoGBDConfig, ConfigLoader
from autogbd.core.provenance import ProvenanceTracker
from autogbd.io.handlers import DataHandler
from autogbd.cleaning.rules import CleaningEngine
from autogbd.mapping.engine import MappingEngine
from autogbd.quality.checks import QualityChecker
from autogbd.reporting.generator import ReportGenerator


class AutoGBDPipeline:
    """
    Main pipeline orchestrator for AutoGBD harmonization.

    This class coordinates all stages of the harmonization process:
    data loading, cleaning, mapping, quality checks, and reporting.
    """

    def __init__(self, config: AutoGBDConfig, provenance: Optional[ProvenanceTracker] = None):
        """
        Initialize the pipeline.

        Parameters
        ----------
        config : AutoGBDConfig
            Configuration object for this run.
        provenance : ProvenanceTracker, optional
            Provenance tracker. If not provided, a new one will be created.
        """
        self.config = config
        self.provenance = provenance or ProvenanceTracker()
        self.data: Optional[pd.DataFrame] = None
        self.quality_results: Optional[dict] = None

        # Initialize components
        self.data_handler = DataHandler()
        self.cleaning_engine = CleaningEngine(provenance=self.provenance)
        self.mapping_engine = MappingEngine(
            source_column=config.mapping.source_column,
            target_column=config.mapping.target_column,
            provenance=self.provenance,
        )
        self.quality_checker = QualityChecker(provenance=self.provenance)
        self.report_generator = ReportGenerator()

    def run(self) -> pd.DataFrame:
        """
        Execute the complete harmonization pipeline.

        Returns
        -------
        pd.DataFrame
            Harmonized data ready for analysis.
        """
        # Log pipeline start
        self.provenance.log(
            step="pipeline",
            action="start",
            details={"config_file": "config.yaml"},  # Don't log full config
        )

        # Step 1: Load data
        self.data = self._load_data()

        # Step 2: Cleaning
        if self.config.cleaning.enabled:
            self.data = self._clean_data()

        # Step 3: Mapping
        if self.config.mapping.enabled:
            self.data = self._map_data()

        # Step 4: Quality checks
        if self.config.quality.enabled:
            self.quality_results = self._check_quality()

        # Step 5: Save output
        self._save_output()

        # Step 6: Generate report
        if self.config.reporting.enabled:
            self._generate_report()

        # Step 7: Save provenance
        provenance_path = Path(self.config.io.output_file).parent / "provenance.json"
        self.provenance.save(provenance_path)

        self.provenance.log(
            step="pipeline",
            action="complete",
            details={"rows_final": len(self.data)},
        )

        return self.data

    def _load_data(self) -> pd.DataFrame:
        """Load input data."""
        self.provenance.log(
            step="io",
            action="load_data",
            details={"input_file": self.config.io.input_file},
            file_used=self.config.io.input_file,
        )

        data = self.data_handler.load(
            file_path=self.config.io.input_file,
            file_format=self.config.io.input_format,
            sheet_name=self.config.io.sheet_name,
        )

        self.provenance.log(
            step="io",
            action="data_loaded",
            details={"rows": len(data), "columns": list(data.columns)},
            rows_affected=len(data),
        )

        return data

    def _clean_data(self) -> pd.DataFrame:
        """Apply cleaning rules."""
        self.provenance.log(
            step="cleaning",
            action="start_cleaning",
            details={"rules_enabled": len([r for r in self.config.cleaning.rules if r.enabled])},
        )

        data = self.cleaning_engine.apply_rules(
            data=self.data,
            rules=self.config.cleaning.rules,
        )

        return data

    def _map_data(self) -> pd.DataFrame:
        """Apply mapping rules."""
        self.provenance.log(
            step="mapping",
            action="start_mapping",
            details={
                "source_column": self.config.mapping.source_column,
                "target_column": self.config.mapping.target_column,
            },
        )

        data = self.mapping_engine.apply_mappings(
            data=self.data,
            mapping_config=self.config.mapping,
        )

        return data

    def _check_quality(self) -> dict:
        """Run quality checks."""
        self.provenance.log(
            step="quality",
            action="start_quality_checks",
            details={"checks_enabled": len([c for c in self.config.quality.checks if c.enabled])},
        )

        results = self.quality_checker.run_checks(
            data=self.data,
            checks=self.config.quality.checks,
        )

        return results

    def _save_output(self) -> None:
        """Save harmonized data."""
        self.provenance.log(
            step="io",
            action="save_data",
            details={"output_file": self.config.io.output_file},
        )

        self.data_handler.save(
            data=self.data,
            file_path=self.config.io.output_file,
            file_format=self.config.io.output_format,
        )

        self.provenance.log(
            step="io",
            action="data_saved",
            details={"rows": len(self.data)},
            rows_affected=len(self.data),
        )

    def _generate_report(self) -> None:
        """Generate harmonization report."""
        self.provenance.log(
            step="reporting",
            action="generate_report",
            details={"output_file": self.config.reporting.output_file},
        )

        report_path = Path(self.config.io.output_file).parent / self.config.reporting.output_file

        self.report_generator.generate(
            data=self.data,
            quality_results=self.quality_results,
            provenance=self.provenance,
            output_path=report_path,
        )

        self.provenance.log(
            step="reporting",
            action="report_generated",
            details={"report_path": str(report_path)},
        )

