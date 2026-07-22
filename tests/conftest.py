"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from core.state import Lead
from providers.llm import LLMProvider


@pytest.fixture
def fake_provider():
    """LLM provider returning deterministic JSON per agent type."""

    class FakeProvider(LLMProvider):
        def __init__(self) -> None:
            super().__init__(base_url="http://fake", api_key="fake", model="fake", fallback_on_error=False)

        def chat(self, system, user, temperature=0.3, json_mode=True) -> str:
            system_lower = system.lower()
            if "research" in system_lower:
                return '{"company_summary": "Test summary", "key_points": ["p1"], "sources": ["s1"]}'
            if "sales" in system_lower:
                return '{"priority": "Alta", "fit_score": 85, "reasoning": "Good fit", "next_action": "Call"}'
            if "reporting" in system_lower or "executive summary" in user.lower():
                return '{"executive_summary": "Good lead", "key_metrics": {"fit_score": 85}, "recommended_actions": ["Call"]}'
            if "scheduling" in system_lower or "slots" in user.lower():
                return '{"proposed_slots": ["2026-07-24T10:00:00"], "notes": "GMT-5"}'
            return '{}'

    return FakeProvider()


@pytest.fixture
def sample_lead():
    return Lead(
        name="Test Lead",
        company="Acme Corp",
        need="Automate reports",
        budget="$5k",
        timeline="2 weeks",
        source="test",
    )
