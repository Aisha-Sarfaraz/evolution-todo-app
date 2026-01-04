"""
In-memory dictionary-based repository implementation.

Implements:
- ADR-0001: In-Memory Dictionary Storage for Phase I
- RepositoryInterface abstraction

Storage Strategy:
- Data Structure: Dict[str, Task] (UUID4 string keys → Task objects)
- Sorting: get_all() returns tasks sorted by created_at DESC
- Migration Path: Phase II swaps MemoryRepository → PostgresRepository in main.py
"""

from src.domain.exceptions import TaskNotFoundError
from src.domain.task import Task
from src.storage.repository_interface import RepositoryInterface


class MemoryRepository(RepositoryInterface):
    """
    In-memory dictionary-based storage for Task entities.

    Storage:
        - Internal dictionary: {task.id: Task object}
        - No persistence between sessions
        - Suitable for Phase I console application

    Phase II Migration:
        - Replace with PostgresRepository in main.py
        - Domain layer remains unchanged (zero modification)
    """

    def __init__(self) -> None:
        """Initialize empty in-memory storage."""
        self._storage: dict[str, Task] = {}

    def add(self, task: Task) -> None:
        """
        Add a new task to in-memory storage.

        Args:
            task: Task entity to store

        Raises:
            ValueError: If task with task.id already exists

        Implementation:
            storage[task.id] = task
        """
        if task.id in self._storage:
            raise ValueError(f"Task with ID {task.id} already exists")

        self._storage[task.id] = task

    def get(self, task_id: str) -> Task | None:
        """
        Retrieve a task by ID from in-memory storage.

        Args:
            task_id: Task UUID4 string

        Returns:
            Task entity if found, None otherwise

        Implementation:
            storage.get(task_id)
        """
        return self._storage.get(task_id)

    def get_all(self) -> list[Task]:
        """
        Retrieve all tasks sorted by created_at DESC (newest first).

        Returns:
            List of Task entities (empty list if no tasks)

        Implementation:
            sorted(storage.values(), key=lambda t: t.created_at, reverse=True)
        """
        return sorted(self._storage.values(), key=lambda t: t.created_at, reverse=True)

    def update(self, task: Task) -> None:
        """
        Update an existing task in in-memory storage.

        Args:
            task: Task entity with updated values

        Raises:
            TaskNotFoundError: If task with task.id not found

        Implementation:
            storage[task.id] = task (replaces entire object)
        """
        if task.id not in self._storage:
            raise TaskNotFoundError(f"Task with ID {task.id} not found")

        self._storage[task.id] = task

    def delete(self, task_id: str) -> None:
        """
        Delete a task from in-memory storage.

        Args:
            task_id: Task UUID4 string

        Raises:
            TaskNotFoundError: If task with task_id not found

        Implementation:
            del storage[task_id]
        """
        if task_id not in self._storage:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")

        del self._storage[task_id]

    def exists(self, task_id: str) -> bool:
        """
        Check if a task exists in in-memory storage.

        Args:
            task_id: Task UUID4 string

        Returns:
            True if task exists, False otherwise

        Implementation:
            task_id in storage
        """
        return task_id in self._storage
