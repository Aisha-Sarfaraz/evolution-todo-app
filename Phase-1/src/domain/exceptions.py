"""
Domain layer exceptions.

Implements ADR-0002: Exception-Based Error Handling Strategy

Exception hierarchy:
- DomainValidationError: Input validation failures
- DomainStateError: Invalid state transitions
- TaskNotFoundError: Task ID not found in storage
"""


class DomainValidationError(Exception):
    """
    Raised when user input violates domain invariants.

    Trigger scenarios:
    - Title is empty after trimming whitespace
    - Title exceeds 200 characters
    """

    pass


class DomainStateError(Exception):
    """
    Raised when attempting invalid state transition.

    Trigger scenarios:
    - Calling mark_complete() on task with status='complete'
    """

    pass


class TaskNotFoundError(Exception):
    """
    Raised when task ID not found in storage.

    Trigger scenarios:
    - repository.get(invalid_id) returns None
    - User attempts to view/update/complete/delete non-existent task
    """

    pass
