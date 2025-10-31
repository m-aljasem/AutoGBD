.PHONY: help install install-dev install-ai test lint format clean build

help:
	@echo "AutoGBD Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  install      - Install AutoGBD with basic dependencies"
	@echo "  install-dev  - Install AutoGBD with development dependencies"
	@echo "  install-ai   - Install AutoGBD with AI dependencies"
	@echo "  test         - Run test suite"
	@echo "  test-cov     - Run tests with coverage report"
	@echo "  lint         - Run linters (flake8)"
	@echo "  format       - Format code with black"
	@echo "  clean        - Remove build artifacts"
	@echo "  build        - Build distribution packages"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-ai:
	pip install -e ".[ai]"

test:
	pytest

test-cov:
	pytest --cov=autogbd --cov-report=html --cov-report=term

lint:
	flake8 autogbd tests

format:
	black autogbd tests

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/

build: clean
	python setup.py sdist bdist_wheel

