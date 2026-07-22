# Changelog — AI Operations Center

## [0.1.0] - 2026-07-22

### Added

- MVP del AI Operations Center con 4 agentes colaborativos.
- `core/state.py`: modelos `Lead`, `AgentResult`, `OperationState`.
- `core/events.py`: `Event` + `EventBus` async-safe.
- `providers/llm.py`: proveedor OpenAI-compatible con fallback por tipo de agente.
- `agents/base.py`: clase base para agentes.
- Agentes especializados: `ResearchAgent`, `SalesAgent`, `SchedulerAgent`, `ReportingAgent`.
- `orchestrator/center.py`: `OperationCenter` que ejecuta agentes concurrentemente.
- `cli.py`: consola en tiempo real con eventos ASCII.
- `app.py`: FastAPI + WebSocket para demos en vivo.
- Tests con `pytest` y `pytest-asyncio`.
- Documentación inicial: README, ARCHITECTURE, DECISIONS, ROADMAP, LICENSE.
- Lead de ejemplo en `data/sample-lead.json`.
