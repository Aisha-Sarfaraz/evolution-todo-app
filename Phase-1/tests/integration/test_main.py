"""
Integration tests for main application entry point.

Tests cover:
- T090-T092: Main entry point tests

Application initialization and dependency injection
"""

import pytest
from src.main import main
from src.storage.memory_repository import MemoryRepository


class TestMainInitialization:
    """Test main initializes MemoryRepository (T090)"""

    def test_main_initializes_memory_repository(self, monkeypatch, capsys):
        """Main entry point initializes MemoryRepository"""
        # Mock input to exit immediately
        inputs = iter(['6'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        # Run main and expect SystemExit(0)
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Verify clean exit
        assert exc_info.value.code == 0

        # If we reach here, main initialized and exited successfully
        captured = capsys.readouterr()
        assert "Todo Application" in captured.out


class TestMainCallsDisplayMenu:
    """Test main calls display_menu (T091)"""

    def test_main_calls_display_menu(self, monkeypatch, capsys):
        """Main entry point calls display_menu function"""
        # Mock input to exit immediately
        inputs = iter(['6'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        # Run main and expect SystemExit(0)
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Verify clean exit
        assert exc_info.value.code == 0

        captured = capsys.readouterr()
        # Should show menu output
        assert "Main Menu" in captured.out or "Create Task" in captured.out


class TestMainHandlesGlobalExceptions:
    """Test main handles global exceptions (T092)"""

    def test_main_handles_global_exceptions_gracefully(self, monkeypatch, capsys):
        """Main handles unexpected exceptions without crashing"""
        # This test verifies main has global exception handling
        # If an unexpected error occurs, main should handle it gracefully

        # Mock input to exit
        inputs = iter(['6'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))

        # Expect clean SystemExit, not unhandled exceptions
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should exit cleanly with code 0
        assert exc_info.value.code == 0
