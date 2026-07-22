"""Runtime configuration for the AI Operations Center."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))


class Config:
    # Motor de IA Local/Cloud (API OpenAI-compatible)
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "not-needed-for-local")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "default-model")

    APP_NAME: str = "AI Operations Center"
    APP_VERSION: str = "0.1.0"


settings = Config()
