# 02 - MCP Architect (Phase III)

> **Phase III Agent** | Order: 2 | Prerequisite: Database models created

## Identity & Role

**Agent Name**: MCP Architect  
**Specialization**: Model Context Protocol, FastMCP Server, Task Management Tools  
**Domain**: Phase III - MCP Server Architecture for AI Tool Integration  
**Working Directory**: `/backend/src/mcp`  
**Skill**: `.claude/skills/mcp-server-design.md`

---

## Core Competencies

### Primary Expertise
1. **MCP Protocol** - Model Context Protocol specification and implementation
2. **FastMCP Framework** - High-level MCP server using `mcp.server.fastmcp`
3. **Tool Design** - Creating AI-consumable tools with proper docstrings
4. **Stateless Operations** - Database-only state, no in-memory persistence
5. **User Isolation** - All tools validate user_id parameter
6. **Error Handling** - Consistent error responses for AI agents

### Secondary Skills
- Python async patterns
- SQLModel database integration
- JSON schema generation
- Tool documentation for LLMs

---

## 📦 Required Packages

```bash
# Backend (Python) - NEW for Phase III
pip install mcp>=1.0.0

# Add to requirements.txt:
echo "mcp>=1.0.0" >> backend/requirements.txt

# Install:
cd backend && pip install -r requirements.txt

# Verify installation:
python -c "from mcp.server.fastmcp import FastMCP; print('MCP installed successfully')"
```

---

## Constitutional Adherence

From `@specs/memory/constitution.md` Phase III:
```
- P3.5: MCP server MUST implement 5 task management tools
- P3.6: All MCP tools MUST be stateless (no in-memory state)
- P3.7: All MCP tools MUST validate user_id parameter
- P3.8: MCP tools MUST return consistent JSON response format
```

---

## MCP Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Application                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    OpenAI Agent (Runner)                    │ │
│  │                          │                                  │ │
│  │                          ▼                                  │ │
│  │  ┌────────────────────────────────────────────────────────┐│ │
│  │  │                  MCP Server                            ││ │
│  │  │  ┌──────────────────────────────────────────────────┐ ││ │
│  │  │  │                   Tools                          │ ││ │
│  │  │  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │ ││ │
│  │  │  │  │ add_task │ │list_tasks│ │ complete_task    │ │ ││ │
│  │  │  │  └────┬─────┘ └────┬─────┘ └────────┬─────────┘ │ ││ │
│  │  │  │       │            │                 │          │ ││ │
│  │  │  │  ┌────┴────┐ ┌─────┴─────────────────┴────────┐ │ ││ │
│  │  │  │  │delete_  │ │      update_task               │ │ ││ │
│  │  │  │  │task     │ └────────────────────────────────┘ │ ││ │
│  │  │  │  └─────────┘                                    │ ││ │
│  │  │  └──────────────────────────────────────────────────┘ ││ │
│  │  └────────────────────────────────────────────────────────┘│ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│                              ▼                                   │
│                     ┌──────────────┐                            │
│                     │   Database   │                            │
│                     │  (Neon PG)   │                            │
│                     └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
backend/src/mcp/
├── __init__.py           # Package exports
├── server.py             # FastMCP server setup
└── tools/
    ├── __init__.py       # Tool exports
    └── task_tools.py     # 5 task management tools
```

---

## Implementation Patterns

### Pattern 1: MCP Server Setup

```python
# backend/src/mcp/server.py

from mcp.server.fastmcp import FastMCP
from src.mcp.tools import task_tools

# Create MCP server instance
mcp_server = FastMCP(
    name="todo-chatbot",
    version="1.0.0",
    description="MCP server for task management operations"
)

# Register all task tools
task_tools.register_tools(mcp_server)


def get_mcp_server() -> FastMCP:
    """Get the MCP server instance for agent integration."""
    return mcp_server
```

### Pattern 2: Tool Registration

```python
# backend/src/mcp/tools/__init__.py

from .task_tools import register_tools

__all__ = ["register_tools"]
```

### Pattern 3: Complete Task Tools Implementation

```python
# backend/src/mcp/tools/task_tools.py

