"""Command-line interface for the todo application."""

import sys
from typing import TYPE_CHECKING
from ..services.task_service import TaskService
from .formatters import format_task_list
from .menu import Menu

if TYPE_CHECKING:
    # This import is used by menu.py
    pass


class TodoCLI:
    """Command-line interface for interacting with the todo application.

    Attributes:
        task_service: The TaskService instance used for task operations
        menu: The Menu instance for navigation
    """

    def __init__(self, task_service: TaskService):
        """Initialize the CLI with a task service.

        Args:
            task_service: TaskService instance to use for operations
        """
        self.task_service = task_service
        self.menu = Menu()

    def run(self):
        """Run the main CLI loop."""
        print("Welcome to the Console Todo Application!")

        while True:
            try:
                self.menu.display_menu()
                choice = self.menu.get_user_choice()

                should_continue = self.menu.execute_choice(self, choice)
                if not should_continue:
                    sys.exit(0)

            except KeyboardInterrupt:
                print("\nGoodbye!")
                sys.exit(0)
            except Exception as e:
                print(f"An error occurred: {e}")

    def run_old_style(self):
        """Run the main CLI loop using old command-style interface."""
        print("Available commands: add, list, complete, delete, exit")

        while True:
            try:
                command = input("\nEnter command: ").strip().lower()

                if command == "add":
                    self._add_task()
                elif command == "list":
                    self._list_tasks()
                elif command.startswith("complete "):
                    self._complete_task(command)
                elif command.startswith("delete "):
                    self._delete_task(command)
                elif command == "exit":
                    print("Goodbye!")
                    sys.exit(0)
                else:
                    print(
                        f"Unknown command: {command}. Available: add, list, complete, delete, exit"
                    )

            except KeyboardInterrupt:
                print("\nGoodbye!")
                sys.exit(0)
            except Exception as e:
                print(f"An error occurred: {e}")

    def _add_task(self):
        """Handle adding a new task."""
        try:
            title = input("Enter task title: ").strip()
            if not title:
                print("Task title cannot be empty.")
                return

            description = input("Enter task description (optional, press Enter to skip): ").strip()
            if not description:
                description = title  # Use title as description if no description provided
            else:
                description = f"{title} - {description}"

            # Get priority
            print("Select priority level:")
            print("1. High")
            print("2. Medium (default)")
            print("3. Low")
            priority_choice = input("Enter choice (1-3, default 2): ").strip()

            priority_map = {"1": "high", "2": "medium", "3": "low"}
            priority = priority_map.get(priority_choice, "medium")  # Default to medium

            # Get tags
            tags_input = input("Enter tags (comma-separated, optional): ").strip()
            tags = []
            if tags_input:
                # Split tags and clean them up
                tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

            # Get due date
            from datetime import datetime
            due_date_input = input("Enter due date (YYYY-MM-DD HH:MM, optional, press Enter to skip): ").strip()
            due_date = None
            if due_date_input:
                try:
                    due_date = datetime.strptime(due_date_input, "%Y-%m-%d %H:%M")
                except ValueError:
                    print("Invalid date format. Expected YYYY-MM-DD HH:MM. Proceeding without due date.")
                    due_date = None

            # Ask if this should be a recurring task
            is_recurring = input("Is this a recurring task? (y/n, default n): ").strip().lower() in ['y', 'yes']
            recurrence_rule = None
            if is_recurring:
                print("Select recurrence frequency:")
                print("1. Daily")
                print("2. Weekly")
                print("3. Monthly")
                print("4. Yearly")
                recurrence_choice = input("Enter choice (1-4): ").strip()

                from src.domain.recurrence_rule import Frequency, EndCondition, RecurrenceRule
                frequency_map = {"1": Frequency.DAILY, "2": Frequency.WEEKLY, "3": Frequency.MONTHLY, "4": Frequency.YEARLY}
                if recurrence_choice in frequency_map:
                    frequency = frequency_map[recurrence_choice]

                    # Get recurrence interval
                    try:
                        interval = int(input("Enter interval (e.g., every N days/weeks/etc., default 1): ").strip() or "1")
                    except ValueError:
                        interval = 1

                    # For weekly, get days of week
                    days_of_week = []
                    if frequency == Frequency.WEEKLY:
                        print("Enter days of week (comma-separated, e.g., mon,tue,wed): ")
                        days_input = input().strip().lower()
                        if days_input:
                            days_of_week = [d.strip() for d in days_input.split(",")]

                    # For monthly, get day of month
                    day_of_month = None
                    if frequency == Frequency.MONTHLY:
                        day_input = input("Enter day of month (1-31, default 1): ").strip()
                        if day_input:
                            try:
                                day_of_month = int(day_input)
                            except ValueError:
                                day_of_month = 1

                    # Get end condition
                    print("Select end condition:")
                    print("1. Never (default)")
                    print("2. After N occurrences")
                    print("3. On specific date")
                    end_choice = input("Enter choice (1-3, default 1): ").strip()

                    end_condition = EndCondition.NEVER
                    end_count = None
                    end_date = None
                    if end_choice == "2":
                        end_condition = EndCondition.AFTER_OCCURRENCES
                        try:
                            end_count = int(input("Enter number of occurrences: ").strip())
                        except ValueError:
                            end_count = 1
                    elif end_choice == "3":
                        end_condition = EndCondition.ON_DATE
                        end_date_input = input("Enter end date (YYYY-MM-DD): ").strip()
                        if end_date_input:
                            try:
                                from datetime import date
                                end_date = datetime.strptime(end_date_input, "%Y-%m-%d").date()
                            except ValueError:
                                print("Invalid date format. Defaulting to no end date.")
                                end_date = None

                    # Create the recurrence rule
                    recurrence_rule = RecurrenceRule(
                        id=f"rr_{len(self.task_service.task_list.tasks) + 1}",
                        frequency=frequency,
                        interval=interval,
                        days_of_week=days_of_week,
                        day_of_month=day_of_month,
                        end_condition=end_condition,
                        end_count=end_count,
                        end_date=end_date
                    )

            # Ask if user wants to set reminders
            set_reminder = input("Set reminder for this task? (y/n, default n): ").strip().lower() in ['y', 'yes']
            reminder_settings = None
            if set_reminder and due_date:
                from src.domain.reminder import Reminder
                reminder_times_input = input("Enter reminder times in minutes before due date (comma-separated, e.g., 30,60,1440): ").strip()
                reminder_times = []
                if reminder_times_input:
                    try:
                        reminder_times = [int(t.strip()) for t in reminder_times_input.split(",")]
                    except ValueError:
                        print("Invalid reminder times format. Using no reminders.")

                reminder_settings = Reminder(
                    id=f"rem_{len(self.task_service.task_list.tasks) + 1}",
                    task_id="",  # Will be set later when task is created
                    enabled=True,
                    reminder_times=reminder_times
                )

            task = self.task_service.create_task(title, description, priority, tags, due_date, recurrence_rule, reminder_settings)
            print(f"Task added with ID: {task.id}")
            print(f"Priority: {task.priority}, Tags: {task.tags}")
            if task.due_date:
                print(f"Due date: {task.due_date.strftime('%Y-%m-%d %H:%M')}")
            if task.recurrence_rule:
                print(f"Recurrence: {task.recurrence_rule.frequency.value} every {task.recurrence_rule.interval} {task.recurrence_rule.frequency.value}(s)")
            if task.reminder:
                print(f"Reminders: {task.reminder.reminder_times} minutes before due")
        except Exception as e:
            print(f"Error adding task: {e}")

    def _list_tasks(self):
        """Handle listing all tasks."""
        try:
            tasks = self.task_service.get_all_tasks()

            print("\nYour tasks:")
            if tasks:
                print(format_task_list(tasks))
            else:
                print("No tasks found.")
        except Exception as e:
            print(f"Error listing tasks: {e}")

    def _complete_task(self, command: str):
        """Handle completing a task.

        Args:
            command: Command string in format "complete <task_id>"
        """
        try:
            parts = command.split(" ", 1)
            if len(parts) != 2:
                print("Usage: complete <task_id>")
                return

            task_id_str = parts[1]
            try:
                task_id = int(task_id_str)
            except ValueError:
                print("Task ID must be a number.")
                return

            task = self.task_service.mark_task_complete(task_id)
            print(f"Task {task.id} marked as complete: {task.description}")
        except Exception as e:
            print(f"Error completing task: {e}")

    def _delete_task(self, command: str):
        """Handle deleting a task.

        Args:
            command: Command string in format "delete <task_id>"
        """
        try:
            parts = command.split(" ", 1)
            if len(parts) != 2:
                print("Usage: delete <task_id>")
                return

            task_id_str = parts[1]
            try:
                task_id = int(task_id_str)
            except ValueError:
                print("Task ID must be a number.")
                return

            success = self.task_service.delete_task(task_id)
            if success:
                print(f"Task {task_id} deleted successfully.")
            else:
                print(f"Task {task_id} not found.")
        except Exception as e:
            print(f"Error deleting task: {e}")

    def _search_tasks(self, keyword: str):
        """Handle searching for tasks by keyword."""
        try:
            if not keyword:
                keyword = input("Enter keyword to search for: ").strip()
                if not keyword:
                    print("Search keyword cannot be empty.")
                    return

            tasks = self.task_service.search_tasks(keyword)

            print(f"\nSearch results for '{keyword}':")
            if tasks:
                print(format_task_list(tasks))
            else:
                print("No tasks found matching the keyword.")
        except Exception as e:
            print(f"Error searching tasks: {e}")

    def _filter_tasks_by_priority(self, priority: str = None):
        """Handle filtering tasks by priority."""
        try:
            if not priority:
                priority = input("Enter priority to filter (high/medium/low): ").strip().lower()
                if priority not in ['high', 'medium', 'low']:
                    print("Invalid priority. Please enter high, medium, or low.")
                    return

            tasks = self.task_service.filter_tasks_by_priority(priority)

            print(f"\nTasks with {priority} priority:")
            if tasks:
                print(format_task_list(tasks))
            else:
                print("No tasks found with that priority.")
        except Exception as e:
            print(f"Error filtering tasks by priority: {e}")

    def _filter_tasks_by_tag(self, tag: str = None):
        """Handle filtering tasks by tag."""
        try:
            if not tag:
                tag = input("Enter tag to filter: ").strip()
                if not tag:
                    print("Tag cannot be empty.")
                    return

            tasks = self.task_service.filter_tasks_by_tag(tag)

            print(f"\nTasks with tag '{tag}':")
            if tasks:
                print(format_task_list(tasks))
            else:
                print(f"No tasks found with tag '{tag}'.")
        except Exception as e:
            print(f"Error filtering tasks by tag: {e}")

    def _sort_tasks_by_priority(self):
        """Handle sorting tasks by priority."""
        try:
            tasks = self.task_service.sort_tasks('priority')

            print("\nTasks sorted by priority (High to Low):")
            if tasks:
                print(format_task_list(tasks))
            else:
                print("No tasks found.")
        except Exception as e:
            print(f"Error sorting tasks by priority: {e}")

    def _sort_tasks_by_title(self):
        """Handle sorting tasks by title."""
        try:
            tasks = self.task_service.sort_tasks('title')

            print("\nTasks sorted by title (A to Z):")
            if tasks:
                print(format_task_list(tasks))
            else:
                print("No tasks found.")
        except Exception as e:
            print(f"Error sorting tasks by title: {e}")
