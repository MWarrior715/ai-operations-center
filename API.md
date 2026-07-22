# AI Operations Center — API

> Referencia técnica de la interfaz del PoC: consola CLI, servidor FastAPI y stream WebSocket.
> Todos los ejemplos asumen que el entorno virtual está activado y las dependencias instaladas (`pip install -r requirements.txt`).

---

## CLI

Entrada principal: `cli.py`. Ejecuta una operación completa sobre un lead y muestra el stream de eventos en vivo seguido del reporte final.

### Argumentos y flags

| Flag       | Tipo    | Descripción                                                                                          | Default                                  |
|------------|---------|------------------------------------------------------------------------------------------------------|------------------------------------------|
| `--lead`   | `Path`  | Ruta a un archivo JSON con el lead. Si se omite, se usa un lead sintético embebido en `cli.py`.      | Lead sintético `Carolina Mendoza`        |
| `--output` | `Path`  | Ruta donde escribir el estado completo de la operación en JSON.                                     | No escribir archivo; imprimir a stdout   |
| `--quiet`  | flag    | Imprime solo el stream de eventos en vivo y el reporte final; omite el estado completo en stdout.   | `false`                                  |

### Ejemplo: ejecución de los 4 agentes concurrentes

```bash
python cli.py --lead data/sample-lead.json --output outputs/operation.json
```

Salida esperada (stream en vivo + reporte final):

```text
TARGET AI Operations Center | operation op-d2952264
IN  Lead: Andrés Ríos @ Constructora Horizonte
GO  Launching agents...

[START] [research    ] started    | research agent started
[START] [sales       ] started    | sales agent started
[START] [scheduler   ] started    | scheduler agent started
[DONE]  [research    ] completed  | research agent completed
[DONE]  [sales       ] completed  | sales agent completed
[DONE]  [scheduler   ] completed  | scheduler agent completed
[START] [reporting   ] started    | reporting agent started
[DONE]  [reporting   ] completed  | reporting agent completed

FINAL REPORT:
{
  "executive_summary": "...",
  "key_metrics": {"fit_score": 80, "priority": "Alta", "slots_offered": 2},
  "recommended_actions": ["Confirmar slot", "Preparar demo corta", "Verificar autoridad de decisión"]
}

SAVED Result saved to outputs/operation.json
```

> Notas de concurrencia: `research`, `sales` y `scheduler` se lanzan en paralelo con `asyncio.gather`. `reporting` se ejecuta en una segunda fase una vez que los tres anteriores terminan, para sintetizar el reporte ejecutivo.

### Ejemplos adicionales

```bash
# Lead sintético por defecto, salida completa en stdout
python cli.py

# Solo stream + reporte final (sin estado completo)
python cli.py --quiet
```

---

## REST (FastAPI)

Servidor: `app.py` (FastAPI). Expone la operación completa como endpoint HTTP y un stream de eventos vía WebSocket.

### Levantar el servidor

```bash
uvicorn app:app --reload
```

Por defecto el servidor escucha en `http://127.0.0.1:8000`. La documentación interactiva está disponible en `/docs` (Swagger UI) y `/redoc`.

### Endpoints HTTP

| Método | Ruta     | Descripción                                                                 | Body                                              |
|--------|----------|-----------------------------------------------------------------------------|---------------------------------------------------|
| `GET`  | `/health`| Health check del servicio.                                                  | —                                                 |
| `GET`  | `/run`   | Ejecuta la operación con el lead sintético por defecto.                     | —                                                 |
| `POST` | `/run`   | Ejecuta la operación con un lead JSON enviado en el body.                   | `LeadPayload` (opcional)                          |

Modelo `LeadPayload` (Pydantic):

| Campo      | Tipo   | Requerido | Default          |
|------------|--------|-----------|------------------|
| `name`     | string | sí        | —                |
| `company`  | string | sí        | —                |
| `need`     | string | sí        | —                |
| `budget`   | string | sí        | —                |
| `timeline` | string | no        | `""`             |
| `source`   | string | no        | `"api"`          |

### Ejemplos curl

#### `GET /health`

```bash
curl -s http://127.0.0.1:8000/health
```

```json
{"status": "ok", "service": "AI Operations Center"}
```

#### `GET /run`

