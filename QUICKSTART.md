# AutoGBD Quick Start Guide

## Installation

**Important:** Make sure you're in a conda/virtual environment first!

```bash
# Activate conda environment (if using conda)
conda activate general

# Basic installation
pip install -r requirements.txt
pip install -e .

# With AI features
pip install -r requirements-ai.txt
pip install -e ".[ai]"

# With visual config builder
pip install -r requirements-app.txt
pip install -e ".[app]"

# Development installation (everything)
pip install -r requirements-dev.txt
pip install -r requirements-ai.txt
pip install -r requirements-app.txt
pip install -e ".[dev,ai,app]"
```

**Troubleshooting:** If you get dependency errors, install them first:
```bash
pip install pandas pydantic pyyaml rapidfuzz typer rich streamlit
```

## Creating Your Configuration

### Option 1: Visual Config Builder (Easiest) ⭐

Launch the Streamlit web interface:

```bash
# Method 1: Install and use CLI command (recommended)
pip install -e ".[app]"
autogbd config-builder

# Method 2: Install and run directly
pip install -e ".[app]"
streamlit run autogbd/app.py

# Method 3: Run without installation (from project root)
cd /path/to/AutoGBD
streamlit run autogbd/app.py

# Method 4: Using Make
make install-app
make app
```

This opens a browser interface where you can:
- ✨ Fill out forms instead of writing YAML
- 👀 See live preview of your config
- ✓ Validate before saving
- 📥 Download the config.yaml file

### Option 2: Manual Configuration

1. **Create input data** (`data/input.csv`):

```csv
id,icd10_code,age,sex,deaths
1,A00,45,M,1
2,B20,67,F,2
3,I21,23,M,1
```

2. **Create configuration** (`config.yaml`):

```yaml
io:
  input_file: "data/input.csv"
  output_file: "output/harmonized.csv"
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

reporting:
  enabled: true
  output_file: "harmonization_report.md"
```

3. **Create mapping file** (`mappings/icd10_to_gbd.csv`):

```csv
source_code,target_code
A00,Cholera
B20,HIV/AIDS
I21,Ischemic heart disease
```

## Running the Pipeline

```bash
# Run the harmonization
autogbd run --config config.yaml

# Validate your config first
autogbd validate --config config.yaml

# With verbose output
autogbd run --config config.yaml --verbose
```

## Output Files

After running, you'll get:

- `output/harmonized.csv` - Harmonized data
- `harmonization_report.md` - Methodology report
- `provenance.json` - Complete audit trail
- `human_review_required.csv` - Unmapped codes for review (if any)

## Next Steps

- See `examples/config.example.yaml` for all configuration options
- Read the full `README.md` for detailed documentation
- Check `CONTRIBUTING.md` if you want to contribute
