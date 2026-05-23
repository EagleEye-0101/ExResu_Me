from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    default_ai_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-haiku-20241022"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-flash-preview"
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    database_url: str = "sqlite:///./data/resume_builder.db"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    export_dir: str = "./exports"

    @property
    def export_path(self) -> Path:
        path = Path(self.export_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
