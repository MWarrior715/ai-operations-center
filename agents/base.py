"""Base class for all operations center agents."""

from __future__ import annotations

import json
from typing import Any

from core.events import Event, EventBus
from core.state import OperationState
from providers.llm import LLMProvider


class BaseAgent:
    name: str = "base"

    def __init__(
        self,
        state: OperationState,
        bus: EventBus,
        provider: LLMProvider,
    ) -> None:
        self.state = state
        self.bus = bus
        self.provider = provider

    async def run(self) -> None:
        """Implement in subclasses. Must update state and emit events."""
        raise NotImplementedError

    async def emit(self, event_type: str, message: str, payload: dict[str, Any] | None = None) -> None:
        event = Event(
            operation_id=self.state.operation_id,
            agent=self.name,
            event_type=event_type,
            message=message,
            payload=payload or {},
        )
        await self.bus.publish(event)
        self.state.events.append(event.to_dict())

    def llm_json(self, system: str, user: str, temperature: float = 0.3) -> dict[str, Any]:
        return self.provider.complete(system, user, temperature=temperature, json_mode=True)

    @staticmethod
    def dumps(obj: Any) -> str:
        return json.dumps(obj, ensure_ascii=False, indent=2)
