# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: pytest (testing), ruff (linting/formatting), uv (package management), croniter (for cron-like recurrence patterns)
**Storage**: In-Memory (Python data structures) - No persistent storage
**Testing**: pytest with >80% test coverage requirement
**Target Platform**: Cross-platform console application (Windows, macOS, Linux)
**Project Type**: Single-project console application with time-based scheduling
**Performance Goals**: Sub-second response for task operations, reminder checks every 30 seconds
**Constraints**: In-memory only storage, console-based UI, single-user application, timer-based scheduling only (no external notification services)
**Scale/Scope**: Individual task management with up to 1000 tasks per session, including recurring tasks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-First Development Compliance
✓ **PASS**: Feature specification exists at `/specs/003-recurring-tasks-due-dates/spec.md` and contains detailed requirements

### Tech Stack Compliance
✓ **PASS**: Using Python 3.13 (matches constitution requirement)
✓ **PASS**: Using pytest for testing (matches constitution requirement)
✓ **PASS**: Using ruff for linting/formatting (matches constitution requirement)
✓ **PASS**: Using uv for package management (matches constitution requirement)

### Storage Constraint Compliance
✓ **PASS**: Feature uses in-memory storage (as required by constitution for Phase I)
✓ **PASS**: No database or persistent storage being implemented (as required)

### UI Constraint Compliance
✓ **PASS**: Implementation will be console-based (as required by constitution)
✓ **PASS**: No GUI or web interface being developed (as required for Phase I)

### Scope Constraint Compliance
✓ **PASS**: Feature is single-user (as required by constitution for Phase I)
✓ **PASS**: No network or API functionality being added (as required for Phase I)

### Domain Model Compliance
✓ **PASS**: Extending existing Task entity (aligns with constitution domain model)
✓ **PASS**: Adding due_date, recurrence_rule, and reminder_settings attributes to Task model (within allowed scope)

### Code Quality Compliance
✓ **PASS**: Will implement with type hints (as required by constitution)
✓ **PASS**: Will follow PEP 8 style (as required by constitution)
✓ **PASS**: Will ensure test coverage >80% (as required by constitution)

### Phase I Notification Constraints
✓ **PASS**: Using console-based notifications only (as required by constitution for Phase I)
✓ **PASS**: No external notification services (as required for Phase I)

## Project Structure

### Documentation (this feature)

```text
specs/003-recurring-tasks-due-dates/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
src/
├── __init__.py
├── main.py              # Application entry point
├── domain/              # Domain models
│   ├── __init__.py
│   ├── task.py          # Extended Task model with due_date, recurrence, reminders
│   ├── task_list.py     # TaskList with time-based operations
│   ├── recurrence_rule.py # Recurrence pattern implementation
│   ├── reminder.py      # Reminder configuration and scheduling
│   └── errors.py        # Domain-specific exceptions
├── services/            # Business logic
│   ├── __init__.py
│   ├── task_service.py  # Task operations with scheduling
│   ├── recurrence_service.py # Recurrence pattern handling
│   ├── reminder_service.py # Reminder scheduling and delivery
│   └── validation.py    # Validation for new fields
├── scheduler/           # Time-based operations (NEW)
│   ├── __init__.py
│   ├── task_scheduler.py # Handles recurring task generation and reminders
│   └── cron_scheduler.py # Cron-like scheduling using croniter
└── ui/                  # Console UI
    ├── __init__.py
    ├── cli.py           # Command-line interface with new features
    ├── menu.py          # Menu implementation with new options
    └── formatters.py    # Display formatting with due dates and reminders
```

### Tests (repository root)

```text
tests/
├── __init__.py
├── conftest.py          # Test configuration
├── test_domain/         # Domain model tests
│   ├── __init__.py
│   ├── test_task.py     # Task model tests with new attributes
│   ├── test_task_list.py # TaskList tests with time-based operations
│   ├── test_recurrence_rule.py # Recurrence pattern tests
│   └── test_reminder.py # Reminder configuration tests
├── test_services/       # Service layer tests
│   ├── __init__.py
│   ├── test_task_service.py # TaskService tests
│   ├── test_recurrence_service.py # RecurrenceService tests
│   └── test_reminder_service.py # ReminderService tests
├── test_scheduler/      # Scheduler tests
│   ├── __init__.py
│   ├── test_task_scheduler.py # TaskScheduler tests
│   └── test_cron_scheduler.py # CronScheduler tests
└── test_integration/    # Integration tests
    ├── __init__.py
    ├── test_cli_add.py       # CLI add functionality tests with due dates/reminders
    ├── test_cli_complete.py  # CLI complete functionality tests with recurring tasks
    └── test_cli_view.py      # CLI view functionality tests with due dates/filtering
```

**Structure Decision**: Single-project console application structure was selected as it aligns with the existing project architecture and the feature requirements for extending task management capabilities. The feature extends the existing domain model with due dates, recurrence patterns, and reminder functionality while adding scheduler components for time-based operations and updating UI components for new functionality.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

## Summary

This plan extends the existing console-based todo application to add due dates with time reminders and recurring tasks that auto-reschedule themselves. The implementation adheres to all Phase I constraints including in-memory storage, console-based UI, and single-user application. The extension maintains backward compatibility with existing functionality while adding the new features as specified.

## Research Findings

All aspects of the feature have been researched and are well-defined through the specification and data model. The implementation approach extends the existing domain model (Task) with new attributes (due_date, recurrence_rule, reminder_settings) and adds new service layer components for handling time-based operations.

The use of croniter library for recurrence pattern processing provides a familiar and powerful way to handle complex recurrence rules, drawing on established cron expression patterns while adapting to the Python context.

## Phase 2 Readiness

The project is ready to proceed to Phase 2 (task breakdown) with `/sp.tasks` command. All design artifacts have been created:
- Data model: `data-model.md`
- API contracts: `contracts/task-service-contract.md`
- Quickstart guide: `quickstart.md`
- Implementation plan: `plan.md` (this file)
