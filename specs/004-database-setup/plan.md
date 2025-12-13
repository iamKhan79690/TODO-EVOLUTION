# Implementation Plan: Database Setup and SQLModel Integration

**Branch**: `004-database-setup` | **Date**: 2025-12-07 | **Spec**: [specs/004-database-setup/spec.md](spec.md)
**Input**: Feature specification from `/specs/004-database-setup/spec.md`

## Summary

Implementation of Neon PostgreSQL database integration with SQLModel for Phase II full-stack todo application. The solution establishes reliable database connectivity with connection pooling, automatic table creation, and environment-based configuration. Research confirms async operations with `asyncpg` driver provide optimal performance for FastAPI applications using serverless PostgreSQL.

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: FastAPI, SQLModel, SQLAlchemy 2.0, asyncpg, pydantic-settings
**Storage**: Neon Serverless PostgreSQL with connection pooling
**Testing**: pytest (Phase III+), manual validation via health endpoints
**Target Platform**: Linux server (development), serverless platforms (production)
**Project Type**: Web application (monorepo with frontend/backend separation)
**Performance Goals**: <200ms database operations, support 50 concurrent connections, 5-second startup
**Constraints**: Serverless environment, connection pool management, graceful error handling
**Scale/Scope**: Production-ready database layer supporting multiple users with task CRUD operations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Database Design & Data Integrity (Section IV) - ✅ PASS
- ✅ Neon Serverless PostgreSQL as single source of truth
- ✅ SQLModel schema definitions as source of truth
- ✅ Foreign key constraints (tasks.user_id → users.id)
- ✅ Auto-managed timestamps (created_at, updated_at)
- ✅ Indexes on query patterns (user_id, completion status)
- ✅ Phase II approach: Direct SQLModel create_all() for MVP

### API Contract & REST Principles (Section V) - ✅ PASS
- ✅ RESTful endpoint design patterns planned
- ✅ User isolation enforced at database level
- ✅ Proper HTTP status codes and JSON responses
- ✅ Pydantic models for request/response validation
- ✅ JWT verification with user_id matching

### Backend Architecture & API Design (Section VII) - ✅ PASS
- ✅ FastAPI best practices followed
- ✅ Modular route handlers planned
- ✅ Database session management with dependency injection
- ✅ Async/await for database operations
- ✅ Auto-generated OpenAPI docs at /docs

### Authentication & Security Framework (Section III) - ✅ PASS
- ✅ User isolation enforced at database level
- ✅ WHERE user_id filtering on all queries
- ✅ SQL injection prevention via SQLModel parameterized queries
- ✅ No API keys in code (environment variables only)

### Testing Strategy (Section XI) - ✅ PASS
- ✅ Manual testing requirements acknowledged
- ✅ Health endpoint implementation planned
- ✅ Database connectivity verification included
- ✅ Error handling testing covered

## Project Structure

### Documentation (this feature)

```text
specs/004-database-setup/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── openapi.yaml     # API contract specification
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── core/
│   │   ├── config.py        # Database configuration and settings
│   │   └── database.py      # Database connection and session management
│   ├── models/
│   │   └── models.py        # SQLModel User and Task definitions
│   ├── api/
│   │   ├── health.py        # Health check endpoints (existing)
│   │   └── tasks.py         # Task CRUD endpoints (future)
│   └── schemas/
│       └── task_schemas.py  # Pydantic request/response models
├── .env                     # Database environment variables
└── requirements.txt         # Python dependencies (updated)

frontend/                   # Existing structure unchanged
└── [current frontend structure]
```

**Structure Decision**: Web application with monorepo architecture. Database layer follows existing Phase II setup with modular backend structure. The database implementation integrates with current FastAPI application structure while maintaining separation of concerns.

## Complexity Tracking

No constitutional violations detected. Implementation follows established patterns and stays within Phase II scope requirements.

## Phase 0: Research Summary

### Database Connection Patterns Research Complete

**Decision**: Async SQLModel with asyncpg driver for optimal FastAPI performance
**Rationale**: Async operations provide better throughput in FastAPI applications, asyncpg is the highest performing PostgreSQL driver, and serverless PostgreSQL benefits from connection pooling optimizations.

**Key Findings**:
- **Connection Pooling**: QueuePool with 20 base connections, 30 max overflow for production
- **Environment Configuration**: Separate sync/async database URLs with SSL requirements
- **Error Handling**: Retry logic with exponential backoff and circuit breaker patterns
- **Performance**: <200ms operations achievable with proper pooling configuration
- **Health Monitoring**: Custom endpoints for pool status and database connectivity

**Implementation Strategy**:
- Use `create_async_engine()` with `postgresql+asyncpg://` connection strings
- Implement dependency injection pattern for session management
- Configure environment-specific pool settings (dev/staging/production)
- Add comprehensive error handling and retry mechanisms
- Create health check endpoints for monitoring database status

**Alternatives Considered**:
- Sync SQLAlchemy operations (rejected for lower performance)
- Direct psycopg2 connections (rejected for lack of async support and ORM features)
- Custom connection management (rejected for maintenance overhead)

## Phase 1: Design Specifications

### Data Model Architecture

The database design follows the constitution's specified schema with User and Task entities:

**Core Entities**:
- **User**: Authentication and profile data (managed by Better Auth)
- **Task**: Todo items with full Phase I feature parity (priority, tags, due dates, recurrence)

**Relationships**:
- One-to-Many: User → Tasks (foreign key constraint enforced)
- Cascading deletes: User deletion removes all associated tasks

**Indexes**:
- Primary keys on id columns
- Index on tasks.user_id for query optimization
- Index on tasks.completed_status for filtering

### API Contract Design

RESTful endpoints following constitution Section V patterns:
- `/api/{user_id}/tasks` - List user's tasks (GET)
- `/api/{user_id}/tasks` - Create new task (POST)
- `/api/{user_id}/tasks/{id}` - Get/update/delete individual task
- JWT verification with user_id matching enforcement
- Standard HTTP status codes and JSON responses

### Environment Configuration

Production-ready configuration with:
- Environment-specific pool settings
- SSL connection requirements
- Application name identification
- Connection timeout and retry parameters
- Comprehensive error logging and monitoring

## Next Steps

The planning phase is complete. Proceed with `/sp.tasks` to generate detailed implementation tasks, or begin implementation with `/sp.implement`.

All constitutional requirements are satisfied and the research confirms the technical approach is optimal for the Phase II full-stack application requirements.
