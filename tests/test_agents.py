"""Tests for individual agents."""

from __future__ import annotations

import pytest

from agents.research import ResearchAgent
from agents.sales import SalesAgent
from agents.scheduler import SchedulerAgent
from agents.reporting import ReportingAgent
from core.events import EventBus
from core.state import Lead, OperationState


@pytest.fixture
def fresh_state():
    return OperationState(operation_id="op-test", lead=Lead(name="T", company="C", need="N", budget="B"))


@pytest.fixture
def fresh_bus():
    return EventBus()


@pytest.mark.asyncio
async def test_research_agent(fake_provider, fresh_state, fresh_bus):
    await ResearchAgent(fresh_state, fresh_bus, fake_provider).run()
    assert fresh_state.agents["research"].status == "completed"
    assert fresh_state.agents["research"].payload["company_summary"]


@pytest.mark.asyncio
async def test_sales_agent(fake_provider, fresh_state, fresh_bus):
    # Seed research output so sales has context.
    fresh_state.touch_agent("research", "completed", {"company_summary": "cs"})
    await SalesAgent(fresh_state, fresh_bus, fake_provider).run()
    assert fresh_state.agents["sales"].status == "completed"
    assert fresh_state.agents["sales"].payload["fit_score"] == 85


@pytest.mark.asyncio
async def test_scheduler_agent(fake_provider, fresh_state, fresh_bus):
    fresh_state.touch_agent("sales", "completed", {"priority": "Alta"})
    await SchedulerAgent(fresh_state, fresh_bus, fake_provider).run()
    assert fresh_state.agents["scheduler"].status == "completed"
    assert len(fresh_state.agents["scheduler"].payload["proposed_slots"]) >= 1


@pytest.mark.asyncio
async def test_reporting_agent(fake_provider, fresh_state, fresh_bus):
    fresh_state.touch_agent("research", "completed", {"company_summary": "cs"})
    fresh_state.touch_agent("sales", "completed", {"fit_score": 85})
    fresh_state.touch_agent("scheduler", "completed", {"proposed_slots": []})
    await ReportingAgent(fresh_state, fresh_bus, fake_provider).run()
    assert fresh_state.agents["reporting"].status == "completed"
    assert fresh_state.agents["reporting"].payload["executive_summary"]
