"""Tests for the LLM provider."""

from __future__ import annotations

import json

from providers.llm import LLMProvider


def test_fallback_per_agent():
    provider = LLMProvider(fallback_on_error=True)
    research = json.loads(provider._fallback("You are a research agent", ""))
    assert "company_summary" in research
    sales = json.loads(provider._fallback("You are a sales agent", ""))
    assert "fit_score" in sales


def test_extract_json():
    provider = LLMProvider(fallback_on_error=True)
    text = 'Here is the result:\n{"fit_score": 90}\nThanks!'
    result = provider._extract_json(text)
    assert result["fit_score"] == 90
