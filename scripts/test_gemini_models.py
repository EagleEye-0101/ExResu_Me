"""Test Google AI Studio models (flash + high tiers). Run from project root."""
import asyncio
import sys

from resume_engine.ai.router import test_provider
from resume_engine.db import database
from resume_engine.db.settings_store import get_runtime_config

MODELS = [
    ("high", "gemini-2.5-pro"),
    ("high", "gemini-3.1-pro-preview"),
    ("high", "gemini-3-pro-preview"),
    ("high", "gemini-pro-latest"),
    ("flash", "gemini-2.5-flash"),
    ("flash", "gemini-flash-latest"),
    ("flash", "gemini-2.5-flash-lite"),
    ("flash", "gemini-3-flash-preview"),
    ("flash", "gemini-3.1-flash-lite-preview"),
]


async def main() -> int:
    database.init_db()
    db = database._SessionLocal()
    cfg = get_runtime_config(db)
    db.close()
    if not cfg.get("gemini_api_key"):
        print("No gemini_api_key in Settings DB or .env")
        return 1
    for tier, model in MODELS:
        c = {**cfg, "gemini_model": model}
        r = await test_provider("google_ai_studio", None, c)
        label = "OK" if r.get("success") else (r.get("error") or "")[:100]
        print(f"{tier:5} {model:36} {label}")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
