"""
Unit tests for MemoryRepository storage implementation.

Tests cover:
- T020: MemoryRepository add operation
- T021: MemoryRepository get operations (get, get_all)
- T022: MemoryRepository update and delete operations

TDD Phase: RED - These tests MUST FAIL before implementation
"""

import pytest
from src.domain.task import Task
from src.storage.memory_repository import MemoryRepository
from src.domain.exceptions import TaskNotFoundError


class TestMemoryRepositoryAdd:
    """Test MemoryRepository.add() operation (T020)"""

    def test_add_task_stores_task_with_uuid_key(self):
        """add() stores task using task.id as dictionary key"""
        repo = MemoryRepository()
        task = Task(title="Test task")

        repo.add(task)

        # Verify task is stored
        stored_task = repo.get(task.id)
        assert stored_task is not None
        assert stored_task.id == task.id
        assert stored_task.title == "Test task"

    def test_add_duplicate_task_id_raises_error(self):
        """add() with duplicate task.id raises ValueError"""
        repo = MemoryRepository()
        task = Task(title="Test task")

        repo.add(task)

        # Attempt to add same task again
        with pytest.raises(ValueError, match="Task with ID .* already exists"):
            repo.add(task)

    def test_add_updates_internal_dictionary(self):
        """add() updates internal storage dictionary"""
        repo = MemoryRepository()
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")

        repo.add(task1)
        repo.add(task2)

        # Verify both tasks stored
        all_tasks = repo.get_all()
        assert len(all_tasks) == 2
        assert any(t.id == task1.id for t in all_tasks)
        assert any(t.id == task2.id for t in all_tasks)


class TestMemoryRepositoryGet:
    """Test MemoryRepository.get() and get_all() operations (T021)"""

    def test_get_returns_task_if_exists(self):
        """get(task_id) returns task if it exists in storage"""
        repo = MemoryRepository()
        task = Task(title="Test task")
        repo.add(task)

        retrieved_task = repo.get(task.id)

        assert retrieved_task is not None
        assert retrieved_task.id == task.id
        assert retrieved_task.title == "Test task"

    def test_get_returns_none_if_not_exists(self):
        """get(task_id) returns None if task ID not found"""
        repo = MemoryRepository()

        retrieved_task = repo.get("non-existent-id")

        assert retrieved_task is None

    def test_get_all_returns_empty_list_when_no_tasks(self):
        """get_all() returns empty list when repository is empty"""
        repo = MemoryRepository()

        all_tasks = repo.get_all()

        assert all_tasks == []
        assert len(all_tasks) == 0

    def test_get_all_returns_tasks_sorted_by_created_at_desc(self):
        """get_all() returns tasks sorted by created_at DESC (newest first)"""
        repo = MemoryRepository()

        # Add tasks in sequence (created_at will be increasing)
        task1 = Task(title="First task")
        repo.add(task1)

        task2 = Task(title="Second task")
        repo.add(task2)

        task3 = Task(title="Third task")
        repo.add(task3)

        all_tasks = repo.get_all()

        # Verify sorted by created_at DESC (newest first)
        assert len(all_tasks) == 3
        assert all_tasks[0].id == task3.id  # Most recent
        assert all_tasks[1].id == task2.id
        assert all_tasks[2].id == task1.id  # Oldest


class TestMemoryRepositoryUpdateAndDelete:
    """Test MemoryRepository.update() and delete() operations (T022)"""

    def test_update_replaces_existing_task(self):
        """update(task) replaces existing task in storage"""
        repo = MemoryRepository()
        task = Task(title="Original title")
        repo.add(task)

        # Modify task and update
        task.update_title("Updated title")
        repo.update(task)

        # Retrieve and verify update
        retrieved_task = repo.get(task.id)
        assert retrieved_task.title == "Updated title"

    def test_update_with_non_existent_task_raises_error(self):
        """update(task) with non-existent task.id raises TaskNotFoundError"""
        repo = MemoryRepository()
        task = Task(title="Test task")

        # Attempt to update task not in repository
        with pytest.raises(TaskNotFoundError, match="Task with ID .* not found"):
            repo.update(task)

    def test_delete_removes_task_from_storage(self):
        """delete(task_id) removes task from storage"""
        repo = MemoryRepository()
        task = Task(title="Test task")
        repo.add(task)

        # Verify task exists
        assert repo.get(task.id) is not None

        # Delete task
        repo.delete(task.id)

        # Verify task removed
        assert repo.get(task.id) is None

    def test_delete_with_non_existent_id_raises_error(self):
        """delete(task_id) with non-existent ID raises TaskNotFoundError"""
        repo = MemoryRepository()

        with pytest.raises(TaskNotFoundError, match="Task with ID .* not found"):
            repo.delete("non-existent-id")

    def test_exists_returns_true_if_task_exists(self):
        """exists(task_id) returns True if task exists"""
        repo = MemoryRepository()
        task = Task(title="Test task")
        repo.add(task)

        assert repo.exists(task.id) is True

    def test_exists_returns_false_if_task_not_exists(self):
        """exists(task_id) returns False if task does not exist"""
        repo = MemoryRepository()

        assert repo.exists("non-existent-id") is False
