"""Application configuration.

Settings are loaded from environment variables / a local .env file using
pydantic-settings. The backend is the sole source of numerical truth for
carbon calculations; configuration here only covers infrastructure concerns
(database connection, CORS, environment, and the Gemini API key placeholder
used later for explanation-only AI integration).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/circularcarbon"
    gemini_api_key: str = ""
    cors_origins: str = "http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
