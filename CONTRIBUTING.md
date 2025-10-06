# Contributing to Ders Dağıtım Programı

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/DolphinLong/dersdagitimprogrami.git
cd dersdagitimprogrami
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests to verify setup:
```bash
pytest tests/ -v
```

## Running the Application

```bash
python main.py
```

For debug mode:
```bash
python main.py --debug
```

## Testing

### Running Tests

Run all tests:
```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_base_scheduler.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=algorithms --cov=database --cov=config --cov-report=html
```

View coverage report:
```bash
# Open htmlcov/index.html in browser
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files as `test_*.py`
- Name test functions as `test_*()`
- Use pytest fixtures from `tests/conftest.py`
- Aim for >80% code coverage

Example test:
```python
def test_my_feature(db_manager):
    """Test description"""
    # Arrange
    scheduler = MyScheduler(db_manager)
    
    # Act
    result = scheduler.do_something()
    
    # Assert
    assert result is not None
    assert len(result) > 0
```

## Code Style

### Python Style Guide

We follow PEP 8 with some modifications:
- Line length: 120 characters
- Use 4 spaces for indentation
- Use double quotes for strings

### Code Formatting

Before committing, format your code:
```bash
# Format with black
black algorithms/ database/ config/

# Sort imports
isort algorithms/ database/ config/
```

### Linting

Run linters:
```bash
# Flake8
flake8 algorithms/ database/ --max-line-length=120

# Pylint
pylint algorithms/ database/
```

## Commit Guidelines

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(scheduler): Add conflict detection to base scheduler

Implemented _detect_conflicts() method in BaseScheduler class
to identify both class and teacher scheduling conflicts.

Closes #123
```

```
fix(database): Resolve memory leak in connection pool

Fixed unclosed database connections by properly implementing
context managers in db_manager.py.
```

## Pull Request Process

1. **Create a branch:**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes:**
   - Write code
   - Add tests
   - Update documentation

3. **Test your changes:**
   ```bash
   pytest tests/ -v
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: Add my new feature"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/my-new-feature
   ```

6. **Create a Pull Request:**
   - Go to GitHub
   - Click "New Pull Request"
   - Fill in the PR template
   - Wait for review

### PR Requirements

- ✅ All tests pass
- ✅ Code is formatted (black, isort)
- ✅ No linting errors
- ✅ Documentation updated
- ✅ Commit messages follow guidelines
- ✅ PR description is clear

## Project Structure

```
dersdagitimprogrami/
├── algorithms/          # Scheduling algorithms
│   ├── base_scheduler.py          # Base class for all schedulers
│   ├── simple_perfect_scheduler.py
│   ├── ultra_aggressive_scheduler.py
│   └── ...
├── database/            # Database layer
│   ├── db_manager.py   # Database operations
│   └── models.py       # Data models
├── ui/                  # User interface
│   ├── main_window.py
│   └── ...
├── config/              # Configuration
│   ├── config_loader.py
│   └── scheduler_config.yaml
├── tests/               # Test suite
│   ├── conftest.py     # Pytest fixtures
│   ├── test_base_scheduler.py
│   └── ...
├── exceptions.py        # Custom exceptions
├── logging_config.py    # Logging setup
├── main.py              # Application entry point
└── requirements.txt     # Dependencies
```

## Key Components

### Algorithms

All scheduling algorithms should:
- Extend `BaseScheduler` class
- Implement `generate_schedule()` method
- Return `List[Dict]` with schedule entries
- Use logging for progress reporting
- Handle errors gracefully

### Database

- Use `db_manager` for all database operations
- Don't use raw SQL queries
- Close connections properly
- Handle transactions

### Testing

- Write tests for new features
- Maintain >70% coverage
- Use fixtures for test data
- Test edge cases

## Common Tasks

### Adding a New Scheduler Algorithm

1. Create new file in `algorithms/`:
```python
# algorithms/my_scheduler.py
from algorithms.base_scheduler import BaseScheduler
import logging

class MyScheduler(BaseScheduler):
    def __init__(self, db_manager, progress_callback=None):
        super().__init__(db_manager, progress_callback)
        self.logger = logging.getLogger(__name__)
    
    def generate_schedule(self):
        self.logger.info("Starting MyScheduler...")
        # Your implementation
        return self.schedule_entries
```

2. Add tests:
```python
# tests/test_my_scheduler.py
def test_my_scheduler(db_manager):
    scheduler = MyScheduler(db_manager)
    schedule = scheduler.generate_schedule()
    assert len(schedule) > 0
```

3. Update documentation

### Adding Configuration Options

1. Edit `config/scheduler_config.yaml`:
```yaml
algorithms:
  my_scheduler:
    enabled: true
    max_iterations: 1000
```

2. Access in code:
```python
from config.config_loader import get_config

config = get_config()
max_iter = config.get('algorithms.my_scheduler.max_iterations', 1000)
```

## Getting Help

- 📖 Read the [Algorithm Analysis Report](ALGORITHM_ANALYSIS_REPORT.md)
- 💬 Open an issue on GitHub
- 📧 Contact the maintainers

## Code of Conduct

- Be respectful and professional
- Help others learn and grow
- Accept constructive criticism
- Focus on what's best for the project

## License

By contributing, you agree that your contributions will be licensed under the project's license.

---

**Thank you for contributing!** 🎉
