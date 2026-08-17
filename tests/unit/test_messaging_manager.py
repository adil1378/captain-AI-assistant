"""
Unit & Integration Tests for Volume 10 Part 10B Messaging & Notification Architecture.
Verifies message creation, channel validation, priority queue ordering, template rendering,
quiet hours enforcement, and async delivery retries.
"""

import pytest
import asyncio
from src.backend.core.messaging_manager import (
    MessagingManager,
    NotificationChannel,
    NotificationPriority,
    DeliveryStatus,
    UserPreference,
    NotificationRecord
)


def test_template_rendering():
    mm = MessagingManager()
    mm.template_engine.register_template("welcome", "Hello {name}, welcome to {system}!")

    rendered = mm.template_engine.render("welcome", {"name": "Adil", "system": "Captain AI OS"})
    assert rendered == "Hello Adil, welcome to Captain AI OS!"


def test_quiet_hours_and_user_preferences():
    mm = MessagingManager()
    pref = UserPreference(
        user_id="user_1",
        quiet_hours_start_hour=22,
        quiet_hours_end_hour=7,
        disabled_channels=[NotificationChannel.SMS]
    )

    # Channel disabled check
    with pytest.raises(PermissionError):
        mm.send_notification(
            sender="System",
            recipient="user_1",
            channel=NotificationChannel.SMS,
            title="Alert",
            content="SMS Test",
            user_pref=pref
        )

    # Quiet hours calculation
    assert mm.is_in_quiet_hours(pref, 23) is True
    assert mm.is_in_quiet_hours(pref, 3) is True
    assert mm.is_in_quiet_hours(pref, 12) is False


@pytest.mark.anyio
async def test_priority_queue_and_delivery():
    mm = MessagingManager()

    delivered_logs = []

    async def mock_email_adapter(notif: NotificationRecord) -> bool:
        delivered_logs.append(notif.notification_id)
        return True

    mm.register_provider(NotificationChannel.EMAIL, mock_email_adapter)

    rec_low = mm.send_notification(
        sender="System",
        recipient="user_1",
        channel=NotificationChannel.EMAIL,
        title="Low Priority",
        content="Low msg",
        priority=NotificationPriority.LOW
    )

    rec_urgent = mm.send_notification(
        sender="System",
        recipient="user_1",
        channel=NotificationChannel.EMAIL,
        title="Urgent Priority",
        content="Urgent msg",
        priority=NotificationPriority.URGENT
    )

    # Verify priority queue ordering (URGENT first)
    assert mm.queue[0].notification_id == rec_urgent.notification_id

    count = await mm.process_queue()
    assert count == 2
    assert mm.history[rec_urgent.notification_id].status == DeliveryStatus.DELIVERED
    assert mm.history[rec_low.notification_id].status == DeliveryStatus.DELIVERED


@pytest.mark.anyio
async def test_retry_handling_on_failure():
    mm = MessagingManager()

    attempts = 0

    async def failing_adapter(notif: NotificationRecord) -> bool:
        nonlocal attempts
        attempts += 1
        return False  # Force delivery failure

    mm.register_provider(NotificationChannel.TELEGRAM, failing_adapter)

    rec = mm.send_notification(
        sender="System",
        recipient="user_1",
        channel=NotificationChannel.TELEGRAM,
        title="Failure Test",
        content="Testing retries",
        priority=NotificationPriority.NORMAL
    )

    await mm.process_queue()
    assert attempts == 4  # Initial + 3 retries
    assert mm.history[rec.notification_id].status == DeliveryStatus.FAILED
