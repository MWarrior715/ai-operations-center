"""Sales Agent: qualifies commercial fit and assigns priority."""

from __future__ import annotations

from agents.base import BaseAgent


SYSTEM_PROMPT = """You are a Sales Agent in an AI Operations Center.

Evaluate the B2B lead and return a structured JSON with:
- "priority": "Alta", "Media" or "Baja"
- "fit_score": integer 1-100
- "reasoning": short explanation in Spanish
- "next_action": concrete next step for the sales team

Respond ONLY with the JSON object. Do not add markdown formatting."""


class SalesAgent(BaseAgent):
    name = "sales"

    async def run(self) -> None:
        await self.emit("started", f"{self.name} agent started", {})
        self.state.touch_agent(self.name, "running")

        research = self.state.agents.get("research", {}).payload or {}
        user = (
            "Qualify this lead using the research context. Return JSON.\n\n"
            f"Lead:\n{self.dumps(self.state.lead.model_dump())}\n\n"
            f"Research:\n{self.dumps(research)}"
        )
        result = self.llm_json(SYSTEM_PROMPT, user)

        self.state.touch_agent(self.name, "completed", result)
        await self.emit("completed", f"{self.name} agent completed", result)
