"""Scheduler Agent: proposes meeting slots."""

from __future__ import annotations

from agents.base import BaseAgent


SYSTEM_PROMPT = """You are a Scheduling Agent in an AI Operations Center.

Propose meeting slots for a discovery call and return a structured JSON with:
- "proposed_slots": list of ISO-8601 datetime strings (next 3-5 business days)
- "notes": short text in Spanish about timezone or availability assumptions

Respond ONLY with the JSON object. Do not add markdown formatting."""


class SchedulerAgent(BaseAgent):
    name = "scheduler"

    async def run(self) -> None:
        await self.emit("started", f"{self.name} agent started", {})
        self.state.touch_agent(self.name, "running")

        sales = self.state.agents.get("sales", {}).payload or {}
        user = (
            "Propose discovery-call slots based on the qualified lead. Return JSON.\n\n"
            f"Lead:\n{self.dumps(self.state.lead.model_dump())}\n\n"
            f"Sales qualification:\n{self.dumps(sales)}"
        )
        result = self.llm_json(SYSTEM_PROMPT, user)

        self.state.touch_agent(self.name, "completed", result)
        await self.emit("completed", f"{self.name} agent completed", result)
