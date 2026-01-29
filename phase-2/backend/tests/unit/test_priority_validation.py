"""Priority validation unit tests.

T099: [US5] Unit test for priority validation

Tests:
- Valid priorities accepted (Low, Medium, High, Urgent)
- Invalid priority returns validation error
- Default priority is Medium

@see specs/001-fullstack-todo-web/spec.md - FR-021, FR-022
"""

import pytest
from pydantic import ValidationError

from src.models.task import TaskPriority, TaskCreate, Task


class TestTaskPriorityEnum:
    """Test TaskPriority enum values."""

    def test_valid_priority_low(self):
        """TaskPriority.LOW has value 'Low'."""
        assert TaskPriority.LOW.value == "Low"

    def test_valid_priority_medium(self):
        """TaskPriority.MEDIUM has value 'Medium'."""
        assert TaskPriority.MEDIUM.value == "Medium"

    def test_valid_priority_high(self):
        """TaskPriority.HIGH has value 'High'."""
        assert TaskPriority.HIGH.value == "High"

    def test_valid_priority_urgent(self):
        """TaskPriority.URGENT has value 'Urgent'."""
        assert TaskPriority.URGENT.value == "Urgent"

    def test_all_priorities_count(self):
        """There are exactly 4 priority levels."""
        assert len(TaskPriority) == 4


class TestTaskCreatePriority:
    """Test priority validation in TaskCreate schema."""

    def test_default_priority_is_medium(self):
        """TaskCreate defaults to Medium priority when not specified."""
        task = TaskCreate(title="Test task")

        assert task.priority == TaskPriority.MEDIUM

    def test_explicit_priority_low(self):
        """TaskCreate accepts explicit Low priority."""
        task = TaskCreate(title="Test task", priority=TaskPriority.LOW)

        assert task.priority == TaskPriority.LOW

    def test_explicit_priority_high(self):
        """TaskCreate accepts explicit High priority."""
        task = TaskCreate(title="Test task", priority=TaskPriority.HIGH)

        assert task.priority == TaskPriority.HIGH

    def test_explicit_priority_urgent(self):
        """TaskCreate accepts explicit Urgent priority."""
        task = TaskCreate(title="Test task", priority=TaskPriority.URGENT)

        assert task.priority == TaskPriority.URGENT

    def test_priority_string_low(self):
        """TaskCreate accepts priority as string 'Low'."""
        task = TaskCreate(title="Test task", priority="Low")

        assert task.priority == TaskPriority.LOW

    def test_priority_string_medium(self):
        """TaskCreate accepts priority as string 'Medium'."""
        task = TaskCreate(title="Test task", priority="Medium")

        assert task.priority == TaskPriority.MEDIUM

    def test_priority_string_high(self):
        """TaskCreate accepts priority as string 'High'."""
        task = TaskCreate(title="Test task", priority="High")

        assert task.priority == TaskPriority.HIGH

    def test_priority_string_urgent(self):
        """TaskCreate accepts priority as string 'Urgent'."""
        task = TaskCreate(title="Test task", priority="Urgent")

        assert task.priority == TaskPriority.URGENT

    def test_invalid_priority_rejects(self):
        """TaskCreate rejects invalid priority value."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Test task", priority="Invalid")

        assert "priority" in str(exc_info.value).lower()

    def test_invalid_priority_number_rejects(self):
        """TaskCreate rejects numeric priority value."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Test task", priority=1)

        assert "priority" in str(exc_info.value).lower()

    def test_invalid_priority_empty_string_rejects(self):
        """TaskCreate rejects empty string priority."""
        with pytest.raises(ValidationError) as exc_info:
            TaskCreate(title="Test task", priority="")

        assert "priority" in str(exc_info.value).lower()


class TestPriorityOrdering:
    """Test priority ordering for sorting."""

    def test_priority_values_for_sorting(self):
        """Priority enum values enable proper sorting."""
        priorities = [
            TaskPriority.LOW,
            TaskPriority.MEDIUM,
            TaskPriority.HIGH,
            TaskPriority.URGENT,
        ]

        # Verify all priorities are distinct
        assert len(set(priorities)) == 4

        # Verify values are string-comparable for sorting
        values = [p.value for p in priorities]
        assert all(isinstance(v, str) for v in values)
