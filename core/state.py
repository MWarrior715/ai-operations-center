"""Shared state models for the AI Operations Center."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Lead(BaseModel):
    name: str
    company: str
    need: str
    budget: str
    timeline: str = ""
    source: str = "ops-center"


class AgentResult(BaseModel):
    agent: str
    status: str = "pending"  # pending, running, completed, failed
    started_at: str | None = None
    finished_at: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class OperationState(BaseModel):
    """Central, shared, observable state for one operation run."""

    operation_id: str
    lead: Lead
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str | None = None
    agents: dict[str, AgentResult] = Field(default_factory=dict)
    events: list[dict[str, Any]] = Field(default_factory=list)
    final_report: dict[str, Any] | None = None

    def touch_agent(self, agent: str, status: str | None = None, payload: dict[str, Any] | None = None) -> AgentResult:
        now = datetime.now(timezone.utc).isoformat()
        if agent not in self.agents:
            self.agents[agent] = AgentResult(agent=agent, status="pending")
        result = self.agents[agent]
        if status:
            result.status = status
        if status == "running" and result.started_at is None:
            result.started_at = now
        if status in ("completed", "failed"):
            result.finished_at = now
        if payload is not None:
            result.payload = payload
        return result

    def finalize(self, final_report: dict[str, Any] | None = None) -> None:
        self.finished_at = datetime.now(timezone.utc).isoformat()
        if final_report is not None:
            self.final_report = final_report
