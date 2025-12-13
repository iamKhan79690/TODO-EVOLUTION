"""Main entry point for the Console Todo Application."""

import logging
from src.services.task_service import TaskService
from src.ui.cli import TodoCLI


def setup_logging():
    """Set up basic logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main():
    """Main function to run the console todo application."""
    # Set up logging
    setup_logging()

    try:
        # Initialize the task service (with in-memory storage)
        task_service = TaskService()

        # Initialize the CLI interface
        cli = TodoCLI(task_service)

        # Run the application
        cli.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
