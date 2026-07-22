# Decisiones de Diseño — AI Operations Center

## 1. Python puro + asyncio

**Decisión:** No usar plataformas visuales ni frameworks de workflow. Todo es Python asyncio.

**Razón:** Demuestra capacidad de diseñar orquestación real, no solo conectar nodos. asyncio permite concurrencia real de agentes I/O-bound.

**Trade-off:** Requiere manejar manualmente el estado compartido y la sincronización.

## 2. Estado compartido en memoria

**Decisión:** Un único `OperationState` Pydantic que todos los agentes leen y escriben.

**Razón:** Es el patrón más simple que demuestra coordinación multi-agente sin introducir bases de datos o caches distribuidos. Pydantic asegura tipado y validación.

**Trade-off:** No persiste entre reinicios. Eso es aceptable para un MVP de demostración.

## 3. EventBus async-safe

**Decisión:** Bus de eventos en memoria con suscriptores, no logging directo desde los agentes.

**Razón:** Desacopla la generación de eventos de su consumo. La misma arquitectura alimenta CLI, WebSocket y tests sin cambiar agentes.

**Trade-off:** Agrega una capa de indirección, pero mínima.

## 4. 4 agentes sobre una tarea B2B

**Decisión:** Limitar a Research, Sales, Scheduler y Reporting sobre el procesamiento de un lead.

**Razón:** Evita over-engineering. El demo cuenta una historia concreta: "cómo un centro de operaciones AI califica una oportunidad". Es coherente con PoC 03 (Autonomous Workflow).

**Trade-off:** No cubre todos los agentes imaginables, pero es suficiente para demostrar arquitectura multi-agente.

## 5. Motor de IA enchufable

**Decisión:** Reutilizar el patrón OpenAI-compatible de PoC 03.

**Razón:** Consistencia técnica entre PoCs. El mismo proveedor puede usarse en todo el AI Product Lab.

## 6. Fallback determinista por agente

**Decisión:** El proveedor LLM devuelve respuestas genéricas pero coherentes por tipo de agente cuando el motor falla.

**Razón:** La demo no se rompe si el modelo local no está disponible. Mantiene la arquitectura visible.

## 7. CLI sin emojis en Windows

**Decisión:** Reemplazar emojis por etiquetas ASCII (`[START]`, `[DONE]`, etc.).

**Razón:** La consola de Windows con encoding cp1252 falla con algunos caracteres Unicode. Texto ASCII garantiza que la demo funcione en cualquier terminal.

## 8. FastAPI + WebSocket opcional

**Decisión:** Incluir servidor web para demos remotas, pero mantener CLI como interfaz principal.

**Razón:** WebSocket demuestra observabilidad en tiempo real, un punto clave para ecosistemas de producción.
