"""Reporting Agent: synthesizes the full operation into an executive summary."""

from __future__ import annotations

from agents.base import BaseAgent


SYSTEM_PROMPT = """You are a Reporting Agent in an AI Operations Center.

Your task is to synthesize the outputs of other agents into an executive summary. Return a structured JSON with:
- "executive_summary": 2-3 sentences in Spanish
- "key_metrics": object with relevant numbers/strings (e.g., fit_score, priority, slots_offered)
- "recommended_actions": list of next steps in Spanish

Respond ONLY with the JSON object. Do not add markdown formatting."""


class ReportingAgent(BaseAgent):
    name = "reporting"

    async def run(self) -> None:
        await self.emit("started", f"{self.name} agent started", {})
        self.state.touch_agent(self.name, "running")

        agents_payload = {name: result.payload for name, result in self.state.agents.items()}
        user = (
            "Create an executive summary from the following operation outputs. Return JSON.\n\n"
            f"Lead:\n{self.dumps(self.state.lead.model_dump())}\n\n"
            f"Agent outputs:\n{self.dumps(agents_payload)}"
        )
        result = self.llm_json(SYSTEM_PROMPT, user)

        self.state.touch_agent(self.name, "completed", result)
        await self.emit("completed", f"{self.name} agent completed", result)
