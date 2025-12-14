#!/bin/bash
# AutoGBD Publishing Script
# This script helps publish AutoGBD to PyPI

set -e

echo "🚀 AutoGBD Publishing Script"
echo "============================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Run this script from the project root."
    exit 1
fi

# Check if version is set correctly
VERSION=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
echo "📦 Publishing AutoGBD version $VERSION"

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

# Build package
echo "🔨 Building package..."
rm -rf dist/
python -m build

# Check package
echo "🔍 Checking package..."
python -m twine check dist/*

# Upload to PyPI (requires PYPI_API_TOKEN environment variable)
echo "📤 Uploading to PyPI..."
python -m twine upload dist/*

echo "✅ Successfully published AutoGBD $VERSION to PyPI!"
echo "📋 Don't forget to:"
echo "   - Create a GitHub release with the same version tag"
echo "   - Update the changelog"
echo "   - Notify the community"