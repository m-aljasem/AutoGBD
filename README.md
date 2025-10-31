# AutoGBD: Intelligent Health Data Harmonization Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**AutoGBD** is an intelligent, open-source framework for harmonizing health data to Global Burden of Disease (GBD) standards. It transforms chaotic raw health data into structured, analysis-ready formats with complete reproducibility and transparency.

## Core Principles

1. **Reproducibility by Default**: Every output is perfectly reproducible with the same input data and configuration.

2. **Transparency as a Feature**: The system generates human-readable reports that narrate every decision, from cleaning to mapping to imputation.

3. **Extensibility as a Foundation**: Plugin architecture allows easy addition of new data sources, mapping targets, and quality checks.

4. **Trustworthy AI Integration**: AI serves as a trusted assistant with human-in-the-loop oversight for low-confidence mappings.

## Features

- **Configuration-Driven**: Single `config.yaml` file controls the entire pipeline
- **Multiple Data Formats**: Support for CSV, Excel, and Parquet files
- **Intelligent Mapping**: Direct mapping, fuzzy matching, and AI-assisted code translation
- **Data Quality Checks**: Comprehensive validation with configurable quality checks
- **Publication-Ready Reports**: Automatic generation of methodological appendix reports
- **Complete Audit Trail**: Full provenance logging for every transformation
- **Plugin Architecture**: Extensible system for custom data sources and transformations

## Installation

### Basic Installation

```bash
pip install autogbd
```

### With AI Features

```bash
pip install autogbd[ai]
```

### Development Installation

```bash
git clone https://github.com/autogbd/autogbd.git
cd autogbd
pip install -e ".[dev,ai]"
```

## Quick Start

1. **Create a configuration file** (`config.yaml`):

```yaml
io:
  input_file: "data/raw_data.csv"
  output_file: "output/harmonized_data.csv"
  input_format: "csv"
  output_format: "csv"

cleaning:
  enabled: true
  rules:
    - name: "remove_duplicates"
      enabled: true
      parameters: {}
    - name: "normalize_sex"
      enabled: true
      parameters:
        column: "sex"

mapping:
  enabled: true
  source_column: "icd10_code"
  target_column: "gbd_cause"
  sources:
    - type: "direct"
      file: "mappings/icd10_to_gbd.csv"
      version: "3.2"
      enabled: true
    - type: "fuzzy"
      file: "mappings/gbd_cause_list.csv"
      threshold: 0.85
      enabled: true
    - type: "ai"
      threshold: 0.85
      enabled: true

quality:
  enabled: true
  checks:
    - name: "check_age_range"
      enabled: true
      parameters:
        column: "age"
        min_age: 0
        max_age: 150
    - name: "check_unmapped_codes"
      enabled: true
      parameters:
        target_column: "gbd_cause"
        threshold: 0.05

reporting:
  enabled: true
  output_file: "harmonization_report.md"
```

2. **Run the pipeline**:

```bash
autogbd run --config config.yaml
```

3. **Validate configuration**:

```bash
autogbd validate --config config.yaml
```

## Configuration

The entire harmonization pipeline is controlled through a single `config.yaml` file. See `examples/config.example.yaml` for a complete example with all available options.

### Key Configuration Sections

- **`io`**: Input/output file paths and formats
- **`cleaning`**: Data cleaning rules and parameters
- **`mapping`**: Cause code mapping configuration (direct, fuzzy, AI)
- **`quality`**: Data quality checks and validation rules
- **`reporting`**: Report generation settings

## Workflow

1. **Data Loading**: Loads data from CSV, Excel, or Parquet files
2. **Data Cleaning**: Applies configured cleaning rules (normalization, deduplication, etc.)
3. **Cause Mapping**: Maps source codes to GBD cause list using:
   - Direct mappings from versioned mapping files
   - Fuzzy string matching for close matches
   - AI-assisted suggestions for unmapped codes
4. **Quality Assessment**: Runs quality checks and generates quality scores
5. **Report Generation**: Creates publication-ready markdown report
6. **Provenance Logging**: Records every transformation for reproducibility

## AI-Assisted Mapping

When direct and fuzzy mapping cannot resolve a code, AutoGBD uses transformer models to suggest the most likely GBD causes. Only high-confidence mappings (above threshold) are auto-applied. Low-confidence suggestions are written to `human_review_required.csv` for expert validation.

After human review, the feedback can be used to improve future mappings:

```python
from autogbd.mapping.ai_assistant import AIAssistant

assistant = AIAssistant()
assistant.update_from_review("human_review_required.csv", retrain=False)
```

## Output Files

- **Harmonized Data**: The final analysis-ready dataset
- **Harmonization Report**: Publication-ready markdown report documenting all transformations
- **Provenance Log**: Complete JSON audit trail (`provenance.json`)
- **Human Review File**: CSV file with AI-suggested mappings for expert validation

## Architecture

```
autogbd/
├── core/           # Pipeline orchestrator, config loader, provenance
├── io/             # Data input/output handlers
├── cleaning/       # Data cleaning and normalization rules
├── mapping/        # Vocabulary mapping (direct, fuzzy, AI)
├── quality/        # Data quality assessment
├── reporting/      # Report generation
└── plugins/        # Plugin system for extensibility
```

## Testing

Run the test suite:

```bash
pytest
```

With coverage:

```bash
pytest --cov=autogbd --cov-report=html
```

## Code Quality

Format code:

```bash
black autogbd tests
```

Lint code:

```bash
flake8 autogbd tests
```

## Documentation

Full documentation is available at [https://autogbd.readthedocs.io](https://autogbd.readthedocs.io).

## Contributing

Contributions are welcome! Please see `CONTRIBUTING.md` for guidelines.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Citation

If you use AutoGBD in your research, please cite:

```bibtex
@software{autogbd2024,
  title={AutoGBD: Intelligent Health Data Harmonization Framework},
  author={AutoGBD Team},
  year={2024},
  url={https://github.com/autogbd/autogbd}
}
```

## Support

For questions, issues, or contributions, please visit:
- GitHub Issues: https://github.com/autogbd/autogbd/issues
- Documentation: https://autogbd.readthedocs.io

## Acknowledgments

Built with support from the GBD Collaborative, Google DeepMind, and OpenAI research communities.

