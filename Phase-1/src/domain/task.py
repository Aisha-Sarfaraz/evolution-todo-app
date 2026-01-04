"""
Task domain entity.

Implements the Task entity with 10 NON-NEGOTIABLE invariants:
1. Title Non-Emptiness
2. Title Length ≤ 200 chars
3. Description Length ≤ 2000 chars (auto-truncate)
4. Status ∈ {"pending", "complete"}
5. State Transition: Only pending → complete (one-way)
6. ID Uniqueness (UUID4)
7. Created Timestamp Immutability
8. Updated Timestamp (auto-update on modifications)
9. Completed Timestamp (set once when complete)
10. Deletion Integrity

Implements ADR-0003: UUID4 for Task Identifiers
Implements ADR-0002: Exception-Based Error Handling
"""

import logging
import uuid
from datetime import datetime
from typing import Literal

from src.domain.exceptions import DomainStateError, DomainValidationError

logger = logging.getLogger(__name__)


class Task:
    """
    Task domain entity representing a single todo item.

    Attributes:
        id: Globally unique identifier (UUID4 string)
        title: Task title (1-200 chars, required)
        description: Task description (0-2000 chars, optional)
        status: Task completion status ("pending" | "complete")
        created_at: Task creation timestamp (immutable)
        updated_at: Last modification timestamp (auto-updated)
        completed_at: Task completion timestamp (set once)
    """

    def __init__(self, title: str, description: str = "") -> None:
        """
        Create a new Task with validation.

        Args:
            title: Task title (required, 1-200 chars after trim)
            description: Task description (optional, auto-truncate at 2000 chars)

        Raises:
            DomainValidationError: If title is empty or > 200 chars after trim

        Invariants enforced:
            - Invariant 1: Title non-empty after trim
            - Invariant 2: Title ≤ 200 chars
            - Invariant 3: Description ≤ 2000 chars (auto-truncate)
            - Invariant 6: UUID4 generated for id
            - Invariant 7: created_at set to current timestamp (immutable)
            - Invariant 8: updated_at set to current timestamp
            - Invariant 9: completed_at = None (pending status)
        """
        # Invariant 1: Trim whitespace
        trimmed_title = title.strip()

        # Invariant 1: Validate non-emptiness
        if not trimmed_title:
            raise DomainValidationError("Title cannot be empty")

        # Invariant 2: Validate length
        if len(trimmed_title) > 200:
            raise DomainValidationError("Title cannot exceed 200 characters")

        # Invariant 3: Auto-truncate description
        if len(description) > 2000:
            logger.warning(f"Description truncated from {len(description)} to 2000 characters")
            description = description[:2000]

        # Invariant 6: Generate UUID4
        self.id: str = str(uuid.uuid4())

        # Set attributes
        self.title: str = trimmed_title
        self.description: str = description
        self.status: Literal["pending", "complete"] = "pending"

        # Invariant 7: Created timestamp (immutable)
        self.created_at: datetime = datetime.now()

        # Invariant 8: Updated timestamp (mutable)
        self.updated_at: datetime = datetime.now()

        # Invariant 9: Completed timestamp (None for pending)
        self.completed_at: datetime | None = None

    def update_title(self, new_title: str) -> None:
        """
        Update task title with validation.

        Args:
            new_title: New title (required, 1-200 chars after trim)

        Raises:
            DomainValidationError: If new_title is empty or > 200 chars after trim

        Invariants enforced:
            - Invariant 1: Title non-empty after trim
            - Invariant 2: Title ≤ 200 chars
            - Invariant 8: updated_at timestamp updated
        """
        # Trim whitespace
        trimmed_title = new_title.strip()

        # Validate non-emptiness
        if not trimmed_title:
            raise DomainValidationError("Title cannot be empty")

        # Validate length
        if len(trimmed_title) > 200:
            raise DomainValidationError("Title cannot exceed 200 characters")

        # Update title and timestamp
        self.title = trimmed_title
        self.updated_at = datetime.now()

    def update_description(self, new_description: str) -> None:
        """
        Update task description with auto-truncation.

        Args:
            new_description: New description (auto-truncate at 2000 chars)

        Invariants enforced:
            - Invariant 3: Description ≤ 2000 chars (auto-truncate)
            - Invariant 8: updated_at timestamp updated
        """
        # Auto-truncate if exceeds 2000 chars
        if len(new_description) > 2000:
            logger.warning(f"Description truncated from {len(new_description)} to 2000 characters")
            new_description = new_description[:2000]

        # Update description and timestamp
        self.description = new_description
        self.updated_at = datetime.now()

    def mark_complete(self) -> None:
        """
        Mark task as complete (one-way state transition).

        Raises:
            DomainStateError: If task is already complete

        Invariants enforced:
            - Invariant 5: State transition only pending → complete (no reverse)
            - Invariant 9: completed_at set once when status becomes complete
        """
        # Validate current status is pending
        if self.status == "complete":
            raise DomainStateError("Task is already complete")

        # Transition state
        self.status = "complete"
        self.completed_at = datetime.now()

        # Note: updated_at is NOT modified (completion is status change, not field modification)

    def to_dict(self) -> dict[str, str | None]:
        """
        Serialize task to dictionary representation.

        Returns:
            Dictionary with all 7 task attributes, timestamps as ISO 8601 strings

        Used for:
            - CLI display formatting
            - Future JSON serialization (Phase II API)
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
