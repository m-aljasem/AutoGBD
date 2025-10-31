"""
AutoGBD: An intelligent, open-source framework for health data harmonization.

This framework transforms raw health data into analysis-ready formats with
full reproducibility and transparency.
"""

__version__ = "0.1.0"
__author__ = "AutoGBD Team"

from autogbd.core.pipeline import AutoGBDPipeline
from autogbd.core.config_loader import ConfigLoader

__all__ = ["AutoGBDPipeline", "ConfigLoader"]