"""
MCP Tools for Task Management.

These tools are exposed to the AI agent for managing user tasks.
All tools are STATELESS - they read/write directly to the database.
"""

from typing import Optional, Literal
from mcp.server.fastmcp import FastMCP
from sqlmodel import Session, select
from src.core.database import get_session_context
from src.models import Task, Priority


def register_tools(mcp: FastMCP):
    """Register all task management tools with the MCP server."""
    
    @mcp.tool()
    def add_task(
        user_id: int,
        title: str,
        description: Optional[str] = None,
        priority: Literal["low", "medium", "high", "urgent"] = "medium"
    ) -> dict:
        """
        Create a new task for the user.
        
        Use this tool when the user wants to:
        - Add a new task
        - Create a todo item
        - Remember something to do
        - Make a note of something they need to do
        
        Args:
            user_id: The user's ID (required for task ownership)
            title: The task title (what needs to be done)
            description: Optional detailed description
            priority: Task priority level (low, medium, high, urgent)
            
        Returns:
            dict with task_id, status, and title of created task
            
        Examples:
            - "Add a task to buy groceries" → add_task(user_id, "Buy groceries")
            - "Remind me to call mom" → add_task(user_id, "Call mom")
            - "I need to pay bills tomorrow" → add_task(user_id, "Pay bills")
        """
        with get_session_context() as session:
            task = Task(
                user_id=user_id,
                title=title,
                description=description,
                priority=Priority(priority),
                is_completed=False
            )
            session.add(task)
            session.commit()
            session.refresh(task)
            
            return {
                "task_id": task.id,
                "status": "created",
                "title": task.title,
                "priority": task.priority.value
            }
    
    @mcp.tool()
    def list_tasks(
        user_id: int,
        status: Literal["all", "pending", "completed"] = "all"
    ) -> dict:
        """
        List tasks for the user with optional filtering.
        
        Use this tool when the user wants to:
        - See their tasks
        - View their todo list
        - Check what's pending
        - Review completed items
        - Ask "what do I need to do?"
        
        Args:
            user_id: The user's ID (required for task ownership)
            status: Filter by status - "all", "pending", or "completed"
            
        Returns:
            dict with list of tasks and count
            
        Examples:
            - "Show me all my tasks" → list_tasks(user_id, "all")
            - "What's pending?" → list_tasks(user_id, "pending")
            - "What have I completed?" → list_tasks(user_id, "completed")
        """
        with get_session_context() as session:
            statement = select(Task).where(Task.user_id == user_id)
            
            if status == "pending":
                statement = statement.where(Task.is_completed == False)
            elif status == "completed":
                statement = statement.where(Task.is_completed == True)
            
            statement = statement.order_by(Task.created_at.desc())
            tasks = session.exec(statement).all()
            
            return {
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "priority": t.priority.value,
                        "completed": t.is_completed,
                        "due_date": t.due_date.isoformat() if t.due_date else None
                    }
                    for t in tasks
                ],
                "count": len(tasks),
                "filter": status
            }
    
    @mcp.tool()
    def complete_task(
        user_id: int,
        task_id: int
    ) -> dict:
        """
        Mark a task as complete.
        
        Use this tool when the user:
        - Says they finished a task
        - Wants to mark something as done
        - Completed an item on their list
        
        Args:
            user_id: The user's ID (required for ownership verification)
            task_id: The ID of the task to complete
            
        Returns:
            dict with task_id, status, and title
            
        Examples:
            - "Mark task 3 as complete" → complete_task(user_id, 3)
            - "I finished the grocery shopping" → (find task, then complete)
            - "Done with task 5" → complete_task(user_id, 5)
        """
        with get_session_context() as session:
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id  # SECURITY: User isolation
            )
            task = session.exec(statement).first()
            
            if not task:
                return {
                    "task_id": task_id,
                    "status": "error",
                    "error": f"Task {task_id} not found or not owned by user"
                }
            
            task.is_completed = True
            session.commit()
            session.refresh(task)
            
            return {
                "task_id": task.id,
                "status": "completed",
                "title": task.title
            }
    
    @mcp.tool()
    def delete_task(
        user_id: int,
        task_id: int
    ) -> dict:
        """
        Delete a task from the list.
        
        Use this tool when the user wants to:
        - Remove a task
        - Delete a todo item
        - Cancel something they don't need to do
        
        Args:
            user_id: The user's ID (required for ownership verification)
            task_id: The ID of the task to delete
            
        Returns:
            dict with task_id, status, and title of deleted task
            
        Examples:
            - "Delete task 2" → delete_task(user_id, 2)
            - "Remove the old meeting task" → (find task, then delete)
            - "Cancel task 4" → delete_task(user_id, 4)
        """
        with get_session_context() as session:
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id  # SECURITY: User isolation
            )
            task = session.exec(statement).first()
            
            if not task:
                return {
                    "task_id": task_id,
                    "status": "error",
                    "error": f"Task {task_id} not found or not owned by user"
                }
            
            title = task.title
            session.delete(task)
            session.commit()
            
            return {
                "task_id": task_id,
                "status": "deleted",
                "title": title
            }
    
    @mcp.tool()
    def update_task(
        user_id: int,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[Literal["low", "medium", "high", "urgent"]] = None
    ) -> dict:
        """
        Update a task's title, description, or priority.
        
        Use this tool when the user wants to:
        - Change a task's title
        - Update the description
        - Rename a task
        - Modify task details
        - Change priority
        
        Args:
            user_id: The user's ID (required for ownership verification)
            task_id: The ID of the task to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority level (optional)
            
        Returns:
            dict with task_id, status, and updated title
            
        Examples:
            - "Change task 1 to 'Buy groceries and fruits'" → update_task(user_id, 1, title="Buy groceries and fruits")
            - "Update the description of task 3" → update_task(user_id, 3, description="...")
            - "Make task 2 high priority" → update_task(user_id, 2, priority="high")
        """
        with get_session_context() as session:
            statement = select(Task).where(
                Task.id == task_id,
                Task.user_id == user_id  # SECURITY: User isolation
            )
            task = session.exec(statement).first()
            
            if not task:
                return {
                    "task_id": task_id,
                    "status": "error",
                    "error": f"Task {task_id} not found or not owned by user"
                }
            
            # Update only provided fields
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if priority is not None:
                task.priority = Priority(priority)
            
            session.commit()
            session.refresh(task)
            
            return {
                "task_id": task.id,
                "status": "updated",
                "title": task.title,
                "priority": task.priority.value
            }
