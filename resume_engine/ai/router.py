import json
from typing import Protocol

import httpx

from resume_engine.config import settings


class AIProvider(Protocol):
    async def complete(self, messages: list[dict], json_schema: dict | None = None) -> dict:
        ...


class OllamaProvider:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model

    async def complete(self, messages: list[dict], json_schema: dict | None = None) -> dict:
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": "json" if json_schema else None,
        }
        if json_schema:
            payload["format"] = json_schema

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("message", {}).get("content", "{}")
            return _parse_json(content)


class OpenAIProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required")

    async def complete(self, messages: list[dict], json_schema: dict | None = None) -> dict:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)
        kwargs: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
        }
        if json_schema:
            kwargs["response_format"] = {"type": "json_object"}

        response = await client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content or "{}"
        return _parse_json(content)


class AnthropicProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.anthropic_model
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")

    async def complete(self, messages: list[dict], json_schema: dict | None = None) -> dict:
        system = ""
        user_messages = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                user_messages.append(m)

        payload = {
            "model": self.model,
            "max_tokens": 4096,
            "system": system + ("\nRespond with valid JSON only." if json_schema else ""),
            "messages": user_messages,
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["content"][0]["text"]
            return _parse_json(content)


class GeminiProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")

    async def complete(self, messages: list[dict], json_schema: dict | None = None) -> dict:
        combined = "\n".join(f"{m['role']}: {m['content']}" for m in messages)
        if json_schema:
            combined += "\n\nRespond with valid JSON only."

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                url,
                json={"contents": [{"parts": [{"text": combined}]}]},
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            return _parse_json(content)


class OpenRouterProvider:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or settings.openrouter_api_key
        self.model = model or settings.openrouter_model
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")

    async def complete(self, messages: list[dict], json_schema: dict | None = None) -> dict:
        payload: dict = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
        }
        if json_schema:
            payload["response_format"] = {"type": "json_object"}

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return _parse_json(content)


def _parse_json(content: str) -> dict:
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
        raise


PROVIDERS = {
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
    "openrouter": OpenRouterProvider,
}


def get_provider(
    name: str | None = None,
    model: str | None = None,
    config: dict | None = None,
) -> AIProvider:
    cfg = config or {}
    name = (name or cfg.get("default_ai_provider") or settings.default_ai_provider).lower()
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {name}. Available: {list(PROVIDERS.keys())}")
    cls = PROVIDERS[name]
    if name == "ollama":
        return cls(
            base_url=cfg.get("ollama_base_url") or settings.ollama_base_url,
            model=model or cfg.get("ollama_model") or settings.ollama_model,
        )
    if name == "openai":
        return cls(
            api_key=cfg.get("openai_api_key") or settings.openai_api_key,
            model=model or cfg.get("openai_model") or settings.openai_model,
        )
    if name == "anthropic":
        return cls(
            api_key=cfg.get("anthropic_api_key") or settings.anthropic_api_key,
            model=model or cfg.get("anthropic_model") or settings.anthropic_model,
        )
    if name == "gemini":
        return cls(
            api_key=cfg.get("gemini_api_key") or settings.gemini_api_key,
            model=model or cfg.get("gemini_model") or settings.gemini_model,
        )
    if name == "openrouter":
        return cls(
            api_key=cfg.get("openrouter_api_key") or settings.openrouter_api_key,
            model=model or cfg.get("openrouter_model") or settings.openrouter_model,
        )
    return cls(model=model)


def list_providers() -> list[dict]:
    return [
        {"id": "ollama", "name": "Ollama (Local)", "requires_key": False},
        {"id": "openai", "name": "OpenAI", "requires_key": True},
        {"id": "anthropic", "name": "Anthropic", "requires_key": True},
        {"id": "gemini", "name": "Google Gemini", "requires_key": True},
        {"id": "openrouter", "name": "OpenRouter", "requires_key": True},
    ]


async def test_provider(name: str, model: str | None = None, config: dict | None = None) -> dict:
    try:
        provider = get_provider(name, model, config)
        result = await provider.complete(
            [{"role": "user", "content": 'Reply with JSON: {"status": "ok"}'}],
            json_schema={"type": "object"},
        )
        return {"success": True, "response": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
