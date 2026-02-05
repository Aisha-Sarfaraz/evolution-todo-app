"""T084-T085: Reminder checker service and push notification delivery.

Queries due reminders, sends push notifications via pywebpush,
marks notification_sent, and handles 410 Gone (stale subscriptions).
"""

import json
import logging
import os
from datetime import datetime, timezone
from uuid import UUID

from pywebpush import webpush, WebPushException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import Task
from src.models.push_subscription import PushSubscription
from src.models.reminder import ReminderMetadata

logger = logging.getLogger("reminder_service")


async def check_reminders() -> None:
    """Check for due reminders and send push notifications.

    Scheduler job that runs every minute to find reminders
    where reminder_time <= now and notification_sent = False.
    """
    from src.mcp.database import get_mcp_session

    async for session in get_mcp_session():
        try:
            await _process_due_reminders(session)
        except Exception as e:
            logger.error("Reminder check failed: %s", e)
        break


async def _process_due_reminders(session: AsyncSession) -> None:
    """Process all due reminders."""
    now = datetime.now(timezone.utc)

    result = await session.execute(
        select(ReminderMetadata).where(
            ReminderMetadata.reminder_time <= now,
            ReminderMetadata.notification_sent == False,  # noqa: E712
            (ReminderMetadata.snooze_until == None) | (ReminderMetadata.snooze_until <= now),  # noqa: E711
        )
    )
    due_reminders = result.scalars().all()

    for reminder in due_reminders:
        try:
            await _send_reminder(session, reminder)
        except Exception as e:
            logger.error("Failed to send reminder %s: %s", reminder.id, e)

    await session.commit()


async def _send_reminder(session: AsyncSession, reminder: ReminderMetadata) -> None:
    """Send push notification for a reminder and mark as sent."""
    # Load the task
    task_result = await session.execute(
        select(Task).where(Task.id == reminder.task_id)
    )
    task = task_result.scalar_one_or_none()
    if not task:
        logger.warning("Task %s not found for reminder %s", reminder.task_id, reminder.id)
        reminder.notification_sent = True
        return

    # Load user's push subscriptions
    sub_result = await session.execute(
        select(PushSubscription).where(PushSubscription.user_id == task.user_id)
    )
    subscriptions = sub_result.scalars().all()

    if not subscriptions:
        logger.info("No push subscriptions for user %s, marking reminder sent", task.user_id)
        reminder.notification_sent = True
        return

    # Send to all subscriptions
    notification_payload = json.dumps({
        "title": "Task Reminder",
        "body": f"Reminder: {task.title}",
        "tag": str(task.id),
        "data": {
            "task_id": str(task.id),
            "url": "/chat",
        },
    })

    for sub in subscriptions:
        await _send_push_notification(session, sub, notification_payload)

    reminder.notification_sent = True
    logger.info("Sent reminder for task '%s' to user %s", task.title, task.user_id)


async def _send_push_notification(
    session: AsyncSession,
    subscription: PushSubscription,
    payload: str,
) -> None:
    """Send a single push notification via pywebpush.

    Handles 410 Gone by removing stale subscriptions.
    """
    vapid_private_key = os.getenv("VAPID_PRIVATE_KEY", "")
    vapid_claims_email = os.getenv("VAPID_CLAIMS_EMAIL", "mailto:admin@example.com")

    subscription_info = {
        "endpoint": subscription.endpoint,
        "keys": subscription.keys,
    }

    try:
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=vapid_private_key,
            vapid_claims={"sub": vapid_claims_email},
        )
    except WebPushException as e:
        if hasattr(e, "response") and e.response is not None and e.response.status_code == 410:
            # Subscription is gone, remove it
            logger.info("Push subscription %s is gone (410), removing", subscription.id)
            await session.delete(subscription)
        else:
            logger.error("Push notification failed for %s: %s", subscription.endpoint, e)
