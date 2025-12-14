# Release Guide

This guide covers the process for releasing a new version of AutoGBD to PyPI and GitHub.

## Prerequisites

- Python 3.10+
- `twine` installed (`pip install twine`)
- `build` installed (`pip install build`)
- PyPI account with API token
- GitHub repository access

## Release Process

### 1. Prepare the Release

1. **Update version numbers:**
   ```bash
   # Update version in autogbd/__init__.py
   # Update version in pyproject.toml
   # Update CHANGELOG.md
   ```

2. **Run tests:**
   ```bash
   python -m pytest tests/ -v --cov=autogbd
   ```

3. **Update documentation:**
   - Ensure README.md is current
   - Update any examples or documentation

4. **Commit changes:**
   ```bash
   git add .
   git commit -m "Release version X.Y.Z"
   git push origin main
   ```

### 2. Create GitHub Release

1. **Create and push a version tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **Create GitHub release:**
   - Go to GitHub repository
   - Click "Releases" → "Create a new release"
   - Tag: `v1.0.0`
   - Title: `Release v1.0.0`
   - Description: Copy from CHANGELOG.md
   - Publish release

### 3. Publish to PyPI

**Option A: Using the automated script**
```bash
# Set your PyPI API token
export PYPI_API_TOKEN="your_token_here"

# Run the publish script
./scripts/publish.sh
```

**Option B: Manual publishing**
```bash
# Build the package
python -m build

# Check the package
python -m twine check dist/*

# Upload to PyPI
python -m twine upload dist/*
```

### 4. Verify the Release

1. **Check PyPI:**
   - Visit https://pypi.org/project/autogbd/
   - Verify version and metadata

2. **Test installation:**
   ```bash
   pip install autogbd
   autogbd --version
   ```

3. **Check GitHub Actions:**
   - Ensure CI passes
   - Verify publishing workflow succeeded

## Version Numbering

AutoGBD follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., `1.2.3`)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Release Checklist

- [ ] Version updated in `autogbd/__init__.py`
- [ ] Version updated in `pyproject.toml`
- [ ] CHANGELOG.md updated
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] GitHub release created
- [ ] PyPI publishing successful
- [ ] Installation tested
- [ ] Community notified (if applicable)

## Troubleshooting

### PyPI Upload Issues
- Ensure API token has correct permissions
- Check package metadata in `pyproject.toml`
- Verify package builds correctly

### GitHub Actions Issues
- Check workflow YAML syntax
- Ensure secrets are configured correctly
- Verify branch protection rules

### Installation Issues
- Test in clean virtual environment
- Check dependency conflicts
- Verify Python version compatibility

## Security Considerations

- Never commit API tokens or credentials
- Use GitHub secrets for sensitive information
- Regularly rotate API tokens
- Review dependency vulnerabilities