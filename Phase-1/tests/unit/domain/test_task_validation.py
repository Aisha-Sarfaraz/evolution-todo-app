"""
Unit tests for Task Unicode and edge case validation.

Tests cover:
- T011: Task Unicode and edge cases

TDD Phase: RED - These tests MUST FAIL before implementation
"""

import pytest
from src.domain.task import Task
from src.domain.exceptions import DomainValidationError


class TestTaskUnicodeSupport:
    """Test Task entity handles Unicode characters correctly"""

    def test_task_title_accepts_unicode_characters(self):
        """Task title accepts Unicode characters (emoji, accents, CJK)"""
        unicode_titles = [
            "買い物リスト",  # Japanese
            "Liste de courses",  # French
            "购物清单",  # Chinese
            "할 일 목록",  # Korean
            "Task with emoji 🎯✅",
        ]

        for title in unicode_titles:
            task = Task(title=title)
            assert task.title == title

    def test_task_description_accepts_unicode_characters(self):
        """Task description accepts Unicode characters"""
        task = Task(
            title="Unicode test",
            description="Café ☕, Naïve résumé, 日本語テスト, emoji 🚀"
        )

        assert "Café" in task.description
        assert "日本語" in task.description
        assert "🚀" in task.description


class TestTaskEdgeCases:
    """Test Task entity edge cases"""

    def test_task_title_with_newlines_and_tabs(self):
        """Task title with newlines and tabs is trimmed correctly"""
        task = Task(title="\t\nBuy groceries\n\t")

        # Leading/trailing whitespace (including \n, \t) should be trimmed
        assert task.title.strip() == "Buy groceries"

    def test_task_title_with_mixed_whitespace(self):
        """Task title with mixed whitespace types is trimmed"""
        task = Task(title="   \t\n  Test task  \n\t   ")

        assert task.title.strip() == "Test task"

    def test_task_description_empty_string_allowed(self):
        """Task description can be empty string"""
        task = Task(title="Test", description="")

        assert task.description == ""

    def test_task_title_exactly_one_char(self):
        """Task title with exactly 1 character is valid"""
        task = Task(title="A")

        assert task.title == "A"
        assert len(task.title) == 1

    def test_task_title_with_special_characters(self):
        """Task title with special characters is valid"""
        task = Task(title="Buy @groceries #today!")

        assert task.title == "Buy @groceries #today!"

    def test_task_title_with_numbers_only(self):
        """Task title with numbers only is valid"""
        task = Task(title="12345")

        assert task.title == "12345"

    def test_task_multiple_spaces_within_title_preserved(self):
        """Multiple spaces within title are preserved (only trim leading/trailing)"""
        task = Task(title="  Task  with   multiple    spaces  ")

        # Leading/trailing trimmed, but internal spaces preserved
        assert task.title == "Task  with   multiple    spaces"
