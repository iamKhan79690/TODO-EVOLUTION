# CLAUDE.md - Project Constitution for Evolution of Todo (Phase I)

## Project Overview

**Project Name:** Evolution of Todo - Phase I  
**Phase:** I - In-Memory Python Console Application  
**Management Framework:** Spec-Kit Plus  
**Development Methodology:** Spec-Driven Development (SDD)

This is the foundational phase of the Evolution of Todo project, implementing a console-based task management system with in-memory storage. This phase establishes the core domain model and business logic that will evolve through subsequent phases.

---

## Governance Rules

### Core Principle: Spec-First Development

**CRITICAL RULE:** You (Claude) **MUST NOT** write any implementation code until you have read and understood the relevant specification file(s).

### Workflow

1. **Read Before Code:** When asked to implement a feature, always:
   - First, locate and read the relevant specification file in `/specs`
   - Understand the requirements, acceptance criteria, and constraints
   - Clarify any ambiguities with the human before proceeding
   
2. **Verify Spec Existence:** If a specification file does not exist for the requested feature:
   - Inform the human that no spec exists
   - Do NOT proceed with implementation
   - Suggest creating the specification first

3. **Spec Compliance:** All implementation must:
   - Align with the specification requirements
   - Meet all acceptance criteria defined in the spec
   - Follow any technical constraints or patterns specified
   - Include tests that validate the spec requirements

4. **Spec Updates:** If during implementation you discover that:
   - The spec is incomplete or ambiguous
   - Requirements conflict with technical constraints
   - New edge cases are identified
   - **STOP** and discuss with the human before proceeding

### Prohibited Actions

- ❌ Writing code without reading the relevant spec first
- ❌ Assuming requirements without consulting the spec
- ❌ Implementing features that have no specification
- ❌ Deviating from spec requirements without explicit approval

---

## Spec-Kit Structure

### Directory Organization
```
/specs
├── features/          # Feature specifications
│   ├── task-crud.md
│   ├── task-priorities.md
│   ├── task-tags-categories.md
│   ├── task-search-filter.md
│   ├── task-sorting.md
│   ├── task-recurring.md
│   ├── task-due-dates-reminders.md
│   └── ...
├── architecture/      # Architecture decision records
│   ├── domain-model.md
│   └── ...
└── api/              # API contracts (for future phases)
    └── ...
```

### Specification Locations

- **Feature Specs:** `/specs/features/` - User-facing features and functionality
- **Architecture Specs:** `/specs/architecture/` - Technical design decisions and patterns
- **API Specs:** `/specs/api/` - API contracts (reserved for future phases)

### Spec File Naming Convention

- Use kebab-case: `task-crud.md`, `user-authentication.md`
- Be descriptive and specific
- Group related specs in subdirectories when appropriate

---

## Tech Stack

### Core Technologies

- **Language:** Python 3.13+
- **Package Manager:** UV
- **Storage:** In-Memory (Python data structures)
- **Testing Framework:** pytest
- **Code Quality:** ruff (linter & formatter)

### Development Tools

- **UV:** Fast Python package and project manager
- **Type Hints:** Required for all function signatures
- **Dataclasses:** Preferred for domain models

### Dependencies

Managed via `pyproject.toml` and installed through UV:
```toml
[project]
requires-python = ">=3.13"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "ruff"]
```

---

## Commands

### Running the Application
```bash
# Using UV (recommended)
uv run src/main.py

# Using Python directly (ensure virtual environment is activated)
python src/main.py
```

### Testing
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_task_crud.py

# Run tests in verbose mode
uv run pytest -v
```

### Code Quality
```bash
# Lint code
uv run ruff check src tests

# Format code
uv run ruff format src tests

# Type checking (if using mypy)
uv run mypy src
```

### Project Setup
```bash
# Create new project with UV
uv init

# Install dependencies
uv sync

# Add new dependency
uv add <package-name>

