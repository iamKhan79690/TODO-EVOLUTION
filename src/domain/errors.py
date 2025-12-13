"""Custom exception classes for the todo application."""


class TaskError(Exception):
    """Base exception for task-related errors."""

    pass


class TaskNotFound(TaskError):
    """Raised when a task with a specific ID is not found.

    Attributes:
        message -- explanation of the error
    """

    pass


class InvalidTaskDescription(TaskError):
    """Raised when a task description is invalid (empty, too long, etc.).

    Attributes:
        message -- explanation of the error
    """

    pass


class TaskLimitExceeded(TaskError):
    """Raised when attempting to create a task would exceed the maximum task count.

    Attributes:
        message -- explanation of the error
    """

    pass


class InvalidTaskStateTransition(TaskError):
    """Raised when attempting an invalid state change on a task.

    Attributes:
        message -- explanation of the error
    """

    pass
