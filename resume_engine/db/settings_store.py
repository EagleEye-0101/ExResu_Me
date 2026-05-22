import json
from typing import Any

from sqlalchemy.orm import Session

from resume_engine.db.models import AppSetting

# Keys stored in DB (local only — never commit DB file)
SETTING_KEYS = [
    "default_ai_provider",
    "openai_api_key",
    "openai_model",
    "anthropic_api_key",
    "anthropic_model",
    "gemini_api_key",
    "gemini_model",
    "openrouter_api_key",
    "openrouter_model",
    "ollama_base_url",
    "ollama_model",
]

PUBLIC_SETTINGS = [
    "default_ai_provider",
    "openai_model",
    "anthropic_model",
    "gemini_model",
    "openrouter_model",
    "ollama_base_url",
    "ollama_model",
]

SECRET_KEYS = [
    "openai_api_key",
    "anthropic_api_key",
    "gemini_api_key",
    "openrouter_api_key",
]


def _mask(value: str) -> str:
    if not value or len(value) < 8:
        return "••••••••" if value else ""
    return value[:4] + "••••" + value[-4:]


def get_all_settings(db: Session) -> dict[str, Any]:
    rows = db.query(AppSetting).all()
    data = {r.key: r.value for r in rows}
    result: dict[str, Any] = {}
    for key in SETTING_KEYS:
        val = data.get(key, "")
        if key in SECRET_KEYS:
            result[key] = _mask(val) if val else ""
            result[f"{key}_set"] = bool(val)
        else:
            result[key] = val
    return result


def get_runtime_config(db: Session) -> dict[str, str]:
    """Full secrets for AI calls (server-side only)."""
    from resume_engine.config import settings

    rows = {r.key: r.value for r in db.query(AppSetting).all()}
    return {
        "default_ai_provider": rows.get("default_ai_provider") or settings.default_ai_provider,
        "openai_api_key": rows.get("openai_api_key") or settings.openai_api_key,
        "openai_model": rows.get("openai_model") or settings.openai_model,
        "anthropic_api_key": rows.get("anthropic_api_key") or settings.anthropic_api_key,
        "anthropic_model": rows.get("anthropic_model") or settings.anthropic_model,
        "gemini_api_key": rows.get("gemini_api_key") or settings.gemini_api_key,
        "gemini_model": rows.get("gemini_model") or settings.gemini_model,
        "openrouter_api_key": rows.get("openrouter_api_key") or settings.openrouter_api_key,
        "openrouter_model": rows.get("openrouter_model") or settings.openrouter_model,
        "ollama_base_url": rows.get("ollama_base_url") or settings.ollama_base_url,
        "ollama_model": rows.get("ollama_model") or settings.ollama_model,
    }


def update_settings(db: Session, payload: dict[str, str]) -> dict[str, Any]:
    for key, value in payload.items():
        if key not in SETTING_KEYS:
            continue
        if key in SECRET_KEYS and (not value or "••••" in value):
            continue
        row = db.query(AppSetting).filter(AppSetting.key == key).first()
        if row:
            row.value = value
        else:
            db.add(AppSetting(key=key, value=value))
    db.commit()
    return get_all_settings(db)
