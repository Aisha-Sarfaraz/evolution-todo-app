"""
Repository interface abstraction for Task storage.

Implements:
- Dependency Inversion Principle (Constitutional Principle IV)
- Phase II migration path (MemoryRepository → PostgresRepository)

This interface is defined by the Domain layer and implemented by the Storage layer,
enabling clean separation and future database migration.
"""

from abc import ABC, abstractmethod

from src.domain.task import Task


class RepositoryInterface(ABC):
    """
    Abstract repository interface for Task persistence.

    Enables:
    - Phase I: MemoryRepository (dictionary-based)
    - Phase II: PostgresRepository (Neon DB serverless)
    - Future: Any storage backend implementing this interface

    All methods operate on Task domain entities, not storage-specific types.
    """

    @abstractmethod
    def add(self, task: Task) -> None:
        """
        Add a new task to storage.

        Args:
            task: Task entity to store

        Raises:
            ValueError: If task with task.id already exists
        """
        pass

    @abstractmethod
    def get(self, task_id: str) -> Task | None:
        """
        Retrieve a task by ID.

        Args:
            task_id: Task UUID4 string

        Returns:
            Task entity if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all(self) -> list[Task]:
        """
        Retrieve all tasks sorted by created_at DESC (newest first).

        Returns:
            List of Task entities (empty list if no tasks)
        """
        pass

    @abstractmethod
    def update(self, task: Task) -> None:
        """
        Update an existing task in storage.

        Args:
            task: Task entity with updated values

        Raises:
            TaskNotFoundError: If task with task.id not found
        """
        pass

    @abstractmethod
    def delete(self, task_id: str) -> None:
        """
        Delete a task from storage.

        Args:
            task_id: Task UUID4 string

        Raises:
            TaskNotFoundError: If task with task_id not found
        """
        pass

    @abstractmethod
    def exists(self, task_id: str) -> bool:
        """
        Check if a task exists in storage.

        Args:
            task_id: Task UUID4 string

        Returns:
            True if task exists, False otherwise
        """
        pass
