---

description: "Task list for database setup and SQLModel integration implementation"
---

# Tasks: Database Setup and SQLModel Integration

**Input**: Design documents from `/specs/004-database-setup/`
**Prerequisites**: plan.md (completed), spec.md (completed), research.md (completed), data-model.md (completed), contracts/ (completed)

**Tests**: Manual testing via health endpoints and database connectivity verification (per spec.md Section XI)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/` for source code
- **Configuration**: `backend/` for environment files
- **Health endpoints**: `backend/src/api/` (existing structure)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency management

- [X] T001 Verify existing backend structure and Phase II setup
- [X] T002 Install additional database dependencies in backend/requirements.txt
- [X] T003 [P] Update backend/.env with database configuration template

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create database configuration module in backend/src/core/database.py
- [X] T005 [P] Update backend/src/core/config.py with database settings
- [X] T006 [P] Create SQLModel models directory structure in backend/src/models/
- [X] T007 [P] Create schemas directory structure in backend/src/schemas/
- [X] T008 Update backend/main.py with database lifespan management
- [X] T009 Update backend/requirements.txt with final database dependencies

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Database Connection Setup (Priority: P1) 🎯 MVP

**Goal**: Establish reliable connection to PostgreSQL database with connection pooling and error handling

**Independent Test**: Database connection verified by running application and checking successful startup logs, health endpoint shows database connectivity

### Implementation for User Story 1

- [X] T010 [US1] Implement async database engine in backend/src/core/database.py (depends on T004)
- [X] T011 [US1] Implement database session management with dependency injection in backend/src/core/database.py (depends on T010)
- [X] T012 [US1] Add connection pooling configuration with environment-specific settings in backend/src/core/config.py (depends on T005)
- [X] T013 [US1] Implement database connectivity validation in backend/src/core/database.py
- [X] T014 [US1] Add database health check endpoint in backend/src/api/health.py (extends existing health.py)
- [X] T015 [US1] Add connection pool monitoring endpoint in backend/src/api/health.py (extends existing health.py)
- [X] T016 [US1] Implement graceful error handling for connection failures in backend/src/core/database.py
- [X] T017 [US1] Add database operation logging in backend/src/core/database.py
- [X] T018 [US1] Update backend/main.py to integrate database initialization with lifespan (depends on T008)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - User and Task Data Models (Priority: P1)

**Goal**: Define SQLModel data models for Users and Tasks with full Phase I feature parity

**Independent Test**: Models validated by creating database tables and performing basic CRUD operations

### Implementation for User Story 2

- [ ] T019 [P] [US2] Create Priority enum in backend/src/models/models.py
- [ ] T020 [P] [US2] Create RecurrencePattern enum in backend/src/models/models.py
- [ ] T021 [US2] Implement User SQLModel in backend/src/models/models.py (Better Auth compatible)
- [ ] T022 [US2] Implement Task SQLModel in backend/src/models/models.py with full Phase I features (depends on T019, T020, T021)
- [ ] T023 [US2] Add relationship definitions between User and Task models in backend/src/models/models.py (depends on T021, T022)
- [ ] T024 [US2] Implement database table creation function in backend/src/core/database.py (depends on T021, T022)
- [ ] T025 [US2] Add model validation and business logic in backend/src/models/models.py
- [ ] T026 [US2] Create model __init__.py file for proper imports in backend/src/models/__init__.py

**Checkpoint**: At this point, User Story 2 should be fully functional and models ready for use

---

## Phase 5: User Story 3 - Database Table Creation and Validation (Priority: P1)

**Goal**: Automatically create and validate database tables on startup with schema synchronization

**Independent Test**: Table creation verified by checking database schema after application startup

### Implementation for User Story 3

- [ ] T027 [US3] Implement automatic table creation in backend/src/core/database.py (depends on T024)
- [ ] T028 [US3] Add schema validation on application startup in backend/src/core/database.py
- [ ] T029 [US3] Create database migration helper functions in backend/src/core/database.py
- [ ] T030 [US3] Update backend/main.py to call table creation during startup (depends on T018, T027)
- [ ] T031 [US3] Add database initialization logging in backend/main.py
- [ ] T032 [US3] Test database table creation with clean database in Neon console
- [ ] T033 [US3] Verify existing database table compatibility in backend/src/core/database.py

**Checkpoint**: At this point, all user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Production readiness, monitoring, and documentation improvements

- [ ] T034 [P] Update backend/.env.example with complete database configuration
- [ ] T035 [P] Create database environment configuration documentation
- [ ] T036 Add comprehensive error handling for database operations
- [ ] T037 [P] Add performance monitoring for database operations
- [ ] T038 Validate quickstart.md instructions against actual implementation
- [ ] T039 [P] Update API documentation with database endpoints
- [ ] T040 Add database connection testing script in backend/scripts/test_db.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (Connection Setup) → User Story 2 (Models) → User Story 3 (Table Creation)
  - Sequential order required: US1 provides database layer, US2 defines models, US3 creates tables
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Connection setup - Foundation for all database operations
- **User Story 2 (P1)**: Model definitions - Depends on US1 for database connection
- **User Story 3 (P1)**: Table creation - Depends on US1 (connection) and US2 (models)

### Within Each User Story

- Database engine before session management
- Configuration before implementation
- Core implementation before health endpoints
- Testing after implementation

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Model enums in US2 marked [P] can run in parallel
- Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story 2 Implementation

```bash
# Launch model creation in parallel:
Task: "Create Priority enum in backend/src/models/models.py"
Task: "Create RecurrencePattern enum in backend/src/models/models.py"
Task: "Implement User SQLModel in backend/src/models/models.py"

