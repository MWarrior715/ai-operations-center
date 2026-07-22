# Arquitectura — AI Operations Center

## Visión general

Sistema multi-agente con estado compartido y observabilidad en tiempo real. Un orquestador central lanza agentes especializados de forma concurrente, cada uno lee y escribe en un `OperationState`, y emite eventos a un `EventBus` que puede ser consumido por la CLI, un WebSocket o cualquier otro observador.

```text
                         ┌────────────────────────────────────────┐
                         │         AI Operations Center           │
                         │     (orchestrator/center.py)           │
                         │                                        │
│  Lead JSON  │──────────▶│  ┌─────────┐ ┌───────┐ ┌──────────┐  │
│  WebSocket  │◀──────────│  │ Research│ │ Sales │ │Scheduler │  │
│  HTTP API   │◀──────────│  │  Agent  │ │ Agent │ │  Agent   │  │
│  CLI        │◀──────────│  └────┬────┘ └───┬───┘ └────┬─────┘  │
                         │       └─────────┬┴──────────┘       │
                         │                 │                      │
                         │         ┌───────▼────────┐             │
                         │         │ OperationState │             │
                         │         │   + EventBus   │             │
                         │         └───────┬────────┘             │
                         │                 │                      │
                         │       ┌─────────▼──────────┐           │
                         │       │   Reporting Agent   │           │
                         │       │  (resumen final)    │           │
                         │       └─────────┬──────────┘           │
                         │                 │                      │
                         └─────────────────▼──────────────────────┘
                                           │
                                    ┌──────▼──────┐
                                    │ Motor de IA │
                                    │Local/Cloud  │
                                    └─────────────┘
```

## Componentes

### 1. `config.py`
Carga variables de entorno desde `.env`. Expone `settings` como objeto plano.

### 2. `providers/llm.py`
Wrapper OpenAI-compatible con:
- chat completions,
- salida JSON forzada,
- parsing tolerante,
- fallback determinista por tipo de agente cuando el motor no responde.

### 3. `core/state.py`
Modelos Pydantic:
- `Lead`: entrada del lead.
- `AgentResult`: resultado y estado de un agente.
- `OperationState`: estado central compartido, eventos, timestamps y reporte final.

### 4. `core/events.py`
- `Event`: evento de ciclo de vida del agente.
- `EventBus`: bus async-safe con suscriptores. Permite que CLI y WebSocket reaccionen a eventos sin acoplar a los agentes.

### 5. `agents/base.py`
`BaseAgent` define:
- `run()` abstracto.
- `emit()` para publicar eventos.
- `llm_json()` helper para llamar al motor.
- `dumps()` para serializar payloads.

### 6. Agentes especializados
- `ResearchAgent`: resumen de empresa + puntos clave.
- `SalesAgent`: prioridad, fit score, razón y siguiente acción.
- `SchedulerAgent`: slots propuestos + notas de zona horaria.
- `ReportingAgent`: resumen ejecutivo, métricas y acciones recomendadas.

### 7. `orchestrator/center.py`
`OperationCenter`:
1. Crea `OperationState` y `EventBus`.
2. Lanza Research, Sales y Scheduler de forma **concurrente** con `asyncio.gather`.
3. Espera resultados.
4. Ejecuta Reporting Agent sobre el estado completo.
5. Finaliza la operación.

### 8. `cli.py`
Consola que:
- Suscribe `console_listener` al bus de eventos.
- Muestra eventos en tiempo real con etiquetas `[START]`, `[DONE]`, `[FAIL]`.
- Imprime el reporte ejecutivo final.
- Puede guardar el estado completo en JSON.

### 9. `app.py`
FastAPI con:
- `GET /health`
- `GET /run` y `POST /run`
- `WS /ws` que transmite eventos en vivo.

## Flujo de datos

1. Entrada: lead JSON.
2. `OperationCenter` inicializa estado y bus.
3. Se lanzan 3 tareas async (research, sales, scheduler).
4. Cada agente:
   - emite `started`,
   - lee estado previo si lo necesita,
   - llama al Motor de IA,
   - escribe su resultado en `OperationState`,
   - emite `completed`.
5. Cuando los 3 terminan, `ReportingAgent` genera el resumen ejecutivo.
6. Estado final se expone como JSON.

## Concurrencia

Los agentes se ejecutan concurrentemente con `asyncio.gather`. Cada agente es principalmente I/O-bound (LLM), por lo que el patrón es adecuado. Si el Motor de IA local solo procesa una solicitud a la vez, las llamadas se serializarán en el backend, pero la arquitectura del centro de operaciones está preparada para paralelismo real.

## Seguridad y configuración

- Configuración del Motor de IA en `.env` (gitignored).
- `.env.example` como plantilla genérica.
- Sin credenciales en el repo.

## Escalabilidad futura

- Persistencia del estado en SQLite/Postgres.
- Cola de operaciones pendientes.
- Más agentes: follow-up, CRM sync, emailer.
- Dashboard web con WebSocket.
