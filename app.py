"""Optional FastAPI server with WebSocket event streaming.

Useful for live demos where a CTO can see agents working in real time from a
browser or API client.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from core.events import Event, EventBus
from core.state import Lead
from orchestrator.center import OperationCenter

app = FastAPI(
    title="AI Operations Center",
    version="0.1.0",
    description="Multi-agent operations console with real-time observability.",
)


class LeadPayload(BaseModel):
    name: str
    company: str
    need: str
    budget: str
    timeline: str = ""
    source: str = "api"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "AI Operations Center"}


@app.post("/run")
async def run_operation_http(lead: LeadPayload | None = None) -> dict[str, Any]:
    """Run the operation and return the full final state."""
    lead_obj = Lead(**lead.model_dump()) if lead else _default_lead()
    center = OperationCenter(lead=lead_obj)
    state = await center.run()
    return state.model_dump(mode="json")


@app.get("/run")
async def run_operation_default() -> dict[str, Any]:
    """Run the operation with the default synthetic lead."""
    center = OperationCenter(lead=_default_lead())
    state = await center.run()
    return state.model_dump(mode="json")


@app.websocket("/ws")
async def operation_websocket(websocket: WebSocket) -> None:
    """Stream operation events live via WebSocket."""
    await websocket.accept()
    lead_obj = _default_lead()
    center = OperationCenter(lead=lead_obj)

    async def ws_listener(event: Event) -> None:
        await websocket.send_json(event.to_dict())

    center.bus.subscribe(ws_listener)
    await websocket.send_json({"type": "status", "message": "operation started", "operation_id": center.operation_id})

    try:
        await center.run()
        await websocket.send_json({"type": "status", "message": "operation completed"})
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        await websocket.send_json({"type": "error", "message": str(exc)})
    finally:
        try:
            await websocket.close()
        except Exception:
            pass


def _default_lead() -> Lead:
    return Lead(
        name="Carolina Mendoza",
        company="LogiTech Andina",
        need="Automatizar el seguimiento de leads entrantes y reducir el tiempo de respuesta comercial.",
        budget="$4,000 - $6,000 USD",
        timeline="4-6 semanas",
        source="ops-center-demo",
    )
