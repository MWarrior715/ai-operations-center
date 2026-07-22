"""Tests for the OperationCenter orchestrator."""

from __future__ import annotations

import pytest

from orchestrator.center import OperationCenter


@pytest.mark.asyncio
async def test_full_operation(fake_provider, sample_lead):
    center = OperationCenter(lead=sample_lead, provider=fake_provider, operation_id="op-xyz")
    state = await center.run()
    assert state.operation_id == "op-xyz"
    assert state.agents["research"].status == "completed"
    assert state.agents["sales"].status == "completed"
    assert state.agents["scheduler"].status == "completed"
    assert state.agents["reporting"].status == "completed"
    assert state.final_report is not None
    assert state.finished_at is not None
