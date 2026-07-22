"""Research Agent: gathers context about the lead's company and need."""

from __future__ import annotations

from agents.base import BaseAgent


SYSTEM_PROMPT = """You are a Research Agent in an AI Operations Center.

Your task is to research a B2B lead and return a structured JSON with:
- "company_summary": 1-2 sentence summary of the company inferred from the lead data
- "key_points": list of strings with relevant insights for the sales team
- "sources": list of simulated sources (e.g., "company website", "public profile")

Respond ONLY with the JSON object. Do not add markdown formatting."""


class ResearchAgent(BaseAgent):
    name = "research"

    async def run(self) -> None:
        await self.emit("started", f"{self.name} agent started", {})
        self.state.touch_agent(self.name, "running")

        user = (
            "Research this lead and return JSON.\n\n"
            f"{self.dumps(self.state.lead.model_dump())}"
        )
        result = self.llm_json(SYSTEM_PROMPT, user)

        self.state.touch_agent(self.name, "completed", result)
        await self.emit("completed", f"{self.name} agent completed", result)
