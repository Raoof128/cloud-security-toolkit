# Contributing to Cloud Security Toolkit

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the Cloud Security Audit & Hardening Toolkit.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/cloud-security-toolkit.git
   cd cloud-security-toolkit
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/Raoof128/cloud-security-toolkit.git
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- AWS CLI (for testing AWS integrations)
- Git

### Installation

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install development dependencies**:
   ```bash
   pip install pytest pytest-cov moto black flake8 mypy
   ```

4. **Verify installation**:
   ```bash
   python -m pytest tests/ -v
   ```

## How to Contribute

### Types of Contributions

We welcome the following types of contributions:

- **Bug fixes** - Fix issues in existing code
- **New features** - Add new cloud providers, scanners, or capabilities
- **Documentation** - Improve README, add examples, write guides
- **Tests** - Increase test coverage, add integration tests
- **Performance** - Optimize scanning speed or memory usage
- **Security** - Improve security checks or remediation

### Contribution Workflow

1. **Check existing issues** - Ensure your contribution isn't already being worked on
2. **Create an issue** (optional but recommended) - Discuss your proposed changes
3. **Create a branch** - Use descriptive names:
   ```bash
   git checkout -b feature/add-rds-scanning
   git checkout -b fix/pagination-bug
   git checkout -b docs/update-installation
   ```
4. **Make your changes** - Follow coding standards
5. **Add tests** - Ensure new code is tested
6. **Run tests** - Verify all tests pass
7. **Commit your changes** - Use clear commit messages
8. **Push to your fork** - Push your branch
9. **Create a Pull Request** - Submit your changes for review

## Coding Standards

### Python Style Guide

- **Follow PEP 8** - Python style guide
- **Use type hints** - Add type annotations (PEP 484)
- **Document functions** - Use docstrings for all public functions
- **Keep functions focused** - Single responsibility principle
- **Maximum line length** - 100 characters

### Code Formatting

We use automated formatting tools:

```bash
# Format code with black
black .

# Check code style with flake8
flake8 .

# Type checking with mypy
mypy scanners/ utils/ remediation/
```

### Example Code Style

```python
from typing import List, Dict, Any

def scan_resources(resource_type: str, region: str = 'us-east-1') -> List[Dict[str, Any]]:
    """
    Scan AWS resources of a specific type.

    Args:
        resource_type (str): Type of resource to scan (e.g., 'ec2', 's3')
        region (str): AWS region to scan (default: us-east-1)

    Returns:
        List[Dict[str, Any]]: List of findings with metadata

    Raises:
        ValueError: If resource_type is not supported
        ClientError: If AWS API call fails
    """
    # Implementation here
    pass
```

### Naming Conventions

- **Variables**: `snake_case`
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private methods**: `_leading_underscore`

## Testing Guidelines

### Writing Tests

- **Test file naming**: `test_<module_name>.py`
- **Test class naming**: `Test<Feature>`
- **Test function naming**: `test_<feature>_<scenario>`

### Test Structure

```python
import pytest
from module import function_to_test

class TestFeatureName:
    """Tests for specific feature"""

    def setup_method(self):
        """Set up test fixtures"""
        self.test_data = {...}

    def test_valid_input(self):
        """Test with valid input"""
        result = function_to_test(self.test_data)
        assert result is not None
        assert result['status'] == 'success'

    def test_invalid_input(self):
        """Test with invalid input"""
        with pytest.raises(ValueError):
            function_to_test(None)
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_validators.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_validators.py::TestS3BucketNameValidation::test_valid_bucket_names
```

### Test Coverage

- Aim for **80%+ code coverage**
- All new features must include tests
- Bug fixes should include regression tests

## Pull Request Process

### Before Submitting

1. ✅ All tests pass locally
2. ✅ Code follows style guidelines
3. ✅ New code has tests
4. ✅ Documentation is updated
5. ✅ CHANGELOG.md is updated
6. ✅ No merge conflicts with main branch

### PR Title Format

Use conventional commit format:

- `feat: Add RDS security scanning`
- `fix: Correct pagination for large S3 accounts`
- `docs: Update installation guide`
- `test: Add tests for remediation module`
- `refactor: Improve risk scoring algorithm`
- `perf: Optimize scanner performance`

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] Tests added/updated
- [ ] All tests passing
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. **Automated checks** - CI/CD runs tests and linters
2. **Code review** - Maintainers review your code
3. **Feedback addressed** - Make requested changes
4. **Approval** - At least one maintainer approves
5. **Merge** - Changes are merged to main branch

## Reporting Bugs

### Before Reporting

- Check existing issues
- Verify it's not a configuration issue
- Test with latest version

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. With configuration '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- Tool version: [e.g., 2.0.0]
- AWS region: [e.g., us-east-1]

**Additional context**
Add any other context, logs, or screenshots.
```

## Suggesting Enhancements

### Enhancement Proposal Template

```markdown
**Feature description**
Clear description of the proposed feature.

**Motivation**
Why is this feature needed? What problem does it solve?

**Proposed solution**
How would this feature work?

**Alternatives considered**
What other approaches did you consider?

**Additional context**
Mockups, examples, or references.
```

## Development Guidelines

### Adding New Cloud Providers

1. Create scanner module: `scanners/<provider>_scanner.py`
2. Create remediation module: `remediation/<provider>_remediation.py`
3. Add configuration: `config/<provider>_config.yaml`
4. Create tests: `tests/test_<provider>_scanner.py`
5. Update documentation
6. Add to README roadmap

### Adding New Security Checks

1. Add check to appropriate scanner module
2. Include compliance mappings (CIS, ASD, NIST)
3. Add corresponding remediation (if applicable)
4. Add tests for new check
5. Update documentation

### Security Considerations

- **Never commit secrets** - Use .gitignore
- **Validate all inputs** - Use validators module
- **Handle credentials securely** - Use AWS credential chain
- **Sanitize outputs** - Avoid exposing sensitive data in logs
- **Test remediation carefully** - Use dry-run mode

## Questions?

If you have questions:
- Open a GitHub Discussion
- Check existing documentation
- Review closed issues for similar questions

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers this project.

## Thank You!

Your contributions help make cloud security more accessible and automated. Thank you for taking the time to contribute!
