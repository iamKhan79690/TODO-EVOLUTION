"""Task domain model representing a single todo item."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from .recurrence_rule import RecurrenceRule
from .reminder import Reminder


@dataclass
class Task:
    """Represents a single todo item with its state and metadata.

    Attributes:
        id: Unique identifier for the task
        description: Human-readable description of the task
        is_completed: Completion status (default: False)
        created_at: Timestamp when task was created
        priority: Priority level (high, medium, low) with default 'medium'
        tags: List of tags for categorizing the task
        updated_at: Timestamp when task was last modified
        completed_at: Timestamp when task was completed (if applicable)
        due_date: When the task is due (with time precision)
        notification_sent: Whether a notification has been sent for this task
        recurrence_rule: Defines recurrence pattern for recurring tasks
        reminder: Reminder configuration for the task
    """

    id: int
    description: str
    is_completed: bool = False
    created_at: Optional[datetime] = None
    priority: str = 'medium'
    tags: List[str] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    notification_sent: bool = False
    recurrence_rule: Optional[RecurrenceRule] = None
    reminder: Optional[Reminder] = None

    def __post_init__(self) -> None:
        """Validate the task after initialization."""
        if not self.description or not self.description.strip():
            raise ValueError(
                "Task description cannot be empty or contain only whitespace"
            )

        if len(self.description) > 2000:
            raise ValueError("Task description must be less than 2000 characters")

        if self.created_at is None:
            self.created_at = datetime.now()

        if self.tags is None:
            self.tags = []

        # Validate priority
        valid_priorities = ['high', 'medium', 'low']
        if self.priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")

        # Validate tags
        for tag in self.tags:
            if not (1 <= len(tag) <= 50):
                raise ValueError(f"Each tag must be 1-50 characters: '{tag}'")
            if not tag.replace('-', '').replace('_', '').isalnum():
                raise ValueError(f"Tag '{tag}' contains invalid characters. Only alphanumeric, hyphens, and underscores allowed.")

        if len(self.tags) > 10:
            raise ValueError("Maximum 10 tags allowed per task")

        # Validate due date is in the future if provided
        if self.due_date and self.due_date < datetime.now():
            raise ValueError("Due date must be in the future")

        # Validate recurrence rule
        if self.recurrence_rule and not self.due_date:
            raise ValueError("Due date is required when recurrence rule is set")

    def complete(self) -> None:
        """Mark the task as complete."""
        self.is_completed = True
        self.completed_at = datetime.now()

    def reopen(self) -> None:
        """Mark the task as incomplete."""
        self.is_completed = False
        self.completed_at = None

    def update_description(self, new_description: str) -> None:
        """Update the task description after validation.

        Args:
            new_description: New description for the task

        Raises:
            ValueError: If the new description is invalid
        """
        if not new_description or not new_description.strip():
            raise ValueError(
                "Task description cannot be empty or contain only whitespace"
            )

        if len(new_description) > 2000:
            raise ValueError("Task description must be less than 2000 characters")

        self.description = new_description
        self.updated_at = datetime.now()

    def update_priority(self, new_priority: str) -> None:
        """Update the task priority after validation.

        Args:
            new_priority: New priority for the task (high, medium, or low)

        Raises:
            ValueError: If the priority is invalid
        """
        valid_priorities = ['high', 'medium', 'low']
        if new_priority not in valid_priorities:
            raise ValueError(f"Priority must be one of: {', '.join(valid_priorities)}")

        self.priority = new_priority
        self.updated_at = datetime.now()

    def update_due_date(self, new_due_date: datetime) -> None:
        """Update the task due date after validation.

        Args:
            new_due_date: New due date for the task

        Raises:
            ValueError: If the due date is invalid
        """
        if new_due_date < datetime.now():
            raise ValueError("Due date must be in the future")
        self.due_date = new_due_date
        self.updated_at = datetime.now()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the task after validation.

        Args:
            tag: Tag to add to the task

        Raises:
            ValueError: If the tag is invalid
        """
        if not (1 <= len(tag) <= 50):
            raise ValueError(f"Tag must be 1-50 characters: '{tag}'")
        if not tag.replace('-', '').replace('_', '').isalnum():
            raise ValueError(f"Tag '{tag}' contains invalid characters. Only alphanumeric, hyphens, and underscores allowed.")
        if len(self.tags) >= 10:
            raise ValueError("Maximum 10 tags allowed per task")
        if tag not in self.tags:
            self.tags.append(tag)

        self.updated_at = datetime.now()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the task.

        Args:
            tag: Tag to remove from the task
        """
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()

    def update_tags(self, new_tags: List[str]) -> None:
        """Update the task tags after validation.

        Args:
            new_tags: New list of tags for the task

        Raises:
            ValueError: If any of the tags are invalid
        """
        for tag in new_tags:
            if not (1 <= len(tag) <= 50):
                raise ValueError(f"Tag must be 1-50 characters: '{tag}'")
            if not tag.replace('-', '').replace('_', '').isalnum():
                raise ValueError(f"Tag '{tag}' contains invalid characters. Only alphanumeric, hyphens, and underscores allowed.")

        if len(new_tags) > 10:
            raise ValueError("Maximum 10 tags allowed per task")

        self.tags = new_tags
        self.updated_at = datetime.now()
