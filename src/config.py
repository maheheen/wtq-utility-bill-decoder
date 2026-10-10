"""Env and model settings. Only the five allowed models can be configured."""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = ROOT / ".cache"

# provider -> allowed model names
ALLOWED = {
    "google": {"gemini-3.5-flash-lite", "gemini-3.1-flash-lite"},
    "openai": {"gpt-4.1-mini", "gpt-5-mini"},
    "anthropic": {"claude-haiku-4-5"},
}
NO_TEMPERATURE = {"gpt-5-mini"}


@dataclass(frozen=True)
class ModelCfg:
    provider: str
    model: str
    api_key: str
    temperature: float | None  # None = parameter not sent


def load_config() -> ModelCfg:
    load_dotenv(ROOT / ".env")
    provider = os.environ.get("MODEL_PROVIDER", "").strip().lower()
    model = os.environ.get("MODEL_NAME", "").strip()
    api_key = os.environ.get("API_KEY", "").strip()
    if provider not in ALLOWED:
        raise ValueError(f"MODEL_PROVIDER must be one of {sorted(ALLOWED)}, got {provider!r}")
    if model not in ALLOWED[provider]:
        raise ValueError(f"MODEL_NAME {model!r} is not an allowed {provider} model: {sorted(ALLOWED[provider])}")
    if not api_key:
        raise ValueError("API_KEY is empty, set it in .env")
    return ModelCfg(provider, model, api_key, None if model in NO_TEMPERATURE else 0.0)
