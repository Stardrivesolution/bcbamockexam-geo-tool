from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables.

    Keeping configuration in one place matters because crawler limits,
    model names, and API keys will change as the product grows.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "GEO Internal Tool"
    app_env: str = "local"
    app_debug: bool = True
    http_timeout_seconds: int = Field(default=20, ge=3, le=120)
    max_html_bytes: int = Field(default=3_000_000, ge=100_000)
    database_url: str = "sqlite:///./geo_internal_tool.db"
    llm_provider: str = "deepseek"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"
    llm_timeout_seconds: int = Field(default=60, ge=5, le=180)


@lru_cache
def get_settings() -> Settings:
    return Settings()
