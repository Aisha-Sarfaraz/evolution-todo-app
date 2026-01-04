"""
Integration tests for Create Task workflow (User Story 1).

Tests cover:
- T029-T034: Create task integration tests (all acceptance scenarios from spec)

User Story P1: User wants to add a new task to track work

TDD Phase: RED - These tests MUST FAIL before CLI implementation
"""

import pytest
from src.domain.task import Task
from src.storage.memory_repository import MemoryRepository
from src.cli.operations import create_task_operation
from src.domain.exceptions import DomainValidationError


class TestCreateTaskValidInputs:
    """Test create task with valid inputs (T029 - P1.1)"""

    def test_create_task_with_valid_title_and_description(self, monkeypatch, capsys):
        """Create task with valid title and description succeeds"""
        repo = MemoryRepository()

        # Mock user inputs: title, description
        inputs = iter(["Buy groceries", "Milk, eggs, bread"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        create_task_operation(repo)

        # Verify task created in repository
        all_tasks = repo.get_all()
        assert len(all_tasks) == 1
        assert all_tasks[0].title == "Buy groceries"
        assert all_tasks[0].description == "Milk, eggs, bread"
        assert all_tasks[0].status == "pending"

        # Verify success message displayed
        captured = capsys.readouterr()
        assert "✓" in captured.out or "created successfully" in captured.out


class TestCreateTaskEmptyTitle:
    """Test create task with empty title (T030 - P1.2)"""

    def test_create_task_with_empty_title_shows_error(self, monkeypatch, capsys):
        """Create task with empty title displays error message"""
        repo = MemoryRepository()

        # Mock user inputs: empty title + description (should fail), then valid title + description
        inputs = iter(["", "", "Valid title", ""])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        create_task_operation(repo)

        # Verify error message shown
        captured = capsys.readouterr()
        assert "✗" in captured.out or "empty" in captured.out.lower()


class TestCreateTaskTitleTooLong:
    """Test create task with title > 200 chars (T031 - P1.3)"""

    def test_create_task_with_title_exceeding_200_chars_shows_error(self, monkeypatch, capsys):
        """Create task with title > 200 chars displays error message"""
        repo = MemoryRepository()

        # Mock user inputs: title with 201 chars + description (should fail), then valid title + description
        long_title = "A" * 201
        inputs = iter([long_title, "", "Valid title", ""])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        create_task_operation(repo)

        # Verify error message shown
        captured = capsys.readouterr()
        assert "✗" in captured.out or "200" in captured.out


class TestCreateTaskDescriptionTruncation:
    """Test create task with description > 2000 chars (T032 - P1.4)"""

    def test_create_task_with_description_exceeding_2000_chars_auto_truncates(self, monkeypatch, capsys):
        """Create task with description > 2000 chars auto-truncates to 2000"""
        repo = MemoryRepository()

        # Mock user inputs: valid title, long description (3000 chars)
        long_description = "A" * 3000
        inputs = iter(["Test task", long_description])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        create_task_operation(repo)

        # Verify task created with truncated description
        all_tasks = repo.get_all()
        assert len(all_tasks) == 1
        assert len(all_tasks[0].description) == 2000


class TestCreateTaskWhitespaceTrimming:
    """Test create task with whitespace trimming (T033 - P1.5)"""

    def test_create_task_trims_whitespace_from_title(self, monkeypatch, capsys):
        """Create task trims leading/trailing whitespace from title"""
        repo = MemoryRepository()

        # Mock user inputs: title with leading/trailing whitespace
        inputs = iter(["  Buy groceries  ", ""])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        create_task_operation(repo)

        # Verify task created with trimmed title
        all_tasks = repo.get_all()
        assert len(all_tasks) == 1
        assert all_tasks[0].title == "Buy groceries"


class TestCreateTaskUnicodeCharacters:
    """Test create task with Unicode characters (T034 - P1.6)"""

    def test_create_task_accepts_unicode_characters(self, monkeypatch, capsys):
        """Create task accepts Unicode characters (emoji, accents, CJK)"""
        repo = MemoryRepository()

        # Mock user inputs: title with Unicode characters
        inputs = iter(["買い物リスト 🛒", "Japanese grocery list"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        create_task_operation(repo)

        # Verify task created with Unicode characters preserved
        all_tasks = repo.get_all()
        assert len(all_tasks) == 1
        assert "買い物" in all_tasks[0].title
        assert "🛒" in all_tasks[0].title
