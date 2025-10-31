"""Tests for provenance tracking."""

import pytest
import json
from pathlib import Path
import tempfile

from autogbd.core.provenance import ProvenanceTracker, ProvenanceEntry


def test_provenance_tracker_initialization():
    """Test provenance tracker initialization."""
    tracker = ProvenanceTracker()
    assert tracker.run_id is not None
    assert len(tracker.entries) == 0


def test_provenance_log():
    """Test logging provenance entries."""
    tracker = ProvenanceTracker(run_id="test_run")

    tracker.log(
        step="cleaning",
        action="remove_duplicates",
        details={"rule": "drop_duplicates"},
        rows_affected=10,
    )

    assert len(tracker.entries) == 1
    assert tracker.entries[0].step == "cleaning"
    assert tracker.entries[0].action == "remove_duplicates"
    assert tracker.entries[0].rows_affected == 10


def test_provenance_save(tmp_path):
    """Test saving provenance log to file."""
    tracker = ProvenanceTracker(run_id="test_run")
    tracker.log(step="test", action="test_action", details={})

    output_file = tmp_path / "provenance.json"
    tracker.save(output_file)

    assert output_file.exists()

    with open(output_file) as f:
        data = json.load(f)

    assert data["run_id"] == "test_run"
    assert len(data["entries"]) == 1


def test_provenance_to_dict():
    """Test converting provenance to dictionary."""
    tracker = ProvenanceTracker(run_id="test_run")
    tracker.log(step="test", action="test_action", details={"key": "value"})

    data = tracker.to_dict()

    assert "run_id" in data
    assert "start_time" in data
    assert "end_time" in data
    assert "entries" in data
    assert len(data["entries"]) == 1


def test_provenance_summary():
    """Test getting provenance summary."""
    tracker = ProvenanceTracker(run_id="test_run")

    tracker.log(step="cleaning", action="rule1", details={}, rows_affected=10)
    tracker.log(step="cleaning", action="rule2", details={}, rows_affected=20)
    tracker.log(step="mapping", action="map_codes", details={}, rows_affected=5)

    summary = tracker.get_summary()

    assert summary["total_entries"] == 3
    assert "cleaning" in summary["steps"]
    assert summary["steps"]["cleaning"]["entry_count"] == 2
    assert summary["steps"]["cleaning"]["total_rows_affected"] == 30

