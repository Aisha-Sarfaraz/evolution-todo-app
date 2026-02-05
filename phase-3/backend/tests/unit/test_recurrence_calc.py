"""T059/T062: Unit tests for recurrence calculation.

Tests daily, weekly, monthly, yearly, interval, month-end edge cases,
and end_date enforcement.
"""

from datetime import date, datetime, timezone

import pytest


@pytest.mark.unit
class TestRecurrenceCalculation:
    """T059: Tests for recurrence calculation service."""

    def test_daily_next_occurrence(self) -> None:
        """Daily recurrence: next day."""
        from phase3_backend.services.recurrence_service import calculate_next_occurrence

        current = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)
        result = calculate_next_occurrence("daily", 1, current)
        assert result.day == 16

    def test_daily_interval_2(self) -> None:
        """Every other day recurrence."""
        from phase3_backend.services.recurrence_service import calculate_next_occurrence

        current = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)
        result = calculate_next_occurrence("daily", 2, current)
        assert result.day == 17

    def test_weekly_next_occurrence(self) -> None:
        """Weekly recurrence: next week."""
        from phase3_backend.services.recurrence_service import calculate_next_occurrence

        current = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)
        result = calculate_next_occurrence("weekly", 1, current)
        assert result.day == 22

    def test_monthly_next_occurrence(self) -> None:
        """Monthly recurrence: same day next month."""
        from phase3_backend.services.recurrence_service import calculate_next_occurrence

        current = datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)
        result = calculate_next_occurrence("monthly", 1, current)
        assert result.month == 2
        assert result.day == 15

    def test_monthly_end_clamping(self) -> None:
        """Monthly recurrence: Feb 31 clamps to Feb 28."""
        from phase3_backend.services.recurrence_service import calculate_next_occurrence

        current = datetime(2026, 1, 31, 10, 0, tzinfo=timezone.utc)
        result = calculate_next_occurrence("monthly", 1, current)
        assert result.month == 2
        assert result.day == 28

    def test_yearly_next_occurrence(self) -> None:
        """Yearly recurrence: same date next year."""
        from phase3_backend.services.recurrence_service import calculate_next_occurrence

        current = datetime(2026, 3, 15, 10, 0, tzinfo=timezone.utc)
        result = calculate_next_occurrence("yearly", 1, current)
        assert result.year == 2027
        assert result.month == 3
        assert result.day == 15

    def test_yearly_leap_day(self) -> None:
        """Yearly recurrence: Feb 29 in non-leap year clamps to Feb 28."""
        from phase3_backend.services.recurrence_service import calculate_next_occurrence

        # 2024 is a leap year
        current = datetime(2024, 2, 29, 10, 0, tzinfo=timezone.utc)
        result = calculate_next_occurrence("yearly", 1, current)
        assert result.year == 2025
        assert result.month == 2
        assert result.day == 28


@pytest.mark.unit
class TestEndDateEnforcement:
    """T062: Tests for end_date enforcement."""

    def test_end_date_stops_recurrence(self) -> None:
        """No next occurrence after end_date."""
        from phase3_backend.services.recurrence_service import calculate_next_occurrence

        current = datetime(2026, 1, 30, 10, 0, tzinfo=timezone.utc)
        end_date = date(2026, 1, 31)
        result = calculate_next_occurrence("daily", 1, current, end_date=end_date)
        assert result is not None  # Jan 31 is before or on end date

    def test_end_date_past_returns_none(self) -> None:
        """Returns None when next occurrence would be after end_date."""
        from phase3_backend.services.recurrence_service import calculate_next_occurrence

        current = datetime(2026, 1, 31, 10, 0, tzinfo=timezone.utc)
        end_date = date(2026, 1, 31)
        result = calculate_next_occurrence("daily", 1, current, end_date=end_date)
        # Next would be Feb 1, which is after Jan 31 end_date
        assert result is None
