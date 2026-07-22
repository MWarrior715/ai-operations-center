"""Event bus for observable multi-agent coordination.

The event bus is intentionally simple: it keeps all events in memory and allows
multiple consumers (CLI, WebSocket, tests) to react to agent lifecycle changes.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine


@dataclass
class Event:
    operation_id: str
    agent: str
    event_type: str  # started, updated, completed, failed, report
    message: str
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "agent": self.agent,
            "event_type": self.event_type,
            "message": self.message,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }


class EventBus:
    """Async-safe in-memory event bus."""

    def __init__(self) -> None:
        self._listeners: list[Callable[[Event], Coroutine[Any, Any, None] | None]] = []
        self._lock = asyncio.Lock()

    def subscribe(self, listener: Callable[[Event], Coroutine[Any, Any, None] | None]) -> None:
        self._listeners.append(listener)

    async def publish(self, event: Event) -> None:
        async with self._lock:
            listeners = list(self._listeners)
        for listener in listeners:
            try:
                result = listener(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                # Consumers must not break the bus.
                pass
