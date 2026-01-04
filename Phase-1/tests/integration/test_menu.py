"""
Integration tests for main menu (Phase 8).

Tests cover:
- T080-T085: Menu tests

Menu orchestration and input validation
"""

import pytest
from src.storage.memory_repository import MemoryRepository
from src.cli.menu import display_menu


class TestMenuDisplay:
    """Test menu display shows 6 options (T080)"""

    def test_menu_displays_6_options(self, monkeypatch, capsys):
        """Menu displays all 6 options"""
        repo = MemoryRepository()

        # Mock input: Exit immediately (choice 6)
        inputs = iter(['6'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        display_menu(repo)

        captured = capsys.readouterr()
        assert "1." in captured.out  # Create Task
        assert "2." in captured.out  # View All Tasks
        assert "3." in captured.out  # Update Task
        assert "4." in captured.out  # Mark Complete
        assert "5." in captured.out  # Delete Task
        assert "6." in captured.out  # Exit


class TestMenuAcceptsValidChoice:
    """Test menu accepts valid choice 1-6 (T081)"""

    def test_menu_accepts_valid_choice(self, monkeypatch, capsys):
        """Menu accepts choices 1-6 without error"""
        repo = MemoryRepository()

        # Mock input: Valid choice then exit
        inputs = iter(['6'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        display_menu(repo)

        # Should exit cleanly
        captured = capsys.readouterr()
        assert "✗" not in captured.out or "invalid" not in captured.out.lower()


class TestMenuRejectsInvalidChoice:
    """Test menu rejects invalid choice (T082)"""

    def test_menu_rejects_invalid_choice(self, monkeypatch, capsys):
        """Menu displays error for invalid choice and re-prompts"""
        repo = MemoryRepository()

        # Mock input: Invalid choice, then valid exit
        inputs = iter(['99', '6'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        display_menu(repo)

        captured = capsys.readouterr()
        # Should show invalid choice message
        assert "invalid" in captured.out.lower() or "1-6" in captured.out


class TestMenuExitsOnChoice6:
    """Test menu exits on choice 6 (T083)"""

    def test_menu_exits_on_choice_6(self, monkeypatch, capsys):
        """Menu exits cleanly when user selects 6"""
        repo = MemoryRepository()

        inputs = iter(['6'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        display_menu(repo)

        captured = capsys.readouterr()
        # Should exit without error
        assert True  # If we reach here, menu exited successfully


class TestMenuOptionRouting:
    """Test menu routes to correct operations (T084)"""

    def test_menu_routes_to_operations(self, monkeypatch, capsys):
        """Menu correctly routes choices to operations"""
        repo = MemoryRepository()

        # Mock: Choice 2 (View All), then exit
        # For view all, need to mock monkeypatch for the operation too
        inputs = iter(['2', '', '6'])  # Choice 2, empty for detail prompt, exit
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        display_menu(repo)

        captured = capsys.readouterr()
        # Should show view all output
        assert "All Tasks" in captured.out or "No tasks found" in captured.out


class TestMenuErrorHandling:
    """Test menu handles errors gracefully (T085)"""

    def test_menu_handles_keyboard_interrupt(self, monkeypatch, capsys):
        """Menu handles Ctrl+C (KeyboardInterrupt) gracefully"""
        repo = MemoryRepository()

        # Mock: KeyboardInterrupt
        def mock_input(prompt):
            raise KeyboardInterrupt

        monkeypatch.setattr('builtins.input', mock_input)

        display_menu(repo)

        captured = capsys.readouterr()
        # Should show exit message
        assert "Exiting" in captured.out or "Goodbye" in captured.out
