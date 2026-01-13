# Contributing Guidelines

Thank you for your interest in contributing to VideoDub! This document provides guidelines for contributing to make the process smooth for everyone.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all contributors.

## Getting Started

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass: `pytest`
6. Run code quality checks: `make check`
7. Commit your changes: `git commit -m 'Add some feature'`
8. Push to your fork: `git push origin feature/your-feature-name`
9. Create a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/VideoDub.git
cd VideoDub

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run code quality checks
make check
```

## Code Style

We follow these coding standards:

- **Formatting**: Black (line length 88)
- **Imports**: isort
- **Linting**: Flake8
- **Type hints**: MyPy (strict mode)
- **Docstrings**: Google style

Run all checks with: `make check`

## Testing

- Write tests for new features
- Ensure existing tests pass: `pytest`
- Maintain test coverage above 80%
- Test on multiple Python versions (3.8+)

## Documentation

- Update docstrings for public APIs
- Add examples for new features
- Update README.md if needed
- Keep CHANGELOG.md up to date

## Pull Request Process

1. Ensure your PR addresses a single issue or feature
2. Include a clear description of changes
3. Reference related issues using `#issue-number`
4. Wait for CI to pass
5. Request review from maintainers
6. Address feedback promptly

## Reporting Issues

When reporting bugs, please include:

- VideoDub version
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Relevant error messages/logs

## Feature Requests

For new features:

1. Check if it's already planned in issues
2. Create a feature request issue
3. Describe the use case clearly
4. Discuss implementation approach

## Questions?

Feel free to ask questions in:
- GitHub Discussions
- Issues (tagged as "question")
- Project maintainers directly

Thank you for contributing to VideoDub!