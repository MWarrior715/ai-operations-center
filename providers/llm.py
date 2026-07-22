"""OpenAI-compatible LLM provider with deterministic fallback.

All LLM interactions are isolated here so the rest of the codebase is backend-
agnostic.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import APIConnectionError, APITimeoutError, OpenAI

from config import settings

logger = logging.getLogger(__name__)


class LLMProvider:
    """Thin wrapper around an OpenAI-compatible chat completion endpoint."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        fallback_on_error: bool = True,
    ) -> None:
        self.base_url = base_url or settings.OPENAI_BASE_URL
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.fallback_on_error = fallback_on_error
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(base_url=self.base_url, api_key=self.api_key)
        return self._client

    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.3,
        json_mode: bool = True,
    ) -> str:
        extra: dict[str, Any] = {}
        if json_mode:
            extra["response_format"] = {"type": "json_object"}

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                **extra,
            )
            content = response.choices[0].message.content or ""
            return content.strip()
        except (APIConnectionError, APITimeoutError) as exc:
            logger.warning("LLM connection failed: %s. Using fallback.", exc)
            return self._fallback(system, user)
        except Exception as exc:
            logger.warning("LLM request failed: %s. Using fallback.", exc)
            return self._fallback(system, user)

    def _fallback(self, system: str, user: str) -> str:
        system_lower = system.lower()
        if "research" in system_lower:
            return json.dumps({
                "company_summary": "Empresa de tecnología logística en crecimiento con operaciones en Colombia.",
                "key_points": ["Enfoque en automatización", "Presencia regional", "Presupuesto ajustado"],
                "sources": ["perfil público", "sitio web simulado"],
            })
        if "sales" in system_lower or "fit" in system_lower:
            return json.dumps({
                "priority": "Alta",
                "fit_score": 80,
                "reasoning": "Necesidad clara y presupuesto alineado. Plazo razonable.",
                "next_action": "Agendar llamada de descubrimiento.",
            })
        if "scheduler" in system_lower or "slots" in system_lower:
            return json.dumps({
                "proposed_slots": [
                    "2026-07-24T10:00:00-05:00",
                    "2026-07-24T15:00:00-05:00",
                ],
                "notes": "Horario sugerido en zona Colombia (GMT-5).",
            })
        if "reporting" in system_lower or "executive" in system_lower:
            return json.dumps({
                "executive_summary": "Lead calificado con buen fit. Se recomienda llamada de descubrimiento esta semana.",
                "key_metrics": {"fit_score": 80, "priority": "Alta", "slots_offered": 2},
                "recommended_actions": ["Confirmar slot", "Preparar demo corta", "Verificar autoridad de decisión"],
            })
        return json.dumps({"result": "fallback", "note": "LLM motor unavailable"})

    def complete(
        self,
        system: str,
        user: str,
        temperature: float = 0.3,
        json_mode: bool = True,
    ) -> dict[str, Any]:
        raw = self.chat(system, user, temperature, json_mode)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return self._extract_json(raw)

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
        return {"raw_response": text}


def get_provider() -> LLMProvider:
    return LLMProvider()