```bash
curl -s http://127.0.0.1:8000/run
```

Respuesta representativa (estado completo de la operación, `OperationState`):

```json
{
  "operation_id": "op-d2952264",
  "lead": {
    "name": "Carolina Mendoza",
    "company": "LogiTech Andina",
    "need": "Automatizar el seguimiento de leads entrantes y reducir el tiempo de respuesta comercial.",
    "budget": "$4,000 - $6,000 USD",
    "timeline": "4-6 semanas",
    "source": "ops-center-demo"
  },
  "started_at": "2026-07-22T13:45:00.000000+00:00",
  "finished_at": "2026-07-22T13:45:08.000000+00:00",
  "agents": {
    "research":   {"agent": "research",   "status": "completed", "started_at": "...", "finished_at": "...", "payload": {"company_summary": "...", "key_points": ["..."], "sources": ["..."]}},
    "sales":      {"agent": "sales",      "status": "completed", "started_at": "...", "finished_at": "...", "payload": {"priority": "Alta", "fit_score": 80, "reasoning": "...", "next_action": "..."}},
    "scheduler":  {"agent": "scheduler",  "status": "completed", "started_at": "...", "finished_at": "...", "payload": {"proposed_slots": ["2026-07-24T10:00:00-05:00", "2026-07-24T15:00:00-05:00"], "notes": "Horario sugerido en zona Colombia (GMT-5)."}},
    "reporting":  {"agent": "reporting",  "status": "completed", "started_at": "...", "finished_at": "...", "payload": {"executive_summary": "...", "key_metrics": {"fit_score": 80, "priority": "Alta", "slots_offered": 2}, "recommended_actions": ["Confirmar slot", "Preparar demo corta", "Verificar autoridad de decisión"]}}
  },
  "events": [
    {"operation_id": "op-d2952264", "agent": "research",  "event_type": "started",   "message": "research agent started",   "payload": {}, "timestamp": "..."},
    {"operation_id": "op-d2952264", "agent": "research",  "event_type": "completed", "message": "research agent completed", "payload": {"...": "..."}, "timestamp": "..."}
  ],
  "final_report": {
    "executive_summary": "Lead calificado con buen fit. Se recomienda llamada de descubrimiento esta semana.",
    "key_metrics": {"fit_score": 80, "priority": "Alta", "slots_offered": 2},
    "recommended_actions": ["Confirmar slot", "Preparar demo corta", "Verificar autoridad de decisión"]
  }
}
```

#### `POST /run`

```bash
curl -s -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Andrés Ríos",
    "company": "Constructora Horizonte",
    "need": "Sistema de clasificación automática de oportunidades comerciales para su equipo de ventas.",
    "budget": "$3,000 - $5,000 USD",
    "timeline": "6 semanas",
    "source": "LinkedIn"
  }'
```

La respuesta sigue el mismo esquema `OperationState` que `GET /run`, con el `lead` y los `agents` correspondientes al lead enviado.

---

## WebSocket

Endpoint: `ws://127.0.0.1:8000/ws`

Stream en tiempo real de los eventos de la operación. Al conectar, el servidor crea un `OperationCenter` con el lead sintético por defecto, suscribe un listener al `EventBus` y ejecuta la operación. Cada evento publicado se envía como un mensaje JSON. La conexión se cierra al finalizar la operación.

### Mensajes emitidos

#### `status` (inicio y fin de operación)

Enviado por el handler del WebSocket (no por un agente) al iniciar y al completar la operación.

```json
{"type": "status", "message": "operation started", "operation_id": "op-d2952264"}
```

```json
{"type": "status", "message": "operation completed"}
```

#### Eventos de agente (`event_type`: `started` | `completed` | `failed` | `updated` | `report`)

Cada evento es un objeto `Event` serializado con `to_dict()`:

| Campo          | Tipo    | Descripción                                                                                  |
|----------------|---------|----------------------------------------------------------------------------------------------|
| `operation_id` | string  | Identificador de la operación (`op-<8 hex chars>`).                                          |
| `agent`        | string  | Nombre del agente: `research`, `sales`, `scheduler`, `reporting`.                            |
| `event_type`   | string  | `started`, `updated`, `completed`, `failed`, `report`.                                       |
| `message`      | string  | Mensaje legible, p. ej. `research agent started`, `research agent completed`.                |
| `payload`      | object  | Carga útil del evento. En `completed` contiene el resultado JSON producido por el agente.    |
| `timestamp`    | string  | Marca temporal ISO-8601 UTC.                                                                 |

