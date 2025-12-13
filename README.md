# 📝 EVOLUTION-OF-TODO

A sophisticated Python console application for intelligent task management with priorities, tags, due dates, recurring tasks, and advanced search capabilities.

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/iamKhan79690/EVOLUTION-OF-TODO/actions)

## 🌟 Features

**Core Task Management:**
- Complete CRUD operations with priority levels (High/Medium/Low)
- Custom tagging system and due date tracking
- Recurring tasks with flexible scheduling patterns

**Search & Organization:**
- Keyword search with filtering by priority, tags, and status
- Multi-option sorting (priority, title, due date)
- Console notification system for reminders

**Architecture:**
- Domain-driven design with clean separation of concerns
- In-memory storage (Phase I) with 80%+ test coverage
- Extensible, maintainable codebase

## 🛠️ Installation

**Requirements:** Python 3.13+, UV package manager (recommended)

```bash
# Clone and setup
git clone https://github.com/iamKhan79690/EVOLUTION-OF-TODO.git
cd EVOLUTION-OF-TODO

# Using UV (recommended)
uv sync && uv run src/main.py

# Or using pip
pip install -e . && python src/main.py
```

## 🚀 Usage

The app provides an intuitive menu-driven interface for managing tasks with advanced features:

**Main Operations:** Add, view, complete, delete, search, filter, and sort tasks.

**Task Creation Options:**
- Priority levels (High/Medium/Low)
- Custom tags for categorization
- Due dates with reminder notifications
- Recurring patterns (daily, weekly, monthly, yearly)

**Search & Organization:**
- Keyword search across all task fields
- Filter by priority, tags, or completion status
- Sort by priority, title, or due date

## 🏗️ Architecture

Clean, layered design with domain-driven principles:

**Domain Layer** (`src/domain/`)
- Task models with priority, tags, due dates, and recurrence
- Business rules and domain-specific exceptions

**Services Layer** (`src/services/`)
- Task orchestration and validation logic
- Recurrence and reminder management services

**UI Layer** (`src/ui/`)
- Console interface with menu navigation
- Formatted output with priority indicators

**Testing** (`tests/`)
- 80%+ coverage across domain, service, and integration layers

## 🧪 Testing

80%+ test coverage with comprehensive validation:

```bash
# Run tests
uv run pytest --cov=src --cov-report=term-missing

# Code quality
uv run ruff format src tests && uv run ruff check src tests
```

**Stack:** Python 3.13+, Pytest, Ruff, UV, Croniter

**Structure:** Domain → Services → UI → Tests (clean separation of concerns)

## 👥 Contributing

1. Fork and create a feature branch
2. Make changes with proper testing and documentation
3. Ensure tests pass (`uv run pytest`) and code quality standards
4. Submit a Pull Request

**Standards:** Type hints, docstrings, PEP 8, 80%+ test coverage, descriptive commits

## 🚀 Roadmap

**Current (Phase I):** ✅ Core task management with priorities, tags, due dates, recurring tasks, and search capabilities

**Planned (Phase II):** Persistent storage, enhanced TUI, authentication, export/import

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

<p align="center">Built with ❤️ using Python | © 2025 EVOLUTION-OF-TODO</p>