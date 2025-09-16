# LLM provider integration
import os, httpx, json
from pathlib import Path

def load_config():
    config_path = Path(".fern/config.json")
    if config_path.exists():
        try:
            return json.loads(config_path.read_text())
        except Exception:
            return {}
    return {}

CONFIG = load_config()

def complete(prompt: str, sys: str = "", provider: str | None = None, model: str | None = None) -> str:
    provider = provider or os.getenv("LLM_PROVIDER") or CONFIG.get("LLM_PROVIDER", "ollama")
    model = model or os.getenv("LLM_MODEL") or CONFIG.get("LLM_MODEL", "qwen2.5-coder:7b")

    if provider == "ollama":
        # requires `ollama serve` running locally
        resp = httpx.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": f"{sys}\n\n{prompt}", "stream": False},
            timeout=600
        )
        resp.raise_for_status()
        return resp.json()["response"]

    raise RuntimeError(f"Unknown LLM provider: {provider}")
