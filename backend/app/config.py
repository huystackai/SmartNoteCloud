from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://minddeck:minddeck@localhost:5432/minddecknote"
    jwt_secret_key: str = "change_me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    backend_cors_origins: str = "http://localhost:5173,http://localhost"
    admin_emails: str = "ntptuy.1910@gmail.com,giahuy.workhard@gmail.com"
    active_window_minutes: int = 5

    mimo_api_url: str = ""
    mimo_api_key: str = ""
    mimo_model: str = "mimo-chat"
    ai_timeout_seconds: int = 20
    ai_max_retries: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    @property
    def admin_email_list(self) -> set[str]:
        return {email.strip().lower() for email in self.admin_emails.split(",") if email.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
