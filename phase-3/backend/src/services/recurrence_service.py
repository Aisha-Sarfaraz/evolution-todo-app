"""T065: Recurrence calculation service.

Calculates next occurrence dates for daily/weekly/monthly/yearly
recurrences with month-end clamping and end_date enforcement.
"""

import calendar
from datetime import date, datetime, timedelta, timezone
from typing import Optional


def calculate_next_occurrence(
    frequency: str,
    interval: int,
    current: datetime,
    end_date: Optional[date] = None,
    days_of_week: Optional[list[int]] = None,
    day_of_month: Optional[int] = None,
) -> Optional[datetime]:
    """Calculate the next occurrence of a recurring task.

    Args:
        frequency: daily, weekly, monthly, or yearly.
        interval: Number of periods between occurrences.
        current: Current occurrence datetime.
        end_date: Optional end date after which no more occurrences.
        days_of_week: For weekly, which days (0=Mon, 6=Sun).
        day_of_month: For monthly, specific day.

    Returns:
        Next occurrence datetime, or None if past end_date.
    """
    if frequency == "daily":
        next_dt = current + timedelta(days=interval)

    elif frequency == "weekly":
        next_dt = current + timedelta(weeks=interval)

    elif frequency == "monthly":
        # Add months
        month = current.month + interval
        year = current.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1

        # Clamp day to valid range for target month
        target_day = day_of_month or current.day
        max_day = calendar.monthrange(year, month)[1]
        day = min(target_day, max_day)

        next_dt = current.replace(year=year, month=month, day=day)

    elif frequency == "yearly":
        year = current.year + interval
        month = current.month
        day = current.day

        # Handle leap day clamping
        max_day = calendar.monthrange(year, month)[1]
        day = min(day, max_day)

        next_dt = current.replace(year=year, month=month, day=day)

    else:
        return None

    # Check end_date
    if end_date and next_dt.date() > end_date:
        return None

    return next_dt
