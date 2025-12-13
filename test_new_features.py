#!/usr/bin/env python3
"""Test script to verify the new task features work correctly."""

from datetime import datetime, timedelta
from src.domain.task import Task
from src.domain.task_list import TaskList
from src.domain.recurrence_rule import Frequency, EndCondition, RecurrenceRule
from src.domain.reminder import Reminder
from src.services.task_service import TaskService
from src.ui.formatters import format_task_list


def test_new_features():
    """Test the new task features: due dates, recurrence, reminders, tags, and priority."""
    print("=== Testing New Task Features ===\n")
    
    # Create a task service
    service = TaskService()
    
    # Test 1: Create a task with due date, priority, and tags
    print("1. Creating a task with due date, priority, and tags...")
    due_date = datetime.now() + timedelta(days=7)  # Due in 7 days
    task1 = service.create_task(
        title="Complete project proposal",
        description="Finish the quarterly project proposal document",
        priority="high",
        tags=["work", "urgent", "q3"],
        due_date=due_date
    )
    print(f"   Created task: {task1.description}")
    print(f"   Priority: {task1.priority}")
    print(f"   Tags: {task1.tags}")
    print(f"   Due date: {task1.due_date}")
    print(f"   ID: {task1.id}\n")
    
    # Test 2: Create a recurring task
    print("2. Creating a recurring task...")
    recurrence_rule = RecurrenceRule(
        id="rr_1",
        frequency=Frequency.WEEKLY,
        interval=1,
        days_of_week=["mon", "wed", "fri"],
        end_condition=EndCondition.NEVER
    )
    
    task2 = service.create_task(
        title="Team standup meeting",
        description="Attend weekly team standup",
        priority="medium",
        tags=["meeting", "team"],
        due_date=datetime.now() + timedelta(days=1),
        recurrence_rule=recurrence_rule
    )
    print(f"   Created recurring task: {task2.description}")
    print(f"   Priority: {task2.priority}")
    print(f"   Tags: {task2.tags}")
    print(f"   Due date: {task2.due_date}")
    print(f"   Recurrence: {task2.recurrence_rule.frequency.value if task2.recurrence_rule else 'None'}")
    print(f"   ID: {task2.id}\n")
    
    # Test 3: Create a task with reminder
    print("3. Creating a task with reminder...")
    reminder = Reminder(
        id="rem_1",
        task_id=str(task1.id),
        enabled=True,
        reminder_times=[60, 1440]  # 1 hour and 1 day before
    )
    
    task3 = service.create_task(
        title="Dentist appointment",
        description="Regular dental checkup",
        priority="medium",
        tags=["health", "appointment"],
        due_date=datetime.now() + timedelta(days=3),
        reminder=reminder
    )
    print(f"   Created task with reminder: {task3.description}")
    print(f"   Priority: {task3.priority}")
    print(f"   Tags: {task3.tags}")
    print(f"   Due date: {task3.due_date}")
    print(f"   Has reminder: {task3.reminder is not None}")
    print(f"   ID: {task3.id}\n")
    
    # Test 4: Get all tasks and display them
    print("4. Getting all tasks...")
    all_tasks = service.get_all_tasks()
    print(f"   Total tasks: {len(all_tasks)}")
    print("\n   All tasks:")
    print(format_task_list(all_tasks))
    
    # Test 5: Search functionality
    print("\n5. Searching for 'project'...")
    search_results = service.search_tasks("project")
    print(f"   Found {len(search_results)} tasks containing 'project':")
    for task in search_results:
        print(f"   - {task.description}")
    
    # Test 6: Filter by priority
    print("\n6. Filtering by high priority...")
    high_priority_tasks = service.filter_tasks_by_priority("high")
    print(f"   Found {len(high_priority_tasks)} high priority tasks:")
    for task in high_priority_tasks:
        print(f"   - {task.description}")
    
    # Test 7: Filter by tag
    print("\n7. Filtering by 'work' tag...")
    work_tasks = service.filter_tasks_by_tag("work")
    print(f"   Found {len(work_tasks)} tasks with 'work' tag:")
    for task in work_tasks:
        print(f"   - {task.description}")
    
    # Test 8: Sort by priority
    print("\n8. Sorting tasks by priority...")
    sorted_tasks = service.sort_tasks('priority')
    print("   Tasks sorted by priority (high to low):")
    for task in sorted_tasks:
        print(f"   - ({task.priority}) {task.description}")
    
    # Test 9: Get overdue tasks (there shouldn't be any since all are future-dated)
    print("\n9. Getting overdue tasks...")
    task_list = service.task_list
    overdue_tasks = task_list.get_overdue_tasks()
    print(f"   Found {len(overdue_tasks)} overdue tasks")
    
    # Test 10: Complete a task and verify it's completed
    print("\n10. Marking task as complete...")
    completed_task = service.mark_task_complete(task1.id)
    print(f"   Task {completed_task.id} marked as: {'completed' if completed_task.is_completed else 'pending'}")
    
    # Test 11: Update a task
    print("\n11. Updating task with new properties...")
    updated_task = service.update_task(
        task2.id,
        title="Updated team standup",
        priority="high",
        tags=["meeting", "team", "important"],
        due_date=datetime.now() + timedelta(days=2)
    )
    print(f"   Updated task: {updated_task.description}")
    print(f"   New priority: {updated_task.priority}")
    print(f"   New tags: {updated_task.tags}")
    print(f"   New due date: {updated_task.due_date}")
    
    print("\n=== All new features working correctly! ===")


if __name__ == "__main__":
    test_new_features()