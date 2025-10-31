"""
Mapping engine for vocabulary and code translation.

This module handles direct and fuzzy string matching of cause-of-death
codes (ICD-10/11) to GBD cause lists.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
from rapidfuzz import fuzz, process

from autogbd.core.config_loader import MappingConfig, MappingSource
from autogbd.core.provenance import ProvenanceTracker
from autogbd.mapping.ai_assistant import AIAssistant


class MappingEngine:
    """
    Engine for mapping source codes to target GBD cause codes.

    Supports direct mapping, fuzzy matching, and AI-assisted mapping
    with human-in-the-loop functionality.
    """

    def __init__(
        self,
        source_column: str,
        target_column: str = "gbd_cause",
        provenance: Optional[ProvenanceTracker] = None,
    ):
        """
        Initialize the mapping engine.

        Parameters
        ----------
        source_column : str
            Name of the column containing source codes.
        target_column : str
            Name of the column for mapped GBD causes.
        provenance : ProvenanceTracker, optional
            Provenance tracker for logging actions.
        """
        self.source_column = source_column
        self.target_column = target_column
        self.provenance = provenance
        self.direct_mappings: Dict[str, str] = {}
        self.ai_assistant: Optional[AIAssistant] = None

    def apply_mappings(
        self, data: pd.DataFrame, mapping_config: MappingConfig
    ) -> pd.DataFrame:
        """
        Apply mapping rules to the data.

        Parameters
        ----------
        data : pd.DataFrame
            Data to map.
        mapping_config : MappingConfig
            Mapping configuration.

        Returns
        -------
        pd.DataFrame
            Data with mapped codes.
        """
        if self.source_column not in data.columns:
            if self.provenance:
                self.provenance.log(
                    step="mapping",
                    action="error",
                    details={"error": f"Source column '{self.source_column}' not found"},
                )
            return data

        result = data.copy()
        result[self.target_column] = None

        initial_unmapped = len(result)

        # Process mapping sources in order
        for source in mapping_config.sources:
            if not source.enabled:
                continue

            if source.type == "direct":
                result = self._apply_direct_mapping(result, source)
            elif source.type == "fuzzy":
                result = self._apply_fuzzy_mapping(result, source)
            elif source.type == "ai":
                result = self._apply_ai_mapping(result, source)

        # Generate human review file for unmapped codes
        unmapped = result[result[self.target_column].isna()]
        if len(unmapped) > 0:
            self._generate_review_file(unmapped, mapping_config)

        final_unmapped = len(unmapped)
        mapped_count = initial_unmapped - final_unmapped
        mapping_rate = (mapped_count / initial_unmapped * 100) if initial_unmapped > 0 else 0

        if self.provenance:
            self.provenance.log(
                step="mapping",
                action="mapping_complete",
                details={
                    "initial_rows": initial_unmapped,
                    "mapped_count": mapped_count,
                    "unmapped_count": final_unmapped,
                    "mapping_rate": f"{mapping_rate:.2f}%",
                },
                rows_affected=mapped_count,
            )

        return result

    def _apply_direct_mapping(
        self, data: pd.DataFrame, source: MappingSource
    ) -> pd.DataFrame:
        """Apply direct (1:1) mapping from a file."""
        if not source.file:
            return data

        mapping_file = Path(source.file)
        if not mapping_file.exists():
            if self.provenance:
                self.provenance.log(
                    step="mapping",
                    action="error",
                    details={"error": f"Mapping file not found: {mapping_file}"},
                    file_used=str(mapping_file),
                )
            return data

        # Load mapping file (expected: source_code, target_code columns)
        mapping_df = pd.read_csv(mapping_file)
        if "source_code" not in mapping_df.columns or "target_code" not in mapping_df.columns:
            raise ValueError(
                "Mapping file must contain 'source_code' and 'target_code' columns"
            )

        mapping_dict = dict(zip(mapping_df["source_code"], mapping_df["target_code"]))

        # Apply mapping only to unmapped rows
        unmapped_mask = data[self.target_column].isna()
        data.loc[unmapped_mask, self.target_column] = data.loc[
            unmapped_mask, self.source_column
        ].map(mapping_dict)

        mapped_count = unmapped_mask.sum() - data[self.target_column].isna().sum()

        if self.provenance:
            self.provenance.log(
                step="mapping",
                action="direct_mapping",
                details={
                    "mapping_file": str(mapping_file),
                    "version": source.version,
                    "mapped_count": mapped_count,
                },
                rows_affected=mapped_count,
                file_used=str(mapping_file),
            )

        return data

    def _apply_fuzzy_mapping(
        self, data: pd.DataFrame, source: MappingSource
    ) -> pd.DataFrame:
        """Apply fuzzy string matching."""
        if not source.file:
            return data

        mapping_file = Path(source.file)
        if not mapping_file.exists():
            return data

        mapping_df = pd.read_csv(mapping_file)
        if "target_code" not in mapping_df.columns:
            raise ValueError("Mapping file must contain 'target_code' column")

        target_codes = mapping_df["target_code"].tolist()
        threshold = source.threshold * 100  # Convert to 0-100 scale for rapidfuzz

        unmapped_mask = data[self.target_column].isna()
        unmapped_codes = data.loc[unmapped_mask, self.source_column].unique()

        mapping_dict = {}
        for code in unmapped_codes:
            if pd.isna(code):
                continue

            result = process.extractOne(
                str(code), target_codes, scorer=fuzz.ratio, score_cutoff=threshold
            )

            if result:
                mapping_dict[code] = result[0]

        # Apply fuzzy mappings
        data.loc[unmapped_mask, self.target_column] = data.loc[
            unmapped_mask, self.source_column
        ].map(mapping_dict)

        mapped_count = len(mapping_dict)

        if self.provenance:
            self.provenance.log(
                step="mapping",
                action="fuzzy_mapping",
                details={
                    "mapping_file": str(mapping_file),
                    "threshold": source.threshold,
                    "mapped_count": mapped_count,
                },
                rows_affected=mapped_count,
                file_used=str(mapping_file),
            )

        return data

    def _apply_ai_mapping(self, data: pd.DataFrame, source: MappingSource) -> pd.DataFrame:
        """Apply AI-assisted mapping with confidence threshold."""
        if self.ai_assistant is None:
            self.ai_assistant = AIAssistant(provenance=self.provenance)

        unmapped_mask = data[self.target_column].isna()
        unmapped_rows = data[unmapped_mask]

        if len(unmapped_rows) == 0:
            return data

        # Get unique unmapped codes
        unmapped_codes = unmapped_rows[self.source_column].dropna().unique()

        # Get AI suggestions with confidence scores
        suggestions = {}
        high_confidence_mappings = {}

        for code in unmapped_codes:
            top_matches = self.ai_assistant.suggest_mappings(str(code), top_k=3)

            if top_matches and top_matches[0]["confidence"] >= source.threshold:
                # Auto-apply high-confidence mappings
                high_confidence_mappings[code] = top_matches[0]["gbd_cause"]
            else:
                # Store suggestions for review
                suggestions[code] = top_matches

        # Apply high-confidence mappings
        if high_confidence_mappings:
            data.loc[unmapped_mask, self.target_column] = data.loc[
                unmapped_mask, self.source_column
            ].map(high_confidence_mappings)

            if self.provenance:
                self.provenance.log(
                    step="mapping",
                    action="ai_mapping_auto",
                    details={
                        "threshold": source.threshold,
                        "auto_mapped_count": len(high_confidence_mappings),
                    },
                    rows_affected=len(high_confidence_mappings),
                )

        return data

    def _generate_review_file(
        self, unmapped_data: pd.DataFrame, mapping_config: MappingConfig
    ) -> None:
        """Generate CSV file for human review of unmapped codes."""
        # Use a default output directory
        output_dir = Path(".")
        review_file = output_dir / "human_review_required.csv"

        unique_codes = unmapped_data[self.source_column].dropna().unique()

        review_rows = []
        if self.ai_assistant:
            for code in unique_codes:
                suggestions = self.ai_assistant.suggest_mappings(str(code), top_k=3)
                if suggestions:
                    for i, suggestion in enumerate(suggestions, 1):
                        review_rows.append(
                            {
                                "source_code": code,
                                "suggestion_rank": i,
                                "suggested_gbd_cause": suggestion["gbd_cause"],
                                "confidence_score": suggestion["confidence"],
                                "human_mapping": "",  # To be filled by reviewer
                            }
                        )
                else:
                    review_rows.append(
                        {
                            "source_code": code,
                            "suggestion_rank": 0,
                            "suggested_gbd_cause": "",
                            "confidence_score": 0.0,
                            "human_mapping": "",
                        }
                    )

        if review_rows:
            review_df = pd.DataFrame(review_rows)
            review_df.to_csv(review_file, index=False)

            if self.provenance:
                self.provenance.log(
                    step="mapping",
                    action="review_file_generated",
                    details={
                        "review_file": str(review_file),
                        "unmapped_codes_count": len(unique_codes),
                    },
                    file_used=str(review_file),
                )