# Once models complete, continue with relationships:
Task: "Implement Task SQLModel in backend/src/models/models.py"
Task: "Add relationship definitions between User and Task models in backend/src/models/models.py"
```

---

## Implementation Strategy

### MVP First (All P1 User Stories)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T009) - **CRITICAL BLOCKER**
3. Complete Phase 3: User Story 1 (T010-T018) - Database Connection
4. Complete Phase 4: User Story 2 (T019-T026) - Data Models
5. Complete Phase 5: User Story 3 (T027-T033) - Table Creation
6. **STOP and VALIDATE**: Test complete database layer
7. Deploy/demo database functionality

### Incremental Delivery

1. Setup + Foundational → Database infrastructure ready
2. Add User Story 1 → Database connection established → Test connectivity
3. Add User Story 2 → Data models defined → Test model creation
4. Add User Story 3 → Tables auto-created → Test full database functionality
5. Each phase adds database capabilities without breaking previous functionality

### Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T009)
2. Once Foundational is done:
   - Developer A: User Story 1 (Connection setup - T010-T018)
   - Developer B: User Story 2 (Models - T019-T026) [waits for US1]
   - Developer C: User Story 3 (Table creation - T027-T033) [waits for US1, US2]
3. Stories complete in sequence but can be planned in parallel

---

## Validation Checkpoints

### After Phase 3 (User Story 1)
- [ ] Application starts without database connection errors
- [ ] Health endpoint shows database connectivity status
- [ ] Connection pool statistics endpoint working
- [ ] Error handling graceful on connection failures

### After Phase 4 (User Story 2)
- [ ] SQLModel classes compile without errors
- [ ] Model relationships properly defined
- [ ] All Phase I features included in Task model
- [ ] User model compatible with Better Auth

### After Phase 5 (User Story 3)
- [ ] Tables automatically created on first startup
- [ ] Database schema matches model definitions
- [ ] Foreign key constraints properly enforced
- [ ] Indexes created for query optimization

### Final Validation
- [ ] Complete database layer functional
- [ ] All constitutional requirements satisfied
- [ ] Performance targets met (<200ms operations)
- [ ] Ready for API endpoint development (next feature)

---

## Success Metrics

- **Database Connection**: Established within 5 seconds of application startup
- **Table Creation**: Automatic on first startup with zero manual intervention
- **Model Completeness**: All Phase I features supported in Task model
- **Performance**: <200ms database operations under normal load
- **Configuration**: Fully externalized through environment variables
- **Error Handling**: Graceful degradation on database failures

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Database setup is foundational for all future API features
- User Story 1, 2, 3 are all P1 priority and must be completed together
- Stop at any checkpoint to validate story independently
- Avoid: missing environment variables, sync database operations, hardcoded credentials