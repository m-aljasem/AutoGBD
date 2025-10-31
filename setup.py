"""
Setup configuration for AutoGBD.
"""

from pathlib import Path
from setuptools import setup, find_packages

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read version from __init__.py
version = "0.1.0"
init_file = Path(__file__).parent / "autogbd" / "__init__.py"
if init_file.exists():
    for line in init_file.read_text().splitlines():
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

setup(
    name="autogbd",
    version=version,
    description="Intelligent health data harmonization framework for GBD",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="AutoGBD Team",
    author_email="info@autogbd.org",
    url="https://github.com/autogbd/autogbd",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.10",
    install_requires=[
        "pandas>=2.0.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "rapidfuzz>=3.0.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "ai": [
            "sentence-transformers>=2.2.0",
            "torch>=2.0.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "autogbd=autogbd.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="health data harmonization GBD global burden disease",
)

