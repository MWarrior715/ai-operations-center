"""OperationCenter orchestrator.

Launches multiple specialized agents concurrently over a shared state and event
bus, then synthesizes a final report. Designed for live observability demos.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

from agents.research import ResearchAgent
from agents.sales import SalesAgent
from agents.scheduler import SchedulerAgent
from agents.reporting import ReportingAgent
from core.events import EventBus
from core.state import Lead, OperationState
from providers.llm import LLMProvider, get_provider


AGENT_CLASSES = [ResearchAgent, SalesAgent, SchedulerAgent]


class OperationCenter:
    """Central coordinator for one operation run."""

    def __init__(
        self,
        lead: Lead,
        provider: LLMProvider | None = None,
        operation_id: str | None = None,
    ) -> None:
        self.operation_id = operation_id or f"op-{uuid.uuid4().hex[:8]}"
        self.state = OperationState(operation_id=self.operation_id, lead=lead)
        self.bus = EventBus()
        self.provider = provider or get_provider()

    async def run(self) -> OperationState:
        """Execute the operation and return the final state."""
        # Phase 1: run research, sales and scheduler concurrently.
        tasks = [
            agent_cls(self.state, self.bus, self.provider).run()
            for agent_cls in AGENT_CLASSES
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Mark any still-running agents as failed if an exception escaped.
        for agent_name in [cls.name for cls in AGENT_CLASSES]:
            result = self.state.agents.get(agent_name)
            if result and result.status == "running":
                self.state.touch_agent(agent_name, "failed", {"error": "Agent did not complete"})
                await self.bus.publish(
                    self._event(agent_name, "failed", "Agent did not complete")
                )

        # Phase 2: reporting agent synthesizes everything.
        await ReportingAgent(self.state, self.bus, self.provider).run()

        report = self.state.agents.get("reporting", AgentResult(agent="reporting")).payload
        self.state.finalize(report)
        return self.state

    def _event(self, agent: str, event_type: str, message: str) -> Any:
        from core.events import Event
        return Event(
            operation_id=self.operation_id,
            agent=agent,
            event_type=event_type,
            message=message,
        )


async def run_operation(lead_dict: dict[str, Any], provider: LLMProvider | None = None) -> dict[str, Any]:
    """High-level helper to run an operation from a raw lead dict."""
    lead = Lead(**lead_dict)
    center = OperationCenter(lead=lead, provider=provider)
    state = await center.run()
    return state.model_dump(mode="json")


# Avoid circular import issues with pydantic AgentResult reference.
from core.state import AgentResult