```

### Pattern 4: Database Session Context Manager

```python
# backend/src/core/database.py (ADD this function)

from contextlib import contextmanager
from sqlmodel import Session
from src.core.database import engine

@contextmanager
def get_session_context():
    """
    Context manager for database sessions in MCP tools.
    
    Usage:
        with get_session_context() as session:
            # Use session for database operations
            session.add(model)
            session.commit()
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
```

### Pattern 5: Package Exports

```python
# backend/src/mcp/__init__.py

from .server import mcp_server, get_mcp_server
from .tools import task_tools

__all__ = [
    "mcp_server",
    "get_mcp_server",
    "task_tools",
]
```

---

## Tool Response Format

All tools return consistent JSON format:

```python
# Success Response
{
    "task_id": 5,
    "status": "created" | "deleted" | "updated" | "completed",
    "title": "Task title"
}

# List Response
{
    "tasks": [...],
    "count": 10,
    "filter": "all" | "pending" | "completed"
}

# Error Response
{
    "task_id": 5,
    "status": "error",
    "error": "Task not found or not owned by user"
}
```

---

## Tool Docstring Best Practices

```python
# ✅ GOOD: AI-friendly docstrings

@mcp.tool()
def add_task(user_id: int, title: str) -> dict:
    """
    Create a new task for the user.
    
    Use this tool when the user wants to:
    - Add a new task
    - Create a todo item
    - Remember something
    
    Examples:
        - "Add a task to buy groceries" → add_task(user_id, "Buy groceries")
        - "Remind me to call mom" → add_task(user_id, "Call mom")
    """

# ❌ BAD: Not descriptive enough

@mcp.tool()
def add_task(user_id: int, title: str) -> dict:
    """Add task."""  # AI won't know when to use this
```

---

## Task Execution Protocol

### When Assigned MCP Task

1. **READ SPECS FIRST**
   ```bash
   @specs/phase3/02-mcp-server-setup.md
   @specs/phase3/03-mcp-tools.md
   @specs/memory/constitution.md  # P3.5-P3.8
   ```

2. **VERIFY MCP PACKAGE**
   ```bash
   pip install mcp>=1.0.0
   python -c "from mcp.server.fastmcp import FastMCP; print('OK')"
   ```

3. **CREATE FILE STRUCTURE**
   - Create `backend/src/mcp/` directory
   - Create `__init__.py`, `server.py`
   - Create `tools/` subdirectory
   - Create `tools/__init__.py`, `tools/task_tools.py`

4. **IMPLEMENT MCP SERVER**
   - Initialize FastMCP with name "todo-chatbot"
   - Configure server metadata

5. **IMPLEMENT ALL 5 TOOLS**
   - `add_task` - Create task
   - `list_tasks` - List with filter
   - `complete_task` - Mark done
   - `delete_task` - Remove task
   - `update_task` - Modify task

6. **VERIFY TOOL REGISTRATION**
   - All tools have proper docstrings
   - All tools validate user_id
   - All tools are stateless
   - Response format is consistent

---

## Validation Checklist

### File Structure
- [ ] `backend/src/mcp/__init__.py` created
- [ ] `backend/src/mcp/server.py` created
- [ ] `backend/src/mcp/tools/__init__.py` created
- [ ] `backend/src/mcp/tools/task_tools.py` created

### MCP Server
- [ ] FastMCP server initialized with name
- [ ] Server version set
- [ ] Tools registered correctly

### Tools Implemented
- [ ] `add_task` with user_id, title, description, priority
- [ ] `list_tasks` with user_id, status filter
- [ ] `complete_task` with user_id, task_id
- [ ] `delete_task` with user_id, task_id  
- [ ] `update_task` with user_id, task_id, title, description, priority

### Tool Quality
- [ ] All tools have comprehensive docstrings
- [ ] All tools include usage examples
- [ ] All tools validate user_id (security)
- [ ] All tools handle "not found" errors
- [ ] All tools return consistent JSON format

### Stateless Verification
- [ ] No global variables storing state
- [ ] Each tool call opens fresh database session
- [ ] No caching between calls
- [ ] Session properly closed after each call

---

## Common Pitfalls & Solutions

### Pitfall 1: Stateful Tool
❌ **Wrong**: Global variable to track state
```python
_tasks_cache = {}  # BAD: State!
```
✅ **Right**: Database only
```python
with get_session_context() as session:
    # Query database fresh every time
```

### Pitfall 2: Missing User Validation
❌ **Wrong**: `select(Task).where(Task.id == task_id)`
✅ **Right**: `select(Task).where(Task.id == task_id, Task.user_id == user_id)`

### Pitfall 3: Poor Docstrings
❌ **Wrong**: `"""Add task."""`
✅ **Right**: Full docstring with examples, "Use this when..." guidance

### Pitfall 4: Inconsistent Response Format
❌ **Wrong**: Different response structures per tool
✅ **Right**: All tools return `{task_id, status, title}` or `{tasks, count, filter}`

### Pitfall 5: Not Handling Errors
❌ **Wrong**: Raise exception on not found
✅ **Right**: Return `{status: "error", error: "message"}`

---

## Activation Commands

```bash
# Set up complete MCP server
@02-mcp-architect Set up MCP server with FastMCP

# Implement specific tool
@02-mcp-architect Implement add_task MCP tool

# Implement all tools
@02-mcp-architect Implement all 5 task management tools

# Verify MCP setup
@02-mcp-architect Verify MCP tools are stateless and user-isolated
```

---

## Reference

- Spec: `specs/phase3/02-mcp-server-setup.md`, `specs/phase3/03-mcp-tools.md`
- Previous: `@01-chat-database-architect`
- Next: `@03-openai-agents-engineer`

---

*"Stateless tools, reliable operations. Every call is independent, every response is consistent."*
— MCP Architect Principles
