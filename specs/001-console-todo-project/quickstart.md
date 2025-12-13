# Quickstart Guide: Console-Based Todo Project

## Project Setup

### Prerequisites
- Python 3.13+
- UV package manager

### Installation
1. Clone or create the project directory
2. Navigate to the project root
3. Install dependencies using UV:
   ```bash
   uv sync
   ```
4. Verify installation:
   ```bash
   uv run python --version
   ```

## Project Structure
```
.
├── pyproject.toml           # Project configuration and dependencies
├── uv.lock                  # Dependency lock file
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── domain/              # Domain models (dataclasses with business logic)
│   │   ├── __init__.py
│   │   ├── task.py          # Task/TodoItem domain model
│   │   └── task_list.py     # Todo List domain model
│   ├── services/            # Business logic and operations
│   │   ├── __init__.py
│   │   ├── task_service.py  # Task management business logic
│   │   └── validation.py    # Input validation logic
│   └── ui/                  # Console UI layer
│       ├── __init__.py
│       ├── cli.py           # Command-line interface
│       ├── menu.py          # Console menu system
│       └── formatters.py    # Output formatting utilities
└── tests/
    ├── __init__.py
    ├── test_domain/         # Unit tests for domain models
    ├── test_services/       # Unit tests for business services
    └── test_integration/    # Integration tests
```

## Running the Application

### Development
```bash
# Run the application
uv run src/main.py

# Or using Python directly (with virtual environment activated)
python src/main.py
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_domain/test_task.py
```

### Code Quality
```bash
# Lint code
uv run ruff check src tests

# Format code
uv run ruff format src tests
```

## Basic Usage

When you run the application, you'll see a menu with the following options:

1. **Add Task**: Allows you to enter a new task description
2. **View Tasks**: Shows all tasks with their completion status
3. **Complete Task**: Mark a specific task as completed by its ID
4. **Delete Task**: Remove a task by its ID
5. **Exit**: Quit the application

### Sample Commands
- Add a task: Select option 1 and enter "Buy groceries"
- View all tasks: Select option 2 to see your task list
- Complete a task: Select option 3 and enter the task ID
- Delete a task: Select option 4 and enter the task ID

## Development Guidelines

### Adding New Features
1. Update the specification if needed
2. Add tasks to the tasks.md file
3. Write tests before implementation (TDD)
4. Follow the layered architecture (domain → services → ui)
5. Include type hints for all functions
6. Run tests and quality checks before committing

### Code Standards
- Use type hints for all function parameters and return values
- Write docstrings for public functions and classes
- Follow PEP 8 style guide (enforced by ruff)
- Keep functions focused on a single responsibility
- Use descriptive variable and function names

## Quality Assurance

### Testing Requirements
- Minimum 80% code coverage
- All spec acceptance criteria must have corresponding tests
- Unit tests for domain logic
- Integration tests for service layer
- Use descriptive test names (test_should_...)

### Code Quality
- Pass all ruff linting checks
- Maintain clean architecture boundaries
- Use appropriate design patterns
- Keep complexity manageable