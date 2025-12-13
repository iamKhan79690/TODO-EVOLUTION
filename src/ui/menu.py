"""Console menu system for the todo application."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .cli import TodoCLI


class Menu:
    """Provides menu navigation for the console todo application."""

    def __init__(self) -> None:
        """Initialize the menu system."""
        self.options: dict[str, str] = {
            "1": "Add Task",
            "2": "View Tasks",
            "3": "Complete Task",
            "4": "Delete Task",
            "5": "Search & Filter",
            "6": "Sort Tasks",
            "7": "Exit",
        }

    def display_menu(self) -> None:
        """Display the main menu options."""
        print("\n" + "=" * 30)
        print("MAIN MENU")
        print("=" * 30)
        for key, value in self.options.items():
            print(f"{key}. {value}")
        print("=" * 30)

    def display_search_filter_menu(self) -> None:
        """Display the search & filter submenu options."""
        print("\n" + "=" * 30)
        print("SEARCH & FILTER MENU")
        print("=" * 30)
        print("1. Search by Keyword")
        print("2. Filter by Priority")
        print("3. Filter by Tag")
        print("4. Return to Main Menu")
        print("=" * 30)

    def display_sort_menu(self) -> None:
        """Display the sort submenu options."""
        print("\n" + "=" * 30)
        print("SORT MENU")
        print("=" * 30)
        print("1. Sort by Priority")
        print("2. Sort by Title")
        print("3. Return to Main Menu")
        print("=" * 30)

    def get_user_choice(self) -> str:
        """Get and validate user menu choice."""
        while True:
            try:
                choice = input("Select an option (1-7): ").strip()
                if choice in self.options:
                    return choice
                else:
                    print("Invalid option. Please select 1-7.")
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                return "7"  # Return exit option

    def get_search_filter_choice(self) -> str:
        """Get and validate user search/filter submenu choice."""
        while True:
            try:
                choice = input("Select an option (1-4): ").strip()
                if choice in ["1", "2", "3", "4"]:
                    return choice
                else:
                    print("Invalid option. Please select 1-4.")
            except (EOFError, KeyboardInterrupt):
                return "4"  # Return to main menu

    def get_sort_choice(self) -> str:
        """Get and validate user sort submenu choice."""
        while True:
            try:
                choice = input("Select an option (1-3): ").strip()
                if choice in ["1", "2", "3"]:
                    return choice
                else:
                    print("Invalid option. Please select 1-3.")
            except (EOFError, KeyboardInterrupt):
                return "3"  # Return to main menu

    def execute_choice(self, cli: "TodoCLI", choice: str) -> bool:
        """Execute the action based on user choice.

        Args:
            cli: The TodoCLI instance to execute commands on
            choice: The user's menu choice (1-7)

        Returns:
            True to continue running, False to exit
        """
        if choice == "1":
            cli._add_task()
        elif choice == "2":
            cli._list_tasks()
        elif choice == "3":
            task_id = input("Enter task ID to complete: ").strip()
            try:
                # Validate that it's a number
                int(task_id)
                cli._complete_task(f"complete {task_id}")
            except ValueError:
                print("Task ID must be a number.")
        elif choice == "4":
            task_id = input("Enter task ID to delete: ").strip()
            try:
                # Validate that it's a number
                int(task_id)
                cli._delete_task(f"delete {task_id}")
            except ValueError:
                print("Task ID must be a number.")
        elif choice == "5":
            self._handle_search_filter_menu(cli)
        elif choice == "6":
            self._handle_sort_menu(cli)
        elif choice == "7":
            print("Goodbye!")
            return False  # Indicate to exit
        return True  # Continue running

    def _handle_search_filter_menu(self, cli: "TodoCLI") -> None:
        """Handle the search & filter submenu."""
        while True:
            self.display_search_filter_menu()
            sub_choice = self.get_search_filter_choice()

            if sub_choice == "1":
                keyword = input("Enter keyword to search: ").strip()
                cli._search_tasks(keyword)
            elif sub_choice == "2":
                priority = input("Enter priority to filter (high/medium/low): ").strip().lower()
                if priority in ['high', 'medium', 'low']:
                    cli._filter_tasks_by_priority(priority)
                else:
                    print("Invalid priority. Please enter high, medium, or low.")
            elif sub_choice == "3":
                tag = input("Enter tag to filter: ").strip()
                cli._filter_tasks_by_tag(tag)
            elif sub_choice == "4":
                break  # Return to main menu

    def _handle_sort_menu(self, cli: "TodoCLI") -> None:
        """Handle the sort submenu."""
        while True:
            self.display_sort_menu()
            sub_choice = self.get_sort_choice()

            if sub_choice == "1":
                cli._sort_tasks_by_priority()
            elif sub_choice == "2":
                cli._sort_tasks_by_title()
            elif sub_choice == "3":
                break  # Return to main menu
