"""
End-to-end integration tests for complete user journeys.

Tests cover:
- T097-T099: E2E workflow tests

Validates complete workflows across all operations
"""

import pytest
from src.domain.task import Task
from src.storage.memory_repository import MemoryRepository
from src.cli.operations import (
    create_task_operation,
    view_all_tasks_operation,
    update_task_operation,
    mark_complete_operation,
    delete_task_operation,
)


class TestE2ECreateViewUpdateView:
    """Test E2E: create → view → update → view (T097)"""

    def test_create_view_update_view_workflow(self, monkeypatch, capsys):
        """Complete workflow: Create task, view it, update it, view again to verify changes"""
        repo = MemoryRepository()

        # Step 1: Create task
        create_inputs = iter(["Buy groceries", "Milk and eggs"])
        monkeypatch.setattr('builtins.input', lambda _: next(create_inputs))
        create_task_operation(repo)

        # Verify task created
        all_tasks = repo.get_all()
        assert len(all_tasks) == 1
        created_task = all_tasks[0]
        assert created_task.title == "Buy groceries"

        # Step 2: View all tasks
        view_inputs = iter([''])  # No detail view
        monkeypatch.setattr('builtins.input', lambda _: next(view_inputs))
        view_all_tasks_operation(repo)

        captured = capsys.readouterr()
        assert "Buy groceries" in captured.out

        # Step 3: Update task
        update_inputs = iter([created_task.id[:8], "Buy groceries and bread", ""])
        monkeypatch.setattr('builtins.input', lambda _: next(update_inputs))
        update_task_operation(repo)

        # Step 4: View again to verify update
        view_inputs2 = iter([''])
        monkeypatch.setattr('builtins.input', lambda _: next(view_inputs2))
        view_all_tasks_operation(repo)

        captured = capsys.readouterr()
        assert "Buy groceries and bread" in captured.out

        # Verify task was updated in repository
        updated_task = repo.get(created_task.id)
        assert updated_task.title == "Buy groceries and bread"


class TestE2ECreateMarkCompleteView:
    """Test E2E: create → mark complete → view (T098)"""

    def test_create_mark_complete_view_workflow(self, monkeypatch, capsys):
        """Complete workflow: Create task, mark complete, view to verify [✓]"""
        repo = MemoryRepository()

        # Step 1: Create task
        create_inputs = iter(["Finish homework", "Math assignment"])
        monkeypatch.setattr('builtins.input', lambda _: next(create_inputs))
        create_task_operation(repo)

        created_task = repo.get_all()[0]
        assert created_task.status == "pending"

        # Step 2: Mark task complete
        complete_inputs = iter([created_task.id[:8]])
        monkeypatch.setattr('builtins.input', lambda _: next(complete_inputs))
        mark_complete_operation(repo)

        # Step 3: View to verify [✓]
        view_inputs = iter([''])
        monkeypatch.setattr('builtins.input', lambda _: next(view_inputs))
        view_all_tasks_operation(repo)

        captured = capsys.readouterr()
        assert "[✓]" in captured.out or "complete" in captured.out

        # Verify task marked complete in repository
        completed_task = repo.get(created_task.id)
        assert completed_task.status == "complete"
        assert completed_task.completed_at is not None


class TestE2ECreateMultipleDeleteOneView:
    """Test E2E: create multiple → delete one → view (T099)"""

    def test_create_multiple_delete_one_view_workflow(self, monkeypatch, capsys):
        """Complete workflow: Create 3 tasks, delete middle one, view to verify count"""
        repo = MemoryRepository()

        # Step 1: Create 3 tasks
        for i in range(1, 4):
            create_inputs = iter([f"Task {i}", f"Description {i}"])
            monkeypatch.setattr('builtins.input', lambda _: next(create_inputs))
            create_task_operation(repo)

        all_tasks = repo.get_all()
        assert len(all_tasks) == 3
        middle_task = all_tasks[1]

        # Step 2: Delete middle task
        delete_inputs = iter([middle_task.id[:8], 'y'])
        monkeypatch.setattr('builtins.input', lambda _: next(delete_inputs))
        delete_task_operation(repo)

        # Step 3: View to verify only 2 remain
        view_inputs = iter([''])
        monkeypatch.setattr('builtins.input', lambda _: next(view_inputs))
        view_all_tasks_operation(repo)

        captured = capsys.readouterr()
        assert "Total: 2 tasks" in captured.out

        # Verify repository has 2 tasks
        remaining_tasks = repo.get_all()
        assert len(remaining_tasks) == 2
        assert middle_task.id not in [t.id for t in remaining_tasks]
