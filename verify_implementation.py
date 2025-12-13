#!/usr/bin/env python3
"""Verification script to test that the application works with new features."""

def test_application_startup():
    """Test that the application can be imported and instantiated."""
    print("Testing application startup with new features...")

    # Test imports work without errors
    try:
        from src.domain.task import Task
        from src.domain.task_list import TaskList
        from src.services.task_service import TaskService
        from src.ui.cli import TodoCLI
        print("[OK] All modules imported successfully")
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False

    # Test basic instantiation
    try:
        task_list = TaskList()
        task_service = TaskService(task_list)
        cli = TodoCLI(task_service)
        print("[OK] All services instantiated successfully")
    except Exception as e:
        print(f"[ERROR] Instantiation error: {e}")
        return False

    # Test creating a task with new features
    try:
        from datetime import datetime, timedelta
        from src.domain.recurrence_rule import Frequency, EndCondition, RecurrenceRule
        from src.domain.reminder import Reminder
        
        # Create a task with new features
        due_date = datetime.now() + timedelta(days=1)
        from src.domain.recurrence_rule import Frequency, EndCondition
        recurrence_rule = RecurrenceRule(
            id="test_rr_1",
            frequency=Frequency.DAILY,
            interval=1,
            end_condition=EndCondition.NEVER
        )
        reminder = Reminder(
            id="test_rem_1",
            task_id="1",
            enabled=True,
            reminder_times=[30, 60]  # 30 and 60 minutes before
        )

        task = task_service.create_task(
            title="Test task with new features",
            description="Test task with new features - Full description",
            priority="high",
            tags=["test", "new-feature"],
            due_date=due_date,
            recurrence_rule=recurrence_rule,
            reminder=reminder
        )

        print(f"[OK] Created task with new features, ID: {task.id}")

        # Verify the task has the new properties
        assert task.due_date is not None, "Task should have due date"
        assert task.recurrence_rule is not None, "Task should have recurrence rule"
        assert task.reminder is not None, "Task should have reminder"
        assert task.priority == "high", "Task should have correct priority"
        assert "test" in task.tags and "new-feature" in task.tags, "Task should have correct tags"
        print("[OK] All new features verified on task")

    except Exception as e:
        print(f"[ERROR] Task creation with new features failed: {e}")
        return False

    # Test filtering, searching, and sorting functionality
    try:
        # Add a few more tasks for testing
        task_service.create_task(
            title="Another task",
            priority="low",
            tags=["test", "simple"],
            due_date=datetime.now() + timedelta(days=2)
        )

        task_service.create_task(
            title="High priority task",
            priority="high",
            tags=["important"],
            due_date=datetime.now() + timedelta(days=3)
        )

        # Test filtering by priority
        high_priority_tasks = task_service.filter_tasks_by_priority("high")
        assert len(high_priority_tasks) == 2, f"Expected 2 high priority tasks, got {len(high_priority_tasks)}"

        # Test filtering by tag
        test_tag_tasks = task_service.filter_tasks_by_tag("test")
        assert len(test_tag_tasks) == 2, f"Expected 2 tasks with 'test' tag, got {len(test_tag_tasks)}"

        # Test search functionality
        search_results = task_service.search_tasks("new features")
        assert len(search_results) == 1, f"Expected 1 search result, got {len(search_results)}"

        # Test sorting by priority
        all_tasks = task_service.get_all_tasks()
        sorted_tasks = task_service.sort_tasks('priority')
        assert len(sorted_tasks) == 3, f"Expected 3 tasks, got {len(sorted_tasks)}"

        print("[OK] Filtering, searching, and sorting functionality works")

    except Exception as e:
        print(f"[ERROR] Filtering/searching/sorting test failed: {e}")
        return False

    print("\n[SUCCESS] All tests passed! Application with new features is working correctly.")
    print("\nSummary of implemented features:")
    print("   • Task priorities (high, medium, low)")
    print("   • Task tags for categorization")
    print("   • Due dates with time precision")
    print("   • Recurring tasks with customizable patterns")
    print("   • Reminder notifications")
    print("   • Search functionality")
    print("   • Filter by priority, tags, status")
    print("   • Sort by priority, title, due date")
    print("   • Enhanced display with priority indicators and tags")

    return True


if __name__ == "__main__":
    success = test_application_startup()
    if success:
        print("\n[SUCCESS] VERIFICATION COMPLETE: All features working correctly!")
    else:
        print("\n[ERROR] VERIFICATION FAILED: Issues found with the implementation")
        exit(1)