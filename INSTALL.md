# Installation Guide

## Quick Installation

### Using Conda Environment

If you're using conda (recommended for this project):

```bash
# Activate your conda environment
conda activate general

# Install core dependencies
pip install -r requirements.txt

# Install with app support (includes Streamlit)
pip install -r requirements-app.txt

# Or install the package in development mode
pip install -e ".[app]"
```

### Using System Python

If using system Python, you may need to use `--user` flag or create a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-app.txt

# Install package
pip install -e ".[app]"
```

## Verify Installation

Check that all dependencies are installed:

```bash
python -c "import pandas, pydantic, yaml, rapidfuzz, typer, rich, streamlit; print('✓ All dependencies installed!')"
```

## Running the Config Builder

After installation:

```bash
# Method 1: Using CLI
autogbd config-builder

# Method 2: Direct Streamlit
streamlit run autogbd/app.py

# Method 3: From project root
cd /home/m-aljasem/projects/AutoGBD
streamlit run autogbd/app.py
```

## Troubleshooting

### ModuleNotFoundError for autogbd

If you get `ModuleNotFoundError: No module named 'autogbd'`:

1. **Install the package:**
   ```bash
   pip install -e .
   ```

2. **Or run from project root:**
   ```bash
   cd /path/to/AutoGBD
   streamlit run autogbd/app.py
   ```

### Missing Dependencies

If you see errors about missing modules (pandas, rapidfuzz, etc.):

```bash
# Install all dependencies
pip install -r requirements.txt
pip install -r requirements-app.txt  # For Streamlit
```

### Conda Environment Issues

Make sure your conda environment is activated:

```bash
# Check active environment
conda env list
conda activate general

# Verify pip is from conda
which pip  # Should show path to conda env pip
```

