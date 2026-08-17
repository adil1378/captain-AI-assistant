"""
Captain AI OS - Messaging & Notification System (Volume 10 Part 10B)
Responsible for multi-channel message routing, priority queue management, delivery tracking,
template rendering, user quiet-hours enforcement, and provider failover retries.
"""

from typing import Dict, Any, List, Optional, Callable, Awaitable
from enum import Enum
import asyncio
import time
from pydantic import BaseModel, Field
from src.backend.core.permission_manager import PermissionManager, Permission


class NotificationChannel(str, Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"
    TELEGRAM = "TELEGRAM"
    SLACK = "SLACK"
    DISCORD = "DISCORD"
    TEAMS = "TEAMS"
    DESKTOP = "DESKTOP"
    MOBILE_PUSH = "MOBILE_PUSH"
    WEB = "WEB"
    AGENT = "AGENT"


class NotificationPriority(int, Enum):
    URGENT = 100
    HIGH = 75
    NORMAL = 50
    LOW = 25
    BACKGROUND = 10


class DeliveryStatus(str, Enum):
    QUEUED = "QUEUED"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"


class UserPreference(BaseModel):
    user_id: str
    quiet_hours_start_hour: Optional[int] = 22  # 10 PM
    quiet_hours_end_hour: Optional[int] = 7     # 7 AM
    disabled_channels: List[NotificationChannel] = Field(default_factory=list)
    min_priority_threshold: NotificationPriority = NotificationPriority.LOW


class NotificationRecord(BaseModel):
    notification_id: str
    sender: str
    recipient: str
    channel: NotificationChannel
    priority: NotificationPriority
    title: str
    content: str
    status: DeliveryStatus = DeliveryStatus.QUEUED
    retry_count: int = 0
    max_retries: int = 3
    timestamp: float = Field(default_factory=time.time)
    correlation_id: Optional[str] = None


class TemplateEngine:
    """Renders reusable message templates with variable substitution."""

    def __init__(self):
        self.templates: Dict[str, str] = {}

    def register_template(self, template_name: str, template_body: str):
        self.templates[template_name] = template_body

    def render(self, template_name: str, variables: Dict[str, Any]) -> str:
        if template_name not in self.templates:
            raise KeyError(f"Template '{template_name}' not found.")
        body = self.templates[template_name]
        for key, val in variables.items():
            body = body.replace(f"{{{key}}}", str(val))
        return body


class MessagingManager:
    """Centralized Messaging & Notification Manager."""

    def __init__(self):
        self.queue: List[NotificationRecord] = []
        self.history: Dict[str, NotificationRecord] = {}
        self.provider_adapters: Dict[NotificationChannel, Callable[[NotificationRecord], Awaitable[bool]]] = {}
        self.template_engine = TemplateEngine()
        self.permission_manager = PermissionManager()

    def register_provider(
        self,
        channel: NotificationChannel,
        adapter_fn: Callable[[NotificationRecord], Awaitable[bool]]
    ):
        """Registers a provider adapter for a specific channel."""
        self.provider_adapters[channel] = adapter_fn

    def is_in_quiet_hours(self, pref: UserPreference, current_hour: int) -> bool:
        """Determines if the current time falls within user-configured quiet hours."""
        if pref.quiet_hours_start_hour is None or pref.quiet_hours_end_hour is None:
            return False
        start = pref.quiet_hours_start_hour
        end = pref.quiet_hours_end_hour
        if start > end:
            return current_hour >= start or current_hour < end
        return start <= current_hour < end

    def send_notification(
        self,
        sender: str,
        recipient: str,
        channel: NotificationChannel,
        title: str,
        content: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        user_pref: Optional[UserPreference] = None,
        correlation_id: Optional[str] = None
    ) -> NotificationRecord:
        """Validates user preferences and queues notification for delivery."""
        current_hour = time.localtime().tm_hour
        if user_pref:
            if channel in user_pref.disabled_channels:
                raise PermissionError(f"Channel '{channel.value}' is disabled in user preferences.")
            
            if priority < user_pref.min_priority_threshold:
                raise ValueError(f"Priority '{priority}' is below minimum user threshold '{user_pref.min_priority_threshold}'.")

            if priority != NotificationPriority.URGENT and self.is_in_quiet_hours(user_pref, current_hour):
                priority = NotificationPriority.LOW

        notif_id = f"notif_{int(time.time() * 1000)}"
        record = NotificationRecord(
            notification_id=notif_id,
            sender=sender,
            recipient=recipient,
            channel=channel,
            priority=priority,
            title=title,
            content=content,
            status=DeliveryStatus.QUEUED,
            correlation_id=correlation_id
        )

        self.queue.append(record)
        self.queue.sort(key=lambda x: x.priority.value, reverse=True)
        self.history[notif_id] = record
        return record

    async def process_queue(self) -> int:
        """Processes queued notifications in priority order using registered adapters."""
        delivered_count = 0
        while self.queue:
            record = self.queue.pop(0)
            adapter = self.provider_adapters.get(record.channel)

            success = False
            if adapter:
                try:
                    success = await adapter(record)
                except Exception:
                    success = False

            if success:
                record.status = DeliveryStatus.DELIVERED
                delivered_count += 1
            else:
                if record.retry_count < record.max_retries:
                    record.retry_count += 1
                    record.status = DeliveryStatus.RETRYING
                    await asyncio.sleep(0.01)
                    self.queue.append(record)
                else:
                    record.status = DeliveryStatus.FAILED

            self.history[record.notification_id] = record

        return delivered_count
