import asyncio
from typing import Dict, List, Callable, Any, Awaitable
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from loguru import logger


class Event(BaseModel):
    event_type: str
    sender: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


EventHandler = Callable[[Event], Awaitable[None]]


class AsyncEventBus:
    """Enterprise Async Pub/Sub Event Bus for decoupled system communication."""
    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._wildcard_subscribers: List[EventHandler] = []

    def subscribe(self, event_type: str, handler: EventHandler):
        """Subscribe an async handler to a specific event_type or '*' for all events."""
        if event_type == "*":
            self._wildcard_subscribers.append(handler)
        else:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)
        logger.debug(f"EventBus: Subscribed handler to event '{event_type}'")

    async def publish(self, event_type: str, sender: str, payload: Dict[str, Any] = None):
        """Publish an event to all subscribed handlers asynchronously."""
        event = Event(event_type=event_type, sender=sender, payload=payload or {})
        logger.info(f"EventBus [PUBLISH] -> Type: '{event.event_type}' | Sender: '{event.sender}'")

        handlers = self._subscribers.get(event_type, []) + self._wildcard_subscribers
        if handlers:
            tasks = [asyncio.create_task(handler(event)) for handler in handlers]
            await asyncio.gather(*tasks, return_exceptions=True)


# Global Singleton Event Bus Instance
event_bus = AsyncEventBus()