# Add development dependency
uv add --dev <package-name>
```

---

## Project Structure
```
evolution-of-todo-phase-1/
├── CLAUDE.md                 # This file - Project Constitution
├── README.md                 # Project documentation
├── pyproject.toml           # Python project configuration
├── uv.lock                  # Dependency lock file
├── specs/                   # Specification files
│   ├── features/
│   │   ├── task-crud.md
│   │   ├── task-priorities.md
│   │   ├── task-tags-categories.md
│   │   ├── task-search-filter.md
│   │   ├── task-sorting.md
│   │   ├── task-recurring.md
│   │   └── task-due-dates-reminders.md
│   ├── architecture/
│   └── api/
├── src/                     # Source code
│   ├── __init__.py
│   ├── main.py             # Application entry point
│   ├── domain/             # Domain models
│   ├── services/           # Business logic
│   ├── scheduler/          # Recurring tasks & reminders
│   └── ui/                 # Console UI
└── tests/                   # Test files
    ├── __init__.py
    ├── test_domain/
    ├── test_services/
    ├── test_scheduler/
    └── test_integration/
```

---

## Feature Roadmap - Phase I

### Core Features (Foundation)

1. **Task CRUD Operations** (`/specs/features/task-crud.md`)
   - Create, Read, Update, Delete tasks
   - Basic task properties: title, description, status, due date

### Intermediate Features (Organization & Usability)

2. **Task Priorities** (`/specs/features/task-priorities.md`)
   - Assign priority levels: High, Medium, Low
   - Visual indicators for priority levels
   - Filter and sort by priority

3. **Tags & Categories** (`/specs/features/task-tags-categories.md`)
   - Assign multiple tags/categories to tasks (e.g., work, home, personal)
   - Manage tag lifecycle (create, rename, delete)
   - Filter tasks by tags/categories

4. **Search & Filter** (`/specs/features/task-search-filter.md`)
   - Search tasks by keyword (title, description)
   - Filter by: status, priority, due date, tags
   - Combine multiple filters
   - Case-insensitive search

5. **Task Sorting** (`/specs/features/task-sorting.md`)
   - Sort by: due date, priority, creation date, alphabetically
   - Ascending/descending order
   - Preserve sort preferences within session

### Advanced Features (Intelligent Automation)

6. **Recurring Tasks** (`/specs/features/task-recurring.md`)
   - Define recurrence patterns: daily, weekly, monthly, yearly, custom
   - Auto-reschedule on completion (e.g., "Weekly team meeting")
   - Recurrence rules: every X days/weeks, specific days of week
   - Skip/postpone individual occurrences
   - End conditions: never, after X occurrences, by date

7. **Due Dates & Time Reminders** (`/specs/features/task-due-dates-reminders.md`)
   - Set precise due dates with time components
   - Configure reminder notifications before due time
   - Multiple reminder options: 15min, 1hr, 1day, 1week before
   - Console-based notification system (Phase I constraint)
   - Overdue task detection and highlighting
   - Snooze reminder functionality

### Future Enhancements (Post Phase I)

- Subtasks and task dependencies
- Task history/audit log
- Bulk operations
- Export/import capabilities
- Browser/system notifications (Phase II+)
- Email reminders (Phase II+)

---

## Development Workflow

### For New Features

1. **Human** creates specification in `/specs/features/[feature-name].md`
2. **Human** requests Claude to implement the feature
3. **Claude** reads the specification file
4. **Claude** asks clarifying questions if needed
5. **Claude** implements the feature according to spec
6. **Claude** writes tests that validate the spec requirements
7. **Human** reviews and provides feedback

### For Bug Fixes

1. Identify which spec is affected
2. Read the spec to understand expected behavior
3. Implement fix that aligns with spec
4. Add regression test

### For Refactoring

1. Ensure specs remain the source of truth
2. Refactor implementation while maintaining spec compliance
3. All tests must continue to pass

---

## Quality Standards

### Code Quality

- ✅ Type hints on all function signatures
- ✅ Docstrings for all public functions and classes
- ✅ Following PEP 8 style guide (enforced by ruff)
- ✅ No unused imports or variables
- ✅ Maximum line length: 100 characters

### Testing Standards

- ✅ Test coverage: Minimum 80%
- ✅ All spec acceptance criteria must have corresponding tests
- ✅ Unit tests for domain logic
- ✅ Integration tests for service layer
- ✅ Use descriptive test names (test_should_...)

### Documentation

- ✅ README.md with project overview and setup instructions
- ✅ Inline comments for complex logic
- ✅ Updated specs when requirements change

---

## Phase I Specific Constraints

### Storage

- **In-Memory Only:** All data stored in Python data structures (lists, dicts)
- **No Persistence:** Data lost on application restart (by design)
- **No Database:** No SQLite, PostgreSQL, or any database system

### User Interface

- **Console Only:** Text-based interface using `input()` and `print()`
- **No GUI:** No web interface, desktop GUI, or TUI libraries
- **Simple Navigation:** Menu-based interaction

### Notifications & Reminders

- **Console-Based Only:** Reminders displayed in console interface
- **No Browser Notifications:** Browser/system notifications reserved for Phase II+
- **No External Services:** No email, SMS, or push notification services
- **Session-Based:** Reminders only active while application is running

### Scope Limitations

- **Single User:** No authentication or multi-user support
- **No Network:** No API, HTTP, or network functionality
- **No External Storage:** No file I/O for task persistence

These constraints will be relaxed in future phases.

---

## Domain Model - Core Entities

### Task Entity

The central entity in Phase I with the following properties:

**Required Properties:**
- `id`: Unique identifier (UUID or auto-increment)
- `title`: Task title (string, max 200 chars)
- `status`: Task status (enum: pending, in_progress, completed)
- `created_at`: Timestamp of creation

**Optional Properties:**
- `description`: Detailed description (string, max 1000 chars)
- `due_date`: Due date with time (datetime, optional)
- `priority`: Priority level (enum: high, medium, low)
- `tags`: List of tags/categories (list of strings)
- `completed_at`: Timestamp when marked complete (optional)
- `updated_at`: Timestamp of last update
- `recurrence_rule`: Recurrence pattern (optional)
- `reminder_settings`: Reminder configuration (optional)

### Priority Levels

- **HIGH:** Urgent and important tasks
- **MEDIUM:** Standard priority (default)
- **LOW:** Nice-to-have tasks

### Task Status

- **PENDING:** Not yet started (default)
- **IN_PROGRESS:** Currently being worked on
- **COMPLETED:** Task finished

### Recurrence Rules

**Frequency Types:**
- `DAILY`: Every day or every X days
- `WEEKLY`: Specific days of the week
- `MONTHLY`: Specific day of month or relative (e.g., first Monday)
- `YEARLY`: Annual recurrence
- `CUSTOM`: Custom interval in days

**Recurrence Properties:**
- `frequency`: Type of recurrence
- `interval`: Number of frequency units (e.g., every 2 weeks)
- `days_of_week`: For weekly recurrence (Mon, Tue, etc.)
- `end_condition`: Never, after X occurrences, or by date

### Reminder Settings

**Reminder Properties:**
- `enabled`: Boolean flag
- `reminder_times`: List of time offsets before due date
  - Examples: 15 minutes, 1 hour, 1 day, 1 week
- `last_triggered`: Timestamp of last reminder
- `snooze_until`: Temporary postponement timestamp

---

## Communication Protocol

### When Claude Needs Clarification

Claude will ask specific questions about:
- Ambiguous requirements in specs
- Missing acceptance criteria
- Edge cases not covered in specs
- Technical trade-offs requiring human decision

### When Human Provides Feedback

Human may:
- Request spec updates before implementation
- Ask for alternative approaches
- Request additional tests or documentation
- Provide clarification on requirements

---

## Success Criteria for Phase I

Phase I is considered complete when:

1. ✅ All feature specs in `/specs/features/` are implemented
2. ✅ Core features: Task CRUD operations working
3. ✅ Intermediate features: Priorities, tags, search/filter, sorting working
4. ✅ Advanced features: Recurring tasks and reminder system working
5. ✅ All tests pass with >80% coverage
6. ✅ Console application runs without errors
7. ✅ Code passes all linting and formatting checks
8. ✅ Documentation is complete and accurate
9. ✅ User can manage tasks efficiently with full feature set
10. ✅ Recurring tasks auto-reschedule correctly
11. ✅ Reminder system alerts users appropriately (console-based)
12. ✅ Ready for transition to Phase II (persistence layer)

---

## Version History

- **v1.2.0** - Added advanced features: recurring tasks, due dates & time reminders
- **v1.1.0** - Added intermediate features: priorities, tags/categories, search/filter, sorting
- **v1.0.0** - Initial constitution for Phase I (In-Memory Python Console App)

---

**Remember:** This constitution is the governance document for this phase. When in doubt, refer back to these rules. The golden rule remains: **Always read the spec before implementing.**