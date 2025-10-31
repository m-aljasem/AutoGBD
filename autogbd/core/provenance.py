"""
Provenance tracking for complete audit trails.

This module logs every action taken during harmonization, creating
an unbreakable chain of evidence for reproducibility.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict


@dataclass
class ProvenanceEntry:
    """Single entry in the provenance log."""

    timestamp: str
    step: str
    action: str
    details: Dict[str, Any]
    rows_affected: Optional[int] = None
    rule_name: Optional[str] = None
    file_used: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ProvenanceTracker:
    """
    Tracks provenance information throughout the harmonization pipeline.

    This creates a complete audit trail of all transformations applied
    to the data, ensuring full reproducibility.
    """

    def __init__(self, run_id: Optional[str] = None):
        """
        Initialize the provenance tracker.

        Parameters
        ----------
        run_id : str, optional
            Unique identifier for this run. If not provided, will be generated.
        """
        self.run_id = run_id or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.entries: List[ProvenanceEntry] = []
        self.start_time = datetime.now()

    def log(
        self,
        step: str,
        action: str,
        details: Dict[str, Any],
        rows_affected: Optional[int] = None,
        rule_name: Optional[str] = None,
        file_used: Optional[str] = None,
    ) -> None:
        """
        Log a provenance entry.

        Parameters
        ----------
        step : str
            Pipeline step (e.g., "cleaning", "mapping", "quality").
        action : str
            Action taken (e.g., "remove_duplicates", "map_codes").
        details : dict
            Additional details about the action.
        rows_affected : int, optional
            Number of rows affected by this action.
        rule_name : str, optional
            Name of the rule or function applied.
        file_used : str, optional
            Path to file used (e.g., mapping file).
        """
        entry = ProvenanceEntry(
            timestamp=datetime.now().isoformat(),
            step=step,
            action=action,
            details=details,
            rows_affected=rows_affected,
            rule_name=rule_name,
            file_used=file_used,
        )
        self.entries.append(entry)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert provenance log to dictionary.

        Returns
        -------
        dict
            Complete provenance log as dictionary.
        """
        end_time = datetime.now()
        duration_seconds = (end_time - self.start_time).total_seconds()

        return {
            "run_id": self.run_id,
            "start_time": self.start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration_seconds,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    def save(self, output_path: Union[str, Path]) -> None:
        """
        Save provenance log to JSON file.

        Parameters
        ----------
        output_path : str or Path
            Path where the provenance log should be saved.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        provenance_dict = self.to_dict()

        with open(output_path, "w") as f:
            json.dump(provenance_dict, f, indent=2)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the provenance log.

        Returns
        -------
        dict
            Summary statistics of the provenance log.
        """
        steps = {}
        for entry in self.entries:
            if entry.step not in steps:
                steps[entry.step] = {
                    "actions": [],
                    "total_rows_affected": 0,
                    "entry_count": 0,
                }
            steps[entry.step]["actions"].append(entry.action)
            steps[entry.step]["entry_count"] += 1
            if entry.rows_affected:
                steps[entry.step]["total_rows_affected"] += entry.rows_affected

        return {
            "run_id": self.run_id,
            "total_entries": len(self.entries),
            "steps": steps,
        }

