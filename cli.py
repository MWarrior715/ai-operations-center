"""Command-line console for the AI Operations Center.

Displays a live event stream while agents run, then prints the final state.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from core.events import Event
from core.state import Lead
from orchestrator.center import OperationCenter


DEFAULT_LEAD = {
    "name": "Carolina Mendoza",
    "company": "LogiTech Andina",
    "need": "Automatizar el seguimiento de leads entrantes y reducir el tiempo de respuesta comercial.",
    "budget": "$4,000 - $6,000 USD",
    "timeline": "4-6 semanas",
    "source": "ops-center-demo",
}


def load_lead(path: Path) -> dict:
    if not path.exists():
        print(f"Lead file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_output(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nSAVED Result saved to {path}")


def console_listener(event: Event) -> None:
    """Print agent events as they happen."""
    icon = {
        "started": "[START]",
        "completed": "[DONE]",
        "failed": "[FAIL]",
        "updated": "[UPDT]",
        "report": "[RPT]",
    }.get(event.event_type, "[    ]")
    print(f"{icon} [{event.agent:12}] {event.event_type:10} | {event.message}")


async def main_async(args: argparse.Namespace) -> int:
    lead_data = load_lead(args.lead) if args.lead else DEFAULT_LEAD.copy()
    lead = Lead(**lead_data)
    center = OperationCenter(lead=lead)
    center.bus.subscribe(console_listener)

    print(f"TARGET AI Operations Center | operation {center.operation_id}")
    print(f"IN  Lead: {lead.name} @ {lead.company}")
    print("GO  Launching agents...\n")

    state = await center.run()

    print("\nFINAL REPORT:")
    report = state.final_report or {}
    print(json.dumps(report, ensure_ascii=False, indent=2))

    result = state.model_dump(mode="json")
    if args.output:
        save_output(args.output, result)
    elif not args.quiet:
        print("\nFULL OPERATION STATE:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AI Operations Center — multi-agent B2B operations console",
    )
    parser.add_argument(
        "--lead",
        type=Path,
        help="Path to a JSON lead file. Uses a default synthetic lead if omitted.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to write the full operation JSON result.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only the live event stream and final report.",
    )
    args = parser.parse_args()
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())