Ejemplo de evento `started`:

```json
{
  "operation_id": "op-d2952264",
  "agent": "research",
  "event_type": "started",
  "message": "research agent started",
  "payload": {},
  "timestamp": "2026-07-22T13:45:00.123456+00:00"
}
```

Ejemplo de evento `completed` con payload:

```json
{
  "operation_id": "op-d2952264",
  "agent": "sales",
  "event_type": "completed",
  "message": "sales agent completed",
  "payload": {
    "priority": "Alta",
    "fit_score": 80,
    "reasoning": "Necesidad clara y presupuesto alineado. Plazo razonable.",
    "next_action": "Agendar llamada de descubrimiento."
  },
  "timestamp": "2026-07-22T13:45:04.987654+00:00"
}
```

#### `error`

Enviado si la operación falla antes de completarse:

```json
{"type": "error", "message": "<descripción del error>"}
```

### Conexión con `websocat`

```bash
websocat ws://127.0.0.1:8000/ws
```

### Conexión con un cliente JavaScript

```javascript
const ws = new WebSocket("ws://127.0.0.1:8000/ws");

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === "status" || data.type === "error") {
    console.log(`[${data.type}] ${data.message}`);
  } else {
    console.log(`[${data.event_type}] [${data.agent}] ${data.message}`);
  }
};

ws.onclose = () => console.log("connection closed");
```

---

## Modelo de agentes y EventBus

### EventBus

`core/events.py` define un bus de eventos async-safe en memoria.

- **`Event`** — dataclass con `operation_id`, `agent`, `event_type`, `message`, `payload`, `timestamp`. Método `to_dict()` para serialización.
- **`EventBus`** — mantiene una lista de listeners (sync o async). `subscribe(listener)` registra un consumer; `publish(event)` lo notifica. Los listeners se ejecutan dentro de un `asyncio.Lock` para evitar condiciones de carrera. Las excepciones en un listener se capturan y se ignoran, de modo que un consumer roto no rompe el bus.

### Agentes

`agents/base.py` define `BaseAgent`. Cada agente recibe `OperationState`, `EventBus` y `LLMProvider`; emite eventos vía `emit(event_type, message, payload)` y actualiza el estado compartido con `state.touch_agent(name, status, payload)`. Las llamadas al Motor de IA se aíslan en `llm_json(system, user, temperature)` que pide respuesta en modo JSON.

| Agente       | `name`       | Fase | Salida principal (payload)                                                                                          |
|--------------|--------------|------|---------------------------------------------------------------------------------------------------------------------|
| Research     | `research`   | 1    | `company_summary`, `key_points[]`, `sources[]`                                                                       |
| Sales        | `sales`      | 1    | `priority` (`Alta`/`Media`/`Baja`), `fit_score` (1-100), `reasoning`, `next_action`                                  |
| Scheduler    | `scheduler`  | 1    | `proposed_slots[]` (ISO-8601), `notes`                                                                               |
| Reporting    | `reporting`  | 2    | `executive_summary`, `key_metrics{}`, `recommended_actions[]`                                                        |

### OperationCenter

`orchestrator/center.py` coordina la operación:

1. **Fase 1** — lanza `research`, `sales` y `scheduler` concurrentemente con `asyncio.gather(..., return_exceptions=True)`. Cualquier agente que quede en estado `running` se marca como `failed` y se publica el evento correspondiente.
2. **Fase 2** — ejecuta `ReportingAgent` para sintetizar los resultados de los agentes anteriores en un reporte ejecutivo.
3. **Finalización** — llama a `state.finalize(report)` con el payload del agente `reporting` y devuelve el `OperationState` completo.

### Proveedor de IA

`providers/llm.py` expone `LLMProvider`, un cliente delgado sobre un endpoint **OpenAI-compatible** (`base_url`, `api_key`, `model` configurables vía `.env`). Si la conexión falla, se usa un fallback determinista embebido para que las demos funcionen sin un motor activo. El resto del códigobase es agnóstico al backend.