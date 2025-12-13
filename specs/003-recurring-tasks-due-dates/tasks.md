# Tasks: Recurring Tasks & Due Dates

**Input**: Design documents from `/specs/003-recurring-tasks-due-dates/`
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

- [ ] T001 [P] Install croniter dependency with `uv add croniter`
- [ ] T002 [P] Verify existing project structure matches plan
- [ ] T003 Create scheduler directory in src/scheduler/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 [P] Create recurrence_rule model in src/domain/recurrence_rule.py
- [ ] T005 [P] Create reminder model in src/domain/reminder.py
- [ ] T006 [P] Update Task model with due_date, recurrence_rule, reminder in src/domain/task.py
- [ ] T007 [P] Update TaskList model with time-based operations in src/domain/task_list.py
- [ ] T008 [P] Extend validation functions for new fields in src/services/validation.py
- [ ] T009 [P] Update task formatters to display due dates in src/ui/formatters.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Set Due Dates for Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can set due dates and times for tasks so they can track deadlines and stay organized.

**Independent Test**: User can successfully add a due date and time to a task, and the system displays this information appropriately in the task list.

### Tests for User Story 1 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Test creating task with due date in tests/test_domain/test_task.py
- [ ] T011 [P] [US1] Test updating task due date in tests/test_domain/test_task.py
- [ ] T012 [P] [US1] Test due date validation in tests/test_services/test_task_service.py
- [ ] T013 [P] [US1] Test CLI prompt for due date in tests/test_integration/test_cli_add.py

### Implementation for User Story 1

- [ ] T014 [P] [US1] Implement due date validation in src/services/validation.py
- [ ] T015 [US1] Update Task model to handle due dates in src/domain/task.py
- [ ] T016 [US1] Update Task creation with due dates in src/services/task_service.py
- [ ] T017 [US1] Update CLI to prompt for due date when adding task in src/ui/cli.py
- [ ] T018 [US1] Update task display format to show due dates in src/ui/formatters.py
- [ ] T019 [US1] Test end-to-end due date functionality

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Receive Time-Based Reminders (Priority: P1)

**Goal**: Users receive console notifications when tasks are approaching their due date so they don't miss important deadlines.

**Independent Test**: User can set up notifications for a task, and receives console notifications at the specified time.

### Tests for User Story 2 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T020 [P] [US2] Test creating task with reminder in tests/test_domain/test_task.py
- [ ] T021 [P] [US2] Test reminder scheduling in tests/test_services/test_reminder_service.py
- [ ] T022 [P] [US2] Test reminder notification delivery in tests/test_scheduler/test_task_scheduler.py
- [ ] T023 [P] [US2] Test CLI reminder settings in tests/test_integration/test_cli_add.py

### Implementation for User Story 2

- [ ] T024 [P] [US2] Implement reminder service interface in src/services/reminder_service.py
- [ ] T025 [US2] Implement reminder logic in src/services/reminder_service.py
- [ ] T026 [US2] Create TaskScheduler for time-based operations in src/scheduler/task_scheduler.py
- [ ] T027 [US2] Update CLI to prompt for reminder settings in src/ui/cli.py
- [ ] T028 [US2] Integrate reminder scheduling with task creation in src/services/task_service.py
- [ ] T029 [US2] Test end-to-end reminder functionality

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Create Recurring Tasks (Priority: P2)

**Goal**: Users can create recurring tasks that auto-reschedule themselves after completion so they don't have to manually recreate routine tasks.

**Independent Test**: User can create a recurring task with a specified interval, and a new instance of the task appears after the current one is completed.

### Tests for User Story 3 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T030 [P] [US3] Test creating recurring task in tests/test_domain/test_task.py
- [ ] T031 [P] [US3] Test recurring task pattern in tests/test_domain/test_recurrence_rule.py
- [ ] T032 [P] [US3] Test recurrence service logic in tests/test_services/test_recurrence_service.py
- [ ] T033 [P] [US3] Test CLI recurring task interface in tests/test_integration/test_cli_add.py

### Implementation for User Story 3

- [ ] T034 [P] [US3] Implement recurrence service interface in src/services/recurrence_service.py
- [ ] T035 [US3] Implement recurrence pattern logic in src/services/recurrence_service.py
- [ ] T036 [US3] Create RecurringTaskInstance model in src/domain/task.py
- [ ] T037 [US3] Update CLI to prompt for recurrence settings in src/ui/cli.py
- [ ] T038 [US3] Implement recurring task generation in src/scheduler/task_scheduler.py
- [ ] T039 [US3] Test end-to-end recurring task functionality

**Checkpoint**: At this point, User Stories 1, 2 AND 3 should all work independently

---

## Phase 6: User Story 4 - Manage Recurring Task Instances (Priority: P3)

**Goal**: Users can modify or skip individual instances of recurring tasks without affecting the overall pattern so they can handle exceptions to routine schedules.

**Independent Test**: User can skip or modify a specific instance of a recurring task, and the recurrence pattern continues for future instances.

### Tests for User Story 4 (OPTIONAL - only if tests requested) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T040 [P] [US4] Test skipping recurring instance in tests/test_domain/test_task.py
- [ ] T041 [P] [US4] Test modifying recurring instance in tests/test_domain/test_task.py
- [ ] T042 [P] [US4] Test recurrence exception handling in tests/test_scheduler/test_task_scheduler.py
- [ ] T043 [P] [US4] Test CLI recurring instance management in tests/test_integration/test_cli_view.py

### Implementation for User Story 4

- [ ] T044 [P] [US4] Implement recurring instance management in src/domain/task.py
- [ ] T045 [US4] Update recurrence service for instance management in src/services/recurrence_service.py
- [ ] T046 [US4] Add recurring instance options to CLI menu in src/ui/cli.py
- [ ] T047 [US4] Implement instance skip/modification UI in src/ui/cli.py
- [ ] T048 [US4] Update scheduler to handle exceptions in src/scheduler/task_scheduler.py
- [ ] T049 [US4] Test end-to-end recurring instance management

**Checkpoint**: At this point, all user stories should be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T050 [P] Update documentation in README.md and specs/
- [ ] T051 Code cleanup and refactoring
- [ ] T052 Performance optimization for time-based operations
- [ ] T053 [P] Additional unit tests in tests/unit/ (if needed to reach 80% coverage)
- [ ] T054 Security validation (input sanitization for date/time values)
- [ ] T055 Run quickstart.md validation
- [ ] T056 Integrate all features and test complete workflow
- [ ] T057 Update main menu with new options in src/ui/menu.py

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
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Depends on User Story 3 (recurring tasks needed)

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
Task: "Test creating task with due date in tests/test_domain/test_task.py"
Task: "Test updating task due date in tests/test_domain/test_task.py"

# Launch all implementation for User Story 1 together:
Task: "Implement due date validation in src/services/validation.py"
Task: "Update Task model to handle due dates in src/domain/task.py"
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
5. Each story adds value without breaking previous stories

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