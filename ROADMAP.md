# Roadmap — AI Operations Center

## v0.1.0 — MVP actual ✅

- [x] 4 agentes colaborativos: Research, Sales, Scheduler, Reporting.
- [x] Estado compartido (`OperationState`) con Pydantic.
- [x] EventBus async-safe para observabilidad en tiempo real.
- [x] Orquestador concurrente con `asyncio.gather`.
- [x] CLI con stream de eventos y reporte final.
- [x] FastAPI + WebSocket opcional.
- [x] Proveedor LLM enchufable + fallback determinista.
- [x] Tests con `pytest` y `pytest-asyncio`.
- [x] Documentación: README, ARCHITECTURE, DECISIONS, ROADMAP, CHANGELOG, LICENSE.

## v0.2.0 — Persistencia y trazabilidad

- [ ] Persistir cada operación en SQLite/Postgres.
- [ ] Historial de operaciones por lead.
- [ ] Replay de una operación pasada.
- [ ] Métricas: tiempo por agente, throughput, tasa de éxito.

## v0.3.0 — Más agentes y habilidades

- [ ] Email Agent: envía propuesta generada.
- [ ] Follow-up Agent: decide cuándo reactivar un lead.
- [ ] CRM Sync Agent: conector genérico (CSV/webhook).
- [ ] Alert Agent: detecta operaciones con score bajo y escala.

## v0.4.0 — Dashboard y producción

- [ ] Dashboard web simple con Vue/React que se conecta por WebSocket.
- [ ] Autenticación básica para el dashboard.
- [ ] Docker + docker-compose para despliegue en 1 comando.
- [ ] CI/CD con tests y lint.

## v1.0.0 — Producto demo cerrado

- [ ] Demo pública desplegada.
- [ ] Video Loom de demostración.
- [ ] Link real en portafolio.
