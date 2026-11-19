from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "QueryCraft NL-to-SQL Analytics Platform"
    host: str = "0.0.0.0"
    port: int = 8001
    environment: str = "development"

    # Database
    database_url: str = "sqlite:///./querycraft.db"
    max_query_rows: int = 100
    query_timeout_seconds: float = 5.0

    # LLM Settings
    llm_api_key: Optional[str] = None
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

