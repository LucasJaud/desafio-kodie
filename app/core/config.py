from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações carregadas de variáveis de ambiente e do arquivo .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "task-organizer"
    log_level: str = "INFO"
    task_request_max_length: int = 4000
    database_path: str = "data/tasks.db"

    ai_provider: str = "openai-compatible"
    ai_api_key: str = ""
    ai_model: str = ""
    ai_base_url: str = ""
    ai_timeout_seconds: float = 30.0
    ai_max_tokens: int = 800
    ai_temperature: float = 0.0
    ai_json_mode: bool = True


@lru_cache
def get_settings() -> Settings:
    """Retorna as configurações carregadas uma única vez por processo."""
    return Settings()
