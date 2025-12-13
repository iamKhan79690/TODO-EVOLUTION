# Tasks: Task Enhancements

**Input**: Design documents from `/specs/002-task-enhancements/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The feature specification requests test coverage >80%, so test tasks are included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create validation module in src/services/validation.py
- [ ] T002 [P] Update pyproject.toml with any new dependencies if needed
- [ ] T003 [P] Verify existing project structure matches plan

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Update Task model with priority and tags in src/domain/task.py
- [ ] T005 [P] Update TaskList model with search/filter/sort methods in src/domain/task_list.py
- [ ] T006 Update TaskService interface based on contract in src/services/task_service.py
- [ ] T007 [P] Implement validation functions for priority and tags in src/services/validation.py
- [ ] T008 Update task formatter to display priority and tags in src/ui/formatters.py
- [ ] T009 Update main menu to include new options in src/ui/menu.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Assign Priorities to Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can assign priority levels (High, Medium, Low) to tasks when creating or editing, and these priorities are displayed in the task list.

**Independent Test**: User can successfully set priority levels (High, Medium, Low) when creating new tasks or modifying existing ones, and these priorities are displayed in the task list.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Test creating task with priority in tests/test_domain/test_task.py
- [ ] T011 [P] [US1] Test updating task priority in tests/test_domain/test_task.py
- [ ] T012 [P] [US1] Test priority validation in tests/test_services/test_task_service.py
- [ ] T013 [P] [US1] Test CLI prompt for priority in tests/test_integration/test_cli_add.py

### Implementation for User Story 1

- [ ] T014 [P] [US1] Implement priority validation in src/services/validation.py
- [ ] T015 [US1] Update Task model to include priority defaults in src/domain/task.py
- [ ] T016 [US1] Update Task creation with priority in src/services/task_service.py
- [ ] T017 [US1] Update CLI to prompt for priority when adding task in src/ui/cli.py
- [ ] T018 [US1] Update task display format to show priority in src/ui/formatters.py
- [ ] T019 [US1] Test end-to-end priority functionality

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Tag Tasks for Categorization (Priority: P1)

**Goal**: Users can add multiple tags to a task, view tasks by their tags, and manage tags effectively.

**Independent Test**: User can add multiple tags to a task, view tasks by their tags, and manage tags effectively.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T020 [P] [US2] Test creating task with tags in tests/test_domain/test_task.py
- [ ] T021 [P] [US2] Test updating task tags in tests/test_domain/test_task.py
- [ ] T022 [P] [US2] Test tag validation in tests/test_services/test_task_service.py
- [ ] T023 [P] [US2] Test CLI prompt for tags in tests/test_integration/test_cli_add.py

### Implementation for User Story 2

- [ ] T024 [P] [US2] Implement tag validation in src/services/validation.py
- [ ] T025 [US2] Update Task model to handle tags in src/domain/task.py
- [ ] T026 [US2] Update Task creation with tags in src/services/task_service.py
- [ ] T027 [US2] Update CLI to prompt for tags when adding task in src/ui/cli.py
- [ ] T028 [US2] Update task display format to show tags in src/ui/formatters.py
- [ ] T029 [US2] Test end-to-end tagging functionality

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Search Tasks by Keyword (Priority: P2)

**Goal**: Users can enter a keyword and receive a filtered list of tasks that match the keyword in their title or description.

**Independent Test**: User can enter a keyword and receive a filtered list of tasks that match the keyword in their title or description.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T030 [P] [US3] Test keyword search functionality in tests/test_domain/test_task_list.py
- [ ] T031 [P] [US3] Test search service method in tests/test_services/test_task_service.py
- [ ] T032 [P] [US3] Test CLI search interface in tests/test_integration/test_cli_view.py

### Implementation for User Story 3

- [ ] T033 [P] [US3] Implement search method in TaskList in src/domain/task_list.py
- [ ] T034 [US3] Implement search service in TaskService in src/services/task_service.py
- [ ] T035 [US3] Add search option to CLI menu in src/ui/cli.py
- [ ] T036 [US3] Implement search UI in src/ui/cli.py
- [ ] T037 [US3] Test end-to-end search functionality

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all work independently

---

## Phase 6: User Story 4 - Filter Tasks by Priority or Status (Priority: P2)

**Goal**: Users can apply filters to see only tasks matching specific criteria (priority, completion status) and can clear filters to return to full view.

**Independent Test**: User can apply filters to see only tasks matching specific criteria (priority, completion status) and can clear filters to return to full view.

### Tests for User Story 4 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T038 [P] [US4] Test priority filter in tests/test_domain/test_task_list.py
- [ ] T039 [P] [US4] Test status filter in tests/test_domain/test_task_list.py
- [ ] T040 [P] [US4] Test filter service methods in tests/test_services/test_task_service.py
- [ ] T041 [P] [US4] Test CLI filter interface in tests/test_integration/test_cli_view.py

### Implementation for User Story 4

- [ ] T042 [P] [US4] Implement filter methods in TaskList in src/domain/task_list.py
- [ ] T043 [US4] Implement filter services in TaskService in src/services/task_service.py
- [ ] T044 [US4] Add filter option to CLI menu in src/ui/cli.py
- [ ] T045 [US4] Implement filter UI in src/ui/cli.py
- [ ] T046 [US4] Test end-to-end filtering functionality

**Checkpoint**: At this point, User Stories 1, 2, 3 AND 4 should all work independently

---

## Phase 7: User Story 5 - Sort Task List (Priority: P3)

**Goal**: Users can change sorting options to organize tasks by different criteria and can return to default ordering.

**Independent Test**: User can change sorting options to organize tasks by different criteria and can return to default ordering.

### Tests for User Story 5 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T047 [P] [US5] Test priority sorting in tests/test_domain/test_task_list.py
- [ ] T048 [P] [US5] Test title sorting in tests/test_domain/test_task_list.py
- [ ] T049 [P] [US5] Test sort service methods in tests/test_services/test_task_service.py
- [ ] T050 [P] [US5] Test CLI sort interface in tests/test_integration/test_cli_view.py

### Implementation for User Story 5

- [ ] T051 [P] [US5] Implement sort methods in TaskList in src/domain/task_list.py
- [ ] T052 [US5] Implement sort services in TaskService in src/services/task_service.py
- [ ] T053 [US5] Add sort option to CLI menu in src/ui/cli.py
- [ ] T054 [US5] Implement sort UI in src/ui/cli.py
- [ ] T055 [US5] Test end-to-end sorting functionality

**Checkpoint**: At this point, all user stories should be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T056 [P] Update documentation in README.md and specs/
- [ ] T057 Code cleanup and refactoring
- [ ] T058 Performance optimization for search, filter, sort operations
- [ ] T059 [P] Additional unit tests in tests/unit/ (if needed to reach 80% coverage)
- [ ] T060 Security validation (input sanitization)
- [ ] T061 Run quickstart.md validation
- [ ] T062 Integrate all features and test complete workflow

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Domain models before services
- Services before UI components
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Domain models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (if tests requested):
Task: "Test creating task with priority in tests/test_domain/test_task.py"
Task: "Test updating task priority in tests/test_domain/test_task.py"

# Launch all implementation for User Story 1 together:
Task: "Implement priority validation in src/services/validation.py"
Task: "Update Task model to include priority defaults in src/domain/task.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. Complete Phase 4: User Story 2
5. **STOP and VALIDATE**: Test User Stories 1 & 2 independently
6. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 & 2 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 3 → Test independently → Deploy/Demo
4. Add User Story 4 → Test independently → Deploy/Demo
5. Add User Story 5 → Test independently → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
   - Developer E: User Story 5
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