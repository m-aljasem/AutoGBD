# AutoGBD Quick Start Guide

## Installation

```bash
# Basic installation
pip install -e .

# With AI features
pip install -e ".[ai]"

# Development installation
pip install -e ".[dev,ai]"
```

## Minimal Example

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

4. **Run the pipeline**:

```bash
autogbd run --config config.yaml
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

