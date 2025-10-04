# Contributing to Overpass QL Generator

Thank you for your interest in contributing to the Overpass QL Generator! This document outlines the guidelines and processes for contributing to this project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Code Style](#code-style)
5. [Testing](#testing)
6. [Submitting Changes](#submitting-changes)
7. [Issue Reporting](#issue-reporting)
8. [Pull Request Process](#pull-request-process)
9. [Development Guidelines](#development-guidelines)

## Getting Started

We welcome contributions of all types! Here are some ways you can contribute:

- Report bugs and issues
- Suggest new features or improvements
- Write or improve documentation
- Add new test cases
- Fix bugs
- Implement new features
- Review pull requests from other contributors

Before you start contributing, please take a look at the existing [issues](https://github.com/your-username/overpass-ql-gen/issues) to see if someone else is already working on what you'd like to contribute.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) for package management (recommended) or pip
- Git

### Installation

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR-USERNAME/overpass-ql-gen.git
   cd overpass-ql-gen
   ```

3. Create a virtual environment:
   ```bash
   # Using uv (recommended)
   uv venv
   
   # Or using standard Python
   python -m venv .venv
   ```

4. Activate your virtual environment:
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

5. Install dependencies:
   ```bash
   # Using uv
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

6. Install the project in development mode:
   ```bash
   pip install -e .
   ```

## Project Structure

```
overpass-ql-gen/
├── apps/                    # Application entry points
│   ├── cli/                # CLI application
│   └── web/                # Web application (Streamlit)
├── lib/                    # Core library code
│   └── overpass_ql_generator/
│       ├── __init__.py
│       └── generator.py    # Main generator logic
├── tests/                  # Test files
├── docs/                   # Documentation
├── config.py              # Configuration constants
├── mypy.ini               # MyPy configuration
├── pyproject.toml         # Project configuration
├── README.md
└── CONTRIBUTING.md        # This file
```

## Code Style

### Python

We follow [PEP 8](https://pep8.org/) coding standards with the following specifics:

- Use [Black](https://github.com/psf/black) for code formatting
- Use [Ruff](https://github.com/charliermarsh/ruff) for linting
- Use type hints for all public functions and methods
- Maximum line length is 88 characters (Black default)

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

Example:
```
Add validation system for OSM tags

This commit introduces a new validation system that verifies OSM tags
against the taginfo database. Resolves #12.

Fixes #12
```

## Testing

### Running Tests

To run all tests:

```bash
# Using uv
uv run pytest

# Or directly with Python
python -m pytest
```

To run tests with coverage:

```bash
uv run pytest --cov=lib --cov-report=html
```

### Writing Tests

- Write tests for all new features
- Update existing tests when modifying functionality
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Test both success and failure cases
- Mock external dependencies when necessary

### Test Structure

Tests should be located in the `tests/` directory and mirror the structure of the `lib/` directory:

```
tests/
├── test_generator.py        # Tests for generator.py
└── test_validation.py       # Tests for validation system
```

## Submitting Changes

### 1. Create a Branch

Create a new branch for your feature or bug fix:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

### 2. Make Your Changes

- Follow the code style guidelines
- Write clear, concise commit messages
- Ensure all tests pass
- Add new tests if necessary

### 3. Run Tests and Linting

Before submitting, run:

```bash
# Run all tests
uv run pytest

# Run linter (using ruff)
uv run ruff check .

# Format code (using black)
uv run black .

# Run type checking (using mypy)
uv run mypy lib/
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "Your descriptive commit message"
```

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

## Issue Reporting

When reporting issues, please include:

1. A clear, descriptive title
2. Steps to reproduce the issue
3. Expected behavior
4. Actual behavior
5. Your environment (Python version, OS, etc.)
6. Any relevant logs or error messages

For feature requests, please describe:
1. The problem you're trying to solve
2. Your proposed solution
3. Any alternatives you've considered

## Pull Request Process

1. Ensure your branch is up-to-date with the main branch:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. Create a pull request through the GitHub interface
3. Follow the pull request template (if available)
4. Describe your changes and link to any related issues
5. Ensure all CI checks pass
6. Request review from maintainers
7. Address any feedback from code reviews
8. Wait for approval before merging

### Pull Request Guidelines

- Keep pull requests focused on a single issue/task
- If you need to make multiple unrelated changes, create separate pull requests
- Include tests for new functionality
- Update documentation as needed
- Ensure all tests pass
- Follow the project's code style

## Development Guidelines

### Architecture Principles

1. **Modularity**: Keep components decoupled with clear interfaces
2. **Validation**: All inputs should be validated using Pydantic models
3. **Type Safety**: Use type hints throughout the codebase
4. **Error Handling**: Handle errors gracefully with appropriate exceptions
5. **Maintainability**: Write clean, readable code with appropriate comments

### Key Components

- **Generator**: Core logic to translate natural language to Overpass QL
- **Validation System**: Ensures OSM tags and queries are valid
- **CLI Application**: Command-line interface for the generator
- **Web Application**: Streamlit-based web interface
- **Configuration**: Centralized configuration management

### Security

- Never commit API keys, passwords, or other sensitive information to the repository
- Validate all user inputs to prevent injection attacks
- Use parameterized queries when interacting with external services

## Getting Help

If you need help:

1. Check the existing documentation
2. Look at existing issues and pull requests
3. Create a new issue with the "question" label
4. Contact the maintainers through the appropriate channels

## Recognition

All contributors will be acknowledged in the project's README. Your contributions help make this project better for everyone!

Thank you for contributing to Overpass QL Generator!