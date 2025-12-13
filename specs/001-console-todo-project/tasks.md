---

description: "Task list for console-based todo application implementation"
---

# Tasks: Console-Based Todo Project

**Input**: Design documents from `/specs/001-console-todo-project/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - included for this project based on constitution requirement for pytest and 80% coverage.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create pyproject.toml with Python 3.13+ requirement and dependencies
- [X] T002 Create directory structure per plan.md (src/, tests/, domain/, services/, ui/)
- [X] T003 [P] Create __init__.py files in all Python directories

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create base Task domain model in src/domain/task.py
- [X] T005 Create base TaskList domain model in src/domain/task_list.py
- [X] T006 Create validation module in src/services/validation.py
- [X] T007 Create Task service interface in src/services/task_service.py
- [X] T008 Create error types in src/domain/errors.py
- [X] T009 Set up pytest configuration and create basic test structure

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add New Todo Items (Priority: P1) 🎯 MVP

**Goal**: Implement the ability to add new todo items through the console interface

**Independent Test**: Can be fully tested by running the application and using the 'add' command to create a new todo item, which should then appear in the todo list.

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Unit test for Task creation in tests/test_domain/test_task.py
- [X] T011 [P] [US1] Unit test for TaskList add_task functionality in tests/test_domain/test_task_list.py
- [X] T012 [P] [US1] Service test for create_task in tests/test_services/test_task_service.py
- [X] T013 [P] [US1] Integration test for adding a task via CLI in tests/test_integration/test_cli_add.py

### Implementation for User Story 1

- [X] T014 [P] [US1] Implement Task domain model with complete(), reopen(), update_description() methods in src/domain/task.py
- [X] T015 [US1] Implement TaskList domain model with all required methods in src/domain/task_list.py
- [X] T016 [US1] Implement Task service create_task method in src/services/task_service.py
- [X] T017 [US1] Implement validation for task descriptions in src/services/validation.py
- [X] T018 [US1] Create CLI module in src/ui/cli.py
- [X] T019 [US1] Implement add task functionality in CLI module
- [X] T020 [US1] Create main.py entry point that integrates all components
- [X] T021 [US1] Add error handling for invalid task descriptions
- [X] T022 [US1] Add logging for task creation operations

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - View Todo Items (Priority: P1)

**Goal**: Implement the ability to view existing todo items through the console interface

**Independent Test**: Can be fully tested by running the application and using the 'list' or 'view' command to display all todo items.

### Tests for User Story 2 ⚠️

- [X] T023 [P] [US2] Unit test for TaskList get_all_tasks(), get_pending_tasks(), get_completed_tasks() methods in tests/test_domain/test_task_list.py
- [X] T024 [P] [US2] Service test for get_all_tasks() in tests/test_services/test_task_service.py
- [X] T025 [P] [US2] Integration test for viewing tasks via CLI in tests/test_integration/test_cli_view.py

### Implementation for User Story 2

- [X] T026 [US2] Implement TaskList get methods (get_all_tasks, get_pending_tasks, get_completed_tasks) in src/domain/task_list.py
- [X] T027 [US2] Implement Task service get methods (get_task, get_all_tasks) in src/services/task_service.py
- [X] T028 [US2] Implement view tasks functionality in CLI module in src/ui/cli.py
- [X] T029 [US2] Create formatters module in src/ui/formatters.py for output formatting
- [X] T030 [US2] Add formatting functions for displaying tasks in src/ui/formatters.py
- [X] T031 [US2] Integrate view functionality with User Story 1 components

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Mark Todo Items as Complete (Priority: P2)

**Goal**: Implement the ability to mark todo items as complete through the console interface

**Independent Test**: Can be fully tested by running the application, using the 'complete' command with an item ID, and verifying the item shows as completed.

### Tests for User Story 3 ⚠️

- [X] T032 [P] [US3] Unit test for Task complete() method in tests/test_domain/test_task.py
- [X] T033 [P] [US3] Unit test for TaskList complete_task() method in tests/test_domain/test_task_list.py
- [X] T034 [P] [US3] Service test for mark_task_complete() in tests/test_services/test_task_service.py
- [X] T035 [P] [US3] Integration test for marking tasks complete via CLI in tests/test_integration/test_cli_complete.py

### Implementation for User Story 3

- [X] T036 [US3] Implement TaskList complete_task() method in src/domain/task_list.py
- [X] T037 [US3] Implement Task service mark_task_complete() method in src/services/task_service.py
- [X] T038 [US3] Implement mark task as complete functionality in CLI module in src/ui/cli.py
- [X] T039 [US3] Add error handling for invalid task IDs in marking complete
- [X] T040 [US3] Add validation to ensure task exists before marking complete
- [X] T041 [US3] Integrate with User Story 1 and 2 components

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: User Story 4 - Delete Todo Items (Priority: P3)

**Goal**: Implement the ability to delete todo items through the console interface

**Independent Test**: Can be fully tested by running the application, using the 'delete' command with an item ID, and verifying the item is removed.

### Tests for User Story 4 ⚠️

- [X] T042 [P] [US4] Unit test for TaskList delete_task() method in tests/test_domain/test_task_list.py
- [X] T043 [P] [US4] Service test for delete_task() in tests/test_services/test_task_service.py
- [X] T044 [P] [US4] Integration test for deleting tasks via CLI in tests/test_integration/test_cli_delete.py

### Implementation for User Story 4

- [X] T045 [US4] Implement TaskList delete_task() method in src/domain/task_list.py
- [X] T046 [US4] Implement Task service delete_task() method in src/services/task_service.py
- [X] T047 [US4] Implement delete task functionality in CLI module in src/ui/cli.py
- [X] T048 [US4] Add error handling for invalid task IDs in deletion
- [X] T049 [US4] Add validation to ensure task exists before deletion
- [X] T050 [US4] Integrate with User Story 1, 2, and 3 components

**Checkpoint**: All user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T051 Create menu system in src/ui/menu.py for console navigation
- [X] T052 [P] Add comprehensive error handling throughout the application
- [X] T053 [P] Add input validation for all user-facing functions
- [X] T054 [P] Add type hints to all public functions and classes
- [X] T055 [P] Implement all edge case handling per spec
- [X] T056 [P] Add documentation for public functions and classes
- [X] T057 [P] Add logging throughout the application
- [X] T058 Run comprehensive tests to ensure 80% coverage requirement
- [X] T059 [P] Run ruff linter and fix all issues
- [X] T060 [P] Run ruff formatter on all code
- [X] T061 Update README.md with project information and setup instructions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US4)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2/US3 but should be independently testable

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Unit test for Task creation in tests/test_domain/test_task.py"
Task: "Unit test for TaskList add_task functionality in tests/test_domain/test_task_list.py"
Task: "Service test for create_task in tests/test_services/test_task_service.py"
Task: "Integration test for adding a task via CLI in tests/test_integration/test_cli_add.py"

# Launch all models for User Story 1 together:
Task: "Implement Task domain model with complete(), reopen(), update_description() methods in src/domain/task.py"
Task: "Implement TaskList domain model with all required methods in src/domain/task_list.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence