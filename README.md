# AI Operations Center

> **PoC 05 — AI Product Lab**  
> Consola central de agentes colaborativos: varios agentes de IA trabajan simultáneamente sobre una misma oportunidad de negocio, con observabilidad en tiempo real.

## ¿Qué demuestra?

En una demo de 10 minutos este repositorio responde la pregunta clave de un CTO:

**"¿Puede diseñar ecosistemas AI de producción?"**

El sistema lanza 4 agentes especializados sobre un lead B2B:

1. **Research Agent** — investiga la empresa y el contexto de la necesidad.
2. **Sales Agent** — evalúa fit comercial y asigna prioridad.
3. **Scheduler Agent** — propone horarios para una llamada de descubrimiento.
4. **Reporting Agent** — sintetiza todo en un resumen ejecutivo.

Cada agente lee y escribe en un **estado compartido**, mientras una consola muestra eventos en vivo.

## Stack

- **Python puro + asyncio** — concurrencia real sin plataformas visuales.
- **Motor de IA Local/Cloud** vía API OpenAI-compatible (configurable en `.env`).
- **Pydantic** para modelos de estado robustos.
- **FastAPI + WebSocket** para demos remotas en vivo.
- **pytest + pytest-asyncio** para tests.

## Estructura

```text
ai-operations-center/
├── agents/                 # 4 agentes especializados + base
├── core/                   # Estado compartido y bus de eventos
├── orchestrator/           # OperationCenter: coordina agentes
├── providers/              # Cliente genérico del Motor de IA
├── tests/                  # Tests unitarios y de API
├── data/sample-lead.json   # Lead de ejemplo
├── cli.py                  # Consola principal
├── app.py                  # FastAPI + WebSocket
├── config.py               # Configuración desde .env
└── docs/                   # README, ARCHITECTURE, etc.
```

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copia `.env.example` a `.env` y ajusta los valores de tu Motor de IA Local/Cloud:

```bash
cp .env.example .env
```

## Uso

### CLI — lead sintético por defecto

```bash
python cli.py
```

### CLI — solo el flujo y el reporte final

```bash
python cli.py --quiet
```

### CLI — lead personalizado desde archivo

```bash
python cli.py --lead data/sample-lead.json --output outputs/operation.json
```

### FastAPI + WebSocket (demo en vivo)

```bash
uvicorn app:app --reload
```

Endpoints:

- `GET  /health` — health check.
- `GET  /run` — ejecuta la operación con el lead por defecto.
- `POST /run` — ejecuta la operación con un lead JSON en el body.
- `WS   /ws` — stream de eventos en tiempo real.

## Salida de ejemplo

```text
TARGET AI Operations Center | operation op-d2952264
IN  Lead: Carolina Mendoza @ LogiTech Andina
GO  Launching agents...

[START] [research    ] started    | research agent started
[DONE]  [research    ] completed  | research agent completed
[START] [sales       ] started    | sales agent started
[DONE]  [sales       ] completed  | sales agent completed
[START] [scheduler   ] started    | scheduler agent started
[DONE]  [scheduler   ] completed  | scheduler agent completed
[START] [reporting   ] started    | reporting agent started
[DONE]  [reporting   ] completed  | reporting agent completed

FINAL REPORT:
{
  "executive_summary": "...",
  "key_metrics": {"fit_score": 90, "priority": "Alta", ...},
  "recommended_actions": [...]
}
```

## Tests

```bash
pytest -v
```

Incluye mocks del proveedor LLM para ejecución determinista sin motor activo, y tests de los endpoints FastAPI.

## Documentación adicional

- [`ARCHITECTURE.md`](ARCHITECTURE.md) — diseño técnico y flujo de datos.
- [`DECISIONS.md`](DECISIONS.md) — decisiones de diseño y trade-offs.
- [`ROADMAP.md`](ROADMAP.md) — evolución planeada.
- [`CHANGELOG.md`](CHANGELOG.md) — historial de cambios.
- [`LICENSE`](LICENSE) — licencia MIT.

## Autor

**Manuel Guerrero — AI Product Builder & Systems Integrator**

Parte del AI Product Lab: pruebas de concepto diseñadas para demostrar capacidades reales de producto con IA.
