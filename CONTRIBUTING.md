# Contributing to AutoGBD

Thank you for your interest in contributing to AutoGBD! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Be patient with questions

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/autogbd.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install in development mode: `pip install -e ".[dev,ai]"`

## Development Workflow

1. Create a branch from `main`: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Write tests for new functionality
4. Ensure all tests pass: `pytest`
5. Run linting: `flake8 autogbd tests`
6. Format code: `black autogbd tests`
7. Commit with clear messages
8. Push and create a Pull Request

## Code Style

- Follow PEP 8 style guide
- Use `black` for code formatting (line length 100)
- Use type hints where appropriate
- Write docstrings in NumPy style
- Maximum line length: 100 characters

## Testing

- Write tests for all new features
- Aim for >90% code coverage
- Tests should be in `tests/` directory
- Use descriptive test names: `test_feature_does_expected_behavior`

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add fuzzy matching for cause codes
fix: Handle missing values in age column
docs: Update README with installation instructions
test: Add tests for mapping engine
refactor: Simplify cleaning rules implementation
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all CI checks pass
4. Request review from maintainers
5. Address any feedback

## Reporting Issues

When reporting bugs or requesting features:

- Use the issue templates
- Provide clear descriptions
- Include reproducible examples
- Mention your environment (OS, Python version, etc.)

## Questions?

Feel free to open an issue for questions or reach out to the maintainers.

Thank you for contributing to AutoGBD!

