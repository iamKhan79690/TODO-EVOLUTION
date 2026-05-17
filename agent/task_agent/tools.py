import os
from supabase import create_client

_supabase = None


def _get_db():
    global _supabase
    if _supabase is None:
        _supabase = create_client(
            os.environ["SUPABASE_URL"],
            os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        )
    return _supabase


def create_task(user_id: str, title: str, priority: str = "medium", description: str = "", due_date: str = "") -> dict:
    """Create a new task for the user.

    Args:
        user_id: The authenticated user's ID.
        title: The task title (required).
        priority: Priority level - one of: low, medium, high, urgent. Defaults to medium.
        description: Optional task description.
        due_date: Optional due date in ISO format (e.g. 2025-01-15T10:00:00Z).

    Returns:
        The created task object.
    """
    row = {
        "user_id": user_id,
        "title": title,
        "priority": priority,
        "status": "pending",
    }
    if description:
        row["description"] = description
    if due_date:
        row["due_date"] = due_date

    result = _get_db().table("tasks").insert(row).execute()
    return result.data[0] if result.data else {"error": "Failed to create task"}


def list_tasks(user_id: str, status: str = "", priority: str = "") -> dict:
    """List all tasks for the user, optionally filtered by status or priority.

    Args:
        user_id: The authenticated user's ID.
        status: Optional filter - one of: pending, in_progress, completed, cancelled, blocked.
        priority: Optional filter - one of: low, medium, high, urgent.

    Returns:
        A dict with 'tasks' list and 'count'.
    """
    query = _get_db().table("tasks").select("*").eq("user_id", user_id).order("created_at", desc=True)

    if status:
        query = query.eq("status", status)
    if priority:
        query = query.eq("priority", priority)

    result = query.execute()
    return {"tasks": result.data, "count": len(result.data)}


def update_task(user_id: str, task_id: str, title: str = "", status: str = "", priority: str = "", description: str = "") -> dict:
    """Update an existing task.

    Args:
        user_id: The authenticated user's ID.
        task_id: The UUID of the task to update.
        title: New title (leave empty to keep current).
        status: New status - one of: pending, in_progress, completed, cancelled, blocked.
        priority: New priority - one of: low, medium, high, urgent.
        description: New description (leave empty to keep current).

    Returns:
        The updated task object.
    """
    updates = {}
    if title:
        updates["title"] = title
    if status:
        updates["status"] = status
        if status == "completed":
            from datetime import datetime, timezone
            updates["completed_at"] = datetime.now(timezone.utc).isoformat()
    if priority:
        updates["priority"] = priority
    if description:
        updates["description"] = description

    if not updates:
        return {"error": "No updates provided"}

    result = (
        _get_db()
        .table("tasks")
        .update(updates)
        .eq("id", task_id)
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0] if result.data else {"error": "Task not found"}


def delete_task(user_id: str, task_id: str) -> dict:
    """Delete a task permanently.

    Args:
        user_id: The authenticated user's ID.
        task_id: The UUID of the task to delete.

    Returns:
        Confirmation message.
    """
    result = (
        _get_db()
        .table("tasks")
        .delete()
        .eq("id", task_id)
        .eq("user_id", user_id)
        .execute()
    )
    if result.data:
        return {"success": True, "message": f"Task '{result.data[0]['title']}' deleted."}
    return {"error": "Task not found"}


def complete_task(user_id: str, task_id: str) -> dict:
    """Mark a task as completed.

    Args:
        user_id: The authenticated user's ID.
        task_id: The UUID of the task to complete.

    Returns:
        The updated task object.
    """
    return update_task(user_id=user_id, task_id=task_id, status="completed")
